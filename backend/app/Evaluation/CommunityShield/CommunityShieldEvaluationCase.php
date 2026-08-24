<?php

namespace App\Evaluation\CommunityShield;

/**
 * Formal contract for one synthetic Community Shield evaluation scenario.
 *
 * All cases are synthetic. They never contain real personal data or real hateful content.
 */
final class CommunityShieldEvaluationCase
{
    public const CATEGORY_EXPLICIT = 'explicit';

    public const CATEGORY_CODED = 'coded';

    public const CATEGORY_VISUAL = 'visual';

    public const CATEGORY_RELATIONAL = 'relational';

    public const CATEGORY_MISINFORMATION = 'misinformation';

    public const CATEGORY_SYNTHETIC_AI = 'synthetic_ai';

    public const CATEGORY_AMBIGUOUS = 'ambiguous';

    /**
     * @param  array{
     *     id: string,
     *     category: string,
     *     platform: string,
     *     content_type: string,
     *     visibility: string,
     *     language: string,
     *     description: string,
     *     synthetic_original_item: array{title:?string,content:?string,author:?string,posted_at:?string},
     *     synthetic_context:?string,
     *     synthetic_replies: list<array{author:?string,content:string,posted_at:?string}>,
     *     synthetic_related_items: list<array{platform:string,content_type:string,description:string,reference_url:?string,observed_at:?string}>,
     *     reporter_notes:?string,
     *     source_url:?string,
     *     observed_at:?string,
     *     privacy_canary:?string,
     *     expected_context_preservation: bool,
     *     expected_uncertainty_behavior: array{level:string,recommended_action:string,must_not_assert_fact:bool},
     *     expected_human_review_behavior: array{route_to_review:bool,preferred_outcome:?string,allow_uncertain:bool},
     *     expected_privacy_behavior: array{protect_reporter_notes:bool,protect_canary:bool,member_cannot_export:bool},
     *     expected_reporting_behavior: array{package_actionable:bool,automatic_submission:bool},
     *     expected_outcome_behavior: array{track_lifecycle:bool,default_verification:string},
     *     expected_harmful_claim_behavior: array{ai_advisory_only:bool,must_not_auto_confirm:bool,observed_not_fact:bool},
     *     expected_review_classification:?string,
     *     rationale: string,
     *     synthetic_analysis: array<string, mixed>,
     * }  $data
     */
    public function __construct(
        public readonly array $data,
    ) {
        if (($this->data['synthetic'] ?? true) !== true) {
            throw new \InvalidArgumentException('Evaluation cases must be marked synthetic.');
        }
    }

    public function id(): string
    {
        return $this->data['id'];
    }

    public function category(): string
    {
        return $this->data['category'];
    }

    /**
     * @return list<string>
     */
    public static function categories(): array
    {
        return [
            self::CATEGORY_EXPLICIT,
            self::CATEGORY_CODED,
            self::CATEGORY_VISUAL,
            self::CATEGORY_RELATIONAL,
            self::CATEGORY_MISINFORMATION,
            self::CATEGORY_SYNTHETIC_AI,
            self::CATEGORY_AMBIGUOUS,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return $this->data;
    }
}
