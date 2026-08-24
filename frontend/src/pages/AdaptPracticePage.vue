<template>
  <div class="adapt-workspace" data-testid="adapt-practice-page">
    <RouterLink
      v-if="lessonId"
      class="back-link"
      :to="{ name: 'academy-lesson-detail', params: { lessonId } }"
    >
      ← Back to lesson
    </RouterLink>
    <RouterLink v-else class="back-link" to="/academy/community-safety">
      ← Back to Community Safety
    </RouterLink>

    <header class="adapt-hero">
      <p class="eyebrow">Adaptive Learning</p>
      <h1>ADAPT Practice</h1>
      <p>
        ADAPT challenges adapt based on your answers, confidence, and reasoning — not a fixed quiz.
        Each response shapes what comes next.
      </p>
    </header>

    <p v-if="error" class="error">{{ error }}</p>
    <LoadingState v-else-if="isLoading" message="Loading adaptive practice…" />

    <div v-else-if="!available" class="adapt-unavailable-panel">
      <p class="muted" data-testid="adapt-unavailable-message">{{ unavailableMessage }}</p>
    </div>

    <div v-else-if="challenge" class="adapt-layout">
      <main class="adapt-main">
        <section class="adapt-challenge-panel" data-testid="adapt-challenge">
          <h2>Challenge</h2>
          <span v-if="challenge.difficulty_label" class="adapt-difficulty">
            {{ challenge.difficulty_label }}
          </span>
          <p class="adapt-prompt">{{ challenge.prompt }}</p>

          <fieldset class="adapt-choices" data-testid="adapt-choices">
            <legend>Choose an answer</legend>
            <label v-for="choice in challenge.choices" :key="choice" class="adapt-choice">
              <input v-model="answer" type="radio" name="adapt-answer" :value="choice" />
              <span>{{ choice }}</span>
            </label>
          </fieldset>

          <label class="field">
            <span>Confidence (1–5)</span>
            <select v-model.number="confidence" data-testid="adapt-confidence">
              <option v-for="level in confidenceOptions" :key="level" :value="level">
                {{ level }}
              </option>
            </select>
          </label>

          <label class="field">
            <span>Reasoning</span>
            <textarea
              v-model="reasoning"
              data-testid="adapt-reasoning"
              placeholder="How did you arrive at this answer?"
              rows="4"
            />
          </label>

          <p v-if="submitError" class="error">{{ submitError }}</p>

          <div class="actions">
            <button
              class="button"
              type="button"
              data-testid="submit-adapt-response"
              :disabled="busy || !answer"
              @click="submit"
            >
              Submit response
            </button>
          </div>
        </section>

        <section v-if="lastResult" class="adapt-feedback-panel" data-testid="adapt-feedback">
          <div v-if="noticedText" class="adapt-noticed-panel" data-testid="adapt-noticed">
            <h2>What ADAPT noticed</h2>
            <p class="adapt-block-body">{{ noticedText }}</p>
          </div>
          <div v-if="whyText" class="adapt-why-panel" data-testid="adapt-why">
            <h2>Why this question?</h2>
            <p class="adapt-block-body">{{ whyText }}</p>
          </div>
          <div v-if="nextChallenge" class="adapt-next-panel" data-testid="adapt-next-challenge">
            <h2>Next challenge from ADAPT</h2>
            <p class="adapt-block-body">{{ nextChallenge.prompt }}</p>
            <button class="button secondary" type="button" @click="continueWithNext">
              Continue with next challenge
            </button>
          </div>
          <p v-if="lastResult.complete" class="muted" data-testid="adapt-complete">
            Adaptive practice complete.
          </p>
        </section>
      </main>

      <aside class="adapt-sidebar">
        <div v-if="challenge || lastResult" class="adapt-loop-panel">
          <p class="section-label">The adaptive loop</p>
          <WorkflowSteps
            :steps="adaptLoopSteps"
            aria-label="ADAPT adaptive learning loop"
            data-testid="adapt-loop-workflow"
          />
        </div>
      </aside>
    </div>

    <div v-else-if="!isLoading && available && !challenge" class="adapt-unavailable-panel">
      <p class="muted">No challenge is available for this session.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import WorkflowSteps from '@/components/ui/WorkflowSteps.vue';
