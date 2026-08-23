<template>
  <section class="panel content stack">
    <div>
      <h1>Community Shield</h1>
      <p class="muted">Review reports submitted in the current organization only.</p>
    </div>
    <p v-if="!organization.canManageIncidents" class="error">
      You cannot review Community Shield reports in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading…</p>
    <table v-else>
      <thead>
        <tr>
          <th>Category</th>
          <th>Status</th>
          <th>Reporter</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.category }}</td>
          <td>{{ item.status }}</td>
          <td>{{ item.reported_by?.name ?? 'Unknown' }}</td>
          <td>
            <RouterLink :to="{ name: 'admin-incident-detail', params: { id: item.id } }">Review</RouterLink>
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
import type { Incident } from '@/types';

const items = ref<Incident[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canManageIncidents) {
    items.value = [];
    return;
  }

  items.value = await communityApi.incidents(organizationId);
});
</script>
