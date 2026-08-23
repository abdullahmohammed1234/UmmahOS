<?php

namespace App\Services\Education;

use App\Models\Incident;
use App\Models\LearningPattern;
use App\Models\Organization;
use App\Models\User;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\AccessDeniedHttpException;

class LearningPatternService
{
    /**
     * @return Collection<int, LearningPattern>
     */
    public function listForStaff(Organization $organization): Collection
    {
        $this->assertCanViewPatterns();

        return $organization->learningPatterns()
            ->with(['creator', 'approver', 'recommendations.lesson', 'recommendations.course'])
            ->latest()
            ->get();
    }

    public function findForStaff(Organization $organization, int $patternId): LearningPattern
    {
        $this->assertCanViewPatterns();

        return $organization->learningPatterns()
            ->with(['creator', 'approver', 'recommendations.lesson', 'recommendations.course', 'sourceIncident'])
            ->whereKey($patternId)
            ->firstOrFail();
    }

    public function findForIncident(Organization $organization, int $incidentId): ?LearningPattern
    {
        $this->assertCanViewPatterns();

        return $organization->learningPatterns()
            ->with(['creator', 'approver', 'recommendations.lesson', 'recommendations.course'])
            ->where('source_incident_id', $incidentId)
            ->first();
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function createFromIncident(
        Organization $organization,
        Incident $incident,
        User $actor,
        array $attributes
    ): LearningPattern {
        $this->assertCanCreatePatterns();

        if ($incident->organization_id !== $organization->id) {
            abort(404);
        }

        if ($incident->review_outcome !== Incident::OUTCOME_CONFIRMED) {
            throw ValidationException::withMessages([
                'source_incident_id' => 'Only confirmed incidents may be promoted into learning patterns.',
            ]);
        }

        if ($organization->learningPatterns()->where('source_incident_id', $incident->id)->exists()) {
            throw ValidationException::withMessages([
                'source_incident_id' => 'A learning pattern already exists for this incident.',
            ]);
        }

        // Intentionally does NOT copy incident description, notes, URLs, or identities.
        return $organization->learningPatterns()->create([
            'source_incident_id' => $incident->id,
            'pattern_type' => $attributes['pattern_type'],
            'title' => $attributes['title'],
            'summary' => $attributes['summary'],
            'learning_objective' => $attributes['learning_objective'],
            'domain' => $attributes['domain'] ?? 'community-safety',
            'severity_context' => $attributes['severity_context'] ?? null,
            'status' => LearningPattern::STATUS_DRAFT,
            'created_by' => $actor->id,
        ])->load(['creator', 'approver', 'recommendations']);
    }

    /**
     * @param  array<string, mixed>  $attributes
     */
    public function update(LearningPattern $pattern, array $attributes): LearningPattern
    {
        $this->assertCanCreatePatterns();

        if ($pattern->status === LearningPattern::STATUS_ARCHIVED) {
            throw ValidationException::withMessages([
                'status' => 'Archived patterns cannot be edited.',
            ]);
        }

        if ($pattern->isApproved() && ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)) {
            throw new AccessDeniedHttpException('Only admins can edit approved patterns.');
        }

        $pattern->update(collect($attributes)->only([
            'pattern_type',
            'title',
            'summary',
            'learning_objective',
            'domain',
            'severity_context',
        ])->all());

        return $pattern->fresh(['creator', 'approver', 'recommendations.lesson', 'recommendations.course']);
    }

    public function approve(LearningPattern $pattern, User $actor): LearningPattern
    {
        if (! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)) {
            throw new AccessDeniedHttpException('Only education pattern managers can approve patterns.');
        }

        if ($pattern->status === LearningPattern::STATUS_ARCHIVED) {
            throw ValidationException::withMessages([
                'status' => 'Archived patterns cannot be approved.',
            ]);
        }

        $pattern->update([
            'status' => LearningPattern::STATUS_APPROVED,
            'approved_by' => $actor->id,
            'approved_at' => now(),
        ]);

        return $pattern->fresh(['creator', 'approver', 'recommendations.lesson', 'recommendations.course']);
    }

    public function archive(LearningPattern $pattern): LearningPattern
    {
        if (! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)) {
            throw new AccessDeniedHttpException('Only education pattern managers can archive patterns.');
        }

        $pattern->update([
            'status' => LearningPattern::STATUS_ARCHIVED,
        ]);

        return $pattern->fresh(['creator', 'approver', 'recommendations.lesson', 'recommendations.course']);
    }

    private function assertCanViewPatterns(): void
    {
        if (
            ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_VIEW)
            && ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_CREATE)
            && ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)
        ) {
            throw new AccessDeniedHttpException('You cannot view learning patterns.');
        }
    }

    private function assertCanCreatePatterns(): void
    {
        if (
            ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_CREATE)
            && ! CommunityVisibility::canManage(Permissions::EDUCATION_PATTERNS_MANAGE)
        ) {
            throw new AccessDeniedHttpException('You cannot create learning patterns.');
        }
    }
}