import LoadingState from '@/components/ui/LoadingState.vue';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type {
  AdaptChallenge,
  AdaptFeedbackPayload,
  AdaptLearningSessionRecord,
} from '@/types';
import { ADAPT_UNAVAILABLE_MESSAGE, formatAdaptBlock } from '@/utils/education';

const route = useRoute();
const organization = useOrganizationStore();

const isLoading = ref(true);
const busy = ref(false);
const error = ref('');
const submitError = ref('');
const available = ref(true);
const unavailableMessage = ref(ADAPT_UNAVAILABLE_MESSAGE);
const session = ref<AdaptLearningSessionRecord | null>(null);
const challenge = ref<AdaptChallenge | null>(null);
const lastResult = ref<AdaptFeedbackPayload | null>(null);
const answer = ref('');
const confidence = ref(3);
const reasoning = ref('');

const lessonId = computed(() => {
  const fromQuery = route.query.lessonId;
  if (typeof fromQuery === 'string' && fromQuery) {
    return fromQuery;
  }
  return session.value?.academy_lesson_id ? String(session.value.academy_lesson_id) : '';
});

const confidenceOptions = [1, 2, 3, 4, 5];

const adaptLoopSteps = ['Your response', 'What ADAPT noticed', 'Feedback', 'Next challenge'];

const noticedText = computed(() => formatAdaptBlock(lastResult.value?.noticed));
const whyText = computed(() => formatAdaptBlock(lastResult.value?.why_this_question));
const nextChallenge = computed(() => lastResult.value?.next_challenge ?? null);

function resetForm(): void {
  answer.value = '';
  confidence.value = 3;
  reasoning.value = '';
}

function applyChallenge(next: AdaptChallenge | null | undefined): void {
  challenge.value = next ?? null;
  resetForm();
}

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const sessionId = Number(route.params.sessionId);

  if (!organizationId || !sessionId) {
    return;
  }

  isLoading.value = true;
  error.value = '';
  submitError.value = '';

  try {
    const response = await communityApi.adaptSession(organizationId, sessionId);
    session.value = response.session;
    available.value = response.available;

    if (!response.available) {
      unavailableMessage.value = response.message || ADAPT_UNAVAILABLE_MESSAGE;
      challenge.value = null;
      return;
    }

    unavailableMessage.value = ADAPT_UNAVAILABLE_MESSAGE;
    lastResult.value = response.last_result ?? null;
    applyChallenge(response.adapt?.challenge ?? response.last_result?.next_challenge ?? null);
  } catch {
    error.value = 'Unable to load this adaptive practice session.';
    available.value = false;
  } finally {
    isLoading.value = false;
  }
}

async function submit(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const sessionId = session.value?.id;

  if (!organizationId || !sessionId || !answer.value) {
    return;
  }

  busy.value = true;
  submitError.value = '';

  try {
    const response = await communityApi.submitAdaptResponse(organizationId, sessionId, {
      answer: answer.value,
      confidence: confidence.value,
      reasoning: reasoning.value || undefined,
      challenge_id: challenge.value?.challenge_id ?? undefined,
    });

    session.value = response.session;
    available.value = response.available;

    if (!response.available) {
      unavailableMessage.value = response.message || ADAPT_UNAVAILABLE_MESSAGE;
      challenge.value = null;
      return;
    }

    lastResult.value = response.result ?? null;

    if (response.result?.next_challenge) {
      // Keep current challenge visible until the learner continues.
    } else if (response.result?.complete) {
      challenge.value = response.result.challenge;
    }
  } catch {
    submitError.value = 'Unable to submit your adaptive practice response.';
  } finally {
    busy.value = false;
  }
}

function continueWithNext(): void {
  if (!nextChallenge.value) {
    return;
  }
  applyChallenge(nextChallenge.value);
  lastResult.value = lastResult.value
    ? { ...lastResult.value, next_challenge: null }
    : null;
}

watch(
  () => [organization.currentOrganization?.id, route.params.sessionId],
  () => {
    void load();
  },
  { immediate: true },
);
</script>
