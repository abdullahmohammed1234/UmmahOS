<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentContextRequest;
use App\Models\IncidentEvidenceExport;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
use App\Models\IncidentReview;
use App\Models\IncidentReviewAction;
use App\Models\Role;
use App\Prompts\CommunityShieldContextAnalysisV1;
use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentEvidencePackageTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_export_permission_exists_and_is_granted_to_reviewer_and_admin(): void
    {
        $this->assertContains(Permissions::INCIDENTS_EXPORT, Permissions::slugs());

        $reviewer = Role::communitySafetyReviewer();
        $this->assertTrue(
            $reviewer->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_EXPORT)
        );

        $admin = Role::admin();
        $this->assertTrue(
            $admin->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_EXPORT)
        );

        $member = Role::member();
        $this->assertFalse(
            $member->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_EXPORT)
        );
    }

    public function test_package_generates_with_full_sections_and_preserves_ai_human_separation(): void
    {
        $organization = $this->createOrganization(['name' => 'Demo MSA Alpha', 'slug' => 'demo-msa-alpha']);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = $this->makeRichIncident($organization, $reviewer);

        $response = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk();

        $data = $response->json('data');

        $this->assertSame(1, $data['package']['schema_version']);
        $this->assertSame('Demo MSA Alpha', $data['package']['organization']['name']);
        $this->assertSame($reviewer->name, $data['package']['generated_by']['name']);
        $this->assertStringContainsString('CS-DEMO-MSA-ALPHA', $data['incident']['reference']);

        $this->assertSame('x', $data['incident']['platform']);
        $this->assertSame('comment', $data['incident']['content_type']);
        $this->assertSame('public', $data['incident']['visibility']);
        $this->assertNotNull($data['evidence']['original_item']['content']);
        $this->assertNotNull($data['evidence']['surrounding_context']);
        $this->assertCount(2, $data['evidence']['replies']);
        $this->assertCount(1, $data['evidence']['related_items']);
        $this->assertSame('en', $data['evidence']['language']);
        $this->assertNotNull($data['evidence']['reporter_notes']['notes']);

        $this->assertTrue($data['ai_analysis']['advisory']);
        $this->assertSame('completed', $data['ai_analysis']['current']['status']);
        $this->assertSame('fake', $data['ai_analysis']['current']['provider']);
        $this->assertSame(CommunityShieldContextAnalysisV1::VERSION, $data['ai_analysis']['current']['prompt_version']);
        $this->assertSame('potential_hate', $data['ai_analysis']['current']['classification']['label']);
        $this->assertSame('moderate', $data['ai_analysis']['uncertainty']['confidence']);
        $this->assertSame('high', $data['ai_analysis']['uncertainty']['uncertainty']);

        $this->assertTrue($data['human_review']['authoritative']);
        $this->assertSame('confirmed', $data['human_review']['outcome']);
        $this->assertSame(Incident::CLASSIFICATION_HATE, $data['human_review']['human_classification']);
        $this->assertNotEmpty($data['human_review']['history']);
        $this->assertNotEmpty($data['references']);
        $this->assertSame('x', $data['reporting_route']['platform']);
        $this->assertFalse($data['reporting_route']['automatic_submission']);
        $this->assertNotEmpty($data['safety_privacy_notes']['notes']);

        $this->assertNotSame(
            $data['ai_analysis']['current']['classification']['label'],
            $data['human_review']['human_classification']
        );
        $this->assertStringContainsString('advisory', strtolower($data['ai_analysis']['disclaimer']));
        $this->assertStringContainsString('authoritative', strtolower($data['human_review']['disclaimer']));
    }

    public function test_package_handles_missing_ai_review_replies_and_urls(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'platform' => Incident::PLATFORM_OTHER,
            'source_url' => null,
            'language' => null,
            'reporter_notes' => null,
            'surrounding_context' => null,
            'original_item_content' => null,
            'review_outcome' => null,
            'status' => Incident::STATUS_OPEN,
        ]);

        $data = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk()
            ->json('data');

        $this->assertSame('not_available', $data['ai_analysis']['current']['status']);
        $this->assertSame('Not provided', $data['ai_analysis']['uncertainty']['uncertainty']);
        $this->assertSame('not_yet_reviewed', $data['human_review']['status']);
        $this->assertNull($data['human_review']['outcome']);
        $this->assertSame([], $data['evidence']['replies']);
        $this->assertSame([], $data['evidence']['related_items']);
        $this->assertNull($data['incident']['source_url']);
        $this->assertSame('other', $data['reporting_route']['platform']);
        $this->assertStringContainsString('current safety/reporting', $data['reporting_route']['recommended_route']);
    }

    public function test_ai_unavailable_and_uncertain_outcome_are_represented_honestly(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'status' => Incident::STATUS_REVIEWING,
            'review_outcome' => Incident::OUTCOME_UNCERTAIN,
            'review_notes' => 'Need more replies.',
            'current_reviewer_id' => $reviewer->id,
        ]);

        IncidentAiAnalysis::query()->create([
            'incident_id' => $incident->id,
            'provider' => 'gemini',
            'model' => 'gemini-test',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_FAILED,
            'analysis' => null,
            'error_message' => 'Analysis could not be completed.',
            'requested_by' => $reviewer->id,
        ]);

        IncidentReview::query()->create([
            'incident_id' => $incident->id,
            'reviewer_id' => $reviewer->id,
            'outcome' => IncidentReview::OUTCOME_UNCERTAIN,
            'notes' => 'Need more replies.',
            'is_current' => true,
        ]);

        $data = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk()
            ->json('data');

        $this->assertSame('failed', $data['ai_analysis']['current']['status']);
        $this->assertSame('gemini', $data['ai_analysis']['current']['provider']);
        $this->assertSame('uncertain', $data['human_review']['outcome']);
        $this->assertSame('UNCERTAIN', $data['human_review']['decision']['uncertain_prominence']);
    }

    public function test_organization_isolation_and_idor_are_enforced(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaReviewer = $this->createMember($alpha, $this->reviewerRole);
        $betaReviewer = $this->createMember($beta, $this->reviewerRole);
        $outsider = $this->createMember($this->createOrganization(), $this->memberRole);

        $alphaIncident = Incident::factory()->create(['organization_id' => $alpha->id]);
        $betaIncident = Incident::factory()->create(['organization_id' => $beta->id]);

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$alphaIncident->id.'/evidence-package'))
            ->assertOk();

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$betaIncident->id.'/evidence-package'))
            ->assertNotFound();

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($beta, '/community-shield/reports/'.$betaIncident->id.'/evidence-package'))
            ->assertForbidden();

        $this->actingAsApi($betaReviewer)
            ->getJson($this->orgUrl($beta, '/community-shield/reports/'.$betaIncident->id.'/evidence-package'))
            ->assertOk();

        $this->actingAsApi($betaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$alphaIncident->id.'/evidence-package'))
            ->assertForbidden();

        $this->actingAsApi($outsider)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$alphaIncident->id.'/evidence-package'))
            ->assertForbidden();
    }

    public function test_member_cannot_export_and_admin_can_export(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertForbidden();

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk();
    }

    public function test_export_is_read_only_and_records_audit_without_mutating_incident(): void
    {
        $organization = $this->createOrganization(['slug' => 'alpha']);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = $this->makeRichIncident($organization, $reviewer);

        $before = $incident->fresh();

        $this->actingAsApi($reviewer)
            ->get($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package.json'))
            ->assertOk()
            ->assertHeader('content-type', 'application/json; charset=UTF-8');

        $after = $incident->fresh();

        $this->assertSame($before->status, $after->status);
        $this->assertSame($before->review_outcome, $after->review_outcome);
        $this->assertSame($before->safety_classification, $after->safety_classification);
        $this->assertSame($before->review_notes, $after->review_notes);
        $this->assertSame($before->review_lock_version, $after->review_lock_version);
        $this->assertSame(1, $after->aiAnalyses()->count());

        $this->assertDatabaseHas('incident_evidence_exports', [
            'incident_id' => $incident->id,
            'exported_by' => $reviewer->id,
            'format' => IncidentEvidenceExport::FORMAT_JSON,
        ]);
    }

    public function test_json_export_does_not_leak_secrets_or_orm_internals(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole, [
            'password' => 'secret-password',
        ]);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'review_notes' => 'Internal reviewer note',
        ]);

        $json = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk()
            ->json();

        $encoded = json_encode($json);
        $this->assertStringNotContainsString('secret-password', $encoded);
        $this->assertStringNotContainsString('remember_token', $encoded);
        $this->assertStringNotContainsString('api_key', $encoded);
        $this->assertArrayNotHasKey('password', $json['data']['package']['generated_by']);
        $this->assertArrayHasKey('incident', $json['data']);
        $this->assertArrayNotHasKey('organization_id', $json['data']['incident']);
    }

    public function test_pdf_export_returns_pdf_with_key_headings_and_escapes_html(): void
    {
        $organization = $this->createOrganization(['slug' => 'alpha']);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'platform' => Incident::PLATFORM_DISCORD,
            'original_item_content' => '<script>alert("xss")</script> لا أحد يريدكم هنا',
            'surrounding_context' => 'Arabic/Unicode context: اخرجوا من الحرم الجامعي',
            'description' => str_repeat('Long evidence line. ', 80),
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'safety_classification' => Incident::CLASSIFICATION_HATE,
            'review_notes' => 'Confirmed despite AI uncertainty.',
            'current_reviewer_id' => $reviewer->id,
        ]);

        IncidentReply::query()->create([
            'incident_id' => $incident->id,
            'author' => 'mod',
            'content' => str_repeat('Reply body. ', 40),
            'position' => 0,
        ]);

        IncidentAiAnalysis::query()->create([
            'incident_id' => $incident->id,
            'provider' => 'gemini',
            'model' => 'gemini-2.0-flash',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => [
                'signals' => [
                    [
                        'name' => 'religious_identity_targeting',
                        'description' => 'Targets identity',
                        'evidence' => ['لا أحد'],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => ['label' => 'potential_hate', 'confidence' => 'moderate'],
                'uncertainty' => [
                    'level' => 'high',
                    'explanation' => 'Additional context may change interpretation.',
                ],
                'alternative_interpretation' => 'Could be figurative speech.',
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
            'requested_by' => $reviewer->id,
        ]);

        $response = $this->actingAsApi($reviewer)
            ->get($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package.pdf'))
            ->assertOk()
            ->assertHeader('content-type', 'application/pdf');

        $pdf = $response->getContent();
        $this->assertNotEmpty($pdf);
        $this->assertStringStartsWith('%PDF', $pdf);
        $this->assertGreaterThan(1000, strlen($pdf));

        // Escaped content should not appear as raw executable markup in the PDF stream.
        $this->assertStringNotContainsString('<script>alert("xss")</script>', $pdf);

        $this->assertDatabaseHas('incident_evidence_exports', [
            'incident_id' => $incident->id,
            'format' => IncidentEvidenceExport::FORMAT_PDF,
            'exported_by' => $reviewer->id,
        ]);

        $incident->refresh();
        $this->assertSame(Incident::STATUS_RESOLVED, $incident->status);
        $this->assertSame(Incident::OUTCOME_CONFIRMED, $incident->review_outcome);
    }

    public function test_reporting_routes_exist_for_all_supported_platforms(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);

        foreach (Incident::platforms() as $platform) {
            $incident = Incident::factory()->create([
                'organization_id' => $organization->id,
                'platform' => $platform,
            ]);

            $route = $this->actingAsApi($reviewer)
                ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
                ->assertOk()
                ->json('data.reporting_route');

            $this->assertSame($platform, $route['platform']);
            $this->assertNotEmpty($route['recommended_route']);
            $this->assertFalse($route['automatic_submission']);
        }
    }

    public function test_real_gemini_stored_analysis_is_packaged_without_new_provider_call(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        IncidentAiAnalysis::query()->create([
            'incident_id' => $incident->id,
            'provider' => 'gemini',
            'model' => 'gemini-2.0-flash',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => [
                'signals' => [
                    [
                        'name' => 'religious_identity_targeting',
                        'description' => 'Stored Gemini result',
                        'evidence' => ['Friday prayer'],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => ['label' => 'potential_hate', 'confidence' => 'moderate'],
                'uncertainty' => [
                    'level' => 'moderate',
                    'explanation' => 'Stored uncertainty from prior Gemini run.',
                ],
                'alternative_interpretation' => 'Political grievance possible.',
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
            'requested_by' => $reviewer->id,
        ]);

        $current = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/evidence-package'))
            ->assertOk()
            ->json('data.ai_analysis.current');

        $this->assertSame('gemini', $current['provider']);
        $this->assertSame('gemini-2.0-flash', $current['model']);
        $this->assertSame(CommunityShieldContextAnalysisV1::VERSION, $current['prompt_version']);
        $this->assertSame('moderate', $current['confidence']);
        $this->assertSame('moderate', $current['uncertainty']['level']);
        $this->assertSame(1, $incident->fresh()->aiAnalyses()->count());
    }

    /**
     * @return Incident
     */
    private function makeRichIncident($organization, $reviewer): Incident
    {
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'platform' => Incident::PLATFORM_X,
            'content_type' => Incident::CONTENT_TYPE_COMMENT,
            'visibility' => Incident::VISIBILITY_PUBLIC,
            'source_url' => 'https://x.com/example/status/phase7',
            'description' => 'Rich evidence package incident',
            'original_item_title' => 'Campus comment',
            'original_item_content' => "These people don't belong here after Friday prayer.",
            'original_item_author' => '@demo',
            'original_item_posted_at' => now()->subDays(2),
            'observed_at' => now()->subDay(),
            'surrounding_context' => "Before: campus facilities thread.\nReported item: hostile comment.\nAfter: amplifying replies.",
            'language' => 'en',
            'reporter_notes' => 'Saw similar tone earlier.',
            'safety_classification' => Incident::CLASSIFICATION_HATE,
            'classified_by' => $reviewer->id,
            'classified_at' => now()->subHour(),
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'review_notes' => 'Evidence supports classification despite AI uncertainty.',
            'current_reviewer_id' => $reviewer->id,
            'review_started_at' => now()->subHours(2),
            'escalated' => false,
        ]);

        IncidentReply::query()->create([
            'incident_id' => $incident->id,
            'author' => '@ally',
            'content' => 'This is wrong.',
            'posted_at' => now()->subDays(2)->addMinutes(10),
            'position' => 0,
        ]);
        IncidentReply::query()->create([
            'incident_id' => $incident->id,
            'author' => '@demo',
            'content' => 'Keep pushing it.',
            'posted_at' => now()->subDays(2)->addMinutes(20),
            'position' => 1,
        ]);

        IncidentRelatedItem::query()->create([
            'incident_id' => $incident->id,
            'platform' => Incident::PLATFORM_REDDIT,
            'content_type' => Incident::CONTENT_TYPE_POST,
            'reference_url' => 'https://reddit.com/r/example/comments/phase7',
            'description' => 'Related wording on Reddit.',
            'observed_at' => now()->subDay(),
        ]);

        IncidentAiAnalysis::query()->create([
            'incident_id' => $incident->id,
            'provider' => 'fake',
            'model' => 'fake-model',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => [
                'signals' => [
                    [
                        'name' => 'religious_identity_targeting',
                        'description' => 'Targets Friday prayer association.',
                        'evidence' => ['Friday prayer'],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => [
                    'label' => 'potential_hate',
                    'confidence' => 'moderate',
                ],
                'uncertainty' => [
                    'level' => 'high',
                    'explanation' => 'Context may change interpretation.',
                ],
                'alternative_interpretation' => 'Political grievance possible.',
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
            'requested_by' => $reviewer->id,
        ]);

        IncidentReview::query()->create([
            'incident_id' => $incident->id,
            'reviewer_id' => $reviewer->id,
            'outcome' => IncidentReview::OUTCOME_CONFIRMED,
            'notes' => 'Evidence supports classification despite AI uncertainty.',
            'safety_classification' => Incident::CLASSIFICATION_HATE,
            'is_current' => true,
        ]);

        IncidentReviewAction::query()->create([
            'incident_id' => $incident->id,
            'actor_id' => $reviewer->id,
            'action' => IncidentReviewAction::ACTION_STARTED,
            'notes' => 'Started review',
            'created_at' => now()->subHours(2),
        ]);
        IncidentReviewAction::query()->create([
            'incident_id' => $incident->id,
            'actor_id' => $reviewer->id,
            'action' => IncidentReviewAction::ACTION_CONFIRMED,
            'notes' => 'Evidence supports classification despite AI uncertainty.',
            'created_at' => now()->subHour(),
        ]);

        IncidentContextRequest::query()->create([
            'incident_id' => $incident->id,
            'requested_by' => $reviewer->id,
            'reason' => 'Need related Reddit reference.',
            'status' => IncidentContextRequest::STATUS_FULFILLED,
            'requested_at' => now()->subHours(90),
            'resolved_by' => $reviewer->id,
            'resolved_at' => now()->subHours(80),
        ]);

        return $incident->fresh();
    }
}
