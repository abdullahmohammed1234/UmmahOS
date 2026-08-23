<?php

namespace Database\Factories;

use App\Models\Organization;
use App\Models\Resource;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Resource>
 */
class ResourceFactory extends Factory
{
    public function definition(): array
    {
        return [
            'organization_id' => Organization::factory(),
            'title' => fake()->sentence(4),
            'description' => fake()->sentence(12),
            'url' => fake()->url(),
            'category' => fake()->randomElement(['community', 'education', 'worship']),
            'created_by' => User::factory(),
        ];
    }
}
