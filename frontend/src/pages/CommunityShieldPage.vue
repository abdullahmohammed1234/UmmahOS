<template>
  <section class="shield stack">
    <article class="panel content hero">
      <p class="eyebrow">Community Shield</p>
      <h1>See something harmful or concerning in an online space?</h1>
      <p class="lede">
        You can submit a report to
        {{ organization.currentOrganization?.name ?? 'your MSA' }}'s authorized Community Shield
        team. Reports stay inside this organization and are not visible to other members.
      </p>
      <div class="actions">
        <button
          v-if="view === 'landing'"
          class="button"
          type="button"
          data-testid="report-concern-cta"
          @click="startReport"
        >
          Report a Concern
        </button>
        <RouterLink
          v-if="organization.canManageIncidents"
          class="button secondary"
          to="/admin/community-shield"
          data-testid="admin-review-link"
        >
          Review Reports
        </RouterLink>
      </div>
    </article>

    <article v-if="view === 'confirmation' && submitted" class="panel content stack" data-testid="report-confirmation">
      <h2>Report submitted</h2>
      <p>
        Your report has been received by your MSA's Community Shield team.
      </p>
      <dl class="summary">
        <div>
          <dt>Report ID</dt>
          <dd>#{{ submitted.id }}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{{ statusLabel(submitted.status) }}</dd>
        </div>
        <div>
          <dt>Platform</dt>
          <dd>{{ platformLabel(submitted.platform) }}</dd>
        </div>
        <div>
          <dt>Content type</dt>
          <dd>{{ contentTypeLabel(submitted.content_type) }}</dd>
        </div>
        <div>
          <dt>Where was it?</dt>
          <dd>{{ visibilityLabel(submitted.visibility) }}</dd>
        </div>
      </dl>
      <p class="muted">{{ confirmationMessage }}</p>
      <button class="button secondary" type="button" @click="startReport">Submit another report</button>
    </article>

    <article v-else-if="view === 'form'" class="panel content stack" data-testid="report-form">
      <div>
        <h2>Report a Concern</h2>
        <p class="muted">
          Share enough structured context for your MSA team to understand where this happened.
          Do not include unnecessary private details.
        </p>
      </div>

      <fieldset class="choice-group">
        <legend>Platform</legend>
        <label v-for="option in PLATFORM_OPTIONS" :key="option.value" class="choice">
          <input v-model="platform" type="radio" name="platform" :value="option.value" required />
          <span>{{ option.label }}</span>
        </label>
        <p class="hint">{{ platformContentHint(platform) }}</p>
      </fieldset>

      <fieldset class="choice-group">
        <legend>Content type</legend>
        <label v-for="option in CONTENT_TYPE_OPTIONS" :key="option.value" class="choice">
          <input
            v-model="contentType"
            type="radio"
            name="content_type"
            :value="option.value"
            required
          />
          <span>{{ option.label }}</span>
        </label>
      </fieldset>

      <fieldset class="choice-group">
        <legend>Where was it?</legend>
        <label v-for="option in VISIBILITY_OPTIONS" :key="option.value" class="choice">
          <input
            v-model="visibility"
            type="radio"
            name="visibility"
            :value="option.value"
            required
          />
          <span>{{ option.label }}</span>
        </label>
        <p v-if="selectedVisibility" class="hint" data-testid="visibility-hint">
          {{ selectedVisibility.hint }}
        </p>
      </fieldset>

      <label class="field">
        <span>Source URL (optional)</span>
        <input
          v-model="sourceUrl"
          type="url"
          placeholder="https://"
          :required="false"
          data-testid="source-url"
        />
        <span v-if="visibility === 'private'" class="hint">
          Private or direct content often has no public URL. You can leave this blank.
        </span>
      </label>

      <label class="field">
        <span>What happened?</span>
        <textarea
          v-model="description"
          required
          maxlength="8000"
          data-testid="description"
          placeholder="Describe what you saw and why it concerns you."
        ></textarea>
      </label>

      <p v-if="error" class="error" data-testid="form-error">{{ error }}</p>

      <div class="actions">
        <button class="button" type="button" :disabled="isSubmitting" @click="onSubmit">
          {{ isSubmitting ? 'Submitting…' : 'Submit Report' }}
        </button>
        <button class="button secondary" type="button" :disabled="isSubmitting" @click="view = 'landing'">
          Cancel
        </button>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type {
  CommunityShieldContentType,
  CommunityShieldPlatform,
  CommunityShieldVisibility,
  Incident,
} from '@/types';
import {
  CONTENT_TYPE_OPTIONS,
  PLATFORM_OPTIONS,
  VISIBILITY_OPTIONS,
  contentTypeLabel,
  platformContentHint,
  platformLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';

const organization = useOrganizationStore();
const view = ref<'landing' | 'form' | 'confirmation'>('landing');
const platform = ref<CommunityShieldPlatform | ''>('');
const contentType = ref<CommunityShieldContentType | ''>('');
const visibility = ref<CommunityShieldVisibility | ''>('');
const sourceUrl = ref('');
const description = ref('');
const confirmationMessage = ref('');
const submitted = ref<Incident | null>(null);
const error = ref('');
const isSubmitting = ref(false);

const selectedVisibility = computed(
  () => VISIBILITY_OPTIONS.find((option) => option.value === visibility.value) ?? null,
);

function resetForm(): void {
  platform.value = '';
  contentType.value = '';
  visibility.value = '';
  sourceUrl.value = '';
  description.value = '';
  error.value = '';
}

function startReport(): void {
  resetForm();
  submitted.value = null;
  confirmationMessage.value = '';
  view.value = 'form';
}

async function onSubmit(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId) {
    error.value = 'No current organization.';
    return;
  }

  if (!platform.value || !contentType.value || !visibility.value || !description.value.trim()) {
    error.value = 'Platform, content type, visibility, and description are required.';
    return;
  }

  isSubmitting.value = true;
  error.value = '';

  try {
    const result = await communityApi.reportIncident(organizationId, {
      platform: platform.value,
      content_type: contentType.value,
      visibility: visibility.value,
      source_url: sourceUrl.value.trim() || null,
      description: description.value.trim(),
    });
    submitted.value = result.incident;
    confirmationMessage.value = result.message;
    view.value = 'confirmation';
    resetForm();
  } catch (err: unknown) {
    const responseErrors =
      err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { errors?: Record<string, string[]>; message?: string } } })
            .response?.data
        : undefined;

    if (responseErrors?.errors) {
      error.value = Object.values(responseErrors.errors).flat().join(' ');
    } else {
      error.value = responseErrors?.message ?? 'Unable to submit this report.';
    }
  } finally {
    isSubmitting.value = false;
  }
}

