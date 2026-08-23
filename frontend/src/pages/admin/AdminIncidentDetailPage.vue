<template>
  <section class="panel content stack">
    <RouterLink to="/admin/community-shield">Back to reports</RouterLink>
    <p v-if="!organization.canManageIncidents" class="error">
      You cannot review Community Shield reports in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading report…</p>
    <template v-else-if="item">
      <p class="muted">
        {{ platformLabel(item.platform) }} · {{ contentTypeLabel(item.content_type) }} ·
        {{ visibilityLabel(item.visibility) }}
      </p>
      <h1>Community Shield report #{{ item.id }}</h1>
      <dl class="details">
        <div>
          <dt>Status</dt>
          <dd>{{ statusLabel(item.status) }}</dd>
        </div>
        <div>
          <dt>Reporter</dt>
          <dd>{{ item.reported_by?.name ?? 'Unknown' }} ({{ item.reported_by?.email }})</dd>
        </div>
        <div>
          <dt>Source URL</dt>
          <dd>
            <a v-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener noreferrer">
              {{ item.source_url }}
            </a>
            <span v-else class="muted">Not provided</span>
          </dd>
        </div>
      </dl>
      <div>
        <h2>What happened?</h2>
        <p class="body">{{ item.description }}</p>
      </div>
      <label class="field">
        <span>Status</span>
        <select v-model="status" data-testid="status-select">
          <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
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
import type { CommunityShieldStatus, Incident } from '@/types';
import {
  STATUS_OPTIONS,
  contentTypeLabel,
  platformLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<Incident | null>(null);
const status = ref<CommunityShieldStatus>('open');
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
.details {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.details div {
  display: grid;
  gap: 0.2rem;
}

.details dt {
  color: var(--muted);
  font-size: 0.9rem;
}

.details dd {
  margin: 0;
}

.body {
  white-space: pre-wrap;
  margin: 0;
}
</style>
