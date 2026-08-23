<?php

namespace App\Http\Requests\Education;

use App\Models\LearningPattern;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateLearningPatternRequest extends FormRequest
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
            'pattern_type' => ['sometimes', 'string', Rule::in(LearningPattern::PATTERN_TYPES)],
            'title' => ['sometimes', 'string', 'max:255'],
            'summary' => ['sometimes', 'string', 'max:5000'],
            'learning_objective' => ['sometimes', 'string', 'max:2000'],
            'domain' => ['sometimes', 'nullable', 'string', 'max:100'],
            'severity_context' => ['sometimes', 'nullable', 'string', 'max:100'],
        ];
    }
}
