<template>
  <section class="panel content stack">
    <RouterLink to="/announcements">Back to announcements</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading announcement…</p>
    <template v-else-if="item">
      <h1>{{ item.title }}</h1>
      <p class="muted">{{ formatDateTime(item.published_at) }}</p>
      <p class="body">{{ item.body }}</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import { formatDateTime } from '@/utils/date';
import type { Announcement } from '@/types';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<Announcement | null>(null);
const isLoading = ref(false);
const error = ref('');

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const id = Number(route.params.id);

  if (!organizationId || !id) {
    return;
  }

  isLoading.value = true;
  error.value = '';

  try {
    item.value = await communityApi.announcement(organizationId, id);
  } catch {
    item.value = null;
    error.value = 'This announcement is not available in the current organization.';
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  () => {
    void load();
  },
  { immediate: true },
);
</script>

<style scoped>
.body {
  white-space: pre-wrap;
}
</style>
