<?php

namespace App\Http\Requests\Education;

use App\Models\LearningPattern;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreLearningPatternRequest extends FormRequest
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
            'pattern_type' => ['required', 'string', Rule::in(LearningPattern::PATTERN_TYPES)],
            'title' => ['required', 'string', 'max:255'],
            'summary' => ['required', 'string', 'max:5000'],
            'learning_objective' => ['required', 'string', 'max:2000'],
            'domain' => ['nullable', 'string', 'max:100'],
            'severity_context' => ['nullable', 'string', 'max:100'],
        ];
    }
}
