<template>
  <section class="panel content stack">
    <div class="actions">
      <div>
        <h1>Resources</h1>
        <p class="muted">Community links for the current organization.</p>
      </div>
      <RouterLink v-if="organization.canManageContent" class="button" to="/admin/resources/new">
        Create
      </RouterLink>
    </div>
    <p v-if="!organization.canManageContent" class="error">
      You cannot manage resources in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading…</p>
    <table v-else>
      <thead>
        <tr>
          <th>Title</th>
          <th>Category</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ item.category ?? '—' }}</td>
          <td class="actions">
            <RouterLink :to="{ name: 'admin-resource-edit', params: { id: item.id } }">Edit</RouterLink>
            <button class="button danger" type="button" @click="onDelete(item.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
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
  if (!organization.canManageContent) {
    items.value = [];
    return;
  }

  items.value = await communityApi.resources(organizationId);
});

async function onDelete(id: number): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !window.confirm('Delete this resource?')) {
    return;
  }

  await communityApi.deleteResource(organizationId, id);
  items.value = items.value.filter((item) => item.id !== id);
}
</script>
