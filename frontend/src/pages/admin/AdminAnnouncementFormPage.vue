<template>
  <section class="panel content stack">
    <RouterLink to="/admin/announcements">Back to announcements</RouterLink>
    <h1>{{ isEdit ? 'Edit announcement' : 'Create announcement' }}</h1>
    <p v-if="!organization.canManageContent" class="error">
      You cannot manage announcements in this organization.
    </p>
    <form v-else class="stack" @submit.prevent="onSubmit">
      <label class="field">
        <span>Title</span>
        <input v-model="title" required />
      </label>
      <label class="field">
        <span>Body</span>
        <textarea v-model="body" required></textarea>
      </label>
      <label class="check">
        <input v-model="published" type="checkbox" />
        <span>Published</span>
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="button" type="submit" :disabled="isSaving">Save</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';

const route = useRoute();
const router = useRouter();
const organization = useOrganizationStore();
const title = ref('');
const body = ref('');
const published = ref(true);
const error = ref('');
const isSaving = ref(false);
const isEdit = computed(() => Boolean(route.params.id));

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  async ([organizationId, id]) => {
    if (!organizationId || !id) {
      title.value = '';
      body.value = '';
      published.value = true;
      return;
    }

    try {
      const item = await communityApi.announcement(Number(organizationId), Number(id));
      title.value = item.title;
      body.value = item.body;
      published.value = item.is_published;
    } catch {
      error.value = 'Unable to load this announcement.';
    }
  },
  { immediate: true },
);

async function onSubmit(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId) {
    return;
  }

  isSaving.value = true;
  error.value = '';

  try {
    const payload = {
      title: title.value,
      body: body.value,
      published: published.value,
    };

    if (isEdit.value) {
      await communityApi.updateAnnouncement(organizationId, Number(route.params.id), payload);
    } else {
      await communityApi.createAnnouncement(organizationId, payload);
    }

    await router.push({ name: 'admin-announcements' });
  } catch {
    error.value = 'Unable to save this announcement.';
  } finally {
    isSaving.value = false;
  }
}
</script>

<style scoped>
.check {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>
