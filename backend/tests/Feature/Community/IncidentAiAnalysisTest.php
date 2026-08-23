<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Services\AI\Providers\FakeAnalysisProvider;
use App\Prompts\CommunityShieldContextAnalysisV1;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Fixtures\AI\EvaluationFixtures;
use Tests\TestCase;

class IncidentAiAnalysisTest extends TestCase
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

    public function test_member_cannot_trigger_or_view_ai_analysis(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analyses"))
            ->assertForbidden();
    }

    public function test_admin_can_trigger_and_retrieve_ai_analysis(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
            'original_item_content' => 'Fictional demo content for analysis.',
            'description' => 'Demo report',
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseAClearPotentialTargeting()['expected_analysis']);

        $created = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->assertJsonPath('data.status', IncidentAiAnalysis::STATUS_COMPLETED)
            ->assertJsonPath('data.provider', 'fake')
            ->assertJsonPath('data.prompt_version', CommunityShieldContextAnalysisV1::VERSION)
            ->assertJsonPath('data.analysis.classification.label', 'potential_hate')
            ->assertJsonPath('data.analysis.uncertainty.level', 'low');

        $analysisId = $created->json('data.id');

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analyses"))
            ->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $analysisId);

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analyses/{$analysisId}"))
            ->assertOk()
            ->assertJsonPath('data.id', $analysisId);
    }

    public function test_cross_org_admin_cannot_trigger_or_view_analysis(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $alphaIncident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseDInsufficientEvidence()['expected_analysis']);

        $this->actingAsApi($alphaAdmin)
            ->postJson($this->orgUrl($alpha, "incidents/{$alphaIncident->id}/ai-analysis"))
            ->assertCreated();

        $analysisId = IncidentAiAnalysis::query()->where('incident_id', $alphaIncident->id)->value('id');

        $this->actingAsApi($betaAdmin)
            ->postJson($this->orgUrl($beta, "incidents/{$alphaIncident->id}/ai-analysis"))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, "incidents/{$alphaIncident->id}/ai-analyses"))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($alpha, "incidents/{$alphaIncident->id}/ai-analyses/{$analysisId}"))
            ->assertForbidden();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, "incidents/{$alphaIncident->id}/ai-analyses/{$analysisId}"))
            ->assertNotFound();
    }

    public function test_provider_failure_is_stored_as_failed_without_fake_success(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
        ]);

        $this->fakeProvider->fail();

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->assertJsonPath('data.status', IncidentAiAnalysis::STATUS_FAILED)
            ->assertJsonPath('data.analysis', null)
            ->assertJsonPath('data.error_message', 'AI analysis unavailable.');

        $this->assertDatabaseHas('incident_ai_analyses', [
            'incident_id' => $incident->id,
            'status' => IncidentAiAnalysis::STATUS_FAILED,
        ]);
    }

    public function test_malformed_provider_output_is_rejected(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
        ]);

        $this->fakeProvider->returnMalformed();

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->assertJsonPath('data.status', IncidentAiAnalysis::STATUS_FAILED);

        $this->assertNull(IncidentAiAnalysis::query()->where('incident_id', $incident->id)->value('analysis'));
    }

    public function test_multiple_analyses_are_created_without_overwriting(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
            'original_item_content' => 'Demo',
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseAClearPotentialTargeting()['expected_analysis']);

        $first = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->json('data.id');

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseBAmbiguousContext()['expected_analysis']);

        $second = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated()
            ->json('data.id');

        $this->assertNotSame($first, $second);
        $this->assertSame(2, IncidentAiAnalysis::query()->where('incident_id', $incident->id)->count());

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analyses"))
            ->assertOk()
            ->assertJsonCount(2, 'data');
    }

    public function test_ai_analysis_does_not_change_human_classification_or_status(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
            'status' => Incident::STATUS_OPEN,
            'safety_classification' => Incident::CLASSIFICATION_HATE,
            'classified_by' => $admin->id,
            'classified_at' => now(),
            'original_item_content' => 'Demo',
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseAClearPotentialTargeting()['expected_analysis']);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
            ->assertCreated();

        $incident->refresh();

        $this->assertSame(Incident::STATUS_OPEN, $incident->status);
        $this->assertSame(Incident::CLASSIFICATION_HATE, $incident->safety_classification);
        $this->assertSame($admin->id, $incident->classified_by);
        $this->assertNotNull($incident->classified_at);
    }

    public function test_organization_id_cannot_be_changed_through_payload(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $admin = $this->createMember($alpha, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $admin->id,
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseDInsufficientEvidence()['expected_analysis']);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($alpha, "incidents/{$incident->id}/ai-analysis"), [
                'organization_id' => $beta->id,
                'incident_id' => 999999,
            ])
            ->assertCreated();

        $analysis = IncidentAiAnalysis::query()->where('incident_id', $incident->id)->firstOrFail();
        $this->assertSame($incident->id, $analysis->incident_id);
        $this->assertSame($alpha->id, $incident->fresh()->organization_id);
    }

    public function test_analysis_cannot_be_accessed_through_another_organizations_incident(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $alphaIncident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
        ]);
        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaAdmin->id,
        ]);

        $this->fakeProvider->respondWith(fn () => EvaluationFixtures::caseAClearPotentialTargeting()['expected_analysis']);

        $analysisId = $this->actingAsApi($alphaAdmin)
            ->postJson($this->orgUrl($alpha, "incidents/{$alphaIncident->id}/ai-analysis"))
            ->assertCreated()
            ->json('data.id');

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, "incidents/{$betaIncident->id}/ai-analyses/{$analysisId}"))
            ->assertNotFound();
    }

    public function test_uncertain_and_high_confidence_fixture_analyses_persist_structured_fields(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
        ]);

        foreach ([
            EvaluationFixtures::caseBAmbiguousContext()['expected_analysis'],
            EvaluationFixtures::caseCRepeatedPattern()['expected_analysis'],
            EvaluationFixtures::caseDInsufficientEvidence()['expected_analysis'],
        ] as $payload) {
            $this->fakeProvider->respondWith(fn () => $payload);

            $response = $this->actingAsApi($admin)
                ->postJson($this->orgUrl($organization, "incidents/{$incident->id}/ai-analysis"))
                ->assertCreated();

            $this->assertSame($payload['uncertainty']['level'], $response->json('data.analysis.uncertainty.level'));
            $this->assertSame($payload['classification']['label'], $response->json('data.analysis.classification.label'));
            $this->assertSame($payload['recommended_action']['type'], $response->json('data.analysis.recommended_action.type'));
            $this->assertIsArray($response->json('data.analysis.signals'));
        }

        $this->assertSame(3, IncidentAiAnalysis::query()->where('incident_id', $incident->id)->count());
    }

    public function test_report_creation_does_not_auto_run_ai_analysis(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $response = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Report without AI.',
            ])
            ->assertCreated();

        $this->assertSame(
            0,
            IncidentAiAnalysis::query()->where('incident_id', $response->json('data.id'))->count()
        );
    }
}
