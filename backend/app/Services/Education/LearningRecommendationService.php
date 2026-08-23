<?php

namespace App\Services\Education;

use App\Models\AcademyLesson;
use App\Models\Course;
use App\Models\LearningPattern;
use App\Models\LearningRecommendation;
use App\Models\Organization;
use App\Models\User;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\AccessDeniedHttpException;

class LearningRecommendationService
{
    /**
     * @return Collection<int, LearningRecommendation>
     */
    public function listForViewer(Organization $organization): Collection
    {
        $query = $organization->learningRecommendations()
            ->with([
                'pattern' => fn ($q) => $q->select([
                    'id',
                    'organization_id',
                    'pattern_type',
                    'title',
                    'summary',
                    'learning_objective',
                    'domain',
                    'severity_context',
                    'status',
                    'created_by',
                    'approved_by',
                    'approved_at',
                    'created_at',
                    'updated_at',
                ]),
                'course',
                'lesson.scenarios',
                'creator',
            ])
            ->latest();

        if (! $this->canManageRecommendations()) {
            $query->where('status', LearningRecommendation::STATUS_PUBLISHED)
                ->whereHas('pattern', fn ($q) => $q->where('status', LearningPattern::STATUS_APPROVED))
                ->whereHas('lesson', fn ($q) => $q->where('status', AcademyLesson::STATUS_PUBLISHED));
        }

        return $query->get();
    }

    public function findVisible(Organization $organization, int $id): LearningRecommendation
    {
        $query = $organization->learningRecommendations()
            ->with(['pattern', 'course', 'lesson.scenarios', 'creator'])
            ->whereKey($id);

        if (! $this->canManageRecommendations()) {
            $query->where('status', LearningRecommendation::STATUS_PUBLISHED)
                ->whereHas('pattern', fn ($q) => $q->where('status', LearningPattern::STATUS_APPROVED))
                ->whereHas('lesson', fn ($q) => $q->where('status', AcademyLesson::STATUS_PUBLISHED));
        }

        return $query->firstOrFail();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function create(Organization $organization, User $actor, array $attributes): LearningRecommendation
    {
        $this->assertCanManage();

        $pattern = $organization->learningPatterns()
            ->whereKey($attributes['learning_pattern_id'])
            ->firstOrFail();

        $status = $attributes['status'] ?? LearningRecommendation::STATUS_DRAFT;

        if ($status === LearningRecommendation::STATUS_PUBLISHED && ! $pattern->isApproved()) {
            throw ValidationException::withMessages([
                'learning_pattern_id' => 'Only approved learning patterns can have published recommendations.',
            ]);
        }

        $courseId = $attributes['academy_course_id'] ?? null;
        $lessonId = $attributes['academy_lesson_id'] ?? null;

        if ($courseId !== null) {
            $organization->courses()->whereKey($courseId)->firstOrFail();
        }

        if ($lessonId !== null) {
            $lesson = $organization->academyLessons()->whereKey($lessonId)->firstOrFail();
            $courseId = $courseId ?? $lesson->course_id;
        }

        return $organization->learningRecommendations()->create([
            'learning_pattern_id' => $pattern->id,
            'academy_course_id' => $courseId,
            'academy_lesson_id' => $lessonId,
            'reason' => $attributes['reason'],
            'status' => $status,
            'created_by' => $actor->id,
        ])->load(['pattern', 'course', 'lesson.scenarios', 'creator']);
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(LearningRecommendation $recommendation, array $attributes): LearningRecommendation
    {
        $this->assertCanManage();

        if (isset($attributes['status'])
            && $attributes['status'] === LearningRecommendation::STATUS_PUBLISHED
            && ! $recommendation->pattern->isApproved()
        ) {
            throw ValidationException::withMessages([
                'status' => 'Only approved learning patterns can have published recommendations.',
            ]);
        }

        if (isset($attributes['academy_lesson_id'])) {
            $lesson = $recommendation->organization
                ->academyLessons()
                ->whereKey($attributes['academy_lesson_id'])
                ->firstOrFail();
            $attributes['academy_course_id'] = $attributes['academy_course_id'] ?? $lesson->course_id;
        }

        if (isset($attributes['academy_course_id'])) {
            $recommendation->organization
                ->courses()
                ->whereKey($attributes['academy_course_id'])
                ->firstOrFail();
        }

        $recommendation->update(collect($attributes)->only([
            'academy_course_id',
            'academy_lesson_id',
            'reason',
            'status',
        ])->all());

        return $recommendation->fresh(['pattern', 'course', 'lesson.scenarios', 'creator']);
    }

    private function canManageRecommendations(): bool
    {
        return CommunityVisibility::canManage(Permissions::EDUCATION_RECOMMENDATIONS_MANAGE)
            || CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE);
    }

    private function assertCanManage(): void
    {
        if (! $this->canManageRecommendations()) {
            throw new AccessDeniedHttpException('You cannot manage learning recommendations.');
        }
    }
}
