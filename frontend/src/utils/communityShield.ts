export type CommunityShieldPlatform =
  | 'x'
  | 'youtube'
  | 'tiktok'
  | 'reddit'
  | 'discord'
  | 'telegram'
  | 'whatsapp'
  | 'other';

export type CommunityShieldContentType =
  | 'post'
  | 'comment'
  | 'video'
  | 'image'
  | 'message'
  | 'profile'
  | 'thread';

export type CommunityShieldVisibility = 'public' | 'group' | 'private' | 'unknown';

export type CommunityShieldStatus = 'open' | 'reviewing' | 'resolved';

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

export function platformContentHint(platform: CommunityShieldPlatform | ''): string {
  if (!platform) {
    return 'Select a platform to see common content examples.';
  }

  return PLATFORM_CONTENT_HINTS[platform];
}
