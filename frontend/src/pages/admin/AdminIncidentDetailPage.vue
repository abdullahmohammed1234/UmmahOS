<template>
  <section class="panel content stack review" data-testid="admin-incident-detail">
    <RouterLink to="/admin/community-shield">Back to reports</RouterLink>
    <p v-if="!organization.canManageIncidents" class="error" data-testid="admin-denied">
      You cannot review Community Shield reports in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading report…</p>
    <template v-else-if="item">
      <header class="header">
        <p class="eyebrow">Community Shield</p>
        <h1>Report #{{ item.id }}</h1>
        <p class="muted">
          {{ platformLabel(item.platform) }} · {{ contentTypeLabel(item.content_type) }} ·
          {{ visibilityLabel(item.visibility) }} · {{ statusLabel(item.status) }}
        </p>
      </header>

      <aside class="completeness" data-testid="review-completeness">
        <p class="section-label">Context captured</p>
        <ul>
          <li class="done">Platform</li>
          <li :class="{ done: hasOriginalItem }">Original item</li>
          <li :class="{ done: !!item.source_url }">Source reference</li>
          <li :class="{ done: !!item.observed_at || !!item.original_item_posted_at }">Timestamp</li>
          <li :class="{ done: !!item.surrounding_context }">Surrounding context</li>
          <li :class="{ done: (item.replies?.length ?? 0) > 0 }">Replies</li>
          <li :class="{ done: (item.related_items?.length ?? 0) > 0 }">Related copies</li>
          <li :class="{ done: !!item.language && item.language !== 'unknown' }">Language</li>
          <li :class="{ done: !!item.reporter_notes }">Reporter notes</li>
          <li :class="{ done: item.safety_classification !== 'unclassified' }">
            Safety classification
          </li>
        </ul>
      </aside>

      <section class="block">
        <h2>Incident</h2>
        <dl class="details">
          <div>
            <dt>Status</dt>
            <dd>{{ statusLabel(item.status) }}</dd>
          </div>
          <div>
            <dt>Platform</dt>
            <dd>{{ platformLabel(item.platform) }}</dd>
          </div>
          <div>
            <dt>Content type</dt>
            <dd>{{ contentTypeLabel(item.content_type) }}</dd>
          </div>
          <div>
            <dt>Visibility</dt>
            <dd>{{ visibilityLabel(item.visibility) }}</dd>
          </div>
          <div>
            <dt>Reporter</dt>
            <dd>{{ item.reported_by?.name ?? 'Unknown' }} ({{ item.reported_by?.email }})</dd>
          </div>
          <div>
            <dt>Observed at</dt>
            <dd>{{ formatTimestamp(item.observed_at) }}</dd>
          </div>
        </dl>
        <div>
          <h3>What happened?</h3>
          <p class="body" data-testid="description-body">{{ item.description }}</p>
        </div>
      </section>

      <section class="block" data-testid="original-item-block">
        <h2>Original item</h2>
        <template v-if="hasOriginalItem">
          <p v-if="item.original_item_title" class="title-line">{{ item.original_item_title }}</p>
          <p v-if="item.original_item_content" class="body" data-testid="original-item-body">
            {{ item.original_item_content }}
          </p>
          <dl class="details">
            <div>
              <dt>Author</dt>
              <dd>{{ item.original_item_author || 'Not provided' }}</dd>
            </div>
            <div>
              <dt>Posted</dt>
              <dd>{{ formatTimestamp(item.original_item_posted_at) }}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>
                <a
                  v-if="item.source_url"
                  :href="item.source_url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ item.source_url }}
                </a>
                <span v-else class="muted">Not provided</span>
              </dd>
            </div>
          </dl>
        </template>
        <p v-else class="muted">No original item details were provided.</p>
      </section>

      <section class="block" data-testid="surrounding-context-block">
        <h2>Surrounding context</h2>
        <p v-if="item.surrounding_context" class="body">{{ item.surrounding_context }}</p>
        <p v-else class="muted">No surrounding context provided.</p>
      </section>

      <section class="block" data-testid="replies-block">
        <h2>Replies</h2>
        <ol v-if="(item.replies?.length ?? 0) > 0" class="evidence-list">
          <li v-for="reply in item.replies" :key="reply.id ?? reply.position">
            <p class="meta">
              {{ reply.author || 'Unknown author' }}
              <span v-if="reply.posted_at"> · {{ formatTimestamp(reply.posted_at) }}</span>
            </p>
            <p class="body">{{ reply.content }}</p>
          </li>
        </ol>
        <p v-else class="muted">No replies recorded.</p>
      </section>

      <section class="block" data-testid="related-items-block">
        <h2>Related copies</h2>
        <ul v-if="(item.related_items?.length ?? 0) > 0" class="evidence-list plain">
          <li v-for="related in item.related_items" :key="related.id">
            <p class="meta">
              {{ platformLabel(related.platform) }} · {{ contentTypeLabel(related.content_type) }}
              <span v-if="related.observed_at"> · {{ formatTimestamp(related.observed_at) }}</span>
            </p>
            <p v-if="related.description" class="body">{{ related.description }}</p>
            <a
              v-if="related.reference_url"
              :href="related.reference_url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ related.reference_url }}
            </a>
          </li>
        </ul>
        <p v-else class="muted">No related copies recorded.</p>
      </section>

      <section class="block">
        <h2>Language</h2>
        <p>{{ languageLabel(item.language) }}</p>
      </section>

      <section class="block" data-testid="reporter-notes-block">
        <h2>Reporter notes</h2>
        <p v-if="item.reporter_notes" class="body">{{ item.reporter_notes }}</p>
        <p v-else class="muted">No reporter notes provided.</p>
      </section>

      <section class="block" data-testid="ai-analysis-block">
        <h2>AI Context Analysis</h2>
        <p class="disclaimer" data-testid="ai-disclaimer">
          AI-generated analysis is advisory and may be incorrect. Human review is required for
          decisions.
        </p>
        <p class="privacy-note" data-testid="ai-privacy-note">
          This sends the report's captured context to the configured AI provider for analysis. The
          result is advisory and requires human review.
        </p>

        <div class="ai-actions">
          <button
            class="button"
            type="button"
            :disabled="isAnalyzing"
            data-testid="analyze-with-ai"
            @click="onAnalyze"
          >
            {{ analyzeButtonLabel }}
          </button>
          <p v-if="isAnalyzing" class="muted" data-testid="ai-loading">Running AI analysis…</p>
          <p v-if="aiError" class="error" data-testid="ai-error">{{ aiError }}</p>
        </div>

        <p v-if="analyses.length === 0 && !isAnalyzing" class="muted" data-testid="ai-empty">
          No AI analysis yet. Analysis is optional and does not change this report's status or human
          classification.
        </p>

        <article
          v-for="entry in analyses"
          :key="entry.id"
          class="ai-package"
          :data-testid="`ai-analysis-${entry.id}`"
          :data-status="entry.status"
        >
          <header class="ai-meta">
            <p class="section-label">Analysis #{{ entry.id }}</p>
            <p class="meta">
              {{ entry.provider }}
              <span v-if="entry.model"> / {{ entry.model }}</span>
              · Prompt {{ entry.prompt_version }}
              · {{ formatTimestamp(entry.created_at) }}
            </p>
          </header>

          <template v-if="entry.status === 'failed'">
            <p class="error" data-testid="ai-failed-state">
              {{ entry.error_message || 'AI analysis unavailable.' }}
            </p>
            <p class="muted">This does not mean no harmful content was detected.</p>
          </template>

          <template v-else-if="entry.status === 'completed' && entry.analysis">
            <div class="ai-section" data-testid="ai-signals">
              <h3>Potential signals</h3>
              <ul class="signal-list">
                <li v-for="(signal, index) in entry.analysis.signals" :key="`${entry.id}-${index}`">
                  <p class="signal-name">{{ aiSignalLabel(signal.name) }}</p>
                  <p class="body">{{ signal.description }}</p>
                  <p class="meta">Potential signal confidence: {{ aiConfidenceLabel(signal.confidence) }}</p>
                  <ul v-if="signal.evidence?.length" class="evidence-bullets">
                    <li v-for="(ev, evIndex) in signal.evidence" :key="evIndex">{{ ev }}</li>
                  </ul>
                </li>
              </ul>
            </div>

            <hr />

            <div class="ai-section" data-testid="ai-classification">
              <h3>Potential classification</h3>
              <p class="emphasis">{{ aiClassificationLabel(entry.analysis.classification.label) }}</p>
              <p class="meta" data-testid="ai-confidence">
                Confidence: {{ aiConfidenceLabel(entry.analysis.classification.confidence) }}
              </p>
            </div>

            <hr />

            <div class="ai-section uncertainty" data-testid="ai-uncertainty">
              <h3>Uncertainty</h3>
              <p class="emphasis">{{ aiConfidenceLabel(entry.analysis.uncertainty.level) }}</p>
              <p class="body">{{ entry.analysis.uncertainty.explanation }}</p>
            </div>

            <template v-if="entry.analysis.alternative_interpretation">
              <hr />
              <div class="ai-section" data-testid="ai-alternative">
                <h3>Alternative interpretation</h3>
                <p class="body">{{ entry.analysis.alternative_interpretation }}</p>
              </div>
            </template>

            <hr />

            <div class="ai-section" data-testid="ai-recommended-action">
              <h3>Recommended action</h3>
              <p class="emphasis">
                {{ aiRecommendedActionLabel(entry.analysis.recommended_action.type) }}
              </p>
              <p class="body">{{ entry.analysis.recommended_action.reason }}</p>
            </div>

            <hr />

            <p class="disclaimer">
              AI-generated analysis — not a final determination. Human classification remains
              authoritative.
            </p>
          </template>

          <template v-else>
            <p class="muted">Analysis status: {{ entry.status }}</p>
          </template>
        </article>
      </section>

      <section class="block" data-testid="classification-block">
        <h2>Human classification</h2>
        <p class="disclaimer">
          Internal review classification — not a legal determination. Separate from AI analysis.
        </p>
        <fieldset class="choice-group">
          <legend class="sr-only">Safety classification</legend>
          <label
            v-for="option in SAFETY_CLASSIFICATION_OPTIONS"
            :key="option.value"
            class="choice"
          >
            <input
              v-model="classification"
              type="radio"
              name="safety_classification"
              :value="option.value"
              data-testid="classification-option"
            />
            <span>{{ option.label }}</span>
          </label>
        </fieldset>
        <p v-if="item.classified_by" class="meta">
          Classified by: {{ item.classified_by.name }}
          <span v-if="item.classified_at"> · {{ formatTimestamp(item.classified_at) }}</span>
        </p>
        <button
          class="button secondary"
          type="button"
          :disabled="isSavingClassification"
          data-testid="save-classification"
          @click="onSaveClassification"
        >
          {{ isSavingClassification ? 'Saving…' : 'Save classification' }}
        </button>
        <p v-if="classificationMessage" class="muted">{{ classificationMessage }}</p>
        <p v-if="classificationError" class="error">{{ classificationError }}</p>
      </section>

      <section class="block" data-testid="status-block">
        <h2>Status</h2>
        <label class="field">
          <span>Review status</span>
          <select v-model="status" data-testid="status-select">
            <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <p v-if="saveError" class="error">{{ saveError }}</p>
        <p v-if="message" class="muted">{{ message }}</p>
        <button class="button" type="button" :disabled="isSaving" @click="onSaveStatus">
          {{ isSaving ? 'Updating…' : 'Update status' }}
        </button>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type {
  CommunityShieldSafetyClassification,
  CommunityShieldStatus,
  Incident,
  IncidentAiAnalysis,
} from '@/types';
import {
  SAFETY_CLASSIFICATION_OPTIONS,
  STATUS_OPTIONS,
  aiClassificationLabel,
  aiConfidenceLabel,
  aiRecommendedActionLabel,
  aiSignalLabel,
  contentTypeLabel,
  languageLabel,
  platformLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';

const route = useRoute();
const organization = useOrganizationStore();
const item = ref<Incident | null>(null);
const analyses = ref<IncidentAiAnalysis[]>([]);
const status = ref<CommunityShieldStatus>('open');
const classification = ref<CommunityShieldSafetyClassification>('unclassified');
const isLoading = ref(false);
const isSaving = ref(false);
const isSavingClassification = ref(false);
const isAnalyzing = ref(false);
const error = ref('');
const saveError = ref('');
const message = ref('');
const classificationError = ref('');
const classificationMessage = ref('');
const aiError = ref('');

const hasOriginalItem = computed(() => {
  if (!item.value) {
    return false;
  }

  return !!(
    item.value.original_item_title ||
    item.value.original_item_content ||
    item.value.original_item_author ||
    item.value.original_item_posted_at ||
    item.value.source_url
  );
});

const analyzeButtonLabel = computed(() => {
  if (isAnalyzing.value) {
    return 'Analyzing…';
  }

  return analyses.value.length > 0 ? 'Run New Analysis' : 'Analyze with AI';
});

function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return 'Not provided';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

async function loadAnalyses(organizationId: number, incidentId: number): Promise<void> {
  try {
    analyses.value = await communityApi.aiAnalyses(organizationId, incidentId);
  } catch {
    analyses.value = [];
  }
}

async function load(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  const id = Number(route.params.id);

  if (!organizationId || !id || !organization.canManageIncidents) {
    item.value = null;
    analyses.value = [];
    return;
  }

  isLoading.value = true;
  error.value = '';
  aiError.value = '';

  try {
    item.value = await communityApi.incident(organizationId, id);
    status.value = item.value.status;
    classification.value = item.value.safety_classification ?? 'unclassified';
    await loadAnalyses(organizationId, id);
  } catch {
    item.value = null;
    analyses.value = [];
    error.value = 'This report is not available in the current organization.';
  } finally {
    isLoading.value = false;
  }
}

async function onAnalyze(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !item.value) {
    return;
  }

  isAnalyzing.value = true;
  aiError.value = '';

  try {
    const created = await communityApi.requestAiAnalysis(organizationId, item.value.id);
    analyses.value = [created, ...analyses.value.filter((entry) => entry.id !== created.id)];

    if (created.status === 'failed') {
      aiError.value = created.error_message || 'AI analysis is currently unavailable.';
    }
  } catch {
    aiError.value = 'AI analysis is currently unavailable.';
  } finally {
    isAnalyzing.value = false;
  }
}

