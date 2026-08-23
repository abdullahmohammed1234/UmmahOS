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
            'status' => Incident::STATUS_OPEN,
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
