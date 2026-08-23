<template>
  <section class="panel content stack">
    <div>
      <h1>Resources</h1>
      <p class="muted">
        Links and references for {{ organization.currentOrganization?.name ?? 'this organization' }}.
      </p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading resources…</p>
    <p v-else-if="items.length === 0" class="muted">No resources yet.</p>
    <div v-else class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="panel card-link"
        :to="{ name: 'resource-detail', params: { id: item.id } }"
      >
        <strong>{{ item.title }}</strong>
        <p class="muted">{{ item.category ?? 'General' }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { ResourceItem } from '@/types';

const items = ref<ResourceItem[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.resources(organizationId);
});
</script>
