<?php

namespace App\Services\Outcome;

use App\Exceptions\Outcome\OutcomeStateException;
use App\Models\IncidentExternalReport;

/**
 * Validates external report status transitions.
 *
 * Allowed:
 *   reported → under_review | decision
 *   under_review → decision
 *   decision → outcome
 *   outcome → outcome (updates within final stage)
 */
final class OutcomeStateMachine
{
    /**
     * @return list<string>
     */
    public function allowedTransitions(string $currentStatus): array
    {
        return match ($currentStatus) {
            IncidentExternalReport::STATUS_REPORTED => [
                IncidentExternalReport::STATUS_UNDER_REVIEW,
                IncidentExternalReport::STATUS_DECISION,
            ],
            IncidentExternalReport::STATUS_UNDER_REVIEW => [
                IncidentExternalReport::STATUS_DECISION,
            ],
            IncidentExternalReport::STATUS_DECISION => [
                IncidentExternalReport::STATUS_OUTCOME,
            ],
            IncidentExternalReport::STATUS_OUTCOME => [
                IncidentExternalReport::STATUS_OUTCOME,
            ],
            default => [],
        };
    }

    public function assertCanTransition(string $from, string $to): void
    {
        if ($from === $to && $from === IncidentExternalReport::STATUS_OUTCOME) {
            return;
        }

        if (! in_array($to, $this->allowedTransitions($from), true)) {
            throw new OutcomeStateException(
                sprintf('Cannot transition external report from "%s" to "%s".', $from, $to)
            );
        }
    }

    public function assertDecisionRequired(string $newStatus, ?string $decision): void
    {
        if ($newStatus === IncidentExternalReport::STATUS_DECISION && $decision === null) {
            throw new OutcomeStateException('A decision value is required when status is decision.');
        }
    }

    public function assertOutcomeRequired(string $newStatus, ?string $outcome): void
    {
        if ($newStatus === IncidentExternalReport::STATUS_OUTCOME && $outcome === null) {
            throw new OutcomeStateException('An outcome value is required when status is outcome.');
        }
    }
}
