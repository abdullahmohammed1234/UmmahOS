<?php

namespace Tests\Feature\Evaluation;

use App\Models\AcademyLesson;
use App\Models\AcademyScenario;
use App\Models\AdaptLearningSession;
use App\Models\Course;
use App\Models\Incident;
use App\Models\LearningPattern;
use App\Models\LearningRecommendation;
use App\Services\Adapt\AdaptChallengeAdapter;
use App\Services\Adapt\FakeAdaptClient;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

/**
 * Phase 10 Academy + ADAPT safety bridge checks (FakeAdaptClient only).
 */
class CommunityShieldAdaptEducationSafetyTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
    }

    public function test_confirmed_incident_to_pattern_to_academy_to_adapt_keeps_privacy_boundaries(): void
    {
        $organization = $this->createOrganization();
        $admin = $this->createMember($organization, $this->adminRole);
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $learner = $this->createMember($organization, $this->memberRole);
        $otherLearner = $this->createMember($organization, $this->memberRole);

        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $learner->id,
            'status' => Incident::STATUS_RESOLVED,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'safety_classification' => Incident::CLASSIFICATION_HATE,
            'description' => 'REAL_INCIDENT_TEXT_MUST_NOT_LEAK',
            'original_item_content' => 'REAL_EVIDENCE_MUST_NOT_LEAK',
            'reporter_notes' => 'REPORTER_IDENTITY_CONTEXT_MUST_NOT_LEAK',
            'review_notes' => 'REVIEWER_NOTES_MUST_NOT_LEAK',
        ]);

        $patternResponse = $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/learning-pattern'), [
                'pattern_type' => 'contextual_hate',
                'title' => 'Synthetic Learning Pattern',
                'summary' => 'Sanitized educational abstraction for evaluation.',
                'learning_objective' => 'Recognize when context changes interpretation.',
                'domain' => 'community-safety',
            ])
            ->assertCreated()
            ->json('data');

        $this->assertSame($incident->id, $patternResponse['source_incident_id']);
        $this->assertStringNotContainsString('REAL_INCIDENT_TEXT_MUST_NOT_LEAK', json_encode($patternResponse));
        $this->assertStringNotContainsString('REAL_EVIDENCE_MUST_NOT_LEAK', json_encode($patternResponse));
        $this->assertStringNotContainsString('REPORTER_IDENTITY_CONTEXT_MUST_NOT_LEAK', json_encode($patternResponse));
        $this->assertStringNotContainsString('REVIEWER_NOTES_MUST_NOT_LEAK', json_encode($patternResponse));

        $pattern = LearningPattern::query()->findOrFail($patternResponse['id']);
        $this->assertNull($pattern->getAttribute('description') ?? null);

        $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'learning-patterns/'.$pattern->id.'/approve'))
            ->assertOk()
            ->assertJsonPath('data.status', LearningPattern::STATUS_APPROVED);

        $course = Course::factory()->published()->create([
            'organization_id' => $organization->id,
            'created_by' => $admin->id,
        ]);
        $lesson = AcademyLesson::query()->create([
            'organization_id' => $organization->id,
            'course_id' => $course->id,
            'title' => 'Synthetic Community Safety Lesson',
            'learning_objective' => 'Practice context preservation.',
            'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
            'status' => AcademyLesson::STATUS_PUBLISHED,
            'created_by' => $admin->id,
            'sections' => [
                ['heading' => 'Demo', 'body' => 'Educational scenario only — not a real incident.'],
            ],
        ]);
        $scenario = AcademyScenario::query()->create([
            'organization_id' => $organization->id,
            'academy_lesson_id' => $lesson->id,
            'title' => 'Synthetic ADAPT scenario',
            'prompt' => 'Demo / educational scenario: choose the safest next step.',
            'options' => ['Preserve context', 'Reply immediately'],
            'expected_reasoning_signals' => ['context'],
            'misconception_tags' => ['CSAFE-M001'],
            'difficulty' => 2,
            'adapt_challenge_id' => 'CSAFE-CTX-001',
            'adapt_topic_id' => 'csafety-context',
            'adapt_concept_id' => 'csafety_context_preservation',
            'adapt_domain' => 'community-safety',
            'sort_order' => 1,
            'is_demo' => true,
        ]);

        $recommendation = $this->actingAsApi($admin)
            ->postJson($this->orgUrl($organization, 'learning-recommendations'), [
                'learning_pattern_id' => $pattern->id,
                'academy_lesson_id' => $lesson->id,
                'academy_course_id' => $course->id,
                'reason' => 'Synthetic evaluation recommendation.',
                'status' => LearningRecommendation::STATUS_PUBLISHED,
            ])
            ->assertCreated()
            ->json('data');

        $learnerRecs = $this->actingAsApi($learner)
            ->getJson($this->orgUrl($organization, 'learning-recommendations'))
            ->assertOk()
            ->json('data');

        $this->assertNotEmpty($learnerRecs);
        $this->assertArrayNotHasKey('source_incident_id', $learnerRecs[0]['pattern'] ?? []);
        $this->assertSame('Synthetic Learning Pattern', $learnerRecs[0]['pattern']['title'] ?? null);

        $mapped = $this->app->make(AdaptChallengeAdapter::class)->toAdaptChallengeRequest($scenario);
        $this->assertSame('Demo / educational scenario: choose the safest next step.', $mapped['prompt']);
        $this->assertStringNotContainsString('REAL_EVIDENCE_MUST_NOT_LEAK', json_encode($mapped));
        $this->assertStringNotContainsString('AI analysis', strtolower(json_encode($mapped)));

        $session = $this->actingAsApi($learner)
            ->postJson($this->orgUrl($organization, 'academy/lessons/'.$lesson->id.'/adapt-sessions'))
            ->assertCreated()
            ->assertJsonPath('data.available', true)
            ->json('data');

        $sessionId = $session['session']['id'];
        $this->assertSame($learner->id, AdaptLearningSession::query()->findOrFail($sessionId)->user_id);

        $this->actingAsApi($otherLearner)
            ->getJson($this->orgUrl($organization, 'academy/adapt-sessions/'.$sessionId))
            ->assertForbidden();

        $this->actingAsApi($otherLearner)
            ->postJson($this->orgUrl($organization, 'academy/adapt-sessions/'.$sessionId.'/responses'), [
                'answer' => 'Preserve context',
                'confidence' => 4,
                'reasoning' => 'Synthetic reasoning',
                'challenge_id' => $session['adapt']['challenge']['challenge_id'],
            ])
            ->assertForbidden();

        /** @var FakeAdaptClient $fake */
        $fake = $this->app->make(FakeAdaptClient::class);
        $this->assertNotNull($fake);

        $this->assertSame($recommendation['id'], $learnerRecs[0]['id']);
    }

    public function test_learning_pattern_service_does_not_copy_private_incident_fields(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reviewer->id,
            'review_outcome' => Incident::OUTCOME_CONFIRMED,
            'status' => Incident::STATUS_RESOLVED,
            'description' => 'should-not-copy',
            'reporter_notes' => 'should-not-copy-notes',
            'original_item_content' => 'should-not-copy-evidence',
            'source_url' => 'https://example.invalid/should-not-copy',
        ]);

        $pattern = $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/learning-pattern'), [
                'pattern_type' => 'other',
                'title' => 'Sanitized only',
                'summary' => 'Human-authored summary',
                'learning_objective' => 'Learn safely',
            ])
            ->assertCreated()
            ->json('data');

        $this->assertSame($incident->id, $pattern['source_incident_id']);
        $this->assertSame('Sanitized only', $pattern['title']);
        $this->assertSame('Human-authored summary', $pattern['summary']);
        $encoded = json_encode($pattern);
        $this->assertStringNotContainsString('should-not-copy', $encoded);
        $this->assertStringNotContainsString('should-not-copy-notes', $encoded);
        $this->assertStringNotContainsString('should-not-copy-evidence', $encoded);
        $this->assertStringNotContainsString('example.invalid/should-not-copy', $encoded);
    }

    public function test_uncertain_incident_cannot_become_learning_pattern(): void
    {
        $organization = $this->createOrganization();
        $reviewer = $this->createMember($organization, $this->reviewerRole);
        $incident = Incident::factory()->create([
            'organization_id' => $organization->id,
            'reported_by' => $reviewer->id,
            'review_outcome' => Incident::OUTCOME_UNCERTAIN,
            'status' => Incident::STATUS_REVIEWING,
        ]);

        $this->actingAsApi($reviewer)
            ->postJson($this->orgUrl($organization, 'community-shield/reports/'.$incident->id.'/learning-pattern'), [
                'pattern_type' => 'other',
                'title' => 'Should fail',
                'summary' => 'Summary',
                'learning_objective' => 'Objective',
            ])
            ->assertStatus(422);
    }
}
