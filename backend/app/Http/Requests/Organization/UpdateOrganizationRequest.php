<?php

namespace App\Http\Requests\Organization;

use App\Models\Organization;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateOrganizationRequest extends FormRequest
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
        /** @var Organization $organization */
        $organization = $this->route('organization');

        return [
            'name' => ['sometimes', 'required', 'string', 'max:255'],
            'slug' => [
                'sometimes',
                'required',
                'string',
                'max:255',
                Rule::unique('organizations', 'slug')->ignore($organization->id),
            ],
            'status' => ['sometimes', 'required', Rule::in([
                Organization::STATUS_ACTIVE,
                Organization::STATUS_INACTIVE,
                Organization::STATUS_SUSPENDED,
            ])],
        ];
    }
}
