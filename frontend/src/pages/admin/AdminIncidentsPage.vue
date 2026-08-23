<template>
  <section class="panel content stack">
    <div>
      <h1>Community Shield</h1>
      <p class="muted">Review reports submitted in the current organization only.</p>
    </div>

    <p v-if="!organization.canReviewIncidents" class="error" data-testid="admin-denied">
      You cannot review Community Shield reports in this organization.
    </p>

    <template v-else>
      <div class="counts" data-testid="status-counts">
        <div>
          <p class="muted">Open</p>
          <strong>{{ counts.open }}</strong>
        </div>
        <div>
          <p class="muted">Reviewing</p>
          <strong>{{ counts.reviewing }}</strong>
        </div>
        <div>
          <p class="muted">Resolved</p>
          <strong>{{ counts.resolved }}</strong>
        </div>
      </div>

      <label class="field filter">
        <span>Filter by status</span>
        <select v-model="statusFilter" data-testid="status-filter">
          <option value="">All reports</option>
          <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-else-if="isLoading" class="muted">Loading…</p>
      <p v-else-if="items.length === 0" class="muted">No reports match this filter.</p>
      <table v-else data-testid="report-queue">
        <thead>
          <tr>
            <th>Platform</th>
            <th>Type</th>
            <th>Context</th>
            <th>Status</th>
            <th>Reporter</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ platformLabel(item.platform) }}</td>
            <td>{{ contentTypeLabel(item.content_type) }}</td>
            <td>{{ visibilityLabel(item.visibility) }}</td>
            <td>{{ statusLabel(item.status) }}</td>
            <td>{{ item.reported_by?.name ?? 'Unknown' }}</td>
            <td>
              <RouterLink :to="{ name: 'admin-incident-detail', params: { id: item.id } }">
                Review
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { useOrganizationStore } from '@/stores/organization';
import type { CommunityShieldStatus, Incident } from '@/types';
import {
  STATUS_OPTIONS,
  contentTypeLabel,
  platformLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';

const organization = useOrganizationStore();
const items = ref<Incident[]>([]);
const statusFilter = ref<CommunityShieldStatus | ''>('');
const counts = ref({ open: 0, reviewing: 0, resolved: 0 });

const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canReviewIncidents) {
    items.value = [];
    counts.value = { open: 0, reviewing: 0, resolved: 0 };
    return;
  }

  const [overview, reports] = await Promise.all([
    communityApi.communityShieldOverview(organizationId),
    communityApi.incidents(organizationId, statusFilter.value),
  ]);

  counts.value = overview.counts ?? { open: 0, reviewing: 0, resolved: 0 };
  items.value = reports;
});

watch(statusFilter, async (status) => {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !organization.canReviewIncidents) {
    return;
  }

  try {
    items.value = await communityApi.incidents(organizationId, status);
  } catch {
    error.value = 'Unable to load this page for the current organization.';
  }
});

watch(
  () => organization.currentOrganization?.id,
  () => {
    statusFilter.value = '';
  },
);
</script>

<style scoped>
.counts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.counts > div {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  background: rgba(31, 107, 74, 0.04);
}

.counts p,
.counts strong {
  margin: 0;
}

.counts strong {
  font-size: 1.4rem;
}

.filter {
  max-width: 16rem;
}

@media (max-width: 720px) {
  .counts {
    grid-template-columns: 1fr;
  }
}
</style>
