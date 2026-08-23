<template>
  <section class="panel content stack">
    <div>
      <h1>Events</h1>
      <p class="muted">
        Community events for {{ organization.currentOrganization?.name ?? 'this organization' }}.
      </p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading events…</p>
    <p v-else-if="items.length === 0" class="muted">No events yet.</p>
    <div v-else class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="panel card-link"
        :to="{ name: 'event-detail', params: { id: item.id } }"
      >
        <strong>{{ item.title }}</strong>
        <p class="muted">{{ formatDateTime(item.starts_at) }} · {{ item.location ?? 'Location TBA' }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { formatDateTime } from '@/utils/date';
import type { CommunityEvent } from '@/types';

const items = ref<CommunityEvent[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.events(organizationId);
});
</script>
