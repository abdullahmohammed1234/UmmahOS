<?php

namespace App\Services\Adapt;

use App\Contracts\Adapt\AdaptClient;
use App\Dto\Adapt\AdaptChallengeResponse;
use App\Dto\Adapt\AdaptFeedbackResponse;
use App\Dto\Adapt\AdaptSessionResponse;
use App\Exceptions\Adapt\AdaptUnavailableException;

/**
 * Deterministic fake for Laravel tests. Live demo uses HttpAdaptClient.
 */
class FakeAdaptClient implements AdaptClient
{
    public bool $available = true;

    /** @var array<string, array<string, mixed>> */
    private array $sessions = [];

    private int $step = 0;

    public function isAvailable(): bool
    {
        return $this->available;
    }

    public function createSession(
        string $topicId,
        string $learnerId,
        ?string $subjectId = null,
        ?string $initialChallengeId = null,
        int $maxSteps = 10
    ): AdaptSessionResponse {
        if (! $this->available) {
            throw AdaptUnavailableException::serviceDown('fake unavailable');
        }

        $sessionId = 'FAKE-SES-'.(count($this->sessions) + 1);
        $challenge = $this->challenge($initialChallengeId ?: 'CSAFE-CTX-001', $topicId, $subjectId);

        $this->sessions[$sessionId] = [
            'learner_id' => $learnerId,
            'topic_id' => $topicId,
            'subject_id' => $subjectId,
            'step' => 0,
            'challenge' => $challenge,
            'max_steps' => $maxSteps,
        ];

        return AdaptSessionResponse::fromArray([
            'session_id' => $sessionId,
            'learner_id' => $learnerId,
            'status' => 'awaiting_answer',
            'challenge' => $challenge,
            'evidence_plan' => [
                'ask_confidence' => true,
                'ask_reasoning' => true,
                'reasoning_prompt' => 'How did you get this?',
            ],
            'confidence_scale' => [
                ['value' => 1, 'label' => 'Not confident'],
                ['value' => 5, 'label' => 'Very confident'],
            ],
            'can_submit' => true,
            'complete' => false,
        ]);
    }

    public function getSession(string $sessionId): AdaptSessionResponse
    {
        if (! $this->available || ! isset($this->sessions[$sessionId])) {
            throw AdaptUnavailableException::serviceDown('session missing');
        }

        $session = $this->sessions[$sessionId];

        return AdaptSessionResponse::fromArray([
            'session_id' => $sessionId,
            'learner_id' => $session['learner_id'],
            'status' => 'awaiting_answer',
            'challenge' => $session['challenge'],
            'evidence_plan' => [
                'ask_confidence' => true,
                'ask_reasoning' => true,
            ],
            'confidence_scale' => [
                ['value' => 1, 'label' => 'Not confident'],
                ['value' => 5, 'label' => 'Very confident'],
            ],
            'can_submit' => true,
            'complete' => false,
        ]);
    }

    public function submitResponse(
        string $sessionId,
        string $answer,
        int $confidence,
        ?string $reasoning = null,
        ?string $challengeId = null
    ): AdaptFeedbackResponse {
        if (! $this->available || ! isset($this->sessions[$sessionId])) {
            throw AdaptUnavailableException::serviceDown('session missing');
        }

        $session = &$this->sessions[$sessionId];
        $session['step']++;
        $this->step = $session['step'];

        $strong = $confidence >= 4 && filled($reasoning) && strlen((string) $reasoning) > 12;
        $strategy = $strong ? 'INCREASE' : ($confidence <= 2 ? 'REMEDIATE' : 'MAINTAIN');

        $nextId = match ($session['step']) {
            1 => 'CSAFE-CTX-002',
            2 => 'CSAFE-CTX-003',
            3 => 'CSAFE-CTX-004',
            default => 'CSAFE-CTX-005',
        };

        $complete = $session['step'] >= ($session['max_steps'] ?? 5);
        $next = $complete
            ? null
            : $this->challenge($nextId, $session['topic_id'], $session['subject_id']);

        $session['challenge'] = $next;

        return AdaptFeedbackResponse::fromArray([
            'session_id' => $sessionId,
            'status' => $complete ? 'complete' : 'showing_feedback',
            'challenge' => $next,
            'complete' => $complete,
            'result' => [
                'feedback' => [
                    'headline' => $strong ? 'Correct' : 'Keep going',
                    'tone' => $strong ? 'success' : 'neutral',
                    'detail' => 'Fake ADAPT evaluated answer, confidence, and reasoning.',
                    'answer_status' => $strong ? 'CORRECT' : 'PARTIAL',
                ],
                'noticed' => [
                    'title' => 'What ADAPT noticed',
                    'headline' => $strong ? 'Strong evidence' : 'Mixed evidence',
                    'body' => $strong
                        ? 'You prioritized context with clear reasoning.'
                        : 'Your response showed uncertainty around context preservation.',
                    'strategy' => $strategy,
                    'strategy_plain' => $strategy === 'INCREASE'
                        ? "Let's raise the challenge"
                        : ($strategy === 'REMEDIATE' ? "Let's reinforce this skill" : 'Stay at this level'),
                    'from_trace' => true,
                    'bullets' => [
                        ['ok' => $strong, 'text' => 'Answer quality'],
                        ['ok' => filled($reasoning), 'text' => 'Reasoning provided'],
                        ['ok' => $confidence >= 3, 'text' => 'Confidence signal'],
                    ],
                ],
                'why_this_question' => [
                    'title' => 'Why this question?',
                    'text' => $complete
                        ? 'Session complete based on adaptive strategy.'
                        : 'ADAPT selected this challenge because your previous response informed the '.$strategy.' strategy.',
                    'strategy' => $strategy,
                    'challenge_id' => $nextId,
                    'from_trace' => true,
                ],
                'next_challenge' => $next,
                'adaptation' => [
                    'decision' => $strategy,
                    'reason' => 'Deterministic fake adaptation for tests.',
                ],
            ],
        ]);
    }

    /**
     * @return array<string, mixed>
     */
    private function challenge(string $id, string $topicId, ?string $subjectId): array
    {
        $prompts = [
            'CSAFE-CTX-001' => 'Demo / educational scenario: A message appears insulting, but the surrounding conversation changes its meaning. What should you do first?',
            'CSAFE-CTX-002' => 'Demo / educational scenario: You encounter repeated comments targeting a religious identity. Which information is most useful to preserve?',
            'CSAFE-CTX-003' => 'Demo / educational scenario: A report contains an isolated screenshot but lacks context. What additional information would make the report more useful?',
            'CSAFE-CTX-004' => 'Demo / educational scenario: You are unsure whether a comment is coded targeting. What is the most careful next step?',
            'CSAFE-CTX-005' => 'Demo / educational scenario: Which practice best supports safe reporting?',
        ];

        return [
            'challenge_id' => $id,
            'prompt' => $prompts[$id] ?? 'Demo / educational scenario challenge',
            'choices' => [
                'Preserve context carefully',
                'Reply immediately in public',
                'Ignore everything',
                'Invent missing details',
            ],
            'difficulty' => 2,
            'difficulty_label' => 'Basic',
            'challenge_type' => 'SCENARIO',
            'concept_id' => 'csafety_context_preservation',
            'domain' => $subjectId ?: 'community-safety',
            'topic_id' => $topicId,
        ];
    }
}
