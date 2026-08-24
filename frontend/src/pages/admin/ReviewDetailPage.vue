<template>
  <div class="review-workspace" data-testid="review-detail-page">
    <RouterLink class="back-link" to="/community-shield/review-queue">Back to review queue</RouterLink>

    <p v-if="!organization.canReviewIncidents" class="error" data-testid="review-denied">
      You cannot review Community Shield reports in this organization.
    </p>
    <p v-else-if="error" class="error" data-testid="review-error">{{ error }}</p>
    <LoadingState v-else-if="isLoading || !pkg" message="Loading review package…" />

    <template v-else>
      <header class="case-header">
        <div class="case-header-top">
          <span class="case-ref">REF #{{ pkg.incident.id }}</span>
          <span class="badge info">{{ statusLabel(pkg.incident.status) }}</span>
          <span v-if="pkg.incident.escalated" class="badge warning">Escalated</span>
        </div>
        <h1>Community Safety Review</h1>
        <p class="case-meta">
          {{ platformLabel(pkg.incident.platform) }} · {{ contentTypeLabel(pkg.incident.content_type) }} ·
          {{ visibilityLabel(pkg.incident.visibility) }}
          <template v-if="pkg.incident.review_outcome">
            · {{ reviewOutcomeLabel(pkg.incident.review_outcome) }}
          </template>
        </p>
      </header>

      <ContextRelationshipView
        :incident="pkg.incident"
        :ai-present="latestAnalysis?.status === 'completed'"
        :human-present="Boolean(pkg.human_review.outcome)"
      />

      <div class="review-layout">
        <main class="review-main">
          <section class="case-file-section" data-testid="incident-block">
            <h2>Incident</h2>
            <dl class="case-details">
          <div>
            <dt>Platform</dt>
            <dd>{{ platformLabel(pkg.incident.platform) }}</dd>
          </div>
          <div>
            <dt>Content type</dt>
            <dd>{{ contentTypeLabel(pkg.incident.content_type) }}</dd>
          </div>
          <div>
            <dt>Visibility</dt>
            <dd>{{ visibilityLabel(pkg.incident.visibility) }}</dd>
          </div>
          <div>
            <dt>Submitted</dt>
            <dd>{{ formatDateTime(pkg.incident.created_at) }}</dd>
          </div>
        </dl>
            <h3>Description</h3>
            <p class="case-body">{{ pkg.incident.description }}</p>
          </section>

          <section class="case-file-section" data-testid="original-item-block">
        <h2>Original item</h2>
        <template v-if="hasOriginalItem">
          <p v-if="pkg.incident.original_item_title" class="title-line">{{ pkg.incident.original_item_title }}</p>
          <p v-if="pkg.incident.original_item_content" class="case-body">{{ pkg.incident.original_item_content }}</p>
          <dl class="case-details">
            <div>
              <dt>Author</dt>
              <dd>{{ pkg.incident.original_item_author || 'Not provided' }}</dd>
            </div>
            <div>
              <dt>Posted</dt>
              <dd>{{ formatDateTime(pkg.incident.original_item_posted_at) }}</dd>
            </div>
            <div>
              <dt>Reference</dt>
              <dd>
                <a
                  v-if="pkg.incident.source_url"
                  :href="pkg.incident.source_url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ pkg.incident.source_url }}
                </a>
                <span v-else class="muted">Not provided</span>
              </dd>
            </div>
          </dl>
        </template>
        <p v-else class="muted">No original item details were provided.</p>
      </section>

          <section class="case-file-section" data-testid="surrounding-context-block">
            <h2>Surrounding context</h2>
            <p v-if="pkg.incident.surrounding_context" class="case-body">{{ pkg.incident.surrounding_context }}</p>
            <p v-else class="muted">No surrounding context provided.</p>
          </section>

          <section class="case-file-section" data-testid="replies-block">
            <h2>Replies</h2>
            <div v-if="(pkg.incident.replies?.length ?? 0) > 0" class="evidence-list">
              <div v-for="reply in pkg.incident.replies" :key="reply.id ?? reply.position" class="evidence-entry">
                <p class="evidence-meta">
                  {{ reply.author || 'Unknown author' }}
                  <span v-if="reply.posted_at"> · {{ formatDateTime(reply.posted_at) }}</span>
                </p>
                <p class="case-body">{{ reply.content }}</p>
              </div>
            </div>
            <p v-else class="muted">No replies recorded.</p>
          </section>

          <section class="case-file-section" data-testid="related-items-block">
            <h2>Related items</h2>
            <div v-if="(pkg.incident.related_items?.length ?? 0) > 0" class="evidence-list">
              <div v-for="related in pkg.incident.related_items" :key="related.id" class="evidence-entry">
                <p class="evidence-meta">
                  {{ platformLabel(related.platform) }} · {{ contentTypeLabel(related.content_type) }}
                  <span v-if="related.observed_at"> · {{ formatDateTime(related.observed_at) }}</span>
                </p>
                <p v-if="related.description" class="case-body">{{ related.description }}</p>
                <a
                  v-if="related.reference_url"
                  :href="related.reference_url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ related.reference_url }}
                </a>
              </div>
            </div>
            <p v-else class="muted">No related items recorded.</p>
          </section>

          <section class="case-file-section">
            <h2>Language</h2>
            <p>{{ languageLabel(pkg.incident.language) }}</p>
          </section>

          <section class="case-file-section" data-testid="reporter-notes-block">
            <h2>Reporter notes</h2>
            <p v-if="pkg.incident.reporter_notes" class="case-body">{{ pkg.incident.reporter_notes }}</p>
            <p v-else class="muted">No reporter notes provided.</p>
          </section>

          <section class="case-file-section" data-testid="review-history">
            <h2>Review History</h2>
            <ul v-if="pkg.human_review.history.length > 0" class="history">
              <li v-for="entry in pkg.human_review.history" :key="entry.id">
                <strong>{{ formatDateTime(entry.created_at) }}</strong>
                · {{ entry.actor?.name ?? 'Unknown reviewer' }}
                · {{ reviewActionLabel(entry.action) }}
                <p v-if="entry.notes" class="muted">{{ entry.notes }}</p>
              </li>
            </ul>
            <p v-else class="muted">No review actions yet.</p>
          </section>

          <OutcomeTrackingPanel
            v-if="organization.canViewOutcomes && organization.currentOrganization && pkg"
            :organization-id="organization.currentOrganization.id"
            :report-id="pkg.incident.id"
            :can-manage="organization.canManageOutcomes"
          />

          <section
            v-if="
              pkg.incident.review_outcome === 'confirmed'
              && (organization.canViewEducationPatterns || organization.canCreateEducationPatterns)
            "
            class="case-file-section education-block"
            data-testid="community-education-section"
          >
            <h2>Learning Pattern</h2>
            <p class="muted">
              Community Shield → Academy. Capture a learning pattern from this confirmed review
              for Community Safety lessons and ADAPT practice.
            </p>

            <p v-if="patternLoading" class="muted">Loading learning pattern…</p>
            <p v-else-if="patternError" class="error">{{ patternError }}</p>

            <template v-else-if="learningPattern">
              <dl class="case-details" data-testid="existing-learning-pattern">
                <div>
                  <dt>Status</dt>
                  <dd>{{ learningPattern.status }}</dd>
                </div>
                <div>
                  <dt>Objective</dt>
                  <dd>{{ learningPattern.learning_objective }}</dd>
                </div>
                <div>
                  <dt>Type</dt>
                  <dd>{{ patternTypeLabel(learningPattern.pattern_type) }}</dd>
                </div>
              </dl>
              <div class="actions">
                <RouterLink
                  :to="{ name: 'admin-learning-pattern-detail', params: { id: learningPattern.id } }"
                  data-testid="view-learning-pattern"
                >
                  View learning pattern
                </RouterLink>
                <RouterLink to="/admin/education/patterns" data-testid="browse-learning-patterns">
                  Browse learning patterns
                </RouterLink>
              </div>
            </template>

            <form
              v-else-if="organization.canCreateEducationPatterns"
              class="stack"
              data-testid="create-learning-pattern-form"
              @submit.prevent="createLearningPattern"
            >
              <label class="field">
                <span>Pattern type</span>
                <select
                  v-model="patternForm.pattern_type"
                  name="pattern_type"
                  data-testid="pattern-type"
                  required
                >
                  <option disabled value="">Select a type</option>
                  <option
                    v-for="option in LEARNING_PATTERN_TYPE_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>
              <label class="field">
                <span>Title</span>
                <input v-model="patternForm.title" name="title" type="text" data-testid="pattern-title" required />
              </label>
              <label class="field">
                <span>Summary</span>
                <textarea v-model="patternForm.summary" name="summary" data-testid="pattern-summary" required />
              </label>
              <label class="field">
                <span>Learning objective</span>
                <textarea
                  v-model="patternForm.learning_objective"
                  name="learning_objective"
                  data-testid="pattern-learning-objective"
                  required
                />
              </label>
              <label class="field">
                <span>Domain</span>
                <input v-model="patternForm.domain" name="domain" type="text" data-testid="pattern-domain" />
              </label>
              <button class="button" type="submit" :disabled="patternBusy">Create Learning Pattern</button>
            </form>

            <p v-else class="muted">No learning pattern has been created for this report yet.</p>
          </section>

          <section
            v-if="organization.canExportIncidents"
            class="evidence-doc"
            data-testid="evidence-package-section"
          >
            <div class="evidence-doc-header">
              <h2>Evidence Package</h2>
              <p>
                Complete incident record with context, AI analysis, human review, and reporting guidance.
              </p>
              <p class="muted">
                Exporting creates a report. It does not automatically submit it.
              </p>
            </div>
            <div class="evidence-doc-body">
              <div v-if="evidencePackage" data-testid="evidence-package-preview">
                <p class="evidence-doc-ref">INCIDENT EVIDENCE PACKAGE · REF #{{ pkg.incident.id }}</p>
                <dl class="case-details">
                  <div>
                    <dt>Incident</dt>
                    <dd>
                      {{ platformLabel(evidencePackage.incident.platform || '') }} ·
                      {{ contentTypeLabel(evidencePackage.incident.content_type || '') }} ·
                      {{ visibilityLabel(evidencePackage.incident.visibility || '') }}
                    </dd>
                  </div>
                  <div>
                    <dt>Review</dt>
                    <dd data-testid="package-review-status">
                      <template v-if="evidencePackage.human_review.status === 'not_yet_reviewed'">
                        Not yet reviewed
                      </template>
                      <template
                        v-else-if="evidencePackage.human_review.decision.uncertain_prominence === 'UNCERTAIN'"
                      >
                        UNCERTAIN
                      </template>
                      <template v-else>
                        {{ reviewOutcomeLabel(evidencePackage.human_review.outcome) }}
                      </template>
                    </dd>
                  </div>
                  <div>
                    <dt>AI</dt>
                    <dd data-testid="package-ai-summary">
                      {{ evidencePackage.ai_analysis.uncertainty.confidence }} confidence ·
                      {{ evidencePackage.ai_analysis.uncertainty.uncertainty }} uncertainty
                    </dd>
                  </div>
                  <div>
                    <dt>Evidence</dt>
                    <dd>
                      1 original item ·
                      {{ evidencePackage.evidence.replies.length }} replies ·
                      {{ evidencePackage.evidence.related_items.length }} related items
                    </dd>
                  </div>
                  <div>
                    <dt>Reporting route</dt>
                    <dd data-testid="package-reporting-route">
                      {{ evidencePackage.reporting_route.platform_label }} —
                      {{ evidencePackage.reporting_route.recommended_route }}
                    </dd>
                  </div>
                  <div>
                    <dt>Privacy</dt>
                    <dd data-testid="package-privacy-notes">Review sensitive information before sharing</dd>
                  </div>
                </dl>

                <button
                  class="button secondary"
                  type="button"
                  data-testid="toggle-package-details"
                  @click="showPackageDetails = !showPackageDetails"
                >
                  {{ showPackageDetails ? 'Hide package details' : 'Expand package sections' }}
                </button>

                <div v-if="showPackageDetails" class="package-details" data-testid="package-details">
                  <h3>Incident</h3>
                  <p>{{ evidencePackage.incident.description }}</p>
                  <h3>Context</h3>
                  <p>{{ evidencePackage.evidence.surrounding_context || 'No surrounding context recorded.' }}</p>
                  <h3>Related Evidence</h3>
                  <p>
                    {{ evidencePackage.evidence.replies.length }} replies ·
                    {{ evidencePackage.evidence.related_items.length }} related items
                  </p>
                  <h3>AI Analysis</h3>
                  <p>{{ evidencePackage.ai_analysis.disclaimer }}</p>
                  <h3>Uncertainty</h3>
                  <p data-testid="package-ai-uncertainty">
                    {{ evidencePackage.ai_analysis.uncertainty.interpretation_note }}
                  </p>
                  <h3>Human Review</h3>
                  <p data-testid="package-human-decision">
                    <template v-if="evidencePackage.human_review.status === 'not_yet_reviewed'">
                      Not yet reviewed
                    </template>
                    <template v-else>
                      {{ reviewOutcomeLabel(evidencePackage.human_review.outcome) }}
                      ·
                      {{
                        safetyClassificationLabel(
                          evidencePackage.human_review.human_classification || 'unclassified',
                        )
                      }}
                    </template>
                  </p>
                  <h3>Safety &amp; privacy</h3>
                  <ul>
                    <li v-for="note in evidencePackage.safety_privacy_notes.notes" :key="note">
                      {{ note }}
                    </li>
                  </ul>
                  <h3>Reporting route</h3>
                  <p>{{ evidencePackage.reporting_route.platform_label }} — {{ evidencePackage.reporting_route.recommended_route }}</p>
                  <h3>Outcome</h3>
                  <p>{{ reviewOutcomeLabel(evidencePackage.human_review.outcome) }}</p>
                </div>
              </div>

              <p v-if="exportError" class="error" data-testid="export-error">{{ exportError }}</p>
              <p v-if="exportStatus" class="muted" data-testid="export-status">{{ exportStatus }}</p>
            </div>

            <div class="evidence-export-actions">
              <button
                class="button secondary"
                type="button"
                data-testid="view-evidence-package"
                :disabled="exportBusy"
                @click="loadEvidencePackage"
              >
                View Evidence Package
              </button>
              <button
                class="button"
                type="button"
                data-testid="export-json"
                :disabled="exportBusy"
                @click="exportJson"
              >
                Export JSON
              </button>
              <button
                class="button"
                type="button"
                data-testid="export-pdf"
                :disabled="exportBusy"
                @click="exportPdf"
              >
                Export PDF
              </button>
            </div>
          </section>

        </main>

        <aside class="review-sidebar">
          <section class="ai-panel" data-testid="ai-context-analysis">
            <div class="ai-panel-header">
              <h2>AI Analysis</h2>
              <span class="ai-advisory-tag">Advisory</span>
            </div>
            <p class="muted">AI Context Analysis is advisory. Humans decide.</p>
            <div class="ai-advisory-banner" data-testid="ai-advisory-banner">
              <span>
                <strong>AI analysis is advisory.</strong> Human review remains authoritative. AI output
                is not a verdict or final determination.
              </span>
            </div>
            <p class="muted disclaimer">{{ pkg.ai_assisted_triage.advisory_disclaimer }}</p>

            <div
              v-if="latestAnalysis?.analysis?.uncertainty?.level === 'high'"
              class="uncertainty-banner"
              data-testid="high-uncertainty-banner"
            >
              <strong>High uncertainty</strong>
              <p>
                {{ latestAnalysis.analysis.uncertainty.explanation }}
                Additional context may be useful before making a determination.
              </p>
            </div>

            <template v-if="latestAnalysis?.status === 'completed' && latestAnalysis.analysis">
              <p class="meta">
                {{ latestAnalysis.provider }} · {{ latestAnalysis.prompt_version }} · Completed
              </p>
              <h3>Potential signals</h3>
              <ul class="evidence-list plain">
                <li v-for="signal in latestAnalysis.analysis.signals" :key="signal.name">
                  <p class="meta">
                    {{ aiSignalLabel(signal.name) }} ·
                    {{ aiConfidenceLabel(signal.confidence) }} confidence
                  </p>
                  <p class="case-body">{{ signal.description }}</p>
                </li>
              </ul>
              <dl class="case-details">
                <div>
                  <dt>Potential classification</dt>
                  <dd>{{ aiClassificationLabel(latestAnalysis.analysis.classification.label) }}</dd>
                </div>
                <div>
                  <dt>AI confidence</dt>
                  <dd>AI confidence: {{ aiConfidenceLabel(latestAnalysis.analysis.classification.confidence) }}</dd>
                </div>
                <div>
                  <dt>AI uncertainty</dt>
                  <dd>
                    AI uncertainty: {{ aiConfidenceLabel(latestAnalysis.analysis.uncertainty.level) }}.
                    Context may change interpretation.
                  </dd>
                </div>
                <div>
                  <dt>Recommended action</dt>
                  <dd>
                    {{ aiRecommendedActionLabel(latestAnalysis.analysis.recommended_action.type) }}
                  </dd>
                </div>
              </dl>
              <p v-if="latestAnalysis.analysis.alternative_interpretation" class="case-body">
                <strong>Alternative interpretation:</strong>
                {{ latestAnalysis.analysis.alternative_interpretation }}
              </p>
            </template>
            <p v-else-if="latestAnalysis?.status === 'failed'" class="muted">
              {{ latestAnalysis.error_message || 'AI analysis unavailable.' }}
            </p>
            <p v-else class="muted">No AI Context Analysis is available yet.</p>

            <p class="ai-footer muted">AI analysis does not determine the final outcome.</p>

            <div
              v-if="pkg.ai_assisted_triage.history.length > 1"
              class="history-block"
              data-testid="ai-analysis-history"
            >
              <h3>AI analysis history</h3>
              <ul class="history">
                <li v-for="entry in pkg.ai_assisted_triage.history" :key="entry.id">
                  {{ formatDateTime(entry.created_at) }} · {{ entry.provider }} ·
                  {{ entry.prompt_version }} · {{ entry.status }}
                </li>
              </ul>
            </div>
          </section>

          <section class="human-panel" data-testid="human-review-block">
            <div class="human-panel-header">
              <h2>Human Review</h2>
              <p>Authoritative. What is your determination? The reviewer decides independently of AI. No action is automatic.</p>
            </div>

            <dl class="case-details">
              <div>
                <dt>Outcome</dt>
                <dd>{{ reviewOutcomeLabel(pkg.human_review.outcome) }}</dd>
              </div>
              <div>
                <dt>Reviewer notes</dt>
                <dd data-testid="reviewer-notes">{{ pkg.human_review.notes || 'None yet' }}</dd>
              </div>
              <div>
                <dt>Human classification</dt>
                <dd>{{ safetyClassificationLabel(pkg.incident.safety_classification) }}</dd>
              </div>
              <div>
                <dt>Escalation</dt>
                <dd>
                  <template v-if="pkg.human_review.escalated">
                    Escalated — {{ pkg.human_review.escalation_reason }}
                  </template>
                  <template v-else>Not escalated</template>
                </dd>
              </div>
              <div>
                <dt>Current reviewer</dt>
                <dd>{{ pkg.incident.current_reviewer?.name || 'Unassigned' }}</dd>
              </div>
            </dl>

            <div
              v-if="pkg.human_review.context_requests.length > 0"
              class="context-requests"
              data-testid="context-requests"
            >
              <h3>Context requests</h3>
              <ul class="history">
                <li v-for="request in pkg.human_review.context_requests" :key="request.id">
                  <strong>{{ request.status }}</strong>
                  — {{ request.reason }}
                  <span class="muted"> · {{ formatDateTime(request.requested_at) }}</span>
                </li>
              </ul>
            </div>

            <div class="human-actions" data-testid="review-actions">
          <button
            v-if="can('start')"
            class="button"
            type="button"
            data-testid="start-review"
            :disabled="busy"
            @click="onStart"
          >
            Start Review
          </button>

          <button
            v-if="can('confirm')"
            class="button"
            type="button"
            data-testid="open-confirm"
            @click="activeDialog = 'confirm'"
          >
            Confirm
          </button>
          <button
            v-if="can('uncertain')"
            class="button secondary"
            type="button"
            data-testid="open-uncertain"
            @click="activeDialog = 'uncertain'"
          >
            Mark Uncertain
          </button>
          <button
            v-if="can('request_context')"
            class="button secondary"
            type="button"
            data-testid="open-request-context"
            @click="activeDialog = 'context'"
          >
            Request More Context
          </button>
          <button
            v-if="can('escalate')"
            class="button secondary"
            type="button"
            data-testid="open-escalate"
            @click="activeDialog = 'escalate'"
          >
            Escalate
          </button>
          <button
            v-if="can('close')"
            class="button secondary"
            type="button"
            data-testid="open-close"
            @click="activeDialog = 'close'"
          >
            Close
          </button>
        </div>

        <p v-if="actionError" class="error" data-testid="action-error">{{ actionError }}</p>

        <div v-if="activeDialog === 'confirm'" class="dialog" data-testid="confirm-dialog">
          <h3>Human determination</h3>
          <label class="field">
            <span>Classification</span>
            <select v-model="confirmForm.classification" data-testid="confirm-classification">
              <option disabled value="">Select classification</option>
              <option
                v-for="option in HUMAN_CLASSIFICATION_OPTIONS"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Reviewer notes</span>
            <textarea v-model="confirmForm.notes" rows="4" data-testid="confirm-notes" />
          </label>
          <div class="actions">
            <button class="button secondary" type="button" @click="activeDialog = null">Cancel</button>
            <button class="button" type="button" data-testid="submit-confirm" :disabled="busy" @click="onConfirm">
              Confirm
            </button>
          </div>
        </div>

        <div v-if="activeDialog === 'uncertain'" class="dialog" data-testid="uncertain-dialog">
          <h3>Mark uncertain</h3>
          <label class="field">
            <span>Reviewer notes</span>
            <textarea v-model="uncertainNotes" rows="4" data-testid="uncertain-notes" />
          </label>
          <div class="actions">
            <button class="button secondary" type="button" @click="activeDialog = null">Cancel</button>
            <button class="button" type="button" data-testid="submit-uncertain" :disabled="busy" @click="onUncertain">
              Mark Uncertain
            </button>
          </div>
        </div>

        <div v-if="activeDialog === 'context'" class="dialog" data-testid="context-dialog">
          <h3>Request more context</h3>
          <label class="field">
            <span>What context is needed?</span>
            <textarea v-model="contextReason" rows="4" data-testid="context-reason" />
          </label>
          <div class="actions">
            <button class="button secondary" type="button" @click="activeDialog = null">Cancel</button>
            <button class="button" type="button" data-testid="submit-context" :disabled="busy" @click="onRequestContext">
              Request Context
            </button>
          </div>
        </div>

        <div v-if="activeDialog === 'escalate'" class="dialog" data-testid="escalate-dialog">
          <h3>Escalate</h3>
          <label class="field">
            <span>Why are you escalating?</span>
            <textarea v-model="escalateReason" rows="4" data-testid="escalate-reason" />
          </label>
          <div class="actions">
            <button class="button secondary" type="button" @click="activeDialog = null">Cancel</button>
            <button class="button" type="button" data-testid="submit-escalate" :disabled="busy" @click="onEscalate">
              Escalate
            </button>
          </div>
        </div>

        <div v-if="activeDialog === 'close'" class="dialog" data-testid="close-dialog">
          <h3>Close review</h3>
          <label class="field">
            <span>Reason (optional)</span>
            <textarea v-model="closeNotes" rows="4" data-testid="close-notes" />
          </label>
          <div class="actions">
            <button class="button secondary" type="button" @click="activeDialog = null">Cancel</button>
            <button class="button" type="button" data-testid="submit-close" :disabled="busy" @click="onClose">
              Close
            </button>
          </div>
        </div>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import LoadingState from '@/components/ui/LoadingState.vue';
