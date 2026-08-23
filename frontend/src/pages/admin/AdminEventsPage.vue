<template>
  <section class="panel content stack">
    <div class="actions">
      <div>
        <h1>Events</h1>
        <p class="muted">Community events for the current organization. This is not a ticketing system.</p>
      </div>
      <RouterLink v-if="organization.canManageEvents" class="button" to="/admin/events/new">
        Create
      </RouterLink>
    </div>
    <p v-if="!organization.canManageEvents" class="error">
      You cannot manage events in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading…</p>
    <table v-else>
      <thead>
        <tr>
          <th>Title</th>
          <th>Starts</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ formatDateTime(item.starts_at) }}</td>
          <td class="actions">
            <RouterLink :to="{ name: 'admin-event-edit', params: { id: item.id } }">Edit</RouterLink>
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
import { formatDateTime } from '@/utils/date';
import type { CommunityEvent } from '@/types';

const items = ref<CommunityEvent[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canManageEvents) {
    items.value = [];
    return;
  }

  items.value = await communityApi.events(organizationId);
});

async function onDelete(id: number): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !window.confirm('Delete this event?')) {
    return;
  }

  await communityApi.deleteEvent(organizationId, id);
  items.value = items.value.filter((item) => item.id !== id);
}
</script>
