<?php

namespace Database\Factories;

use App\Models\Incident;
use App\Models\IncidentRelatedItem;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<IncidentRelatedItem>
 */
class IncidentRelatedItemFactory extends Factory
{
    protected $model = IncidentRelatedItem::class;

    public function definition(): array
    {
        return [
            'incident_id' => Incident::factory(),
            'platform' => fake()->randomElement(Incident::platforms()),
            'content_type' => fake()->randomElement(Incident::contentTypes()),
            'reference_url' => null,
            'description' => fake()->sentence(),
            'observed_at' => fake()->optional()->dateTimeBetween('-7 days', 'now'),
        ];
    }
}
