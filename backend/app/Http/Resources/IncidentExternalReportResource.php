<?php

namespace App\Http\Resources;

use App\Models\IncidentExternalReport;
use App\Models\IncidentExternalReportStatusHistory;
use App\Models\IncidentReportAppeal;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin IncidentExternalReport */
class IncidentExternalReportResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        $memberView = (bool) $request->attributes->get('member_outcome_view', false);

        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'platform' => $this->platform,
            'reporting_channel' => $this->reporting_channel,
            'external_reference' => $memberView ? $this->external_reference : $this->external_reference,
            'reported_at' => optional($this->reported_at)?->toIso8601String(),
            'status' => $this->status,
            'decision' => $this->decision,
            'decision_note' => $memberView ? null : $this->decision_note,
            'outcome' => $this->outcome,
            'outcome_source' => $this->outcome_source,
            'outcome_summary' => $memberView ? null : $this->outcome_summary,
            'reporter_visible_summary' => $this->reporter_visible_summary,
            'verification_status' => $this->verification_status,
            'internal_notes' => $memberView ? null : $this->internal_notes,
            'created_by' => $memberView ? null : $this->whenLoaded('creator', fn () => [
                'id' => $this->creator?->id,
                'name' => $this->creator?->name,
            ]),
            'updated_by' => $memberView ? null : $this->whenLoaded('updater', fn () => [
                'id' => $this->updater?->id,
                'name' => $this->updater?->name,
            ]),
            'created_at' => optional($this->created_at)?->toIso8601String(),
            'updated_at' => optional($this->updated_at)?->toIso8601String(),
            'status_history' => IncidentExternalReportStatusHistoryResource::collection(
                $this->whenLoaded('statusHistory')
            )->additional(['member_outcome_view' => $memberView]),
            'appeals' => IncidentReportAppealResource::collection(
                $this->whenLoaded('appeals')
            )->additional(['member_outcome_view' => $memberView]),
        ];
    }
}
