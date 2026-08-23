<?php

namespace App\Http\Requests\Education;

use App\Models\LearningRecommendation;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateLearningRecommendationRequest extends FormRequest
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
            'academy_course_id' => ['sometimes', 'nullable', 'integer'],
            'academy_lesson_id' => ['sometimes', 'nullable', 'integer'],
            'reason' => ['sometimes', 'string', 'max:5000'],
            'status' => ['sometimes', 'string', Rule::in([
                LearningRecommendation::STATUS_DRAFT,
                LearningRecommendation::STATUS_PUBLISHED,
                LearningRecommendation::STATUS_ARCHIVED,
            ])],
        ];
    }
}
