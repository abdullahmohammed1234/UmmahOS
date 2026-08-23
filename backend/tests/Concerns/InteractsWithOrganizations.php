<?php

namespace Tests\Concerns;

use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use Database\Seeders\RolePermissionSeeder;

trait InteractsWithOrganizations
{
    protected Role $adminRole;

    protected Role $memberRole;

    protected Role $reviewerRole;

    protected function seedRbac(): void
    {
        $this->seed(RolePermissionSeeder::class);

        $this->adminRole = Role::admin();
        $this->memberRole = Role::member();
        $this->reviewerRole = Role::communitySafetyReviewer();
    }

    protected function createOrganization(array $attributes = []): Organization
    {
        return Organization::factory()->create($attributes);
    }

    protected function createMember(
        Organization $organization,
        ?Role $role = null,
        array $userAttributes = []
    ): User {
        $user = User::factory()->create($userAttributes);

        $this->joinOrganization($user, $organization, $role ?? $this->memberRole);

        return $user->fresh(['memberships.role.permissions', 'memberships.organization']);
    }

    protected function joinOrganization(User $user, Organization $organization, Role $role): Membership
    {
        return Membership::query()->create([
            'user_id' => $user->id,
            'organization_id' => $organization->id,
            'role_id' => $role->id,
        ]);
    }

    protected function actingAsApi(User $user): self
    {
        $this->flushHeaders();
        $this->app['auth']->forgetGuards();

        $token = $user->createToken('test-token')->plainTextToken;

        $this->withHeader('Authorization', 'Bearer '.$token);
        $this->withHeader('Accept', 'application/json');

        return $this;
    }

    protected function orgUrl(Organization $organization, string $path = ''): string
    {
        $suffix = $path === '' ? '' : '/'.ltrim($path, '/');

        return '/api/v1/organizations/'.$organization->id.$suffix;
    }
}
