<template>
  <div class="academy-workspace">
    <RouterLink class="back-link" to="/academy">← Back to Academy</RouterLink>

    <p v-if="error" class="error">{{ error }}</p>
    <LoadingState v-else-if="isLoading" message="Loading course…" />

    <template v-else-if="item">
      <header class="academy-hero">
        <p class="eyebrow">{{ item.status }}</p>
        <h1>{{ item.title }}</h1>
        <p>{{ item.description }}</p>
      </header>

      <article class="lesson-section">
        <p class="muted">
          This organization-scoped course entry point is part of the Academy foundation. Full lesson
          catalogs, quizzes, and certificates are not in scope yet.
        </p>
      </article>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import LoadingState from '@/components/ui/LoadingState.vue';
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
