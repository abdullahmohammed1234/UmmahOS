<?php

namespace App\Services\Outcome;

use App\Exceptions\Outcome\OutcomeStateException;
use App\Models\Incident;
use App\Models\IncidentExternalReport;
use App\Models\IncidentExternalReportStatusHistory;
use App\Models\IncidentReportAppeal;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;

class IncidentOutcomeService
{
    public function __construct(
        private readonly OutcomeStateMachine $stateMachine,
    ) {}

    /**
     * @return Collection<int, IncidentExternalReport>
     */
    public function listForIncident(Organization $organization, int $incidentId): Collection
    {
        $incident = $this->findIncident($organization, $incidentId);

        return $this->loadReports($incident);
    }

    public function findReport(
        Organization $organization,
        int $incidentId,
        int $reportId
    ): IncidentExternalReport {
        $incident = $this->findIncident($organization, $incidentId);

        return $incident->externalReports()
            ->with(['statusHistory.changedByUser', 'appeals.submitter', 'appeals.responder', 'creator', 'updater'])
            ->findOrFail($reportId);
    }

    /**
     * @param  array<string, mixed>  $data
     */
    public function recordExternalReport(
        Organization $organization,
        int $incidentId,
        User $actor,
        array $data
    ): IncidentExternalReport {
        $incident = $this->findIncident($organization, $incidentId);

        return DB::transaction(function () use ($incident, $actor, $data) {
            $report = IncidentExternalReport::query()->create([
                'incident_id' => $incident->id,
                'organization_id' => $incident->organization_id,
                'platform' => $data['platform'],
                'reporting_channel' => $data['reporting_channel'],
                'external_reference' => $data['external_reference'] ?? null,
                'reported_at' => $data['reported_at'],
                'status' => IncidentExternalReport::STATUS_REPORTED,
                'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
                'internal_notes' => $data['internal_notes'] ?? null,
                'reporter_visible_summary' => $data['reporter_visible_summary'] ?? null,
                'created_by' => $actor->id,
                'updated_by' => $actor->id,
            ]);

            $this->appendHistory(
                $report,
                null,
                IncidentExternalReport::STATUS_REPORTED,
                $actor,
                $data['note'] ?? 'External report recorded.',
                null,
                null
            );

            return $this->findReport(
                $incident->organization,
                $incident->id,
                $report->id
            );
        });
    }

    /**
     * @param  array<string, mixed>  $data
     */
    public function updateReport(
        Organization $organization,
        int $incidentId,
        int $reportId,
        User $actor,
        array $data
    ): IncidentExternalReport {
        $report = $this->findReport($organization, $incidentId, $reportId);

        return DB::transaction(function () use ($report, $actor, $data) {
            $previousStatus = $report->status;
            $newStatus = $data['status'] ?? $previousStatus;

            if ($newStatus !== $previousStatus) {
                $this->stateMachine->assertCanTransition($previousStatus, $newStatus);
            }

            $decision = array_key_exists('decision', $data) ? $data['decision'] : $report->decision;
            $outcome = array_key_exists('outcome', $data) ? $data['outcome'] : $report->outcome;

            $this->stateMachine->assertDecisionRequired($newStatus, $decision);
            $this->stateMachine->assertOutcomeRequired($newStatus, $outcome);

            if ($newStatus === IncidentExternalReport::STATUS_DECISION) {
                $report->decision = $decision;
                if (array_key_exists('decision_note', $data)) {
                    $report->decision_note = $data['decision_note'];
                }
            }

            if ($newStatus === IncidentExternalReport::STATUS_OUTCOME) {
                $report->outcome = $outcome;
                if (array_key_exists('outcome_source', $data)) {
                    $report->outcome_source = $data['outcome_source'];
                }
                if (array_key_exists('outcome_summary', $data)) {
                    $report->outcome_summary = $data['outcome_summary'];
                }
                if (array_key_exists('reporter_visible_summary', $data)) {
                    $report->reporter_visible_summary = $data['reporter_visible_summary'];
                }
            }

            if (array_key_exists('verification_status', $data)) {
                $report->verification_status = $data['verification_status'];
            }

            if (array_key_exists('internal_notes', $data)) {
                $report->internal_notes = $data['internal_notes'];
            }

            if (array_key_exists('external_reference', $data)) {
                $report->external_reference = $data['external_reference'];
            }

            $report->status = $newStatus;
            $report->updated_by = $actor->id;
            $report->save();

            if ($newStatus !== $previousStatus || ($decision !== null && $newStatus === IncidentExternalReport::STATUS_DECISION)) {
                $this->appendHistory(
                    $report,
                    $previousStatus !== $newStatus ? $previousStatus : null,
                    $newStatus,
                    $actor,
                    $data['note'] ?? $this->defaultTransitionNote($previousStatus, $newStatus),
                    $report->decision,
                    $report->outcome
                );
            }

            return $this->findReport(
                $report->organization,
                $report->incident_id,
                $report->id
            );
        });
    }

