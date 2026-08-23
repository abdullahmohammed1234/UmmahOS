<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_submit_incident(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'source_url' => 'https://x.com/example/status/1',
                'description' => 'Someone shared a concerning public post.',
            ])
            ->assertCreated()
            ->assertJsonPath('data.platform', Incident::PLATFORM_X)
            ->assertJsonPath('data.content_type', Incident::CONTENT_TYPE_POST)
            ->assertJsonPath('data.visibility', Incident::VISIBILITY_PUBLIC)
            ->assertJsonPath('data.source_url', 'https://x.com/example/status/1')
            ->assertJsonPath('data.status', Incident::STATUS_OPEN)
            ->assertJsonPath('data.reported_by.id', $member->id)
            ->assertJsonPath('message', 'Your report has been received by your MSA\'s Community Shield team.');
    }

    public function test_unauthenticated_user_cannot_create_a_report(): void
    {
        $organization = $this->createOrganization();

        $this->postJson($this->orgUrl($organization, 'incidents'), [
            'platform' => Incident::PLATFORM_X,
            'content_type' => Incident::CONTENT_TYPE_POST,
            'visibility' => Incident::VISIBILITY_PUBLIC,
            'description' => 'Unauthenticated attempt.',
        ])->assertUnauthorized();
    }

    public function test_creation_validation_rejects_invalid_structured_fields(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Missing platform.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['platform']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => 'myspace',
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Invalid platform.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['platform']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Missing content type.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['content_type']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => 'livestream',
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Invalid content type.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['content_type']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'description' => 'Missing visibility.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['visibility']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => 'secret',
                'description' => 'Invalid visibility.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['visibility']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['description']);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'source_url' => 'not-a-url',
                'description' => 'Invalid source URL.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['source_url']);
    }

    public function test_representative_platform_context_combinations_are_accepted(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $combinations = [
            [Incident::PLATFORM_X, Incident::CONTENT_TYPE_POST, Incident::VISIBILITY_PUBLIC],
            [Incident::PLATFORM_DISCORD, Incident::CONTENT_TYPE_MESSAGE, Incident::VISIBILITY_GROUP],
            [Incident::PLATFORM_WHATSAPP, Incident::CONTENT_TYPE_MESSAGE, Incident::VISIBILITY_PRIVATE],
            [Incident::PLATFORM_TIKTOK, Incident::CONTENT_TYPE_VIDEO, Incident::VISIBILITY_PUBLIC],
        ];

        foreach ($combinations as [$platform, $contentType, $visibility]) {
            $this->actingAsApi($member)
                ->postJson($this->orgUrl($organization, 'incidents'), [
                    'platform' => $platform,
                    'content_type' => $contentType,
                    'visibility' => $visibility,
                    'description' => "Report for {$platform}/{$contentType}/{$visibility}.",
                ])
                ->assertCreated()
                ->assertJsonPath('data.platform', $platform)
                ->assertJsonPath('data.content_type', $contentType)
                ->assertJsonPath('data.visibility', $visibility)
                ->assertJsonPath('data.status', Incident::STATUS_OPEN);
        }
    }

    public function test_report_organization_cannot_be_changed_through_request_payload(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $member = $this->createMember($alpha, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($alpha, 'incidents'), [
                'organization_id' => $beta->id,
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Attempt to reassign organization.',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['organization_id']);

        $this->assertDatabaseMissing('incidents', [
            'organization_id' => $beta->id,
            'description' => 'Attempt to reassign organization.',
        ]);
    }

    public function test_member_cannot_view_another_users_incident(): void
    {
        $organization = $this->createOrganization();
        $reporter = $this->createMember($organization, $this->memberRole);
        $otherMember = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reporter->id,
        ]);

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'incidents/'.$incident->id))
            ->assertForbidden();

        $this->actingAsApi($reporter)
            ->getJson($this->orgUrl($organization, 'incidents/'.$incident->id))
            ->assertForbidden();

        $this->actingAsApi($reporter)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$incident->id), [
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertForbidden();
    }

    public function test_member_cannot_view_another_organizations_incident(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'incidents/'.$betaIncident->id))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertForbidden();
    }

    public function test_admin_can_view_organization_incidents_filter_and_update_status(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);

        $open = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'status' => Incident::STATUS_OPEN,
            'platform' => Incident::PLATFORM_X,
        ]);
        Incident::factory()->reviewing()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'platform' => Incident::PLATFORM_DISCORD,
        ]);

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'incidents'))
            ->assertOk()
            ->assertJsonCount(2, 'data');

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'incidents?status=open'))
            ->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $open->id);

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'incidents/'.$open->id))
            ->assertOk()
            ->assertJsonPath('data.platform', Incident::PLATFORM_X);

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$open->id), [
                'status' => Incident::STATUS_REVIEWING,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', Incident::STATUS_REVIEWING);

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$open->id), [
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', Incident::STATUS_RESOLVED);

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$open->id), [
                'status' => 'archived',
            ])
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['status']);
    }

    public function test_cross_organization_admin_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);
        $alphaIncident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
        ]);

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($beta, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->patchJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id), [
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->patchJson($this->orgUrl($beta, 'incidents/'.$alphaIncident->id), [
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertNotFound();

        $this->assertSame(Incident::STATUS_OPEN, $betaIncident->fresh()->status);
        $this->assertSame(Incident::STATUS_OPEN, $alphaIncident->fresh()->status);
    }

    public function test_community_shield_overview_hides_counts_from_members(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);

        Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'status' => Incident::STATUS_OPEN,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'community-shield'))
            ->assertOk()
            ->assertJsonPath('data.can_report', true)
            ->assertJsonPath('data.can_review', false)
            ->assertJsonMissingPath('data.counts');

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'community-shield'))
            ->assertOk()
            ->assertJsonPath('data.can_review', true)
            ->assertJsonPath('data.counts.open', 1);
    }
}
