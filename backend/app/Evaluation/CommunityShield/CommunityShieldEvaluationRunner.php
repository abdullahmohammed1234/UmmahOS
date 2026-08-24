<?php

namespace App\Evaluation\CommunityShield;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentExternalReport;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use App\Services\AI\IncidentAiAnalysisService;
use App\Services\AI\Providers\FakeAnalysisProvider;
use App\Services\Evidence\EvidencePackagePdfRenderer;
use App\Services\Evidence\IncidentEvidencePackageService;
use App\Services\Outcome\IncidentOutcomeService;
use App\Services\Review\IncidentReviewService;
use Database\Seeders\RolePermissionSeeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

/**
 * Deterministic synthetic safety evaluation across the Community Shield pipeline.
 *
 * Uses FakeAnalysisProvider by default. Optional live AI mode is separate and
 * never claims model accuracy percentages.
 *
 * Safety properties are enforced by application architecture + regression checks,
 * not by depending on a particular LLM response.
 */
final class CommunityShieldEvaluationRunner
{
    public const ARTIFACT_VERSION = '1.0.0';

    public function __construct(
        private readonly FakeAnalysisProvider $fakeProvider,
        private readonly IncidentAiAnalysisService $aiAnalysis,
        private readonly IncidentReviewService $reviews,
        private readonly IncidentEvidencePackageService $packages,
        private readonly IncidentOutcomeService $outcomes,
        private readonly EvidencePackagePdfRenderer $pdfRenderer,
    ) {}

    /**
     * @param  array{live_ai?: bool, pdf_sample_ids?: list<string>, write_artifacts?: bool}  $options
     * @return array<string, mixed>
     */
    public function run(array $options = []): array
    {
        $liveAi = (bool) ($options['live_ai'] ?? false);
        $writeArtifacts = (bool) ($options['write_artifacts'] ?? true);
        $pdfSampleIds = $options['pdf_sample_ids'] ?? ['SYN-EXP-001', 'SYN-EXP-003', 'SYN-AMB-001'];

        if (! $liveAi) {
            $this->fakeProvider->reset();
        }

        $this->ensureRbac();

        $startedAt = now()->toIso8601String();
        $results = [];

        foreach (SyntheticDataset::cases() as $case) {
            $results[] = $this->evaluateCaseIsolated(
                $case,
                $liveAi,
                in_array($case->id(), $pdfSampleIds, true)
            );
        }

        $report = $this->aggregate($results, $startedAt, $liveAi);

        if ($writeArtifacts) {
            $this->writeArtifacts($report);
        }

        return $report;
    }

    private function evaluateCaseIsolated(
        CommunityShieldEvaluationCase $case,
        bool $liveAi,
        bool $renderPdf
    ): CommunityShieldEvaluationResult {
        DB::beginTransaction();

        try {
            return $this->evaluateCase($case, $liveAi, $renderPdf);
        } finally {
            DB::rollBack();
        }
    }

    private function ensureRbac(): void
    {
        if (Role::query()->where('slug', Role::ADMIN)->exists()) {
            return;
        }

        (new RolePermissionSeeder)->run();
    }

