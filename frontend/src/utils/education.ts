import type { LearningPatternType } from '@/types';

export const LEARNING_PATTERN_TYPE_OPTIONS: Array<{ value: LearningPatternType; label: string }> = [
  { value: 'religious_targeting', label: 'Religious targeting' },
  { value: 'coded_language', label: 'Coded language' },
  { value: 'repeated_harassment', label: 'Repeated harassment' },
  { value: 'contextual_hate', label: 'Contextual hate' },
  { value: 'visual_hate', label: 'Visual hate' },
  { value: 'dog_whistle', label: 'Dog whistle' },
  { value: 'coordinated_behavior', label: 'Coordinated behavior' },
  { value: 'misinformation_related_harm', label: 'Misinformation-related harm' },
  { value: 'reporting_safety', label: 'Reporting safety' },
  { value: 'other', label: 'Other' },
];

export const LEARNING_PATTERN_FORM_FIELDS = [
  'pattern_type',
  'title',
  'summary',
  'learning_objective',
  'domain',
] as const;

export const ADAPT_UNAVAILABLE_MESSAGE =
  'Adaptive practice is temporarily unavailable. You can continue with the lesson.';

export function patternTypeLabel(value: string): string {
  return LEARNING_PATTERN_TYPE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

export function formatAdaptBlock(value: unknown): string {
  if (value == null) {
    return '';
  }

  if (typeof value === 'string') {
    return value;
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value
      .map((entry) => {
        if (entry && typeof entry === 'object' && 'text' in entry) {
          return String((entry as { text: unknown }).text);
        }
        return formatAdaptBlock(entry);
      })
      .filter(Boolean)
      .join('\n');
  }

  if (typeof value === 'object') {
    const record = value as Record<string, unknown>;
    const preferred =
      record.body ?? record.text ?? record.headline ?? record.detail ?? record.message;
    if (typeof preferred === 'string') {
      return preferred;
    }
    if (Array.isArray(record.bullets)) {
      return formatAdaptBlock(record.bullets);
    }
  }

  return '';
}
