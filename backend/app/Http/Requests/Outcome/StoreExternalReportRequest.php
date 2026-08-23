<?php

namespace App\Http\Requests\Outcome;

use App\Models\IncidentExternalReport;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreExternalReportRequest extends FormRequest
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
            'platform' => ['required', 'string', Rule::in(IncidentExternalReport::destinationPlatforms())],
            'reporting_channel' => [
                'required',
                'string',
                'max:'.IncidentExternalReport::REPORTING_CHANNEL_MAX_LENGTH,
            ],
            'external_reference' => [
                'nullable',
                'string',
                'max:'.IncidentExternalReport::EXTERNAL_REFERENCE_MAX_LENGTH,
            ],
            'reported_at' => ['required', 'date'],
            'note' => ['nullable', 'string', 'max:4000'],
            'internal_notes' => ['nullable', 'string', 'max:'.IncidentExternalReport::INTERNAL_NOTES_MAX_LENGTH],
            'reporter_visible_summary' => [
                'nullable',
                'string',
                'max:'.IncidentExternalReport::REPORTER_VISIBLE_SUMMARY_MAX_LENGTH,
            ],
        ];
    }
}