import OutcomeTrackingPanel from '@/components/OutcomeTrackingPanel.vue';
import ContextRelationshipView from '@/components/community-shield/ContextRelationshipView.vue';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type {
  CommunityShieldSafetyClassification,
  IncidentEvidencePackage,
  IncidentReviewPackage,
  LearningPattern,
  LearningPatternType,
  ReviewAllowedAction,
} from '@/types';
import {
  HUMAN_CLASSIFICATION_OPTIONS,
  aiClassificationLabel,
  aiConfidenceLabel,
  aiRecommendedActionLabel,
  aiSignalLabel,
  contentTypeLabel,
  languageLabel,
  platformLabel,
  reviewActionLabel,
  reviewOutcomeLabel,
  safetyClassificationLabel,
  statusLabel,
  visibilityLabel,
} from '@/utils/communityShield';
import { LEARNING_PATTERN_TYPE_OPTIONS, patternTypeLabel } from '@/utils/education';
import { formatDateTime } from '@/utils/date';

const organization = useOrganizationStore();
const route = useRoute();

const pkg = ref<IncidentReviewPackage | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const actionError = ref<string | null>(null);
const busy = ref(false);
const activeDialog = ref<'confirm' | 'uncertain' | 'context' | 'escalate' | 'close' | null>(null);

