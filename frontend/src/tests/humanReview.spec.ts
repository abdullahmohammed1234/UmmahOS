import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import AppShell from '@/components/AppShell.vue';
import CommunityShieldPage from '@/pages/CommunityShieldPage.vue';
import ReviewQueuePage from '@/pages/admin/ReviewQueuePage.vue';
import ReviewDetailPage from '@/pages/admin/ReviewDetailPage.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type {
  IncidentReviewPackage,
  Membership,
  Organization,
  OrganizationContext,
  ReviewQueueItem,
  User,
} from '@/types';

const reviewQueueMock = vi.fn();
const reviewPackageMock = vi.fn();
const startReviewMock = vi.fn();
const confirmReviewMock = vi.fn();
const markUncertainMock = vi.fn();
const closeReviewMock = vi.fn();
const escalateReviewMock = vi.fn();
const requestContextMock = vi.fn();
const contextMock = vi.fn();
const membersMock = vi.fn();
const overviewMock = vi.fn();

vi.mock('@/services/community', () => ({
  communityApi: {
    reviewQueue: (...args: unknown[]) => reviewQueueMock(...args),
    reviewPackage: (...args: unknown[]) => reviewPackageMock(...args),
    startReview: (...args: unknown[]) => startReviewMock(...args),
    confirmReview: (...args: unknown[]) => confirmReviewMock(...args),
    markUncertain: (...args: unknown[]) => markUncertainMock(...args),
    closeReview: (...args: unknown[]) => closeReviewMock(...args),
    escalateReview: (...args: unknown[]) => escalateReviewMock(...args),
    requestContext: (...args: unknown[]) => requestContextMock(...args),
    communityShieldOverview: (...args: unknown[]) => overviewMock(...args),
    evidencePackage: vi.fn(),
    exportEvidenceJson: vi.fn(),
    exportEvidencePdf: vi.fn(),
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
    user: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
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
const beta = organization(2, 'Demo MSA Beta');

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

const adminPermissions = [
  'organization.manage',
  'incidents.manage',
  'incidents.review',
  'incidents.classify',
  'incidents.escalate',
  'incidents.request_context',
  'incidents.export',
  'members.manage',
  'members.view',
];

function queueItem(overrides: Partial<ReviewQueueItem> = {}): ReviewQueueItem {
  return {
    id: 104,
    platform: 'x',
    content_type: 'post',
    visibility: 'public',
    status: 'open',
    review_outcome: null,
    escalated: false,
    safety_classification: 'unclassified',
    related_item_count: 2,
    open_context_requests: 0,
    ai_assisted_triage: {
      classification: 'potential_hate',
      confidence: 'moderate',
      uncertainty: 'high',
      recommended_action: 'human_review',
    },
    current_reviewer: null,
    created_at: '2026-08-22T12:00:00+00:00',
    ...overrides,
  };
}

function reviewPackage(overrides: Partial<IncidentReviewPackage> = {}): IncidentReviewPackage {
  return {
    incident: {
      id: 104,
      organization_id: 1,
      platform: 'x',
      content_type: 'post',
      visibility: 'public',
      source_url: 'https://x.com/example/status/1',
      description: 'Flagship Alpha report',
      original_item_title: 'Campus students after jumuah',
      original_item_content: "These people don't belong here.",
      original_item_author: '@campusvoice_demo',
      original_item_posted_at: '2026-08-20T14:20:00+00:00',
      observed_at: '2026-08-21T09:15:00+00:00',
      surrounding_context: 'Public timeline thread about campus facilities.',
      language: 'en',
      reporter_notes: 'Saw similar tone earlier.',
      safety_classification: 'unclassified',
      classified_by: null,
      classified_at: null,
      status: 'open',
      review_outcome: null,
      escalated: false,
      review_lock_version: 1,
      replies: [
        {
          id: 1,
          author: '@ally_demo',
          content: 'This is wrong.',
          posted_at: '2026-08-20T14:35:00+00:00',
          position: 0,
        },
      ],
      related_items: [
        {
          id: 1,
          platform: 'reddit',
          content_type: 'post',
          reference_url: 'https://reddit.com/r/example',
          description: 'Nearly identical wording.',
          observed_at: '2026-08-21T21:00:00+00:00',
        },
      ],
      reported_by: { id: 2, name: 'Alpha Member', email: 'alpha.member@example.com' },
      created_at: '2026-08-22T12:00:00+00:00',
    },
    ai_assisted_triage: {
      label: 'AI Context Analysis',
      advisory_disclaimer:
        'AI-assisted triage is advisory. A trained human reviewer makes the authoritative decision.',
      latest: {
        id: 9,
        incident_id: 104,
        provider: 'fake',
        model: 'fake-model',
        prompt_version: 'community_shield_context_v1',
        status: 'completed',
        analysis: {
          signals: [
            {
              name: 'religious_identity_targeting',
              description: 'Targets Friday prayer association.',
              evidence: ['after Friday prayer'],
              confidence: 'moderate',
            },
          ],
          classification: { label: 'potential_hate', confidence: 'moderate' },
          uncertainty: {
            level: 'high',
            explanation: 'Multiple interpretations remain possible.',
          },
          alternative_interpretation: 'Could be political speech.',
          recommended_action: { type: 'human_review', reason: 'Needs human review.' },
        },
        created_at: '2026-08-22T12:05:00+00:00',
      },
      history: [
        {
          id: 9,
          incident_id: 104,
          provider: 'fake',
          model: 'fake-model',
          prompt_version: 'community_shield_context_v1',
          status: 'completed',
          analysis: null,
          created_at: '2026-08-22T12:05:00+00:00',
        },
      ],
    },
    human_review: {
      outcome: null,
      notes: null,
      escalated: false,
      escalation_reason: null,
      current_review: null,
      reviews: [],
      context_requests: [],
      history: [],
      allowed_actions: ['start'],
    },
    queue_summary: {
      related_item_count: 1,
      reply_count: 1,
      ai_classification: 'potential_hate',
      ai_confidence: 'moderate',
      ai_uncertainty: 'high',
    },
    ...overrides,
  };
}

async function mountWithAuth(
  component: object,
  routeName: string,
  params: Record<string, string> = {},
  orgContext: OrganizationContext = contextFor(alpha, 'community_safety_reviewer', reviewerPermissions),
  memberships: Membership[] = [membership(1, alpha, 'community_safety_reviewer')],
) {
  const pinia = createPinia();
  setActivePinia(pinia);

  const user: User = {
    id: 1,
    name: 'Multi Org User',
    email: 'multi.user@example.com',
    memberships,
  };

  const auth = useAuthStore();
  auth.persist('token', user);

  contextMock.mockResolvedValue(orgContext);
  membersMock.mockResolvedValue([]);

  const organization = useOrganizationStore();
  organization.persistCurrentOrganization(orgContext.organization.id);
  await organization.loadContext();

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'dashboard', component: { template: '<div />' } },
      { path: '/community-shield', name: 'community-shield', component: CommunityShieldPage },
      {
        path: '/community-shield/review-queue',
        name: 'community-shield-review-queue',
        component: ReviewQueuePage,
      },
      {
        path: '/community-shield/review-queue/:id',
        name: 'community-shield-review-detail',
        component: ReviewDetailPage,
      },
      { path: '/admin/community-shield', name: 'admin-incidents', component: { template: '<div />' } },
      { path: '/login', name: 'login', component: { template: '<div />' } },
    ],
  });

  await router.push({ name: routeName, params });
  await router.isReady();

  const wrapper = mount(component, {
    global: {
      plugins: [pinia, router],
    },
  });

  await flushPromises();
  return { wrapper, organization, router };
}

