import type {
  CommunityShieldContentType,
  CommunityShieldLanguage,
  CommunityShieldPlatform,
  CommunityShieldSafetyClassification,
  CommunityShieldStatus,
  CommunityShieldVisibility,
} from '@/types';

export type {
  CommunityShieldContentType,
  CommunityShieldLanguage,
  CommunityShieldPlatform,
  CommunityShieldSafetyClassification,
  CommunityShieldStatus,
  CommunityShieldVisibility,
};

export const PLATFORM_OPTIONS: Array<{ value: CommunityShieldPlatform; label: string }> = [
  { value: 'x', label: 'X' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'reddit', label: 'Reddit' },
  { value: 'discord', label: 'Discord' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'other', label: 'Other' },
];

export const CONTENT_TYPE_OPTIONS: Array<{ value: CommunityShieldContentType; label: string }> = [
  { value: 'post', label: 'Post' },
  { value: 'comment', label: 'Comment' },
  { value: 'video', label: 'Video' },
  { value: 'image', label: 'Image' },
  { value: 'message', label: 'Message' },
  { value: 'profile', label: 'Profile' },
  { value: 'thread', label: 'Thread' },
];

export const VISIBILITY_OPTIONS: Array<{
  value: CommunityShieldVisibility;
  label: string;
  hint: string;
}> = [
  {
    value: 'public',
    label: 'Public',
    hint: 'This content is publicly accessible.',
  },
  {
    value: 'group',
    label: 'Group / Community',
    hint: 'This content appears within a group or community.',
  },
  {
    value: 'private',
    label: 'Private / Direct',
    hint: 'This content was shared privately or in a direct conversation. Only provide information necessary for the report.',
  },
  {
    value: 'unknown',
    label: 'Unknown',
    hint: 'You are unsure how widely this content can be seen.',
  },
];

export const STATUS_OPTIONS: Array<{ value: CommunityShieldStatus; label: string }> = [
  { value: 'open', label: 'Open' },
  { value: 'reviewing', label: 'Reviewing' },
  { value: 'resolved', label: 'Resolved' },
];

export const LANGUAGE_OPTIONS: Array<{ value: CommunityShieldLanguage; label: string }> = [
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
  { value: 'fr', label: 'French' },
  { value: 'ur', label: 'Urdu' },
  { value: 'tr', label: 'Turkish' },
  { value: 'es', label: 'Spanish' },
  { value: 'bn', label: 'Bengali' },
  { value: 'id', label: 'Indonesian' },
  { value: 'ms', label: 'Malay' },
  { value: 'fa', label: 'Persian' },
  { value: 'so', label: 'Somali' },
  { value: 'sw', label: 'Swahili' },
  { value: 'de', label: 'German' },
  { value: 'nl', label: 'Dutch' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'hi', label: 'Hindi' },
  { value: 'other', label: 'Other' },
  { value: 'unknown', label: 'Unknown / Not sure' },
];

export const SAFETY_CLASSIFICATION_OPTIONS: Array<{
  value: CommunityShieldSafetyClassification;
  label: string;
}> = [
  { value: 'unclassified', label: 'Not classified' },
  { value: 'harassment', label: 'Harassment' },
  { value: 'hate', label: 'Hate / hateful conduct' },
  { value: 'threat', label: 'Threat' },
  { value: 'targeted_abuse', label: 'Targeted abuse' },
  { value: 'discrimination', label: 'Discrimination' },
  { value: 'incitement', label: 'Incitement' },
  { value: 'other', label: 'Other concern' },
];

const PLATFORM_CONTENT_HINTS: Record<CommunityShieldPlatform, string> = {
  x: 'Common examples: Post, Comment, Profile',
  youtube: 'Common examples: Video, Comment, Channel/Profile',
  tiktok: 'Common examples: Video, Comment, Profile',
  reddit: 'Common examples: Post, Comment, Profile, Thread',
  discord: 'Common examples: Message, Image, Video, Profile, Thread',
  telegram: 'Common examples: Message, Image, Video, Profile',
  whatsapp: 'Common examples: Message, Image, Video, Profile',
  other: 'Choose the content type that best matches what you saw.',
};

