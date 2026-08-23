<?php

namespace Tests\Feature\Community;

use App\Models\AcademyLesson;
use App\Models\AcademyScenario;
use App\Models\AdaptLearningSession;
use App\Models\Course;
use App\Models\Incident;
use App\Models\LearningPattern;
use App\Models\LearningRecommendation;
use App\Services\Adapt\AdaptChallengeAdapter;
use App\Services\Adapt\FakeAdaptClient;
use App\Support\Permissions;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class Phase9EducationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_reviewer_can_create_pattern_from_confirmed_incident_only(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $confirmed = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reviewer->id,
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
        ]);
        $uncertain = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reviewer->id,
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_UNCERTAIN,
        ]);

        $payload = [
            'pattern_type' => 'contextual_hate',
            'title' => 'Contextual Religious Targeting',
            'summary' => 'Sanitized educational abstraction about context changing interpretation.',
            'learning_objective' => 'Identify when context changes interpretation.',
            'domain' => 'community-safety',
        ];

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$confirmed->id.'/learning-pattern'), $payload)
            ->assertCreated()
            ->assertJsonPath('data.title', 'Contextual Religious Targeting')
            ->assertJsonPath('data.status', LearningPattern::STATUS_DRAFT)
            ->assertJsonPath('data.source_incident_id', $confirmed->id)
            ->assertJsonMissingPath('data.description');

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$uncertain->id.'/learning-pattern'), $payload)
            ->assertStatus(422);
    }

    public function test_member_cannot_create_pattern_and_admin_can_approve(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $admin = $this->createMember($organization, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $member->id,
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
        ]);

        $payload = [
            'pattern_type' => 'coded_language',
            'title' => 'Recognizing coded language',
            'summary' => 'Sanitized summary.',
            'learning_objective' => 'Spot coded targeting.',
        ];

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/learning-pattern'), $payload)
            ->assertForbidden();

        $created = $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/learning-pattern'), $payload)
            ->assertCreated();

        $patternId = $created->json('data.id');

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'learning-patterns/'.$patternId.'/approve'))
            ->assertForbidden();

        $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'learning-patterns/'.$patternId.'/approve'))
            ->assertForbidden();

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'learning-patterns/'.$patternId.'/approve'))
            ->assertOk()
            ->assertJsonPath('data.status', LearningPattern::STATUS_APPROVED);
    }

    public function test_cross_org_pattern_access_is_blocked(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $betaAdmin = $this->createMember($beta, $this->adminRole);
        $incident = Incident::factory()->create([
            'organization_id' => $alpha->id,
            'reported_by' => $alphaAdmin->id,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'status' => Incident::STATUS_RESOLVED,
        ]);

        $pattern = LearningPattern::query()->create([
            'organization_id' => $alpha->id,
            'source_incident_id' => $incident->id,
            'pattern_type' => 'other',
            'title' => 'Alpha only',
            'summary' => 'Alpha summary',
            'learning_objective' => 'Alpha objective',
            'domain' => 'community-safety',
            'status' => LearningPattern::STATUS_APPROVED,
            'created_by' => $alphaAdmin->id,
            'approved_by' => $alphaAdmin->id,
            'approved_at' => now(),
        ]);

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($beta, 'learning-patterns/'.$pattern->id))
            ->assertNotFound();

        $this->actingAsApi($betaAdmin)
            ->getJson($this->orgUrl($alpha, 'learning-patterns/'.$pattern->id))
            ->assertForbidden();
    }

    public function test_only_approved_patterns_can_publish_recommendations_and_members_cannot_see_drafts_or_source(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $member = $this->createMember($organization, $this->memberRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $admin->id,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'status' => Incident::STATUS_RESOLVED,
        ]);

        $draftPattern = LearningPattern::query()->create([
            'organization_id' => $organization->id,
            'source_incident_id' => $incident->id,
            'pattern_type' => 'contextual_hate',
            'title' => 'Draft pattern',
            'summary' => 'Summary',
            'learning_objective' => 'Objective',
            'status' => LearningPattern::STATUS_DRAFT,
            'created_by' => $admin->id,
        ]);

        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'created_by' => $admin->id,
        ]);
        $lesson = AcademyLesson::query()->create([
            'organization_id' => $organization->id,
            'course_id' => $course->id,
            'title' => 'Understanding Context Before Responding',
            'learning_objective' => 'Recognize context.',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_PUBLISHED,
            'created_by' => $admin->id,
            'sections' => [['heading' => 'Why context matters', 'body' => 'Demo']],
        ]);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'learning-recommendations'), [
                'learning_pattern_id' => $draftPattern->id,
                'academy_lesson_id' => $lesson->id,
                'reason' => 'Should fail while draft.',
                'status' => LearningRecommendation::STATUS_PUBLISHED,
            ])
            ->assertStatus(422);

        $draftPattern->update([
            'status' => LearningPattern::STATUS_APPROVED,
            'approved_by' => $admin->id,
            'approved_at' => now(),
        ]);

        $published = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'learning-recommendations'), [
                'learning_pattern_id' => $draftPattern->id,
                'academy_lesson_id' => $lesson->id,
                'academy_course_id' => $course->id,
                'reason' => 'Teaches context preservation.',
                'status' => LearningRecommendation::STATUS_PUBLISHED,
            ])
            ->assertCreated();

        $draftRec = LearningRecommendation::query()->create([
            'organization_id' => $organization->id,
            'learning_pattern_id' => $draftPattern->id,
            'academy_lesson_id' => $lesson->id,
            'academy_course_id' => $course->id,
            'reason' => 'Draft only',
            'status' => LearningRecommendation::STATUS_DRAFT,
            'created_by' => $admin->id,
        ]);

        $memberList = $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'learning-recommendations'))
            ->assertOk()
            ->json('data');

        $this->assertCount(1, $memberList);
        $this->assertSame($published->json('data.id'), $memberList[0]['id']);
        $this->assertArrayNotHasKey('source_incident_id', $memberList[0]['pattern'] ?? []);

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'learning-recommendations/'.$draftRec->id))
            ->assertNotFound();

        $this->actingAsApi($member)
            ->getJson($this->orgUrl($organization, 'learning-patterns'))
            ->assertForbidden();
    }

    public function test_academy_community_safety_isolation_and_draft_hiding(): void
    {
        $alpha = $this->createOrganization(['name' => 'Alpha']);
        $beta = $this->createOrganization(['name' => 'Beta']);
        $alphaAdmin = $this->createMember($alpha, $this->adminRole);
        $alphaMember = $this->createMember($alpha, $this->memberRole);
        $betaMember = $this->createMember($beta, $this->memberRole);

        $alphaCourse = Course::factory()->published()->create([
            'organization_id' => $alpha->id,
            'created_by' => $alphaAdmin->id,
        ]);
        $published = AcademyLesson::query()->create([
            'organization_id' => $alpha->id,
            'course_id' => $alphaCourse->id,
            'title' => 'Alpha Context Lesson',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_PUBLISHED,
            'created_by' => $alphaAdmin->id,
        ]);
        $draft = AcademyLesson::query()->create([
            'organization_id' => $alpha->id,
            'course_id' => $alphaCourse->id,
            'title' => 'Alpha Draft Lesson',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_DRAFT,
            'created_by' => $alphaAdmin->id,
        ]);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'academy/community-safety'))
            ->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $published->id);

        $this->actingAsApi($alphaMember)
            ->getJson($this->orgUrl($alpha, 'academy/lessons/'.$draft->id))
            ->assertNotFound();

        $this->actingAsApi($betaMember)
            ->getJson($this->orgUrl($beta, 'academy/community-safety'))
            ->assertOk()
            ->assertJsonCount(0, 'data');

        $this->actingAsApi($betaMember)
            ->getJson($this->orgUrl($alpha, 'academy/lessons/'.$published->id))
            ->assertForbidden();
    }

    public function test_adapt_adapter_maps_scenario_and_fake_client_adapts(): void
    {
        $organization = $this->createOrganization();
        $member = $this->createMember($organization, $this->memberRole);
        $admin = $this->createMember($organization, $this->adminRole);

        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'created_by' => $admin->id,
        ]);
        $lesson = AcademyLesson::query()->create([
            'organization_id' => $organization->id,
            'course_id' => $course->id,
            'title' => 'Understanding Context Before Responding',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_PUBLISHED,
            'created_by' => $admin->id,
        ]);
        $scenario = AcademyScenario::query()->create([
            'organization_id' => $organization->id,
            'academy_lesson_id' => $lesson->id,
            'title' => 'Context preservation',
            'prompt' => 'Demo / educational scenario prompt',
            'options' => ['Preserve context', 'Reply immediately'],
            'expected_reasoning_signals' => ['context', 'preserve'],
            'misconception_tags' => ['CSAFE-M001'],
            'difficulty' => 2,
            'adapt_challenge_id' => 'CSAFE-CTX-001',
            'adapt_topic_id' => 'csafety-context',
            'adapt_concept_id' => 'csafety_context_preservation',
            'adapt_domain' => 'community-safety',
            'sort_order' => 1,
            'is_demo' => true,
        ]);

        $mapped = app(AdaptChallengeAdapter::class)->toAdaptChallengeRequest($scenario);
        $this->assertSame('csafety-context', $mapped['topic_id']);
        $this->assertSame('CSAFE-CTX-001', $mapped['initial_challenge']);
        $this->assertSame(['Preserve context', 'Reply immediately'], $mapped['choices']);

        $start = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'academy/lessons/'.$lesson->id.'/adapt-sessions'))
            ->assertCreated()
            ->assertJsonPath('data.available', true);

        $sessionId = $start->json('data.session.id');
        $challengeId = $start->json('data.adapt.challenge.challenge_id');

        $submit = $this->actingAsApi($member)
            ->postJson($this->orgUrl($organization, 'academy/adapt-sessions/'.$sessionId.'/responses'), [
                'answer' => 'Preserve context',
                'confidence' => 5,
                'reasoning' => 'I preserved surrounding context before concluding.',
                'challenge_id' => $challengeId,
            ])
            ->assertOk()
            ->assertJsonPath('data.available', true);

        $this->assertNotNull($submit->json('data.result.noticed'));
        $this->assertNotNull($submit->json('data.result.why_this_question'));
        $this->assertNotNull($submit->json('data.result.next_challenge'));
        $this->assertNotSame($challengeId, $submit->json('data.result.next_challenge.challenge_id'));
    }

    public function test_adapt_session_ownership_and_unavailable_mode(): void
    {
        $organization = $this->createOrganization();
        $memberA = $this->createMember($organization, $this->memberRole);
        $memberB = $this->createMember($organization, $this->memberRole);
        $admin = $this->createMember($organization, $this->adminRole);

        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'created_by' => $admin->id,
        ]);
        $lesson = AcademyLesson::query()->create([
            'organization_id' => $organization->id,
            'course_id' => $course->id,
            'title' => 'Lesson',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_PUBLISHED,
            'created_by' => $admin->id,
        ]);
        AcademyScenario::query()->create([
            'organization_id' => $organization->id,
            'academy_lesson_id' => $lesson->id,
            'title' => 'Scenario',
            'prompt' => 'Demo prompt',
            'adapt_challenge_id' => 'CSAFE-CTX-001',
            'adapt_topic_id' => 'csafety-context',
            'adapt_domain' => 'community-safety',
            'sort_order' => 1,
        ]);

        $start = $this->actingAsApi($memberA)
            ->postJson($this->orgUrl($organization, 'academy/lessons/'.$lesson->id.'/adapt-sessions'))
            ->assertCreated();
        $sessionId = $start->json('data.session.id');

        $this->actingAsApi($memberB)
            ->getJson($this->orgUrl($organization, 'academy/adapt-sessions/'.$sessionId))
            ->assertForbidden();

        /** @var FakeAdaptClient $fake */
        $fake = app(FakeAdaptClient::class);
        $fake->available = false;

        $unavailable = $this->actingAsApi($memberA)
            ->postJson($this->orgUrl($organization, 'academy/lessons/'.$lesson->id.'/adapt-sessions'))
            ->assertOk()
            ->assertJsonPath('data.available', false);

        $this->assertStringContainsString('temporarily unavailable', $unavailable->json('data.message'));
        $this->assertSame(
            AdaptLearningSession::STATUS_UNAVAILABLE,
            AdaptLearningSession::query()->findOrFail($unavailable->json('data.session.id'))->status
        );
    }

    public function test_reviewer_education_permissions_are_scoped(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);

        $this->assertTrue($reviewer->hasPermissionIn($organization, Permissions::EDUCATION_PATTERNS_VIEW));
        $this->assertTrue($reviewer->hasPermissionIn($organization, Permissions::EDUCATION_PATTERNS_CREATE));
        $this->assertFalse($reviewer->hasPermissionIn($organization, Permissions::EDUCATION_PATTERNS_MANAGE));
        $this->assertFalse($reviewer->hasPermissionIn($organization, Permissions::EDUCATION_RECOMMENDATIONS_MANAGE));
        $this->assertFalse($reviewer->hasPermissionIn($organization, Permissions::COURSES_MANAGE));
    }
}
