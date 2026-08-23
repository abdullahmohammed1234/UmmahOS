<?php

namespace Database\Factories;

use App\Models\Announcement;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Announcement>
 */
class AnnouncementFactory extends Factory
{
    public function definition(): array
    {
        return [
            'organization_id' => Organization::factory(),
            'title' => fake()->sentence(6),
            'body' => fake()->paragraphs(2, true),
            'published_at' => now(),
            'created_by' => User::factory(),
        ];
    }

    public function unpublished(): static
    {
        return $this->state(fn () => [
            'published_at' => null,
        ]);
    }

    public function published(?\DateTimeInterface $at = null): static
    {
        return $this->state(fn () => [
            'published_at' => $at ?? now(),
        ]);
    }
}
