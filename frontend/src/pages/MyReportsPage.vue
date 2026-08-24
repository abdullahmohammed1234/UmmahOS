<template>
  <section class="my-reports stack" data-testid="my-reports-page">
    <PageHeader
      eyebrow="Community Shield"
      title="My Reports"
      description="Track what happened after you submitted a report."
      test-id="my-reports-header"
    />

    <LoadingState v-if="isLoading" test-id="my-reports-loading" />
    <p v-else-if="error" class="error" data-testid="my-reports-error">{{ error }}</p>
    <EmptyState
      v-else-if="reports.length === 0"
      title="No reports yet"
      description="When you submit a Community Shield report, you can track its progress here."
      icon="🛡"
      test-id="my-reports-empty"
    >
      <template #action>
        <RouterLink class="button" to="/community-shield">Report a Concern</RouterLink>
      </template>
    </EmptyState>

    <div v-else class="report-grid">
      <RouterLink
        v-for="report in reports"
        :key="report.id"
        class="report-card panel card-link"
        :to="`/community-shield/my-reports/${report.id}`"
        data-testid="my-report-link"
      >
        <div class="report-card-header">
          <strong>{{ report.reference }}</strong>
          <span class="badge" :class="statusBadgeClass(report.status)">
            {{ statusLabel(report.status) }}
          </span>
        </div>
        <p class="report-meta muted">
          {{ platformLabel(report.platform) }}
          · Submitted {{ formatDateTime(report.submitted_at) }}
        </p>
        <p v-if="report.external_report_count" class="report-update muted">
          {{ report.external_report_count }} external report(s) recorded
        </p>
        <p v-if="report.review_outcome" class="report-outcome">
          Outcome: {{ reviewOutcomeLabel(report.review_outcome) }}
        </p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import EmptyState from '@/components/ui/EmptyState.vue';
import LoadingState from '@/components/ui/LoadingState.vue';
import PageHeader from '@/components/ui/PageHeader.vue';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { communityApi } from '@/services/community';
import type { MemberReportSummary } from '@/types';
import { platformLabel, reviewOutcomeLabel, statusLabel } from '@/utils/communityShield';
import { formatDateTime } from '@/utils/date';

const reports = ref<MemberReportSummary[]>([]);

const { isLoading, error } = useOrganizationQuery(async (orgId) => {
  reports.value = await communityApi.myReports(orgId);
});

function statusBadgeClass(status: string): string {
  if (status === 'resolved') return 'success';
  if (status === 'reviewing') return 'info';
  return 'neutral';
}
</script>

<style scoped>
.my-reports {
  max-width: var(--content-max);
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
}

.report-card {
  min-width: 0;
}

.report-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.report-meta,
.report-update,
.report-outcome {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
}

.report-outcome {
  color: var(--primary);
  font-weight: var(--font-medium);
}

@media (max-width: 640px) {
  .report-card-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
