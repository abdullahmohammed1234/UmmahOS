<?php

namespace App\Http\Requests\Outcome;

use App\Models\IncidentExternalReport;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateExternalReportRequest extends FormRequest
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
            'status' => ['sometimes', 'string', Rule::in(IncidentExternalReport::statuses())],
            'decision' => ['nullable', 'string', Rule::in(IncidentExternalReport::decisions())],
            'decision_note' => ['nullable', 'string', 'max:'.IncidentExternalReport::DECISION_NOTE_MAX_LENGTH],
            'outcome' => ['nullable', 'string', Rule::in(IncidentExternalReport::outcomes())],
            'outcome_source' => ['nullable', 'string', Rule::in(IncidentExternalReport::outcomeSources())],
            'outcome_summary' => ['nullable', 'string', 'max:'.IncidentExternalReport::OUTCOME_SUMMARY_MAX_LENGTH],
            'reporter_visible_summary' => [
                'nullable',
                'string',
                'max:'.IncidentExternalReport::REPORTER_VISIBLE_SUMMARY_MAX_LENGTH,
            ],
            'verification_status' => [
                'sometimes',
                'string',
                Rule::in(IncidentExternalReport::verificationStatuses()),
            ],
            'internal_notes' => ['nullable', 'string', 'max:'.IncidentExternalReport::INTERNAL_NOTES_MAX_LENGTH],
            'external_reference' => [
                'nullable',
                'string',
                'max:'.IncidentExternalReport::EXTERNAL_REFERENCE_MAX_LENGTH,
            ],
            'note' => ['nullable', 'string', 'max:4000'],
        ];
    }
}
