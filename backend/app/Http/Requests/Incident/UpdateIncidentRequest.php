<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Validator;

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
            'status' => ['sometimes', 'string', Rule::in(Incident::statuses())],
            'safety_classification' => ['sometimes', 'string', Rule::in(Incident::safetyClassifications())],
            'organization_id' => ['prohibited'],
            'reported_by' => ['prohibited'],
            'classified_by' => ['prohibited'],
            'classified_at' => ['prohibited'],
            'platform' => ['prohibited'],
            'content_type' => ['prohibited'],
            'visibility' => ['prohibited'],
            'source_url' => ['prohibited'],
            'description' => ['prohibited'],
            'original_item_title' => ['prohibited'],
            'original_item_content' => ['prohibited'],
            'original_item_author' => ['prohibited'],
            'original_item_posted_at' => ['prohibited'],
            'observed_at' => ['prohibited'],
            'surrounding_context' => ['prohibited'],
            'language' => ['prohibited'],
            'reporter_notes' => ['prohibited'],
            'replies' => ['prohibited'],
            'related_items' => ['prohibited'],
        ];
    }

    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator): void {
            if (! $this->exists('status') && ! $this->exists('safety_classification')) {
                $validator->errors()->add('status', 'Provide a status and/or safety classification to update.');
            }
        });
    }
}
