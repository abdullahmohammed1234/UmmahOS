<?php

namespace App\Http\Requests\Review;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class ConfirmReviewRequest extends FormRequest
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
            'notes' => ['required', 'string', 'min:1', 'max:'.Incident::REVIEW_NOTES_MAX_LENGTH],
            'safety_classification' => [
                'required',
                'string',
                Rule::in(array_values(array_filter(
                    Incident::safetyClassifications(),
                    fn (string $value) => $value !== Incident::CLASSIFICATION_UNCLASSIFIED
                ))),
            ],
            'review_lock_version' => ['sometimes', 'nullable', 'integer', 'min:1'],
        ];
    }
}
