<?php

namespace Tests\Feature\Evaluation;

use App\Evaluation\CommunityShield\CommunityShieldEvaluationCase;
use App\Evaluation\CommunityShield\CommunityShieldEvaluationRunner;
use App\Evaluation\CommunityShield\SyntheticDataset;
use App\Services\AI\Providers\FakeAnalysisProvider;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CommunityShieldEvaluationRunnerTest extends TestCase
{
    use RefreshDatabase;

    private FakeAnalysisProvider $fakeProvider;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seedRbac();
        $this->fakeProvider = $this->app->make(FakeAnalysisProvider::class);
        $this->fakeProvider->reset();
    }

    public function test_synthetic_dataset_covers_required_categories_and_is_labeled(): void
    {
        $export = SyntheticDataset::export();

        $this->assertTrue($export['synthetic']);
        $this->assertSame(SyntheticDataset::VERSION, $export['version']);
        $this->assertGreaterThanOrEqual(35, $export['case_count']);
        $this->assertLessThanOrEqual(50, $export['case_count']);

        $categories = collect($export['cases'])->pluck('category')->unique()->sort()->values()->all();
        foreach (CommunityShieldEvaluationCase::categories() as $required) {
            $this->assertContains($required, $categories);
        }

        foreach ($export['cases'] as $case) {
            $this->assertTrue($case['synthetic']);
            $this->assertStringStartsWith('SYN-', $case['id']);
            $this->assertArrayHasKey('rationale', $case);
            $this->assertArrayHasKey('expected_uncertainty_behavior', $case);
            $this->assertFalse($case['expected_reporting_behavior']['automatic_submission']);
        }

        $platforms = collect($export['cases'])->pluck('platform')->unique();
        foreach (['x', 'youtube', 'tiktok', 'reddit', 'discord', 'telegram', 'whatsapp', 'other'] as $platform) {
            $this->assertTrue($platforms->contains($platform), "Missing platform coverage: {$platform}");
        }
    }

    public function test_deterministic_evaluation_runner_passes_all_safety_invariants(): void
    {
        /** @var CommunityShieldEvaluationRunner $runner */
        $runner = $this->app->make(CommunityShieldEvaluationRunner::class);

        $report = $runner->run([
            'live_ai' => false,
            'write_artifacts' => false,
            'pdf_sample_ids' => ['SYN-EXP-001', 'SYN-EXP-003'],
        ]);

        $this->assertSame('PASS', $report['result'], json_encode($report['failures'], JSON_PRETTY_PRINT));
        $this->assertSame(0, $report['critical_safety_failures']);
        $this->assertSame(SyntheticDataset::count(), $report['scenarios']);
        $this->assertSame('deterministic_fake_provider', $report['mode']);

        foreach ($report['categories'] as $category => $stats) {
            $this->assertSame('PASS', $stats['status'], "Category {$category} failed");
        }

        foreach ($report['invariants'] as $name => $status) {
            $this->assertSame('PASS', $status, "Invariant {$name} failed");
        }
    }

    public function test_artisan_evaluate_command_exits_zero_on_pass(): void
    {
        $this->artisan('community-shield:evaluate', ['--no-artifacts' => true])
            ->expectsOutputToContain('Community Shield Synthetic Safety Evaluation')
            ->expectsOutputToContain('RESULT: PASS')
            ->assertExitCode(0);
    }

    public function test_ambiguous_cases_require_high_uncertainty_and_human_attention(): void
    {
        $ambiguous = array_values(array_filter(
            SyntheticDataset::cases(),
            fn ($case) => $case->category() === CommunityShieldEvaluationCase::CATEGORY_AMBIGUOUS
        ));

        $this->assertNotEmpty($ambiguous);

        foreach ($ambiguous as $case) {
            $data = $case->toArray();
            $this->assertSame('high', $data['expected_uncertainty_behavior']['level'], $case->id());
            $this->assertTrue($data['expected_uncertainty_behavior']['must_not_assert_fact'], $case->id());
            $this->assertTrue($data['expected_human_review_behavior']['route_to_review'], $case->id());
            $this->assertTrue($data['expected_human_review_behavior']['allow_uncertain'], $case->id());
            $this->assertNotSame('confirmed', $data['expected_human_review_behavior']['preferred_outcome'] ?? 'uncertain', $case->id());
        }
    }
}
