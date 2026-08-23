<?php

namespace App\Services;

use App\Models\Incident;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Carbon;

class IncidentService
{
    /**
     * @return Collection<int, Incident>
     */
    public function list(Organization $organization, ?string $status = null): Collection
    {
        $query = $organization->incidents()
            ->with(['reporter', 'classifier', 'replies', 'relatedItems'])
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
            ->with(['reporter', 'classifier', 'replies', 'relatedItems'])
            ->whereKey($incidentId)
            ->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function report(Organization $organization, User $reporter, array $attributes): Incident
    {
        return DB::transaction(function () use ($organization, $reporter, $attributes) {
            $observedAt = array_key_exists('observed_at', $attributes) && $attributes['observed_at'] !== null
                ? Carbon::parse($attributes['observed_at'])
                : now();

            /** @var Incident $incident */
            $incident = $organization->incidents()->create([
                'reported_by' => $reporter->id,
                'platform' => $attributes['platform'],
                'content_type' => $attributes['content_type'],
                'visibility' => $attributes['visibility'],
                'source_url' => $attributes['source_url'] ?? null,
                'description' => $attributes['description'],
                'original_item_title' => $attributes['original_item_title'] ?? null,
                'original_item_content' => $attributes['original_item_content'] ?? null,
                'original_item_author' => $attributes['original_item_author'] ?? null,
                'original_item_posted_at' => isset($attributes['original_item_posted_at'])
                    ? Carbon::parse($attributes['original_item_posted_at'])
                    : null,
                'observed_at' => $observedAt,
                'surrounding_context' => $attributes['surrounding_context'] ?? null,
                'language' => $attributes['language'] ?? Incident::LANGUAGE_UNKNOWN,
                'reporter_notes' => $attributes['reporter_notes'] ?? null,
                'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
                'classified_by' => null,
                'classified_at' => null,
                'status' => Incident::STATUS_OPEN,
            ]);

            $this->syncReplies($incident, $attributes['replies'] ?? []);
            $this->syncRelatedItems($incident, $attributes['related_items'] ?? []);

            return $incident->load(['reporter', 'classifier', 'replies', 'relatedItems']);
        });
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function updateReview(Incident $incident, User $reviewer, array $attributes): Incident
    {
        $updates = [];

        if (array_key_exists('status', $attributes)) {
            $updates['status'] = $attributes['status'];
        }

        if (array_key_exists('safety_classification', $attributes)) {
            $classification = $attributes['safety_classification'];
            $updates['safety_classification'] = $classification;

            if ($classification === Incident::CLASSIFICATION_UNCLASSIFIED) {
                $updates['classified_by'] = null;
                $updates['classified_at'] = null;
            } else {
                $updates['classified_by'] = $reviewer->id;
                $updates['classified_at'] = now();
            }
        }

        if ($updates !== []) {
            $incident->update($updates);
        }

        return $incident->fresh(['reporter', 'classifier', 'replies', 'relatedItems']);
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function addReply(Incident $incident, array $attributes): IncidentReply
    {
        $position = $attributes['position'] ?? (($incident->replies()->max('position') ?? -1) + 1);

        return $incident->replies()->create([
            'author' => $attributes['author'] ?? null,
            'content' => $attributes['content'],
            'posted_at' => isset($attributes['posted_at'])
                ? Carbon::parse($attributes['posted_at'])
                : null,
            'position' => $position,
        ]);
    }

    public function deleteReply(Incident $incident, int $replyId): void
    {
        $reply = $incident->replies()->whereKey($replyId)->firstOrFail();
        $reply->delete();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function addRelatedItem(Incident $incident, array $attributes): IncidentRelatedItem
    {
        return $incident->relatedItems()->create([
            'platform' => $attributes['platform'],
            'content_type' => $attributes['content_type'],
            'reference_url' => $attributes['reference_url'] ?? null,
            'description' => $attributes['description'] ?? null,
            'observed_at' => isset($attributes['observed_at'])
                ? Carbon::parse($attributes['observed_at'])
                : null,
        ]);
    }

    public function deleteRelatedItem(Incident $incident, int $itemId): void
    {
        $item = $incident->relatedItems()->whereKey($itemId)->firstOrFail();
        $item->delete();
    }

    /**
     * @param  list<array<string, mixed>>  $replies
     */
    private function syncReplies(Incident $incident, array $replies): void
    {
        foreach (array_values($replies) as $index => $reply) {
            $incident->replies()->create([
                'author' => $reply['author'] ?? null,
                'content' => $reply['content'],
                'posted_at' => isset($reply['posted_at'])
                    ? Carbon::parse($reply['posted_at'])
                    : null,
                'position' => $reply['position'] ?? $index,
            ]);
        }
    }

    /**
     * @param  list<array<string, mixed>>  $items
     */
    private function syncRelatedItems(Incident $incident, array $items): void
    {
        foreach ($items as $item) {
            $incident->relatedItems()->create([
                'platform' => $item['platform'],
                'content_type' => $item['content_type'],
                'reference_url' => $item['reference_url'] ?? null,
                'description' => $item['description'] ?? null,
                'observed_at' => isset($item['observed_at'])
                    ? Carbon::parse($item['observed_at'])
                    : null,
            ]);
        }
    }
}
