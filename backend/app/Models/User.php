<?php

namespace App\Models;

use App\Support\Permissions;
use Database\Factories\UserFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    /** @use HasFactory<UserFactory> */
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }

    public function memberships(): HasMany
    {
        return $this->hasMany(Membership::class);
    }

    public function organizations(): BelongsToMany
    {
        return $this->belongsToMany(Organization::class, 'memberships')
            ->withPivot(['id', 'role_id'])
            ->withTimestamps();
    }

    public function membershipFor(Organization $organization): ?Membership
    {
        return $this->memberships()
            ->with('role.permissions')
            ->where('organization_id', $organization->id)
            ->first();
    }

    public function belongsToOrganization(Organization $organization): bool
    {
        return $this->membershipFor($organization) !== null;
    }

    public function roleIn(Organization $organization): ?Role
    {
        return $this->membershipFor($organization)?->role;
    }

    public function hasRoleIn(Organization $organization, string $role): bool
    {
        $membershipRole = $this->roleIn($organization);

        return $membershipRole !== null && (
            $membershipRole->slug === $role || $membershipRole->name === $role
        );
    }

    public function hasPermissionIn(Organization $organization, string $permission): bool
    {
        $membership = $this->membershipFor($organization);

        if ($membership === null || $membership->role === null) {
            return false;
        }

        if ($membership->role->isAdmin()) {
            return true;
        }

        return $membership->role->permissions
            ->contains(fn (Permission $model) => $model->slug === $permission);
    }

    /**
     * @return list<string>
     */
    public function permissionsIn(Organization $organization): array
    {
        if (! $this->belongsToOrganization($organization)) {
            return [];
        }

        if ($this->hasRoleIn($organization, Role::ADMIN)) {
            return Permissions::slugs();
        }

        return $this->roleIn($organization)
            ?->permissions
            ->pluck('slug')
            ->values()
            ->all() ?? [];
    }
}
