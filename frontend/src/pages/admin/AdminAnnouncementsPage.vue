<template>
  <section class="panel content stack">
    <div class="actions">
      <div>
        <h1>Announcements</h1>
        <p class="muted">Manage notices for the current organization.</p>
      </div>
      <RouterLink v-if="organization.canManageContent" class="button" to="/admin/announcements/new">
        Create
      </RouterLink>
    </div>
    <p v-if="!organization.canManageContent" class="error">
      You cannot manage announcements in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading…</p>
    <table v-else>
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ item.is_published ? 'Published' : 'Draft' }}</td>
          <td class="actions">
            <RouterLink :to="{ name: 'admin-announcement-edit', params: { id: item.id } }">Edit</RouterLink>
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
import type { Announcement } from '@/types';

const items = ref<Announcement[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canManageContent) {
    items.value = [];
    return;
  }

  items.value = await communityApi.announcements(organizationId);
});

async function onDelete(id: number): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !window.confirm('Delete this announcement?')) {
    return;
  }

  await communityApi.deleteAnnouncement(organizationId, id);
  items.value = items.value.filter((item) => item.id !== id);
}
</script>
