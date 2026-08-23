<template>
  <section class="stack">
    <article class="panel content">
      <p class="muted">{{ organization.currentOrganization?.name ?? 'No organization' }}</p>
      <h1>{{ dashboard?.welcome ?? 'Welcome' }}</h1>
      <p class="muted">
        You are viewing this MSA as <strong>{{ organization.currentRole ?? 'a visitor' }}</strong>.
        Switching organizations changes both the community and your permissions.
      </p>
    </article>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading this organization's community…</p>

    <template v-else-if="dashboard">
      <div class="grid">
        <article class="panel content">
          <h2>Upcoming events</h2>
          <p v-if="dashboard.upcoming_events.length === 0" class="muted">No upcoming events yet.</p>
          <ul v-else>
            <li v-for="event in dashboard.upcoming_events" :key="event.id">
              <RouterLink :to="{ name: 'event-detail', params: { id: event.id } }">
                {{ event.title }}
              </RouterLink>
              <span class="muted"> · {{ formatDateTime(event.starts_at) }}</span>
            </li>
          </ul>
        </article>
        <article class="panel content">
          <h2>Recent announcements</h2>
          <p v-if="dashboard.recent_announcements.length === 0" class="muted">No announcements yet.</p>
          <ul v-else>
            <li v-for="item in dashboard.recent_announcements" :key="item.id">
              <RouterLink :to="{ name: 'announcement-detail', params: { id: item.id } }">
                {{ item.title }}
              </RouterLink>
            </li>
          </ul>
        </article>
      </div>

      <article class="panel content">
        <h2>Featured resources</h2>
        <p v-if="dashboard.featured_resources.length === 0" class="muted">No resources yet.</p>
        <ul v-else>
          <li v-for="item in dashboard.featured_resources" :key="item.id">
            <RouterLink :to="{ name: 'resource-detail', params: { id: item.id } }">
              {{ item.title }}
            </RouterLink>
            <span v-if="item.category" class="muted"> · {{ item.category }}</span>
          </li>
        </ul>
      </article>

      <div class="grid">
        <article class="panel content">
          <h2>Academy</h2>
          <p class="muted">
            {{ dashboard.academy.published_courses_count }} published course(s) in this organization.
          </p>
          <ul>
            <li v-for="course in dashboard.academy.courses" :key="course.id">
              <RouterLink :to="{ name: 'course-detail', params: { id: course.id } }">
                {{ course.title }}
              </RouterLink>
            </li>
          </ul>
          <RouterLink class="button secondary" to="/academy">Open Academy</RouterLink>
        </article>
        <article class="panel content">
          <h2>Community Shield</h2>
          <p class="muted">
            Report a safety or community concern privately to this organization's administrators.
          </p>
          <RouterLink class="button" to="/community-shield">Report a concern</RouterLink>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { formatDateTime } from '@/utils/date';
import type { MemberDashboard } from '@/types';

const dashboard = ref<MemberDashboard | null>(null);

const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  dashboard.value = await communityApi.dashboard(organizationId);
});
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

h1,
h2,
p {
  margin-top: 0;
}

ul {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
}

@media (max-width: 720px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
