<?php

namespace Tests\Feature\Community;

use App\Models\Resource;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ResourceTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_view_own_organization_resources(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $resource = Resource::factory()->create([
            'organization_id' => $organization->id,
            'title' => 'Alpha prayer timetable',
            'url' => 'https://example.com/alpha/prayer',
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'resources'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $resource->id);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'resources/'.$resource->id))
            ->assertOk()
            ->assertJsonPath('data.url', 'https://example.com/alpha/prayer');
    }

    public function test_cross_organization_resource_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $betaResource = Resource::factory()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta housing list',
            'created_by' => $betaAdmin->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'resources'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'resources/'.$betaResource->id))
            ->assertNotFound();
    }

    public function test_admin_can_create_update_and_delete_resources(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        $created = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'resources'), [
                'title' => 'Campus map',
                'description' => 'MSA rooms',
                'url' => 'https://example.com/map',
                'category' => 'community',
            ])
            ->assertCreated()
            ->assertJsonPath('data.title', 'Campus map');

        $id = $created->json('data.id');

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'resources/'.$id), [
                'title' => 'Updated map',
            ])
            ->assertOk()
            ->assertJsonPath('data.title', 'Updated map');

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'resources/'.$id))
            ->assertOk();

        $this->assertDatabaseMissing('resources', ['id' => $id]);
    }

    public function test_member_cannot_manage_resources(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $resource = Resource::factory()->create([
            'organization_id' => $organization->id,
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'resources'), [
                'title' => 'Nope',
                'url' => 'https://example.com',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, 'resources/'.$resource->id), [
                'title' => 'Nope',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->deleteJson($this->orgUrl($organization, 'resources/'.$resource->id))
            ->assertForbidden();
    }
}
