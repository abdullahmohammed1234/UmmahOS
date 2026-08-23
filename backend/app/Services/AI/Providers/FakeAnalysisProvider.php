<?php

namespace App\Services\AI\Providers;

use App\Contracts\AI\AIAnalysisProvider;
use App\Exceptions\AI\AIAnalysisException;
use App\Models\Incident;
use App\Prompts\CommunityShieldContextAnalysisV1;
use App\Services\AI\AnalysisResultValidator;

/**
 * Deterministic provider for automated tests. Never calls an external API.
 */
class FakeAnalysisProvider implements AIAnalysisProvider
{
    /** @var callable|null */
    private $handler = null;

    private bool $shouldFail = false;

    private bool $returnMalformed = false;

    public function __construct(
        private readonly AnalysisResultValidator $validator,
    ) {}

    public function respondWith(callable $handler): self
    {
        $this->handler = $handler;
        $this->shouldFail = false;
        $this->returnMalformed = false;

        return $this;
    }

    public function fail(): self
    {
        $this->shouldFail = true;
        $this->returnMalformed = false;
        $this->handler = null;

        return $this;
    }

    public function returnMalformed(): self
    {
        $this->returnMalformed = true;
        $this->shouldFail = false;
        $this->handler = null;

        return $this;
    }

    public function reset(): self
    {
        $this->handler = null;
        $this->shouldFail = false;
        $this->returnMalformed = false;

        return $this;
    }

    public function isAvailable(): bool
    {
        return true;
    }

    public function providerName(): string
    {
        return 'fake';
    }

    public function modelName(): ?string
    {
        return 'fake-model';
    }

    public function analyzeIncident(Incident $incident, array $context): array
    {
        if ($this->shouldFail) {
            throw AIAnalysisException::providerFailed('AI analysis unavailable.');
        }

        if ($this->returnMalformed) {
            throw AIAnalysisException::malformedResponse('The AI provider returned an invalid analysis.');
        }

        $payload = is_callable($this->handler)
            ? ($this->handler)($incident, $context)
            : $this->defaultAnalysis($context);

        if (! is_array($payload)) {
            throw AIAnalysisException::malformedResponse('The AI provider returned an invalid analysis.');
        }

        $analysis = $this->validator->validate($payload);

        return [
            'provider' => $this->providerName(),
            'model' => $this->modelName(),
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'analysis' => $analysis,
        ];
    }

    /**
     * @param  array<string, mixed>  $context
     * @return array<string, mixed>
     */
    private function defaultAnalysis(array $context): array
    {
        $hasContent = ($context['original_item']['content'] ?? 'Not provided') !== 'Not provided'
            || ($context['description'] ?? '') !== '';

        if (! $hasContent) {
            return [
                'signals' => [
                    [
                        'name' => 'no_clear_signal',
                        'description' => 'Insufficient evidence was provided to identify a potential harm signal.',
                        'evidence' => ['Original item content was not provided.'],
                        'confidence' => 'low',
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
                'alternative_interpretation' => null,
                'recommended_action' => [
                    'type' => 'request_more_context',
                    'reason' => 'Additional context recommended before classification.',
                ],
            ];
        }

        return [
            'signals' => [
                [
                    'name' => 'contextual_ambiguity',
                    'description' => 'The supplied context may support more than one interpretation.',
                    'evidence' => ['Reviewer should compare original item, replies, and related copies.'],
                    'confidence' => 'moderate',
                ],
            ],
            'classification' => [
                'label' => 'unclear',
                'confidence' => 'moderate',
            ],
            'uncertainty' => [
                'level' => 'moderate',
                'explanation' => 'Moderate uncertainty — additional human review is needed before classification.',
            ],
            'alternative_interpretation' => 'The reported content may be quoting another participant rather than expressing the author\'s own position.',
            'recommended_action' => [
                'type' => 'human_review',
                'reason' => 'Human review recommended.',
            ],
        ];
    }
}
