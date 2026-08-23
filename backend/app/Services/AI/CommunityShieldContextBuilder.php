<?php

namespace App\Services\AI;

use App\Models\Incident;

/**
 * Builds a minimized, organization-safe context payload for AI analysis.
 *
 * Does not include reporter identity, membership IDs, organization IDs,
 * auth tokens, or unrelated user data.
 */
class CommunityShieldContextBuilder
{
    /**
     * @return array<string, mixed>
     */
    public function build(Incident $incident): array
    {
        $incident->loadMissing(['replies', 'relatedItems']);

        return [
            'platform' => $incident->platform,
            'content_type' => $incident->content_type,
            'visibility' => $incident->visibility,
            'source_url' => $this->valueOrNotProvided($incident->source_url),
            'description' => $incident->description,
            'original_item' => [
                'title' => $this->valueOrNotProvided($incident->original_item_title),
                'content' => $this->valueOrNotProvided($incident->original_item_content),
                'author' => $this->valueOrNotProvided($incident->original_item_author),
                'posted_at' => $incident->original_item_posted_at?->toIso8601String() ?? 'Not provided',
            ],
            'observed_at' => $incident->observed_at?->toIso8601String() ?? 'Not provided',
            'surrounding_context' => $this->valueOrNotProvided($incident->surrounding_context),
            'replies' => $incident->replies->map(function ($reply) {
                return [
                    'author' => $this->valueOrNotProvided($reply->author),
                    'content' => $reply->content,
                    'posted_at' => $reply->posted_at?->toIso8601String() ?? 'Not provided',
                    'position' => $reply->position,
                ];
            })->values()->all(),
            'related_items' => $incident->relatedItems->map(function ($item) {
                return [
                    'platform' => $item->platform,
                    'content_type' => $item->content_type,
                    'description' => $this->valueOrNotProvided($item->description),
                    'reference_url' => $this->valueOrNotProvided($item->reference_url),
                    'observed_at' => $item->observed_at?->toIso8601String() ?? 'Not provided',
                ];
            })->values()->all(),
            'language' => $incident->language ?: 'unknown',
            'reporter_notes' => $this->valueOrNotProvided($incident->reporter_notes),
        ];
    }

    private function valueOrNotProvided(mixed $value): string
    {
        if ($value === null || $value === '') {
            return 'Not provided';
        }

        return (string) $value;
    }
}
