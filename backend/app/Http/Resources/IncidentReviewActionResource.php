<?php

namespace App\Http\Resources;

use App\Models\IncidentReviewAction;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin IncidentReviewAction
 */
class IncidentReviewActionResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'action' => $this->action,
            'notes' => $this->notes,
            'payload' => $this->payload,
            'actor' => $this->whenLoaded('actor', fn () => new UserSummaryResource($this->actor)),
            'created_at' => $this->created_at?->toIso8601String(),
        ];
    }
}