watch(
  () => organization.currentOrganization?.id,
  () => {
    view.value = 'landing';
    submitted.value = null;
    confirmationMessage.value = '';
    resetForm();
  },
);
</script>

<style scoped>
.shield {
  max-width: 760px;
}

.hero {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(31, 107, 74, 0.12), transparent 42%),
    linear-gradient(180deg, #fffdf8, #f7f3ea);
}

.hero::after {
  content: '';
  position: absolute;
  inset: auto -10% -40% auto;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(31, 107, 74, 0.08);
  pointer-events: none;
}

.eyebrow {
  margin: 0 0 0.4rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.78rem;
  color: var(--accent);
}

h1,
h2 {
  margin: 0 0 0.75rem;
}

.lede {
  margin: 0 0 1.1rem;
  max-width: 38rem;
  line-height: 1.5;
}

.choice-group {
  margin: 0;
  padding: 0;
  border: 0;
  display: grid;
  gap: 0.55rem;
}

.choice-group legend {
  margin-bottom: 0.35rem;
  font-weight: 600;
}

.choice {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
}

.choice:has(input:checked) {
  border-color: rgba(31, 107, 74, 0.55);
  background: rgba(31, 107, 74, 0.06);
}

.hint {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.summary {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.summary div {
  display: grid;
  grid-template-columns: 8rem 1fr;
  gap: 0.5rem;
}

.summary dt {
  color: var(--muted);
}

.summary dd {
  margin: 0;
}
</style>
