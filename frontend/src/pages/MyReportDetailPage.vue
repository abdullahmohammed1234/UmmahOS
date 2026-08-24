<template>
  <section class="panel content stack" data-testid="my-report-detail-page">
    <RouterLink to="/community-shield/my-reports">Back to My Reports</RouterLink>

    <p v-if="error" class="error" data-testid="my-report-error">{{ error }}</p>
    <p v-else-if="isLoading || !report" class="muted">Loading your report…</p>

    <template v-else>
      <header>
        <p class="eyebrow">What happened next?</p>
        <h1>{{ report.reference }}</h1>
        <p class="muted">
          {{ platformLabel(report.platform) }} · {{ statusLabel(report.status) }}
          <template v-if="report.review_outcome">
            · {{ reviewOutcomeLabel(report.review_outcome) }}
          </template>
        </p>
      </header>

      <p class="muted">
        This view shows reporter-visible progress only. Internal reviewer notes are not shown here.
      </p>

      <WorkflowSteps :steps="memberFlow" aria-label="Report progress" />

      <OutcomeTrackingPanel
        v-if="organization.currentOrganization"
        :organization-id="organization.currentOrganization.id"
        :report-id="report.id"
        :initial-reports="report.external_reports"
        member-view
      />
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import OutcomeTrackingPanel from '@/components/OutcomeTrackingPanel.vue';
import WorkflowSteps from '@/components/ui/WorkflowSteps.vue';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import type { MemberReportSummary } from '@/types';
import { platformLabel, reviewOutcomeLabel, statusLabel } from '@/utils/communityShield';

const organization = useOrganizationStore();
const route = useRoute();
const report = ref<MemberReportSummary | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const memberFlow = [
  'Reported',
  'Under Review',
  'Decision',
  'Outcome',
  'Appeal / Correction',
];

async function loadReport(): Promise<void> {
  const orgId = organization.currentOrganization?.id;
  const reportId = route.params.id;

  if (!orgId || !reportId) {
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    report.value = await communityApi.myReport(orgId, String(reportId));
  } catch {
    error.value = 'Unable to load this report.';
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  () => {
    void loadReport();
  },
  { immediate: true },
);
</script>
