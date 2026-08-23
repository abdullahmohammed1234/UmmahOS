<?php

namespace App\Http\Resources;

use App\Models\IncidentReview;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin IncidentReview
 */
class IncidentReviewResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'outcome' => $this->outcome,
            'notes' => $this->notes,
            'safety_classification' => $this->safety_classification,
            'escalation_reason' => $this->escalation_reason,
            'is_current' => $this->is_current,
            'reviewer' => $this->whenLoaded('reviewer', fn () => new UserSummaryResource($this->reviewer)),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
