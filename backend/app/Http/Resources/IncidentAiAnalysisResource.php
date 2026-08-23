<?php

namespace App\Http\Resources;

use App\Models\IncidentAiAnalysis;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin IncidentAiAnalysis
 */
class IncidentAiAnalysisResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'incident_id' => $this->incident_id,
            'provider' => $this->provider,
            'model' => $this->model,
            'prompt_version' => $this->prompt_version,
            'status' => $this->status,
            'analysis' => $this->analysis,
            'error_message' => $this->when(
                $this->status === IncidentAiAnalysis::STATUS_FAILED,
                $this->error_message
            ),
            'requested_by' => $this->whenLoaded('requester', fn () => $this->requester
                ? new UserSummaryResource($this->requester)
                : null),
            'created_at' => $this->created_at?->toIso8601String(),
            'updated_at' => $this->updated_at?->toIso8601String(),
            'advisory_disclaimer' => 'AI-generated analysis is advisory and may be incorrect. Human review is required for decisions.',
        ];
    }
}
