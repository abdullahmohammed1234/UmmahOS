<template>
  <div class="academy-workspace">
    <header class="academy-hero">
      <p class="eyebrow">UmmahOS Academy</p>
      <h1>Academy</h1>
      <p>
        Published courses for {{ organization.currentOrganization?.name ?? 'this organization' }}.
        Organization-scoped learning — not a full LMS.
      </p>
    </header>

    <AcademySubNav />

    <p v-if="error" class="error">{{ error }}</p>
    <LoadingState v-else-if="isLoading" message="Loading courses…" />
    <EmptyState
      v-else-if="items.length === 0"
      title="No published courses yet"
      description="Courses will appear here once your organization publishes them."
      icon="📚"
    />
    <div v-else class="academy-grid">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="academy-card"
        :to="{ name: 'course-detail', params: { id: item.id } }"
      >
        <span class="academy-card-meta">Course</span>
        <h2 class="academy-card-title">{{ item.title }}</h2>
        <p v-if="item.description" class="academy-card-desc">{{ item.description }}</p>
        <span class="academy-card-arrow">View course →</span>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import AcademySubNav from '@/components/AcademySubNav.vue';
import EmptyState from '@/components/ui/EmptyState.vue';
import LoadingState from '@/components/ui/LoadingState.vue';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { useOrganizationStore } from '@/stores/organization';
import type { Course } from '@/types';

const organization = useOrganizationStore();
const items = ref<Course[]>([]);
const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.courses(organizationId);
});
</script>
