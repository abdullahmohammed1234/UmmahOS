<?php

namespace App\Evaluation\CommunityShield;

/**
 * Result of evaluating one synthetic Community Shield scenario against safety invariants.
 */
final class CommunityShieldEvaluationResult
{
    /**
     * @param  list<string>  $failures
     * @param  array<string, bool>  $checks
     */
    public function __construct(
        public readonly string $scenarioId,
        public readonly string $category,
        public readonly bool $passed,
        public readonly bool $contextPreserved,
        public readonly bool $uncertaintyIdentified,
        public readonly bool $humanReviewRequired,
        public readonly bool $privacyProtected,
        public readonly bool $evidencePackageActionable,
        public readonly bool $outcomeTrackingPreserved,
        public readonly bool $harmfulClaimAvoided,
        public readonly array $failures = [],
        public readonly string $notes = '',
        public readonly array $checks = [],
        public readonly bool $critical = false,
    ) {}

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return [
            'scenario_id' => $this->scenarioId,
            'category' => $this->category,
            'passed' => $this->passed,
            'critical' => $this->critical,
            'context_preserved' => $this->contextPreserved,
            'uncertainty_identified' => $this->uncertaintyIdentified,
            'human_review_required' => $this->humanReviewRequired,
            'privacy_protected' => $this->privacyProtected,
            'evidence_package_actionable' => $this->evidencePackageActionable,
            'outcome_tracking_preserved' => $this->outcomeTrackingPreserved,
            'harmful_claim_avoided' => $this->harmfulClaimAvoided,
            'failures' => $this->failures,
            'notes' => $this->notes,
            'checks' => $this->checks,
        ];
    }
}
