<?php

namespace App\Services;

use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class OrganizationService
{
    /**
     * @param  array{name: string, slug?: string|null, status?: string|null}  $data
     */
    public function create(User $user, array $data): Organization
    {
        return DB::transaction(function () use ($user, $data) {
            $organization = Organization::query()->create([
                'name' => $data['name'],
                'slug' => filled($data['slug'] ?? null)
                    ? Str::slug($data['slug'])
                    : Organization::uniqueSlugFromName($data['name']),
                'status' => $data['status'] ?? Organization::STATUS_ACTIVE,
            ]);

            Membership::query()->create([
                'user_id' => $user->id,
                'organization_id' => $organization->id,
                'role_id' => Role::admin()->id,
            ]);

            return $organization->fresh();
        });
    }

    /**
     * @param  array{name?: string, slug?: string, status?: string}  $data
     */
    public function update(Organization $organization, array $data): Organization
    {
        if (array_key_exists('slug', $data) && filled($data['slug'])) {
            $data['slug'] = Str::slug($data['slug']);
        }

        $organization->fill($data);
        $organization->save();

        return $organization->fresh();
    }

    public function delete(Organization $organization): void
    {
        $organization->delete();
    }
}
