<?php

namespace App\Http\Resources;

use App\Models\AcademyLesson;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin AcademyLesson
 */
class AcademyLessonResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'course_id' => $this->course_id,
            'title' => $this->title,
            'learning_objective' => $this->learning_objective,
            'sections' => $this->sections,
            'category' => $this->category,
            'status' => $this->status,
            'is_demo' => (bool) $this->is_demo,
            'course' => $this->whenLoaded('course', fn () => $this->course
                ? [
                    'id' => $this->course->id,
                    'title' => $this->course->title,
                    'status' => $this->course->status,
                ]
                : null),
            'scenarios' => AcademyScenarioResource::collection($this->whenLoaded('scenarios')),
            'scenario_count' => $this->when(
                $this->relationLoaded('scenarios'),
                fn () => $this->scenarios->count()
            ),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
