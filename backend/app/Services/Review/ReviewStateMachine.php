<?php

namespace App\Services\Review;

use App\Exceptions\Review\ReviewStateException;
use App\Models\Incident;
use App\Models\IncidentReview;

/**
 * Explicit Community Shield human-review state machine.
 *
 * Distinguishes workflow status (open / reviewing / resolved)
 * from review outcome (confirmed / uncertain / closed).
 */
final class ReviewStateMachine
{
    public function assertCanStart(Incident $incident): void
    {
        if ($incident->status === Incident::STATUS_RESOLVED) {
            throw new ReviewStateException('Resolved incidents cannot be started for review without an explicit reopen workflow.');
        }

        if ($incident->status === Incident::STATUS_REVIEWING && $incident->current_reviewer_id !== null) {
            throw new ReviewStateException('This report is already under review.');
        }
    }

    public function assertCanDecide(Incident $incident): void
    {
        if ($incident->status !== Incident::STATUS_REVIEWING) {
            throw new ReviewStateException('Start review before recording a determination.');
        }

        if ($incident->status === Incident::STATUS_RESOLVED) {
            throw new ReviewStateException('Resolved incidents cannot receive a new determination.');
        }
    }

    public function assertCanConfirm(Incident $incident): void
    {
        $this->assertCanDecide($incident);
    }

    public function assertCanMarkUncertain(Incident $incident): void
    {
        $this->assertCanDecide($incident);
    }

    public function assertCanClose(Incident $incident): void
    {
        $this->assertCanDecide($incident);
    }

    public function assertCanEscalate(Incident $incident): void
    {
        if ($incident->status === Incident::STATUS_RESOLVED) {
            throw new ReviewStateException('Resolved incidents cannot be escalated.');
        }

        if ($incident->status !== Incident::STATUS_REVIEWING) {
            throw new ReviewStateException('Start review before escalating.');
        }

        if ($incident->escalated) {
            throw new ReviewStateException('This report is already escalated.');
        }
    }

    public function assertCanRequestContext(Incident $incident): void
    {
        if ($incident->status === Incident::STATUS_RESOLVED) {
            throw new ReviewStateException('Resolved incidents cannot receive context requests.');
        }

        if ($incident->status !== Incident::STATUS_REVIEWING) {
            throw new ReviewStateException('Start review before requesting additional context.');
        }
    }

    /**
     * @return list<string>
     */
    public function allowedActions(Incident $incident): array
    {
        $actions = [];

        try {
            $this->assertCanStart($incident);
            $actions[] = 'start';
        } catch (ReviewStateException) {
        }

        try {
            $this->assertCanConfirm($incident);
            $actions[] = 'confirm';
            $actions[] = 'uncertain';
            $actions[] = 'close';
        } catch (ReviewStateException) {
        }

        try {
            $this->assertCanEscalate($incident);
            $actions[] = 'escalate';
        } catch (ReviewStateException) {
        }

        try {
            $this->assertCanRequestContext($incident);
            $actions[] = 'request_context';
        } catch (ReviewStateException) {
        }

        return $actions;
    }

    public function outcomeLabel(?string $outcome): ?string
    {
        return match ($outcome) {
            IncidentReview::OUTCOME_CONFIRMED => 'Confirmed',
            IncidentReview::OUTCOME_UNCERTAIN => 'Uncertain',
            IncidentReview::OUTCOME_CLOSED => 'Closed',
            default => null,
        };
    }
}
