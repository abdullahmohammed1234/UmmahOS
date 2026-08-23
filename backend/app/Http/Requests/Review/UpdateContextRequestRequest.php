<?php

namespace App\Http\Requests\Review;

use App\Models\IncidentContextRequest;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateContextRequestRequest extends FormRequest
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
            'status' => [
                'required',
                'string',
                Rule::in([
                    IncidentContextRequest::STATUS_FULFILLED,
                    IncidentContextRequest::STATUS_CANCELLED,
                ]),
            ],
            'review_lock_version' => ['sometimes', 'nullable', 'integer', 'min:1'],
        ];
    }
}
