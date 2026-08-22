<?php

namespace Tests\Feature\Organization;

use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class OrganizationContextTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_load_organization_context(): void
    {
        $organization = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $user = $this->createMember($organization, $this->adminRole);

        $this->actingAsApi($user)
            ->getJson(route('api.organizations.context', $organization))
            ->assertOk()
            ->assertJsonPath('data.organization.id', $organization->id)
            ->assertJsonPath('data.role', 'admin')
            ->assertJsonFragment(['organization.manage']);
    }

    public function test_switching_organizations_changes_role_and_permissions(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);

        $alphaContext = $this->actingAsApi($user)
            ->getJson(route('api.organizations.context', $alpha))
            ->assertOk();

        $this->assertSame('member', $alphaContext->json('data.role'));
        $this->assertContains(Permissions::MEMBERS_VIEW, $alphaContext->json('data.permissions'));
        $this->assertNotContains(Permissions::MEMBERS_MANAGE, $alphaContext->json('data.permissions'));

        $betaContext = $this->actingAsApi($user)
            ->getJson(route('api.organizations.context', $beta))
            ->assertOk();

        $this->assertSame('admin', $betaContext->json('data.role'));
        $this->assertContains(Permissions::MEMBERS_MANAGE, $betaContext->json('data.permissions'));
        $this->assertSame($beta->id, $betaContext->json('data.organization.id'));
    }

    public function test_organization_context_can_be_resolved_by_slug(): void
    {
        $organization = $this->createOrganization([
            'name' => 'Demo MSA Alpha',
            'slug' => 'demo-msa-alpha',
        ]);
        $user = $this->createMember($organization, $this->memberRole);

        $this->actingAsApi($user)
            ->getJson('/api/v1/organizations/demo-msa-alpha/context')
            ->assertOk()
            ->assertJsonPath('data.organization.slug', 'demo-msa-alpha');
    }
}