async function onSaveStatus(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !item.value) {
    return;
  }

  isSaving.value = true;
  saveError.value = '';
  message.value = '';

  try {
    item.value = await communityApi.updateIncident(organizationId, item.value.id, {
      status: status.value,
    });
    message.value = 'Status updated.';
  } catch {
    saveError.value = 'Unable to update this report.';
  } finally {
    isSaving.value = false;
  }
}

async function onSaveClassification(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !item.value) {
    return;
  }

  isSavingClassification.value = true;
  classificationError.value = '';
  classificationMessage.value = '';

  try {
    item.value = await communityApi.updateIncident(organizationId, item.value.id, {
      safety_classification: classification.value,
    });
    classificationMessage.value = 'Classification saved.';
  } catch {
    classificationError.value = 'Unable to save classification.';
  } finally {
    isSavingClassification.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.id, organization.canManageIncidents],
  () => {
    void load();
  },
  { immediate: true },
);
</script>

<style scoped>
.review {
  max-width: 860px;
}

.header {
  margin-bottom: 0.25rem;
}

.eyebrow {
  margin: 0 0 0.35rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.78rem;
  color: var(--accent);
}

h1,
h2,
h3 {
  margin: 0 0 0.65rem;
}

.block {
  display: grid;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.details {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.details div {
  display: grid;
  gap: 0.2rem;
}

.details dt {
  color: var(--muted);
  font-size: 0.9rem;
}

.details dd {
  margin: 0;
}

.body {
  white-space: pre-wrap;
  margin: 0;
}

.title-line {
  margin: 0;
  font-weight: 600;
}

.meta {
  margin: 0 0 0.35rem;
  color: var(--muted);
  font-size: 0.92rem;
}

.disclaimer,
.privacy-note {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.privacy-note {
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: rgba(20, 40, 30, 0.03);
}

.evidence-list {
  margin: 0;
  padding-left: 1.2rem;
  display: grid;
  gap: 0.85rem;
}

.evidence-list.plain {
  list-style: none;
  padding-left: 0;
}

.choice-group {
  margin: 0;
  padding: 0;
  border: 0;
  display: grid;
  gap: 0.45rem;
}

.choice {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 0.7rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
}

.choice:has(input:checked) {
  border-color: rgba(31, 107, 74, 0.55);
  background: rgba(31, 107, 74, 0.06);
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

.ai-actions {
  display: grid;
  gap: 0.5rem;
  justify-items: start;
}

.ai-package {
  display: grid;
  gap: 0.85rem;
  padding: 1rem;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #fff;
}

.ai-meta .section-label {
  margin-bottom: 0.25rem;
}

.ai-section {
  display: grid;
  gap: 0.45rem;
}

.ai-section.uncertainty {
  padding: 0.85rem 0.95rem;
  border: 1px solid rgba(166, 124, 0, 0.35);
  border-radius: 12px;
  background: rgba(166, 124, 0, 0.08);
}

.signal-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.85rem;
}

.signal-name {
  margin: 0;
  font-weight: 600;
}

.signal-name::before {
  content: 'Potential: ';
  font-weight: 500;
  color: var(--muted);
}

.evidence-bullets {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--muted);
  font-size: 0.92rem;
}

.emphasis {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 0.15rem 0;
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
</style>
