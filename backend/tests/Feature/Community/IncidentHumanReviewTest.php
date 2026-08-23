<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentContextRequest;
use App\Models\IncidentReviewAction;
use App\Models\Role;
use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentHumanReviewTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_community_safety_reviewer_role_and_permissions_exist(): void
    {
        $role = Role::communitySafetyReviewer();

        $this->assertSame('Community Safety Reviewer', $role->name);
        $this->assertSame(Role::COMMUNITY_SAFETY_REVIEWER, $role->slug);

        foreach (Permissions::communitySafetyReviewerSlugs() as $permission) {
            $this->assertTrue(
                $role->permissions->contains(fn ($model) => $model->slug === $permission),
                $permission
            );
        }

        $this->assertFalse(
            $role->permissions->contains(fn ($model) => $model->slug === Permissions::INCIDENTS_MANAGE)
        );
        $this->assertFalse(
            $role->permissions->contains(fn ($model) => $model->slug === Permissions::ORGANIZATION_MANAGE)
        );
    }

    public function test_reviewer_permissions_are_organization_scoped(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->reviewerRole);
        $this->joinOrganization($user, $beta, $this->memberRole);

        $this->assertTrue($user->hasPermissionIn($alpha, Permissions::INCIDENTS_REVIEW));
        $this->assertTrue($user->hasPermissionIn($alpha, Permissions::INCIDENTS_CLASSIFY));
        $this->assertFalse($user->hasPermissionIn($beta, Permissions::INCIDENTS_REVIEW));
        $this->assertFalse($user->hasPermissionIn($beta, Permissions::INCIDENTS_CLASSIFY));
        $this->assertTrue($user->hasPermissionIn($beta, Permissions::INCIDENTS_VIEW));
    }

    public function test_alpha_reviewer_can_list_alpha_queue_but_not_beta(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $reviewer = $this->createMember($alpha, $this->reviewerRole);
        $this->joinOrganization($reviewer, $beta, $this->memberRole);

        $alphaIncident = Incident::factory()->create(['organization_id' => $alpha->id]);
        $betaIncident = Incident::factory()->create(['organization_id' => $beta->id]);

        $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/review-queue'))
            ->assertOk()
            ->assertJsonFragment(['id' => $alphaIncident->id])
            ->assertJsonMissing(['id' => $betaIncident->id]);

        $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($beta, '/community-shield/review-queue'))
            ->assertForbidden();
    }

    public function test_member_cannot_access_review_queue_or_notes(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'review_notes' => 'Internal reviewer note',
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, '/community-shield/review-queue'))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review'))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/start'))
            ->assertForbidden();
    }

    public function test_admin_retains_review_access(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, '/community-shield/review-queue'))
            ->assertOk()
            ->assertJsonFragment(['id' => $incident->id]);
    }

    public function test_reviewer_can_start_confirm_uncertain_close_escalate_and_request_context(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);

        $confirmIncident = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$confirmIncident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk()
            ->assertJsonPath('data.incident.status', Incident::STATUS_REVIEWING)
            ->assertJsonPath('data.incident.current_reviewer.id', $reviewer->id);

        $confirmIncident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$confirmIncident->id.'/review/confirm'), [
                'notes' => 'Context and related copies support the classification.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => $confirmIncident->review_lock_version,
            ])
            ->assertOk()
            ->assertJsonPath('data.incident.status', Incident::STATUS_RESOLVED)
            ->assertJsonPath('data.incident.review_outcome', Incident::OUTCOME_CONFIRMED)
            ->assertJsonPath('data.incident.safety_classification', Incident::CLASSIFICATION_HATE);

        $uncertainIncident = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$uncertainIncident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();
        $uncertainIncident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$uncertainIncident->id.'/review/uncertain'), [
                'notes' => 'Evidence is incomplete.',
                'review_lock_version' => $uncertainIncident->review_lock_version,
            ])
            ->assertOk()
            ->assertJsonPath('data.incident.status', Incident::STATUS_REVIEWING)
            ->assertJsonPath('data.incident.review_outcome', Incident::OUTCOME_UNCERTAIN);

        $closeIncident = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$closeIncident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();
        $closeIncident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$closeIncident->id.'/review/close'), [
                'notes' => 'No further review action required.',
                'review_lock_version' => $closeIncident->review_lock_version,
            ])
            ->assertOk()
            ->assertJsonPath('data.incident.status', Incident::STATUS_RESOLVED)
            ->assertJsonPath('data.incident.review_outcome', Incident::OUTCOME_CLOSED);

        $escalateIncident = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$escalateIncident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();
        $escalateIncident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$escalateIncident->id.'/review/escalate'), [
                'reason' => 'Requires specialized human review.',
                'review_lock_version' => $escalateIncident->review_lock_version,
            ])
            ->assertOk()
            ->assertJsonPath('data.incident.escalated', true)
            ->assertJsonPath('data.incident.status', Incident::STATUS_REVIEWING);

        $contextIncident = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$contextIncident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();
        $contextIncident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$contextIncident->id.'/context-requests'), [
                'reason' => 'Need the two replies immediately preceding the reported comment.',
                'review_lock_version' => $contextIncident->review_lock_version,
            ])
            ->assertCreated()
            ->assertJsonPath('data.status', IncidentContextRequest::STATUS_OPEN)
            ->assertJsonPath('data.reason', 'Need the two replies immediately preceding the reported comment.');
    }

    public function test_invalid_transitions_and_required_fields_are_rejected(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => 'Too early',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => 1,
            ])
            ->assertStatus(422);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $incident->refresh();

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => '',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertStatus(422);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/escalate'), [
                'reason' => '',
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertStatus(422);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => 'Confirmed with rationale.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertOk();

        $incident->refresh();

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => 'Again',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertStatus(422);
    }

    public function test_cross_organization_review_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaReviewer = $this->createMember($alpha, $this->reviewerRole);
        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'review_notes' => 'Beta-only notes',
        ]);

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($alpha, '/community-shield/reports/'.$betaIncident->id.'/review'))
            ->assertNotFound();

        $this->actingAsApi($alphaReviewer)
            ->postJson($this->orgUrl($alpha, '/community-shield/reports/'.$betaIncident->id.'/review/start'))
            ->assertNotFound();

        $this->actingAsApi($alphaReviewer)
            ->getJson($this->orgUrl($beta, '/community-shield/reports/'.$betaIncident->id.'/review'))
            ->assertForbidden();
    }

    public function test_review_actions_are_auditable_and_not_overwritten(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $incident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/context-requests'), [
                'reason' => 'Need surrounding replies.',
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertCreated();

        $incident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => 'Confirmed after context request.',
                'safety_classification' => Incident::CLASSIFICATION_HARASSMENT,
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertOk();

        $actions = IncidentReviewAction::query()
            ->where('incident_id', $incident->id)
            ->orderBy('id')
            ->get();

        $this->assertCount(3, $actions);
        $this->assertSame(IncidentReviewAction::ACTION_STARTED, $actions[0]->action);
        $this->assertSame($reviewer->id, $actions[0]->actor_id);
        $this->assertNotNull($actions[0]->created_at);
        $this->assertSame(IncidentReviewAction::ACTION_CONTEXT_REQUESTED, $actions[1]->action);
        $this->assertSame(IncidentReviewAction::ACTION_CONFIRMED, $actions[2]->action);

        $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review'))
            ->assertOk()
            ->assertJsonPath('data.human_review.history.0.action', IncidentReviewAction::ACTION_STARTED)
            ->assertJsonPath('data.human_review.history.2.action', IncidentReviewAction::ACTION_CONFIRMED);
    }

    public function test_human_review_does_not_rewrite_ai_analysis(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);
        $analysis = IncidentAiAnalysis::factory()->create([
            'incident_id' => $incident->id,
            'requested_by' => $reviewer->id,
            'analysis' => [
                'signals' => [],
                'classification' => ['label' => 'potential_hate', 'confidence' => 'moderate'],
                'uncertainty' => ['level' => 'high', 'explanation' => 'Ambiguous'],
                'alternative_interpretation' => 'Could be satire',
                'recommended_action' => ['type' => 'human_review', 'reason' => 'Needs human'],
            ],
        ]);

        $original = $analysis->analysis;

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $incident->refresh();
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/confirm'), [
                'notes' => 'Human confirms a concern independently.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => $incident->review_lock_version,
            ])
            ->assertOk();

        $analysis->refresh();
        $incident->refresh();

        $this->assertSame($original, $analysis->analysis);
        $this->assertSame('potential_hate', $analysis->analysis['classification']['label']);
        $this->assertSame(Incident::CLASSIFICATION_HATE, $incident->safety_classification);
        $this->assertSame(Incident::OUTCOME_CONFIRMED, $incident->review_outcome);
        $this->assertSame(1, IncidentAiAnalysis::query()->where('incident_id', $incident->id)->count());
    }

    public function test_stale_review_updates_are_rejected(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $other = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create(['organization_id' => $organization->id]);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $incident->refresh();
        $staleVersion = $incident->review_lock_version;

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/uncertain'), [
                'notes' => 'First update wins.',
                'review_lock_version' => $staleVersion,
            ])
            ->assertOk();

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$incident->id.'/review/close'), [
                'notes' => 'Stale close',
                'review_lock_version' => $staleVersion,
            ])
            ->assertStatus(409);

        $second = Incident::factory()->create(['organization_id' => $organization->id]);
        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$second->id.'/review/start'), [
                'review_lock_version' => 1,
            ])
            ->assertOk();

        $this->actingAsApi($other)
            ->postJson($this->orgUrl($organization, '/community-shield/reports/'.$second->id.'/review/confirm'), [
                'notes' => 'Should not overwrite',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'review_lock_version' => 2,
            ])
            ->assertStatus(409);
    }

    public function test_queue_filters_and_ai_assisted_triage_labels(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'platform' => Incident::PLATFORM_X,
            'status' => Incident::STATUS_OPEN,
            'escalated' => false,
        ]);

        IncidentAiAnalysis::factory()->create([
            'incident_id' => $incident->id,
            'requested_by' => $reviewer->id,
            'analysis' => [
                'signals' => [],
                'classification' => ['label' => 'potential_hate', 'confidence' => 'moderate'],
                'uncertainty' => ['level' => 'high', 'explanation' => 'Ambiguous'],
                'alternative_interpretation' => null,
                'recommended_action' => ['type' => 'human_review', 'reason' => 'Needs human'],
            ],
        ]);

        $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield/review-queue?platform=x&uncertainty=high&confidence=moderate'))
            ->assertOk()
            ->assertJsonFragment(['id' => $incident->id])
            ->assertJsonPath('data.0.ai_assisted_triage.classification', 'potential_hate')
            ->assertJsonPath('data.0.ai_assisted_triage.confidence', 'moderate')
            ->assertJsonPath('data.0.ai_assisted_triage.uncertainty', 'high')
            ->assertJsonMissing(['AI Verdict']);
    }

    public function test_overview_can_review_for_reviewer_role(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($reviewer)
            ->getJson($this->orgUrl($organization, '/community-shield'))
            ->assertOk()
            ->assertJsonPath('data.can_review', true);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, '/community-shield'))
            ->assertOk()
            ->assertJsonPath('data.can_review', false);
    }
}