const learningPattern = ref<LearningPattern | null>(null);
const patternLoading = ref(false);
const patternBusy = ref(false);
const patternError = ref<string | null>(null);
const patternForm = ref({
  pattern_type: '' as LearningPatternType | '',
  title: '',
  summary: '',
  learning_objective: '',
  domain: '',
});

const confirmForm = ref({
  classification: '' as CommunityShieldSafetyClassification | '',
  notes: '',
});
const uncertainNotes = ref('');
const contextReason = ref('');
const escalateReason = ref('');
const closeNotes = ref('');

const evidencePackage = ref<IncidentEvidencePackage | null>(null);
const showPackageDetails = ref(false);
const exportBusy = ref(false);
const exportError = ref<string | null>(null);
const exportStatus = ref<string | null>(null);

const latestAnalysis = computed(() => pkg.value?.ai_assisted_triage.latest ?? null);
const hasOriginalItem = computed(() => {
  const item = pkg.value?.incident;
  if (!item) {
    return false;
  }

  return !!(
    item.original_item_title
    || item.original_item_content
    || item.original_item_author
    || item.original_item_posted_at
    || item.source_url
  );
});

function can(action: ReviewAllowedAction): boolean {
  return pkg.value?.human_review.allowed_actions.includes(action) ?? false;
}

