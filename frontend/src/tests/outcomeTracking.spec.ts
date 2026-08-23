import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import OutcomeTrackingPanel from '@/components/OutcomeTrackingPanel.vue';
import MyReportDetailPage from '@/pages/MyReportDetailPage.vue';
import ReviewDetailPage from '@/pages/admin/ReviewDetailPage.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type { IncidentExternalReportRecord, IncidentReviewPackage, OrganizationContext } from '@/types';

const externalReportsMock = vi.fn();
const createExternalReportMock = vi.fn();
const updateExternalReportMock = vi.fn();
const submitAppealMock = vi.fn();
const myReportMock = vi.fn();
const myReportsMock = vi.fn();
const reviewPackageMock = vi.fn();

vi.mock('@/services/community', () => ({
  communityApi: {
    externalReports: (...args: unknown[]) => externalReportsMock(...args),
    createExternalReport: (...args: unknown[]) => createExternalReportMock(...args),
    updateExternalReport: (...args: unknown[]) => updateExternalReportMock(...args),
    submitExternalReportAppeal: (...args: unknown[]) => submitAppealMock(...args),
    myReport: (...args: unknown[]) => myReportMock(...args),
    myReports: (...args: unknown[]) => myReportsMock(...args),
    reviewPackage: (...args: unknown[]) => reviewPackageMock(...args),
    evidencePackage: vi.fn(),
    exportEvidenceJson: vi.fn(),
    exportEvidencePdf: vi.fn(),
  },
}));

vi.mock('@/services/organizations', () => ({
  organizationApi: {
    context: (...args: unknown[]) => contextMock(...args),
    members: vi.fn(),
    list: vi.fn(),
    show: vi.fn(),
    update: vi.fn(),
  },
  organizationPath: (organizationId: number | string, suffix = '') =>
    `/organizations/${organizationId}${suffix}`,
}));

const contextMock = vi.fn();

function reviewerContext(): OrganizationContext {
  const org = { id: 1, name: 'Demo MSA Alpha', slug: 'demo-msa-alpha', status: 'active' as const };
  return {
    organization: org,
    membership: {
      id: 1,
      user: { id: 1, name: 'Reviewer', email: 'reviewer@example.com' },
      organization: org,
      role: { id: 3, name: 'Community Safety Reviewer', slug: 'community_safety_reviewer' },
    },
    role: 'community_safety_reviewer',
    permissions: [
      'organization.view',
      'incidents.view',
      'incidents.review',
      'incidents.export',
      'incidents.outcomes.view',
      'incidents.outcomes.manage',
      'incidents.outcomes.appeal',
    ],
  };
}

function memberContext(): OrganizationContext {
  const org = { id: 1, name: 'Demo MSA Alpha', slug: 'demo-msa-alpha', status: 'active' as const };
  return {
    organization: org,
    membership: {
      id: 2,
      user: { id: 2, name: 'Member', email: 'member@example.com' },
      organization: org,
      role: { id: 2, name: 'Member', slug: 'member' },
    },
    role: 'member',
    permissions: ['organization.view', 'incidents.view', 'incidents.outcomes.view', 'incidents.outcomes.appeal'],
  };
}

const sampleExternalReport: IncidentExternalReportRecord = {
  id: 10,
  incident_id: 5,
  platform: 'reddit',
  reporting_channel: 'In-app report',
  external_reference: 'RDT-4821',
  reported_at: '2026-08-20T12:00:00Z',
  status: 'under_review',
  decision: null,
  decision_note: null,
  outcome: null,
  outcome_source: null,
  outcome_summary: null,
  reporter_visible_summary: 'Your report is being reviewed.',
  verification_status: 'unverified',
  internal_notes: 'Private note',
  created_by: null,
  updated_by: null,
  status_history: [
    {
      id: 1,
      previous_status: null,
      new_status: 'reported',
      decision: null,
      outcome: null,
      changed_by: null,
      changed_at: '2026-08-20T12:00:00Z',
      note: null,
    },
  ],
  appeals: [],
};

