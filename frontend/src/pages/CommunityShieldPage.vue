<template>
  <div class="shield-page">
    <!-- Landing -->
    <section v-if="view === 'landing'" class="shield-landing">
      <div class="shield-hero">
        <div class="hero-glow" aria-hidden="true" />
        <div class="hero-content">
          <p class="eyebrow">Community Shield</p>
          <h1>Community Shield</h1>
          <p class="hero-subtitle">
            Document concerns with the context reviewers need.
          </p>
          <p class="hero-tagline">
            Preserve context. Protect people. Respond responsibly.
          </p>

          <div class="hero-actions">
            <button
              class="button large"
              type="button"
              data-testid="report-concern-cta"
              @click="startReport"
            >
              Report a Concern
            </button>
            <RouterLink
              class="button secondary large hero-secondary-btn"
              to="/community-shield/my-reports"
              data-testid="my-reports-cta"
            >
              View My Reports
            </RouterLink>
            <RouterLink
              v-if="organization.canReviewIncidents"
              class="button secondary large hero-secondary-btn"
              to="/community-shield/review-queue"
              data-testid="review-queue-link"
            >
              Open Review Queue
            </RouterLink>
            <RouterLink
              v-if="organization.canManageIncidents"
              class="button secondary large hero-secondary-btn"
              to="/admin/community-shield"
              data-testid="admin-review-link"
            >
              Review Reports
            </RouterLink>
          </div>
        </div>
      </div>

      <div class="shield-process-section">
        <p class="process-label">How it works</p>
        <ShieldProcessSteps
          :steps="['Capture', 'Review', 'Respond', 'Follow Up']"
          aria-label="Community Shield workflow"
        />
      </div>

      <article class="shield-intro panel content">
        <h2>What is Community Shield?</h2>
        <p class="intro-text">
          Community Shield helps members of
          {{ organization.currentOrganization?.name ?? 'your MSA' }} document concerning online
          content while preserving context for trained reviewers — not just a screenshot.
        </p>
        <p class="muted ai-principle">
          <strong>AI assists. Humans decide.</strong> AI analysis, when used, is advisory only.
          Trained human reviewers make all determinations.
        </p>
      </article>
    </section>

    <!-- Confirmation -->
    <article
      v-else-if="view === 'confirmation' && submitted"
      class="confirmation panel content"
      data-testid="report-confirmation"
    >
      <div class="confirmation-header">
        <div class="confirmation-icon" aria-hidden="true">✓</div>
        <div>
          <h2>Your report has been recorded</h2>
          <p>
            Reference <strong>#{{ submitted.id }}</strong> — your concern has been received by your
            MSA's Community Shield team.
          </p>
        </div>
      </div>

      <dl class="summary-grid">
        <div>
          <dt>Report reference</dt>
          <dd>#{{ submitted.id }}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd><span class="badge info">{{ statusLabel(submitted.status) }}</span></dd>
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
          <dt>Visibility</dt>
          <dd>{{ visibilityLabel(submitted.visibility) }}</dd>
        </div>
        <div>
          <dt>Language</dt>
          <dd>{{ languageLabel(submitted.language) }}</dd>
        </div>
      </dl>

      <div class="next-steps panel content">
        <h3>What happens next?</h3>
        <Timeline :items="confirmationTimeline" />
        <p class="muted ai-note">
          If AI analysis is used, it is <strong>advisory only</strong>. Trained human reviewers
          make all decisions about your report.
        </p>
      </div>

      <p class="muted">{{ confirmationMessage }}</p>
      <div class="actions">
        <RouterLink class="button" to="/community-shield/my-reports" data-testid="view-my-reports-cta">
          View My Reports
        </RouterLink>
        <button class="button secondary" type="button" @click="startReport">Submit another report</button>
      </div>
    </article>

    <!-- Report wizard -->
    <article v-else-if="view === 'form'" class="wizard panel" data-testid="report-form">
      <header class="wizard-header">
        <div>
          <p class="eyebrow">New report</p>
          <h2>Report a Concern</h2>
          <p class="muted wizard-intro">
            Provide what you know. Optional sections help reviewers understand surrounding context.
          </p>
        </div>
        <button class="button ghost small" type="button" @click="cancelReport">Cancel</button>
      </header>

      <div class="wizard-layout">
        <aside class="wizard-sidebar">
          <ReportWizardProgress
            :steps="wizardSteps"
            :current-step="currentStep"
            @go-to="goToStep"
          />
          <div class="completeness" data-testid="context-completeness" aria-label="Context captured">
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
          </div>
        </aside>

        <div class="wizard-body">
          <!-- Step 1: Platform -->
          <section v-show="currentStep === 0" class="wizard-step">
            <div class="step-header">
              <span class="step-badge">Step 01</span>
              <h3>Where did you see this?</h3>
              <p class="step-desc">Select the platform where the concerning content appeared.</p>
            </div>
            <fieldset class="tile-grid" data-testid="section-what">
              <legend class="sr-only">Platform</legend>
              <label
                v-for="option in PLATFORM_OPTIONS"
                :key="option.value"
                class="select-tile"
                :class="{ selected: platform === option.value }"
              >
                <input
                  v-model="platform"
                  type="radio"
                  name="platform"
                  :value="option.value"
                  required
                />
                <span class="tile-icon">{{ platformIcon(option.value) }}</span>
                <span class="tile-label">{{ option.label }}</span>
              </label>
            </fieldset>
            <p v-if="platform" class="hint">{{ platformContentHint(platform) }}</p>
          </section>

          <!-- Step 2: Content -->
          <section v-show="currentStep === 1" class="wizard-step">
            <div class="step-header">
              <span class="step-badge">Step 02</span>
              <h3>What type of content is it?</h3>
              <p class="step-desc">Choose the format that best describes what you are reporting.</p>
            </div>
            <fieldset class="tile-grid tile-grid-compact">
              <legend class="sr-only">Content type</legend>
              <label
                v-for="option in CONTENT_TYPE_OPTIONS"
                :key="option.value"
                class="select-tile select-tile-sm"
                :class="{ selected: contentType === option.value }"
              >
                <input
                  v-model="contentType"
                  type="radio"
                  name="content_type"
                  :value="option.value"
                  required
                />
                <span class="tile-label">{{ option.label }}</span>
              </label>
            </fieldset>
            <label class="field field-spacious">
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

          <!-- Step 3: Visibility -->
          <section v-show="currentStep === 2" class="wizard-step">
            <div class="step-header">
              <span class="step-badge">Step 03</span>
              <h3>Who could see it?</h3>
              <p class="step-desc">Visibility helps reviewers understand the reach of the content.</p>
            </div>
            <fieldset class="visibility-grid">
              <legend class="sr-only">Visibility</legend>
              <label
                v-for="option in VISIBILITY_OPTIONS"
                :key="option.value"
                class="visibility-tile"
                :class="{ selected: visibility === option.value }"
              >
                <input
                  v-model="visibility"
                  type="radio"
                  name="visibility"
                  :value="option.value"
                  required
                />
                <span class="visibility-label">{{ option.label }}</span>
                <span class="visibility-hint-text">{{ option.hint }}</span>
              </label>
            </fieldset>
            <p v-if="selectedVisibility" class="hint" data-testid="visibility-hint">
              {{ selectedVisibility.hint }}
            </p>
          </section>

          <!-- Step 4: Context -->
          <div v-show="currentStep === 3" class="wizard-step context-step">
            <div class="step-header">
              <span class="step-badge">Step 04</span>
              <h3>Add context reviewers need</h3>
              <p class="step-desc">
                Everything here is optional. More context helps — but you can submit with only the
                basics.
              </p>
            </div>

            <section class="context-block" data-testid="section-original-item">
              <h4>Original item</h4>
              <label class="field">
                <span>Item title / label</span>
                <input v-model="originalItemTitle" type="text" maxlength="255" data-testid="original-item-title" />
              </label>
              <label class="field field-spacious">
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

            <section class="context-block" data-testid="section-source">
              <h4>Source &amp; when you saw it</h4>
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
                  A source reference identifies where the reported item can be found.
                </span>
              </label>
              <label class="field">
                <span>When did you observe it?</span>
                <input v-model="observedAt" type="datetime-local" data-testid="observed-at" />
                <span class="hint">If left blank, submission time is recorded.</span>
              </label>
            </section>

            <section class="context-block" data-testid="section-context">
              <h4>Surrounding context</h4>
              <label class="field field-spacious">
                <span>What happened around the reported item?</span>
                <textarea
                  v-model="surroundingContext"
                  maxlength="8000"
                  data-testid="surrounding-context"
                  placeholder="What happened before or after? What was the conversation about?"
                ></textarea>
                <span class="hint">
                  Include relevant conversation that helps explain the reported content.
                </span>
              </label>
            </section>

            <section class="context-block" data-testid="section-replies">
              <div class="block-head">
                <div>
                  <h4>Replies</h4>
                  <p class="optional-note">Optional evidence records</p>
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
                <label class="field field-spacious">
                  <span>Content</span>
                  <textarea v-model="reply.content" maxlength="8000" required></textarea>
                </label>
              </div>
            </section>

            <section class="context-block" data-testid="section-related">
              <div class="block-head">
                <div>
                  <h4>Related copies / similar occurrences</h4>
                  <p class="optional-note">Optional — cross-platform repetition</p>
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

            <section class="context-block" data-testid="section-additional">
              <h4>Additional information</h4>
              <label class="field">
                <span>Language</span>
                <select v-model="language" data-testid="language">
                  <option v-for="option in LANGUAGE_OPTIONS" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </label>
              <label class="field field-spacious">
                <span>Reporter notes</span>
                <textarea
                  v-model="reporterNotes"
                  maxlength="4000"
                  data-testid="reporter-notes"
                  placeholder="Anything else reviewers should know."
                ></textarea>
                <span class="hint">
                  Do not include passwords, authentication tokens, or private account credentials.
                </span>
              </label>
            </section>
          </div>

          <!-- Step 5: Review -->
          <section v-show="currentStep === 4" class="wizard-step review-step">
            <div class="step-header">
              <span class="step-badge">Step 05</span>
              <h3>Review before submitting</h3>
              <p class="step-desc">This is what reviewers will receive.</p>
            </div>

            <div class="review-preview">
              <div class="preview-header">
                <span class="preview-label">Evidence package preview</span>
              </div>
              <dl class="preview-grid">
                <div>
                  <dt>Platform</dt>
                  <dd>{{ platform ? platformLabel(platform) : '—' }}</dd>
                </div>
                <div>
                  <dt>Content type</dt>
                  <dd>{{ contentType ? contentTypeLabel(contentType) : '—' }}</dd>
                </div>
                <div>
                  <dt>Visibility</dt>
                  <dd>{{ visibility ? visibilityLabel(visibility) : '—' }}</dd>
                </div>
                <div>
                  <dt>Language</dt>
                  <dd>{{ languageLabel(language) }}</dd>
                </div>
              </dl>
              <div v-if="description.trim()" class="preview-block">
                <h5>Description</h5>
                <p>{{ description }}</p>
              </div>
              <div v-if="originalItemContent.trim()" class="preview-block">
                <h5>Original item</h5>
                <p>{{ originalItemContent }}</p>
              </div>
              <div v-if="surroundingContext.trim()" class="preview-block">
                <h5>Surrounding context</h5>
                <p>{{ surroundingContext }}</p>
              </div>
              <div v-if="replies.length > 0" class="preview-block">
                <h5>Replies ({{ replies.length }})</h5>
              </div>
              <div v-if="relatedItems.length > 0" class="preview-block">
                <h5>Related copies ({{ relatedItems.length }})</h5>
              </div>
              <p class="preview-footer muted">
                Reviewers will see the full structured evidence. AI analysis, if run later, is
                advisory only.
              </p>
            </div>
          </section>

          <p v-if="error" class="error" data-testid="form-error">{{ error }}</p>

          <div class="wizard-nav">
            <button
              v-if="currentStep > 0"
              class="button secondary"
              type="button"
              @click="prevStep"
            >
              Back
            </button>
            <div class="nav-spacer" />
            <button
              v-if="currentStep < 4"
              class="button"
              type="button"
              @click="nextStep"
            >
              Continue
            </button>
            <button
              v-show="currentStep === 4"
              class="button"
              type="button"
              :disabled="isSubmitting"
              data-testid="submit-report"
              @click="onSubmit"
            >
              {{ isSubmitting ? 'Submitting…' : 'Submit Report' }}
            </button>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import ReportWizardProgress from '@/components/community-shield/ReportWizardProgress.vue';
