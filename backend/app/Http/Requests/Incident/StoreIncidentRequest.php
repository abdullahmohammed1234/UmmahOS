<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreIncidentRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    protected function prepareForValidation(): void
    {
        if ($this->exists('description') && is_string($this->input('description'))) {
            $this->merge([
                'description' => trim($this->input('description')),
            ]);
        }

        if ($this->exists('source_url')) {
            $sourceUrl = $this->input('source_url');
            $normalized = is_string($sourceUrl) ? trim($sourceUrl) : $sourceUrl;

            $this->merge([
                'source_url' => $normalized === '' ? null : $normalized,
            ]);
        }
    }

    /**
     * @return array<string, mixed>
     */
    public function rules(): array
    {
        return [
            'platform' => ['required', 'string', Rule::in(Incident::platforms())],
            'content_type' => ['required', 'string', Rule::in(Incident::contentTypes())],
            'visibility' => ['required', 'string', Rule::in(Incident::visibilities())],
            'source_url' => ['nullable', 'string', 'url', 'max:2048'],
            'description' => ['required', 'string', 'max:'.Incident::DESCRIPTION_MAX_LENGTH],
            'organization_id' => ['prohibited'],
            'reported_by' => ['prohibited'],
            'status' => ['prohibited'],
        ];
    }
}
