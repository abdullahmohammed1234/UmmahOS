<?php

namespace App\Services;

use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use Illuminate\Validation\ValidationException;

class MembershipService
{
    public function add(Organization $organization, User $user, Role $role): Membership
    {
        if ($user->belongsToOrganization($organization)) {
            throw ValidationException::withMessages([
                'user_id' => ['This user is already a member of the organization.'],
            ]);
        }

        return Membership::query()->create([
            'user_id' => $user->id,
            'organization_id' => $organization->id,
            'role_id' => $role->id,
        ])->load(['user', 'role', 'organization']);
    }

    public function updateRole(Membership $membership, Role $role): Membership
    {
        $membership->role()->associate($role);
        $membership->save();

        return $membership->fresh(['user', 'role', 'organization']);
    }

    public function remove(Membership $membership): void
    {
        $membership->delete();
    }

    public function findInOrganization(Organization $organization, int $membershipId): Membership
    {
        return $organization->memberships()
            ->with(['user', 'role'])
            ->whereKey($membershipId)
            ->firstOrFail();
    }
}
