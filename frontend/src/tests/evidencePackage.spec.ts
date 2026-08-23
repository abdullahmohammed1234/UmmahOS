import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import ReviewDetailPage from '@/pages/admin/ReviewDetailPage.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type {
  IncidentEvidencePackage,
  IncidentReviewPackage,
  Membership,
  Organization,
  OrganizationContext,
  User,
} from '@/types';

const reviewPackageMock = vi.fn();
const evidencePackageMock = vi.fn();
const exportJsonMock = vi.fn();
const exportPdfMock = vi.fn();
const contextMock = vi.fn();
const membersMock = vi.fn();

vi.mock('@/services/community', () => ({
  communityApi: {
    reviewPackage: (...args: unknown[]) => reviewPackageMock(...args),
    evidencePackage: (...args: unknown[]) => evidencePackageMock(...args),
    exportEvidenceJson: (...args: unknown[]) => exportJsonMock(...args),
    exportEvidencePdf: (...args: unknown[]) => exportPdfMock(...args),
    startReview: vi.fn(),
    confirmReview: vi.fn(),
    markUncertain: vi.fn(),
    closeReview: vi.fn(),
    escalateReview: vi.fn(),
    requestContext: vi.fn(),
  },
}));

vi.mock('@/services/organizations', () => ({
  organizationApi: {
    context: (...args: unknown[]) => contextMock(...args),
    members: (...args: unknown[]) => membersMock(...args),
    list: vi.fn(),
    show: vi.fn(),
    update: vi.fn(),
  },
  organizationPath: (organizationId: number | string, suffix = '') =>
    `/organizations/${organizationId}${suffix}`,
}));

function organization(id: number, name: string): Organization {
  return {
    id,
    name,
    slug: name.toLowerCase().replace(/\s+/g, '-'),
    status: 'active',
  };
}

function membership(id: number, org: Organization, role: string): Membership {
  return {
    id,
    user: { id: 1, name: 'Reviewer', email: 'reviewer@example.com' },
    organization: org,
    role: {
      id: role === 'admin' ? 1 : role === 'community_safety_reviewer' ? 3 : 2,
      name: role,
      slug: role,
    },
  };
}

function contextFor(org: Organization, role: string, permissions: string[]): OrganizationContext {
  return {
    organization: org,
    membership: membership(org.id, org, role),
    role,
    permissions,
  };
}

const alpha = organization(1, 'Demo MSA Alpha');

const reviewerPermissions = [
  'organization.view',
  'incidents.view',
  'incidents.review',
  'incidents.request_context',
  'incidents.escalate',
  'incidents.classify',
  'incidents.export',
];

const memberPermissions = [
  'organization.view',
  'incidents.view',
  'content.view',
  'events.view',
  'courses.view',
  'members.view',
  'reports.view',
];

function reviewPackage(): IncidentReviewPackage {
  return {
    incident: {
      id: 104,
      organization_id: 1,
      platform: 'x',
      content_type: 'post',
      visibility: 'public',
      source_url: 'https://x.com/example/status/1',
      description: 'Flagship Alpha report',
      original_item_title: 'Campus post',
      original_item_content: "These people don't belong here.",
      original_item_author: '@demo',
      original_item_posted_at: '2026-08-20T14:20:00+00:00',
      observed_at: '2026-08-21T09:15:00+00:00',
      surrounding_context: 'Public timeline thread.',
      language: 'en',
      reporter_notes: 'Saw similar tone.',
      safety_classification: 'hate',
      classified_by: null,
      classified_at: null,
      status: 'resolved',
      review_outcome: 'confirmed',
      escalated: false,
      review_lock_version: 4,
      replies: [],
      related_items: [],
      created_at: '2026-08-22T12:00:00+00:00',
    },
    ai_assisted_triage: {
      label: 'AI Context Analysis',
      advisory_disclaimer: 'AI-assisted triage is advisory.',
      latest: {
        id: 9,
        incident_id: 104,
        provider: 'fake',
        model: 'fake-model',
        prompt_version: 'community_shield_context_v1',
        status: 'completed',
        analysis: {
          signals: [],
          classification: { label: 'potential_hate', confidence: 'moderate' },
          uncertainty: {
            level: 'high',
            explanation: 'Context may change interpretation.',
          },
          alternative_interpretation: 'Political grievance',
          recommended_action: { type: 'human_review', reason: 'Review needed' },
        },
        error_message: null,
        created_at: '2026-08-22T12:05:00+00:00',
      },
      history: [],
    },
    human_review: {
      outcome: 'confirmed',
      notes: 'Confirmed despite AI uncertainty.',
      escalated: false,
      escalation_reason: null,
      current_review: null,
      reviews: [],
      context_requests: [],
      history: [],
      allowed_actions: [],
    },
    queue_summary: {
      related_item_count: 1,
      reply_count: 2,
      ai_classification: 'potential_hate',
      ai_confidence: 'moderate',
      ai_uncertainty: 'high',
    },
  };
}