function lockVersion(): number | undefined {
  return pkg.value?.incident.review_lock_version;
}

async function loadPackage(): Promise<void> {
  if (!organization.currentOrganization || !organization.canReviewIncidents) {
    pkg.value = null;
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    pkg.value = await communityApi.reviewPackage(
      organization.currentOrganization.id,
      String(route.params.id),
    );
    await loadLearningPattern();
  } catch {
    error.value = 'Unable to load this review package.';
    pkg.value = null;
  } finally {
    isLoading.value = false;
  }
}

async function loadLearningPattern(): Promise<void> {
  learningPattern.value = null;
  patternError.value = null;

  if (
    !organization.currentOrganization
    || !(organization.canViewEducationPatterns || organization.canCreateEducationPatterns)
    || pkg.value?.incident.review_outcome !== 'confirmed'
  ) {
    return;
  }

  patternLoading.value = true;

  try {
    learningPattern.value = await communityApi.reportLearningPattern(
      organization.currentOrganization.id,
      String(route.params.id),
    );
  } catch {
    patternError.value = 'Unable to load the learning pattern for this report.';
  } finally {
    patternLoading.value = false;
  }
}

async function createLearningPattern(): Promise<void> {
  if (!organization.currentOrganization || !patternForm.value.pattern_type) {
    return;
  }

  patternBusy.value = true;
  patternError.value = null;

  try {
    learningPattern.value = await communityApi.createReportLearningPattern(
      organization.currentOrganization.id,
      String(route.params.id),
      {
        pattern_type: patternForm.value.pattern_type,
        title: patternForm.value.title,
        summary: patternForm.value.summary,
        learning_objective: patternForm.value.learning_objective,
        domain: patternForm.value.domain || null,
      },
    );
  } catch {
    patternError.value = 'Unable to create a learning pattern from this report.';
  } finally {
    patternBusy.value = false;
  }
}

