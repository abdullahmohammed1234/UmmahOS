<template>
  <section class="panel content stack" data-testid="review-queue-page">
    <div>
      <p class="eyebrow">Community Shield</p>
      <h1>Community Safety Review</h1>
      <p class="muted">
        Open reviews for {{ organization.currentOrganization?.name ?? 'this organization' }}.
        AI-assisted triage is advisory — a human reviewer decides.
      </p>
    </div>

    <p v-if="!organization.canReviewIncidents" class="error" data-testid="review-denied">
      You cannot access the Community Safety Review queue in this organization.
    </p>

    <template v-else>
      <div class="filters" data-testid="review-filters">
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
          <span>Human classification</span>
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
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-else-if="isLoading" class="muted">Loading open reviews…</p>
      <p v-else-if="items.length === 0" class="muted">No reports match these filters.</p>

      <ul v-else class="queue" data-testid="review-queue">
        <li v-for="item in items" :key="item.id" class="queue-item" data-testid="review-queue-item">
          <div class="queue-main">
            <p class="queue-title">
              <strong>#{{ item.id }}</strong>
              <span>{{ platformLabel(item.platform) }}</span>
              <span>{{ visibilityLabel(item.visibility) }}</span>
              <span v-if="item.escalated" class="badge escalate">Escalated</span>
              <span v-if="item.status === 'reviewing'" class="badge">Under review</span>
            </p>
            <p class="muted triage" data-testid="ai-assisted-triage">
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
            <p class="muted">
              {{ item.related_item_count }} related
              {{ item.related_item_count === 1 ? 'item' : 'items' }}
              · Submitted {{ formatDateTime(item.created_at) }}
            </p>
            <p
              v-if="item.ai_assisted_triage.uncertainty === 'high'"
              class="uncertainty"
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
    </template>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
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
  platformLabel,
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
.content {
  padding: 1.25rem 1.4rem;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--muted);
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
}

.queue {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.85rem;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
  padding: 1rem 0;
  border-top: 1px solid var(--line);
}

.queue-item:first-child {
  border-top: 0;
  padding-top: 0.25rem;
}

.queue-title {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin: 0 0 0.35rem;
}

.triage {
  margin: 0 0 0.25rem;
}

.uncertainty {
  margin: 0.45rem 0 0;
  color: #8a5a00;
}

.badge {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: rgba(31, 107, 74, 0.12);
  font-size: 0.78rem;
}

.badge.escalate {
  background: rgba(138, 90, 0, 0.16);
}

@media (max-width: 720px) {
  .queue-item {
    display: grid;
  }
}
</style>
