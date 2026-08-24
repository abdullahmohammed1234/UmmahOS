<template>
  <section class="case-file-section outcome-panel" data-testid="outcome-tracking-section">
    <div class="outcome-panel-header">
      <div>
        <h2>{{ memberView ? 'What happened next?' : 'Outcome Tracking' }}</h2>
        <p v-if="!memberView" class="muted">
          Record externally reported outcomes. "Reported" means a submission was recorded — not that UmmahOS
          submitted anything automatically.
        </p>
      </div>
    </div>

    <p v-if="loadError" class="error" data-testid="outcome-error">{{ loadError }}</p>
    <p v-else-if="isLoading" class="muted" data-testid="outcome-loading">Loading outcome tracking…</p>

    <template v-else>
      <p v-if="reports.length === 0" class="muted" data-testid="outcome-empty">
        {{
          memberView
            ? 'No outcome updates are available yet.'
            : 'No external reporting activity has been recorded yet.'
        }}
      </p>

      <article
        v-for="report in reports"
        :key="report.id"
        class="outcome-report-card"
        :data-testid="`external-report-${report.id}`"
      >
        <header class="outcome-report-header">
          <h3>{{ destinationPlatformLabel(report.platform) }}</h3>
          <span class="outcome-status-badge" :data-testid="`report-status-${report.id}`">
            {{ externalReportStatusLabel(report.status) }}
          </span>
        </header>

        <dl class="case-details">
          <div>
            <dt>Reporting channel</dt>
            <dd>{{ report.reporting_channel }}</dd>
          </div>
          <div>
            <dt>Reported</dt>
            <dd>{{ formatDateTime(report.reported_at) }}</dd>
          </div>
          <div v-if="!memberView && report.external_reference">
            <dt>External reference</dt>
            <dd>{{ report.external_reference }}</dd>
          </div>
          <div>
            <dt>Decision</dt>
            <dd>{{ externalReportDecisionLabel(report.decision) }}</dd>
          </div>
          <div>
            <dt>Outcome</dt>
            <dd>{{ externalReportOutcomeLabel(report.outcome) }}</dd>
          </div>
          <div v-if="report.outcome">
            <dt>Source</dt>
            <dd>{{ externalReportSourceLabel(report.outcome_source) }}</dd>
          </div>
          <div>
            <dt>Verification</dt>
            <dd data-testid="verification-status">
              {{ externalReportVerificationLabel(report.verification_status) }}
            </dd>
          </div>
        </dl>

        <p v-if="memberView && report.reporter_visible_summary" class="outcome-summary">
          {{ report.reporter_visible_summary }}
        </p>

        <div
          v-if="report.status_history && report.status_history.length > 0"
          class="outcome-timeline-track"
          data-testid="outcome-timeline"
        >
          <h4>{{ memberView ? 'Your report' : 'Timeline' }}</h4>
          <ul class="outcome-timeline-steps">
            <li
              v-for="(entry, index) in report.status_history"
              :key="entry.id ?? index"
              class="outcome-timeline-step"
              :class="{
                done: isTimelineStepDone(entry.new_status, report.status),
                current: entry.new_status === report.status,
              }"
            >
              <span class="outcome-step-marker">
                {{ isTimelineStepDone(entry.new_status, report.status) ? '✓' : index + 1 }}
              </span>
              <div class="outcome-step-body">
                <span class="outcome-step-label">{{ externalReportStatusLabel(entry.new_status) }}</span>
                <span class="outcome-step-date">{{ formatDateTime(entry.changed_at) }}</span>
                <p v-if="!memberView && entry.note" class="outcome-step-note muted">{{ entry.note }}</p>
              </div>
            </li>
          </ul>
        </div>

        <div v-if="report.appeals && report.appeals.length > 0" class="outcome-appeals" data-testid="appeals-list">
          <h4>Appeals</h4>
          <article v-for="(appeal, index) in report.appeals" :key="appeal.id" class="outcome-appeal-card">
            <p><strong>Appeal #{{ index + 1 }}</strong></p>
            <p>Submitted: {{ formatDateTime(appeal.submitted_at) }}</p>
            <p>Status: {{ appealStatusLabel(appeal.status) }}</p>
            <p>Reason: {{ appeal.reason }}</p>
            <p v-if="appeal.response">Response: {{ appeal.response }}</p>
            <p v-else class="muted">Response: Pending</p>
          </article>
        </div>

        <div v-if="memberView && canAppeal(report)" class="outcome-actions">
          <button
            class="button secondary"
            type="button"
            data-testid="request-appeal"
            @click="openAppealForm(report)"
          >
            Request Correction / Appeal
          </button>
        </div>

        <div v-if="!memberView && canManage" class="outcome-actions">
          <button
            class="button secondary"
            type="button"
            data-testid="update-status"
            @click="openUpdateForm(report)"
          >
            Update Status
          </button>
        </div>
      </article>

      <button
        v-if="!memberView && canManage"
        class="button outcome-record-cta"
        type="button"
        data-testid="record-external-report"
        @click="showRecordForm = true"
      >
        Record External Report
      </button>
    </template>

    <dialog v-if="showRecordForm" open class="dialog" data-testid="record-report-dialog">
      <form class="stack" @submit.prevent="submitRecord">
        <h3>Record External Report</h3>
        <label class="field">
          Platform
          <select v-model="recordForm.platform" required>
            <option value="">Select platform</option>
            <option v-for="option in DESTINATION_PLATFORM_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="field">
          Reporting channel
          <input v-model="recordForm.reporting_channel" required maxlength="255" />
        </label>
        <label class="field">
          External reference (optional)
          <input v-model="recordForm.external_reference" maxlength="255" />
        </label>
        <label class="field">
          Reported at
          <input v-model="recordForm.reported_at" type="datetime-local" required />
        </label>
        <label class="field">
          Initial note
          <textarea v-model="recordForm.note" rows="3" />
        </label>
        <p v-if="formError" class="error">{{ formError }}</p>
        <div class="actions">
          <button class="button" type="submit" :disabled="formBusy">Record</button>
          <button class="button secondary" type="button" @click="showRecordForm = false">Cancel</button>
        </div>
      </form>
    </dialog>

    <dialog v-if="updateTarget" open class="dialog" data-testid="update-report-dialog">
      <form class="stack" @submit.prevent="submitUpdate">
        <h3>Update External Report</h3>
        <label class="field">
          Status
          <select v-model="updateForm.status" required>
            <option v-for="option in EXTERNAL_REPORT_STATUS_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label v-if="updateForm.status === 'decision'" class="field">
          Decision
          <select v-model="updateForm.decision" required>
            <option value="">Select decision</option>
            <option v-for="option in EXTERNAL_REPORT_DECISION_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label v-if="updateForm.status === 'outcome'" class="field">
          Outcome
          <select v-model="updateForm.outcome" required>
            <option value="">Select outcome</option>
            <option v-for="option in EXTERNAL_REPORT_OUTCOME_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label v-if="updateForm.status === 'outcome'" class="field">
          Outcome source
          <select v-model="updateForm.outcome_source">
            <option v-for="option in EXTERNAL_REPORT_SOURCE_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label v-if="updateForm.status === 'outcome'" class="field">
          Reporter-visible summary
          <textarea v-model="updateForm.reporter_visible_summary" rows="2" />
        </label>
        <label class="field">
          Verification
          <select v-model="updateForm.verification_status">
            <option v-for="option in EXTERNAL_REPORT_VERIFICATION_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="field">
          Note
          <textarea v-model="updateForm.note" rows="2" />
        </label>
        <p v-if="formError" class="error">{{ formError }}</p>
        <div class="actions">
          <button class="button" type="submit" :disabled="formBusy">Save</button>
          <button class="button secondary" type="button" @click="updateTarget = null">Cancel</button>
        </div>
      </form>
    </dialog>

    <dialog v-if="appealTarget" open class="dialog" data-testid="appeal-dialog">
      <form class="stack" @submit.prevent="submitAppeal">
        <h3>Request Correction / Appeal</h3>
        <p class="muted">
          This records that an appeal was submitted — it does not automatically send anything externally.
        </p>
        <label class="field">
          Reason
          <textarea v-model="appealForm.reason" required rows="4" />
        </label>
        <label class="field">
          Additional evidence
          <textarea v-model="appealForm.additional_evidence" rows="3" />
        </label>
        <label class="field">
          Reference (optional)
          <input v-model="appealForm.reference" />
        </label>
        <p v-if="formError" class="error">{{ formError }}</p>
        <div class="actions">
          <button class="button" type="submit" :disabled="formBusy">Appeal Submitted</button>
          <button class="button secondary" type="button" @click="appealTarget = null">Cancel</button>
        </div>
      </form>
    </dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { communityApi } from '@/services/community';
