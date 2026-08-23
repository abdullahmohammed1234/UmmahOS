<?php

namespace App\Dto\Adapt;

final class AdaptSessionResponse
{
    /**
     * @param  array<string, mixed>  $evidencePlan
     * @param  list<array<string, mixed>>  $confidenceScale
     * @param  array<string, mixed>  $raw
     */
    public function __construct(
        public readonly string $sessionId,
        public readonly ?string $learnerId,
        public readonly ?string $status,
        public readonly ?AdaptChallengeResponse $challenge,
        public readonly array $evidencePlan,
        public readonly array $confidenceScale,
        public readonly bool $canSubmit,
        public readonly bool $complete,
        public readonly array $raw = [],
    ) {}

    /**
     * @param  array<string, mixed>  $payload
     */
    public static function fromArray(array $payload): self
    {
        $evidencePlan = $payload['evidence_plan'] ?? [];
        $confidenceScale = $payload['confidence_scale'] ?? [];

        return new self(
            sessionId: (string) ($payload['session_id'] ?? ''),
            learnerId: isset($payload['learner_id']) ? (string) $payload['learner_id'] : null,
            status: isset($payload['status']) ? (string) $payload['status'] : null,
            challenge: AdaptChallengeResponse::fromArray(
                isset($payload['challenge']) && is_array($payload['challenge'])
                    ? $payload['challenge']
                    : null
            ),
            evidencePlan: is_array($evidencePlan) ? $evidencePlan : [],
            confidenceScale: is_array($confidenceScale) ? array_values($confidenceScale) : [],
            canSubmit: (bool) ($payload['can_submit'] ?? false),
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
            'learner_id' => $this->learnerId,
            'status' => $this->status,
            'challenge' => $this->challenge?->toArray(),
            'evidence_plan' => $this->evidencePlan,
            'confidence_scale' => $this->confidenceScale,
            'can_submit' => $this->canSubmit,
            'complete' => $this->complete,
        ];
    }
}
