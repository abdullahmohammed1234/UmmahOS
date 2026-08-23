<?php

namespace App\Services;

use App\Models\Course;
use App\Models\Organization;
use App\Models\User;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Database\Eloquent\Collection;

class CourseService
{
    /**
     * @return Collection<int, Course>
     */
    public function listForCurrentViewer(Organization $organization): Collection
    {
        $query = $organization->courses()
            ->with('creator')
            ->orderBy('title');

        if (! CommunityVisibility::canManage(Permissions::COURSES_MANAGE)) {
            $query->published();
        }

        return $query->get();
    }

    public function findVisible(Organization $organization, int $courseId): Course
    {
        $query = $organization->courses()->with('creator')->whereKey($courseId);

        if (! CommunityVisibility::canManage(Permissions::COURSES_MANAGE)) {
            $query->published();
        }

        return $query->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function create(Organization $organization, User $actor, array $attributes): Course
    {
        return $organization->courses()->create([
            'title' => $attributes['title'],
            'description' => $attributes['description'] ?? null,
            'status' => $attributes['status'] ?? Course::STATUS_DRAFT,
            'created_by' => $actor->id,
        ])->load('creator');
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(Course $course, array $attributes): Course
    {
        $course->update($attributes);

        return $course->fresh('creator');
    }

    public function delete(Course $course): void
    {
        $course->delete();
    }
}
