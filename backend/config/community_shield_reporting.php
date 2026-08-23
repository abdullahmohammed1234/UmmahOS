<?php

/**
 * Informational platform reporting guidance for Community Shield evidence packages.
 *
 * Guidance is non-authoritative. Platform procedures change; reviewers must verify
 * the current reporting mechanism before any external submission.
 *
 * Phase 7 does not submit reports to external platforms.
 */

return [
    'disclaimer' => 'Reporting guidance is informational. Platform procedures may change. Verify the platform\'s current reporting mechanism before submission.',

    'platforms' => [
        'x' => [
            'label' => 'X',
            'recommended_route' => 'Use the platform\'s current in-app reporting mechanism for the original post or account.',
            'general_instructions' => 'Attach or reference the original item URL and relevant surrounding context from this evidence package when using the platform\'s reporting flow. Do not automatically submit anything from UmmahOS.',
            'safety_notes' => 'Avoid redistributing harmful content beyond what the reporting channel requires.',
            'privacy_notes' => 'Share only the evidence needed for the report. Remove unrelated personal information before external submission.',
            'last_reviewed' => '2026-08-22',
        ],
        'youtube' => [
            'label' => 'YouTube',
            'recommended_route' => 'Use YouTube\'s current reporting mechanism for the relevant video, comment, or channel.',
            'general_instructions' => 'Include the captured reference URL and enough surrounding context from this package to identify the reported item. Confirm the current reporting options in the YouTube interface.',
            'safety_notes' => 'Do not download or re-upload harmful media solely for redistribution.',
            'privacy_notes' => 'Omit unrelated channel or account details that are not required for the report.',
            'last_reviewed' => '2026-08-22',
        ],
        'tiktok' => [
            'label' => 'TikTok',
            'recommended_route' => 'Use TikTok\'s current reporting mechanism for the relevant video, comment, or account.',
            'general_instructions' => 'Provide the captured reference and context from this evidence package. Verify TikTok\'s current in-app reporting options before submission.',
            'safety_notes' => 'Avoid publicly resharing the reported content outside the reporting process.',
            'privacy_notes' => 'Limit shared details to what is necessary to identify the reported item.',
            'last_reviewed' => '2026-08-22',
        ],
        'reddit' => [
            'label' => 'Reddit',
            'recommended_route' => 'Use Reddit\'s current reporting mechanism for the post, comment, or community.',
            'general_instructions' => 'Include the captured reference URL and surrounding context. Confirm whether report, modmail, or other community channels are appropriate for the situation.',
            'safety_notes' => 'Do not cross-post harmful content into unrelated communities for visibility.',
            'privacy_notes' => 'Avoid exposing private reporter details when using public or community channels.',
            'last_reviewed' => '2026-08-22',
        ],
        'discord' => [
            'label' => 'Discord',
            'recommended_route' => 'Report the relevant message, user, or server through Discord\'s available reporting process.',
            'general_instructions' => 'Use message IDs, channel context, and captured text from this package where available. Verify Discord\'s current Trust & Safety reporting options before submission.',
            'safety_notes' => 'Do not expose private community information unnecessarily outside the reporting channel.',
            'privacy_notes' => 'Private server content may require extra care; share only what the reporting process needs.',
            'last_reviewed' => '2026-08-22',
        ],
        'telegram' => [
            'label' => 'Telegram',
            'recommended_route' => 'Use Telegram\'s current reporting mechanism for the message, channel, or group.',
            'general_instructions' => 'Include captured message content and any available reference from this package. Confirm Telegram\'s current reporting options in the client before submission.',
            'safety_notes' => 'Private chats and invite-only groups may contain sensitive participant information.',
            'privacy_notes' => 'Do not forward private chat content more widely than necessary for reporting.',
            'last_reviewed' => '2026-08-22',
        ],
        'whatsapp' => [
            'label' => 'WhatsApp',
            'recommended_route' => 'Use WhatsApp\'s current reporting mechanism for the message, account, or group.',
            'general_instructions' => 'Include the captured message content and surrounding context from this package. Verify WhatsApp\'s current in-app reporting options before submission.',
            'safety_notes' => 'Private message content should not be publicly redistributed.',
            'privacy_notes' => 'Phone numbers and contact identity are sensitive; omit them unless required by the reporting channel.',
            'last_reviewed' => '2026-08-22',
        ],
        'other' => [
            'label' => 'Other',
            'recommended_route' => 'Review the relevant platform\'s current safety/reporting mechanism and attach the evidence package where appropriate.',
            'general_instructions' => 'No platform-specific workflow is provided for unclassified platforms. Use the captured evidence carefully and confirm the destination channel before sharing.',
            'safety_notes' => 'Treat unknown platforms as untrusted destinations until verified.',
            'privacy_notes' => 'Minimize personal information when the reporting channel is unfamiliar.',
            'last_reviewed' => '2026-08-22',
        ],
    ],
];
