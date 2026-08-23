<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use App\Models\IncidentExternalReport;
use App\Models\IncidentExternalReportStatusHistory;
use App\Models\IncidentReportAppeal;
use App\Models\Role;
use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentOutcomeTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_outcome_permissions_exist_and_are_granted_correctly(): void
    {
        $this->assertContains(Permissions::INCIDENTS_OUTCOMES_VIEW, Permissions::slugs());
        $this->assertContains(Permissions::INCIDENTS_OUTCOMES_MANAGE, Permissions::slugs());
        $this->assertContains(Permissions::INCIDENTS_OUTCOMES_APPEAL, Permissions::slugs());

        $reviewer = Role::communitySafetyReviewer();
        foreach ([
            Permissions::INCIDENTS_OUTCOMES_VIEW,
            Permissions::INCIDENTS_OUTCOMES_MANAGE,
            Permissions::INCIDENTS_OUTCOMES_APPEAL,
        ] as $permission) {
            $this->assertTrue(
                $reviewer->permissions->contains(fn ($model) => $model->slug === $permission),
                $permission
            );
        }

        $member = Role::member();
        $this->assertTrue(
            $member->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_OUTCOMES_VIEW)
        );
        $this->assertTrue(
            $member->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_OUTCOMES_APPEAL)
        );
        $this->assertFalse(
            $member->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_OUTCOMES_MANAGE)
        );
    }

    public function test_reviewer_can_record_external_report(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $response = $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports'), [
                'platform' => Incident::PLATFORM_REDDIT,
                'reporting_channel' => 'In-app report',
                'external_reference' => 'RDT-1234',
                'reported_at' => now()->subDay()->toIso8601String(),
                'note' => 'Submitted evidence package to Reddit.',
            ])
            ->assertCreated();

        $data = $response->json('data');
        $this->assertSame('reported', $data['status']);
        $this->assertSame('reddit', $data['platform']);
        $this->assertSame('unverified', $data['verification_status']);

        $this->assertDatabaseHas('incident_external_reports', [
            'incident_id' => $incident->id,
            'organization_id' => $organization->id,
            'status' => IncidentExternalReport::STATUS_REPORTED,
        ]);

        $this->assertDatabaseHas('incident_external_report_status_history', [
            'new_status' => IncidentExternalReport::STATUS_REPORTED,
        ]);
    }

    public function test_admin_can_record_external_report(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports'), [
                'platform' => Incident::PLATFORM_X,
                'reporting_channel' => 'In-app report',
                'reported_at' => now()->toIso8601String(),
            ])
            ->assertCreated();
    }

    public function test_member_cannot_create_external_report(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports'), [
                'platform' => Incident::PLATFORM_X,
                'reporting_channel' => 'In-app report',
                'reported_at' => now()->toIso8601String(),
            ])
            ->assertForbidden();
    }

    public function test_status_transitions_work_and_invalid_transitions_are_blocked(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
                'note' => 'Platform acknowledged receipt.',
            ])
            ->assertOk()
            ->assertJsonPath('data.status', IncidentExternalReport::STATUS_UNDER_REVIEW);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_DECISION,
                'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                'decision_note' => 'Platform confirmed action.',
            ])
            ->assertOk()
            ->assertJsonPath('data.decision', IncidentExternalReport::DECISION_ACTION_TAKEN);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'outcome' => IncidentExternalReport::OUTCOME_CONTENT_REMOVED,
                'outcome_source' => IncidentExternalReport::SOURCE_PLATFORM_RESPONSE,
                'outcome_summary' => 'Content removed per platform response.',
            ])
            ->assertOk()
            ->assertJsonPath('data.outcome', IncidentExternalReport::OUTCOME_CONTENT_REMOVED);

        // Invalid: reported → outcome directly on fresh report
        $fresh = $this->createExternalReport($organization, $incident, $reviewer);
        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$fresh->id), [
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'outcome' => IncidentExternalReport::OUTCOME_CONTENT_REMOVED,
            ])
            ->assertStatus(422);
    }

    public function test_reported_to_decision_skip_is_allowed(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_DECISION,
                'decision' => IncidentExternalReport::DECISION_NO_ACTION,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', IncidentExternalReport::STATUS_DECISION);
    }

    public function test_decision_required_when_status_is_decision(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_DECISION,
            ])
            ->assertStatus(422);
    }

    public function test_outcome_required_when_status_is_outcome(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_DECISION,
                'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
            ])
            ->assertOk();

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_OUTCOME,
            ])
            ->assertStatus(422);
    }

    public function test_multiple_external_reports_per_incident(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->createExternalReport($organization, $incident, $reviewer, ['platform' => Incident::PLATFORM_REDDIT]);
        $this->createExternalReport($organization, $incident, $reviewer, ['platform' => Incident::PLATFORM_X]);

        $response = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports'))
            ->assertOk();

        $this->assertCount(2, $response->json('data'));
    }

    public function test_appeal_can_be_created_and_original_outcome_preserved(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);
        $report = $this->createExternalReport($organization, $incident, $reviewer, [
            'status' => IncidentExternalReport::STATUS_OUTCOME,
            'decision' => IncidentExternalReport::DECISION_NO_ACTION,
            'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, '/community-shield/my-reports/'.$incident->id.'/external-reports/'.$report->id.'/appeals'), [
                'reason' => 'Additional evidence was not considered.',
            ])
            ->assertCreated()
            ->assertJsonPath('data.status', IncidentReportAppeal::STATUS_SUBMITTED);

        $report->refresh();
        $this->assertSame(IncidentExternalReport::OUTCOME_NO_ACTION, $report->outcome);
        $this->assertCount(1, $report->appeals);
    }

    public function test_member_cannot_fabricate_accepted_appeal_via_update(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);
        $report = $this->createExternalReport($organization, $incident, $reviewer, [
            'status' => IncidentExternalReport::STATUS_OUTCOME,
            'decision' => IncidentExternalReport::DECISION_NO_ACTION,
            'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
        ]);
        $appeal = IncidentReportAppeal::query()->create([
            'incident_external_report_id' => $report->id,
            'submitted_at' => now(),
            'submitted_by' => $member->id,
            'reason' => 'Appeal reason',
            'status' => IncidentReportAppeal::STATUS_SUBMITTED,
        ]);

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id.'/appeals/'.$appeal->id), [
                'status' => IncidentReportAppeal::STATUS_ACCEPTED,
                'response' => 'Accepted',
            ])
            ->assertForbidden();
    }

    public function test_member_sees_own_outcome_not_internal_notes(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $member = $this->createMember($organization, $this->memberRole);
        $otherMember = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);
        $this->createExternalReport($organization, $incident, $reviewer, [
            'internal_notes' => 'Private reviewer note',
            'reporter_visible_summary' => 'Your report is being reviewed.',
        ]);

        $response = $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, '/community-shield/my-reports/'.$incident->id))
            ->assertOk();

        $report = $response->json('data.external_reports.0');
        $this->assertNull($report['internal_notes']);
        $this->assertSame('Your report is being reviewed.', $report['reporter_visible_summary']);

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, '/community-shield/my-reports/'.$incident->id))
            ->assertNotFound();
    }

    public function test_member_cannot_modify_outcome_status(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
        ]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$report->id), [
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'outcome' => IncidentExternalReport::OUTCOME_CONTENT_REMOVED,
            ])
            ->assertForbidden();
    }

    public function test_tenant_isolation_blocks_cross_org_access(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $alphaReviewer = $this->createMember($alpha, $this->reviewerRole);
        $betaReviewer = $this->createMember($beta, $this->reviewerRole);

        $alphaIncident = Incident::factory()->create(['organization_id' => $alpha->id]);
        $betaIncident = Incident::factory()->create(['organization_id' => $beta->id]);
        $betaReport = $this->createExternalReport($beta, $betaIncident, $betaReviewer);

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$betaIncident->id.'/external-reports'))
            ->assertNotFound();

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$alphaIncident->id.'/external-reports/'.$betaReport->id))
            ->assertNotFound();
    }

    public function test_history_is_immutable_append_only(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $createResponse = $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports'), [
                'platform' => Incident::PLATFORM_REDDIT,
                'reporting_channel' => 'In-app report',
                'reported_at' => now()->toIso8601String(),
            ])
            ->assertCreated();

        $reportId = $createResponse->json('data.id');

        $this->actingAsApi($reviewer)
            ->patchJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$reportId), [
                'status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
            ])
            ->assertOk();

        $historyCount = IncidentExternalReportStatusHistory::query()
            ->where('incident_external_report_id', $reportId)
            ->count();

        $this->assertSame(2, $historyCount);

        $response = $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/external-reports/'.$reportId.'/history'))
            ->assertOk();

        $this->assertCount(2, $response->json('data'));
    }

    public function test_verification_defaults_to_unverified(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $report = $this->createExternalReport($organization, $incident, $reviewer);

        $this->assertSame(IncidentExternalReport::VERIFICATION_UNVERIFIED, $report->verification_status);
    }

    /**
     * @param  array<string, mixed>  $overrides
     */
    private function createExternalReport(
        $organization,
        Incident $incident,
        $actor,
        array $overrides = []
    ): IncidentExternalReport {
        return IncidentExternalReport::query()->create(array_merge([
            'incident_id' => $incident->id,
            'organization_id' => $organization->id,
            'platform' => Incident::PLATFORM_REDDIT,
            'reporting_channel' => 'In-app report',
            'reported_at' => now()->subDay(),
            'status' => IncidentExternalReport::STATUS_REPORTED,
            'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
            'created_by' => $actor->id,
            'updated_by' => $actor->id,
        ], $overrides));
    }
}
