<?php

namespace App\Http\Requests\Review;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;

class EscalateReviewRequest extends FormRequest
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
            'reason' => ['required', 'string', 'min:1', 'max:'.Incident::ESCALATION_REASON_MAX_LENGTH],
            'review_lock_version' => ['sometimes', 'nullable', 'integer', 'min:1'],
        ];
    }
}
