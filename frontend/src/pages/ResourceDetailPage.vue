<template>
  <section class="panel content stack">
    <RouterLink to="/resources">Back to resources</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading resource…</p>
    <template v-else-if="item">
      <p v-if="item.category" class="muted">{{ item.category }}</p>
      <h1>{{ item.title }}</h1>
      <p>{{ item.description }}</p>
      <a class="button" :href="item.url" target="_blank" rel="noopener noreferrer">Open resource</a>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { ResourceItem } from '@/types';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<ResourceItem | null>(null);
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
    item.value = await communityApi.resource(organizationId, id);
  } catch {
    item.value = null;
    error.value = 'This resource is not available in the current organization.';
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
