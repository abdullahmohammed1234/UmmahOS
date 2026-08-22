<?php

namespace Tests\Feature\Auth;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AuthenticationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_user_can_login_with_valid_credentials(): void
    {
        $user = User::factory()->create([
            'email' => 'user@example.com',
            'password' => 'password',
        ]);

        $response = $this->postJson(route('api.auth.login'), [
            'email' => 'user@example.com',
            'password' => 'password',
        ]);

        $response->assertOk()
            ->assertJsonPath('user.id', $user->id)
            ->assertJsonPath('user.email', 'user@example.com')
            ->assertJsonStructure(['message', 'user', 'token']);

        $this->assertNotEmpty($response->json('token'));
    }

    public function test_user_cannot_login_with_invalid_password(): void
    {
        User::factory()->create([
            'email' => 'user@example.com',
            'password' => 'password',
        ]);

        $this->postJson(route('api.auth.login'), [
            'email' => 'user@example.com',
            'password' => 'wrong-password',
        ])->assertStatus(422)
            ->assertJsonValidationErrors(['email']);
    }

    public function test_authenticated_user_can_view_me(): void
    {
        $user = User::factory()->create();

        $this->actingAsApi($user)
            ->getJson(route('api.auth.me'))
            ->assertOk()
            ->assertJsonPath('user.id', $user->id)
            ->assertJsonPath('user.email', $user->email);
    }

    public function test_unauthenticated_user_cannot_view_me(): void
    {
        $this->getJson(route('api.auth.me'))
            ->assertUnauthorized();
    }

    public function test_authenticated_user_can_logout(): void
    {
        $user = User::factory()->create();

        $this->actingAsApi($user)
            ->postJson(route('api.auth.logout'))
            ->assertOk()
            ->assertJsonPath('message', 'Logout successful.');

        $this->assertSame(0, $user->tokens()->count());
    }

    public function test_me_includes_memberships_for_multiple_organizations(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $user = $this->createMember($alpha, $this->memberRole);
        $this->joinOrganization($user, $beta, $this->adminRole);

        $response = $this->actingAsApi($user)
            ->getJson(route('api.auth.me'))
            ->assertOk();

        $this->assertCount(2, $response->json('user.memberships'));
    }
}
