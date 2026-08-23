<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentContextCaptureTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_original_item_fields_and_long_content_are_preserved(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $longContent = str_repeat('Context capture content. ', 200);

        $response = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Structured original item report.',
                'original_item_title' => 'Demo post title',
                'original_item_content' => $longContent.'<script>alert(1)</script>',
                'original_item_author' => '@demo_account',
                'original_item_posted_at' => '2026-08-20T14:30:00+00:00',
            ])
            ->assertCreated();

        $response
            ->assertJsonPath('data.original_item_title', 'Demo post title')
            ->assertJsonPath('data.original_item_author', '@demo_account')
            ->assertJsonPath('data.original_item_content', $longContent.'<script>alert(1)</script>');

        $this->assertStringContainsString('<script>', $response->json('data.original_item_content'));
        $this->assertSame(
            \Illuminate\Support\Carbon::parse('2026-08-20T14:30:00+00:00')->utc()->timestamp,
            \Illuminate\Support\Carbon::parse($response->json('data.original_item_posted_at'))->utc()->timestamp
        );
    }

    public function test_timestamps_preserve_explicit_values_and_default_observed_at(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $withObserved = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_YOUTUBE,
                'content_type' => Incident::CONTENT_TYPE_COMMENT,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Explicit observation time.',
                'original_item_posted_at' => '2026-08-18T17:00:00Z',
                'observed_at' => '2026-08-19T18:15:00Z',
            ])
            ->assertCreated();

        $this->assertSame(
            \Illuminate\Support\Carbon::parse('2026-08-18T17:00:00Z')->utc()->timestamp,
            \Illuminate\Support\Carbon::parse($withObserved->json('data.original_item_posted_at'))->utc()->timestamp
        );
        $this->assertSame(
            \Illuminate\Support\Carbon::parse('2026-08-19T18:15:00Z')->utc()->timestamp,
            \Illuminate\Support\Carbon::parse($withObserved->json('data.observed_at'))->utc()->timestamp
        );

        $incident = Incident::query()->findOrFail($withObserved->json('data.id'));
        $this->assertTrue(
            $incident->original_item_posted_at->equalTo(\Illuminate\Support\Carbon::parse('2026-08-18T17:00:00Z'))
        );
        $this->assertTrue(
            $incident->observed_at->equalTo(\Illuminate\Support\Carbon::parse('2026-08-19T18:15:00Z'))
        );

        $withoutObserved = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_REDDIT,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Default observation time.',
            ])
            ->assertCreated();

        $this->assertNotNull($withoutObserved->json('data.observed_at'));
        $this->assertNotNull(Incident::query()->find($withoutObserved->json('data.id'))?->observed_at);
    }

    public function test_surrounding_context_and_reporter_notes_are_optional(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Minimal Phase 3-compatible report.',
            ])
            ->assertCreated()
            ->assertJsonPath('data.surrounding_context', null)
            ->assertJsonPath('data.reporter_notes', null)
            ->assertJsonPath('data.language', Incident::LANGUAGE_UNKNOWN)
            ->assertJsonPath('data.safety_classification', Incident::CLASSIFICATION_UNCLASSIFIED);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_DISCORD,
                'content_type' => Incident::CONTENT_TYPE_MESSAGE,
                'visibility' => Incident::VISIBILITY_GROUP,
                'description' => 'Context-rich report.',
                'surrounding_context' => 'This followed a heated channel argument.',
                'reporter_notes' => 'I saw similar posts earlier today.',
                'language' => 'en',
            ])
            ->assertCreated()
            ->assertJsonPath('data.surrounding_context', 'This followed a heated channel argument.')
            ->assertJsonPath('data.reporter_notes', 'I saw similar posts earlier today.')
            ->assertJsonPath('data.language', 'en');
    }

    public function test_replies_are_created_atomically_with_order_preserved(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $response = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Report with replies.',
                'replies' => [
                    [
                        'author' => 'first',
                        'content' => 'First reply',
                        'posted_at' => '2026-08-20T15:00:00+00:00',
                    ],
                    [
                        'author' => 'second',
                        'content' => 'Second reply',
                        'posted_at' => '2026-08-20T15:05:00+00:00',
                    ],
                ],
            ])
            ->assertCreated();

        $this->assertCount(2, $response->json('data.replies'));
        $this->assertSame('First reply', $response->json('data.replies.0.content'));
        $this->assertSame('Second reply', $response->json('data.replies.1.content'));
        $this->assertSame(0, $response->json('data.replies.0.position'));
        $this->assertSame(1, $response->json('data.replies.1.position'));
        $this->assertSame(1, Incident::query()->count());
        $this->assertSame(2, IncidentReply::query()->count());
    }

    public function test_related_items_support_multiple_platforms(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $response = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Report with related copies.',
                'related_items' => [
                    [
                        'platform' => Incident::PLATFORM_REDDIT,
                        'content_type' => Incident::CONTENT_TYPE_POST,
                        'reference_url' => 'https://reddit.com/r/example/comments/1',
                        'description' => 'Reposted on Reddit.',
                    ],
                    [
                        'platform' => Incident::PLATFORM_TELEGRAM,
                        'content_type' => Incident::CONTENT_TYPE_MESSAGE,
                        'description' => 'Forwarded in Telegram.',
                    ],
                ],
            ])
            ->assertCreated();

        $this->assertCount(2, $response->json('data.related_items'));
        $this->assertSame(Incident::PLATFORM_REDDIT, $response->json('data.related_items.0.platform'));
        $this->assertSame(Incident::PLATFORM_TELEGRAM, $response->json('data.related_items.1.platform'));
        $this->assertSame(2, IncidentRelatedItem::query()->count());
    }

    public function test_language_validation_accepts_supported_and_unknown_values(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Arabic language report.',
                'language' => 'ar',
            ])
            ->assertCreated()
            ->assertJsonPath('data.language', 'ar');

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Unknown language report.',
                'language' => 'unknown',
            ])
            ->assertCreated()
            ->assertJsonPath('data.language', 'unknown');

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Invalid language.',
                'language' => 'xx-invalid',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['language']);
    }

    public function test_admin_can_classify_and_member_cannot(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Attempt to set classification on create.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['safety_classification']);

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$incident->id), [
                'safety_classification' => Incident::CLASSIFICATION_HATE,
            ])
            ->assertForbidden();

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$incident->id), [
                'safety_classification' => Incident::CLASSIFICATION_HATE,
            ])
            ->assertOk()
            ->assertJsonPath('data.safety_classification', Incident::CLASSIFICATION_HATE)
            ->assertJsonPath('data.classified_by.id', $admin->id);

        $this->assertNotNull($incident->fresh()->classified_at);
    }

    public function test_cross_organization_child_record_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $alphaIncident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaMember->id,
        ]);
        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);

        $alphaReply = IncidentReply::factory()->create([
            'incident_id' => $alphaIncident->id,
            'content' => 'Alpha reply',
            'position' => 0,
        ]);
        $betaReply = IncidentReply::factory()->create([
            'incident_id' => $betaIncident->id,
            'content' => 'Beta reply',
            'position' => 0,
        ]);

        $alphaRelated = IncidentRelatedItem::factory()->create([
            'incident_id' => $alphaIncident->id,
            'platform' => Incident::PLATFORM_REDDIT,
            'content_type' => Incident::CONTENT_TYPE_POST,
        ]);
        $betaRelated = IncidentRelatedItem::factory()->create([
            'incident_id' => $betaIncident->id,
            'platform' => Incident::PLATFORM_TELEGRAM,
            'content_type' => Incident::CONTENT_TYPE_MESSAGE,
        ]);

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id))
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->postJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id.'/replies'), [
                'content' => 'Should not attach.',
            ])
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->postJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id.'/replies'), [
                'content' => 'Should not attach.',
            ])
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->deleteJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id.'/replies/'.$betaReply->id))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->deleteJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id.'/replies/'.$alphaReply->id))
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->postJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id.'/related-items'), [
                'platform' => Incident::PLATFORM_TIKTOK,
                'content_type' => Incident::CONTENT_TYPE_VIDEO,
            ])
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->postJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id.'/related-items'), [
                'platform' => Incident::PLATFORM_TIKTOK,
                'content_type' => Incident::CONTENT_TYPE_VIDEO,
            ])
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->deleteJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id.'/related-items/'.$betaRelated->id))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->deleteJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id.'/related-items/'.$alphaRelated->id))
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->patchJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id), [
                'safety_classification' => Incident::CLASSIFICATION_THREAT,
            ])
            ->assertNotFound();

        $this->assertSame(1, $alphaIncident->replies()->count());
        $this->assertSame(1, $betaIncident->replies()->count());
        $this->assertSame(1, $alphaIncident->relatedItems()->count());
        $this->assertSame(1, $betaIncident->relatedItems()->count());
        $this->assertSame(Incident::CLASSIFICATION_UNCLASSIFIED, $betaIncident->fresh()->safety_classification);
    }

    public function test_mass_assignment_cannot_override_organization_or_reporter_identity(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $response = $this->actingAsApi($alphaMember)
            ->postJson($this->orgUrl($alpha, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Mass assignment attempt.',
                'organization_id' => $beta->id,
                'reported_by' => $betaMember->id,
                'classified_by' => $betaMember->id,
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertUnprocessable();

        $response->assertJsonValidationErrors(['organization_id', 'reported_by', 'status', 'classified_by']);

        $this->assertSame(0, Incident::query()->count());
    }

    public function test_admin_can_add_and_delete_child_context_within_organization(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);

        $replyResponse = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'incidents/'.$incident->id.'/replies'), [
                'author' => 'reviewer-added',
                'content' => 'Additional reply evidence.',
            ])
            ->assertCreated();

        $replyId = $replyResponse->json('data.id');

        $relatedResponse = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'incidents/'.$incident->id.'/related-items'), [
                'platform' => Incident::PLATFORM_TIKTOK,
                'content_type' => Incident::CONTENT_TYPE_VIDEO,
                'description' => 'Related video copy.',
            ])
            ->assertCreated();

        $relatedId = $relatedResponse->json('data.id');

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'incidents/'.$incident->id.'/replies/'.$replyId))
            ->assertNoContent();

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'incidents/'.$incident->id.'/related-items/'.$relatedId))
            ->assertNoContent();

        $this->assertSame(0, $incident->replies()->count());
        $this->assertSame(0, $incident->relatedItems()->count());
    }

    public function test_member_cannot_browse_or_view_context_queue(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $other = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $other->id,
            'surrounding_context' => 'Private review context.',
            'reporter_notes' => 'Reporter-only notes.',
            'safety_classification' => Incident::CLASSIFICATION_HATE,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'incidents/'.$incident->id))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents/'.$incident->id.'/replies'), [
                'content' => 'Member should not add replies after submit.',
            ])
            ->assertForbidden();
    }
}
