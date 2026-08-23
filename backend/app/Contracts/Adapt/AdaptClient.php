<?php

namespace App\Contracts\Adapt;

use App\Dto\Adapt\AdaptChallengeResponse;
use App\Dto\Adapt\AdaptFeedbackResponse;
use App\Dto\Adapt\AdaptSessionResponse;
use App\Exceptions\Adapt\AdaptUnavailableException;

interface AdaptClient
{
    public function isAvailable(): bool;

    /**
     * @throws AdaptUnavailableException
     */
    public function createSession(
        string $topicId,
        string $learnerId,
        ?string $subjectId = null,
        ?string $initialChallengeId = null,
        int $maxSteps = 10
    ): AdaptSessionResponse;

    /**
     * @throws AdaptUnavailableException
     */
    public function getSession(string $sessionId): AdaptSessionResponse;

    /**
     * @throws AdaptUnavailableException
     */
    public function submitResponse(
        string $sessionId,
        string $answer,
        int $confidence,
        ?string $reasoning = null,
        ?string $challengeId = null
    ): AdaptFeedbackResponse;
}
