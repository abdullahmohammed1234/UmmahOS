<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateIncidentRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    /**
     * @return array<string, mixed>
     */
    public function rules(): array
    {
        return [
            'status' => ['required', 'string', Rule::in(Incident::statuses())],
            'organization_id' => ['prohibited'],
            'reported_by' => ['prohibited'],
            'platform' => ['prohibited'],
            'content_type' => ['prohibited'],
            'visibility' => ['prohibited'],
            'source_url' => ['prohibited'],
            'description' => ['prohibited'],
        ];
    }
}
