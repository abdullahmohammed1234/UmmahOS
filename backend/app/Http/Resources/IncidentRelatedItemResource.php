<?php

namespace App\Http\Resources;

use App\Models\IncidentRelatedItem;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin IncidentRelatedItem
 */
class IncidentRelatedItemResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'platform' => $this->platform,
            'content_type' => $this->content_type,
            'reference_url' => $this->reference_url,
            'description' => $this->description,
            'observed_at' => $this->observed_at?->toIso8601String(),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
