<template>
  <section class="panel content stack">
    <RouterLink to="/admin/community-shield">Back to reports</RouterLink>
    <p v-if="!organization.canManageIncidents" class="error">
      You cannot review Community Shield reports in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading report…</p>
    <template v-else-if="item">
      <p class="muted">{{ item.category }} · {{ item.status }}</p>
      <h1>Community Shield report</h1>
      <p><strong>Reporter:</strong> {{ item.reported_by?.name ?? 'Unknown' }} ({{ item.reported_by?.email }})</p>
      <p class="body">{{ item.description }}</p>
      <label class="field">
        <span>Status</span>
        <select v-model="status">
          <option value="open">Open</option>
          <option value="reviewing">Reviewing</option>
          <option value="resolved">Resolved</option>
        </select>
      </label>
      <p v-if="saveError" class="error">{{ saveError }}</p>
      <p v-if="message" class="muted">{{ message }}</p>
      <button class="button" type="button" :disabled="isSaving" @click="onSave">Update status</button>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { Incident } from '@/types';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<Incident | null>(null);
const status = ref<Incident['status']>('open');
const isLoading = ref(false);
const isSaving = ref(false);
const error = ref('');
const saveError = ref('');
const message = ref('');

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const id = Number(route.params.id);

  if (!organizationId || !id || !organization.canManageIncidents) {
    item.value = null;
    return;
  }

  isLoading.value = true;
  error.value = '';

  try {
    item.value = await communityApi.incident(organizationId, id);
    status.value = item.value.status;
  } catch {
    item.value = null;
    error.value = 'This report is not available in the current organization.';
  } finally {
    isLoading.value = false;
  }
}

async function onSave(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !item.value) {
    return;
  }

  isSaving.value = true;
  saveError.value = '';
  message.value = '';

  try {
    item.value = await communityApi.updateIncident(organizationId, item.value.id, {
      status: status.value,
    });
    message.value = 'Status updated.';
  } catch {
    saveError.value = 'Unable to update this report.';
  } finally {
    isSaving.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.id, organization.canManageIncidents],
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