async function runAction(action: () => Promise<IncidentReviewPackage | unknown>): Promise<void> {
  busy.value = true;
  actionError.value = null;

  try {
    const result = await action();
    if (result && typeof result === 'object' && 'incident' in (result as object)) {
      pkg.value = result as IncidentReviewPackage;
    } else if (organization.currentOrganization) {
      pkg.value = await communityApi.reviewPackage(
        organization.currentOrganization.id,
        String(route.params.id),
      );
    }
    activeDialog.value = null;
    await loadLearningPattern();
  } catch (err: unknown) {
    const message =
      (err as { response?: { data?: { message?: string }; status?: number } })?.response?.data
        ?.message
      ?? ((err as { response?: { status?: number } })?.response?.status === 409
        ? 'This review was updated by another reviewer. Reload and try again.'
        : 'Unable to complete that review action.');
    actionError.value = message;
  } finally {
    busy.value = false;
  }
}

async function onStart(): Promise<void> {
  if (!organization.currentOrganization) return;
  await runAction(() =>
    communityApi.startReview(organization.currentOrganization!.id, String(route.params.id), {
      review_lock_version: lockVersion(),
    }),
  );
}

async function onConfirm(): Promise<void> {
  if (!organization.currentOrganization || !confirmForm.value.classification) {
    actionError.value = 'Select a classification and provide notes.';
    return;
  }

  await runAction(() =>
    communityApi.confirmReview(organization.currentOrganization!.id, String(route.params.id), {
      notes: confirmForm.value.notes,
      safety_classification: confirmForm.value.classification as CommunityShieldSafetyClassification,
      review_lock_version: lockVersion(),
    }),
  );
}

