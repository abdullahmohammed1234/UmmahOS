<?php

namespace App\Http\Resources;

use App\Models\Resource as ResourceModel;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin ResourceModel
 */
class ResourceItemResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'title' => $this->title,
            'description' => $this->description,
            'url' => $this->url,
            'category' => $this->category,
            'created_by' => $this->whenLoaded('creator', fn () => new UserSummaryResource($this->creator)),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
        ];
    }
}
