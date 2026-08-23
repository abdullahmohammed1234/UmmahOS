<template>
  <section class="panel content stack" data-testid="learning-pattern-detail">
    <RouterLink to="/admin/education/patterns">Back to learning patterns</RouterLink>

    <p v-if="!organization.canViewEducationPatterns" class="error">
      You cannot view learning patterns in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading pattern…</p>

    <template v-else-if="pattern">
      <div>
        <p class="muted">{{ pattern.status }} · {{ patternTypeLabel(pattern.pattern_type) }}</p>
        <h1>{{ pattern.title }}</h1>
        <p>{{ pattern.summary }}</p>
      </div>

      <dl class="details">
        <div>
          <dt>Learning objective</dt>
          <dd>{{ pattern.learning_objective }}</dd>
        </div>
        <div>
          <dt>Domain</dt>
          <dd>{{ pattern.domain || 'Not set' }}</dd>
        </div>
        <div>
          <dt>Audience</dt>
          <dd>{{ pattern.audience_context || 'Not set' }}</dd>
        </div>
        <div v-if="pattern.source_incident_id">
          <dt>Source incident</dt>
          <dd>
            <RouterLink
              :to="{ name: 'community-shield-review-detail', params: { id: pattern.source_incident_id } }"
              data-testid="source-incident-link"
            >
              Report #{{ pattern.source_incident_id }}
            </RouterLink>
          </dd>
        </div>
      </dl>

      <div v-if="organization.canManageEducationPatterns" class="actions">
        <button
          v-if="pattern.status === 'draft'"
          class="button"
          type="button"
          :disabled="busy"
          @click="approve"
        >
          Approve
        </button>
        <button
          v-if="pattern.status !== 'archived'"
          class="button secondary"
          type="button"
          :disabled="busy"
          @click="archive"
        >
          Archive
        </button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { LearningPattern } from '@/types';
import { patternTypeLabel } from '@/utils/education';

const route = useRoute();
const organization = useOrganizationStore();

const pattern = ref<LearningPattern | null>(null);
const isLoading = ref(false);
const error = ref('');
const busy = ref(false);

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const id = Number(route.params.id);

  if (!organizationId || !id || !organization.canViewEducationPatterns) {
    pattern.value = null;
    return;
  }

  isLoading.value = true;
  error.value = '';

  try {
    pattern.value = await communityApi.learningPattern(organizationId, id);
  } catch {
    pattern.value = null;
    error.value = 'Unable to load this learning pattern.';
  } finally {
    isLoading.value = false;
  }
}

async function approve(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  if (!organizationId || !pattern.value) {
    return;
  }

  busy.value = true;
  try {
    pattern.value = await communityApi.approveLearningPattern(organizationId, pattern.value.id);
  } finally {
    busy.value = false;
  }
}

async function archive(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  if (!organizationId || !pattern.value) {
    return;
  }

  busy.value = true;
  try {
    pattern.value = await communityApi.archiveLearningPattern(organizationId, pattern.value.id);
  } finally {
    busy.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, organization.canViewEducationPatterns, route.params.id],
  () => {
    void load();
  },
  { immediate: true },
);
</script>

<style scoped>
.details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin: 0;
}

.details dt {
  color: var(--muted);
  font-size: 0.8rem;
}

.details dd {
  margin: 0.15rem 0 0;
}
</style>
