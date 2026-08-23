<?php

namespace App\Http\Requests\Outcome;

use App\Models\IncidentReportAppeal;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreAppealRequest extends FormRequest
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
            'reason' => ['required', 'string', 'max:'.IncidentReportAppeal::REASON_MAX_LENGTH],
            'additional_evidence' => [
                'nullable',
                'string',
                'max:'.IncidentReportAppeal::ADDITIONAL_EVIDENCE_MAX_LENGTH,
            ],
            'reference' => ['nullable', 'string', 'max:'.IncidentReportAppeal::REFERENCE_MAX_LENGTH],
            'notes' => ['nullable', 'string', 'max:'.IncidentReportAppeal::NOTES_MAX_LENGTH],
            'submitted_at' => ['nullable', 'date'],
        ];
    }
}
