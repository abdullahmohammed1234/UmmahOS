<template>
  <section class="dashboard stack">
    <article class="panel content welcome-card">
      <p class="eyebrow">{{ organization.currentOrganization?.name ?? 'Your organization' }}</p>
      <h1>{{ dashboard?.welcome ?? 'Welcome' }}</h1>
      <p class="muted">
        You are viewing this MSA as <strong>{{ organization.currentRole ?? 'a visitor' }}</strong>.
        Switching organizations changes both the community and your permissions.
      </p>
    </article>

    <LoadingState v-if="isLoading" skeleton :lines="4" test-id="dashboard-loading" />
    <p v-else-if="error" class="error">{{ error }}</p>

    <template v-else-if="dashboard">
      <div class="stat-row">
        <article class="panel content quick-card">
          <h2>Upcoming events</h2>
          <EmptyState
            v-if="dashboard.upcoming_events.length === 0"
            title="No upcoming events"
            description="Check back later for new events."
            icon="📅"
          />
          <ul v-else class="item-list">
            <li v-for="event in dashboard.upcoming_events" :key="event.id">
              <RouterLink :to="{ name: 'event-detail', params: { id: event.id } }">
                {{ event.title }}
              </RouterLink>
              <span class="muted"> · {{ formatDateTime(event.starts_at) }}</span>
            </li>
          </ul>
        </article>

        <article class="panel content quick-card">
          <h2>Recent announcements</h2>
          <EmptyState
            v-if="dashboard.recent_announcements.length === 0"
            title="No announcements yet"
            description="Organization announcements will appear here."
            icon="📢"
          />
          <ul v-else class="item-list">
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
        <EmptyState
          v-if="dashboard.featured_resources.length === 0"
          title="No resources yet"
          description="Helpful resources from your MSA will appear here."
          icon="📚"
        />
        <ul v-else class="item-list">
          <li v-for="item in dashboard.featured_resources" :key="item.id">
            <RouterLink :to="{ name: 'resource-detail', params: { id: item.id } }">
              {{ item.title }}
            </RouterLink>
            <span v-if="item.category" class="muted"> · {{ item.category }}</span>
          </li>
        </ul>
      </article>

      <div class="stat-row">
        <article class="panel content feature-card">
          <h2>Academy</h2>
          <p class="muted">
            {{ dashboard.academy.published_courses_count }} published course(s) in this organization.
          </p>
          <ul v-if="dashboard.academy.courses.length > 0" class="item-list">
            <li v-for="course in dashboard.academy.courses" :key="course.id">
              <RouterLink :to="{ name: 'course-detail', params: { id: course.id } }">
                {{ course.title }}
              </RouterLink>
            </li>
          </ul>
          <RouterLink class="button secondary" to="/academy">Open Academy</RouterLink>
        </article>

        <article class="panel content feature-card shield-card">
          <h2>Community Shield</h2>
          <p class="muted">
            Report a concern about harmful or concerning online content. Preserve context — not just
            a screenshot.
          </p>
          <p class="shield-tagline muted"><em>AI assists. Humans decide.</em></p>
          <RouterLink class="button" to="/community-shield">Report a concern</RouterLink>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import EmptyState from '@/components/ui/EmptyState.vue';
import LoadingState from '@/components/ui/LoadingState.vue';
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
.dashboard {
  max-width: var(--content-max);
}

.welcome-card {
  background: linear-gradient(135deg, var(--primary-soft), transparent 60%), var(--surface);
}

.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.quick-card h2,
.feature-card h2 {
  margin-top: 0;
  font-size: var(--text-lg);
}

.item-list {
  margin: 0 0 var(--space-4);
  padding-left: var(--space-5);
}

.item-list li {
  margin-bottom: var(--space-2);
}

.shield-card {
  border-left: 3px solid var(--primary);
}

.shield-tagline {
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

@media (max-width: 720px) {
  .stat-row {
    grid-template-columns: 1fr;
  }
}
</style>
