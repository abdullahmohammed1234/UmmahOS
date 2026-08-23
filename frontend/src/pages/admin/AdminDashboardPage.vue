<template>
  <section class="stack">
    <article class="panel content">
      <p class="muted">Organization dashboard</p>
      <h1>{{ organization.currentOrganization?.name ?? 'Organization' }}</h1>
      <p class="muted">Simple counts for the current organization only. This is not analytics.</p>
    </article>

    <p v-if="!organization.isOrganizationAdmin" class="error">
      You do not have permission to manage this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading organization overview…</p>

    <div v-else-if="dashboard" class="grid">
      <RouterLink class="panel content card-link" to="/members">
        <p class="muted">Members</p>
        <h2>{{ dashboard.counts.members }}</h2>
      </RouterLink>
      <RouterLink class="panel content card-link" to="/admin/announcements">
        <p class="muted">Published announcements</p>
        <h2>{{ dashboard.counts.published_announcements }}</h2>
      </RouterLink>
      <RouterLink class="panel content card-link" to="/admin/events">
        <p class="muted">Upcoming events</p>
        <h2>{{ dashboard.counts.upcoming_events }}</h2>
      </RouterLink>
      <RouterLink class="panel content card-link" to="/admin/resources">
        <p class="muted">Resources</p>
        <h2>Manage</h2>
      </RouterLink>
      <RouterLink class="panel content card-link" to="/admin/academy">
        <p class="muted">Published courses</p>
        <h2>{{ dashboard.counts.published_courses }}</h2>
      </RouterLink>
      <RouterLink class="panel content card-link" to="/admin/community-shield">
        <p class="muted">Open Community Shield reports</p>
        <h2>{{ dashboard.counts.open_incidents }}</h2>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
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
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

h1,
h2,
p {
  margin-top: 0;
}

@media (max-width: 720px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
