<?php

namespace App\Services\Adapt;

use App\Contracts\Adapt\AdaptClient;
use App\Dto\Adapt\AdaptFeedbackResponse;
use App\Dto\Adapt\AdaptSessionResponse;
use App\Exceptions\Adapt\AdaptUnavailableException;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Http;
use Throwable;

class HttpAdaptClient implements AdaptClient
{
    public function isAvailable(): bool
    {
        try {
            $response = Http::baseUrl($this->baseUrl())
                ->timeout(3)
                ->acceptJson()
                ->get('/api/health');

            return $response->successful();
        } catch (Throwable) {
            return false;
        }
    }

    public function createSession(
        string $topicId,
        string $learnerId,
        ?string $subjectId = null,
        ?string $initialChallengeId = null,
        int $maxSteps = 10
    ): AdaptSessionResponse {
        $payload = array_filter([
            'topic_id' => $topicId,
            'learner_id' => $learnerId,
            'subject_id' => $subjectId,
            'initial_challenge' => $initialChallengeId,
            'max_steps' => $maxSteps,
            'mode' => 'learner',
        ], fn ($value) => $value !== null && $value !== '');

        return AdaptSessionResponse::fromArray(
            $this->request('post', '/api/sessions', $payload)
        );
    }

    public function getSession(string $sessionId): AdaptSessionResponse
    {
        return AdaptSessionResponse::fromArray(
            $this->request('get', '/api/sessions/'.$sessionId)
        );
    }

    public function submitResponse(
        string $sessionId,
        string $answer,
        int $confidence,
        ?string $reasoning = null,
        ?string $challengeId = null
    ): AdaptFeedbackResponse {
        $payload = array_filter([
            'answer' => $answer,
            'confidence' => $confidence,
            'reasoning' => $reasoning,
            'explanation' => $reasoning,
            'challenge_id' => $challengeId,
        ], fn ($value) => $value !== null && $value !== '');

        return AdaptFeedbackResponse::fromArray(
            $this->request('post', '/api/sessions/'.$sessionId.'/responses', $payload)
        );
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    private function request(string $method, string $path, array $payload = []): array
    {
        try {
            $pending = Http::baseUrl($this->baseUrl())
                ->timeout((int) config('adapt.timeout', 10))
                ->acceptJson();

            $response = $method === 'get'
                ? $pending->get($path)
                : $pending->{$method}($path, $payload);

            if (! $response->successful()) {
                throw AdaptUnavailableException::serviceDown(
                    'ADAPT returned HTTP '.$response->status()
                );
            }

            $json = $response->json();

            return is_array($json) ? $json : [];
        } catch (AdaptUnavailableException $e) {
            throw $e;
        } catch (ConnectionException $e) {
            throw AdaptUnavailableException::serviceDown($e->getMessage());
        } catch (Throwable $e) {
            throw AdaptUnavailableException::serviceDown($e->getMessage());
        }
    }

    private function baseUrl(): string
    {
        return rtrim((string) config('adapt.base_url', 'http://127.0.0.1:8765'), '/');
    }
}
