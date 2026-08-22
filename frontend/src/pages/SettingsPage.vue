<template>
  <section class="panel content stack">
    <div>
      <h1>Organization settings</h1>
      <p class="muted">Changes apply only to the current organization.</p>
    </div>
    <p v-if="!organization.canManageOrganization" class="error">
      You do not have permission to manage this organization.
    </p>
    <form v-else class="stack" @submit.prevent="onSubmit">
      <label class="field">
        <span>Name</span>
        <input v-model="name" required />
      </label>
      <label class="field">
        <span>Slug</span>
        <input v-model="slug" required />
      </label>
      <p v-if="message" class="muted">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="button" type="submit" :disabled="organization.isLoading">Save</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();
const name = ref(organization.currentOrganization?.name ?? '');
const slug = ref(organization.currentOrganization?.slug ?? '');
const message = ref('');
const error = ref('');

watch(
  () => organization.currentOrganization,
  (value) => {
    name.value = value?.name ?? '';
    slug.value = value?.slug ?? '';
  },
  { immediate: true },
);

async function onSubmit(): Promise<void> {
  message.value = '';
  error.value = '';

  try {
    await organization.updateCurrentOrganization({
      name: name.value,
      slug: slug.value,
    });
    message.value = 'Organization updated.';
  } catch {
    error.value = 'Unable to update this organization.';
  }
}
</script>

<style scoped>
.content {
  padding: 1.25rem 1.4rem;
}
</style>
