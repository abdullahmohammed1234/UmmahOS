<template>
  <section class="queue-workspace" data-testid="review-queue-page">
    <header class="review-workspace-header">
      <p class="eyebrow">Community Shield</p>
      <h1>Review Queue</h1>
      <p class="lede muted">
        Open reviews for {{ organization.currentOrganization?.name ?? 'this organization' }}.
        AI-assisted triage is advisory — a human reviewer decides.
      </p>
    </header>

    <p v-if="!organization.canReviewIncidents" class="error" data-testid="review-denied">
      You cannot access the Community Safety Review queue in this organization.
    </p>

    <template v-else>
      <form class="queue-filters" data-testid="review-filters" aria-label="Review queue filters" @submit.prevent>
        <label class="field">
          <span>Status</span>
          <select v-model="filters.status" data-testid="filter-status">
            <option value="">All</option>
            <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>Platform</span>
          <select v-model="filters.platform" data-testid="filter-platform">
            <option value="">All</option>
            <option v-for="option in PLATFORM_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>AI confidence</span>
          <select v-model="filters.confidence" data-testid="filter-confidence">
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </label>
        <label class="field">
          <span>Uncertainty</span>
          <select v-model="filters.uncertainty" data-testid="filter-uncertainty">
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </label>
        <label class="field">
          <span>Classification</span>
          <select v-model="filters.classification" data-testid="filter-classification">
            <option value="">All</option>
            <option
              v-for="option in SAFETY_CLASSIFICATION_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </label>
      </form>

      <LoadingState v-if="isLoading" message="Loading open reviews…" />
      <EmptyState
        v-else-if="error"
        title="Unable to load queue"
        :description="error"
      />
      <EmptyState
        v-else-if="items.length === 0"
        title="No reports match"
        description="Try adjusting your filters or check back later."
      />

      <template v-else>
        <section v-if="completedStories.length > 0" class="queue-section" data-testid="completed-stories">
          <h2 class="queue-section-title">Complete demo stories</h2>
          <p class="muted queue-section-hint">
            Confirmed reviews with full context, AI analysis, evidence, and outcomes — ideal for walkthroughs.
          </p>
          <ul class="queue-list">
            <li
              v-for="item in completedStories"
              :key="`complete-${item.id}`"
              class="queue-case queue-case-featured"
              data-testid="review-queue-item"
            >
              <div class="queue-case-body">
                <p class="queue-case-ref">#{{ item.id }}</p>
                <div class="queue-indicators">
                  <span class="queue-indicator">{{ platformLabel(item.platform) }}</span>
                  <span class="queue-indicator">{{ contentTypeLabel(item.content_type) }}</span>
                  <span class="queue-indicator">{{ visibilityLabel(item.visibility) }}</span>
                  <span class="queue-indicator">{{ statusLabel(item.status) }}</span>
                  <span v-if="item.review_outcome" class="queue-indicator confidence-high">
                    {{ reviewOutcomeLabel(item.review_outcome) }}
                  </span>
                  <span
                    v-if="item.ai_assisted_triage.confidence"
                    class="queue-indicator"
                    :class="confidenceClass(item.ai_assisted_triage.confidence)"
                  >
                    {{ aiConfidenceLabel(item.ai_assisted_triage.confidence) }} confidence
                  </span>
                  <span
                    v-if="item.ai_assisted_triage.uncertainty"
                    class="queue-indicator"
                    :class="uncertaintyClass(item.ai_assisted_triage.uncertainty)"
                  >
                    {{ aiConfidenceLabel(item.ai_assisted_triage.uncertainty) }} uncertainty
                  </span>
                </div>
                <p v-if="item.description" class="queue-description">{{ truncate(item.description) }}</p>
                <p class="queue-triage" data-testid="ai-assisted-triage">
                  AI-assisted triage:
                  {{
                    item.ai_assisted_triage.classification
                      ? aiClassificationLabel(item.ai_assisted_triage.classification)
                      : 'No analysis yet'
                  }}
                  <template v-if="item.ai_assisted_triage.confidence">
                    · {{ aiConfidenceLabel(item.ai_assisted_triage.confidence) }} confidence
                  </template>
                  <template v-if="item.ai_assisted_triage.uncertainty">
                    · {{ aiConfidenceLabel(item.ai_assisted_triage.uncertainty) }} uncertainty
                  </template>
                </p>
              </div>
              <RouterLink
                class="button"
                :to="{ name: 'community-shield-review-detail', params: { id: item.id } }"
                data-testid="open-review"
              >
                Open complete story
              </RouterLink>
            </li>
          </ul>
        </section>

        <section class="queue-section">
          <h2 class="queue-section-title">{{ completedStories.length ? 'All reports' : 'Queue' }}</h2>
          <ul class="queue-list" data-testid="review-queue">
            <li
              v-for="item in items"
              :key="item.id"
              class="queue-case"
              data-testid="review-queue-item"
            >
              <div class="queue-case-body">
                <p class="queue-case-ref">#{{ item.id }}</p>
                <div class="queue-indicators">
                  <span class="queue-indicator">{{ platformLabel(item.platform) }}</span>
                  <span class="queue-indicator">{{ contentTypeLabel(item.content_type) }}</span>
                  <span class="queue-indicator">{{ visibilityLabel(item.visibility) }}</span>
                  <span class="queue-indicator">{{ statusLabel(item.status) }}</span>
                  <span v-if="item.review_outcome" class="queue-indicator confidence-high">
                    {{ reviewOutcomeLabel(item.review_outcome) }}
                  </span>
                  <span
                    v-if="item.ai_assisted_triage.confidence"
                    class="queue-indicator"
                    :class="confidenceClass(item.ai_assisted_triage.confidence)"
                  >
                    {{ aiConfidenceLabel(item.ai_assisted_triage.confidence) }} confidence
                  </span>
                  <span
                    v-if="item.ai_assisted_triage.uncertainty"
                    class="queue-indicator"
                    :class="uncertaintyClass(item.ai_assisted_triage.uncertainty)"
                  >
                    {{ aiConfidenceLabel(item.ai_assisted_triage.uncertainty) }} uncertainty
                  </span>
                  <span v-if="item.escalated" class="queue-indicator uncertainty-high">Escalated</span>
                  <span v-if="item.status === 'reviewing'" class="queue-indicator">Under review</span>
                </div>
                <p v-if="item.description" class="queue-description">{{ truncate(item.description) }}</p>
                <p class="queue-triage" data-testid="ai-assisted-triage">
                  AI-assisted triage:
                  {{
                    item.ai_assisted_triage.classification
                      ? aiClassificationLabel(item.ai_assisted_triage.classification)
                      : 'No analysis yet'
                  }}
                  <template v-if="item.ai_assisted_triage.confidence">
                    · {{ aiConfidenceLabel(item.ai_assisted_triage.confidence) }} confidence
                  </template>
                  <template v-if="item.ai_assisted_triage.uncertainty">
                    · {{ aiConfidenceLabel(item.ai_assisted_triage.uncertainty) }} uncertainty
                  </template>
                </p>
                <p class="queue-meta">
                  {{ item.related_item_count }} related
                  {{ item.related_item_count === 1 ? 'item' : 'items' }}
                  · Submitted {{ formatDateTime(item.created_at) }}
                </p>
                <p
                  v-if="item.ai_assisted_triage.uncertainty === 'high'"
                  class="queue-uncertainty-note"
                  data-testid="high-uncertainty-flag"
                >
                  High uncertainty — additional context may help before a determination.
                </p>
              </div>
              <RouterLink
                class="button"
                :to="{ name: 'community-shield-review-detail', params: { id: item.id } }"
                data-testid="open-review"
              >
                Review
              </RouterLink>
            </li>
          </ul>
        </section>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import EmptyState from '@/components/ui/EmptyState.vue';
