<?php

namespace App\Http\Requests\Education;

use Illuminate\Foundation\Http\FormRequest;

class SubmitAdaptResponseRequest extends FormRequest
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
            'answer' => ['required', 'string', 'max:5000'],
            'confidence' => ['required', 'integer', 'min:1', 'max:5'],
            'reasoning' => ['nullable', 'string', 'max:5000'],
            'challenge_id' => ['nullable', 'string', 'max:100'],
        ];
    }
}
