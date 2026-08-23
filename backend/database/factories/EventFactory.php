<?php

namespace Database\Factories;

use App\Models\Event;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Event>
 */
class EventFactory extends Factory
{
    public function definition(): array
    {
            $startsAt = now()->addDays(fake()->numberBetween(1, 21))->setTime(18, 30);

            return [
                'organization_id' => Organization::factory(),
                'title' => fake()->sentence(5),
                'description' => fake()->paragraph(),
                'location' => fake()->city().' MSA Room',
                'starts_at' => $startsAt,
                'ends_at' => $startsAt->copy()->addHours(2),
                'registration_url' => null,
                'created_by' => User::factory(),
            ];
    }

    public function past(): static
    {
        return $this->state(function () {
            $startsAt = now()->subDays(7)->setTime(18, 0);

            return [
                'starts_at' => $startsAt,
                'ends_at' => $startsAt->copy()->addHours(2),
            ];
        });
    }
}