async function onUncertain(): Promise<void> {
  if (!organization.currentOrganization) return;
  await runAction(() =>
    communityApi.markUncertain(organization.currentOrganization!.id, String(route.params.id), {
      notes: uncertainNotes.value,
      review_lock_version: lockVersion(),
    }),
  );
}

async function onRequestContext(): Promise<void> {
  if (!organization.currentOrganization) return;
  await runAction(() =>
    communityApi.requestContext(organization.currentOrganization!.id, String(route.params.id), {
      reason: contextReason.value,
      review_lock_version: lockVersion(),
    }),
  );
}

async function onEscalate(): Promise<void> {
  if (!organization.currentOrganization) return;
  await runAction(() =>
    communityApi.escalateReview(organization.currentOrganization!.id, String(route.params.id), {
      reason: escalateReason.value,
      review_lock_version: lockVersion(),
    }),
  );
}

async function onClose(): Promise<void> {
  if (!organization.currentOrganization) return;
  await runAction(() =>
    communityApi.closeReview(organization.currentOrganization!.id, String(route.params.id), {
      notes: closeNotes.value || undefined,
      review_lock_version: lockVersion(),
    }),
  );
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}

async function loadEvidencePackage(): Promise<void> {
  if (!organization.currentOrganization) return;

  exportBusy.value = true;
  exportError.value = null;
  exportStatus.value = 'Loading evidence package…';

  try {
    evidencePackage.value = await communityApi.evidencePackage(
      organization.currentOrganization.id,
      String(route.params.id),
    );
    exportStatus.value = 'Evidence package ready.';
  } catch {
    exportError.value = 'Unable to load the evidence package.';
    exportStatus.value = null;
  } finally {
    exportBusy.value = false;
  }
}

