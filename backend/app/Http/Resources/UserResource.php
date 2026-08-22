<?php

namespace App\Http\Resources;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin User
 */
class UserResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $this->resource->loadMissing(['memberships.organization', 'memberships.role']);

        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'memberships' => MembershipResource::collection($this->memberships),
        ];
    }
}
