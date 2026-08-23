<?php

namespace App\Http\Resources;

use App\Models\LearningRecommendation;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin LearningRecommendation
 */
class LearningRecommendationResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $staff = CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_VIEW)
            || CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_CREATE)
            || CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)
            || CommunityVisibility::canManage(Permissions::EDUCATION_RECOMMENDATIONS_MANAGE);

        $pattern = null;
        if ($this->relationLoaded('pattern') && $this->pattern) {
            $pattern = [
                'id' => $this->pattern->id,
                'title' => $this->pattern->title,
                'pattern_type' => $this->pattern->pattern_type,
                'summary' => $this->pattern->summary,
                'learning_objective' => $this->pattern->learning_objective,
                'domain' => $this->pattern->domain,
                'status' => $this->pattern->status,
            ];
            // Never expose source_incident_id on learner-facing recommendation payloads.
            if ($staff) {
                $pattern['source_incident_id'] = $this->pattern->source_incident_id;
            }
        }

        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'learning_pattern_id' => $this->learning_pattern_id,
            'academy_course_id' => $this->academy_course_id,
            'academy_lesson_id' => $this->academy_lesson_id,
            'reason' => $this->reason,
            'status' => $this->status,
            'pattern' => $pattern,
            'course' => $this->whenLoaded('course', fn () => $this->course
                ? new CourseResource($this->course)
                : null),
            'lesson' => $this->whenLoaded('lesson', fn () => $this->lesson
                ? new AcademyLessonResource($this->lesson)
                : null),
            'created_by' => $this->whenLoaded('creator', fn () => new UserSummaryResource($this->creator)),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