export function platformLabel(value: string): string {
  return PLATFORM_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function contentTypeLabel(value: string): string {
  return CONTENT_TYPE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function visibilityLabel(value: string): string {
  return VISIBILITY_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function statusLabel(value: string): string {
  return STATUS_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function languageLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Unknown / Not sure';
  }

  return LANGUAGE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function safetyClassificationLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Not classified';
  }

  return SAFETY_CLASSIFICATION_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function aiSignalLabel(value: string): string {
  return value
    .split('_')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function aiClassificationLabel(value: string): string {
  const known: Record<string, string> = {
    potential_harassment: 'Potential harassment',
    potential_hate: 'Potential hate',
    potential_coded_visual_hate: 'Potential coded/visual hate',
    potential_targeted_abuse: 'Potential targeted abuse',
    potential_threat: 'Potential threat',
    potential_discrimination: 'Potential discrimination',
    potential_incitement: 'Potential incitement',
    unclear: 'Unclear',
    no_clear_harm_signal: 'No clear harm signal',
  };

  return known[value] ?? aiSignalLabel(value);
}

export function aiConfidenceLabel(value: string): string {
  const known: Record<string, string> = {
    low: 'Low',
    moderate: 'Moderate',
    high: 'High',
  };

  return known[value] ?? value;
}

export function aiRecommendedActionLabel(value: string): string {
  const known: Record<string, string> = {
    human_review: 'Human review recommended',
    request_more_context: 'Additional context recommended before classification',
    no_immediate_action: 'No immediate action suggested',
  };

  return known[value] ?? aiSignalLabel(value);
}

export function reviewOutcomeLabel(value: string | null | undefined): string {
  if (!value) {
    return 'No determination yet';
  }

  const known: Record<string, string> = {
    confirmed: 'Confirmed',
    uncertain: 'Uncertain',
    closed: 'Closed',
  };

  return known[value] ?? value;
}

export function reviewActionLabel(value: string): string {
  const known: Record<string, string> = {
    started: 'Started review',
    confirmed: 'Confirmed',
    marked_uncertain: 'Marked uncertain',
    closed: 'Closed review',
    escalated: 'Escalated',
    context_requested: 'Requested additional context',
    context_fulfilled: 'Context added',
    context_cancelled: 'Cancelled context request',
    notes_updated: 'Updated notes',
  };

  return known[value] ?? aiSignalLabel(value);
}

export const HUMAN_CLASSIFICATION_OPTIONS = SAFETY_CLASSIFICATION_OPTIONS.filter(
  (option) => option.value !== 'unclassified',
);

export function platformContentHint(platform: CommunityShieldPlatform | ''): string {
  if (!platform) {
    return 'Select a platform to see common content examples.';
  }

  return PLATFORM_CONTENT_HINTS[platform];
}

export function toDatetimeLocalValue(iso: string | null | undefined): string {
  if (!iso) {
    return '';
  }

  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return '';
  }

  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function fromDatetimeLocalValue(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  const date = new Date(trimmed);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date.toISOString();
}

export const DESTINATION_PLATFORM_OPTIONS = [
  ...PLATFORM_OPTIONS,
  { value: 'campus_administration', label: 'Campus administration' },
  { value: 'university_office', label: 'University office' },
  { value: 'community_organization', label: 'Community organization' },
];

export const EXTERNAL_REPORT_STATUS_OPTIONS = [
  { value: 'reported', label: 'Reported' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'decision', label: 'Decision Recorded' },
  { value: 'outcome', label: 'Outcome Recorded' },
] as const;

export const EXTERNAL_REPORT_DECISION_OPTIONS = [
  { value: 'action_taken', label: 'Action Taken' },
  { value: 'no_action', label: 'No Action' },
  { value: 'content_does_not_violate_policy', label: 'Content Does Not Violate Policy' },
  { value: 'insufficient_information', label: 'Insufficient Information' },
  { value: 'other', label: 'Other' },
] as const;

export const EXTERNAL_REPORT_OUTCOME_OPTIONS = [
  { value: 'content_removed', label: 'Content Removed' },
  { value: 'content_restricted', label: 'Content Restricted' },
  { value: 'account_action', label: 'Account Action' },
  { value: 'no_action', label: 'No Action' },
  { value: 'warning', label: 'Warning' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'unable_to_determine', label: 'Unable to Determine' },
  { value: 'other', label: 'Other' },
] as const;

export const EXTERNAL_REPORT_SOURCE_OPTIONS = [
  { value: 'platform_response', label: 'Platform response' },
  { value: 'reporter_observation', label: 'Reporter observation' },
  { value: 'reviewer_observation', label: 'Reviewer observation' },
  { value: 'other', label: 'Other' },
] as const;

export const EXTERNAL_REPORT_VERIFICATION_OPTIONS = [
  { value: 'unverified', label: 'Unverified' },
  { value: 'reported_by_user', label: 'Reported by user' },
  { value: 'verified_by_reviewer', label: 'Verified by reviewer' },
] as const;

export function destinationPlatformLabel(value: string): string {
  return DESTINATION_PLATFORM_OPTIONS.find((option) => option.value === value)?.label ?? platformLabel(value);
}

export function externalReportStatusLabel(value: string): string {
  return EXTERNAL_REPORT_STATUS_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function externalReportDecisionLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Not yet recorded';
  }

  return EXTERNAL_REPORT_DECISION_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function externalReportOutcomeLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Not yet recorded';
  }

  return EXTERNAL_REPORT_OUTCOME_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function externalReportSourceLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Not provided';
  }

  return EXTERNAL_REPORT_SOURCE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function externalReportVerificationLabel(value: string | null | undefined): string {
  if (!value) {
    return 'Unverified';
  }

  return EXTERNAL_REPORT_VERIFICATION_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function appealStatusLabel(value: string): string {
  const known: Record<string, string> = {
    submitted: 'Submitted',
    under_review: 'Under Review',
    accepted: 'Accepted',
    rejected: 'Rejected',
    withdrawn: 'Withdrawn',
    resolved: 'Resolved',
  };

  return known[value] ?? value;
}
