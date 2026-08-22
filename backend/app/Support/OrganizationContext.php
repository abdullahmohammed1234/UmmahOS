<?php

namespace App\Support;

use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;

class OrganizationContext
{
    public function __construct(
        public readonly Organization $organization,
        public readonly Membership $membership,
        public readonly User $user,
    ) {}

    public function role(): ?Role
    {
        return $this->membership->role;
    }

    public function hasPermission(string $permission): bool
    {
        return $this->user->hasPermissionIn($this->organization, $permission);
    }

    /**
     * @return list<string>
     */
    public function permissions(): array
    {
        return $this->user->permissionsIn($this->organization);
    }
}
