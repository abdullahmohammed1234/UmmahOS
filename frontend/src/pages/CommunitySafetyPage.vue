<template>
  <div class="academy-workspace" data-testid="community-safety-page">
    <header class="academy-hero">
      <p class="eyebrow">Community Safety Education</p>
      <h1>Community Safety</h1>
      <p>
        Lessons that help members recognize harmful patterns and document context carefully —
        bridging confirmed Community Shield reviews to practical learning.
      </p>
    </header>

    <div class="academy-bridge">
      <div class="academy-bridge-flow" aria-hidden="true">
        <span>Community Safety Pattern</span>
        <span>↓</span>
        <span>Academy Lesson</span>
        <span>↓</span>
        <span>Scenario</span>
        <span>↓</span>
        <span>ADAPT Practice</span>
      </div>
      <p>
        <strong>From Community Shield to Academy.</strong> Validated patterns from human-reviewed
        incidents become lessons. ADAPT adapts practice based on your responses — not a fixed quiz.
      </p>
    </div>

    <AcademySubNav />

    <p v-if="error" class="error">{{ error }}</p>
    <LoadingState v-else-if="isLoading" message="Loading community safety lessons…" />
    <EmptyState
      v-else-if="items.length === 0"
      title="No community safety lessons yet"
      description="Published lessons will appear here once available."
      icon="🛡"
    />
    <div v-else class="academy-grid">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        class="academy-card"
        :to="{ name: 'academy-lesson-detail', params: { lessonId: item.id } }"
        data-testid="community-safety-lesson"
      >
        <span class="academy-card-meta">Lesson</span>
        <h2 class="academy-card-title">{{ item.title }}</h2>
        <p v-if="item.learning_objective" class="academy-card-desc">{{ item.learning_objective }}</p>
        <span class="academy-card-arrow">Open lesson →</span>
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
import type { AcademyLesson } from '@/types';

const items = ref<AcademyLesson[]>([]);
const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.communitySafetyLessons(organizationId);
});
</script>