function evidencePackage(overrides: Partial<IncidentEvidencePackage> = {}): IncidentEvidencePackage {
  return {
    package: {
      schema_version: 1,
      package_version: 1,
      generated_at: '2026-08-22T15:00:00+00:00',
      generated_by: { name: 'Alpha Reviewer' },
      organization: { name: 'Demo MSA Alpha', slug: 'demo-msa-alpha' },
      source_incident_updated_at: '2026-08-22T14:00:00+00:00',
      hierarchy: {
        source_evidence: 'SOURCE EVIDENCE',
        ai_analysis: 'AI ANALYSIS — ADVISORY',
        human_review: 'HUMAN REVIEW — AUTHORITATIVE',
        reporting_guidance: 'REPORTING GUIDANCE',
      },
    },
    incident: {
      reference: 'CS-DEMO-MSA-ALPHA-104',
      submitted_at: '2026-08-22T12:00:00+00:00',
      observed_at: '2026-08-21T09:15:00+00:00',
      original_item_posted_at: '2026-08-20T14:20:00+00:00',
      status: 'resolved',
      review_outcome: 'confirmed',
      content_type: 'post',
      visibility: 'public',
      platform: 'x',
      language: 'en',
      source_url: 'https://x.com/example/status/1',
      description: 'Flagship Alpha report',
    },
    evidence: {
      label: 'SOURCE EVIDENCE',
      original_item: { content: 'Original' },
      surrounding_context: 'Context',
      replies: [{ content: 'Reply 1' }, { content: 'Reply 2' }, { content: 'Reply 3' }, { content: 'Reply 4' }],
      related_items: [{ platform: 'reddit' }, { platform: 'x' }],
      language: 'en',
      reporter_notes: { label: 'REPORTER-PROVIDED CONTEXT', notes: 'Notes' },
      reported_safety_classification: {
        label: 'Reported / captured classification',
        value: 'hate',
        note: 'Distinct',
      },
    },
    ai_analysis: {
      label: 'AI-GENERATED ANALYSIS',
      advisory: true,
      disclaimer: 'AI analysis is advisory.',
      current: {
        status: 'completed',
        confidence: 'moderate',
      },
      previous: [],
      uncertainty: {
        confidence: 'Moderate',
        uncertainty: 'High',
        interpretation_note: 'Context may change interpretation.',
      },
    },
    human_review: {
      label: 'HUMAN REVIEW',
      authoritative: true,
      disclaimer: 'Human review is authoritative.',
      status: 'reviewed',
      reviewer: 'Alpha Reviewer',
      review_started_at: '2026-08-22T13:00:00+00:00',
      review_completed_at: '2026-08-22T14:00:00+00:00',
      outcome: 'confirmed',
      human_classification: 'hate',
      notes: 'Confirmed',
      escalation: {
        escalated: false,
        escalated_by: null,
        escalated_at: null,
        reason: null,
        note: 'Internal only',
      },
      context_requests: [],
      history: [],
      decision: {
        outcome: 'confirmed',
        classification: 'hate',
        reviewer: 'Alpha Reviewer',
        reviewed_at: '2026-08-22T14:00:00+00:00',
        rationale: 'Confirmed',
        uncertain_prominence: null,
      },
    },
    references: [],
    reporting_route: {
      platform: 'x',
      platform_label: 'X',
      recommended_route: 'Use the platform\'s current in-app reporting mechanism for the original post or account.',
      general_instructions: 'Attach evidence.',
      safety_notes: 'Avoid redistributing.',
      privacy_notes: 'Share only required evidence.',
      last_reviewed: '2026-08-22',
      disclaimer: 'Informational only.',
      automatic_submission: false,
    },
    safety_privacy_notes: {
      label: 'SAFETY & PRIVACY',
      notes: [
        'Avoid redistributing harmful content unnecessarily.',
        'Share only the evidence required for the report.',
      ],
      reporting_disclaimer: 'Informational only.',
    },
    disclaimers: {
      ai: 'AI analysis is advisory.',
      human_review: 'Human review is authoritative.',
      reporting: 'Informational only.',
    },
    ...overrides,
  };
}

