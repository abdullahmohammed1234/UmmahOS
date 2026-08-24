<?php

namespace Tests\Fixtures\CommunityShieldEvaluation;

use App\Evaluation\CommunityShield\CommunityShieldEvaluationCase;
use App\Evaluation\CommunityShield\SyntheticDataset;

/**
 * Test fixture pointer to the versioned synthetic evaluation dataset.
 *
 * @see \App\Evaluation\CommunityShield\SyntheticDataset
 */
final class SyntheticEvaluationFixtures
{
    /**
     * @return list<CommunityShieldEvaluationCase>
     */
    public static function cases(): array
    {
        return SyntheticDataset::cases();
    }

    public static function count(): int
    {
        return SyntheticDataset::count();
    }

    /**
     * @return array<string, mixed>
     */
    public static function export(): array
    {
        return SyntheticDataset::export();
    }
}
