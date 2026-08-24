<?php

namespace App\Console\Commands;

use App\Contracts\AI\AIAnalysisProvider;
use App\Evaluation\CommunityShield\CommunityShieldEvaluationCase;
use App\Evaluation\CommunityShield\CommunityShieldEvaluationRunner;
use App\Evaluation\CommunityShield\SyntheticDataset;
use App\Services\AI\IncidentAiAnalysisService;
use App\Services\AI\Providers\FakeAnalysisProvider;
use Illuminate\Console\Command;

class CommunityShieldEvaluateCommand extends Command
{
    protected $signature = 'community-shield:evaluate
                            {--live-ai : Optional demo mode using the configured live AI provider on synthetic data only}
                            {--no-artifacts : Skip writing docs/evaluation artifacts}';

    protected $description = 'Run the Community Shield synthetic safety evaluation (deterministic by default)';

    public function handle(): int
    {
        $liveAi = (bool) $this->option('live-ai');

        $this->newLine();
        $this->info('Community Shield Synthetic Safety Evaluation');
        $this->line(SyntheticDataset::LABEL);
        $this->line('Dataset version: '.SyntheticDataset::VERSION);
        $this->line('Scenarios: '.SyntheticDataset::count());
        $this->line('Mode: '.($liveAi ? 'live_ai_optional (synthetic inputs only)' : 'deterministic_fake_provider'));
        $this->newLine();

        if ($liveAi) {
            $this->warn('Live AI mode is optional and demo-only.');
            $this->warn('Safety properties are enforced by architecture + regression tests, not by LLM responses.');
            $this->warn('Never uses real incidents or personal data.');
            $this->newLine();
        } else {
            // Force fake provider before resolving the runner so CLI runs stay deterministic.
            config(['ai.provider' => 'fake']);
            $this->laravel->forgetInstance(AIAnalysisProvider::class);
            $this->laravel->forgetInstance(IncidentAiAnalysisService::class);
            $this->laravel->forgetInstance(CommunityShieldEvaluationRunner::class);
            $this->laravel->instance(
                AIAnalysisProvider::class,
                $this->laravel->make(FakeAnalysisProvider::class)
            );
        }

        /** @var CommunityShieldEvaluationRunner $runner */
        $runner = $this->laravel->make(CommunityShieldEvaluationRunner::class);

        $report = $runner->run([
            'live_ai' => $liveAi,
            'write_artifacts' => ! $this->option('no-artifacts'),
        ]);

        $this->printCategoryTable($report);
        $this->newLine();
        $this->printInvariantTable($report);
        $this->newLine();

        $this->line('Critical safety failures: '.$report['critical_safety_failures']);
        $this->line('RESULT: '.$report['result']);
        $this->newLine();
        $this->comment($report['disclaimer']);

        if (($report['failures'] ?? []) !== []) {
            $this->newLine();
            $this->error('Failed scenarios:');
            foreach ($report['failures'] as $failure) {
                $this->line(' - '.$failure['scenario_id'].': '.implode(' | ', $failure['failures']));
            }
        }

        return $report['result'] === 'PASS' && (int) $report['critical_safety_failures'] === 0
            ? self::SUCCESS
            : self::FAILURE;
    }

    /**
     * @param  array<string, mixed>  $report
     */
    private function printCategoryTable(array $report): void
    {
        $labels = [
            CommunityShieldEvaluationCase::CATEGORY_EXPLICIT => 'Explicit',
            CommunityShieldEvaluationCase::CATEGORY_CODED => 'Coded',
            CommunityShieldEvaluationCase::CATEGORY_VISUAL => 'Visual',
            CommunityShieldEvaluationCase::CATEGORY_RELATIONAL => 'Relational / Reply Swarm',
            CommunityShieldEvaluationCase::CATEGORY_MISINFORMATION => 'Misinformation',
            CommunityShieldEvaluationCase::CATEGORY_SYNTHETIC_AI => 'Synthetic AI Content',
            CommunityShieldEvaluationCase::CATEGORY_AMBIGUOUS => 'Ambiguous / Uncertain',
        ];

        foreach ($labels as $key => $label) {
            $status = $report['categories'][$key]['status'] ?? 'FAIL';
            $this->line(sprintf('%-28s %s', $label, $status));
        }
    }

    /**
     * @param  array<string, mixed>  $report
     */
    private function printInvariantTable(array $report): void
    {
        $labels = [
            'context_preservation' => 'Context preservation',
            'uncertainty_handling' => 'Uncertainty handling',
            'human_routing' => 'Human routing',
            'privacy_protection' => 'Privacy protection',
            'evidence_reporting' => 'Evidence reporting',
            'outcome_tracking' => 'Outcome tracking',
            'harmful_claim_avoidance' => 'Harmful-claim avoidance',
        ];

        foreach ($labels as $key => $label) {
            $status = $report['invariants'][$key] ?? 'FAIL';
            $this->line(sprintf('%-28s %s', $label, $status));
        }
    }
}
