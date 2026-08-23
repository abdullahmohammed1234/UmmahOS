<?php

namespace Tests\Feature\Community;

use App\Models\Announcement;
use App\Models\Course;
use App\Models\Event;
use App\Models\Incident;
use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CommunityTenantIsolationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_multi_organization_user_sees_only_the_current_organizations_community(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);

        $alphaAnnouncement = Announcement::factory()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha announcement',
            'created_by' => $alphaAdmin->id,
        ]);
        $alphaEvent = Event::factory()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha event',
            'created_by' => $alphaAdmin->id,
        ]);
        $alphaCourse = Course::factory()->published()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha course',
            'created_by' => $alphaAdmin->id,
        ]);
        $alphaIncident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $user->id,
            'description' => 'Alpha incident',
        ]);

        $betaAnnouncement = Announcement::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta announcement',
            'created_by' => $user->id,
        ]);
        $betaEvent = Event::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta event',
            'created_by' => $user->id,
        ]);
        $betaCourse = Course::factory()->published()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta course',
            'created_by' => $user->id,
        ]);
        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $user->id,
            'description' => 'Beta incident',
        ]);

        $this->assertTrue($user->hasRoleIn($alpha, 'member'));
        $this->assertTrue($user->hasRoleIn($beta, 'admin'));
        $this->assertFalse($user->hasPermissionIn($alpha, Permissions::CONTENT_MANAGE));
        $this->assertTrue($user->hasPermissionIn($beta, Permissions::CONTENT_MANAGE));

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'announcements'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $alphaAnnouncement->id)
            ->assertJsonMissing(['title' => 'Beta announcement']);

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'events'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $alphaEvent->id);

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'courses'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $alphaCourse->id);

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'announcements/'.$betaAnnouncement->id))
            ->assertNotFound();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'events/'.$betaEvent->id))
            ->assertNotFound();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'courses/'.$betaCourse->id))
            ->assertNotFound();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertForbidden();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$alphaIncident->id))
            ->assertForbidden();

        $this->actingAsApi($user)
            ->postJson($this->orgUrl($alpha, 'announcements'), [
                'title' => 'Should fail',
                'body' => 'Member cannot manage Alpha content.',
            ])
            ->assertForbidden();
        $this->actingAsApi($user)
            ->postJson($this->orgUrl($alpha, 'events'), [
                'title' => 'Should fail',
                'starts_at' => now()->addDay()->toIso8601String(),
            ])
            ->assertForbidden();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($alpha, 'admin/dashboard'))
            ->assertForbidden();

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($beta, 'announcements'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $betaAnnouncement->id)
            ->assertJsonMissing(['title' => 'Alpha announcement']);

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($beta, 'events/'.$alphaEvent->id))
            ->assertNotFound();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($beta, 'courses/'.$alphaCourse->id))
            ->assertNotFound();
        $this->actingAsApi($user)
            ->getJson($this->orgUrl($beta, 'incidents'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $betaIncident->id)
            ->assertJsonMissing(['description' => 'Alpha incident']);

        $this->actingAsApi($user)
            ->postJson($this->orgUrl($beta, 'announcements'), [
                'title' => 'Beta admin notice',
                'body' => 'Created while operating inside Beta.',
                'published' => true,
            ])
            ->assertCreated();

        $this->actingAsApi($user)
            ->getJson($this->orgUrl($beta, 'admin/dashboard'))
            ->assertOk()
            ->assertJsonPath('data.organization.id', $beta->id)
            ->assertJsonPath('data.counts.members', 1);
    }
}