import ShieldProcessSteps from '@/components/community-shield/ShieldProcessSteps.vue';
import Timeline from '@/components/ui/Timeline.vue';
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

const wizardSteps = [
  { id: 'platform', label: 'Platform', number: '01' },
  { id: 'content', label: 'Content', number: '02' },
  { id: 'visibility', label: 'Visibility', number: '03' },
  { id: 'context', label: 'Context', number: '04' },
  { id: 'review', label: 'Review', number: '05' },
];

const PLATFORM_ICONS: Record<CommunityShieldPlatform, string> = {
  x: 'X',
  youtube: 'YT',
  tiktok: 'TT',
  reddit: 'RD',
  discord: 'DC',
  telegram: 'TG',
  whatsapp: 'WA',
  other: '+',
};

let draftKey = 0;
function nextKey(prefix: string): string {
  draftKey += 1;
  return `${prefix}-${draftKey}`;
}

function platformIcon(value: CommunityShieldPlatform): string {
  return PLATFORM_ICONS[value] ?? '•';
}

const organization = useOrganizationStore();
const view = ref<'landing' | 'form' | 'confirmation'>('landing');
const currentStep = ref(0);
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

const confirmationTimeline = [
  { label: 'Report recorded', done: true, active: true },
  { label: 'Under review by trained reviewers', description: 'Your report enters the review queue.' },
  { label: 'Human decision', description: 'A reviewer makes an independent determination.' },
  { label: 'Outcome & follow-up', description: 'Track updates in My Reports.' },
];

