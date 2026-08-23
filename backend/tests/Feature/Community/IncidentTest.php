<?php

namespace Tests\Feature\Community;

use App\Models\Incident;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IncidentTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_submit_incident(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'incidents'), [
                'category' => Incident::CATEGORY_SAFETY,
                'description' => 'Someone was followed after maghrib.',
            ])
            ->assertCreated()
            ->assertJsonPath('data.category', Incident::CATEGORY_SAFETY)
            ->assertJsonPath('data.status', Incident::STATUS_OPEN)
            ->assertJsonPath('data.reported_by.id', $member->id)
            ->assertJsonPath('message', 'Your report was received. An organization administrator can review it.');
    }

    public function test_member_cannot_view_another_users_incident(): void
    {
        $organization = $this->createOrganization();
        $reporter = $this->createMember($organization, $this->memberRole);
        $otherMember = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reporter->id,
        ]);

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($otherMember)
            ->getJson($this->orgUrl($organization, 'incidents/'.$incident->id))
            ->assertForbidden();

        $this->actingAsApi($reporter)
            ->getJson($this->orgUrl($organization, 'incidents/'.$incident->id))
            ->assertForbidden();
    }

    public function test_member_cannot_view_another_organizations_incident(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'incidents/'.$betaIncident->id))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertForbidden();
    }

    public function test_admin_can_view_organization_incidents_and_update_status(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'status' => Incident::STATUS_OPEN,
        ]);

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'incidents'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $incident->id);

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'incidents/'.$incident->id), [
                'status' => Incident::STATUS_REVIEWING,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', Incident::STATUS_REVIEWING);
    }

    public function test_cross_organization_admin_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $betaIncident = Incident::factory()->create([
            'organization_id' => $beta->id,
            'reported_by' => $betaMember->id,
        ]);

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($beta, 'incidents'))
            ->assertForbidden();

        $this->actingAsApi($alphaAdmin)
            ->getJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id))
            ->assertNotFound();

        $this->actingAsApi($alphaAdmin)
            ->patchJson($this->orgUrl($alpha, 'incidents/'.$betaIncident->id), [
                'status' => Incident::STATUS_RESOLVED,
            ])
            ->assertNotFound();

        $this->assertSame(Incident::STATUS_OPEN, $betaIncident->fresh()->status);
    }
}
