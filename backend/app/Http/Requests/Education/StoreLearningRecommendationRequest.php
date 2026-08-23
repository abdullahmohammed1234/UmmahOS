<?php

namespace App\Http\Requests\Education;

use App\Models\LearningRecommendation;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreLearningRecommendationRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /**
     * @return array<string, mixed>
     */
    public function rules(): array
    {
        return [
            'learning_pattern_id' => ['required', 'integer'],
            'academy_course_id' => ['nullable', 'integer'],
            'academy_lesson_id' => ['nullable', 'integer'],
            'reason' => ['required', 'string', 'max:5000'],
            'status' => ['nullable', 'string', Rule::in([
                LearningRecommendation::STATUS_DRAFT,
                LearningRecommendation::STATUS_PUBLISHED,
                LearningRecommendation::STATUS_ARCHIVED,
            ])],
        ];
    }
}
