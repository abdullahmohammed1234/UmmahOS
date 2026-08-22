<?php

namespace Tests\Feature\Organization;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class MembershipTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_user_can_belong_to_multiple_organizations(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);

        $user->refresh()->load('memberships.organization', 'memberships.role');

        $this->assertCount(2, $user->memberships);
        $this->assertTrue($user->belongsToOrganization($alpha));
        $this->assertTrue($user->belongsToOrganization($beta));
        $this->assertTrue($user->hasRoleIn($alpha, 'member'));
        $this->assertTrue($user->hasRoleIn($beta, 'admin'));
    }

    public function test_admin_can_add_a_member_to_their_organization(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $invitee = User::factory()->create();

        $this->actingAsApi($admin)
            ->postJson(route('api.organizations.members.store', $organization), [
                'user_id' => $invitee->id,
                'role' => 'member',
            ])
            ->assertCreated()
            ->assertJsonPath('data.user.id', $invitee->id)
            ->assertJsonPath('data.role.slug', 'member');

        $this->assertTrue($invitee->fresh()->belongsToOrganization($organization));
    }

    public function test_member_cannot_add_members(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $invitee = User::factory()->create();

        $this->actingAsApi($member)
            ->postJson(route('api.organizations.members.store', $organization), [
                'user_id' => $invitee->id,
                'role' => 'member',
            ])
            ->assertForbidden();
    }

    public function test_admin_can_change_a_member_role(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);
        $membership = $member->membershipFor($organization);

        $this->actingAsApi($admin)
            ->patchJson(route('api.organizations.members.update', [$organization, $membership]), [
                'role' => 'admin',
            ])
            ->assertOk()
            ->assertJsonPath('data.role.slug', 'admin');
    }

    public function test_admin_can_remove_a_member(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);
        $membership = $member->membershipFor($organization);

        $this->actingAsApi($admin)
            ->deleteJson(route('api.organizations.members.destroy', [$organization, $membership]))
            ->assertOk();

        $this->assertFalse($member->fresh()->belongsToOrganization($organization));
    }

    public function test_members_can_list_organization_members(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($admin)
            ->getJson(route('api.organizations.members.index', $organization))
            ->assertOk()
            ->assertJsonCount(2, 'data');
    }
}