describe('Evidence package export UI', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    reviewPackageMock.mockReset();
    evidencePackageMock.mockReset();
    exportJsonMock.mockReset();
    exportPdfMock.mockReset();
    contextMock.mockReset();
    membersMock.mockReset();
    membersMock.mockResolvedValue([]);

    Object.defineProperty(window.URL, 'createObjectURL', {
      writable: true,
      value: vi.fn(() => 'blob:mock'),
    });
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      writable: true,
      value: vi.fn(),
    });
  });

  async function mountDetail(permissions: string[], role = 'community_safety_reviewer') {
    const auth = useAuthStore();
    const organization = useOrganizationStore();
    const user: User = {
      id: 1,
      name: 'Reviewer',
      email: 'reviewer@example.com',
      memberships: [membership(1, alpha, role)],
    };
    auth.user = user;
    auth.token = 'token';
    organization.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(contextFor(alpha, role, permissions));
    await organization.loadContext();

    reviewPackageMock.mockResolvedValue(reviewPackage());
    evidencePackageMock.mockResolvedValue(evidencePackage());
    exportJsonMock.mockResolvedValue(new Blob(['{}'], { type: 'application/json' }));
    exportPdfMock.mockResolvedValue(new Blob(['%PDF'], { type: 'application/pdf' }));

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/community-shield/reports/:id', component: ReviewDetailPage },
        { path: '/community-shield/review-queue', component: { template: '<div />' } },
      ],
    });
    await router.push('/community-shield/reports/104');
    await router.isReady();

    const wrapper = mount(ReviewDetailPage, {
      global: { plugins: [router] },
    });
    await flushPromises();
    return wrapper;
  }

  it('shows evidence package section for authorized exporters', async () => {
    const wrapper = await mountDetail(reviewerPermissions);
    expect(wrapper.find('[data-testid="evidence-package-section"]').exists()).toBe(true);
  });

  it('hides export controls for members without export permission', async () => {
    const wrapper = await mountDetail(memberPermissions, 'member');
    expect(wrapper.find('[data-testid="evidence-package-section"]').exists()).toBe(false);
  });

  it('loads package preview with AI uncertainty, human decision, reporting route, and privacy notes', async () => {
    const wrapper = await mountDetail(reviewerPermissions);
    await wrapper.get('[data-testid="view-evidence-package"]').trigger('click');
    await flushPromises();

    expect(evidencePackageMock).toHaveBeenCalledWith(1, '104');
    expect(wrapper.get('[data-testid="evidence-package-preview"]').text()).toContain('INCIDENT EVIDENCE PACKAGE');
    expect(wrapper.get('[data-testid="package-ai-summary"]').text()).toContain('High uncertainty');
    expect(wrapper.get('[data-testid="package-reporting-route"]').text()).toContain('X');
    expect(wrapper.get('[data-testid="package-privacy-notes"]').text()).toContain('Review sensitive information');

    await wrapper.get('[data-testid="toggle-package-details"]').trigger('click');
    expect(wrapper.get('[data-testid="package-ai-uncertainty"]').text()).toContain('Context may change');
    expect(wrapper.get('[data-testid="package-human-decision"]').text()).toContain('Confirmed');
    expect(wrapper.text()).toContain('Avoid redistributing harmful content unnecessarily.');
  });

  it('exports JSON and PDF with loading feedback', async () => {
    const wrapper = await mountDetail(reviewerPermissions);

    await wrapper.get('[data-testid="export-json"]').trigger('click');
    await flushPromises();
    expect(exportJsonMock).toHaveBeenCalled();
    expect(wrapper.get('[data-testid="export-status"]').text()).toBe('Report ready.');

    await wrapper.get('[data-testid="export-pdf"]').trigger('click');
    await flushPromises();
    expect(exportPdfMock).toHaveBeenCalled();
    expect(wrapper.get('[data-testid="export-status"]').text()).toBe('Report ready.');
  });

  it('shows error state when export fails', async () => {
    const wrapper = await mountDetail(reviewerPermissions);
    exportPdfMock.mockRejectedValueOnce(new Error('fail'));

    await wrapper.get('[data-testid="export-pdf"]').trigger('click');
    await flushPromises();

    expect(wrapper.get('[data-testid="export-error"]').text()).toContain('Unable to export PDF');
  });

  it('shows not yet reviewed and AI unavailable states in the package preview', async () => {
    const wrapper = await mountDetail(reviewerPermissions);
    evidencePackageMock.mockResolvedValue(
      evidencePackage({
        ai_analysis: {
          label: 'AI-GENERATED ANALYSIS',
          advisory: true,
          disclaimer: 'AI analysis is advisory.',
          current: { status: 'failed', error_message: 'Analysis could not be completed.' },
          previous: [],
          uncertainty: {
            confidence: 'Not provided',
            uncertainty: 'Not provided',
            interpretation_note: 'Not provided',
          },
        },
        human_review: {
          label: 'HUMAN REVIEW',
          authoritative: true,
          disclaimer: 'Human review is authoritative.',
          status: 'not_yet_reviewed',
          reviewer: null,
          review_started_at: null,
          review_completed_at: null,
          outcome: null,
          human_classification: null,
          notes: null,
          escalation: {
            escalated: false,
            escalated_by: null,
            escalated_at: null,
            reason: null,
            note: 'Internal only',
          },
          context_requests: [],
          history: [],
          decision: {
            outcome: null,
            classification: null,
            reviewer: null,
            reviewed_at: null,
            rationale: null,
            uncertain_prominence: null,
          },
        },
      }),
    );

    await wrapper.get('[data-testid="view-evidence-package"]').trigger('click');
    await flushPromises();

    expect(wrapper.get('[data-testid="package-review-status"]').text()).toContain('Not yet reviewed');
    expect(wrapper.get('[data-testid="package-ai-summary"]').text()).toContain('Not provided');
  });
});