function resetForm(): void {
  currentStep.value = 0;
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

function cancelReport(): void {
  view.value = 'landing';
  resetForm();
}

function goToStep(index: number): void {
  if (index <= currentStep.value) {
    currentStep.value = index;
    error.value = '';
  }
}

function validateStep(step: number): string | null {
  if (step === 0 && !platform.value) return 'Please select a platform.';
  if (step === 1) {
    if (!contentType.value) return 'Please select a content type.';
    if (!description.value.trim()) return 'Please describe what happened.';
  }
  if (step === 2 && !visibility.value) return 'Please select a visibility option.';
  return null;
}

function nextStep(): void {
  const stepError = validateStep(currentStep.value);
  if (stepError) {
    error.value = stepError;
    return;
  }
  error.value = '';
  if (currentStep.value < 4) currentStep.value += 1;
}

function prevStep(): void {
  error.value = '';
  if (currentStep.value > 0) currentStep.value -= 1;
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
.shield-page {
  max-width: 960px;
  margin: 0 auto;
}

/* Landing hero */
.shield-landing {
  display: grid;
  gap: var(--space-6);
}

.shield-hero {
  position: relative;
  padding: var(--space-10) var(--space-8);
  border-radius: var(--radius-2xl);
  background: var(--gradient-dark);
  color: var(--text-on-dark);
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  top: -30%;
  right: -15%;
  width: 55%;
  height: 120%;
  background: radial-gradient(circle, rgba(42, 157, 143, 0.18), transparent 65%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 36rem;
}

.shield-hero .eyebrow {
  color: var(--accent-mint);
  margin-bottom: var(--space-3);
}

.shield-hero h1 {
  font-size: clamp(2rem, 4vw, var(--text-4xl));
  color: var(--text-on-dark);
  margin-bottom: var(--space-3);
}

.hero-subtitle {
  font-size: var(--text-xl);
  color: var(--text-on-dark-muted);
  line-height: var(--leading-relaxed);
  margin: 0 0 var(--space-4);
}

.hero-tagline {
  font-size: var(--text-sm);
  color: var(--accent-mint);
  margin: 0 0 var(--space-6);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.hero-secondary-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: rgba(255, 255, 255, 0.25) !important;
  color: var(--text-on-dark) !important;
}

.hero-secondary-btn:hover {
  background: rgba(255, 255, 255, 0.14) !important;
}

.shield-process-section {
  padding: var(--space-6) var(--space-8);
  border-radius: var(--radius-xl);
  background: var(--forest-soft);
}

.process-label {
  margin: 0 0 var(--space-4);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-mint);
}

.shield-intro h2 {
  margin-top: 0;
  font-size: var(--text-xl);
}

.intro-text {
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-4);
}

.ai-principle {
  font-size: var(--text-sm);
  margin: 0;
}

/* Confirmation */
.confirmation-header {
  display: flex;
  gap: var(--space-5);
  align-items: flex-start;
  margin-bottom: var(--space-6);
}

.confirmation-icon {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  flex-shrink: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
  margin: 0 0 var(--space-6);
}

.summary-grid dt {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: var(--space-1);
}

.summary-grid dd {
  margin: 0;
  font-weight: var(--font-medium);
}

.next-steps {
  background: var(--primary-soft);
  border: 1px solid rgba(20, 92, 62, 0.15);
  margin-bottom: var(--space-5);
}

.next-steps h3 {
  margin-top: 0;
}

.ai-note {
  margin-top: var(--space-4);
  font-size: var(--text-sm);
}

/* Wizard */
.wizard {
  padding: 0;
  overflow: hidden;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.wizard-header h2 {
  margin: 0 0 var(--space-2);
}

.wizard-intro {
  margin: 0;
  font-size: var(--text-sm);
}

.wizard-layout {
  display: grid;
  grid-template-columns: minmax(220px, 260px) 1fr;
  min-height: 480px;
}

.wizard-sidebar {
  padding: var(--space-5) var(--space-4);
  border-right: 1px solid var(--border-subtle);
  background: var(--background-alt);
}

.wizard-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
}

.wizard-step {
  flex: 1;
}

.step-header {
  margin-bottom: var(--space-6);
}

.step-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: var(--font-bold);
  letter-spacing: 0.1em;
  color: var(--primary);
  margin-bottom: var(--space-2);
}

