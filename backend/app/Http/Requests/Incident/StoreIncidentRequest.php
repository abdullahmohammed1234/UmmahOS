<?php

namespace App\Http\Requests\Incident;

use App\Models\Incident;
use App\Models\IncidentRelatedItem;
use App\Models\IncidentReply;
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
        $merge = [];

        if ($this->exists('description') && is_string($this->input('description'))) {
            $merge['description'] = trim($this->input('description'));
        }

        if ($this->exists('source_url')) {
            $sourceUrl = $this->input('source_url');
            $normalized = is_string($sourceUrl) ? trim($sourceUrl) : $sourceUrl;
            $merge['source_url'] = $normalized === '' ? null : $normalized;
        }

        foreach ([
            'original_item_title',
            'original_item_content',
            'original_item_author',
            'surrounding_context',
            'reporter_notes',
            'language',
        ] as $field) {
            if ($this->exists($field) && is_string($this->input($field))) {
                $trimmed = trim($this->input($field));
                $merge[$field] = $trimmed === '' ? null : $trimmed;
            }
        }

        if ($this->exists('replies') && is_array($this->input('replies'))) {
            $merge['replies'] = collect($this->input('replies'))
                ->map(function ($reply) {
                    if (! is_array($reply)) {
                        return $reply;
                    }

                    foreach (['author', 'content'] as $field) {
                        if (array_key_exists($field, $reply) && is_string($reply[$field])) {
                            $trimmed = trim($reply[$field]);
                            $reply[$field] = $trimmed === '' ? null : $trimmed;
                        }
                    }

                    return $reply;
                })
                ->all();
        }

        if ($this->exists('related_items') && is_array($this->input('related_items'))) {
            $merge['related_items'] = collect($this->input('related_items'))
                ->map(function ($item) {
                    if (! is_array($item)) {
                        return $item;
                    }

                    foreach (['reference_url', 'description'] as $field) {
                        if (array_key_exists($field, $item) && is_string($item[$field])) {
                            $trimmed = trim($item[$field]);
                            $item[$field] = $trimmed === '' ? null : $trimmed;
                        }
                    }

                    return $item;
                })
                ->all();
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
            'visibility' => ['required', 'string', Rule::in(Incident::visibilities())],
            'source_url' => ['nullable', 'string', 'url', 'max:2048'],
            'description' => ['required', 'string', 'max:'.Incident::DESCRIPTION_MAX_LENGTH],
            'original_item_title' => ['nullable', 'string', 'max:'.Incident::ORIGINAL_ITEM_TITLE_MAX_LENGTH],
            'original_item_content' => ['nullable', 'string', 'max:'.Incident::ORIGINAL_ITEM_CONTENT_MAX_LENGTH],
            'original_item_author' => ['nullable', 'string', 'max:'.Incident::ORIGINAL_ITEM_AUTHOR_MAX_LENGTH],
            'original_item_posted_at' => ['nullable', 'date'],
            'observed_at' => ['nullable', 'date'],
            'surrounding_context' => ['nullable', 'string', 'max:'.Incident::SURROUNDING_CONTEXT_MAX_LENGTH],
            'language' => ['nullable', 'string', 'max:'.Incident::LANGUAGE_MAX_LENGTH, Rule::in(Incident::languages())],
            'reporter_notes' => ['nullable', 'string', 'max:'.Incident::REPORTER_NOTES_MAX_LENGTH],
            'replies' => ['sometimes', 'array', 'max:50'],
            'replies.*.author' => ['nullable', 'string', 'max:'.IncidentReply::AUTHOR_MAX_LENGTH],
            'replies.*.content' => ['required', 'string', 'max:'.IncidentReply::CONTENT_MAX_LENGTH],
            'replies.*.posted_at' => ['nullable', 'date'],
            'replies.*.position' => ['nullable', 'integer', 'min:0', 'max:999'],
            'related_items' => ['sometimes', 'array', 'max:50'],
            'related_items.*.platform' => ['required', 'string', Rule::in(Incident::platforms())],
            'related_items.*.content_type' => ['required', 'string', Rule::in(Incident::contentTypes())],
            'related_items.*.reference_url' => ['nullable', 'string', 'url', 'max:'.IncidentRelatedItem::REFERENCE_URL_MAX_LENGTH],
            'related_items.*.description' => ['nullable', 'string', 'max:'.IncidentRelatedItem::DESCRIPTION_MAX_LENGTH],
            'related_items.*.observed_at' => ['nullable', 'date'],
            'organization_id' => ['prohibited'],
            'reported_by' => ['prohibited'],
            'status' => ['prohibited'],
            'safety_classification' => ['prohibited'],
            'classified_by' => ['prohibited'],
            'classified_at' => ['prohibited'],
        ];
    }
}
