<?php

namespace App\Http\Resources;

use App\Models\LearningPattern;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin LearningPattern
 */
class LearningPatternResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $canSeeSource = CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_CREATE)
            || CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)
            || CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_VIEW);

        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'pattern_type' => $this->pattern_type,
            'title' => $this->title,
            'summary' => $this->summary,
            'learning_objective' => $this->learning_objective,
            'domain' => $this->domain,
            'severity_context' => $this->severity_context,
            'status' => $this->status,
            'source_incident_id' => $this->when($canSeeSource, $this->source_incident_id),
            'created_by' => $this->whenLoaded('creator', fn () => new UserSummaryResource($this->creator)),
            'approved_by' => $this->whenLoaded('approver', fn () => $this->approver
                ? new UserSummaryResource($this->approver)
                : null),
            'approved_at' => $this->approved_at?->toIso8601String(),
            'recommendations' => LearningRecommendationResource::collection($this->whenLoaded('recommendations')),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
