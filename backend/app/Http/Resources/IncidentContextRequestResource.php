<?php

namespace App\Http\Resources;

use App\Models\IncidentContextRequest;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin IncidentContextRequest
 */
class IncidentContextRequestResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'reason' => $this->reason,
            'status' => $this->status,
            'requested_at' => $this->requested_at?->toIso8601String(),
            'resolved_at' => $this->resolved_at?->toIso8601String(),
            'requested_by' => $this->whenLoaded('requester', fn () => new UserSummaryResource($this->requester)),
            'resolved_by' => $this->whenLoaded('resolver', fn () => $this->resolver
                ? new UserSummaryResource($this->resolver)
                : null),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
