<?php

namespace Tests\Feature\Organization;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class IdorTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_direct_id_access_to_another_organization_fails(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaUser = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaUser)
            ->getJson('/api/v1/organizations/'.$beta->id)
            ->assertForbidden();

        $this->actingAsApi($alphaUser)
            ->patchJson('/api/v1/organizations/'.$beta->id, [
                'name' => 'IDOR Update',
            ])
            ->assertForbidden();

        $this->actingAsApi($alphaUser)
            ->deleteJson('/api/v1/organizations/'.$beta->id)
            ->assertForbidden();
    }

    public function test_membership_id_from_another_organization_cannot_be_changed_via_current_org(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaMember = $this->createMember($beta, $this->memberRole);
        $betaMembership = $betaMember->membershipFor($beta);

        $this->actingAsApi($alphaAdmin)
            ->patchJson('/api/v1/organizations/'.$alpha->id.'/members/'.$betaMembership->id, [
                'role' => 'admin',
            ])
            ->assertNotFound();

        $this->assertTrue($betaMember->fresh()->hasRoleIn($beta, 'member'));
    }

    public function test_membership_id_from_another_organization_cannot_be_deleted_via_current_org(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaMember = $this->createMember($beta, $this->memberRole);
        $betaMembership = $betaMember->membershipFor($beta);

        $this->actingAsApi($alphaAdmin)
            ->deleteJson('/api/v1/organizations/'.$alpha->id.'/members/'.$betaMembership->id)
            ->assertNotFound();

        $this->assertTrue($betaMember->fresh()->belongsToOrganization($beta));
    }

    public function test_direct_id_access_to_another_organizations_incidents_fails(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaUser = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaUser)
            ->getJson('/api/v1/organizations/'.$beta->id.'/incidents/123')
            ->assertForbidden();

        $this->actingAsApi($alphaUser)
            ->patchJson('/api/v1/organizations/'.$beta->id.'/incidents/123', [
                'title' => 'IDOR',
            ])
            ->assertForbidden();

        $this->actingAsApi($alphaUser)
            ->deleteJson('/api/v1/organizations/'.$beta->id.'/incidents/123')
            ->assertForbidden();
    }

    public function test_incident_ids_are_not_readable_across_organizations_even_for_members_of_the_current_org(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $alphaUser = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaUser)
            ->getJson('/api/v1/organizations/'.$alpha->id.'/incidents/123')
            ->assertNotFound()
            ->assertJsonPath('organization_id', $alpha->id)
            ->assertJsonMissing(['data']);
    }

    public function test_future_module_namespaces_are_organization_isolated(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaUser = $this->createMember($alpha, $this->adminRole);

        foreach (['events', 'courses', 'content', 'reports'] as $module) {
            $this->actingAsApi($alphaUser)
                ->getJson("/api/v1/organizations/{$beta->id}/{$module}/1")
                ->assertForbidden();
        }
    }
}
