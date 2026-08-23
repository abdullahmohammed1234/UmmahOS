<?php

namespace Tests\Fixtures\AI;

/**
 * Deterministic fictional evaluation fixtures for Community Shield AI analysis.
 *
 * These are not live model outputs. They define structured incident contexts
 * representing clear, ambiguous, repeated-pattern, and insufficient-evidence cases.
 */
final class EvaluationFixtures
{
    /**
     * Case A — clear potential targeting of a religious identity.
     *
     * @return array{context: array<string, mixed>, expected_analysis: array<string, mixed>}
     */
    public static function caseAClearPotentialTargeting(): array
    {
        return [
            'context' => [
                'platform' => 'x',
                'content_type' => 'post',
                'visibility' => 'public',
                'source_url' => 'https://example.test/post/case-a',
                'description' => 'Public post using derogatory language about Muslims.',
                'original_item' => [
                    'title' => 'Not provided',
                    'content' => 'Fictional demo: Those people who follow Islam do not belong here and should leave.',
                    'author' => '@demo_case_a',
                    'posted_at' => '2026-08-20T12:00:00+00:00',
                ],
                'observed_at' => '2026-08-20T13:00:00+00:00',
                'surrounding_context' => 'Posted publicly under a campus discussion hashtag.',
                'replies' => [
                    [
                        'author' => '@observer1',
                        'content' => 'This is unacceptable.',
                        'posted_at' => '2026-08-20T12:10:00+00:00',
                        'position' => 0,
                    ],
                ],
                'related_items' => [],
                'language' => 'en',
                'reporter_notes' => 'Appears to target religious identity.',
            ],
            'expected_analysis' => [
                'signals' => [
                    [
                        'name' => 'religious_identity_targeting',
                        'description' => 'Potential signal — the language may reference a religious identity in a derogatory exclusionary context.',
                        'evidence' => [
                            'Original item refers to people who follow Islam and says they should leave.',
                        ],
                        'confidence' => 'high',
                    ],
                    [
                        'name' => 'group_targeting',
                        'description' => 'Possible indication of collective targeting rather than criticism of a specific individual action.',
                        'evidence' => [
                            'The phrasing addresses a religious group collectively.',
                        ],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => [
                    'label' => 'potential_hate',
                    'confidence' => 'high',
                ],
                'uncertainty' => [
                    'level' => 'low',
                    'explanation' => 'Low uncertainty — the available context consistently supports the identified signals, but human review is still recommended.',
                ],
                'alternative_interpretation' => null,
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
        ];
    }

    /**
     * Case B — ambiguous context with a plausible alternative interpretation.
     *
     * @return array{context: array<string, mixed>, expected_analysis: array<string, mixed>}
     */
    public static function caseBAmbiguousContext(): array
    {
        return [
            'context' => [
                'platform' => 'discord',
                'content_type' => 'message',
                'visibility' => 'group',
                'source_url' => 'Not provided',
                'description' => 'Ambiguous phrase that may be quoting another user.',
                'original_item' => [
                    'title' => 'Not provided',
                    'content' => 'Fictional demo: Someone said "Muslims are the problem" in yesterday\'s thread.',
                    'author' => '@demo_case_b',
                    'posted_at' => '2026-08-19T20:00:00+00:00',
                ],
                'observed_at' => '2026-08-19T21:00:00+00:00',
                'surrounding_context' => 'Incomplete thread — earlier messages were not captured.',
                'replies' => [
                    [
                        'author' => '@peer',
                        'content' => 'Are you quoting that or agreeing with it?',
                        'posted_at' => '2026-08-19T20:05:00+00:00',
                        'position' => 0,
                    ],
                ],
                'related_items' => [],
                'language' => 'en',
                'reporter_notes' => 'Hard to tell if this is endorsement or documentation.',
            ],
            'expected_analysis' => [
                'signals' => [
                    [
                        'name' => 'contextual_ambiguity',
                        'description' => 'Potential signal — the phrase may reproduce harmful language, but intent is unclear from the incomplete thread.',
                        'evidence' => [
                            'Original message embeds a harmful phrase inside a report of what someone said.',
                            'A reply asks whether the author is quoting or agreeing.',
                        ],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => [
                    'label' => 'unclear',
                    'confidence' => 'low',
                ],
                'uncertainty' => [
                    'level' => 'high',
                    'explanation' => 'High uncertainty — surrounding context is incomplete and the available evidence may have multiple interpretations.',
                ],
                'alternative_interpretation' => 'The phrase may be quoting another participant rather than expressing the author\'s own position.',
                'recommended_action' => [
                    'type' => 'request_more_context',
                    'reason' => 'Additional context recommended before classification.',
                ],
            ],
        ];
    }

    /**
     * Case C — repeated / cross-platform pattern.
     *
     * @return array{context: array<string, mixed>, expected_analysis: array<string, mixed>}
     */
    public static function caseCRepeatedPattern(): array
    {
        return [
            'context' => [
                'platform' => 'x',
                'content_type' => 'post',
                'visibility' => 'public',
                'source_url' => 'https://example.test/post/case-c',
                'description' => 'Same slogan appearing across platforms.',
                'original_item' => [
                    'title' => 'Not provided',
                    'content' => 'Fictional demo slogan: No Muslims on campus.',
                    'author' => '@demo_case_c',
                    'posted_at' => '2026-08-18T09:00:00+00:00',
                ],
                'observed_at' => '2026-08-18T10:00:00+00:00',
                'surrounding_context' => 'Similar wording spotted elsewhere the same day.',
                'replies' => [],
                'related_items' => [
                    [
                        'platform' => 'reddit',
                        'content_type' => 'post',
                        'description' => 'Fictional demo slogan: No Muslims on campus.',
                        'reference_url' => 'https://example.test/reddit/case-c',
                        'observed_at' => '2026-08-18T11:00:00+00:00',
                    ],
                    [
                        'platform' => 'telegram',
                        'content_type' => 'message',
                        'description' => 'Fictional demo slogan: No Muslims on campus.',
                        'reference_url' => 'Not provided',
                        'observed_at' => '2026-08-18T12:00:00+00:00',
                    ],
                ],
                'language' => 'en',
                'reporter_notes' => 'Looks coordinated or copy-pasted.',
            ],
            'expected_analysis' => [
                'signals' => [
                    [
                        'name' => 'repeated_language_pattern',
                        'description' => 'Potential signal — similar wording appears across the supplied related items.',
                        'evidence' => [
                            'Original item and related Reddit/Telegram items share the same slogan.',
                        ],
                        'confidence' => 'high',
                    ],
                    [
                        'name' => 'cross_platform_repetition',
                        'description' => 'Possible indication of cross-platform repetition based on supplied related copies.',
                        'evidence' => [
                            'Related copies were recorded on Reddit and Telegram.',
                        ],
                        'confidence' => 'moderate',
                    ],
                    [
                        'name' => 'religious_identity_targeting',
                        'description' => 'May suggest targeting of a religious identity.',
                        'evidence' => [
                            'The repeated slogan singles out Muslims.',
                        ],
                        'confidence' => 'moderate',
                    ],
                ],
                'classification' => [
                    'label' => 'potential_targeted_abuse',
                    'confidence' => 'moderate',
                ],
                'uncertainty' => [
                    'level' => 'moderate',
                    'explanation' => 'Moderate uncertainty — repetition is visible in supplied evidence, but coordination cannot be proven from the record alone.',
                ],
                'alternative_interpretation' => null,
                'recommended_action' => [
                    'type' => 'human_review',
                    'reason' => 'Human review recommended.',
                ],
            ],
        ];
    }

    /**
     * Case D — benign / insufficient evidence.
     *
     * @return array{context: array<string, mixed>, expected_analysis: array<string, mixed>}
     */
    public static function caseDInsufficientEvidence(): array
    {
        return [
            'context' => [
                'platform' => 'other',
                'content_type' => 'post',
                'visibility' => 'unknown',
                'source_url' => 'Not provided',
                'description' => 'Reporter saw something concerning but could not capture details.',
                'original_item' => [
                    'title' => 'Not provided',
                    'content' => 'Not provided',
                    'author' => 'Not provided',
                    'posted_at' => 'Not provided',
                ],
                'observed_at' => '2026-08-17T15:00:00+00:00',
                'surrounding_context' => 'Not provided',
                'replies' => [],
                'related_items' => [],
                'language' => 'unknown',
                'reporter_notes' => 'I deleted the screenshot by mistake.',
            ],
            'expected_analysis' => [
                'signals' => [
                    [
                        'name' => 'no_clear_signal',
                        'description' => 'Insufficient captured evidence to identify a potential harm signal.',
                        'evidence' => [
                            'Original item content was not provided.',
                            'Surrounding context was not provided.',
                        ],
                        'confidence' => 'low',
                    ],
                ],
                'classification' => [
                    'label' => 'no_clear_harm_signal',
                    'confidence' => 'low',
                ],
                'uncertainty' => [
                    'level' => 'high',
                    'explanation' => 'High uncertainty — surrounding context is incomplete and the available evidence may have multiple interpretations.',
                ],
                'alternative_interpretation' => null,
                'recommended_action' => [
                    'type' => 'request_more_context',
                    'reason' => 'Additional context recommended before classification.',
                ],
            ],
        ];
    }
}