.step-header h3 {
  margin: 0 0 var(--space-2);
  font-size: var(--text-2xl);
}

.step-desc {
  margin: 0;
  color: var(--text-muted);
  line-height: var(--leading-relaxed);
}

/* Selection tiles */
.tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  border: 0;
}

.tile-grid-compact {
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  margin-bottom: var(--space-5);
}

.select-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-3);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast),
    box-shadow var(--transition-fast), transform var(--transition-fast);
  text-align: center;
  min-height: 100px;
}

.select-tile:hover {
  border-color: rgba(20, 92, 62, 0.35);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.select-tile.selected {
  border-color: var(--primary);
  background: var(--primary-soft);
  box-shadow: 0 0 0 3px rgba(20, 92, 62, 0.12);
}

.select-tile input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.tile-icon {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--primary);
}

.tile-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.select-tile-sm {
  min-height: 72px;
  padding: var(--space-4);
}

/* Visibility tiles */
.visibility-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  border: 0;
}

.visibility-tile {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-5);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.visibility-tile:hover {
  border-color: rgba(20, 92, 62, 0.35);
}

.visibility-tile.selected {
  border-color: var(--primary);
  background: var(--primary-soft);
}

.visibility-tile input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.visibility-label {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

.visibility-hint-text {
  font-size: var(--text-sm);
  color: var(--text-muted);
  line-height: var(--leading-relaxed);
}

/* Context blocks */
.context-step {
  display: grid;
  gap: var(--space-6);
}

.context-block {
  padding: var(--space-5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--background-alt);
}

.context-block h4 {
  margin: 0 0 var(--space-4);
  font-size: var(--text-lg);
}

.block-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.block-head h4 {
  margin: 0;
}

.field-spacious textarea {
  min-height: 10rem;
}

/* Review preview */
.review-preview {
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--surface);
}

