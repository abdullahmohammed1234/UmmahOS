<?php

namespace Tests\Feature\Community;

use App\Models\Announcement;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AnnouncementTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_view_own_organization_announcements(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $member = $this->createMember($alpha, $this->memberRole);

        $announcement = Announcement::factory()->create([
            'organization_id' => $alpha->id,
            'title' => 'Alpha jumuah update',
            'created_by' => $member->id,
            'published_at' => now()->subHour(),
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($alpha, 'announcements'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $announcement->id)
            ->assertJsonPath('data.0.title', 'Alpha jumuah update');

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($alpha, 'announcements/'.$announcement->id))
            ->assertOk()
            ->assertJsonPath('data.id', $announcement->id);
    }

    public function test_member_cannot_view_another_organizations_announcements(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $betaAnnouncement = Announcement::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta elections',
            'created_by' => $betaAdmin->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'announcements'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'announcements/'.$betaAnnouncement->id))
            ->assertNotFound();
    }

    public function test_member_cannot_see_unpublished_announcements(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $admin = $this->createMember($organization, $this->adminRole);

        $draft = Announcement::factory()->unpublished()->create([
            'organization_id' => $organization->id,
            'title' => 'Officer draft',
            'created_by' => $admin->id,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'announcements'))
            ->assertOk()
            ->assertJsonCount(0, 'data');

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'announcements/'.$draft->id))
            ->assertNotFound();
    }

    public function test_admin_can_create_update_and_delete_announcement(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        $created = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'announcements'), [
                'title' => 'New gathering',
                'body' => 'Details for members.',
                'published' => true,
            ])
            ->assertCreated()
            ->assertJsonPath('data.title', 'New gathering');

        $id = $created->json('data.id');

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'announcements/'.$id), [
                'title' => 'Updated gathering',
            ])
            ->assertOk()
            ->assertJsonPath('data.title', 'Updated gathering');

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'announcements/'.$id))
            ->assertOk();

        $this->assertDatabaseMissing('announcements', ['id' => $id]);
    }

    public function test_admin_cannot_update_another_organizations_announcement(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $betaAnnouncement = Announcement::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta original',
            'created_by' => $betaAdmin->id,
        ]);

        $this->actingAsApi($alphaAdmin)
            ->patchJson($this->orgUrl($alpha, 'announcements/'.$betaAnnouncement->id), [
                'title' => 'Taken over',
            ])
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->patchJson($this->orgUrl($beta, 'announcements/'.$betaAnnouncement->id), [
                'title' => 'Taken over',
            ])
            ->assertForbidden();

        $this->assertSame('Beta original', $betaAnnouncement->fresh()->title);
    }

    public function test_member_cannot_manage_announcements(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $announcement = Announcement::factory()->create([
            'organization_id' => $organization->id,
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'announcements'), [
                'title' => 'Unauthorized',
                'body' => 'No',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, 'announcements/'.$announcement->id), [
                'title' => 'Unauthorized',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->deleteJson($this->orgUrl($organization, 'announcements/'.$announcement->id))
            ->assertForbidden();
    }
}
