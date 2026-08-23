<?php

namespace Database\Factories;

use App\Models\Incident;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Incident>
 */
class IncidentFactory extends Factory
{
    public function definition(): array
    {
        return [
            'organization_id' => Organization::factory(),
            'reported_by' => User::factory(),
            'platform' => fake()->randomElement(Incident::platforms()),
            'content_type' => fake()->randomElement(Incident::contentTypes()),
            'visibility' => fake()->randomElement(Incident::visibilities()),
            'source_url' => null,
            'description' => fake()->paragraph(),
            'original_item_title' => null,
            'original_item_content' => null,
            'original_item_author' => null,
            'original_item_posted_at' => null,
            'observed_at' => null,
            'surrounding_context' => null,
            'language' => Incident::LANGUAGE_UNKNOWN,
            'reporter_notes' => null,
            'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
            'classified_by' => null,
            'classified_at' => null,
            'status' => Incident::STATUS_OPEN,
            'review_outcome' => null,
            'escalated' => false,
            'escalation_reason' => null,
            'escalated_by' => null,
            'escalated_at' => null,
            'current_reviewer_id' => null,
            'review_started_at' => null,
            'review_notes' => null,
            'review_lock_version' => 1,
        ];
    }

    public function reviewing(): static
    {
        return $this->state(fn () => [
            'status' => Incident::STATUS_REVIEWING,
        ]);
    }

    public function resolved(): static
    {
        return $this->state(fn () => [
            'status' => Incident::STATUS_RESOLVED,
        ]);
    }
}