import type { ExternalReportStatus, IncidentExternalReportRecord } from '@/types';
import {
  DESTINATION_PLATFORM_OPTIONS,
  EXTERNAL_REPORT_DECISION_OPTIONS,
  EXTERNAL_REPORT_OUTCOME_OPTIONS,
  EXTERNAL_REPORT_SOURCE_OPTIONS,
  EXTERNAL_REPORT_STATUS_OPTIONS,
  EXTERNAL_REPORT_VERIFICATION_OPTIONS,
  appealStatusLabel,
  destinationPlatformLabel,
  externalReportDecisionLabel,
  externalReportOutcomeLabel,
  externalReportSourceLabel,
  externalReportStatusLabel,
  externalReportVerificationLabel,
  fromDatetimeLocalValue,
  toDatetimeLocalValue,
} from '@/utils/communityShield';
import { formatDateTime } from '@/utils/date';

const props = defineProps<{
  organizationId: number;
  reportId: number;
  memberView?: boolean;
  canManage?: boolean;
  initialReports?: IncidentExternalReportRecord[];
}>();

const reports = ref<IncidentExternalReportRecord[]>(props.initialReports ?? []);
const isLoading = ref(false);
const loadError = ref<string | null>(null);
const showRecordForm = ref(false);
const updateTarget = ref<IncidentExternalReportRecord | null>(null);
const appealTarget = ref<IncidentExternalReportRecord | null>(null);
const formError = ref<string | null>(null);
const formBusy = ref(false);