async function exportJson(): Promise<void> {
  if (!organization.currentOrganization) return;

  exportBusy.value = true;
  exportError.value = null;
  exportStatus.value = 'Generating report…';

  try {
    if (!evidencePackage.value) {
      evidencePackage.value = await communityApi.evidencePackage(
        organization.currentOrganization.id,
        String(route.params.id),
      );
    }
    const blob = await communityApi.exportEvidenceJson(
      organization.currentOrganization.id,
      String(route.params.id),
    );
    const reference = evidencePackage.value.incident.reference || String(route.params.id);
    downloadBlob(blob, `community-shield-incident-${reference}.json`);
    exportStatus.value = 'Report ready.';
  } catch {
    exportError.value = 'Unable to export JSON.';
    exportStatus.value = null;
  } finally {
    exportBusy.value = false;
  }
}

async function exportPdf(): Promise<void> {
  if (!organization.currentOrganization) return;

  exportBusy.value = true;
  exportError.value = null;
  exportStatus.value = 'Generating report…';

  try {
    if (!evidencePackage.value) {
      evidencePackage.value = await communityApi.evidencePackage(
        organization.currentOrganization.id,
        String(route.params.id),
      );
    }
    const blob = await communityApi.exportEvidencePdf(
      organization.currentOrganization.id,
      String(route.params.id),
    );
    const reference = evidencePackage.value.incident.reference || String(route.params.id);
    downloadBlob(blob, `community-shield-incident-${reference}.pdf`);
    exportStatus.value = 'Report ready.';
  } catch {
    exportError.value = 'Unable to export PDF.';
    exportStatus.value = null;
  } finally {
    exportBusy.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, organization.canReviewIncidents, route.params.id],
  () => {
    evidencePackage.value = null;
    showPackageDetails.value = false;
    exportError.value = null;
    exportStatus.value = null;
    void loadPackage();
  },
  { immediate: true },
);
</script>

