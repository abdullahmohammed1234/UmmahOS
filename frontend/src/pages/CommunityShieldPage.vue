<template>
  <section class="panel content stack">
    <div>
      <h1>Community Shield</h1>
      <p class="muted">
        Report a concern to administrators of
        {{ organization.currentOrganization?.name ?? 'this organization' }}.
        Other members cannot see your report.
      </p>
    </div>

    <article v-if="confirmation" class="panel content">
      <h2>Report received</h2>
      <p>{{ confirmation }}</p>
      <p class="muted">This organization's administrators can review it. You will not see other members' reports.</p>
      <button class="button secondary" type="button" @click="confirmation = ''">Submit another report</button>
    </article>

    <form v-else class="stack" @submit.prevent="onSubmit">
      <label class="field">
        <span>Category</span>
        <select v-model="category" required>
          <option value="safety">Safety</option>
          <option value="harassment">Harassment</option>
          <option value="hate">Hate</option>
          <option value="community_concern">Community concern</option>
          <option value="other">Other</option>
        </select>
      </label>
      <label class="field">
        <span>What happened?</span>
        <textarea v-model="description" required></textarea>
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="button" type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Sending…' : 'Submit report' }}
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { Incident } from '@/types';

const organization = useOrganizationStore();
const category = ref<Incident['category']>('community_concern');
const description = ref('');
const confirmation = ref('');
const error = ref('');
const isSubmitting = ref(false);

async function onSubmit(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId) {
    error.value = 'No current organization.';
    return;
  }

  isSubmitting.value = true;
  error.value = '';

  try {
    const result = await communityApi.reportIncident(organizationId, {
      category: category.value,
      description: description.value,
    });
    confirmation.value = result.message;
    description.value = '';
  } catch {
    error.value = 'Unable to submit this report.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>
