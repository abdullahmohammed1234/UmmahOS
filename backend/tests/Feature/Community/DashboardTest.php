<?php

namespace Tests\Feature\Community;

use App\Models\Announcement;
use App\Models\Course;
use App\Models\Event;
use App\Models\Incident;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class DashboardTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_dashboard_only_aggregates_current_organization_data(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        Announcement::factory()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha welcome',
            'created_by' => $alphaMember->id,
        ]);
        Event::factory()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha iftar',
            'created_by' => $alphaMember->id,
            'starts_at' => now()->addDays(2),
        ]);
        Course::factory()->published()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha course',
            'created_by' => $alphaMember->id,
        ]);

        Announcement::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta elections',
            'created_by' => $betaAdmin->id,
        ]);
        Event::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta sports day',
            'created_by' => $betaAdmin->id,
            'starts_at' => now()->addDays(3),
        ]);

        $response = $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'dashboard'))
            ->assertOk()
            ->assertJsonPath('data.organization.id', $alpha->id)
            ->assertJsonPath('data.recent_announcements.0.title', 'Alpha welcome')
            ->assertJsonPath('data.upcoming_events.0.title', 'Alpha iftar')
            ->assertJsonPath('data.academy.courses.0.title', 'Alpha course');

        $payload = json_encode($response->json('data'));
        $this->assertStringNotContainsString('Beta elections', $payload);
        $this->assertStringNotContainsString('Beta sports day', $payload);
    }

    public function test_admin_dashboard_only_aggregates_current_organization_data(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        Event::factory()->create([
            'organization_id' => $alpha->id,
            'created_by' => $alphaAdmin->id,
            'starts_at' => now()->addDay(),
        ]);
        Announcement::factory()->create([
            'organization_id' => $alpha->id,
            'created_by' => $alphaAdmin->id,
        ]);
        Course::factory()->published()->create([
            'organization_id' => $alpha->id,
            'created_by' => $alphaAdmin->id,
        ]);
        Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
            'status' => Incident::STATUS_OPEN,
        ]);

        Event::factory()->count(2)->create([
            'organization_id' => $beta->id,
            'created_by' => $betaAdmin->id,
            'starts_at' => now()->addDays(4),
        ]);
        Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($alpha, 'admin/dashboard'))
            ->assertOk()
            ->assertJsonPath('data.organization.id', $alpha->id)
            ->assertJsonPath('data.counts.members', 1)
            ->assertJsonPath('data.counts.upcoming_events', 1)
            ->assertJsonPath('data.counts.published_announcements', 1)
            ->assertJsonPath('data.counts.published_courses', 1)
            ->assertJsonPath('data.counts.open_incidents', 1)
            ->assertJsonPath('data.counts.reviewing_incidents', 0)
            ->assertJsonPath('data.counts.resolved_incidents', 0);

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($beta, 'admin/dashboard'))
            ->assertForbidden();
    }

    public function test_member_cannot_open_the_admin_dashboard(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'admin/dashboard'))
            ->assertForbidden();
    }
}
