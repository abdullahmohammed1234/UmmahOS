<?php

namespace App\Http\Requests\Review;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class ListReviewQueueRequest extends FormRequest
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
            'status' => ['sometimes', 'nullable', 'string', Rule::in(Incident::statuses())],
            'platform' => ['sometimes', 'nullable', 'string', Rule::in(Incident::platforms())],
            'confidence' => ['sometimes', 'nullable', 'string', Rule::in(['low', 'moderate', 'high'])],
            'uncertainty' => ['sometimes', 'nullable', 'string', Rule::in(['low', 'moderate', 'high'])],
            'classification' => ['sometimes', 'nullable', 'string', Rule::in(Incident::safetyClassifications())],
            'escalated' => ['sometimes', 'nullable', 'boolean'],
        ];
    }

    protected function prepareForValidation(): void
    {
        if ($this->has('escalated') && is_string($this->input('escalated'))) {
            $this->merge([
                'escalated' => filter_var($this->input('escalated'), FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE),
            ]);
        }
    }
}
