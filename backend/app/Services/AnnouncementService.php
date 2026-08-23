<?php

namespace App\Services;

use App\Models\Announcement;
use App\Models\Organization;
use App\Models\User;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Database\Eloquent\Collection;

class AnnouncementService
{
    /**
     * @return Collection<int, Announcement>
     */
    public function listForCurrentViewer(Organization $organization): Collection
    {
        $query = $organization->announcements()
            ->with('creator')
            ->orderByRaw('published_at is null')
            ->orderByDesc('published_at')
            ->orderByDesc('id');

        if (! CommunityVisibility::canManage(Permissions::CONTENT_MANAGE)) {
            $query->published();
        }

        return $query->get();
    }

    public function findVisible(Organization $organization, int $announcementId): Announcement
    {
        $query = $organization->announcements()->with('creator')->whereKey($announcementId);

        if (! CommunityVisibility::canManage(Permissions::CONTENT_MANAGE)) {
            $query->published();
        }

        return $query->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function create(Organization $organization, User $actor, array $attributes): Announcement
    {
        return $organization->announcements()->create([
            ...$this->payload($attributes),
            'created_by' => $actor->id,
        ])->load('creator');
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(Announcement $announcement, array $attributes): Announcement
    {
        $announcement->update($this->payload($attributes));

        return $announcement->fresh('creator');
    }

    public function delete(Announcement $announcement): void
    {
        $announcement->delete();
    }

    /**
     * @param  array<string, mixed>  $attributes
     * @return array<string, mixed>
     */
    private function payload(array $attributes): array
    {
        if (array_key_exists('published', $attributes)) {
            $published = (bool) $attributes['published'];
            unset($attributes['published']);

            if (! array_key_exists('published_at', $attributes)) {
                $attributes['published_at'] = $published ? now() : null;
            }
        }

        return $attributes;
    }
}
