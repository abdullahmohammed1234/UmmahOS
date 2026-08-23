<?php

namespace Database\Factories;

use App\Models\Course;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Course>
 */
class CourseFactory extends Factory
{
    public function definition(): array
    {
        return [
            'organization_id' => Organization::factory(),
            'title' => fake()->sentence(4),
            'description' => fake()->paragraph(),
            'status' => Course::STATUS_PUBLISHED,
            'created_by' => User::factory(),
        ];
    }

    public function draft(): static
    {
        return $this->state(fn () => [
            'status' => Course::STATUS_DRAFT,
        ]);
    }

    public function published(): static
    {
        return $this->state(fn () => [
            'status' => Course::STATUS_PUBLISHED,
        ]);
    }
}