describe('Outcome tracking', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    externalReportsMock.mockReset();
    createExternalReportMock.mockReset();
    updateExternalReportMock.mockReset();
    submitAppealMock.mockReset();
    myReportMock.mockReset();
    myReportsMock.mockReset();
    reviewPackageMock.mockReset();
  });

  it('shows outcome tracking to authorized reviewers', async () => {
    externalReportsMock.mockResolvedValue([sampleExternalReport]);
    reviewPackageMock.mockResolvedValue({
      incident: { id: 5, platform: 'reddit', content_type: 'post', visibility: 'public', status: 'resolved' },
      ai_assisted_triage: { label: '', advisory_disclaimer: '', latest: null, history: [] },
      human_review: {
        outcome: 'confirmed',
        notes: null,
        escalated: false,
        escalation_reason: null,
        current_review: null,
        reviews: [],
        context_requests: [],
        history: [],
        allowed_actions: [],
      },
      queue_summary: {
        related_item_count: 0,
        reply_count: 0,
        ai_classification: null,
        ai_confidence: null,
        ai_uncertainty: null,
      },
    } as unknown as IncidentReviewPackage);

    const orgContext = reviewerContext();
    contextMock.mockResolvedValue(orgContext);

    const auth = useAuthStore();
    auth.persist('token', {
      id: 1,
      name: 'Reviewer',
      email: 'reviewer@example.com',
      memberships: [orgContext.membership],
    });

    const organization = useOrganizationStore();
    organization.persistCurrentOrganization(orgContext.organization.id);
    await organization.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/community-shield/review-queue/:id', component: ReviewDetailPage }],
    });
    router.push('/community-shield/review-queue/5');
    await router.isReady();

    const wrapper = mount(ReviewDetailPage, {
      global: { plugins: [router] },
    });

    await flushPromises();

    expect(wrapper.find('[data-testid="outcome-tracking-section"]').exists()).toBe(true);
    expect(externalReportsMock).toHaveBeenCalled();
  });

  it('member sees own outcome without internal notes', async () => {
    myReportMock.mockResolvedValue({
      id: 5,
      reference: 'CS-DEMO-MSA-ALPHA-5',
      platform: 'x',
      content_type: 'post',
      status: 'resolved',
      review_outcome: 'confirmed',
      submitted_at: '2026-08-20T12:00:00Z',
      external_reports: [{ ...sampleExternalReport, internal_notes: 'Private note' }],
    });

    const orgContext = memberContext();
    contextMock.mockResolvedValue(orgContext);

    const auth = useAuthStore();
    auth.persist('token', {
      id: 2,
      name: 'Member',
      email: 'member@example.com',
      memberships: [orgContext.membership],
    });

    const organization = useOrganizationStore();
    organization.persistCurrentOrganization(orgContext.organization.id);
    await organization.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/community-shield/my-reports/:id', component: MyReportDetailPage }],
    });
    router.push('/community-shield/my-reports/5');
    await router.isReady();

    const wrapper = mount(MyReportDetailPage, {
      global: { plugins: [router] },
    });

    await flushPromises();

    expect(wrapper.text()).toContain('What happened next?');
    expect(wrapper.text()).not.toContain('Private note');
  });

  it('renders record external report form for managers', async () => {
    externalReportsMock.mockResolvedValue([]);

    const wrapper = mount(OutcomeTrackingPanel, {
      props: {
        organizationId: 1,
        reportId: 5,
        canManage: true,
      },
    });

    await flushPromises();

    expect(wrapper.find('[data-testid="record-external-report"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="outcome-empty"]').text()).toContain('No external reporting activity');
  });

  it('shows verification state and outcome source', async () => {
    externalReportsMock.mockResolvedValue([
      {
        ...sampleExternalReport,
        status: 'outcome',
        outcome: 'content_removed',
        outcome_source: 'reporter_observation',
        verification_status: 'unverified',
      },
    ]);

    const wrapper = mount(OutcomeTrackingPanel, {
      props: {
        organizationId: 1,
        reportId: 5,
        canManage: false,
        memberView: true,
      },
    });

    await flushPromises();

    expect(wrapper.find('[data-testid="verification-status"]').text()).toContain('Unverified');
    expect(wrapper.text()).toContain('Reporter observation');
  });
});
