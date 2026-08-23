<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use App\Models\IncidentRelatedItem;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreIncidentRelatedItemRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    protected function prepareForValidation(): void
    {
        $merge = [];

        foreach (['reference_url', 'description'] as $field) {
            if ($this->exists($field) && is_string($this->input($field))) {
                $trimmed = trim($this->input($field));
                $merge[$field] = $trimmed === '' ? null : $trimmed;
            }
        }

        if ($merge !== []) {
            $this->merge($merge);
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
            'reference_url' => ['nullable', 'string', 'url', 'max:'.IncidentRelatedItem::REFERENCE_URL_MAX_LENGTH],
            'description' => ['nullable', 'string', 'max:'.IncidentRelatedItem::DESCRIPTION_MAX_LENGTH],
            'observed_at' => ['nullable', 'date'],
            'incident_id' => ['prohibited'],
            'organization_id' => ['prohibited'],
        ];
    }
}
