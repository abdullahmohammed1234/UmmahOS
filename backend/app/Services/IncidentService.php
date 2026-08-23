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
    public function list(Organization $organization, ?string $status = null): Collection
    {
        $query = $organization->incidents()
            ->with('reporter')
            ->orderByRaw("case status when 'open' then 0 when 'reviewing' then 1 else 2 end")
            ->orderByDesc('id');

        if ($status !== null) {
            $query->where('status', $status);
        }

        return $query->get();
    }

    /**
     * @return array{open: int, reviewing: int, resolved: int}
     */
    public function counts(Organization $organization): array
    {
        $grouped = $organization->incidents()
            ->selectRaw('status, count(*) as aggregate')
            ->groupBy('status')
            ->pluck('aggregate', 'status');

        return [
            'open' => (int) ($grouped[Incident::STATUS_OPEN] ?? 0),
            'reviewing' => (int) ($grouped[Incident::STATUS_REVIEWING] ?? 0),
            'resolved' => (int) ($grouped[Incident::STATUS_RESOLVED] ?? 0),
        ];
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
            'platform' => $attributes['platform'],
            'content_type' => $attributes['content_type'],
            'visibility' => $attributes['visibility'],
            'source_url' => $attributes['source_url'] ?? null,
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
