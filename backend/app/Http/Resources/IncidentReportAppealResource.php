<?php

namespace App\Http\Resources;

use App\Models\IncidentReportAppeal;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin IncidentReportAppeal */
class IncidentReportAppealResource extends JsonResource
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
            'submitted_at' => optional($this->submitted_at)?->toIso8601String(),
            'submitted_by' => $memberView ? null : $this->whenLoaded('submitter', fn () => [
                'id' => $this->submitter?->id,
                'name' => $this->submitter?->name,
            ]),
            'reason' => $this->reason,
            'additional_evidence' => $this->additional_evidence,
            'reference' => $this->reference,
            'notes' => $memberView ? null : $this->notes,
            'status' => $this->status,
            'response' => $this->response,
            'responded_at' => optional($this->responded_at)?->toIso8601String(),
            'responded_by' => $memberView ? null : $this->whenLoaded('responder', fn () => [
                'id' => $this->responder?->id,
                'name' => $this->responder?->name,
            ]),
            'created_at' => optional($this->created_at)?->toIso8601String(),
            'updated_at' => optional($this->updated_at)?->toIso8601String(),
        ];
    }
}
