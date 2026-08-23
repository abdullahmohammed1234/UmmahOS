<?php

namespace App\Http\Resources;

use App\Models\IncidentExternalReportStatusHistory;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin IncidentExternalReportStatusHistory */
class IncidentExternalReportStatusHistoryResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $memberView = (bool) ($request->attributes->get('member_outcome_view', false)
            ?? $this->additional['member_outcome_view'] ?? false);

        return [
            'id' => $this->id,
            'previous_status' => $this->previous_status,
            'new_status' => $this->new_status,
            'decision' => $this->decision,
            'outcome' => $this->outcome,
            'changed_by' => $memberView ? null : $this->whenLoaded('changedByUser', fn () => [
                'id' => $this->changedByUser?->id,
                'name' => $this->changedByUser?->name,
            ]),
            'changed_at' => optional($this->changed_at)?->toIso8601String(),
            'note' => $memberView ? null : $this->note,
        ];
    }
}
