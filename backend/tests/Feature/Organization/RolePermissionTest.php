<?php

namespace Tests\Feature\Organization;

use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class RolePermissionTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_user_can_have_different_roles_per_organization(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);

        $this->assertTrue($user->hasRoleIn($alpha, 'member'));
        $this->assertFalse($user->hasRoleIn($alpha, 'admin'));
        $this->assertTrue($user->hasRoleIn($beta, 'admin'));
        $this->assertFalse($user->hasRoleIn($beta, 'member'));
    }

    public function test_admin_permissions_do_not_cross_organizations(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->adminRole);
        $this->joinOrganization($user, $beta, $this->memberRole);

        $this->assertTrue($user->hasPermissionIn($alpha, Permissions::ORGANIZATION_MANAGE));
        $this->assertTrue($user->hasPermissionIn($alpha, Permissions::MEMBERS_MANAGE));
        $this->assertFalse($user->hasPermissionIn($beta, Permissions::ORGANIZATION_MANAGE));
        $this->assertFalse($user->hasPermissionIn($beta, Permissions::MEMBERS_MANAGE));
        $this->assertTrue($user->hasPermissionIn($beta, Permissions::ORGANIZATION_VIEW));
        $this->assertTrue($user->hasPermissionIn($beta, Permissions::MEMBERS_VIEW));
    }

    public function test_member_receives_view_permissions_only(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        foreach (Permissions::viewSlugs() as $permission) {
            $this->assertTrue($member->hasPermissionIn($organization, $permission), $permission);
        }

        $this->assertFalse($member->hasPermissionIn($organization, Permissions::ORGANIZATION_MANAGE));
        $this->assertFalse($member->hasPermissionIn($organization, Permissions::MEMBERS_MANAGE));
        $this->assertFalse($member->hasPermissionIn($organization, Permissions::INCIDENTS_MANAGE));
    }

    public function test_admin_receives_all_organization_permissions(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        foreach (Permissions::slugs() as $permission) {
            $this->assertTrue($admin->hasPermissionIn($organization, $permission), $permission);
        }
    }

    public function test_non_member_has_no_permissions_in_an_organization(): void
    {
        $organization = $this->createOrganization();
        $outsider = $this->createMember($this->createOrganization(), $this->adminRole);

        $this->assertFalse($outsider->belongsToOrganization($organization));
        $this->assertFalse($outsider->hasPermissionIn($organization, Permissions::ORGANIZATION_VIEW));
        $this->assertSame([], $outsider->permissionsIn($organization));
    }
}
