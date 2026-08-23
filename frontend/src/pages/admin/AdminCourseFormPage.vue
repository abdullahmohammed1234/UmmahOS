<template>
  <section class="panel content stack">
    <RouterLink to="/admin/academy">Back to Academy</RouterLink>
    <h1>{{ isEdit ? 'Edit course' : 'Create course' }}</h1>
    <p v-if="!organization.canManageCourses" class="error">
      You cannot manage Academy in this organization.
    </p>
    <form v-else class="stack" @submit.prevent="onSubmit">
      <label class="field">
        <span>Title</span>
        <input v-model="title" required />
      </label>
      <label class="field">
        <span>Description</span>
        <textarea v-model="description"></textarea>
      </label>
      <label class="field">
        <span>Status</span>
        <select v-model="status">
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
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
import type { Course } from '@/types';

const route = useRoute();
const router = useRouter();
const organization = useOrganizationStore();
const title = ref('');
const description = ref('');
const status = ref<Course['status']>('draft');
const error = ref('');
const isSaving = ref(false);
const isEdit = computed(() => Boolean(route.params.id));

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  async ([organizationId, id]) => {
    if (!organizationId || !id) {
      title.value = '';
      description.value = '';
      status.value = 'draft';
      return;
    }

    try {
      const item = await communityApi.course(Number(organizationId), Number(id));
      title.value = item.title;
      description.value = item.description ?? '';
      status.value = item.status;
    } catch {
      error.value = 'Unable to load this course.';
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
      description: description.value,
      status: status.value,
    };

    if (isEdit.value) {
      await communityApi.updateCourse(organizationId, Number(route.params.id), payload);
    } else {
      await communityApi.createCourse(organizationId, payload);
    }

    await router.push({ name: 'admin-academy' });
  } catch {
    error.value = 'Unable to save this course.';
  } finally {
    isSaving.value = false;
  }
}
</script>
