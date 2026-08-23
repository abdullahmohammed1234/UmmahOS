<template>
  <section class="panel content stack" data-testid="academy-lesson-detail">
    <RouterLink to="/academy/community-safety">Back to Community Safety</RouterLink>
    <AcademySubNav />

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading lesson…</p>

    <template v-else-if="lesson">
      <div>
        <p class="muted">{{ lesson.category }}</p>
        <h1>{{ lesson.title }}</h1>
        <p v-if="lesson.learning_objective" class="muted">{{ lesson.learning_objective }}</p>
      </div>

      <section
        v-for="(section, index) in lesson.sections"
        :key="`${section.heading}-${index}`"
        class="lesson-section"
      >
        <h2>{{ section.heading }}</h2>
        <p class="body">{{ section.body }}</p>
      </section>

      <p v-if="actionError" class="error">{{ actionError }}</p>
      <p v-if="actionStatus" class="muted">{{ actionStatus }}</p>
      <p v-if="adaptUnavailable" class="muted" data-testid="adapt-unavailable">
        {{ adaptUnavailable }}
      </p>

      <div class="actions">
        <button
          class="button"
          type="button"
          data-testid="start-adapt-practice"
          :disabled="busy"
          @click="startAdapt"
        >
          Start Adaptive Practice
        </button>
        <button
          class="button secondary"
          type="button"
          data-testid="mark-lesson-complete"
          :disabled="busy"
          @click="markComplete"
        >
          Mark complete
        </button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import AcademySubNav from '@/components/AcademySubNav.vue';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { AcademyLesson } from '@/types';
import { ADAPT_UNAVAILABLE_MESSAGE } from '@/utils/education';

const route = useRoute();
const router = useRouter();
const organization = useOrganizationStore();

const lesson = ref<AcademyLesson | null>(null);
const isLoading = ref(false);
const error = ref('');
const busy = ref(false);
const actionError = ref('');
const actionStatus = ref('');
const adaptUnavailable = ref('');

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const lessonId = Number(route.params.lessonId);

  if (!organizationId || !lessonId) {
    return;
  }

  isLoading.value = true;
  error.value = '';
  adaptUnavailable.value = '';

  try {
    lesson.value = await communityApi.academyLesson(organizationId, lessonId);
  } catch {
    lesson.value = null;
    error.value = 'This lesson is not available in the current organization.';
  } finally {
    isLoading.value = false;
  }
}

async function startAdapt(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const lessonId = lesson.value?.id;

  if (!organizationId || !lessonId) {
    return;
  }

  busy.value = true;
  actionError.value = '';
  actionStatus.value = '';
  adaptUnavailable.value = '';

  try {
    const response = await communityApi.startAdaptSession(organizationId, lessonId);

    if (!response.available) {
      adaptUnavailable.value = response.message || ADAPT_UNAVAILABLE_MESSAGE;
      return;
    }

    await router.push({
      name: 'academy-adapt-practice',
      params: { sessionId: response.session.id },
      query: { lessonId: String(lessonId) },
    });
  } catch {
    actionError.value = 'Unable to start adaptive practice.';
  } finally {
    busy.value = false;
  }
}

async function markComplete(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const lessonId = lesson.value?.id;

  if (!organizationId || !lessonId) {
    return;
  }

  busy.value = true;
  actionError.value = '';
  actionStatus.value = '';

  try {
    await communityApi.completeAcademyLesson(organizationId, lessonId);
    actionStatus.value = 'Lesson marked complete.';
  } catch {
    actionError.value = 'Unable to mark this lesson complete.';
  } finally {
    busy.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.lessonId],
  () => {
    void load();
  },
  { immediate: true },
);
</script>

<style scoped>
.lesson-section {
  padding-top: 0.75rem;
  border-top: 1px solid var(--line);
}

.lesson-section h2 {
  margin-bottom: 0.4rem;
}

.body {
  white-space: pre-wrap;
  line-height: 1.5;
}
</style>