.preview-header {
  padding: var(--space-4) var(--space-5);
  background: var(--forest-soft);
  color: var(--text-on-dark);
}

.preview-label {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-mint);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-4);
  padding: var(--space-5);
  margin: 0;
  border-bottom: 1px solid var(--border-subtle);
}

.preview-grid dt {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: var(--space-1);
}

.preview-grid dd {
  margin: 0;
  font-weight: var(--font-medium);
}

.preview-block {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
}

.preview-block h5 {
  margin: 0 0 var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.preview-block p {
  margin: 0;
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
}

.preview-footer {
  padding: var(--space-4) var(--space-5);
  font-size: var(--text-sm);
  margin: 0;
}

/* Completeness sidebar */
.completeness {
  margin-top: var(--space-5);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid rgba(20, 92, 62, 0.15);
}

.section-label {
  margin: 0 0 var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--primary);
}

.completeness ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-1);
}

.completeness li {
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.completeness li::before {
  content: '○ ';
}

.completeness li.done {
  color: var(--primary);
}

.completeness li.done::before {
  content: '✓ ';
}

.optional-note {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.req {
  font-style: normal;
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: var(--font-medium);
}

.hint {
  margin: var(--space-3) 0 0;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.empty-hint {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.nested-item {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  margin-top: var(--space-3);
}

.nested-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.linkish {
  border: 0;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  padding: 0;
  font-size: var(--text-sm);
}

.wizard-nav {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-subtle);
}

.nav-spacer {
  flex: 1;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 768px) {
  .wizard-layout {
    grid-template-columns: 1fr;
  }

  .wizard-sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--border-subtle);
  }

  .shield-hero {
    padding: var(--space-8) var(--space-5);
  }

  .shield-process-section {
    padding: var(--space-5);
  }

  .confirmation-header {
    flex-direction: column;
  }
}
</style>
