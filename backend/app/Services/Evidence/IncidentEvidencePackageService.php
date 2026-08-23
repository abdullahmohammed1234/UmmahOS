<?php

namespace App\Services\Evidence;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentContextRequest;
use App\Models\IncidentExternalReport;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
use App\Models\IncidentReview;
use App\Models\IncidentReviewAction;
use App\Models\Organization;
use App\Models\User;
use App\Services\Outcome\IncidentOutcomeService;
use Illuminate\Support\Carbon;

/**
 * Builds a deterministic Incident Evidence Package from source-of-truth records.
 * Read-only — does not mutate incidents, reviews, or AI analyses.
 */
class IncidentEvidencePackageService
{
    public function __construct(
        private readonly ReportingRouteService $reportingRoutes,
        private readonly SafetyPrivacyGuidanceService $safetyGuidance,
        private readonly IncidentOutcomeService $outcomes,
    ) {}

    public function build(Organization $organization, int $incidentId, User $generatedBy): IncidentEvidencePackage
    {
        $incident = $this->loadIncident($organization, $incidentId);

        return $this->buildFromIncident($incident, $generatedBy);
    }

    public function buildFromIncident(Incident $incident, User $generatedBy): IncidentEvidencePackage
    {
        $analyses = $incident->aiAnalyses;
        $currentAnalysis = $analyses->first();
        $previousAnalyses = $analyses->slice(1)->values();

        $payload = [
            'package' => [
                'schema_version' => IncidentEvidencePackage::SCHEMA_VERSION,
                'package_version' => $this->packageVersion($incident),
                'generated_at' => now()->toIso8601String(),
                'generated_by' => [
                    'name' => $generatedBy->name,
                    'role_label' => 'Authorized exporter',
                ],
                'organization' => [
                    'name' => $incident->organization?->name,
                    'slug' => $incident->organization?->slug,
                ],
                'source_incident_updated_at' => optional($incident->updated_at)?->toIso8601String(),
                'hierarchy' => [
                    'source_evidence' => 'SOURCE EVIDENCE',
                    'ai_analysis' => 'AI ANALYSIS — ADVISORY',
                    'human_review' => 'HUMAN REVIEW — AUTHORITATIVE',
                    'reporting_guidance' => 'REPORTING GUIDANCE',
                ],
            ],
            'incident' => $this->incidentMetadata($incident),
            'evidence' => [
                'label' => 'SOURCE EVIDENCE',
                'original_item' => $this->originalItem($incident),
                'surrounding_context' => $this->nullableString($incident->surrounding_context),
                'replies' => $incident->replies->map(fn (IncidentReply $reply) => $this->reply($reply))->all(),
                'related_items' => $incident->relatedItems
                    ->map(fn (IncidentRelatedItem $item) => $this->relatedItem($item))
                    ->all(),
                'language' => $this->nullableString($incident->language),
                'reporter_notes' => [
                    'label' => 'REPORTER-PROVIDED CONTEXT',
                    'notes' => $this->nullableString($incident->reporter_notes),
                ],
                'reported_safety_classification' => [
                    'label' => 'Reported / captured classification',
                    'value' => $this->nullableString($incident->safety_classification)
                        ?? Incident::CLASSIFICATION_UNCLASSIFIED,
                    'note' => 'Distinct from AI suggested classification and human reviewer classification when those differ.',
                ],
            ],
            'ai_analysis' => [
                'label' => 'AI-GENERATED ANALYSIS',
                'advisory' => true,
                'disclaimer' => $this->safetyGuidance->aiDisclaimer(),
                'current' => $this->aiAnalysis($currentAnalysis),
                'previous' => $previousAnalyses
                    ->map(fn (IncidentAiAnalysis $analysis) => $this->aiAnalysisSummary($analysis))
                    ->all(),
                'uncertainty' => $this->aiUncertainty($currentAnalysis),
            ],
            'human_review' => $this->humanReview($incident),
            'references' => $this->references($incident),
            'reporting_route' => array_merge(
                ['label' => 'REPORTING GUIDANCE'],
                $this->reportingRoutes->forPlatform((string) $incident->platform)
            ),
            'safety_privacy_notes' => [
                'label' => 'SAFETY & PRIVACY',
                'notes' => $this->safetyGuidance->notes(),
                'reporting_disclaimer' => $this->safetyGuidance->reportingDisclaimer(),
            ],
            'disclaimers' => [
                'ai' => $this->safetyGuidance->aiDisclaimer(),
                'human_review' => $this->safetyGuidance->humanReviewDisclaimer(),
                'reporting' => $this->safetyGuidance->reportingDisclaimer(),
                'outcome_tracking' => 'Outcome tracking records externally reported information as entered by authorized users. '
                    .'UmmahOS does not automatically submit reports or verify external platform decisions unless explicitly recorded.',
            ],
            'outcome_tracking' => [
                'label' => 'OUTCOME TRACKING',
                'disclaimer' => 'Recorded external reporting outcomes — not automatically verified by UmmahOS.',
                'reports' => $this->outcomes->serializeForPackage($incident),
            ],
        ];

        return new IncidentEvidencePackage($payload);
    }

