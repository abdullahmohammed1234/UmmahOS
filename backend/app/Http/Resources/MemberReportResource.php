<?php

namespace App\Http\Resources;

use App\Models\Incident;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin Incident */
class MemberReportResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'reference' => sprintf(
                'CS-%s-%d',
                strtoupper($this->organization?->slug ?? 'ORG'),
                $this->id
            ),
            'platform' => $this->platform,
            'content_type' => $this->content_type,
            'status' => $this->status,
            'review_outcome' => $this->review_outcome,
            'submitted_at' => optional($this->created_at)?->toIso8601String(),
            'external_reports' => $this->whenLoaded('externalReports', function () use ($request) {
                $request->attributes->set('member_outcome_view', true);

                return IncidentExternalReportResource::collection($this->externalReports);
            }),
            'external_report_count' => $this->whenLoaded('externalReports', fn () => $this->externalReports->count()),
        ];
    }
}
