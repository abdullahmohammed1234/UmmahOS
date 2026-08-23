<?php

namespace App\Services\AI\Providers;

use App\Contracts\AI\AIAnalysisProvider;
use App\Exceptions\AI\AIAnalysisException;
use App\Models\Incident;

/**
 * Used when no AI credentials are configured. Fails honestly without fabricating analysis.
 */
class UnavailableAnalysisProvider implements AIAnalysisProvider
{
    public function isAvailable(): bool
    {
        return false;
    }

    public function providerName(): string
    {
        return 'unavailable';
    }

    public function modelName(): ?string
    {
        return null;
    }

    public function analyzeIncident(Incident $incident, array $context): array
    {
        throw AIAnalysisException::unavailable();
    }
}
