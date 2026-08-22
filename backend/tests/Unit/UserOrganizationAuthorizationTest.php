<?php

namespace Tests\Unit;

use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class UserOrganizationAuthorizationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_belongs_to_organization_trait_scopes_memberships(): void
    {
        $alpha = $this->createOrganization();
        $beta = $this->createOrganization();
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);

        $alphaMemberships = $user->memberships()->forOrganization($alpha)->get();
        $betaMemberships = $user->memberships()->forOrganization($beta)->get();

        $this->assertCount(1, $alphaMemberships);
        $this->assertCount(1, $betaMemberships);
        $this->assertSame($alpha->id, $alphaMemberships->first()->organization_id);
        $this->assertSame($beta->id, $betaMemberships->first()->organization_id);
    }

    public function test_permissions_are_empty_without_membership(): void
    {
        $organization = $this->createOrganization();
        $user = \App\Models\User::factory()->create();

        $this->assertFalse($user->hasPermissionIn($organization, Permissions::ORGANIZATION_VIEW));
        $this->assertSame([], $user->permissionsIn($organization));
    }
}
