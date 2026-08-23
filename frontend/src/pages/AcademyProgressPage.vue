<template>
  <section class="panel content stack" data-testid="academy-progress-page">
    <div>
      <h1>My Progress</h1>
      <p class="muted">Your community safety lesson progress in this organization.</p>
    </div>
    <AcademySubNav />
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading progress…</p>
    <p v-else-if="items.length === 0" class="muted">No lesson progress yet.</p>
    <table v-else data-testid="academy-progress-table">
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
          <td>{{ item.status }}</td>
          <td>{{ formatDateTime(item.started_at) }}</td>
          <td>{{ formatDateTime(item.completed_at) }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import AcademySubNav from '@/components/AcademySubNav.vue';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { AcademyLessonProgress } from '@/types';
import { formatDateTime } from '@/utils/date';

const items = ref<AcademyLessonProgress[]>([]);
const { isLoading, error } = useOrganizationQuery(async (organizationId) => {
  items.value = await communityApi.academyProgress(organizationId);
});
</script>
