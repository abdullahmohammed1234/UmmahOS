<?php

namespace App\Services;

use App\Models\Event;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;

class EventService
{
    /**
     * @return Collection<int, Event>
     */
    public function list(Organization $organization): Collection
    {
        return $organization->events()
            ->with('creator')
            ->orderBy('starts_at')
            ->get();
    }

    public function findInOrganization(Organization $organization, int $eventId): Event
    {
        return $organization->events()
            ->with('creator')
            ->whereKey($eventId)
            ->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function create(Organization $organization, User $actor, array $attributes): Event
    {
        return $organization->events()->create([
            ...$attributes,
            'created_by' => $actor->id,
        ])->load('creator');
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(Event $event, array $attributes): Event
    {
        $event->update($attributes);

        return $event->fresh('creator');
    }

    public function delete(Event $event): void
    {
        $event->delete();
    }
}
