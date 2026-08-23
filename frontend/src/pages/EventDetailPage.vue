<template>
  <section class="panel content stack">
    <RouterLink to="/events">Back to events</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading event…</p>
    <template v-else-if="item">
      <h1>{{ item.title }}</h1>
      <p class="muted">{{ formatDateTime(item.starts_at) }}<span v-if="item.ends_at"> – {{ formatDateTime(item.ends_at) }}</span></p>
      <p v-if="item.location"><strong>Location:</strong> {{ item.location }}</p>
      <p>{{ item.description }}</p>
      <a
        v-if="item.registration_url"
        class="button"
        :href="item.registration_url"
        target="_blank"
        rel="noopener noreferrer"
      >
        Registration link
      </a>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import { formatDateTime } from '@/utils/date';
import type { CommunityEvent } from '@/types';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<CommunityEvent | null>(null);
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
    item.value = await communityApi.event(organizationId, id);
  } catch {
    item.value = null;
    error.value = 'This event is not available in the current organization.';
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
