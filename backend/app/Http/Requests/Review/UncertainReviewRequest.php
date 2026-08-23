<?php

namespace App\Http\Requests\Review;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;

class UncertainReviewRequest extends FormRequest
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
            'review_lock_version' => ['sometimes', 'nullable', 'integer', 'min:1'],
        ];
    }
}