const recordForm = ref({
  platform: '',
  reporting_channel: '',
  external_reference: '',
  reported_at: toDatetimeLocalValue(new Date().toISOString()),
  note: '',
});

const updateForm = ref({
  status: 'reported' as ExternalReportStatus,
  decision: '',
  outcome: '',
  outcome_source: 'reviewer_observation',
  reporter_visible_summary: '',
  verification_status: 'unverified',
  note: '',
});

const appealForm = ref({
  reason: '',
  additional_evidence: '',
  reference: '',
});

async function loadReports(): Promise<void> {
  if (props.initialReports) {
    reports.value = props.initialReports;
    return;
  }

  isLoading.value = true;
  loadError.value = null;

  try {
    reports.value = await communityApi.externalReports(props.organizationId, props.reportId);
  } catch {
    loadError.value = 'Unable to load outcome tracking.';
  } finally {
    isLoading.value = false;
  }
}

function isTimelineStepDone(step: ExternalReportStatus, current: ExternalReportStatus): boolean {
  const order: ExternalReportStatus[] = ['reported', 'under_review', 'decision', 'outcome'];
  return order.indexOf(step) <= order.indexOf(current);
}

function canAppeal(report: IncidentExternalReportRecord): boolean {
  return report.status === 'decision' || report.status === 'outcome';
}

function openUpdateForm(report: IncidentExternalReportRecord): void {
  updateTarget.value = report;
  updateForm.value = {
    status: report.status,
    decision: report.decision ?? '',
    outcome: report.outcome ?? '',
    outcome_source: report.outcome_source ?? 'reviewer_observation',
    reporter_visible_summary: report.reporter_visible_summary ?? '',
    verification_status: report.verification_status ?? 'unverified',
    note: '',
  };
}

function openAppealForm(report: IncidentExternalReportRecord): void {
  appealTarget.value = report;
  appealForm.value = { reason: '', additional_evidence: '', reference: '' };
  formError.value = null;
}

async function submitRecord(): Promise<void> {
  formBusy.value = true;
  formError.value = null;

  try {
    const reportedAt = fromDatetimeLocalValue(recordForm.value.reported_at);
    if (!reportedAt) {
      formError.value = 'Reported date is required.';
      return;
    }

    await communityApi.createExternalReport(props.organizationId, props.reportId, {
      platform: recordForm.value.platform,
      reporting_channel: recordForm.value.reporting_channel,
      external_reference: recordForm.value.external_reference || undefined,
      reported_at: reportedAt,
      note: recordForm.value.note || undefined,
    });

    showRecordForm.value = false;
    await loadReports();
  } catch {
    formError.value = 'Unable to record external report.';
  } finally {
    formBusy.value = false;
  }
}

async function submitUpdate(): Promise<void> {
  if (!updateTarget.value) {
    return;
  }

  formBusy.value = true;
  formError.value = null;

  try {
    await communityApi.updateExternalReport(
      props.organizationId,
      props.reportId,
      updateTarget.value.id,
      {
        status: updateForm.value.status,
        decision: updateForm.value.decision || undefined,
        outcome: updateForm.value.outcome || undefined,
        outcome_source: updateForm.value.outcome_source || undefined,
        reporter_visible_summary: updateForm.value.reporter_visible_summary || undefined,
        verification_status: updateForm.value.verification_status,
        note: updateForm.value.note || undefined,
      },
    );

    updateTarget.value = null;
    await loadReports();
  } catch {
    formError.value = 'Unable to update external report.';
  } finally {
    formBusy.value = false;
  }
}

async function submitAppeal(): Promise<void> {
  if (!appealTarget.value) {
    return;
  }

  formBusy.value = true;
  formError.value = null;

  try {
    await communityApi.submitExternalReportAppeal(
      props.organizationId,
      props.reportId,
      appealTarget.value.id,
      {
        reason: appealForm.value.reason,
        additional_evidence: appealForm.value.additional_evidence || undefined,
        reference: appealForm.value.reference || undefined,
      },
      props.memberView,
    );

    appealTarget.value = null;
    await loadReports();
  } catch {
    formError.value = 'Unable to submit appeal.';
  } finally {
    formBusy.value = false;
  }
}

watch(
  () => [props.organizationId, props.reportId],
  () => {
    void loadReports();
  },
);

onMounted(() => {
  void loadReports();
});
</script>

<style scoped>
.dialog {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  margin-top: var(--space-4);
  max-width: 32rem;
  background: var(--surface);
  box-shadow: var(--shadow-md);
}
</style>
