<?php

namespace Database\Factories;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\User;
use App\Prompts\CommunityShieldContextAnalysisV1;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<IncidentAiAnalysis>
 */
class IncidentAiAnalysisFactory extends Factory
{
    protected $model = IncidentAiAnalysis::class;

    public function definition(): array
    {
        return [
            'incident_id' => Incident::factory(),
            'provider' => 'fake',
            'model' => 'fake-model',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => [
                'signals' => [
                    [
                        'name' => 'no_clear_signal',
                        'description' => 'Demo / fixture analysis — not a live model result.',
                        'evidence' => ['Fixture only'],
                        'confidence' => 'low',
                    ],
                ],
                'classification' => [
                    'label' => 'unclear',
                    'confidence' => 'low',
                ],
                'uncertainty' => [
                    'level' => 'high',
                    'explanation' => 'Demo / fixture analysis — not a live model result.',
                ],
                'alternative_interpretation' => null,
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
            'error_message' => null,
            'requested_by' => User::factory(),
        ];
    }

    public function failed(): static
    {
        return $this->state(fn () => [
            'status' => IncidentAiAnalysis::STATUS_FAILED,
            'analysis' => null,
            'error_message' => 'AI analysis unavailable.',
        ]);
    }

    public function queued(): static
    {
        return $this->state(fn () => [
            'status' => IncidentAiAnalysis::STATUS_QUEUED,
            'analysis' => null,
            'error_message' => null,
        ]);
    }
}