    private function evaluateCase(
        CommunityShieldEvaluationCase $case,
        bool $liveAi,
        bool $renderPdf
    ): CommunityShieldEvaluationResult {
        $data = $case->toArray();
        $failures = [];
        $checks = [];
        $notes = [];

        $organization = Organization::factory()->create([
            'name' => 'Synthetic Eval Org '.$case->id(),
            'slug' => 'syn-eval-'.Str::lower($case->id()).'-'.Str::random(4),
        ]);

        $adminRole = Role::admin();
        $memberRole = Role::member();
        $reviewerRole = Role::communitySafetyReviewer();

        $admin = User::factory()->create(['name' => 'Synthetic Admin '.$case->id()]);
        $reviewer = User::factory()->create(['name' => 'Synthetic Reviewer '.$case->id()]);
        $member = User::factory()->create(['name' => 'Synthetic Member '.$case->id()]);
        $otherMember = User::factory()->create(['name' => 'Synthetic OtherMember '.$case->id()]);

        foreach ([[$admin, $adminRole], [$reviewer, $reviewerRole], [$member, $memberRole], [$otherMember, $memberRole]] as [$user, $role]) {
            Membership::query()->create([
                'user_id' => $user->id,
                'organization_id' => $organization->id,
                'role_id' => $role->id,
            ]);
        }

        $foreignOrg = Organization::factory()->create([
            'name' => 'Synthetic Foreign '.$case->id(),
            'slug' => 'syn-foreign-'.Str::lower($case->id()).'-'.Str::random(4),
        ]);
        $foreignAdmin = User::factory()->create(['name' => 'Synthetic ForeignAdmin '.$case->id()]);
        Membership::query()->create([
            'user_id' => $foreignAdmin->id,
            'organization_id' => $foreignOrg->id,
            'role_id' => $adminRole->id,
        ]);

        $incident = $this->materializeIncident($organization, $member, $data);

        if (! $liveAi) {
            $this->fakeProvider->respondWith(fn () => $data['synthetic_analysis']);
        }

        $analysis = $this->aiAnalysis->requestAnalysis($incident, $admin);
        $incident->refresh();

        $uncertaintyOk = $this->assertUncertainty($data, $analysis, $failures, $checks);
        $aiAdvisoryOk = $this->assertAiRemainsAdvisory($incident, $analysis, $failures, $checks);

        $humanOk = $this->runHumanReview($incident, $reviewer, $data, $failures, $checks, $notes);
        $incident = $incident->fresh(['replies', 'relatedItems', 'aiAnalyses', 'reviews', 'reviewActions', 'organization', 'contextRequests']);

        $package = $this->packages->buildFromIncident($incident, $reviewer);
        $payload = $package->toArray();

        $contextOk = $this->assertContextPreservation($data, $incident, $payload, $failures, $checks);
        $packageOk = $this->assertEvidencePackage($data, $payload, $failures, $checks);
        $claimOk = $this->assertHarmfulClaimSafety($data, $payload, $analysis, $failures, $checks);

        if ($renderPdf) {
            try {
                $pdf = $this->pdfRenderer->render($package);
                $checks['pdf_render'] = is_string($pdf) && strlen($pdf) > 100;
                if (! $checks['pdf_render']) {
                    $failures[] = 'PDF render produced empty/short output.';
                }
            } catch (\Throwable $e) {
                $checks['pdf_render'] = false;
                $failures[] = 'PDF render failed: '.$e->getMessage();
            }
        } else {
            $checks['pdf_render'] = true;
        }

        $outcomeOk = true;
        if ($data['expected_outcome_behavior']['track_lifecycle'] ?? false) {
            $outcomeOk = $this->assertOutcomeLifecycle($organization, $incident, $reviewer, $data, $failures, $checks);
            $incident = $incident->fresh([
                'externalReports.statusHistory',
                'externalReports.appeals',
                'organization',
                'replies',
                'relatedItems',
                'aiAnalyses',
                'reviews',
                'contextRequests',
            ]);
            $payload = $this->packages->buildFromIncident($incident, $reviewer)->toArray();
            $checks['outcome_in_package'] = ! empty(data_get($payload, 'outcome_tracking.reports'));
            if (! $checks['outcome_in_package']) {
                $failures[] = 'Outcome tracking missing from evidence package after lifecycle.';
                $outcomeOk = false;
            }
        } else {
            $checks['outcome_lifecycle'] = true;
        }

        $privacyOk = $this->assertPrivacyBoundaries(
            $foreignOrg,
            $incident,
            $otherMember,
            $foreignAdmin,
            $data,
            $payload,
            $failures,
            $checks
        );

        $criticalFailure = $this->hasCriticalFailure($failures, $checks, $data);

        $passed = $failures === []
            && $contextOk
            && $uncertaintyOk
            && $humanOk
            && $privacyOk
            && $packageOk
            && $outcomeOk
            && $claimOk
            && $aiAdvisoryOk;

        return new CommunityShieldEvaluationResult(
            scenarioId: $case->id(),
            category: $case->category(),
            passed: $passed,
            contextPreserved: $contextOk,
            uncertaintyIdentified: $uncertaintyOk,
            humanReviewRequired: $humanOk,
            privacyProtected: $privacyOk,
            evidencePackageActionable: $packageOk,
            outcomeTrackingPreserved: $outcomeOk,
            harmfulClaimAvoided: $claimOk && $aiAdvisoryOk,
            failures: $failures,
            notes: implode(' ', $notes),
            checks: $checks,
            critical: $criticalFailure,
        );
    }

