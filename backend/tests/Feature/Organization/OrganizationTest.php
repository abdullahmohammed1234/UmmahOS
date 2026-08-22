<?php

namespace Tests\Feature\Organization;

use App\Models\Organization;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class OrganizationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_authenticated_user_can_create_an_organization(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAsApi($user)
            ->postJson(route('api.organizations.store'), [
                'name' => 'Campus MSA',
                'slug' => 'campus-msa',
            ]);

        $response->assertCreated()
            ->assertJsonPath('data.name', 'Campus MSA')
            ->assertJsonPath('data.slug', 'campus-msa')
            ->assertJsonPath('data.status', Organization::STATUS_ACTIVE);

        $this->assertDatabaseHas('organizations', [
            'name' => 'Campus MSA',
            'slug' => 'campus-msa',
        ]);

        $organization = Organization::query()->where('slug', 'campus-msa')->first();
        $this->assertTrue($user->fresh()->belongsToOrganization($organization));
        $this->assertTrue($user->fresh()->hasRoleIn($organization, 'admin'));
    }

    public function test_organization_slug_must_be_unique(): void
    {
        $this->createOrganization(['slug' => 'taken-slug']);
        $user = User::factory()->create();

        $this->actingAsApi($user)
            ->postJson(route('api.organizations.store'), [
                'name' => 'Another MSA',
                'slug' => 'taken-slug',
            ])
            ->assertStatus(422)
            ->assertJsonValidationErrors(['slug']);
    }

    public function test_user_only_lists_organizations_they_belong_to(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->adminRole);

        $response = $this->actingAsApi($user)
            ->getJson(route('api.organizations.index'))
            ->assertOk();

        $ids = collect($response->json('data'))->pluck('id');

        $this->assertTrue($ids->contains($alpha->id));
        $this->assertFalse($ids->contains($beta->id));
    }

    public function test_member_can_view_their_organization(): void
    {
        $organization = $this->createOrganization();
        $user = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($user)
            ->getJson(route('api.organizations.show', $organization))
            ->assertOk()
            ->assertJsonPath('data.id', $organization->id);
    }

    public function test_admin_can_update_their_organization(): void
    {
        $organization = $this->createOrganization(['name' => 'Original Name']);
        $admin = $this->createMember($organization, $this->adminRole);

        $this->actingAsApi($admin)
            ->patchJson(route('api.organizations.update', $organization), [
                'name' => 'Updated MSA',
            ])
            ->assertOk()
            ->assertJsonPath('data.name', 'Updated MSA');
    }

    public function test_member_cannot_update_their_organization(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->patchJson(route('api.organizations.update', $organization), [
                'name' => 'Hijacked Name',
            ])
            ->assertForbidden();
    }

    public function test_admin_can_delete_their_organization(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        $this->actingAsApi($admin)
            ->deleteJson(route('api.organizations.destroy', $organization))
            ->assertOk();

        $this->assertDatabaseMissing('organizations', ['id' => $organization->id]);
    }

    public function test_guest_cannot_create_an_organization(): void
    {
        $this->postJson(route('api.organizations.store'), [
            'name' => 'Guest MSA',
        ])->assertUnauthorized();
    }
}