    public function loadIncident(Organization $organization, int $incidentId): Incident
    {
        return $organization->incidents()
            ->with([
                'organization',
                'reporter',
                'classifier',
                'currentReviewer',
                'escalatedByUser',
                'replies',
                'relatedItems',
                'aiAnalyses' => fn ($q) => $q->orderByDesc('id'),
                'reviews' => fn ($q) => $q->with('reviewer')->orderByDesc('id'),
                'reviewActions' => fn ($q) => $q->with('actor')->orderBy('id'),
                'contextRequests' => fn ($q) => $q->with(['requester', 'resolver'])->orderBy('id'),
                'externalReports' => fn ($q) => $q->with(['statusHistory', 'appeals'])->orderBy('reported_at')->orderBy('id'),
            ])
            ->findOrFail($incidentId);
    }

    /**
     * Deterministic package version derived from source timestamps (not a mutation counter).
     */
    private function packageVersion(Incident $incident): int
    {
        $timestamps = collect([
            optional($incident->updated_at)?->getTimestamp(),
            $incident->replies->max(fn (IncidentReply $reply) => optional($reply->updated_at)?->getTimestamp()),
            $incident->relatedItems->max(fn (IncidentRelatedItem $item) => optional($item->updated_at)?->getTimestamp()),
            $incident->aiAnalyses->max(fn (IncidentAiAnalysis $analysis) => optional($analysis->updated_at)?->getTimestamp()),
            $incident->reviews->max(fn (IncidentReview $review) => optional($review->updated_at)?->getTimestamp()),
            $incident->reviewActions->max(fn (IncidentReviewAction $action) => optional($action->created_at)?->getTimestamp()),
            $incident->contextRequests->max(fn (IncidentContextRequest $request) => optional($request->updated_at)?->getTimestamp()),
            $incident->externalReports->max(fn (IncidentExternalReport $report) => optional($report->updated_at)?->getTimestamp()),
        ])->filter()->values();

        if ($timestamps->isEmpty()) {
            return 1;
        }

        return max(1, (int) $timestamps->max());
    }

    /**
     * @return array<string, mixed>
     */
    private function incidentMetadata(Incident $incident): array
    {
        return [
            'reference' => $this->incidentReference($incident),
            'submitted_at' => optional($incident->created_at)?->toIso8601String(),
            'observed_at' => optional($incident->observed_at)?->toIso8601String(),
            'original_item_posted_at' => optional($incident->original_item_posted_at)?->toIso8601String(),
            'status' => $this->nullableString($incident->status),
            'review_outcome' => $this->nullableString($incident->review_outcome),
            'content_type' => $this->nullableString($incident->content_type),
            'visibility' => $this->nullableString($incident->visibility),
            'platform' => $this->nullableString($incident->platform),
            'language' => $this->nullableString($incident->language),
            'source_url' => $this->nullableString($incident->source_url),
            'description' => $this->nullableString($incident->description),
        ];
    }

    private function incidentReference(Incident $incident): string
    {
        $slug = $incident->organization?->slug ?: 'org';

        return sprintf('CS-%s-%d', strtoupper($slug), $incident->id);
    }