describe('Phase 6 human review workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    overviewMock.mockResolvedValue({ can_report: true, can_review: true, counts: { open: 1, reviewing: 0, resolved: 0 } });
    reviewQueueMock.mockResolvedValue([queueItem()]);
    reviewPackageMock.mockResolvedValue(reviewPackage());
    startReviewMock.mockResolvedValue(
      reviewPackage({
        incident: {
          ...reviewPackage().incident,
          status: 'reviewing',
          current_reviewer: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
          review_lock_version: 2,
        },
        human_review: {
          ...reviewPackage().human_review,
          allowed_actions: ['confirm', 'uncertain', 'close', 'escalate', 'request_context'],
        },
      }),
    );
  });

  it('shows Review Queue navigation for reviewers and not for members', async () => {
    const { wrapper: reviewerShell } = await mountWithAuth(
      AppShell,
      'community-shield-review-queue',
    );
    expect(reviewerShell.find('[data-testid="nav-review-queue"]').exists()).toBe(true);

    const { wrapper: memberShell } = await mountWithAuth(
      AppShell,
      'community-shield',
      {},
      contextFor(alpha, 'member', memberPermissions),
      [membership(1, alpha, 'member')],
    );
    expect(memberShell.find('[data-testid="nav-review-queue"]').exists()).toBe(false);
  });

  it('lets admins retain review queue access', async () => {
    const { wrapper } = await mountWithAuth(
      ReviewQueuePage,
      'community-shield-review-queue',
      {},
      contextFor(alpha, 'admin', adminPermissions),
      [membership(1, alpha, 'admin')],
    );

    expect(wrapper.find('[data-testid="review-denied"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="review-queue"]').exists()).toBe(true);
  });

  it('denies the review queue to ordinary members', async () => {
    const { wrapper } = await mountWithAuth(
      ReviewQueuePage,
      'community-shield-review-queue',
      {},
      contextFor(alpha, 'member', memberPermissions),
      [membership(1, alpha, 'member')],
    );

    expect(wrapper.find('[data-testid="review-denied"]').exists()).toBe(true);
    expect(reviewQueueMock).not.toHaveBeenCalled();
  });

  it('renders AI-assisted triage without calling it an AI verdict', async () => {
    const { wrapper } = await mountWithAuth(ReviewQueuePage, 'community-shield-review-queue');

    expect(wrapper.find('[data-testid="ai-assisted-triage"]').text()).toContain('AI-assisted triage');
    expect(wrapper.text()).not.toContain('AI Verdict');
    expect(wrapper.find('[data-testid="high-uncertainty-flag"]').exists()).toBe(true);
  });

  it('shows the complete evidence package and AI analysis on the review page', async () => {
    const { wrapper } = await mountWithAuth(ReviewDetailPage, 'community-shield-review-detail', {
      id: '104',
    });

    expect(wrapper.find('[data-testid="original-item-block"]').text()).toContain("don't belong here");
    expect(wrapper.find('[data-testid="surrounding-context-block"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="replies-block"]').text()).toContain('This is wrong.');
    expect(wrapper.find('[data-testid="related-items-block"]').text()).toContain('Reddit');
    expect(wrapper.find('[data-testid="reporter-notes-block"]').text()).toContain('similar tone');
    expect(wrapper.find('[data-testid="ai-context-analysis"]').text()).toContain('AI Context Analysis');
    expect(wrapper.find('[data-testid="high-uncertainty-banner"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="human-review-block"]').text()).toContain(
      'What is your determination?',
    );
  });

  it('starts review and supports confirm, uncertain, context, escalate, and close flows', async () => {
    const openPackage = reviewPackage();
    const started = reviewPackage({
      incident: {
        ...openPackage.incident,
        status: 'reviewing',
        current_reviewer: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
        review_lock_version: 2,
      },
      human_review: {
        ...openPackage.human_review,
        notes: 'Need preceding replies before classification.',
        history: [
          {
            id: 1,
            incident_id: 104,
            action: 'started',
            notes: 'Started review',
            actor: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
            created_at: '2026-08-22T14:32:00+00:00',
          },
        ],
        allowed_actions: ['confirm', 'uncertain', 'close', 'escalate', 'request_context'],
      },
    });

    reviewPackageMock.mockResolvedValue(openPackage);
    startReviewMock.mockResolvedValue(started);
    confirmReviewMock.mockResolvedValue(started);
    markUncertainMock.mockResolvedValue(started);
    escalateReviewMock.mockResolvedValue(started);
    closeReviewMock.mockResolvedValue(started);
    requestContextMock.mockResolvedValue({
      id: 1,
      incident_id: 104,
      reason: 'Need preceding replies.',
      status: 'open',
      requested_at: '2026-08-22T14:38:00+00:00',
      resolved_at: null,
    });

    const { wrapper } = await mountWithAuth(ReviewDetailPage, 'community-shield-review-detail', {
      id: '104',
    });

    await wrapper.find('[data-testid="start-review"]').trigger('click');
    await flushPromises();
    expect(startReviewMock).toHaveBeenCalled();
    expect(wrapper.find('[data-testid="review-history"]').text()).toContain('Started review');
    expect(wrapper.find('[data-testid="reviewer-notes"]').text()).toContain('preceding replies');

    // Subsequent package reloads (e.g. after context request) keep action buttons available.
    reviewPackageMock.mockResolvedValue(started);

    await wrapper.find('[data-testid="open-confirm"]').trigger('click');
    await wrapper.find('[data-testid="confirm-classification"]').setValue('hate');
    await wrapper.find('[data-testid="confirm-notes"]').setValue('Context supports the concern.');
    await wrapper.find('[data-testid="submit-confirm"]').trigger('click');
    await flushPromises();
    expect(confirmReviewMock).toHaveBeenCalled();

    await wrapper.find('[data-testid="open-uncertain"]').trigger('click');
    await wrapper.find('[data-testid="uncertain-notes"]').setValue('Incomplete evidence.');
    await wrapper.find('[data-testid="submit-uncertain"]').trigger('click');
    await flushPromises();
    expect(markUncertainMock).toHaveBeenCalled();

    await wrapper.find('[data-testid="open-request-context"]').trigger('click');
    await wrapper.find('[data-testid="context-reason"]').setValue('Need preceding replies.');
    await wrapper.find('[data-testid="submit-context"]').trigger('click');
    await flushPromises();
    expect(requestContextMock).toHaveBeenCalled();

    await wrapper.find('[data-testid="open-escalate"]').trigger('click');
    await wrapper.find('[data-testid="escalate-reason"]').setValue('Needs specialized review.');
    await wrapper.find('[data-testid="submit-escalate"]').trigger('click');
    await flushPromises();
    expect(escalateReviewMock).toHaveBeenCalled();

    await wrapper.find('[data-testid="open-close"]').trigger('click');
    await wrapper.find('[data-testid="close-notes"]').setValue('No further action required.');
    await wrapper.find('[data-testid="submit-close"]').trigger('click');
    await flushPromises();
    expect(closeReviewMock).toHaveBeenCalled();
  });

  it('isolates review queues when switching organizations', async () => {
    const { wrapper, organization } = await mountWithAuth(
      ReviewQueuePage,
      'community-shield-review-queue',
      {},
      contextFor(alpha, 'community_safety_reviewer', reviewerPermissions),
      [
        membership(1, alpha, 'community_safety_reviewer'),
        membership(2, beta, 'member'),
      ],
    );

    expect(reviewQueueMock).toHaveBeenCalledWith(1, expect.any(Object));

    contextMock.mockResolvedValue(contextFor(beta, 'member', memberPermissions));
    await organization.switchOrganization(2);
    await flushPromises();

    expect(wrapper.find('[data-testid="review-denied"]').exists()).toBe(true);
  });

  it('surfaces failed review actions safely', async () => {
    startReviewMock.mockRejectedValue({
      response: { status: 409, data: { message: 'This review was updated by another reviewer. Reload and try again.' } },
    });

    const { wrapper } = await mountWithAuth(ReviewDetailPage, 'community-shield-review-detail', {
      id: '104',
    });

    await wrapper.find('[data-testid="start-review"]').trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="action-error"]').text()).toContain(
      'updated by another reviewer',
    );
  });

  it('shows the review queue entry point on the member Community Shield page for reviewers', async () => {
    const { wrapper } = await mountWithAuth(CommunityShieldPage, 'community-shield');
    expect(wrapper.find('[data-testid="review-queue-link"]').exists()).toBe(true);
  });
});