<style scoped>
.content {
  padding: 1.25rem 1.4rem;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--muted);
}

.block {
  padding-top: 0.75rem;
  border-top: 1px solid var(--line);
}

.block h2 {
  margin-bottom: 0.45rem;
}

.details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin: 0 0 1rem;
}

.details dt {
  color: var(--muted);
  font-size: 0.8rem;
}

.details dd {
  margin: 0.15rem 0 0;
}

.body {
  white-space: pre-wrap;
  line-height: 1.5;
}

.evidence-list {
  display: grid;
  gap: 0.75rem;
  padding-left: 1.1rem;
}

.evidence-list.plain {
  list-style: none;
  padding-left: 0;
}

.meta {
  margin: 0 0 0.25rem;
  color: var(--muted);
  font-size: 0.9rem;
}

.ai-block {
  background: rgba(31, 107, 74, 0.04);
  padding: 1rem;
  border-radius: 12px;
  border-top: 0;
}

.human-block {
  background: rgba(255, 253, 248, 0.9);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.disclaimer {
  font-style: italic;
}

.uncertainty-banner {
  margin: 0.75rem 0;
  padding: 0.85rem 1rem;
  border-left: 3px solid #8a5a00;
  background: rgba(138, 90, 0, 0.08);
}

.actions-panel,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.85rem;
}

.dialog {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fffdf8;
}

.history {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}

.history li {
  padding-bottom: 0.55rem;
  border-bottom: 1px solid var(--line);
}

.title-line {
  font-weight: 600;
}

.export-block {
  background: rgba(31, 61, 107, 0.04);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--line);
  border-top: 1px solid var(--line);
}

.education-block {
  background: rgba(31, 107, 74, 0.04);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.package-preview {
  margin: 0.85rem 0;
}

.package-details {
  margin-top: 0.85rem;
  display: grid;
  gap: 0.5rem;
}
</style>
