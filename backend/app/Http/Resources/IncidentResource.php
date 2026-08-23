<?php

namespace App\Http\Resources;

use App\Models\Incident;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin Incident
 */
class IncidentResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'platform' => $this->platform,
            'content_type' => $this->content_type,
            'visibility' => $this->visibility,
            'source_url' => $this->source_url,
            'description' => $this->description,
            'original_item_title' => $this->original_item_title,
            'original_item_content' => $this->original_item_content,
            'original_item_author' => $this->original_item_author,
            'original_item_posted_at' => $this->original_item_posted_at?->toIso8601String(),
            'observed_at' => $this->observed_at?->toIso8601String(),
            'surrounding_context' => $this->surrounding_context,
            'language' => $this->language,
            'reporter_notes' => $this->reporter_notes,
            'safety_classification' => $this->safety_classification,
            'classified_by' => $this->whenLoaded('classifier', fn () => $this->classifier
                ? new UserSummaryResource($this->classifier)
                : null),
            'classified_at' => $this->classified_at?->toIso8601String(),
            'status' => $this->status,
            'replies' => IncidentReplyResource::collection($this->whenLoaded('replies')),
            'related_items' => IncidentRelatedItemResource::collection($this->whenLoaded('relatedItems')),
            'reported_by' => $this->whenLoaded('reporter', fn () => new UserSummaryResource($this->reporter)),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
