<?php

namespace App\Http\Resources;

use App\Models\AcademyLessonProgress;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin AcademyLessonProgress
 */
class AcademyLessonProgressResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'user_id' => $this->user_id,
            'academy_lesson_id' => $this->academy_lesson_id,
            'status' => $this->status,
            'started_at' => $this->started_at?->toIso8601String(),
            'completed_at' => $this->completed_at?->toIso8601String(),
            'lesson' => $this->whenLoaded('lesson', fn () => $this->lesson
                ? [
                    'id' => $this->lesson->id,
                    'title' => $this->lesson->title,
                    'category' => $this->lesson->category,
                    'status' => $this->lesson->status,
                ]
                : null),
        ];
    }
}
