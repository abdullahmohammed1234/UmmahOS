<?php

namespace App\Services\Education;

use App\Contracts\Adapt\AdaptClient;
use App\Exceptions\Adapt\AdaptUnavailableException;
use App\Models\AdaptLearningSession;
use App\Models\AcademyLesson;
use App\Models\AcademyScenario;
use App\Models\Organization;
use App\Models\User;
use App\Services\Adapt\AdaptChallengeAdapter;
use Illuminate\Support\Carbon;
use Symfony\Component\HttpKernel\Exception\AccessDeniedHttpException;

class AdaptLearningSessionService
{
    public function __construct(
        private readonly AdaptClient $adapt,
        private readonly AdaptChallengeAdapter $adapter,
        private readonly AcademyEducationService $academy,
    ) {}

    /**
     * @return array<string, mixed>
     */
    public function start(Organization $organization, User $user, AcademyLesson $lesson): array
    {
        $lesson = $this->academy->findLesson($organization, $lesson->id);
        $this->academy->markStarted($organization, $user, $lesson);

        $scenario = $lesson->scenarios->first();
        if ($scenario === null) {
            throw AdaptUnavailableException::serviceDown('No adaptive scenarios are attached to this lesson.');
        }

        if (! $this->adapt->isAvailable()) {
            $record = $organization->adaptLearningSessions()->create([
                'user_id' => $user->id,
                'academy_lesson_id' => $lesson->id,
                'academy_scenario_id' => $scenario->id,
                'adapt_topic_id' => $scenario->adapt_topic_id,
                'adapt_subject_id' => $scenario->adapt_domain ?: 'community-safety',
                'status' => AdaptLearningSession::STATUS_UNAVAILABLE,
                'started_at' => Carbon::now(),
            ]);

            return [
                'available' => false,
                'message' => 'Adaptive practice is temporarily unavailable. You can continue with the lesson.',
                'session' => $this->serializeLocalSession($record),
            ];
        }

        $request = $this->adapter->toAdaptChallengeRequest($scenario);
        $learnerId = 'ummah-org-'.$organization->id.'-user-'.$user->id;

        try {
            $remote = $this->adapt->createSession(
                topicId: $request['topic_id'],
                learnerId: $learnerId,
                subjectId: $request['subject_id'],
                initialChallengeId: $request['initial_challenge'],
                maxSteps: max(3, $lesson->scenarios->count()),
            );
        } catch (AdaptUnavailableException $e) {
            $record = $organization->adaptLearningSessions()->create([
                'user_id' => $user->id,
                'academy_lesson_id' => $lesson->id,
                'academy_scenario_id' => $scenario->id,
                'adapt_topic_id' => $request['topic_id'],
                'adapt_subject_id' => $request['subject_id'],
                'status' => AdaptLearningSession::STATUS_UNAVAILABLE,
                'started_at' => Carbon::now(),
            ]);

            return [
                'available' => false,
                'message' => $e->getMessage(),
                'session' => $this->serializeLocalSession($record),
            ];
        }

        $record = $organization->adaptLearningSessions()->create([
            'user_id' => $user->id,
            'academy_lesson_id' => $lesson->id,
            'academy_scenario_id' => $scenario->id,
            'adapt_session_id' => $remote->sessionId,
            'adapt_topic_id' => $request['topic_id'],
            'adapt_subject_id' => $request['subject_id'],
            'status' => AdaptLearningSession::STATUS_ACTIVE,
            'started_at' => Carbon::now(),
        ]);

        return [
            'available' => true,
            'session' => $this->serializeLocalSession($record),
            'adapt' => $remote->toArray(),
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function show(Organization $organization, User $user, int $sessionId): array
    {
        $record = $this->ownedSession($organization, $user, $sessionId);

        if ($record->status === AdaptLearningSession::STATUS_UNAVAILABLE || ! $record->adapt_session_id) {
            return [
                'available' => false,
                'message' => 'Adaptive practice is temporarily unavailable. You can continue with the lesson.',
                'session' => $this->serializeLocalSession($record),
            ];
        }

        try {
            $remote = $this->adapt->getSession($record->adapt_session_id);
        } catch (AdaptUnavailableException $e) {
            return [
                'available' => false,
                'message' => $e->getMessage(),
                'session' => $this->serializeLocalSession($record),
            ];
        }

        return [
            'available' => true,
            'session' => $this->serializeLocalSession($record),
            'adapt' => $remote->toArray(),
            'last_result' => $record->last_result,
        ];
    }

    /**
     * @param  array{answer: string, confidence: int, reasoning?: string|null, challenge_id?: string|null}  $payload
     * @return array<string, mixed>
     */
    public function submit(Organization $organization, User $user, int $sessionId, array $payload): array
    {
        $record = $this->ownedSession($organization, $user, $sessionId);

        if ($record->status === AdaptLearningSession::STATUS_UNAVAILABLE || ! $record->adapt_session_id) {
            return [
                'available' => false,
                'message' => 'Adaptive practice is temporarily unavailable. You can continue with the lesson.',
                'session' => $this->serializeLocalSession($record),
            ];
        }

        try {
            $result = $this->adapt->submitResponse(
                sessionId: $record->adapt_session_id,
                answer: $payload['answer'],
                confidence: (int) $payload['confidence'],
                reasoning: $payload['reasoning'] ?? null,
                challengeId: $payload['challenge_id'] ?? null,
            );
        } catch (AdaptUnavailableException $e) {
            return [
                'available' => false,
                'message' => $e->getMessage(),
                'session' => $this->serializeLocalSession($record),
            ];
        }

        $serialized = $result->toArray();
        $record->last_result = $serialized;

        if ($result->complete) {
            $record->status = AdaptLearningSession::STATUS_COMPLETED;
            $record->completed_at = Carbon::now();
            if ($record->lesson) {
                $this->academy->markCompleted($organization, $user, $record->lesson);
            }
        }

        $record->save();

        return [
            'available' => true,
            'session' => $this->serializeLocalSession($record->fresh()),
            'result' => $serialized,
        ];
    }

    private function ownedSession(Organization $organization, User $user, int $sessionId): AdaptLearningSession
    {
        $record = $organization->adaptLearningSessions()
            ->with(['lesson.scenarios', 'scenario'])
            ->whereKey($sessionId)
            ->firstOrFail();

        if ((int) $record->user_id !== (int) $user->id) {
            throw new AccessDeniedHttpException('You cannot access another learner\'s ADAPT session.');
        }

        return $record;
    }

    /**
     * @return array<string, mixed>
     */
    private function serializeLocalSession(AdaptLearningSession $record): array
    {
        return [
            'id' => $record->id,
            'organization_id' => $record->organization_id,
            'user_id' => $record->user_id,
            'academy_lesson_id' => $record->academy_lesson_id,
            'academy_scenario_id' => $record->academy_scenario_id,
            'adapt_session_id' => $record->adapt_session_id,
            'adapt_topic_id' => $record->adapt_topic_id,
            'adapt_subject_id' => $record->adapt_subject_id,
            'status' => $record->status,
            'started_at' => $record->started_at?->toIso8601String(),
            'completed_at' => $record->completed_at?->toIso8601String(),
        ];
    }
}
