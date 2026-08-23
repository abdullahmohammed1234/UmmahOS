<?php

namespace App\Http\Resources;

use App\Models\AcademyScenario;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @mixin AcademyScenario
 */
class AcademyScenarioResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'organization_id' => $this->organization_id,
            'academy_lesson_id' => $this->academy_lesson_id,
            'title' => $this->title,
            'prompt' => $this->prompt,
            'context' => $this->context,
            'options' => $this->options,
            'expected_reasoning_signals' => $this->expected_reasoning_signals,
            'misconception_tags' => $this->misconception_tags,
            'difficulty' => $this->difficulty,
            'adapt_challenge_id' => $this->adapt_challenge_id,
            'adapt_topic_id' => $this->adapt_topic_id,
            'adapt_concept_id' => $this->adapt_concept_id,
            'adapt_domain' => $this->adapt_domain,
            'sort_order' => $this->sort_order,
            'is_demo' => (bool) $this->is_demo,
        ];
    }
}
