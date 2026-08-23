<?php

namespace App\Services;

use App\Models\Incident;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;

class IncidentService
{
    /**
     * @return Collection<int, Incident>
     */
    public function list(Organization $organization): Collection
    {
        return $organization->incidents()
            ->with('reporter')
            ->orderByRaw("case status when 'open' then 0 when 'reviewing' then 1 else 2 end")
            ->orderByDesc('id')
            ->get();
    }

    public function findInOrganization(Organization $organization, int $incidentId): Incident
    {
        return $organization->incidents()
            ->with('reporter')
            ->whereKey($incidentId)
            ->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function report(Organization $organization, User $reporter, array $attributes): Incident
    {
        return $organization->incidents()->create([
            'reported_by' => $reporter->id,
            'category' => $attributes['category'],
            'description' => $attributes['description'],
            'status' => Incident::STATUS_OPEN,
        ])->load('reporter');
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function updateStatus(Incident $incident, array $attributes): Incident
    {
        $incident->update([
            'status' => $attributes['status'],
        ]);

        return $incident->fresh('reporter');
    }
}
