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
            'status' => $this->status,
            'reported_by' => $this->whenLoaded('reporter', fn () => new UserSummaryResource($this->reporter)),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
