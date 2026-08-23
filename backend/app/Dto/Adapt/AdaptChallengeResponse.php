<?php

namespace App\Dto\Adapt;

final class AdaptChallengeResponse
{
    /**
     * @param  list<string>  $choices
     * @param  array<string, mixed>  $raw
     */
    public function __construct(
        public readonly ?string $challengeId,
        public readonly ?string $prompt,
        public readonly array $choices,
        public readonly ?int $difficulty,
        public readonly ?string $difficultyLabel,
        public readonly ?string $challengeType,
        public readonly ?string $conceptId,
        public readonly ?string $domain,
        public readonly ?string $topicId,
        public readonly array $raw = [],
    ) {}

    /**
     * @param  array<string, mixed>|null  $payload
     */
    public static function fromArray(?array $payload): ?self
    {
        if ($payload === null || $payload === []) {
            return null;
        }

        $choices = $payload['choices'] ?? [];
        if (! is_array($choices)) {
            $choices = [];
        }

        return new self(
            challengeId: isset($payload['challenge_id']) ? (string) $payload['challenge_id'] : null,
            prompt: isset($payload['prompt']) ? (string) $payload['prompt'] : null,
            choices: array_values(array_map('strval', $choices)),
            difficulty: isset($payload['difficulty']) ? (int) $payload['difficulty'] : null,
            difficultyLabel: isset($payload['difficulty_label']) ? (string) $payload['difficulty_label'] : null,
            challengeType: isset($payload['challenge_type']) ? (string) $payload['challenge_type'] : null,
            conceptId: isset($payload['concept_id']) ? (string) $payload['concept_id'] : null,
            domain: isset($payload['domain']) ? (string) $payload['domain'] : null,
            topicId: isset($payload['topic_id']) ? (string) $payload['topic_id'] : null,
            raw: $payload,
        );
    }

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return [
            'challenge_id' => $this->challengeId,
            'prompt' => $this->prompt,
            'choices' => $this->choices,
            'difficulty' => $this->difficulty,
            'difficulty_label' => $this->difficultyLabel,
            'challenge_type' => $this->challengeType,
            'concept_id' => $this->conceptId,
            'domain' => $this->domain,
            'topic_id' => $this->topicId,
        ];
    }
}
