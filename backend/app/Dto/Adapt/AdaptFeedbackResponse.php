<?php

namespace App\Dto\Adapt;

final class AdaptFeedbackResponse
{
    /**
     * @param  array<string, mixed>|null  $feedback
     * @param  array<string, mixed>|null  $noticed
     * @param  array<string, mixed>|null  $whyThisQuestion
     * @param  array<string, mixed>|null  $adaptation
     * @param  array<string, mixed>  $raw
     */
    public function __construct(
        public readonly string $sessionId,
        public readonly ?string $status,
        public readonly ?AdaptChallengeResponse $challenge,
        public readonly ?array $feedback,
        public readonly ?array $noticed,
        public readonly ?array $whyThisQuestion,
        public readonly ?AdaptChallengeResponse $nextChallenge,
        public readonly ?array $adaptation,
        public readonly bool $complete,
        public readonly array $raw = [],
    ) {}

    /**
     * @param  array<string, mixed>  $payload
     */
    public static function fromArray(array $payload): self
    {
        $result = isset($payload['result']) && is_array($payload['result'])
            ? $payload['result']
            : [];

        $next = $result['next_challenge'] ?? null;
        if (! is_array($next)) {
            $next = null;
        }

        return new self(
            sessionId: (string) ($payload['session_id'] ?? ''),
            status: isset($payload['status']) ? (string) $payload['status'] : null,
            challenge: AdaptChallengeResponse::fromArray(
                isset($payload['challenge']) && is_array($payload['challenge'])
                    ? $payload['challenge']
                    : null
            ),
            feedback: isset($result['feedback']) && is_array($result['feedback']) ? $result['feedback'] : null,
            noticed: isset($result['noticed']) && is_array($result['noticed']) ? $result['noticed'] : null,
            whyThisQuestion: isset($result['why_this_question']) && is_array($result['why_this_question'])
                ? $result['why_this_question']
                : null,
            nextChallenge: AdaptChallengeResponse::fromArray($next),
            adaptation: isset($result['adaptation']) && is_array($result['adaptation'])
                ? $result['adaptation']
                : null,
            complete: (bool) ($payload['complete'] ?? false),
            raw: $payload,
        );
    }

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return [
            'session_id' => $this->sessionId,
            'status' => $this->status,
            'challenge' => $this->challenge?->toArray(),
            'feedback' => $this->feedback,
            'noticed' => $this->noticed,
            'why_this_question' => $this->whyThisQuestion,
            'next_challenge' => $this->nextChallenge?->toArray(),
            'adaptation' => $this->adaptation,
            'complete' => $this->complete,
        ];
    }
}
