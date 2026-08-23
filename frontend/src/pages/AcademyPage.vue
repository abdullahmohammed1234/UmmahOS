<template>
  <section class="panel content stack">
    <div>
      <h1>Academy</h1>
      <p class="muted">
        Published courses for {{ organization.currentOrganization?.name ?? 'this organization' }}.
        This is an organization-scoped entry point, not a full LMS.
      </p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading courses…</p>
    <p v-else-if="items.length === 0" class="muted">No published courses yet.</p>
    <div v-else class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="panel card-link"
        :to="{ name: 'course-detail', params: { id: item.id } }"
      >
        <strong>{{ item.title }}</strong>
        <p class="muted">{{ item.description }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { Course } from '@/types';

const items = ref<Course[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.courses(organizationId);
});
</script>
