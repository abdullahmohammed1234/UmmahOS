<template>
  <section class="shield stack">
    <article class="panel content hero">
      <p class="eyebrow">Community Shield</p>
      <h1>See something harmful or concerning in an online space?</h1>
      <p class="lede">
        You can submit a report to
        {{ organization.currentOrganization?.name ?? 'your MSA' }}'s authorized Community Shield
        team. Preserve the item, surrounding context, and related copies — not just a screenshot.
        Reports stay inside this organization and are not visible to other members.
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
          v-if="organization.canReviewIncidents"
          class="button secondary"
          to="/community-shield/review-queue"
          data-testid="review-queue-link"
        >
          Open Review Queue
        </RouterLink>
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
        <div>
          <dt>Language</dt>
          <dd>{{ languageLabel(submitted.language) }}</dd>
        </div>
      </dl>
      <p class="muted">{{ confirmationMessage }}</p>
      <button class="button secondary" type="button" @click="startReport">Submit another report</button>
    </article>

    <article v-else-if="view === 'form'" class="panel content stack" data-testid="report-form">
      <div>
        <h2>Report a Concern</h2>
        <p class="muted">
          Required fields identify what you are reporting. Optional sections help reviewers
          understand surrounding context. Only provide information necessary to help authorized
          reviewers understand the concern.
        </p>
      </div>

      <aside class="completeness" data-testid="context-completeness" aria-label="Context captured">
        <p class="section-label">Context captured</p>
        <ul>
          <li :class="{ done: !!platform }">Platform</li>
          <li :class="{ done: !!contentType }">Content type</li>
          <li :class="{ done: !!visibility }">Visibility</li>
          <li :class="{ done: hasOriginalItem }">Original item</li>
          <li :class="{ done: !!sourceUrl.trim() }">Source reference</li>
          <li :class="{ done: !!observedAt || !!originalPostedAt }">Timestamp</li>
          <li :class="{ done: !!surroundingContext.trim() }">Surrounding context</li>
          <li :class="{ done: replies.length > 0 }">Replies</li>
          <li :class="{ done: relatedItems.length > 0 }">Related copies</li>
          <li :class="{ done: !!language && language !== 'unknown' }">Language</li>
          <li :class="{ done: !!reporterNotes.trim() }">Reporter notes</li>
        </ul>
        <p class="hint">Missing information is acceptable. You can still submit.</p>
      </aside>

      <section class="form-section" data-testid="section-what">
        <h3>1. What are you reporting?</h3>
        <p class="required-note">Required</p>

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
          <span>What happened? <em class="req">Required</em></span>
          <textarea
            v-model="description"
            required
            maxlength="8000"
            data-testid="description"
            placeholder="Describe what you saw and why it concerns you."
          ></textarea>
        </label>
      </section>

      <section class="form-section" data-testid="section-original-item">
        <h3>2. Original item</h3>
        <p class="optional-note">Optional — provide what you know</p>

        <label class="field">
          <span>Item title / label</span>
          <input v-model="originalItemTitle" type="text" maxlength="255" data-testid="original-item-title" />
        </label>

        <label class="field">
          <span>Content</span>
          <textarea
            v-model="originalItemContent"
            maxlength="16000"
            data-testid="original-item-content"
            placeholder="Paste or type the reported content as text. Do not paste passwords or private credentials."
          ></textarea>
        </label>

        <label class="field">
          <span>Author / account reference</span>
          <input
            v-model="originalItemAuthor"
            type="text"
            maxlength="255"
            data-testid="original-item-author"
            placeholder="@handle or display name"
          />
        </label>

        <label class="field">
          <span>Original posted time</span>
          <input
            v-model="originalPostedAt"
            type="datetime-local"
            data-testid="original-item-posted-at"
          />
        </label>
      </section>

      <section class="form-section" data-testid="section-source">
        <h3>3. Source &amp; when you saw it</h3>
        <p class="optional-note">Optional</p>

        <label class="field">
          <span>Source URL / reference</span>
          <input
            v-model="sourceUrl"
            type="url"
            placeholder="https://"
            data-testid="source-url"
          />
          <span v-if="visibility === 'private'" class="hint">
            Private or direct content often has no public URL. You can leave this blank.
          </span>
          <span v-else class="hint">
            A source reference identifies where the reported item can be found or was originally observed.
          </span>
        </label>

        <label class="field">
          <span>When did you observe it?</span>
          <input v-model="observedAt" type="datetime-local" data-testid="observed-at" />
          <span class="hint">If left blank, submission time is recorded as the observation time.</span>
        </label>
      </section>

      <section class="form-section" data-testid="section-context">
        <h3>4. Surrounding context</h3>
        <p class="optional-note">Optional</p>

        <label class="field">
          <span>What happened around the reported item?</span>
          <textarea
            v-model="surroundingContext"
            maxlength="8000"
            data-testid="surrounding-context"
            placeholder="What happened before or after? What was the conversation about?"
          ></textarea>
          <span class="hint">
            Include relevant conversation or events that help explain the reported content. Avoid
            adding unnecessary personal information.
          </span>
        </label>
      </section>

      <section class="form-section" data-testid="section-replies">
        <div class="section-head">
          <div>
            <h3>5. Replies</h3>
            <p class="optional-note">Optional evidence records — not a full conversation thread</p>
          </div>
          <button class="button secondary small" type="button" data-testid="add-reply" @click="addReply">
            + Add reply
          </button>
        </div>

        <div v-if="replies.length === 0" class="empty-hint">No replies added.</div>
        <div
          v-for="(reply, index) in replies"
          :key="reply.key"
          class="nested-item"
          data-testid="reply-item"
        >
          <div class="nested-head">
            <strong>Reply {{ index + 1 }}</strong>
            <button class="linkish" type="button" @click="removeReply(index)">Remove</button>
          </div>
          <label class="field">
            <span>Author</span>
            <input v-model="reply.author" type="text" maxlength="255" />
          </label>
          <label class="field">
            <span>Posted at</span>
            <input v-model="reply.posted_at" type="datetime-local" />
          </label>
          <label class="field">
            <span>Content</span>
            <textarea v-model="reply.content" maxlength="8000" required></textarea>
          </label>
        </div>
      </section>

      <section class="form-section" data-testid="section-related">
        <div class="section-head">
          <div>
            <h3>6. Related copies / similar occurrences</h3>
            <p class="optional-note">Optional — record cross-platform repetition manually</p>
          </div>
          <button
            class="button secondary small"
            type="button"
            data-testid="add-related-item"
            @click="addRelatedItem"
          >
            + Add related item
          </button>
        </div>

        <div v-if="relatedItems.length === 0" class="empty-hint">No related copies added.</div>
        <div
          v-for="(item, index) in relatedItems"
          :key="item.key"
          class="nested-item"
          data-testid="related-item"
        >
          <div class="nested-head">
            <strong>Related item {{ index + 1 }}</strong>
            <button class="linkish" type="button" @click="removeRelatedItem(index)">Remove</button>
          </div>
          <label class="field">
            <span>Platform</span>
            <select v-model="item.platform">
              <option disabled value="">Select platform</option>
              <option v-for="option in PLATFORM_OPTIONS" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Content type</span>
            <select v-model="item.content_type">
              <option disabled value="">Select type</option>
              <option
                v-for="option in CONTENT_TYPE_OPTIONS"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Reference URL</span>
            <input v-model="item.reference_url" type="url" placeholder="https://" />
          </label>
          <label class="field">
            <span>What is related?</span>
            <textarea v-model="item.description" maxlength="4000"></textarea>
          </label>
          <label class="field">
            <span>Observed at</span>
            <input v-model="item.observed_at" type="datetime-local" />
          </label>
        </div>
      </section>

      <section class="form-section" data-testid="section-additional">
        <h3>7. Additional information</h3>
        <p class="optional-note">Optional</p>

        <label class="field">
          <span>Language</span>
          <select v-model="language" data-testid="language">
            <option v-for="option in LANGUAGE_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Reporter notes</span>
          <textarea
            v-model="reporterNotes"
            maxlength="4000"
            data-testid="reporter-notes"
            placeholder="Anything else reviewers should know (separate from the description)."
          ></textarea>
          <span class="hint">
            For private or group content, share only what is necessary. Do not include passwords,
            authentication tokens, or private account credentials.
          </span>
        </label>
      </section>

      <p v-if="error" class="error" data-testid="form-error">{{ error }}</p>

      <div class="actions">
        <button class="button" type="button" :disabled="isSubmitting" data-testid="submit-report" @click="onSubmit">
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
  CommunityShieldLanguage,
  CommunityShieldPlatform,
  CommunityShieldVisibility,
  Incident,
} from '@/types';
import {
  CONTENT_TYPE_OPTIONS,
  LANGUAGE_OPTIONS,
  PLATFORM_OPTIONS,
  VISIBILITY_OPTIONS,
  contentTypeLabel,
  fromDatetimeLocalValue,
  languageLabel,
  platformContentHint,
  platformLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';

interface DraftReply {
  key: string;
  author: string;
  content: string;
  posted_at: string;
}

interface DraftRelatedItem {
  key: string;
  platform: CommunityShieldPlatform | '';
  content_type: CommunityShieldContentType | '';
  reference_url: string;
  description: string;
  observed_at: string;
}

let draftKey = 0;
function nextKey(prefix: string): string {
  draftKey += 1;
  return `${prefix}-${draftKey}`;
}

const organization = useOrganizationStore();
const view = ref<'landing' | 'form' | 'confirmation'>('landing');
const platform = ref<CommunityShieldPlatform | ''>('');
const contentType = ref<CommunityShieldContentType | ''>('');
const visibility = ref<CommunityShieldVisibility | ''>('');
const sourceUrl = ref('');
const description = ref('');
const originalItemTitle = ref('');
const originalItemContent = ref('');
const originalItemAuthor = ref('');
const originalPostedAt = ref('');
const observedAt = ref('');
const surroundingContext = ref('');
const replies = ref<DraftReply[]>([]);
const relatedItems = ref<DraftRelatedItem[]>([]);
const language = ref<CommunityShieldLanguage>('unknown');
const reporterNotes = ref('');
const confirmationMessage = ref('');
const submitted = ref<Incident | null>(null);
const error = ref('');
const isSubmitting = ref(false);

const selectedVisibility = computed(
  () => VISIBILITY_OPTIONS.find((option) => option.value === visibility.value) ?? null,
);

const hasOriginalItem = computed(
  () =>
    !!originalItemTitle.value.trim() ||
    !!originalItemContent.value.trim() ||
    !!originalItemAuthor.value.trim() ||
    !!originalPostedAt.value,
);

function resetForm(): void {
  platform.value = '';
  contentType.value = '';
  visibility.value = '';
  sourceUrl.value = '';
  description.value = '';
  originalItemTitle.value = '';
  originalItemContent.value = '';
  originalItemAuthor.value = '';
  originalPostedAt.value = '';
  observedAt.value = '';
  surroundingContext.value = '';
  replies.value = [];
  relatedItems.value = [];
  language.value = 'unknown';
  reporterNotes.value = '';
  error.value = '';
}

function startReport(): void {
  resetForm();
  submitted.value = null;
  confirmationMessage.value = '';
  view.value = 'form';
}

function addReply(): void {
  replies.value.push({
    key: nextKey('reply'),
    author: '',
    content: '',
    posted_at: '',
  });
}

function removeReply(index: number): void {
  replies.value.splice(index, 1);
}

function addRelatedItem(): void {
  relatedItems.value.push({
    key: nextKey('related'),
    platform: '',
    content_type: '',
    reference_url: '',
    description: '',
    observed_at: '',
  });
}

function removeRelatedItem(index: number): void {
  relatedItems.value.splice(index, 1);
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

  for (const reply of replies.value) {
    if (!reply.content.trim()) {
      error.value = 'Each reply needs content, or remove empty replies.';
      return;
    }
  }

  for (const item of relatedItems.value) {
    if (!item.platform || !item.content_type) {
      error.value = 'Each related item needs a platform and content type, or remove incomplete items.';
      return;
    }
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
      original_item_title: originalItemTitle.value.trim() || null,
      original_item_content: originalItemContent.value.trim() || null,
      original_item_author: originalItemAuthor.value.trim() || null,
      original_item_posted_at: fromDatetimeLocalValue(originalPostedAt.value),
      observed_at: fromDatetimeLocalValue(observedAt.value),
      surrounding_context: surroundingContext.value.trim() || null,
      language: language.value,
      reporter_notes: reporterNotes.value.trim() || null,
      replies: replies.value.map((reply, index) => ({
        author: reply.author.trim() || null,
        content: reply.content.trim(),
        posted_at: fromDatetimeLocalValue(reply.posted_at),
        position: index,
      })),
      related_items: relatedItems.value.map((item) => ({
        platform: item.platform as CommunityShieldPlatform,
        content_type: item.content_type as CommunityShieldContentType,
        reference_url: item.reference_url.trim() || null,
        description: item.description.trim() || null,
        observed_at: fromDatetimeLocalValue(item.observed_at),
      })),
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
  max-width: 820px;
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
h2,
h3 {
  margin: 0 0 0.75rem;
}

h3 {
  margin-bottom: 0.35rem;
}

.lede {
  margin: 0 0 1.1rem;
  max-width: 40rem;
  line-height: 1.5;
}

.form-section {
  display: grid;
  gap: 0.85rem;
  padding: 1rem 0 0.25rem;
  border-top: 1px solid var(--line);
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.required-note,
.optional-note {
  margin: 0 0 0.35rem;
  font-size: 0.88rem;
  color: var(--muted);
}

.req {
  font-style: normal;
  font-size: 0.82rem;
  color: var(--muted);
  font-weight: 500;
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

.empty-hint {
  color: var(--muted);
  font-size: 0.92rem;
}

.nested-item {
  display: grid;
  gap: 0.7rem;
  padding: 0.85rem;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
}

.nested-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.linkish {
  border: 0;
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  padding: 0;
}

.button.small {
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
}

.completeness {
  padding: 0.9rem 1rem;
  border: 1px solid rgba(31, 107, 74, 0.18);
  border-radius: 14px;
  background: rgba(31, 107, 74, 0.05);
}

.section-label {
  margin: 0 0 0.55rem;
  font-weight: 600;
}

.completeness ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  gap: 0.35rem 0.75rem;
}

.completeness li {
  color: var(--muted);
  font-size: 0.9rem;
}

.completeness li::before {
  content: '○ ';
}

.completeness li.done {
  color: #1b5e41;
}

.completeness li.done::before {
  content: '✓ ';
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

@media (max-width: 640px) {
  .section-head {
    flex-direction: column;
  }

  .summary div {
    grid-template-columns: 1fr;
  }
}
</style>
