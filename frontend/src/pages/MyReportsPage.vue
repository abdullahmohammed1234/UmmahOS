<template>
  <section class="panel content stack" data-testid="my-reports-page">
    <header>
      <p class="eyebrow">Community Shield</p>
      <h1>My Reports</h1>
      <p class="muted">Track what happened after you submitted a report.</p>
    </header>

    <p v-if="error" class="error" data-testid="my-reports-error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading your reports…</p>
    <p v-else-if="reports.length === 0" class="muted" data-testid="my-reports-empty">
      You have not submitted any Community Shield reports yet.
    </p>

    <ul v-else class="report-list">
      <li v-for="report in reports" :key="report.id">
        <RouterLink :to="`/community-shield/my-reports/${report.id}`" data-testid="my-report-link">
          <strong>{{ report.reference }}</strong>
          · {{ platformLabel(report.platform) }}
          · {{ statusLabel(report.status) }}
          <span v-if="report.external_report_count"> · {{ report.external_report_count }} external report(s)</span>
        </RouterLink>
        <p class="muted">Submitted {{ formatDateTime(report.submitted_at) }}</p>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import { communityApi } from '@/services/community';
import type { MemberReportSummary } from '@/types';
import { platformLabel, statusLabel } from '@/utils/communityShield';
import { formatDateTime } from '@/utils/date';

const reports = ref<MemberReportSummary[]>([]);

const { isLoading, error } = useOrganizationQuery(async (orgId) => {
  reports.value = await communityApi.myReports(orgId);
});
</script>

<style scoped>
.report-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.report-list li {
  border-bottom: 1px solid var(--line);
  padding: 0.75rem 0;
}
</style>
