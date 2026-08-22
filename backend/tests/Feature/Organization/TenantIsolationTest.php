<?php

namespace Tests\Feature\Organization;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class TenantIsolationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_organization_a_cannot_read_organization_b(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaAdmin)
            ->getJson(route('api.organizations.show', $beta))
            ->assertForbidden()
            ->assertJsonPath('message', 'You are not a member of this organization.');
    }

    public function test_organization_a_cannot_update_organization_b(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaAdmin)
            ->patchJson(route('api.organizations.update', $beta), [
                'name' => 'Taken Over',
            ])
            ->assertForbidden();

        $this->assertSame('Demo MSA Beta', $beta->fresh()->name);
    }

    public function test_organization_a_cannot_delete_organization_b(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);

        $this->actingAsApi($alphaAdmin)
            ->deleteJson(route('api.organizations.destroy', $beta))
            ->assertForbidden();

        $this->assertDatabaseHas('organizations', ['id' => $beta->id]);
    }

    public function test_organization_a_cannot_read_organization_b_members(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $this->createMember($beta, $this->adminRole);

        $this->actingAsApi($alphaAdmin)
            ->getJson(route('api.organizations.members.index', $beta))
            ->assertForbidden();
    }

    public function test_non_member_cannot_access_an_organization(): void
    {
        $organization = $this->createOrganization();
        $outsider = $this->createMember($this->createOrganization(), $this->adminRole);

        $this->actingAsApi($outsider)
            ->getJson(route('api.organizations.show', $organization))
            ->assertForbidden();

        $this->actingAsApi($outsider)
            ->getJson(route('api.organizations.context', $organization))
            ->assertForbidden();
    }

    public function test_invalid_organization_context_is_rejected(): void
    {
        $user = $this->createMember($this->createOrganization(), $this->adminRole);

        $this->actingAsApi($user)
            ->getJson('/api/v1/organizations/999999')
            ->assertNotFound();

        $this->actingAsApi($user)
            ->getJson('/api/v1/organizations/not-a-real-organization')
            ->assertNotFound();
    }

    public function test_unauthenticated_requests_cannot_access_organization_routes(): void
    {
        $organization = $this->createOrganization();

        $this->getJson(route('api.organizations.show', $organization))
            ->assertUnauthorized();
    }
}