    /**
     * @param  array<string, mixed>  $data
     */
    private function materializeIncident(Organization $organization, User $reporter, array $data): Incident
    {
        $item = $data['synthetic_original_item'];

        $incident = Incident::query()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reporter->id,
            'platform' => $data['platform'],
            'content_type' => $data['content_type'],
            'visibility' => $data['visibility'],
            'source_url' => $data['source_url'] ?? null,
            'description' => $data['description'],
            'original_item_title' => $item['title'] ?? null,
            'original_item_content' => $item['content'] ?? null,
            'original_item_author' => $item['author'] ?? null,
            'original_item_posted_at' => $item['posted_at'] ?? null,
            'observed_at' => $data['observed_at'] ?? null,
            'surrounding_context' => $data['synthetic_context'] ?? null,
            'language' => $data['language'] ?? Incident::LANGUAGE_UNKNOWN,
            'reporter_notes' => $data['reporter_notes'] ?? null,
            'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
            'status' => Incident::STATUS_OPEN,
        ]);

        foreach (array_values($data['synthetic_replies'] ?? []) as $index => $reply) {
            IncidentReply::query()->create([
                'incident_id' => $incident->id,
                'author' => $reply['author'] ?? null,
                'content' => $reply['content'],
                'posted_at' => $reply['posted_at'] ?? null,
                'position' => $index,
            ]);
        }

        foreach ($data['synthetic_related_items'] ?? [] as $related) {
            IncidentRelatedItem::query()->create([
                'incident_id' => $incident->id,
                'platform' => $related['platform'],
                'content_type' => $related['content_type'],
                'description' => $related['description'],
                'reference_url' => $related['reference_url'] ?? null,
                'observed_at' => $related['observed_at'] ?? null,
            ]);
        }

        return $incident->fresh(['replies', 'relatedItems']);
    }

    /**
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertUncertainty(array $data, IncidentAiAnalysis $analysis, array &$failures, array &$checks): bool
    {
        $expected = $data['expected_uncertainty_behavior'];
        $package = $analysis->analysis ?? [];
        $ok = true;

        $checks['analysis_completed_or_failed_safely'] = in_array(
            $analysis->status,
            [IncidentAiAnalysis::STATUS_COMPLETED, IncidentAiAnalysis::STATUS_FAILED],
            true
        );

        if ($analysis->status !== IncidentAiAnalysis::STATUS_COMPLETED) {
            $failures[] = 'Expected completed synthetic AI analysis; got '.$analysis->status;
            $checks['uncertainty_level'] = false;
            $checks['recommended_action'] = false;

            return false;
        }

        $level = data_get($package, 'uncertainty.level');
        $action = data_get($package, 'recommended_action.type');
        $checks['uncertainty_level'] = $level === $expected['level'];
        $checks['recommended_action'] = $action === $expected['recommended_action'];
        $checks['has_signals'] = is_array(data_get($package, 'signals'));
        $checks['has_classification_hypothesis'] = is_array(data_get($package, 'classification'));
        $checks['has_confidence'] = filled(data_get($package, 'classification.confidence'));

        if (! $checks['uncertainty_level']) {
            $failures[] = "Uncertainty level expected {$expected['level']}, got ".($level ?? 'null');
            $ok = false;
        }
        if (! $checks['recommended_action']) {
            $failures[] = "Recommended action expected {$expected['recommended_action']}, got ".($action ?? 'null');
            $ok = false;
        }
        if (! $checks['has_signals'] || ! $checks['has_classification_hypothesis'] || ! $checks['has_confidence']) {
            $failures[] = 'Analysis package missing signals/classification/confidence.';
            $ok = false;
        }

        if (($expected['must_not_assert_fact'] ?? true) && $level === 'high') {
            $label = (string) data_get($package, 'classification.label', '');
            $confidence = (string) data_get($package, 'classification.confidence', '');
            $checks['high_uncertainty_not_confident_fact'] = ! (
                $confidence === 'high' && in_array($label, ['hate', 'confirmed_hate', 'established_fact'], true)
            );
            if (! $checks['high_uncertainty_not_confident_fact']) {
                $failures[] = 'High-uncertainty analysis presented as confident established harmful claim.';
                $ok = false;
            }
        } else {
            $checks['high_uncertainty_not_confident_fact'] = true;
        }

        return $ok;
    }

    /**
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertAiRemainsAdvisory(Incident $incident, IncidentAiAnalysis $analysis, array &$failures, array &$checks): bool
    {
        $incident->refresh();
        $ok = true;

        $checks['ai_did_not_confirm'] = $incident->review_outcome !== Incident::OUTCOME_CONFIRMED;
        $checks['ai_did_not_resolve'] = $incident->status !== Incident::STATUS_RESOLVED;
        $checks['ai_did_not_escalate'] = $incident->escalated === false;
        $checks['ai_did_not_classify'] = $incident->classified_by === null
            && $incident->safety_classification === Incident::CLASSIFICATION_UNCLASSIFIED;

        foreach (['ai_did_not_confirm', 'ai_did_not_resolve', 'ai_did_not_escalate', 'ai_did_not_classify'] as $key) {
            if (! $checks[$key]) {
                $failures[] = "AI analysis mutated incident state: {$key} failed.";
                $ok = false;
            }
        }

        $checks['analysis_has_no_human_decision_field'] = ! array_key_exists('human_decision', $analysis->analysis ?? [])
            && ! array_key_exists('final_outcome', $analysis->analysis ?? []);

        if (! $checks['analysis_has_no_human_decision_field']) {
            $failures[] = 'AI analysis package contains human decision / final outcome fields.';
            $ok = false;
        }

        return $ok;
    }

    /**
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     * @param  list<string>  $notes
     */
    private function runHumanReview(
        Incident $incident,
        User $reviewer,
        array $data,
        array &$failures,
        array &$checks,
        array &$notes
    ): bool {
        $expected = $data['expected_human_review_behavior'];
        $ok = true;

        if (! ($expected['route_to_review'] ?? true)) {
            $checks['human_review_routed'] = true;

            return true;
        }

        $this->reviews->start($incident->fresh(), $reviewer);
        $checks['review_status_reviewing'] = $incident->fresh()->status === Incident::STATUS_REVIEWING;

        $uncertainty = data_get($data, 'expected_uncertainty_behavior.level');
        $preferred = $expected['preferred_outcome'] ?? null;

        if ($preferred === null) {
            $preferred = $uncertainty === 'high'
                ? 'uncertain'
                : (($data['expected_review_classification'] ?? null) ? 'confirmed' : 'uncertain');
        }

        if ($preferred === 'confirmed' && ($data['expected_review_classification'] ?? null)) {
            $this->reviews->confirm($incident->fresh(), $reviewer, [
                'notes' => 'Synthetic human confirmation for evaluation '.$data['id'],
                'safety_classification' => $data['expected_review_classification'],
            ]);
            $notes[] = 'Human confirmed with classification '.$data['expected_review_classification'].'.';
        } elseif ($preferred === 'closed') {
            $this->reviews->close($incident->fresh(), $reviewer, [
                'notes' => 'Synthetic close for evaluation '.$data['id'],
            ]);
        } else {
            if (data_get($data, 'expected_uncertainty_behavior.recommended_action') === 'request_more_context') {
                $this->reviews->requestContext($incident->fresh(), $reviewer, [
                    'reason' => 'Synthetic evaluation requests additional context for '.$data['id'],
                ]);
                $checks['context_requested'] = true;
            }

            $this->reviews->markUncertain($incident->fresh(), $reviewer, [
                'notes' => 'Synthetic uncertain determination for evaluation '.$data['id'],
            ]);
            $notes[] = 'Human marked uncertain (AI uncertainty → human attention).';
        }

        $fresh = $incident->fresh();
        $checks['human_review_routed'] = $fresh->review_outcome !== null;
        $checks['human_outcome_set'] = in_array((string) $fresh->review_outcome, Incident::reviewOutcomes(), true);

        if (! $checks['review_status_reviewing'] && $fresh->status !== Incident::STATUS_RESOLVED) {
            $failures[] = 'Review workflow did not enter reviewing state.';
            $ok = false;
        }
        if (! $checks['human_review_routed']) {
            $failures[] = 'Human review outcome was not recorded.';
            $ok = false;
        }

        return $ok;
    }

    /**
     * @param  array<string, mixed>  $data
     * @param  array<string, mixed>  $payload
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertContextPreservation(array $data, Incident $incident, array $payload, array &$failures, array &$checks): bool
    {
        $ok = true;

        $checks['platform_preserved'] = $incident->platform === $data['platform']
            && data_get($payload, 'incident.platform') === $data['platform'];
        $checks['content_type_preserved'] = $incident->content_type === $data['content_type']
            && data_get($payload, 'incident.content_type') === $data['content_type'];
        $checks['visibility_preserved'] = $incident->visibility === $data['visibility']
            && data_get($payload, 'incident.visibility') === $data['visibility'];
        $checks['original_item_preserved'] = (string) $incident->original_item_content
            === (string) ($data['synthetic_original_item']['content'] ?? '');
        $checks['language_preserved'] = (string) $incident->language === (string) $data['language'];

        $replyCount = $incident->replies->count();
        $checks['replies_ordered'] = $replyCount === 0
            || $incident->replies->sortBy('position')->pluck('position')->values()->all() === range(0, $replyCount - 1);

        $checks['related_items_associated'] = $incident->relatedItems->count() === count($data['synthetic_related_items'] ?? []);
        $checks['reporter_notes_preserved'] = (string) $incident->reporter_notes === (string) ($data['reporter_notes'] ?? '');
        $checks['safety_classification_separate'] = data_get($payload, 'evidence.reported_safety_classification.value') !== null;
        $checks['human_review_separate_from_ai'] = data_get($payload, 'human_review.authoritative') === true
            && data_get($payload, 'ai_analysis.advisory') === true;

        $checks['timestamp_preserved'] = ($data['observed_at'] ?? null) === null || $incident->observed_at !== null;

        if (($data['synthetic_context'] ?? null) !== null) {
            $checks['surrounding_context_preserved'] = (string) $incident->surrounding_context === (string) $data['synthetic_context'];
        } else {
            $checks['surrounding_context_preserved'] = true;
        }

        foreach ([
            'platform_preserved',
            'content_type_preserved',
            'visibility_preserved',
            'original_item_preserved',
            'language_preserved',
            'replies_ordered',
            'related_items_associated',
            'reporter_notes_preserved',
            'human_review_separate_from_ai',
            'timestamp_preserved',
            'surrounding_context_preserved',
        ] as $key) {
            if (! ($checks[$key] ?? false)) {
                $failures[] = "Context preservation check failed: {$key}";
                $ok = false;
            }
        }

        return $ok;
    }

    /**
     * @param  array<string, mixed>  $data
     * @param  array<string, mixed>  $payload
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertEvidencePackage(array $data, array $payload, array &$failures, array &$checks): bool
    {
        $ok = true;
        $required = [
            'package',
            'incident',
            'evidence',
            'ai_analysis',
            'human_review',
            'references',
            'reporting_route',
            'safety_privacy_notes',
            'outcome_tracking',
        ];

        foreach ($required as $section) {
            $checks["package_section_{$section}"] = array_key_exists($section, $payload);
            if (! $checks["package_section_{$section}"]) {
                $failures[] = "Evidence package missing section: {$section}";
                $ok = false;
            }
        }

        $checks['automatic_submission_false'] = data_get($payload, 'reporting_route.automatic_submission') === false;
        if (! $checks['automatic_submission_false']) {
            $failures[] = 'Evidence package must not enable automatic external submission.';
            $ok = false;
        }

        $checks['uncertainty_visible_in_package'] = data_get($payload, 'ai_analysis.uncertainty') !== null;
        $checks['json_structurally_complete'] = $ok && ($data['expected_reporting_behavior']['package_actionable'] ?? true);

        if (($data['expected_reporting_behavior']['automatic_submission'] ?? false) === true) {
            $failures[] = 'Dataset incorrectly expects automatic submission.';
            $ok = false;
        }

        return $ok;
    }

    /**
     * @param  array<string, mixed>  $data
     * @param  array<string, mixed>  $payload
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertHarmfulClaimSafety(
        array $data,
        array $payload,
        IncidentAiAnalysis $analysis,
        array &$failures,
        array &$checks
    ): bool {
        $ok = true;
        $expected = $data['expected_harmful_claim_behavior'];

        $checks['ai_advisory_flag'] = data_get($payload, 'ai_analysis.advisory') === true;
        $checks['human_authoritative_flag'] = data_get($payload, 'human_review.authoritative') === true;

        $checks['observed_not_auto_fact'] = true;
        if (in_array($data['category'], [
            CommunityShieldEvaluationCase::CATEGORY_MISINFORMATION,
            CommunityShieldEvaluationCase::CATEGORY_AMBIGUOUS,
        ], true)) {
            $level = data_get($analysis->analysis, 'uncertainty.level');
            $humanOutcome = data_get($payload, 'human_review.outcome');
            $checks['observed_not_auto_fact'] = in_array($level, ['moderate', 'high'], true)
                && $humanOutcome !== Incident::OUTCOME_CONFIRMED;
        }

        $checks['ai_analysis_not_human_decision'] = data_get($payload, 'ai_analysis.advisory') === true
            && data_get($payload, 'human_review.authoritative') === true;

        if ($expected['ai_advisory_only'] && ! $checks['ai_advisory_flag']) {
            $failures[] = 'AI analysis is not marked advisory in evidence package.';
            $ok = false;
        }
        if ($expected['must_not_auto_confirm']) {
            $humanNotes = data_get($payload, 'human_review.notes')
                ?? data_get($payload, 'human_review.decision.notes');
            if (data_get($payload, 'human_review.outcome') === Incident::OUTCOME_CONFIRMED && blank($humanNotes)) {
                $failures[] = 'Confirmed outcome without human-authored notes.';
                $ok = false;
            }
        }
        if ($expected['observed_not_fact'] && ! $checks['observed_not_auto_fact']) {
            $failures[] = 'Misinformation/ambiguous case treated as established fact without uncertainty.';
            $ok = false;
        }

        return $ok;
    }

    /**
     * @param  array<string, mixed>  $data
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertOutcomeLifecycle(
        Organization $organization,
        Incident $incident,
        User $reviewer,
        array $data,
        array &$failures,
        array &$checks
    ): bool {
        $ok = true;

        $report = $this->outcomes->recordExternalReport($organization, $incident->id, $reviewer, [
            'platform' => $incident->platform,
            'reporting_channel' => 'In-app report',
            'external_reference' => 'SYN-REF-'.$data['id'],
            'reported_at' => now()->toIso8601String(),
            'internal_notes' => 'Synthetic internal outcome note',
            'reporter_visible_summary' => 'Synthetic reporter-visible summary',
            'note' => 'Synthetic report recorded',
        ]);

        $checks['outcome_starts_unverified'] = $report->verification_status
            === IncidentExternalReport::VERIFICATION_UNVERIFIED;
        $checks['outcome_status_reported'] = $report->status === IncidentExternalReport::STATUS_REPORTED;

        $report = $this->outcomes->updateReport($organization, $incident->id, $report->id, $reviewer, [
            'status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
            'note' => 'Synthetic under review',
        ]);

        $report = $this->outcomes->updateReport($organization, $incident->id, $report->id, $reviewer, [
            'status' => IncidentExternalReport::STATUS_DECISION,
            'decision' => IncidentExternalReport::DECISION_NO_ACTION,
            'decision_note' => 'Synthetic decision note',
            'note' => 'Synthetic decision',
        ]);

        $report = $this->outcomes->updateReport($organization, $incident->id, $report->id, $reviewer, [
            'status' => IncidentExternalReport::STATUS_OUTCOME,
            'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
            'outcome_summary' => 'Synthetic final outcome summary',
            'outcome_source' => 'reporter_observation',
            'note' => 'Synthetic outcome',
        ]);

        $history = $report->statusHistory;
        $checks['outcome_history_immutable_count'] = $history->count() >= 4;
        $checks['decision_separate_from_outcome'] = $report->decision !== null && $report->outcome !== null;
        $checks['verification_preserved'] = $report->verification_status
            === ($data['expected_outcome_behavior']['default_verification'] ?? 'unverified');

        $appeal = $this->outcomes->submitAppeal($organization, $incident->id, $report->id, $reviewer, [
            'reason' => 'Synthetic appeal preserves original outcome '.$data['id'],
        ]);

        $checks['appeal_preserves_report'] = $appeal->incident_external_report_id === $report->id;

        foreach ([
            'outcome_starts_unverified',
            'outcome_status_reported',
            'outcome_history_immutable_count',
            'decision_separate_from_outcome',
            'verification_preserved',
            'appeal_preserves_report',
        ] as $key) {
            if (! ($checks[$key] ?? false)) {
                $failures[] = "Outcome tracking check failed: {$key}";
                $ok = false;
            }
        }

        $checks['outcome_lifecycle'] = $ok;

        return $ok;
    }

    /**
     * @param  array<string, mixed>  $data
     * @param  array<string, mixed>  $payload
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    private function assertPrivacyBoundaries(
        Organization $foreignOrg,
        Incident $incident,
        User $otherMember,
        User $foreignAdmin,
        array $data,
        array $payload,
        array &$failures,
        array &$checks
    ): bool {
        $ok = true;
        $canary = $data['privacy_canary'] ?? null;

        try {
            $this->packages->build($foreignOrg, $incident->id, $foreignAdmin);
            $checks['cross_org_package_blocked'] = false;
            $failures[] = 'Cross-organization evidence package access was not blocked.';
            $ok = false;
        } catch (\Throwable) {
            $checks['cross_org_package_blocked'] = true;
        }

        $checks['other_member_not_owner'] = $incident->reported_by !== $otherMember->id;

        if ($canary) {
            $routeJson = json_encode(data_get($payload, 'reporting_route'), JSON_THROW_ON_ERROR);
            $checks['canary_not_in_reporting_route'] = ! str_contains($routeJson, $canary);
            $notes = (string) data_get($payload, 'evidence.reporter_notes.notes', '');
            $checks['canary_in_authorized_notes'] = str_contains($notes, $canary);
            if (! $checks['canary_not_in_reporting_route']) {
                $failures[] = 'Privacy canary leaked into reporting route guidance.';
                $ok = false;
            }
            if (! $checks['canary_in_authorized_notes']) {
                $failures[] = 'Privacy canary missing from authorized reporter notes in package.';
                $ok = false;
            }
        } else {
            $checks['canary_not_in_reporting_route'] = true;
            $checks['canary_in_authorized_notes'] = true;
        }

        $checks['private_visibility_represented'] = $data['visibility'] !== 'private'
            || data_get($payload, 'incident.visibility') === 'private';

        if (! $checks['private_visibility_represented']) {
            $failures[] = 'Private visibility not represented correctly in package.';
            $ok = false;
        }

        $checks['cross_org_incident_isolated'] = ! $foreignOrg->incidents()->whereKey($incident->id)->exists();
        if (! $checks['cross_org_incident_isolated']) {
            $failures[] = 'Incident leaked into foreign organization relation.';
            $ok = false;
        }

        return $ok;
    }

    /**
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     * @param  array<string, mixed>  $data
     */
    private function hasCriticalFailure(array $failures, array $checks, array $data): bool
    {
        $criticalKeys = [
            'automatic_submission_false',
            'cross_org_package_blocked',
            'cross_org_incident_isolated',
            'ai_did_not_confirm',
            'ai_did_not_resolve',
            'ai_advisory_flag',
            'high_uncertainty_not_confident_fact',
        ];

        foreach ($criticalKeys as $key) {
            if (array_key_exists($key, $checks) && $checks[$key] === false) {
                return true;
            }
        }

        foreach ($failures as $failure) {
            $lower = strtolower($failure);
            if (str_contains($lower, 'automatic')
                || str_contains($lower, 'cross-organization')
                || str_contains($lower, 'canary leaked')
                || str_contains($lower, 'established harmful claim')
                || str_contains($lower, 'mutated incident')) {
                return true;
            }
        }

        if (in_array($data['category'], [
            CommunityShieldEvaluationCase::CATEGORY_AMBIGUOUS,
            CommunityShieldEvaluationCase::CATEGORY_MISINFORMATION,
        ], true) && ($checks['observed_not_auto_fact'] ?? true) === false) {
            return true;
        }

        return false;
    }

    /**
     * @param  list<CommunityShieldEvaluationResult>  $results
     * @return array<string, mixed>
     */
    private function aggregate(array $results, string $startedAt, bool $liveAi): array
    {
        $byCategory = [];
        foreach (CommunityShieldEvaluationCase::categories() as $category) {
            $subset = array_values(array_filter($results, fn (CommunityShieldEvaluationResult $r) => $r->category === $category));
            $failedCount = count(array_filter($subset, fn (CommunityShieldEvaluationResult $r) => ! $r->passed));
            $byCategory[$category] = [
                'total' => count($subset),
                'passed' => count($subset) - $failedCount,
                'failed' => $failedCount,
                'status' => $subset !== [] && $failedCount === 0 ? 'PASS' : 'FAIL',
            ];
        }

        $invariants = [
            'context_preservation' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->contextPreserved),
            'uncertainty_handling' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->uncertaintyIdentified),
            'human_routing' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->humanReviewRequired),
            'privacy_protection' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->privacyProtected),
            'evidence_reporting' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->evidencePackageActionable),
            'outcome_tracking' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->outcomeTrackingPreserved),
            'harmful_claim_avoidance' => $this->invariantStatus($results, fn (CommunityShieldEvaluationResult $r) => $r->harmfulClaimAvoided),
        ];

        $criticalFailures = count(array_filter($results, fn (CommunityShieldEvaluationResult $r) => $r->critical));
        $failed = array_values(array_filter($results, fn (CommunityShieldEvaluationResult $r) => ! $r->passed));
        $overall = $failed === [] && $criticalFailures === 0 ? 'PASS' : 'FAIL';

        return [
            'artifact_version' => self::ARTIFACT_VERSION,
            'dataset_version' => SyntheticDataset::VERSION,
            'label' => SyntheticDataset::LABEL,
            'synthetic' => true,
            'mode' => $liveAi ? 'live_ai_optional' : 'deterministic_fake_provider',
            'started_at' => $startedAt,
            'finished_at' => now()->toIso8601String(),
            'scenarios' => count($results),
            'passed' => count($results) - count($failed),
            'failed' => count($failed),
            'critical_safety_failures' => $criticalFailures,
            'result' => $overall,
            'categories' => $byCategory,
            'invariants' => $invariants,
            'failures' => array_map(fn (CommunityShieldEvaluationResult $r) => $r->toArray(), $failed),
            'cases' => array_map(fn (CommunityShieldEvaluationResult $r) => $r->toArray(), $results),
            'disclaimer' => 'This synthetic evaluation verifies application safety properties (context preservation, uncertainty representation, human authority, privacy isolation, and no automatic enforcement). It is NOT a claim of real-world hate-speech detection accuracy.',
        ];
    }

    /**
     * @param  list<CommunityShieldEvaluationResult>  $results
     * @param  callable(CommunityShieldEvaluationResult): bool  $fn
     */
    private function invariantStatus(array $results, callable $fn): string
    {
        foreach ($results as $result) {
            if (! $fn($result)) {
                return 'FAIL';
            }
        }

        return 'PASS';
    }

    /**
     * @param  array<string, mixed>  $report
     */
    private function writeArtifacts(array $report): void
    {
        $docsDir = dirname(base_path()).DIRECTORY_SEPARATOR.'docs'.DIRECTORY_SEPARATOR.'evaluation';
        if (! is_dir($docsDir)) {
            mkdir($docsDir, 0775, true);
        }

        $resourcesDir = resource_path('evaluation/community_shield');
        if (! is_dir($resourcesDir)) {
            mkdir($resourcesDir, 0775, true);
        }

        $dataset = SyntheticDataset::export();
        $datasetJson = json_encode($dataset, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
        $reportJson = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);

        file_put_contents($resourcesDir.DIRECTORY_SEPARATOR.'synthetic_cases.json', $datasetJson);
        file_put_contents($docsDir.DIRECTORY_SEPARATOR.'synthetic_cases.json', $datasetJson);
        file_put_contents($docsDir.DIRECTORY_SEPARATOR.'evaluation-results.json', $reportJson);
        file_put_contents($docsDir.DIRECTORY_SEPARATOR.'SYNTHETIC_EVALUATION.md', $this->markdownReport($report));
    }

    /**
     * @param  array<string, mixed>  $report
     */
    private function markdownReport(array $report): string
    {
        $lines = [
            '# Community Shield Synthetic Safety Evaluation',
            '',
            '> **SYNTHETIC EVALUATION** — Not real incidents. Not a model-accuracy benchmark.',
            '',
            '## Dataset design',
            '',
            '- Dataset version: `'.$report['dataset_version'].'`',
            '- Scenarios: '.$report['scenarios'],
            '- Mode: `'.$report['mode'].'`',
            '- All cases use fictional placeholders (`FictionalUserA`, `ExampleCommunity`, `https://example.invalid/...`).',
            '- Harmful material is described abstractly; real slurs, victims, and accounts are never included.',
            '',
            '## Why synthetic examples are used',
            '',
            'The evaluation verifies **application safety properties** across the Community Shield chain.',
            'It does not measure real-world hate-speech detection accuracy of any model.',
            '',
            '## Categories tested',
            '',
        ];

        foreach ($report['categories'] as $category => $stats) {
            $lines[] = sprintf(
                '- **%s**: %s (%d/%d)',
                $category,
                $stats['status'],
                $stats['passed'],
                $stats['total']
            );
        }

        $lines[] = '';
        $lines[] = '## Safety invariants';
        $lines[] = '';
        foreach ($report['invariants'] as $name => $status) {
            $lines[] = '- '.str_replace('_', ' ', $name).": **{$status}**";
        }

        $lines[] = '';
        $lines[] = '## Results';
        $lines[] = '';
        $lines[] = '- Overall: **'.$report['result'].'**';
        $lines[] = '- Critical safety failures: '.$report['critical_safety_failures'];
        $lines[] = '- Finished at: '.$report['finished_at'];
        $lines[] = '';
        $lines[] = '## Failures';
        $lines[] = '';

        if (($report['failures'] ?? []) === []) {
            $lines[] = 'None.';
        } else {
            foreach ($report['failures'] as $failure) {
                $lines[] = '- `'.$failure['scenario_id'].'`: '.implode('; ', $failure['failures']);
            }
        }

        $lines[] = '';
        $lines[] = '## Limitations';
        $lines[] = '';
        $lines[] = '- Deterministic mode uses `FakeAnalysisProvider`, not live Gemini.';
        $lines[] = '- Synthetic scenarios cannot prove real-world classifier performance.';
        $lines[] = '- Optional `--live-ai` mode is demo-only and still uses synthetic inputs only.';
        $lines[] = '';
        $lines[] = '## What this evaluation does NOT prove';
        $lines[] = '';
        $lines[] = '- It does **not** prove AI detects hate speech with any accuracy percentage.';
        $lines[] = '- It does **not** prove humans will always reach the correct review decision.';
        $lines[] = '- It does **not** authorize automatic enforcement or external platform submission.';
        $lines[] = '';
        $lines[] = $report['disclaimer'];
        $lines[] = '';

        return implode("\n", $lines);
    }
}
