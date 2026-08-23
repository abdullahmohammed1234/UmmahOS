<template>
  <section class="panel content stack">
    <RouterLink to="/admin/resources">Back to resources</RouterLink>
    <h1>{{ isEdit ? 'Edit resource' : 'Create resource' }}</h1>
    <p v-if="!organization.canManageContent" class="error">
      You cannot manage resources in this organization.
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
        <span>URL</span>
        <input v-model="url" type="url" required />
      </label>
      <label class="field">
        <span>Category</span>
        <input v-model="category" />
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
const description = ref('');
const url = ref('');
const category = ref('');
const error = ref('');
const isSaving = ref(false);
const isEdit = computed(() => Boolean(route.params.id));

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  async ([organizationId, id]) => {
    if (!organizationId || !id) {
      title.value = '';
      description.value = '';
      url.value = '';
      category.value = '';
      return;
    }

    try {
      const item = await communityApi.resource(Number(organizationId), Number(id));
      title.value = item.title;
      description.value = item.description ?? '';
      url.value = item.url;
      category.value = item.category ?? '';
    } catch {
      error.value = 'Unable to load this resource.';
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
      url: url.value,
      category: category.value || null,
    };

    if (isEdit.value) {
      await communityApi.updateResource(organizationId, Number(route.params.id), payload);
    } else {
      await communityApi.createResource(organizationId, payload);
    }

    await router.push({ name: 'admin-resources' });
  } catch {
    error.value = 'Unable to save this resource.';
  } finally {
    isSaving.value = false;
  }
}
</script>
