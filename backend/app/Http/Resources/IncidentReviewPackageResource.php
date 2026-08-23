<?php

namespace App\Http\Resources;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Services\Review\IncidentReviewService;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * Full reviewer package: evidence + AI-assisted triage + human review.
 *
 * @mixin Incident
 */
class IncidentReviewPackageResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        /** @var IncidentReviewService $reviews */
        $reviews = app(IncidentReviewService::class);

        $latestAnalysis = $this->whenLoaded('aiAnalyses')
            ? $this->aiAnalyses->first()
            : null;

        return [
            'incident' => [
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
                'review_outcome' => $this->review_outcome,
                'escalated' => (bool) $this->escalated,
                'escalation_reason' => $this->escalation_reason,
                'escalated_by' => $this->whenLoaded('escalatedByUser', fn () => $this->escalatedByUser
                    ? new UserSummaryResource($this->escalatedByUser)
                    : null),
                'escalated_at' => $this->escalated_at?->toIso8601String(),
                'current_reviewer' => $this->whenLoaded('currentReviewer', fn () => $this->currentReviewer
                    ? new UserSummaryResource($this->currentReviewer)
                    : null),
                'review_started_at' => $this->review_started_at?->toIso8601String(),
                'review_notes' => $this->review_notes,
                'review_lock_version' => (int) $this->review_lock_version,
                'replies' => IncidentReplyResource::collection($this->whenLoaded('replies')),
                'related_items' => IncidentRelatedItemResource::collection($this->whenLoaded('relatedItems')),
                'reported_by' => $this->whenLoaded('reporter', fn () => new UserSummaryResource($this->reporter)),
                'created_at' => $this->created_at?->toIso8601String(),
                'updated_at' => $this->updated_at?->toIso8601String(),
            ],
            'ai_assisted_triage' => [
                'label' => 'AI Context Analysis',
                'advisory_disclaimer' => 'AI-assisted triage is advisory. A trained human reviewer makes the authoritative decision.',
                'latest' => $latestAnalysis
                    ? new IncidentAiAnalysisResource($latestAnalysis)
                    : null,
                'history' => IncidentAiAnalysisResource::collection($this->whenLoaded('aiAnalyses')),
            ],
            'human_review' => [
                'outcome' => $this->review_outcome,
                'notes' => $this->review_notes,
                'escalated' => (bool) $this->escalated,
                'escalation_reason' => $this->escalation_reason,
                'current_review' => $this->whenLoaded('reviews', function () {
                    $current = $this->reviews->firstWhere('is_current', true);

                    return $current ? new IncidentReviewResource($current) : null;
                }),
                'reviews' => IncidentReviewResource::collection($this->whenLoaded('reviews')),
                'context_requests' => IncidentContextRequestResource::collection($this->whenLoaded('contextRequests')),
                'history' => IncidentReviewActionResource::collection($this->whenLoaded('reviewActions')),
                'allowed_actions' => $reviews->allowedActions($this->resource),
            ],
            'queue_summary' => [
                'related_item_count' => $this->whenLoaded('relatedItems', fn () => $this->relatedItems->count(), 0),
                'reply_count' => $this->whenLoaded('replies', fn () => $this->replies->count(), 0),
                'ai_classification' => data_get(
                    $latestAnalysis?->status === IncidentAiAnalysis::STATUS_COMPLETED ? $latestAnalysis->analysis : null,
                    'classification.label'
                ),
                'ai_confidence' => data_get(
                    $latestAnalysis?->status === IncidentAiAnalysis::STATUS_COMPLETED ? $latestAnalysis->analysis : null,
                    'classification.confidence'
                ),
                'ai_uncertainty' => data_get(
                    $latestAnalysis?->status === IncidentAiAnalysis::STATUS_COMPLETED ? $latestAnalysis->analysis : null,
                    'uncertainty.level'
                ),
            ],
        ];
    }
}
