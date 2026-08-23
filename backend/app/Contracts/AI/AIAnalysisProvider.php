<?php

namespace App\Contracts\AI;

use App\Models\Incident;

interface AIAnalysisProvider
{
    /**
     * Analyze a Community Shield incident using structured Phase 4 context.
     *
     * @param  array<string, mixed>  $context  Sanitized incident context payload
     * @return array{
     *     provider: string,
     *     model: string|null,
     *     prompt_version: string,
     *     analysis: array<string, mixed>
     * }
     *
     * @throws \App\Exceptions\AI\AIAnalysisException
     */
    public function analyzeIncident(Incident $incident, array $context): array;

    /**
     * Whether this provider is currently usable (credentials present, etc.).
     */
    public function isAvailable(): bool;

    public function providerName(): string;

    public function modelName(): ?string;
}