    /**
     * @param  array<string, mixed>  $data
     */
    public function submitAppeal(
        Organization $organization,
        int $incidentId,
        int $reportId,
        User $actor,
        array $data,
        bool $isMemberSubmission = false
    ): IncidentReportAppeal {
        $report = $this->findReport($organization, $incidentId, $reportId);
        $incident = $report->incident;

        if ($isMemberSubmission && (int) $incident->reported_by !== (int) $actor->id) {
            throw new OutcomeStateException('You can only submit appeals for your own reports.');
        }

        if (! in_array($report->status, [
            IncidentExternalReport::STATUS_DECISION,
            IncidentExternalReport::STATUS_OUTCOME,
        ], true)) {
            throw new OutcomeStateException('Appeals can only be submitted after a decision or outcome has been recorded.');
        }

        return DB::transaction(function () use ($report, $actor, $data) {
            return IncidentReportAppeal::query()->create([
                'incident_external_report_id' => $report->id,
                'submitted_at' => $data['submitted_at'] ?? now(),
                'submitted_by' => $actor->id,
                'reason' => $data['reason'],
                'additional_evidence' => $data['additional_evidence'] ?? null,
                'reference' => $data['reference'] ?? null,
                'notes' => $data['notes'] ?? null,
                'status' => IncidentReportAppeal::STATUS_SUBMITTED,
            ]);
        });
    }

    /**
     * @param  array<string, mixed>  $data
     */
    public function updateAppeal(
        Organization $organization,
        int $incidentId,
        int $reportId,
        int $appealId,
        User $actor,
        array $data
    ): IncidentReportAppeal {
        $report = $this->findReport($organization, $incidentId, $reportId);

        $appeal = $report->appeals()->findOrFail($appealId);

        if (array_key_exists('status', $data)) {
            $appeal->status = $data['status'];
        }

        if (array_key_exists('response', $data)) {
            $appeal->response = $data['response'];
            $appeal->responded_at = now();
            $appeal->responded_by = $actor->id;
        }

        $appeal->save();

        return $appeal->fresh(['submitter', 'responder']);
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function serializeForPackage(Incident $incident): array
    {
        $reports = $this->loadReports($incident);

        return $reports->map(fn (IncidentExternalReport $report) => $this->serializeReport($report, true))->all();
    }

    /**
     * @return array<string, mixed>
     */
    public function serializeReport(IncidentExternalReport $report, bool $includeInternal = true): array
    {
        $data = [
            'id' => $report->id,
            'platform' => $report->platform,
            'reporting_channel' => $report->reporting_channel,
            'reported_at' => optional($report->reported_at)?->toIso8601String(),
            'status' => $report->status,
            'external_reference' => $report->external_reference,
            'decision' => $report->decision,
            'decision_note' => $includeInternal ? $report->decision_note : null,
            'outcome' => $report->outcome,
            'outcome_source' => $report->outcome_source,
            'outcome_summary' => $includeInternal ? $report->outcome_summary : $report->reporter_visible_summary,
            'verification_status' => $report->verification_status,
            'reporter_visible_summary' => $report->reporter_visible_summary,
            'appeals' => $report->appeals->map(fn (IncidentReportAppeal $appeal) => [
                'id' => $appeal->id,
                'submitted_at' => optional($appeal->submitted_at)?->toIso8601String(),
                'status' => $appeal->status,
                'reason' => $appeal->reason,
                'response' => $appeal->response,
                'responded_at' => optional($appeal->responded_at)?->toIso8601String(),
            ])->all(),
            'history' => $report->statusHistory->map(fn (IncidentExternalReportStatusHistory $entry) => [
                'previous_status' => $entry->previous_status,
                'new_status' => $entry->new_status,
                'decision' => $entry->decision,
                'outcome' => $entry->outcome,
                'changed_by' => $includeInternal ? $entry->changedByUser?->name : null,
                'changed_at' => optional($entry->changed_at)?->toIso8601String(),
                'note' => $includeInternal ? $entry->note : null,
            ])->all(),
        ];

        if ($includeInternal) {
            $data['internal_notes'] = $report->internal_notes;
        }

        return $data;
    }

    /**
     * @return Collection<int, Incident>
     */
    public function listMemberReports(Organization $organization, User $member): Collection
    {
        return $organization->incidents()
            ->where('reported_by', $member->id)
            ->with(['externalReports' => fn ($q) => $q->with(['appeals', 'statusHistory'])])
            ->orderByDesc('id')
            ->get();
    }

    public function memberReportDetail(Organization $organization, User $member, int $incidentId): Incident
    {
        return $organization->incidents()
            ->where('reported_by', $member->id)
            ->with([
                'externalReports' => fn ($q) => $q->with(['appeals', 'statusHistory.changedByUser']),
            ])
            ->findOrFail($incidentId);
    }

    private function findIncident(Organization $organization, int $incidentId): Incident
    {
        return $organization->incidents()->findOrFail($incidentId);
    }

    /**
     * @return Collection<int, IncidentExternalReport>
     */
    private function loadReports(Incident $incident): Collection
    {
        return $incident->externalReports()
            ->with(['statusHistory.changedByUser', 'appeals.submitter', 'appeals.responder', 'creator', 'updater'])
            ->orderBy('reported_at')
            ->orderBy('id')
            ->get();
    }

    private function appendHistory(
        IncidentExternalReport $report,
        ?string $previousStatus,
        string $newStatus,
        User $actor,
        ?string $note,
        ?string $decision,
        ?string $outcome
    ): void {
        IncidentExternalReportStatusHistory::query()->create([
            'incident_external_report_id' => $report->id,
            'previous_status' => $previousStatus,
            'new_status' => $newStatus,
            'decision' => $decision,
            'outcome' => $outcome,
            'changed_by' => $actor->id,
            'note' => $note,
            'changed_at' => now(),
        ]);
    }

    private function defaultTransitionNote(string $from, string $to): string
    {
        return match ($to) {
            IncidentExternalReport::STATUS_UNDER_REVIEW => 'Status updated to under review.',
            IncidentExternalReport::STATUS_DECISION => 'Decision recorded.',
            IncidentExternalReport::STATUS_OUTCOME => 'Outcome recorded.',
            default => sprintf('Status changed from %s to %s.', $from, $to),
        };
    }
}
