<template>
  <section class="panel content stack" data-testid="community-safety-page">
    <div>
      <h1>Community Safety</h1>
      <p class="muted">
        Lessons that help members recognize harmful patterns and document context carefully.
      </p>
    </div>
    <AcademySubNav />
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading community safety lessons…</p>
    <p v-else-if="items.length === 0" class="muted">No community safety lessons published yet.</p>
    <div v-else class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="panel card-link"
        :to="{ name: 'academy-lesson-detail', params: { lessonId: item.id } }"
        data-testid="community-safety-lesson"
      >
        <strong>{{ item.title }}</strong>
        <p v-if="item.learning_objective" class="muted">{{ item.learning_objective }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import AcademySubNav from '@/components/AcademySubNav.vue';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { AcademyLesson } from '@/types';

const items = ref<AcademyLesson[]>([]);
const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.communitySafetyLessons(organizationId);
});
</script>
