<template>
  <div class="academy-workspace" data-testid="academy-progress-page">
    <header class="academy-hero">
      <p class="eyebrow">Your learning</p>
      <h1>My Progress</h1>
      <p>Community safety lesson progress in this organization.</p>
    </header>

    <AcademySubNav />

    <p v-if="error" class="error">{{ error }}</p>
    <LoadingState v-else-if="isLoading" message="Loading progress…" />
    <EmptyState
      v-else-if="items.length === 0"
      title="No lesson progress yet"
      description="Start a Community Safety lesson to track your progress here."
      icon="📈"
    />
    <div v-else class="progress-table-wrap">
      <table class="progress-table" data-testid="academy-progress-table">
        <thead>
          <tr>
            <th>Lesson</th>
            <th>Status</th>
            <th>Started</th>
            <th>Completed</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>
              <RouterLink
                v-if="item.lesson"
                :to="{ name: 'academy-lesson-detail', params: { lessonId: item.lesson.id } }"
              >
                {{ item.lesson.title }}
              </RouterLink>
              <span v-else>Lesson #{{ item.academy_lesson_id }}</span>
            </td>
            <td>
              <span class="progress-status" :class="{ completed: item.status === 'completed' }">
                {{ item.status }}
              </span>
            </td>
            <td>{{ formatDateTime(item.started_at) }}</td>
            <td>{{ formatDateTime(item.completed_at) }}</td>
          </tr>
        </tbody>
      </table>
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
import type { AcademyLessonProgress } from '@/types';
import { formatDateTime } from '@/utils/date';

const items = ref<AcademyLessonProgress[]>([]);
const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.academyProgress(organizationId);
});
</script>