import LoadingState from '@/components/ui/LoadingState.vue';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { useOrganizationStore } from '@/stores/organization';
import type { ReviewQueueItem } from '@/types';
import {
  PLATFORM_OPTIONS,
  SAFETY_CLASSIFICATION_OPTIONS,
  STATUS_OPTIONS,
  aiClassificationLabel,
  aiConfidenceLabel,
  contentTypeLabel,
  platformLabel,
  reviewOutcomeLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';
import { formatDateTime } from '@/utils/date';

const organization = useOrganizationStore();
const items = ref<ReviewQueueItem[]>([]);
const error = ref<string | null>(null);
const isLoading = ref(false);

const filters = reactive({
  status: '',
  platform: '',
  confidence: '',
  uncertainty: '',
  classification: '',
});

const completedStories = computed(() =>
  items.value.filter(
    (item) => item.status === 'resolved' && item.review_outcome === 'confirmed',
  ),
);

function truncate(text: string, max = 140): string {
  const trimmed = text.trim();
  if (trimmed.length <= max) {
    return trimmed;
  }
  return `${trimmed.slice(0, max - 1)}…`;
}

function confidenceClass(level: string): string {
  if (level === 'high') return 'confidence-high';
  if (level === 'moderate') return 'confidence-moderate';
  return '';
}

function uncertaintyClass(level: string): string {
  if (level === 'high') return 'uncertainty-high';
  return '';
}

async function loadQueue(): Promise<void> {
  if (!organization.currentOrganization || !organization.canReviewIncidents) {
    items.value = [];
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    items.value = await communityApi.reviewQueue(organization.currentOrganization.id, {
      status: filters.status as '' | 'open' | 'reviewing' | 'resolved',
      platform: filters.platform,
      confidence: filters.confidence,
      uncertainty: filters.uncertainty,
      classification: filters.classification,
    });
  } catch {
    error.value = 'Unable to load the review queue.';
    items.value = [];
  } finally {
    isLoading.value = false;
  }
}

useOrganizationQuery(loadQueue);
watch(filters, () => {
  void loadQueue();
});
</script>

<style scoped>
.queue-section {
  margin-top: var(--space-6);
}

.queue-section-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-lg);
}

.queue-section-hint {
  margin: 0 0 var(--space-4);
  font-size: var(--text-sm);
}

.queue-case-featured {
  border-color: rgba(20, 92, 62, 0.35);
  background: linear-gradient(180deg, var(--primary-soft) 0%, var(--surface) 70%);
}

.queue-description {
  margin: var(--space-2) 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
</style>
