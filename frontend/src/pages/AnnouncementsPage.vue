<template>
  <section class="panel content stack">
    <div>
      <h1>Announcements</h1>
      <p class="muted">
        Notices for {{ organization.currentOrganization?.name ?? 'this organization' }} only.
      </p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading announcements…</p>
    <p v-else-if="items.length === 0" class="muted">No published announcements yet.</p>
    <div v-else class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="panel card-link"
        :to="{ name: 'announcement-detail', params: { id: item.id } }"
      >
        <strong>{{ item.title }}</strong>
        <p class="muted">{{ formatDateTime(item.published_at) }}</p>
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
import type { Announcement } from '@/types';

const items = ref<Announcement[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.announcements(organizationId);
});
</script>
