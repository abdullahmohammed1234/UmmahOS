<?php

namespace Tests\Feature\Community;

use App\Models\Course;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CourseTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_member_can_view_published_courses(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'title' => 'Alpha Qur\'an foundations',
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'courses'))
            ->assertOk()
            ->assertJsonPath('data.0.id', $course->id);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'courses/'.$course->id))
            ->assertOk()
            ->assertJsonPath('data.status', Course::STATUS_PUBLISHED);
    }

    public function test_draft_courses_are_not_visible_to_members(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $admin = $this->createMember($organization, $this->adminRole);
        $draft = Course::factory()->draft()->create([
            'organization_id' => $organization->id,
            'title' => 'Alpha leadership draft',
            'created_by' => $admin->id,
        ]);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'courses'))
            ->assertOk()
            ->assertJsonCount(0, 'data');

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'courses/'.$draft->id))
            ->assertNotFound();

        $this->actingAsApi($admin)
            ->getJson($this->orgUrl($organization, 'courses/'.$draft->id))
            ->assertOk()
            ->assertJsonPath('data.status', Course::STATUS_DRAFT);
    }

    public function test_cross_organization_course_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Demo MSA Alpha']);
        $beta = $this->createOrganization(['name' => 'Demo MSA Beta']);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);

        $betaCourse = Course::factory()->published()->create([
            'organization_id' => $beta->id,
            'title' => 'Beta seerah circle',
            'created_by' => $betaAdmin->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($beta, 'courses'))
            ->assertForbidden();

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'courses/'.$betaCourse->id))
            ->assertNotFound();
    }

    public function test_admin_can_manage_courses_including_publish_and_unpublish(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);

        $created = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'courses'), [
                'title' => 'Fiqh basics',
                'description' => 'Intro',
                'status' => Course::STATUS_DRAFT,
            ])
            ->assertCreated()
            ->assertJsonPath('data.status', Course::STATUS_DRAFT);

        $id = $created->json('data.id');

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'courses/'.$id), [
                'status' => Course::STATUS_PUBLISHED,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', Course::STATUS_PUBLISHED);

        $this->actingAsApi($admin)
            ->patchJson($this->orgUrl($organization, 'courses/'.$id), [
                'status' => Course::STATUS_DRAFT,
            ])
            ->assertOk()
            ->assertJsonPath('data.status', Course::STATUS_DRAFT);

        $this->actingAsApi($admin)
            ->deleteJson($this->orgUrl($organization, 'courses/'.$id))
            ->assertOk();

        $this->assertDatabaseMissing('courses', ['id' => $id]);
    }

    public function test_member_cannot_manage_courses(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'created_by' => $member->id,
        ]);

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'courses'), [
                'title' => 'Unauthorized',
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->patchJson($this->orgUrl($organization, 'courses/'.$course->id), [
                'status' => Course::STATUS_DRAFT,
            ])
            ->assertForbidden();

        $this->actingAsApi($member)
            ->deleteJson($this->orgUrl($organization, 'courses/'.$course->id))
            ->assertForbidden();
    }
}
