<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use App\Models\IncidentReply;
use Illuminate\Foundation\Http\FormRequest;

class StoreIncidentReplyRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    protected function prepareForValidation(): void
    {
        $merge = [];

        if ($this->exists('author') && is_string($this->input('author'))) {
            $trimmed = trim($this->input('author'));
            $merge['author'] = $trimmed === '' ? null : $trimmed;
        }

        if ($this->exists('content') && is_string($this->input('content'))) {
            $merge['content'] = trim($this->input('content'));
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
            'author' => ['nullable', 'string', 'max:'.IncidentReply::AUTHOR_MAX_LENGTH],
            'content' => ['required', 'string', 'max:'.IncidentReply::CONTENT_MAX_LENGTH],
            'posted_at' => ['nullable', 'date'],
            'position' => ['nullable', 'integer', 'min:0', 'max:999'],
            'incident_id' => ['prohibited'],
            'organization_id' => ['prohibited'],
        ];
    }
}
