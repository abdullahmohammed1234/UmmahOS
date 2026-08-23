<?php

namespace App\Http\Resources;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * Compact queue row for Community Safety Review.
 *
 * @mixin Incident
 */
class ReviewQueueItemResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $latestAnalysis = $this->whenLoaded('aiAnalyses')
            ? $this->aiAnalyses->first()
            : null;
        $package = $latestAnalysis?->status === IncidentAiAnalysis::STATUS_COMPLETED
            ? $latestAnalysis->analysis
            : null;

        return [
            'id' => $this->id,
            'platform' => $this->platform,
            'content_type' => $this->content_type,
            'visibility' => $this->visibility,
            'status' => $this->status,
            'review_outcome' => $this->review_outcome,
            'escalated' => (bool) $this->escalated,
            'safety_classification' => $this->safety_classification,
            'related_item_count' => $this->whenLoaded('relatedItems', fn () => $this->relatedItems->count(), 0),
            'open_context_requests' => $this->whenLoaded(
                'contextRequests',
                fn () => $this->contextRequests->count(),
                0
            ),
            'ai_assisted_triage' => [
                'classification' => data_get($package, 'classification.label'),
                'confidence' => data_get($package, 'classification.confidence'),
                'uncertainty' => data_get($package, 'uncertainty.level'),
                'recommended_action' => data_get($package, 'recommended_action.type'),
            ],
            'current_reviewer' => $this->whenLoaded('currentReviewer', fn () => $this->currentReviewer
                ? new UserSummaryResource($this->currentReviewer)
                : null),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
