<?php

namespace App\Models\Concerns;

use App\Models\Organization;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Foundation for future organization-scoped modules
 * (events, courses, content, incidents, reports).
 *
 * Queries must always be constrained through the current organization.
 * Do not rely on client-supplied IDs alone.
 */
trait BelongsToOrganization
{
    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    public function scopeForOrganization(Builder $query, Organization|int $organization): Builder
    {
        $organizationId = $organization instanceof Organization
            ? $organization->id
            : $organization;

        return $query->where($this->qualifyColumn('organization_id'), $organizationId);
    }
}
