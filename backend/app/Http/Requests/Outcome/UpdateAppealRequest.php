<?php

namespace App\Http\Requests\Outcome;

use App\Models\IncidentReportAppeal;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateAppealRequest extends FormRequest
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
            'status' => ['sometimes', 'string', Rule::in(IncidentReportAppeal::statuses())],
            'response' => ['nullable', 'string', 'max:'.IncidentReportAppeal::RESPONSE_MAX_LENGTH],
        ];
    }
}
