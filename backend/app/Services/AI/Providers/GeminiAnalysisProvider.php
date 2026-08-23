<?php

namespace App\Services\AI\Providers;

use App\Contracts\AI\AIAnalysisProvider;
use App\Exceptions\AI\AIAnalysisException;
use App\Models\Incident;
use App\Prompts\CommunityShieldContextAnalysisV1;
use App\Services\AI\AnalysisResultValidator;
use Illuminate\Support\Facades\Http;
use Throwable;

class GeminiAnalysisProvider implements AIAnalysisProvider
{
    public function __construct(
        private readonly AnalysisResultValidator $validator,
    ) {}

    public function isAvailable(): bool
    {
        return filled(config('ai.gemini.api_key'));
    }

    public function providerName(): string
    {
        return 'gemini';
    }

    public function modelName(): ?string
    {
        $model = config('ai.gemini.model');

        return filled($model) ? (string) $model : null;
    }

    public function analyzeIncident(Incident $incident, array $context): array
    {
        if (! $this->isAvailable()) {
            throw AIAnalysisException::unavailable();
        }

        $apiKey = (string) config('ai.gemini.api_key');
        $model = (string) config('ai.gemini.model');
        $endpoint = rtrim((string) config('ai.gemini.endpoint'), '/');
        $timeout = (int) config('ai.gemini.timeout', 45);

        $url = "{$endpoint}/models/{$model}:generateContent";

        $system = CommunityShieldContextAnalysisV1::systemInstructions()."\n\n"
            .CommunityShieldContextAnalysisV1::outputSchemaDescription();

        try {
            $response = Http::timeout($timeout)
                ->withHeaders([
                    'Content-Type' => 'application/json',
                    'x-goog-api-key' => $apiKey,
                ])
                ->post($url, [
                    'systemInstruction' => [
                        'parts' => [
                            ['text' => $system],
                        ],
                    ],
                    'contents' => [
                        [
                            'role' => 'user',
                            'parts' => [
                                ['text' => CommunityShieldContextAnalysisV1::userMessage($context)],
                            ],
                        ],
                    ],
                    'generationConfig' => [
                        'temperature' => 0.2,
                        'responseMimeType' => 'application/json',
                    ],
                ]);
        } catch (Throwable $e) {
            report($e);

            throw AIAnalysisException::providerFailed('AI analysis unavailable.');
        }

        if (! $response->successful()) {
            throw AIAnalysisException::providerFailed('AI analysis unavailable.');
        }

        $text = data_get($response->json(), 'candidates.0.content.parts.0.text');

        if (! is_string($text) || trim($text) === '') {
            throw AIAnalysisException::malformedResponse('The AI provider returned an empty analysis.');
        }

        $decoded = $this->decodeJson($text);
        $analysis = $this->validator->validate($decoded);

        return [
            'provider' => $this->providerName(),
            'model' => $model,
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'analysis' => $analysis,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function decodeJson(string $text): array
    {
        $trimmed = trim($text);

        if (str_starts_with($trimmed, '```')) {
            $trimmed = preg_replace('/^```(?:json)?\s*/i', '', $trimmed) ?? $trimmed;
            $trimmed = preg_replace('/\s*```$/', '', $trimmed) ?? $trimmed;
            $trimmed = trim($trimmed);
        }

        $decoded = json_decode($trimmed, true);

        if (! is_array($decoded)) {
            throw AIAnalysisException::malformedResponse('The AI provider returned invalid JSON.');
        }

        return $decoded;
    }
}
