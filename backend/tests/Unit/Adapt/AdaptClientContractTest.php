<?php

namespace Tests\Unit\Adapt;

use App\Models\AcademyScenario;
use App\Services\Adapt\AdaptChallengeAdapter;
use App\Services\Adapt\HttpAdaptClient;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class AdaptClientContractTest extends TestCase
{
    public function test_adapter_maps_academy_scenario_fields(): void
    {
        $scenario = new AcademyScenario([
            'prompt' => 'Demo / educational scenario prompt',
            'options' => ['A', 'B'],
            'expected_reasoning_signals' => ['context'],
            'misconception_tags' => ['CSAFE-M001'],
            'difficulty' => 3,
            'adapt_challenge_id' => 'CSAFE-CTX-001',
            'adapt_topic_id' => 'csafety-context',
            'adapt_concept_id' => 'csafety_context_preservation',
            'adapt_domain' => 'community-safety',
        ]);

        $mapped = (new AdaptChallengeAdapter)->toAdaptChallengeRequest($scenario);

        $this->assertSame('csafety-context', $mapped['topic_id']);
        $this->assertSame('community-safety', $mapped['subject_id']);
        $this->assertSame('CSAFE-CTX-001', $mapped['initial_challenge']);
        $this->assertSame(['A', 'B'], $mapped['choices']);
        $this->assertSame(3, $mapped['difficulty']);
    }

    public function test_http_client_parses_session_and_feedback_contract(): void
    {
        config(['adapt.base_url' => 'http://adapt.test']);

        Http::fake([
            'http://adapt.test/api/health' => Http::response(['ok' => true], 200),
            'http://adapt.test/api/sessions' => Http::response([
                'session_id' => 'SES-1',
                'learner_id' => 'u1',
                'status' => 'awaiting_answer',
                'challenge' => [
                    'challenge_id' => 'CSAFE-CTX-001',
                    'prompt' => 'Demo prompt',
                    'choices' => ['Preserve context'],
                    'difficulty' => 2,
                    'topic_id' => 'csafety-context',
                    'domain' => 'community-safety',
                ],
                'evidence_plan' => ['ask_reasoning' => true],
                'confidence_scale' => [['value' => 5, 'label' => 'Very confident']],
                'can_submit' => true,
                'complete' => false,
            ], 201),
            'http://adapt.test/api/sessions/SES-1/responses' => Http::response([
                'session_id' => 'SES-1',
                'status' => 'showing_feedback',
                'complete' => false,
                'challenge' => [
                    'challenge_id' => 'CSAFE-CTX-002',
                    'prompt' => 'Next demo prompt',
                    'choices' => ['Pattern'],
                ],
                'result' => [
                    'feedback' => ['headline' => 'Correct'],
                    'noticed' => ['title' => 'What ADAPT noticed', 'headline' => 'Strong evidence'],
                    'why_this_question' => ['title' => 'Why this question?', 'strategy' => 'INCREASE'],
                    'next_challenge' => [
                        'challenge_id' => 'CSAFE-CTX-002',
                        'prompt' => 'Next demo prompt',
                    ],
                    'adaptation' => ['decision' => 'INCREASE'],
                ],
            ], 200),
        ]);

        $client = new HttpAdaptClient;

        $this->assertTrue($client->isAvailable());

        $session = $client->createSession('csafety-context', 'u1', 'community-safety', 'CSAFE-CTX-001');
        $this->assertSame('SES-1', $session->sessionId);
        $this->assertSame('CSAFE-CTX-001', $session->challenge?->challengeId);

        $feedback = $client->submitResponse('SES-1', 'Preserve context', 5, 'Because context matters', 'CSAFE-CTX-001');
        $this->assertSame('Strong evidence', $feedback->noticed['headline'] ?? null);
        $this->assertSame('INCREASE', $feedback->whyThisQuestion['strategy'] ?? null);
        $this->assertSame('CSAFE-CTX-002', $feedback->nextChallenge?->challengeId);
    }

    public function test_http_client_surfaces_unavailable_without_faking_adaptation(): void
    {
        config(['adapt.base_url' => 'http://adapt.test']);
        Http::fake([
            'http://adapt.test/api/sessions' => Http::response(['error' => 'down'], 503),
        ]);

        $this->expectException(\App\Exceptions\Adapt\AdaptUnavailableException::class);
        (new HttpAdaptClient)->createSession('csafety-context', 'u1');
    }
}
