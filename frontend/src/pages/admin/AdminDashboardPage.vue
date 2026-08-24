<template>
  <section class="admin-dashboard stack">
    <PageHeader
      eyebrow="Organization"
      :title="organization.currentOrganization?.name ?? 'Organization'"
      description="Concise metrics for the current organization. Demo data is seeded — not production analytics."
    />

    <p v-if="!organization.isOrganizationAdmin" class="error">
      You do not have permission to manage this organization.
    </p>
    <LoadingState v-else-if="isLoading" skeleton :lines="3" />
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-else-if="dashboard" class="stat-grid">
      <RouterLink class="panel stat-card card-link" to="/members">
        <p class="stat-label">Members</p>
        <p class="stat-value">{{ dashboard.counts.members }}</p>
      </RouterLink>
      <RouterLink class="panel stat-card card-link" to="/admin/announcements">
        <p class="stat-label">Published announcements</p>
        <p class="stat-value">{{ dashboard.counts.published_announcements }}</p>
      </RouterLink>
      <RouterLink class="panel stat-card card-link" to="/admin/events">
        <p class="stat-label">Upcoming events</p>
        <p class="stat-value">{{ dashboard.counts.upcoming_events }}</p>
      </RouterLink>
      <RouterLink class="panel stat-card card-link" to="/admin/academy">
        <p class="stat-label">Published courses</p>
        <p class="stat-value">{{ dashboard.counts.published_courses }}</p>
      </RouterLink>
      <RouterLink class="panel stat-card card-link shield-stat" to="/admin/community-shield">
        <p class="stat-label">Open Community Shield reports</p>
        <p class="stat-value">{{ dashboard.counts.open_incidents }}</p>
        <p class="muted stat-sub">
          {{ dashboard.counts.reviewing_incidents }} under review ·
          {{ dashboard.counts.resolved_incidents }} resolved
        </p>
      </RouterLink>
      <RouterLink
        v-if="organization.canReviewIncidents"
        class="panel stat-card card-link"
        to="/community-shield/review-queue"
      >
        <p class="stat-label">Review queue</p>
        <p class="stat-value">{{ dashboard.counts.reviewing_incidents }}</p>
        <p class="muted stat-sub">Reports awaiting human review</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import LoadingState from '@/components/ui/LoadingState.vue';
import PageHeader from '@/components/ui/PageHeader.vue';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { AdminDashboard } from '@/types';

const dashboard = ref<AdminDashboard | null>(null);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.isOrganizationAdmin) {
    dashboard.value = null;
    return;
  }

  dashboard.value = await communityApi.adminDashboard(organizationId);
});
</script>

<style scoped>
.admin-dashboard {
  max-width: var(--content-max);
}

.shield-stat {
  border-left: 3px solid var(--primary);
}

.stat-sub {
  font-size: var(--text-xs);
  margin: var(--space-2) 0 0;
}
</style>
