<?php

namespace App\Services;

use App\Models\Organization;
use App\Models\Resource;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;

class ResourceService
{
    /**
     * @return Collection<int, Resource>
     */
    public function list(Organization $organization): Collection
    {
        return $organization->resources()
            ->with('creator')
            ->orderBy('title')
            ->get();
    }

    public function findInOrganization(Organization $organization, int $resourceId): Resource
    {
        return $organization->resources()
            ->with('creator')
            ->whereKey($resourceId)
            ->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function create(Organization $organization, User $actor, array $attributes): Resource
    {
        return $organization->resources()->create([
            ...$attributes,
            'created_by' => $actor->id,
        ])->load('creator');
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(Resource $resource, array $attributes): Resource
    {
        $resource->update($attributes);

        return $resource->fresh('creator');
    }

    public function delete(Resource $resource): void
    {
        $resource->delete();
    }
}
