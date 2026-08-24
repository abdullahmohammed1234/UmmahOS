<?php

namespace Tests\Feature\Evaluation;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentExternalReport;
use App\Models\IncidentReportAppeal;
use App\Services\AI\Providers\FakeAnalysisProvider;
use App\Services\Evidence\IncidentEvidencePackageService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Fixtures\AI\EvaluationFixtures;
use Tests\TestCase;

/**
 * Phase 10 security-boundary regression tests for Community Shield evaluation surfaces.
 */
class CommunityShieldEvaluationPrivacyBoundaryTest extends TestCase
{
    use RefreshDatabase;

    private FakeAnalysisProvider $fakeProvider;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
        $this->fakeProvider = $this->app->make(FakeAnalysisProvider::class);
        $this->fakeProvider->reset();
    }

    public function test_cross_organization_incident_ai_evidence_and_outcome_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha Eval']);
        $beta = $this->createOrganization(['name' => 'Beta Eval']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $alphaReviewer = $this->createMember($alpha, $this->reviewerRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $incident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
            'platform' => 'x',
            'original_item_content' => 'Synthetic abstract evidence for privacy boundary evaluation.',
            'reporter_notes' => 'Contains PRIVATE_CANARY_BOUNDARY_001',
            'visibility' => Incident::VISIBILITY_PRIVATE,
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseBAmbiguousContext()['expected_analysis']);

        $analysis = $this->actingAsApi($alphaAdmin)
            ->postJson($this->orgUrl($alpha, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->json('data');

        $this->actingAsApi($betaAdmin)
            ->postJson($this->orgUrl($beta, "incidents/{$incident->id}/ai-analysis"))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, "incidents/{$incident->id}/ai-analyses/{$analysis['id']}"))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($alpha, "incidents/{$incident->id}/ai-analyses/{$analysis['id']}"))
            ->assertForbidden();

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, 'community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, 'community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($alpha, 'community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertForbidden();

        $this->actingAsApi($alphaReviewer)
            ->postJson($this->orgUrl($alpha, 'community-shield/reports/'.$incident->id.'/external-reports'), [
                'platform' => 'x',
                'reporting_channel' => 'In-app report',
                'reported_at' => now()->toIso8601String(),
                'reporter_visible_summary' => 'Synthetic summary',
                'internal_notes' => 'Synthetic internal notes with PRIVATE_CANARY_BOUNDARY_001',
            ])
            ->assertCreated();

        $reportId = IncidentExternalReport::query()->where('incident_id', $incident->id)->value('id');

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, 'community-shield/reports/'.$incident->id.'/external-reports'))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($alpha, 'community-shield/reports/'.$incident->id.'/external-reports/'.$reportId))
            ->assertForbidden();
    }

    public function test_member_cannot_access_other_user_incident_reviewer_notes_or_ai_metadata(): void
    {
        $organization = $this->createOrganization();
        $reporter = $this->createMember($organization, $this->memberRole);
        $otherMember = $this->createMember($organization, $this->memberRole);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $admin = $this->createMember($organization, $this->adminRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reporter->id,
            'reporter_notes' => 'PRIVATE_CANARY_MEMBER_001',
            'review_notes' => null,
            'original_item_content' => 'Synthetic content',
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseAClearPotentialTargeting()['expected_analysis']);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated();

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'community-shield/my-reports/'.$incident->id))
            ->assertNotFound();

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analyses"))
            ->assertForbidden();

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertForbidden();

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $incident->refresh();

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/review/uncertain'), [
                'notes' => 'Synthetic reviewer-only uncertain note PRIVATE_CANARY_REVIEW_001',
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertOk();

        $ownerView = $this->actingAsApi($reporter)
            ->getJson($this->orgUrl($organization, 'community-shield/my-reports/'.$incident->id))
            ->assertOk()
            ->json('data');

        $encoded = json_encode($ownerView);
        $this->assertStringNotContainsString('PRIVATE_CANARY_REVIEW_001', $encoded);
        $this->assertArrayNotHasKey('review_notes', $ownerView);
        $this->assertArrayNotHasKey('latest_ai_analysis', $ownerView);
        $this->assertArrayNotHasKey('ai_analyses', $ownerView);
    }

    public function test_evidence_export_does_not_enable_automatic_submission_and_keeps_canary_scoped(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reviewer->id,
            'platform' => 'whatsapp',
            'visibility' => Incident::VISIBILITY_PRIVATE,
            'reporter_notes' => 'Synthetic private note PRIVATE_CANARY_EXPORT_001',
            'original_item_content' => 'Synthetic private abstract evidence',
            'status' => Incident::STATUS_REVIEWING,
            'review_outcome' => Incident::OUTCOME_UNCERTAIN,
            'review_notes' => 'Human uncertain determination',
            'current_reviewer_id' => $reviewer->id,
        ]);

        IncidentAiAnalysis::query()->create([
            'incident_id' => $incident->id,
            'provider' => 'fake',
            'model' => 'fake-model',
            'prompt_version' => 'community_shield_context_v1',
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => EvaluationFixtures::caseBAmbiguousContext()['expected_analysis'],
            'requested_by' => $reviewer->id,
        ]);

        $package = $this->app->make(IncidentEvidencePackageService::class)
            ->buildFromIncident($incident->fresh(['replies', 'relatedItems', 'aiAnalyses', 'reviews', 'reviewActions', 'contextRequests', 'organization', 'externalReports']), $reviewer)
            ->toArray();

        $this->assertFalse($package['reporting_route']['automatic_submission']);
        $this->assertTrue($package['ai_analysis']['advisory']);
        $this->assertTrue($package['human_review']['authoritative']);
        $this->assertSame('private', $package['incident']['visibility']);
        $this->assertStringContainsString('PRIVATE_CANARY_EXPORT_001', (string) data_get($package, 'evidence.reporter_notes.notes'));
        $this->assertStringNotContainsString('PRIVATE_CANARY_EXPORT_001', json_encode($package['reporting_route']));
    }

    public function test_unauthorized_appeal_access_is_blocked_across_users_and_orgs(): void
    {
        $organization = $this->createOrganization();
        $otherOrg = $this->createOrganization(['name' => 'Other']);
        $reporter = $this->createMember($organization, $this->memberRole);
        $stranger = $this->createMember($organization, $this->memberRole);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $otherAdmin = $this->createMember($otherOrg, $this->adminRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reporter->id,
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
        ]);

        $external = IncidentExternalReport::query()->create([
            'incident_id' => $incident->id,
            'organization_id' => $organization->id,
            'platform' => 'x',
            'reporting_channel' => 'In-app report',
            'reported_at' => now(),
            'status' => IncidentExternalReport::STATUS_OUTCOME,
            'decision' => IncidentExternalReport::DECISION_NO_ACTION,
            'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
            'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
            'created_by' => $reviewer->id,
            'updated_by' => $reviewer->id,
        ]);

        $appeal = IncidentReportAppeal::query()->create([
            'incident_external_report_id' => $external->id,
            'submitted_at' => now(),
            'submitted_by' => $reporter->id,
            'reason' => 'Synthetic appeal',
            'status' => IncidentReportAppeal::STATUS_SUBMITTED,
        ]);

        $this->actingAsApi($stranger)
            ->postJson($this->orgUrl($organization, 'community-shield/my-reports/'.$incident->id.'/external-reports/'.$external->id.'/appeals'), [
                'reason' => 'Should be forbidden',
            ])
            ->assertStatus(422);

        $this->actingAsApi($otherAdmin)
            ->patchJson($this->orgUrl($otherOrg, 'community-shield/reports/'.$incident->id.'/external-reports/'.$external->id.'/appeals/'.$appeal->id), [
                'status' => IncidentReportAppeal::STATUS_REJECTED,
                'response' => 'Nope',
            ])
            ->assertNotFound();
    }
}
