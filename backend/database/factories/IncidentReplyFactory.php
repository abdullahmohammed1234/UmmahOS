<?php

namespace Database\Factories;

use App\Models\Incident;
use App\Models\IncidentReply;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<IncidentReply>
 */
class IncidentReplyFactory extends Factory
{
    protected $model = IncidentReply::class;

    public function definition(): array
    {
        return [
            'incident_id' => Incident::factory(),
            'author' => fake()->userName(),
            'content' => fake()->sentence(),
            'posted_at' => fake()->optional()->dateTimeBetween('-7 days', 'now'),
            'position' => 0,
        ];
    }
}
