<template>
  <section class="panel content stack">
    <RouterLink to="/academy">Back to Academy</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading course…</p>
    <template v-else-if="item">
      <p class="muted">{{ item.status }}</p>
      <h1>{{ item.title }}</h1>
      <p>{{ item.description }}</p>
      <p class="muted">Lessons, quizzes, and progress tracking are not part of this foundation yet.</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { Course } from '@/types';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<Course | null>(null);
const isLoading = ref(false);
const error = ref('');

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const id = Number(route.params.id);

  if (!organizationId || !id) {
    return;
  }

  isLoading.value = true;
  error.value = '';

  try {
    item.value = await communityApi.course(organizationId, id);
  } catch {
    item.value = null;
    error.value = 'This course is not available in the current organization.';
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  () => {
    void load();
  },
  { immediate: true },
);
</script>
