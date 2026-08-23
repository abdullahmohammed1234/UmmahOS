<?php

namespace App\Services\Education;

use App\Models\AcademyLesson;
use App\Models\AcademyLessonProgress;
use App\Models\AcademyScenario;
use App\Models\Organization;
use App\Models\User;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Carbon;

class AcademyEducationService
{
    /**
     * @return Collection<int, AcademyLesson>
     */
    public function communitySafetyLessons(Organization $organization): Collection
    {
        $query = $organization->academyLessons()
            ->with(['course', 'scenarios'])
            ->where('category', AcademyLesson::CATEGORY_COMMUNITY_SAFETY)
            ->orderBy('title');

        if (! CommunityVisibility::canManage(Permissions::COURSES_MANAGE)) {
            $query->where('status', AcademyLesson::STATUS_PUBLISHED);
        }

        return $query->get();
    }

    public function findLesson(Organization $organization, int $lessonId): AcademyLesson
    {
        $query = $organization->academyLessons()
            ->with(['course', 'scenarios'])
            ->whereKey($lessonId);

        if (! CommunityVisibility::canManage(Permissions::COURSES_MANAGE)) {
            $query->where('status', AcademyLesson::STATUS_PUBLISHED);
        }

        return $query->firstOrFail();
    }

    public function findScenario(Organization $organization, int $scenarioId): AcademyScenario
    {
        $query = $organization->academyScenarios()
            ->with('lesson')
            ->whereKey($scenarioId);

        if (! CommunityVisibility::canManage(Permissions::COURSES_MANAGE)) {
            $query->whereHas('lesson', fn ($q) => $q->where('status', AcademyLesson::STATUS_PUBLISHED));
        }

        return $query->firstOrFail();
    }

    /**
     * @return Collection<int, AcademyLessonProgress>
     */
    public function progressForUser(Organization $organization, User $user): Collection
    {
        return $organization->academyLessonProgress()
            ->with('lesson')
            ->where('user_id', $user->id)
            ->latest()
            ->get();
    }

    public function markStarted(Organization $organization, User $user, AcademyLesson $lesson): AcademyLessonProgress
    {
        $progress = $organization->academyLessonProgress()
            ->firstOrNew([
                'user_id' => $user->id,
                'academy_lesson_id' => $lesson->id,
            ]);

        if (! $progress->exists) {
            $progress->fill([
                'status' => AcademyLessonProgress::STATUS_STARTED,
                'started_at' => Carbon::now(),
            ]);
        }

        $progress->save();

        return $progress->fresh('lesson');
    }

    public function markCompleted(Organization $organization, User $user, AcademyLesson $lesson): AcademyLessonProgress
    {
        $progress = $this->markStarted($organization, $user, $lesson);
        $progress->update([
            'status' => AcademyLessonProgress::STATUS_COMPLETED,
            'completed_at' => Carbon::now(),
        ]);

        return $progress->fresh('lesson');
    }
}
