<?php

namespace App\Services\AI;

use App\Contracts\AI\AIAnalysisProvider;
use App\Exceptions\AI\AIAnalysisException;
use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\User;
use App\Prompts\CommunityShieldContextAnalysisV1;
use Illuminate\Database\Eloquent\Collection;
use Throwable;

class IncidentAiAnalysisService
{
    public function __construct(
        private readonly AIAnalysisProvider $provider,
        private readonly CommunityShieldContextBuilder $contextBuilder,
    ) {}

    /**
     * @return Collection<int, IncidentAiAnalysis>
     */
    public function listForIncident(Incident $incident): Collection
    {
        return $incident->aiAnalyses()
            ->with('requester')
            ->orderByDesc('id')
            ->get();
    }

    public function findForIncident(Incident $incident, int $analysisId): IncidentAiAnalysis
    {
        return $incident->aiAnalyses()
            ->with('requester')
            ->whereKey($analysisId)
            ->firstOrFail();
    }

    /**
     * Create a new analysis record and run the provider synchronously.
     *
     * Does not mutate human classification or incident status.
     * Does not overwrite previous analyses — each request creates a new record.
     */
    public function requestAnalysis(Incident $incident, User $requester): IncidentAiAnalysis
    {
        $analysis = $incident->aiAnalyses()->create([
            'provider' => $this->provider->providerName(),
            'model' => $this->provider->modelName(),
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_QUEUED,
            'analysis' => null,
            'error_message' => null,
            'requested_by' => $requester->id,
        ]);

        $analysis->update(['status' => IncidentAiAnalysis::STATUS_RUNNING]);

        try {
            $context = $this->contextBuilder->build($incident);
            $result = $this->provider->analyzeIncident($incident, $context);

            $analysis->update([
                'provider' => $result['provider'],
                'model' => $result['model'],
                'prompt_version' => $result['prompt_version'],
                'status' => IncidentAiAnalysis::STATUS_COMPLETED,
                'analysis' => $result['analysis'],
                'error_message' => null,
            ]);
        } catch (AIAnalysisException $e) {
            $analysis->update([
                'status' => IncidentAiAnalysis::STATUS_FAILED,
                'analysis' => null,
                'error_message' => $this->safeErrorMessage($e->getMessage()),
            ]);
        } catch (Throwable $e) {
            report($e);

            $analysis->update([
                'status' => IncidentAiAnalysis::STATUS_FAILED,
                'analysis' => null,
                'error_message' => 'AI analysis unavailable.',
            ]);
        }

        return $analysis->fresh(['requester']);
    }

    public function providerAvailable(): bool
    {
        return $this->provider->isAvailable();
    }

    private function safeErrorMessage(string $message): string
    {
        $message = trim($message);

        if ($message === '') {
            return 'AI analysis unavailable.';
        }

        if (preg_match('/api[_-]?key|token|secret|authorization/i', $message)) {
            return 'AI analysis unavailable.';
        }

        return $message;
    }
}
