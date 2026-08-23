<?php

namespace Tests\Feature\Community;

use App\Models\Event;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EventTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_view_own_organization_events(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $event = Event::factory()->create([
            'organization_id' => $organization->id,
            'title' => 'Alpha community iftar',
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'events'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $event->id);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'events/'.$event->id))
            ->assertOk()
            ->assertJsonPath('data.title', 'Alpha community iftar');
    }

    public function test_cross_organization_event_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $betaEvent = Event::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta sports day',
            'created_by' => $betaAdmin->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'events'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'events/'.$betaEvent->id))
            ->assertNotFound();
    }

    public function test_admin_can_create_update_and_delete_events(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        $created = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'events'), [
                'title' => 'Study circle',
                'description' => 'Weekly',
                'location' => 'Room 4',
                'starts_at' => now()->addDays(3)->toIso8601String(),
                'ends_at' => now()->addDays(3)->addHours(2)->toIso8601String(),
                'registration_url' => 'https://example.com/register',
            ])
            ->assertCreated()
            ->assertJsonPath('data.title', 'Study circle');

        $id = $created->json('data.id');

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'events/'.$id), [
                'location' => 'Room 12',
            ])
            ->assertOk()
            ->assertJsonPath('data.location', 'Room 12');

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'events/'.$id))
            ->assertOk();

        $this->assertDatabaseMissing('events', ['id' => $id]);
    }

    public function test_member_cannot_manage_events(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $event = Event::factory()->create([
            'organization_id' => $organization->id,
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'events'), [
                'title' => 'Unauthorized',
                'starts_at' => now()->addDay()->toIso8601String(),
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, 'events/'.$event->id), [
                'title' => 'Unauthorized',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->deleteJson($this->orgUrl($organization, 'events/'.$event->id))
            ->assertForbidden();
    }
}
