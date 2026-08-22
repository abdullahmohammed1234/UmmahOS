<?php

namespace App\Http\Resources;

use App\Support\OrganizationContext;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin OrganizationContext
 */
class OrganizationContextResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'organization' => new OrganizationResource($this->organization),
            'membership' => new MembershipResource($this->membership),
            'role' => $this->role()?->slug,
            'permissions' => $this->permissions(),
        ];
    }
}
