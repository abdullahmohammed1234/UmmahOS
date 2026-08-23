<?php

namespace App\Services\Evidence;

class SafetyPrivacyGuidanceService
{
    /**
     * @return list<string>
     */
    public function notes(): array
    {
        /** @var list<string> $notes */
        $notes = array_values(array_filter(
            config('community_shield_safety.notes', []),
            fn ($note) => is_string($note) && $note !== ''
        ));

        return $notes;
    }

    public function aiDisclaimer(): string
    {
        return (string) config(
            'community_shield_safety.ai_disclaimer',
            'AI analysis is advisory and may be uncertain. It does not constitute the final determination. Human review is authoritative.'
        );
    }

    public function humanReviewDisclaimer(): string
    {
        return (string) config(
            'community_shield_safety.human_review_disclaimer',
            'Human review is authoritative. The determination shown here was made by an authorized Community Safety Reviewer based on the available evidence, when a review exists.'
        );
    }

    public function reportingDisclaimer(): string
    {
        return (string) config(
            'community_shield_safety.reporting_disclaimer',
            'Reporting guidance is informational. Platform procedures may change. Verify the platform\'s current reporting mechanism before submission.'
        );
    }
}
