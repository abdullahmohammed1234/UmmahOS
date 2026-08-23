<?php

namespace App\Services\AI;

use App\Exceptions\AI\AIAnalysisException;

/**
 * Validates structured AI analysis packages before persistence.
 */
class AnalysisResultValidator
{
    private const CONFIDENCE_LEVELS = ['low', 'moderate', 'high'];

    private const UNCERTAINTY_LEVELS = ['low', 'moderate', 'high'];

    private const RECOMMENDED_ACTIONS = [
        'human_review',
        'request_more_context',
        'no_immediate_action',
    ];

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     *
     * @throws AIAnalysisException
     */
    public function validate(array $payload): array
    {
        if (! isset($payload['signals']) || ! is_array($payload['signals'])) {
            throw AIAnalysisException::malformedResponse('Missing or invalid signals.');
        }

        if (! isset($payload['classification']) || ! is_array($payload['classification'])) {
            throw AIAnalysisException::malformedResponse('Missing or invalid classification.');
        }

        if (! isset($payload['uncertainty']) || ! is_array($payload['uncertainty'])) {
            throw AIAnalysisException::malformedResponse('Missing or invalid uncertainty.');
        }

        if (! isset($payload['recommended_action']) || ! is_array($payload['recommended_action'])) {
            throw AIAnalysisException::malformedResponse('Missing or invalid recommended_action.');
        }

        $signals = [];
        foreach ($payload['signals'] as $signal) {
            if (! is_array($signal)) {
                throw AIAnalysisException::malformedResponse('Each signal must be an object.');
            }

            $name = $signal['name'] ?? null;
            $description = $signal['description'] ?? null;
            $evidence = $signal['evidence'] ?? [];
            $confidence = strtolower((string) ($signal['confidence'] ?? ''));

            if (! is_string($name) || $name === '') {
                throw AIAnalysisException::malformedResponse('Signal name is required.');
            }

            if (! is_string($description) || $description === '') {
                throw AIAnalysisException::malformedResponse('Signal description is required.');
            }

            if (! is_array($evidence)) {
                throw AIAnalysisException::malformedResponse('Signal evidence must be an array.');
            }

            if (! in_array($confidence, self::CONFIDENCE_LEVELS, true)) {
                throw AIAnalysisException::malformedResponse('Signal confidence is invalid.');
            }

            $signals[] = [
                'name' => $name,
                'description' => $description,
                'evidence' => array_values(array_map(
                    static fn ($item) => is_scalar($item) ? (string) $item : '',
                    $evidence
                )),
                'confidence' => $confidence,
            ];
        }

        $label = $payload['classification']['label'] ?? null;
        $classificationConfidence = strtolower((string) ($payload['classification']['confidence'] ?? ''));

        if (! is_string($label) || $label === '') {
            throw AIAnalysisException::malformedResponse('Classification label is required.');
        }

        if (! in_array($classificationConfidence, self::CONFIDENCE_LEVELS, true)) {
            throw AIAnalysisException::malformedResponse('Classification confidence is invalid.');
        }

        $uncertaintyLevel = strtolower((string) ($payload['uncertainty']['level'] ?? ''));
        $uncertaintyExplanation = $payload['uncertainty']['explanation'] ?? null;

        if (! in_array($uncertaintyLevel, self::UNCERTAINTY_LEVELS, true)) {
            throw AIAnalysisException::malformedResponse('Uncertainty level is invalid.');
        }

        if (! is_string($uncertaintyExplanation) || $uncertaintyExplanation === '') {
            throw AIAnalysisException::malformedResponse('Uncertainty explanation is required.');
        }

        $actionType = $payload['recommended_action']['type'] ?? null;
        $actionReason = $payload['recommended_action']['reason'] ?? null;

        if (! is_string($actionType) || ! in_array($actionType, self::RECOMMENDED_ACTIONS, true)) {
            throw AIAnalysisException::malformedResponse('Recommended action type is invalid.');
        }

        if (! is_string($actionReason) || $actionReason === '') {
            throw AIAnalysisException::malformedResponse('Recommended action reason is required.');
        }

        $alternative = $payload['alternative_interpretation'] ?? null;
        if ($alternative !== null && ! is_string($alternative)) {
            throw AIAnalysisException::malformedResponse('Alternative interpretation must be a string or null.');
        }

        return [
            'signals' => $signals,
            'classification' => [
                'label' => $label,
                'confidence' => $classificationConfidence,
            ],
            'uncertainty' => [
                'level' => $uncertaintyLevel,
                'explanation' => $uncertaintyExplanation,
            ],
            'alternative_interpretation' => $alternative !== null && $alternative !== ''
                ? $alternative
                : null,
            'recommended_action' => [
                'type' => $actionType,
                'reason' => $actionReason,
            ],
        ];
    }
}
