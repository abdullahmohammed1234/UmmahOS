<?php

namespace App\Services\Adapt;

use App\Models\AcademyScenario;

/**
 * Maps Academy scenarios to ADAPT session/start parameters.
 * Does not invent adaptive decisions — only provides catalog IDs ADAPT already knows.
 */
class AdaptChallengeAdapter
{
    /**
     * @return array{
     *     topic_id: string,
     *     subject_id: string,
     *     concept_id: ?string,
     *     initial_challenge: ?string,
     *     domain: string,
     *     prompt: string,
     *     choices: list<string>,
     *     difficulty: int,
     *     misconception_tags: list<string>,
     *     expected_reasoning_signals: list<string>
     * }
     */
    public function toAdaptChallengeRequest(AcademyScenario $scenario): array
    {
        $options = $scenario->options ?? [];
        if (! is_array($options)) {
            $options = [];
        }

        $signals = $scenario->expected_reasoning_signals ?? [];
        if (! is_array($signals)) {
            $signals = [];
        }

        $tags = $scenario->misconception_tags ?? [];
        if (! is_array($tags)) {
            $tags = [];
        }

        return [
            'topic_id' => (string) ($scenario->adapt_topic_id ?: 'csafety-context'),
            'subject_id' => (string) ($scenario->adapt_domain ?: 'community-safety'),
            'concept_id' => $scenario->adapt_concept_id,
            'initial_challenge' => $scenario->adapt_challenge_id,
            'domain' => (string) ($scenario->adapt_domain ?: 'community-safety'),
            'prompt' => (string) $scenario->prompt,
            'choices' => array_values(array_map('strval', $options)),
            'difficulty' => (int) $scenario->difficulty,
            'misconception_tags' => array_values(array_map('strval', $tags)),
            'expected_reasoning_signals' => array_values(array_map('strval', $signals)),
        ];
    }
}
