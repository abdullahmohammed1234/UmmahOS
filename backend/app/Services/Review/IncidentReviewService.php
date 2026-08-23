<?php

namespace App\Services\Review;

use App\Exceptions\Review\ReviewConflictException;
use App\Exceptions\Review\ReviewStateException;
use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentContextRequest;
use App\Models\IncidentReview;
use App\Models\IncidentReviewAction;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;

class IncidentReviewService
{
    public function __construct(
        private readonly ReviewStateMachine $stateMachine,
    ) {}

    /**
     * @param  array{
     *     status?: string|null,
     *     platform?: string|null,
     *     confidence?: string|null,
     *     uncertainty?: string|null,
     *     classification?: string|null,
     *     escalated?: bool|null,
     * }  $filters
     * @return Collection<int, Incident>
     */
    public function queue(Organization $organization, array $filters = []): Collection
    {
        $query = $organization->incidents()
            ->with([
                'reporter',
                'classifier',
                'currentReviewer',
                'replies',
                'relatedItems',
                'aiAnalyses' => fn ($q) => $q->orderByDesc('id')->limit(1),
                'contextRequests' => fn ($q) => $q->where('status', IncidentContextRequest::STATUS_OPEN),
            ]);

        if (! empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (! empty($filters['platform'])) {
            $query->where('platform', $filters['platform']);
        }

        if (! empty($filters['classification'])) {
            $query->where('safety_classification', $filters['classification']);
        }

        if (array_key_exists('escalated', $filters) && $filters['escalated'] !== null) {
            $query->where('escalated', (bool) $filters['escalated']);
        }

        $incidents = $query->get();

        $incidents = $incidents->filter(function (Incident $incident) use ($filters) {
            $analysis = $incident->aiAnalyses->first();
            $package = $analysis?->status === IncidentAiAnalysis::STATUS_COMPLETED
                ? $analysis->analysis
                : null;

            if (! empty($filters['confidence'])) {
                $confidence = data_get($package, 'classification.confidence');
                if ($confidence !== $filters['confidence']) {
                    return false;
                }
            }

            if (! empty($filters['uncertainty'])) {
                $uncertainty = data_get($package, 'uncertainty.level');
                if ($uncertainty !== $filters['uncertainty']) {
                    return false;
                }
            }

            return true;
        })->values();

        return $incidents->sort(function (Incident $a, Incident $b) {
            $priority = function (Incident $incident): array {
                $analysis = $incident->aiAnalyses->first();
                $package = $analysis?->status === IncidentAiAnalysis::STATUS_COMPLETED
                    ? $analysis->analysis
                    : null;
                $uncertainty = data_get($package, 'uncertainty.level');

                $statusRank = match ($incident->status) {
                    Incident::STATUS_REVIEWING => 0,
                    Incident::STATUS_OPEN => 1,
                    default => 2,
                };

                $escalatedRank = $incident->escalated ? 0 : 1;
                $uncertaintyRank = match ($uncertainty) {
                    'high' => 0,
                    'moderate' => 1,
                    'low' => 2,
                    default => 3,
                };

                return [$statusRank, $escalatedRank, $uncertaintyRank, $incident->created_at?->timestamp ?? 0];
            };

            return $priority($a) <=> $priority($b);
        })->values();
    }

    public function reviewPackage(Organization $organization, int $incidentId): Incident
    {
        return $organization->incidents()
            ->with([
                'reporter',
                'classifier',
                'currentReviewer',
                'escalatedByUser',
                'replies',
                'relatedItems',
                'aiAnalyses' => fn ($q) => $q->with('requester')->orderByDesc('id'),
                'reviews' => fn ($q) => $q->with('reviewer')->orderByDesc('id'),
                'reviewActions' => fn ($q) => $q->with('actor')->orderBy('id'),
                'contextRequests' => fn ($q) => $q->with(['requester', 'resolver'])->orderByDesc('id'),
            ])
            ->whereKey($incidentId)
            ->firstOrFail();
    }

    /**
     * @param  array{review_lock_version?: int|null}  $attributes
     */
    public function start(Incident $incident, User $reviewer, array $attributes = []): Incident
    {
        return $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer) {
            $this->stateMachine->assertCanStart($locked);

            $locked->reviews()->where('is_current', true)->update(['is_current' => false]);

            $locked->reviews()->create([
                'reviewer_id' => $reviewer->id,
                'outcome' => null,
                'notes' => null,
                'is_current' => true,
            ]);

            $locked->forceFill([
                'status' => Incident::STATUS_REVIEWING,
                'current_reviewer_id' => $reviewer->id,
                'review_started_at' => now(),
                'review_outcome' => null,
            ])->save();

            $this->recordAction($locked, $reviewer, IncidentReviewAction::ACTION_STARTED, 'Started review');
        });
    }

    /**
     * @param  array{
     *     notes: string,
     *     safety_classification: string,
     *     review_lock_version?: int|null,
     * }  $attributes
     */
    public function confirm(Incident $incident, User $reviewer, array $attributes): Incident
    {
        return $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer, $attributes) {
            $this->stateMachine->assertCanConfirm($locked);
            $this->assertReviewerOfRecord($locked, $reviewer);

            $classification = $attributes['safety_classification'];
            if ($classification === Incident::CLASSIFICATION_UNCLASSIFIED) {
                throw new ReviewStateException('Confirm requires a human safety classification.');
            }

            $notes = trim($attributes['notes']);
            if ($notes === '') {
                throw new ReviewStateException('Confirm requires a concise human rationale.');
            }

            $this->finalizeCurrentReview($locked, $reviewer, IncidentReview::OUTCOME_CONFIRMED, $notes, $classification);

            $locked->forceFill([
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => IncidentReview::OUTCOME_CONFIRMED,
                'review_notes' => $notes,
                'safety_classification' => $classification,
                'classified_by' => $reviewer->id,
                'classified_at' => now(),
            ])->save();

            $this->recordAction($locked, $reviewer, IncidentReviewAction::ACTION_CONFIRMED, $notes, [
                'safety_classification' => $classification,
                'outcome' => IncidentReview::OUTCOME_CONFIRMED,
            ]);
        });
    }

    /**
     * @param  array{notes: string, review_lock_version?: int|null}  $attributes
     */
    public function markUncertain(Incident $incident, User $reviewer, array $attributes): Incident
    {
        return $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer, $attributes) {
            $this->stateMachine->assertCanMarkUncertain($locked);
            $this->assertReviewerOfRecord($locked, $reviewer);

            $notes = trim($attributes['notes']);
            if ($notes === '') {
                throw new ReviewStateException('Uncertain determinations require reviewer notes.');
            }

            $this->finalizeCurrentReview($locked, $reviewer, IncidentReview::OUTCOME_UNCERTAIN, $notes);

            $locked->forceFill([
                'status' => Incident::STATUS_REVIEWING,
                'review_outcome' => IncidentReview::OUTCOME_UNCERTAIN,
                'review_notes' => $notes,
            ])->save();

            $this->recordAction($locked, $reviewer, IncidentReviewAction::ACTION_MARKED_UNCERTAIN, $notes, [
                'outcome' => IncidentReview::OUTCOME_UNCERTAIN,
            ]);
        });
    }

    /**
     * @param  array{notes?: string|null, review_lock_version?: int|null}  $attributes
     */
    public function close(Incident $incident, User $reviewer, array $attributes = []): Incident
    {
        return $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer, $attributes) {
            $this->stateMachine->assertCanClose($locked);
            $this->assertReviewerOfRecord($locked, $reviewer);

            $notes = trim((string) ($attributes['notes'] ?? ''));

            $this->finalizeCurrentReview($locked, $reviewer, IncidentReview::OUTCOME_CLOSED, $notes !== '' ? $notes : null);

            $locked->forceFill([
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => IncidentReview::OUTCOME_CLOSED,
                'review_notes' => $notes !== '' ? $notes : $locked->review_notes,
            ])->save();

            $this->recordAction(
                $locked,
                $reviewer,
                IncidentReviewAction::ACTION_CLOSED,
                $notes !== '' ? $notes : 'Closed review',
                ['outcome' => IncidentReview::OUTCOME_CLOSED]
            );
        });
    }

    /**
     * @param  array{reason: string, review_lock_version?: int|null}  $attributes
     */
    public function escalate(Incident $incident, User $reviewer, array $attributes): Incident
    {
        return $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer, $attributes) {
            $this->stateMachine->assertCanEscalate($locked);
            $this->assertReviewerOfRecord($locked, $reviewer);

            $reason = trim($attributes['reason']);
            if ($reason === '') {
                throw new ReviewStateException('Escalation requires a reason.');
            }

            $current = $locked->reviews()->where('is_current', true)->first();
            if ($current) {
                $current->update(['escalation_reason' => $reason]);
            }

            $locked->forceFill([
                'status' => Incident::STATUS_REVIEWING,
                'escalated' => true,
                'escalation_reason' => $reason,
                'escalated_by' => $reviewer->id,
                'escalated_at' => now(),
            ])->save();

            $this->recordAction($locked, $reviewer, IncidentReviewAction::ACTION_ESCALATED, $reason, [
                'escalated' => true,
            ]);
        });
    }

    /**
     * @param  array{reason: string, review_lock_version?: int|null}  $attributes
     */
    public function requestContext(Incident $incident, User $reviewer, array $attributes): IncidentContextRequest
    {
        $request = null;

        $this->mutate($incident, $reviewer, $attributes, function (Incident $locked) use ($reviewer, $attributes, &$request) {
            $this->stateMachine->assertCanRequestContext($locked);
            $this->assertReviewerOfRecord($locked, $reviewer);

            $reason = trim($attributes['reason']);
            if ($reason === '') {
                throw new ReviewStateException('Context requests require a description of what is needed.');
            }

            $request = $locked->contextRequests()->create([
                'requested_by' => $reviewer->id,
                'reason' => $reason,
                'status' => IncidentContextRequest::STATUS_OPEN,
                'requested_at' => now(),
            ]);

            $locked->forceFill([
                'status' => Incident::STATUS_REVIEWING,
                'review_outcome' => IncidentReview::OUTCOME_UNCERTAIN,
            ])->save();

            $this->recordAction($locked, $reviewer, IncidentReviewAction::ACTION_CONTEXT_REQUESTED, $reason, [
                'context_request_id' => $request->id,
            ]);
        });

        /** @var IncidentContextRequest $request */
        return $request->load(['requester', 'resolver']);
    }

    /**
     * @param  array{status: string, review_lock_version?: int|null}  $attributes
     */
    public function resolveContextRequest(
        Incident $incident,
        IncidentContextRequest $contextRequest,
        User $actor,
        array $attributes
    ): IncidentContextRequest {
        if ($contextRequest->incident_id !== $incident->id) {
            throw new ReviewStateException('Context request does not belong to this report.', 404);
        }

        if ($contextRequest->status !== IncidentContextRequest::STATUS_OPEN) {
            throw new ReviewStateException('Only open context requests can be updated.');
        }

        $status = $attributes['status'];
        if (! in_array($status, [IncidentContextRequest::STATUS_FULFILLED, IncidentContextRequest::STATUS_CANCELLED], true)) {
            throw new ReviewStateException('Invalid context request status.');
        }

        $this->mutate($incident, $actor, $attributes, function (Incident $locked) use ($contextRequest, $actor, $status) {
            $contextRequest->refresh();

            $contextRequest->forceFill([
                'status' => $status,
                'resolved_by' => $actor->id,
                'resolved_at' => now(),
            ])->save();

            $action = $status === IncidentContextRequest::STATUS_FULFILLED
                ? IncidentReviewAction::ACTION_CONTEXT_FULFILLED
                : IncidentReviewAction::ACTION_CONTEXT_CANCELLED;

            $this->recordAction($locked, $actor, $action, $contextRequest->reason, [
                'context_request_id' => $contextRequest->id,
                'status' => $status,
            ]);
        });

        return $contextRequest->fresh(['requester', 'resolver']);
    }

    /**
     * @return list<string>
     */
    public function allowedActions(Incident $incident): array
    {
        return $this->stateMachine->allowedActions($incident);
    }

    /**
     * @param  array<string, mixed>  $attributes
     * @param  callable(Incident): void  $callback
     */
    private function mutate(Incident $incident, User $actor, array $attributes, callable $callback): Incident
    {
        return DB::transaction(function () use ($incident, $attributes, $callback) {
            /** @var Incident $locked */
            $locked = Incident::query()->whereKey($incident->id)->lockForUpdate()->firstOrFail();

            $expectedVersion = $attributes['review_lock_version'] ?? null;
            if ($expectedVersion !== null && (int) $expectedVersion !== (int) $locked->review_lock_version) {
                throw new ReviewConflictException;
            }

            $callback($locked);

            $locked->forceFill([
                'review_lock_version' => ((int) $locked->review_lock_version) + 1,
            ])->save();

            return $this->reviewPackage($locked->organization, $locked->id);
        });
    }

    private function assertReviewerOfRecord(Incident $incident, User $reviewer): void
    {
        if ($incident->current_reviewer_id === null) {
            throw new ReviewStateException('Start review before performing this action.');
        }

        if ((int) $incident->current_reviewer_id !== (int) $reviewer->id) {
            throw new ReviewConflictException(
                'Another reviewer is already reviewing this report. Reload and coordinate before continuing.'
            );
        }
    }

    private function finalizeCurrentReview(
        Incident $incident,
        User $reviewer,
        string $outcome,
        ?string $notes,
        ?string $classification = null
    ): void {
        $current = $incident->reviews()->where('is_current', true)->first();

        if ($current === null) {
            $current = $incident->reviews()->create([
                'reviewer_id' => $reviewer->id,
                'is_current' => true,
            ]);
        }

        $current->update([
            'reviewer_id' => $reviewer->id,
            'outcome' => $outcome,
            'notes' => $notes,
            'safety_classification' => $classification,
            'is_current' => true,
        ]);
    }

    /**
     * @param  array<string, mixed>|null  $payload
     */
    private function recordAction(
        Incident $incident,
        User $actor,
        string $action,
        ?string $notes = null,
        ?array $payload = null
    ): IncidentReviewAction {
        return $incident->reviewActions()->create([
            'actor_id' => $actor->id,
            'action' => $action,
            'notes' => $notes,
            'payload' => $payload,
            'created_at' => now(),
        ]);
    }
}
