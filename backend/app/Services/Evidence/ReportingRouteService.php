<?php

namespace App\Services\Evidence;

use App\Models\Incident;

class ReportingRouteService
{
    /**
     * @return array{
     *     platform: string,
     *     platform_label: string,
     *     recommended_route: string,
     *     general_instructions: string,
     *     safety_notes: string,
     *     privacy_notes: string,
     *     last_reviewed: string|null,
     *     disclaimer: string,
     *     automatic_submission: false
     * }
     */
    public function forPlatform(string $platform): array
    {
        $key = in_array($platform, Incident::platforms(), true)
            ? $platform
            : Incident::PLATFORM_OTHER;

        $platforms = config('community_shield_reporting.platforms', []);
        $entry = $platforms[$key] ?? $platforms[Incident::PLATFORM_OTHER] ?? [];

        return [
            'platform' => $key,
            'platform_label' => (string) ($entry['label'] ?? ucfirst($key)),
            'recommended_route' => (string) ($entry['recommended_route'] ?? 'Review the relevant platform\'s current safety/reporting mechanism and attach the evidence package where appropriate.'),
            'general_instructions' => (string) ($entry['general_instructions'] ?? ''),
            'safety_notes' => (string) ($entry['safety_notes'] ?? ''),
            'privacy_notes' => (string) ($entry['privacy_notes'] ?? ''),
            'last_reviewed' => isset($entry['last_reviewed']) ? (string) $entry['last_reviewed'] : null,
            'disclaimer' => (string) config(
                'community_shield_reporting.disclaimer',
                'Reporting guidance is informational. Platform procedures may change.'
            ),
            'automatic_submission' => false,
        ];
    }
}