    /**
     * @return array<string, mixed>
     */
    private function originalItem(Incident $incident): array
    {
        return [
            'title' => $this->nullableString($incident->original_item_title),
            'content' => $this->nullableString($incident->original_item_content),
            'author' => $this->nullableString($incident->original_item_author),
            'reference_url' => $this->nullableString($incident->source_url),
            'posted_at' => optional($incident->original_item_posted_at)?->toIso8601String(),
            'observed_at' => optional($incident->observed_at)?->toIso8601String(),
            'platform' => $this->nullableString($incident->platform),
            'content_type' => $this->nullableString($incident->content_type),
            'visibility' => $this->nullableString($incident->visibility),
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function reply(IncidentReply $reply): array
    {
        return [
            'position' => $reply->position,
            'author' => $this->nullableString($reply->author),
            'content' => $this->nullableString($reply->content),
            'posted_at' => optional($reply->posted_at)?->toIso8601String(),
            'label' => 'Reply',
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function relatedItem(IncidentRelatedItem $item): array
    {
        return [
            'label' => 'RELATED EVIDENCE',
            'platform' => $this->nullableString($item->platform),
            'content_type' => $this->nullableString($item->content_type),
            'reference_url' => $this->nullableString($item->reference_url),
            'description' => $this->nullableString($item->description),
            'observed_at' => optional($item->observed_at)?->toIso8601String(),
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function aiAnalysis(?IncidentAiAnalysis $analysis): array
    {
        if ($analysis === null) {
            return [
                'status' => 'not_available',
                'provider' => null,
                'model' => null,
                'prompt_version' => null,
                'generated_at' => null,
                'error_message' => null,
                'signals' => [],
                'classification' => null,
                'confidence' => null,
                'uncertainty' => null,
                'alternative_interpretation' => null,
                'recommended_action' => null,
                'note' => 'No AI Context Analysis is available for this incident.',
            ];
        }

        if ($analysis->status !== IncidentAiAnalysis::STATUS_COMPLETED) {
            return [
                'status' => $analysis->status,
                'provider' => $this->nullableString($analysis->provider),
                'model' => $this->nullableString($analysis->model),
                'prompt_version' => $this->nullableString($analysis->prompt_version),
                'generated_at' => optional($analysis->created_at)?->toIso8601String(),
                'error_message' => $this->nullableString($analysis->error_message)
                    ?? 'Analysis could not be completed.',
                'signals' => [],
                'classification' => null,
                'confidence' => null,
                'uncertainty' => null,
                'alternative_interpretation' => null,
                'recommended_action' => null,
                'note' => 'AI Context Analysis is unavailable or incomplete.',
            ];
        }

        $package = is_array($analysis->analysis) ? $analysis->analysis : [];

        return [
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'provider' => $this->nullableString($analysis->provider),
            'model' => $this->nullableString($analysis->model),
            'prompt_version' => $this->nullableString($analysis->prompt_version),
            'generated_at' => optional($analysis->created_at)?->toIso8601String(),
            'error_message' => null,
            'signals' => array_values($package['signals'] ?? []),
            'classification' => $package['classification'] ?? null,
            'confidence' => data_get($package, 'classification.confidence'),
            'uncertainty' => $package['uncertainty'] ?? null,
            'alternative_interpretation' => $this->nullableString(
                isset($package['alternative_interpretation']) ? (string) $package['alternative_interpretation'] : null
            ),
            'recommended_action' => $package['recommended_action'] ?? null,
            'note' => 'AI analysis is advisory only and is not the final determination.',
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function aiAnalysisSummary(IncidentAiAnalysis $analysis): array
    {
        return [
            'status' => $analysis->status,
            'provider' => $this->nullableString($analysis->provider),
            'model' => $this->nullableString($analysis->model),
            'prompt_version' => $this->nullableString($analysis->prompt_version),
            'generated_at' => optional($analysis->created_at)?->toIso8601String(),
            'superseded' => true,
            'note' => 'Historical analysis — superseded by a later AI result when a current analysis exists.',
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function aiUncertainty(?IncidentAiAnalysis $analysis): array
    {
        if ($analysis === null || $analysis->status !== IncidentAiAnalysis::STATUS_COMPLETED) {
            return [
                'confidence' => 'Not provided',
                'uncertainty' => 'Not provided',
                'interpretation_note' => 'Not provided',
            ];
        }

        $package = is_array($analysis->analysis) ? $analysis->analysis : [];

        return [
            'confidence' => data_get($package, 'classification.confidence') ?: 'Not provided',
            'uncertainty' => data_get($package, 'uncertainty.level') ?: 'Not provided',
            'interpretation_note' => data_get($package, 'uncertainty.explanation') ?: 'Not provided',
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function humanReview(Incident $incident): array
    {
        $currentReview = $incident->reviews->firstWhere('is_current', true)
            ?? $incident->reviews->first();

        $reviewed = $incident->review_outcome !== null || $currentReview !== null;

        return [
            'label' => 'HUMAN REVIEW',
            'authoritative' => true,
            'disclaimer' => $this->safetyGuidance->humanReviewDisclaimer(),
            'status' => $reviewed ? 'reviewed' : 'not_yet_reviewed',
            'reviewer' => $this->personName(
                $currentReview?->reviewer ?? $incident->currentReviewer
            ),
            'review_started_at' => optional($incident->review_started_at)?->toIso8601String(),
            'review_completed_at' => $incident->status === Incident::STATUS_RESOLVED
                ? optional($incident->updated_at)?->toIso8601String()
                : null,
            'outcome' => $this->nullableString($incident->review_outcome)
                ?? ($reviewed ? $this->nullableString($currentReview?->outcome) : null),
            'human_classification' => $this->nullableString(
                $currentReview?->safety_classification ?? $incident->safety_classification
            ),
            'notes' => $this->nullableString($currentReview?->notes ?? $incident->review_notes),
            'escalation' => [
                'escalated' => (bool) $incident->escalated,
                'escalated_by' => $this->personName($incident->escalatedByUser),
                'escalated_at' => optional($incident->escalated_at)?->toIso8601String(),
                'reason' => $this->nullableString($incident->escalation_reason),
                'note' => 'Escalation is an internal workflow state. This package does not claim external reporting occurred.',
            ],
            'context_requests' => $incident->contextRequests
                ->map(fn (IncidentContextRequest $request) => [
                    'requested_by' => $this->personName($request->requester),
                    'requested_at' => optional($request->requested_at)?->toIso8601String(),
                    'reason' => $this->nullableString($request->reason),
                    'status' => $this->nullableString($request->status),
                    'resolved_by' => $this->personName($request->resolver),
                    'resolved_at' => optional($request->resolved_at)?->toIso8601String(),
                ])
                ->all(),
            'history' => $incident->reviewActions
                ->map(fn (IncidentReviewAction $action) => [
                    'at' => optional($action->created_at)?->toIso8601String(),
                    'actor' => $this->personName($action->actor),
                    'action' => $this->nullableString($action->action),
                    'summary' => $this->reviewActionSummary($action),
                    'notes' => $this->nullableString($action->notes),
                ])
                ->all(),
            'decision' => [
                'outcome' => $this->nullableString($incident->review_outcome),
                'classification' => $this->nullableString(
                    $currentReview?->safety_classification ?? (
                        $incident->review_outcome === Incident::OUTCOME_CONFIRMED
                            ? $incident->safety_classification
                            : null
                    )
                ),
                'reviewer' => $this->personName(
                    $currentReview?->reviewer ?? $incident->currentReviewer
                ),
                'reviewed_at' => optional(
                    $currentReview?->updated_at ?? $incident->classified_at ?? $incident->review_started_at
                )?->toIso8601String(),
                'rationale' => $this->nullableString($currentReview?->notes ?? $incident->review_notes),
                'uncertain_prominence' => $incident->review_outcome === Incident::OUTCOME_UNCERTAIN
                    ? 'UNCERTAIN'
                    : null,
            ],
        ];
    }

    /**
     * @return list<array{type: string, label: string, url: string|null, note: string|null}>
     */
    private function references(Incident $incident): array
    {
        $refs = [];

        $refs[] = [
            'type' => 'original',
            'label' => 'Original item',
            'url' => $this->nullableString($incident->source_url),
            'note' => $incident->source_url
                ? 'Captured reference only — not fetched or verified by UmmahOS.'
                : 'No external reference provided.',
        ];

        foreach ($incident->replies as $index => $reply) {
            $refs[] = [
                'type' => 'reply',
                'label' => 'Reply '.($index + 1),
                'url' => null,
                'note' => 'Reply evidence is captured as text; no separate external URL was stored.',
            ];
        }

        foreach ($incident->relatedItems as $index => $item) {
            $refs[] = [
                'type' => 'related_item',
                'label' => 'Related item '.($index + 1),
                'url' => $this->nullableString($item->reference_url),
                'note' => $item->reference_url
                    ? 'Related evidence reference — captured data only, not fetched or verified.'
                    : 'No external reference provided.',
            ];
        }

        return $refs;
    }

    private function reviewActionSummary(IncidentReviewAction $action): string
    {
        return match ($action->action) {
            IncidentReviewAction::ACTION_STARTED => 'Reviewer started review',
            IncidentReviewAction::ACTION_CONFIRMED => 'Reviewer confirmed incident',
            IncidentReviewAction::ACTION_MARKED_UNCERTAIN => 'Reviewer marked incident uncertain',
            IncidentReviewAction::ACTION_CLOSED => 'Reviewer closed review',
            IncidentReviewAction::ACTION_ESCALATED => 'Reviewer escalated incident',
            IncidentReviewAction::ACTION_CONTEXT_REQUESTED => 'Additional context requested',
            IncidentReviewAction::ACTION_CONTEXT_FULFILLED => 'Context request fulfilled',
            IncidentReviewAction::ACTION_CONTEXT_CANCELLED => 'Context request cancelled',
            IncidentReviewAction::ACTION_NOTES_UPDATED => 'Reviewer notes updated',
            default => 'Review action recorded',
        };
    }

    private function personName(?User $user): ?string
    {
        return $user?->name;
    }

    private function nullableString(mixed $value): ?string
    {
        if ($value === null) {
            return null;
        }

        if ($value instanceof Carbon) {
            return $value->toIso8601String();
        }

        $string = trim((string) $value);

        return $string === '' ? null : $string;
    }
}
