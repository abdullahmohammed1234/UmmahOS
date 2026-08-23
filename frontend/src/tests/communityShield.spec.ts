import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import CommunityShieldPage from '@/pages/CommunityShieldPage.vue';
import AdminIncidentsPage from '@/pages/admin/AdminIncidentsPage.vue';
import AdminIncidentDetailPage from '@/pages/admin/AdminIncidentDetailPage.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type {
  Incident,
  IncidentAiAnalysis,
  Membership,
  Organization,
  OrganizationContext,
  User,
} from '@/types';

const reportIncidentMock = vi.fn();
const incidentsMock = vi.fn();
const incidentMock = vi.fn();
const updateIncidentMock = vi.fn();
const overviewMock = vi.fn();
const contextMock = vi.fn();
const membersMock = vi.fn();
const aiAnalysesMock = vi.fn();
const requestAiAnalysisMock = vi.fn();

vi.mock('@/services/community', () => ({
  communityApi: {
    reportIncident: (...args: unknown[]) => reportIncidentMock(...args),
    incidents: (...args: unknown[]) => incidentsMock(...args),
    incident: (...args: unknown[]) => incidentMock(...args),
    updateIncident: (...args: unknown[]) => updateIncidentMock(...args),
    communityShieldOverview: (...args: unknown[]) => overviewMock(...args),
    aiAnalyses: (...args: unknown[]) => aiAnalysesMock(...args),
    requestAiAnalysis: (...args: unknown[]) => requestAiAnalysisMock(...args),
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
    role: { id: role === 'admin' ? 1 : 2, name: role, slug: role },
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

function sampleIncident(overrides: Partial<Incident> = {}): Incident {
  return {
    id: 123,
    organization_id: 1,
    platform: 'x',
    content_type: 'post',
    visibility: 'public',
    source_url: null,
    description: 'Demo concern',
    original_item_title: null,
    original_item_content: null,
    original_item_author: null,
    original_item_posted_at: null,
    observed_at: '2026-08-21T12:00:00+00:00',
    surrounding_context: null,
    language: 'unknown',
    reporter_notes: null,
    safety_classification: 'unclassified',
    classified_by: null,
    classified_at: null,
    status: 'open',
    replies: [],
    related_items: [],
    reported_by: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
    ...overrides,
  };
}

function sampleAiAnalysis(overrides: Partial<IncidentAiAnalysis> = {}): IncidentAiAnalysis {
  return {
    id: 901,
    incident_id: 55,
    provider: 'fake',
    model: 'fake-model',
    prompt_version: 'community_shield_context_v1',
    status: 'completed',
    analysis: {
      signals: [
        {
          name: 'religious_identity_targeting',
          description: 'The language may reference a religious identity in a derogatory context.',
          evidence: ['Demo evidence phrase'],
          confidence: 'moderate',
        },
      ],
      classification: {
        label: 'potential_coded_visual_hate',
        confidence: 'moderate',
      },
      uncertainty: {
        level: 'moderate',
        explanation:
          'The surrounding conversation is incomplete and may change the interpretation.',
      },
      alternative_interpretation:
        "The phrase may be quoting another participant rather than expressing the author's own position.",
      recommended_action: {
        type: 'human_review',
        reason: 'Human review recommended.',
      },
    },
    requested_by: { id: 1, name: 'Multi Org User', email: 'multi.user@example.com' },
    created_at: '2026-08-22T19:00:00+00:00',
    advisory_disclaimer:
      'AI-generated analysis is advisory and may be incorrect. Human review is required for decisions.',
    ...overrides,
  };
}

describe('Community Shield UI', () => {
  const alpha = organization(1, 'Demo MSA Alpha');
  const beta = organization(2, 'Demo MSA Beta');
  let pinia: ReturnType<typeof createPinia>;

  beforeEach(() => {
    window.localStorage.clear();
    pinia = createPinia();
    setActivePinia(pinia);
    reportIncidentMock.mockReset();
    incidentsMock.mockReset();
    incidentMock.mockReset();
    updateIncidentMock.mockReset();
    overviewMock.mockReset();
    contextMock.mockReset();
    membersMock.mockReset();
    aiAnalysesMock.mockReset();
    requestAiAnalysisMock.mockReset();
    aiAnalysesMock.mockResolvedValue([]);

    const auth = useAuthStore();
    const user: User = {
      id: 4,
      name: 'Multi Org User',
      email: 'multi.user@example.com',
      memberships: [membership(10, alpha, 'member'), membership(11, beta, 'admin')],
    };
    auth.persist('test-token', user);
  });

  it('renders the Community Shield page and structured reporting controls', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    membersMock.mockResolvedValue([]);
    await store.loadContext();

    const wrapper = await mountMemberPage(pinia);

    expect(wrapper.text()).toContain('Community Shield');
    expect(wrapper.find('[data-testid="report-concern-cta"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="admin-review-link"]').exists()).toBe(false);

    await wrapper.get('[data-testid="report-concern-cta"]').trigger('click');

    expect(wrapper.find('[data-testid="report-form"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="section-original-item"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="section-context"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="section-replies"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="section-related"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="language"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('X');
    expect(wrapper.text()).toContain('YouTube');
    expect(wrapper.text()).toContain('Post');
    expect(wrapper.text()).toContain('Public');
    expect(wrapper.text()).toContain('Private / Direct');
  });

  it('supports platform, content type, and visibility selection with validation', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    membersMock.mockResolvedValue([]);
    await store.loadContext();

    const wrapper = await mountMemberPage(pinia);
    await wrapper.get('[data-testid="report-concern-cta"]').trigger('click');

    await wrapper.get('input[value="x"]').setValue(true);
    await wrapper.get('input[value="post"]').setValue(true);
    await wrapper.get('input[value="public"]').setValue(true);

    expect(wrapper.get('[data-testid="visibility-hint"]').text()).toContain(
      'This content is publicly accessible.',
    );

    await wrapper.get('[data-testid="submit-report"]').trigger('click');
    expect(wrapper.get('[data-testid="form-error"]').text()).toContain('required');
    expect(reportIncidentMock).not.toHaveBeenCalled();
  });

  it('captures original item, context, replies, related copies, and language on submit', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    membersMock.mockResolvedValue([]);
    await store.loadContext();

    reportIncidentMock.mockResolvedValue({
      incident: sampleIncident({
        language: 'en',
        original_item_content: 'Reported post text',
        surrounding_context: 'Thread context',
        replies: [{ author: 'ally', content: 'Reply one', posted_at: null, position: 0 }],
        related_items: [
          {
            platform: 'reddit',
            content_type: 'post',
            reference_url: null,
            description: 'Related copy',
            observed_at: null,
          },
        ],
      }),
      message: "Your report has been received by your MSA's Community Shield team.",
    });

    const wrapper = await mountMemberPage(pinia);
    await wrapper.get('[data-testid="report-concern-cta"]').trigger('click');
    await wrapper.get('input[value="x"]').setValue(true);
    await wrapper.get('input[value="post"]').setValue(true);
    await wrapper.get('input[value="public"]').setValue(true);
    await wrapper.get('[data-testid="description"]').setValue('Concern about a public post.');
    await wrapper.get('[data-testid="original-item-content"]').setValue('Reported post text');
    await wrapper.get('[data-testid="surrounding-context"]').setValue('Thread context');
    await wrapper.get('[data-testid="language"]').setValue('en');
    await wrapper.get('[data-testid="reporter-notes"]').setValue('Saw similar content earlier.');
    await wrapper.get('[data-testid="add-reply"]').trigger('click');
    await wrapper.get('[data-testid="reply-item"] textarea').setValue('Reply one');
    await wrapper.get('[data-testid="add-related-item"]').trigger('click');
    const related = wrapper.get('[data-testid="related-item"]');
    const relatedSelects = related.findAll('select');
    expect(relatedSelects.length).toBeGreaterThanOrEqual(2);
    await relatedSelects[0]!.setValue('reddit');
    await relatedSelects[1]!.setValue('post');
    await related.find('textarea').setValue('Related copy');
    await wrapper.get('[data-testid="submit-report"]').trigger('click');
    await flushPromises();

    expect(reportIncidentMock).toHaveBeenCalledWith(
      1,
      expect.objectContaining({
        platform: 'x',
        content_type: 'post',
        visibility: 'public',
        source_url: null,
        description: 'Concern about a public post.',
        original_item_content: 'Reported post text',
        surrounding_context: 'Thread context',
        language: 'en',
        reporter_notes: 'Saw similar content earlier.',
        replies: [
          expect.objectContaining({
            content: 'Reply one',
            position: 0,
          }),
        ],
        related_items: [
          expect.objectContaining({
            platform: 'reddit',
            content_type: 'post',
            description: 'Related copy',
          }),
        ],
      }),
    );
    expect(wrapper.get('[data-testid="report-confirmation"]').text()).toContain('#123');
    expect(wrapper.get('[data-testid="report-confirmation"]').text()).toContain('Open');
  });

  it('shows confirmation after a successful report submission', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    membersMock.mockResolvedValue([]);
    await store.loadContext();

    reportIncidentMock.mockResolvedValue({
      incident: sampleIncident(),
      message: "Your report has been received by your MSA's Community Shield team.",
    });

    const wrapper = await mountMemberPage(pinia);
    await wrapper.get('[data-testid="report-concern-cta"]').trigger('click');
    await wrapper.get('input[value="x"]').setValue(true);
    await wrapper.get('input[value="post"]').setValue(true);
    await wrapper.get('input[value="public"]').setValue(true);
    await wrapper.get('[data-testid="description"]').setValue('Concern about a public post.');
    await wrapper.get('[data-testid="submit-report"]').trigger('click');
    await flushPromises();

    expect(reportIncidentMock).toHaveBeenCalledWith(
      1,
      expect.objectContaining({
        platform: 'x',
        content_type: 'post',
        visibility: 'public',
        description: 'Concern about a public post.',
      }),
    );
    expect(wrapper.get('[data-testid="report-confirmation"]').text()).toContain('#123');
  });

  it('shows the admin review queue only when the current organization grants manage permission', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(beta.id);
    contextMock.mockResolvedValue(
      contextFor(beta, 'admin', [
        'organization.view',
        'organization.manage',
        'incidents.manage',
      ]),
    );
    membersMock.mockResolvedValue([]);
    overviewMock.mockResolvedValue({
      can_report: true,
      can_review: true,
      counts: { open: 1, reviewing: 1, resolved: 0 },
    });
    incidentsMock.mockResolvedValue([
      sampleIncident({
        id: 10,
        organization_id: 2,
        platform: 'tiktok',
        content_type: 'video',
        visibility: 'public',
        status: 'reviewing',
      }),
    ]);
    await store.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/admin/community-shield', name: 'admin-incidents', component: AdminIncidentsPage },
        {
          path: '/admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: { template: '<div />' },
        },
      ],
    });
    await router.push('/admin/community-shield');
    await router.isReady();

    const wrapper = mount(AdminIncidentsPage, {
      global: {
        plugins: [pinia, router],
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="report-queue"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('TikTok');
    expect(wrapper.text()).toContain('Video');
    expect(wrapper.text()).toContain('Public');

    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    await store.switchOrganization(alpha.id);
    await flushPromises();

    expect(wrapper.find('[data-testid="admin-denied"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="report-queue"]').exists()).toBe(false);
  });

  it('admin detail displays structured context and supports classification', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(beta.id);
    contextMock.mockResolvedValue(
      contextFor(beta, 'admin', [
        'organization.view',
        'organization.manage',
        'incidents.manage',
      ]),
    );
    membersMock.mockResolvedValue([]);
    incidentMock.mockResolvedValue(
      sampleIncident({
        id: 55,
        organization_id: 2,
        platform: 'discord',
        content_type: 'message',
        visibility: 'group',
        status: 'open',
        language: 'ar',
        original_item_content: 'Arabic demo content',
        surrounding_context: 'Server exchange context',
        reporter_notes: 'Needs translation help',
        replies: [{ id: 1, author: 'mod', content: 'Please stop', posted_at: null, position: 0 }],
        related_items: [
          {
            id: 2,
            platform: 'telegram',
            content_type: 'message',
            reference_url: null,
            description: 'Similar phrasing',
            observed_at: null,
          },
        ],
      }),
    );
    updateIncidentMock.mockResolvedValue(
      sampleIncident({
        id: 55,
        organization_id: 2,
        safety_classification: 'hate',
        classified_by: { id: 4, name: 'Multi Org User', email: 'multi.user@example.com' },
        classified_at: '2026-08-22T18:00:00+00:00',
      }),
    );
    await store.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/admin/community-shield', name: 'admin-incidents', component: { template: '<div />' } },
        {
          path: '/admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: AdminIncidentDetailPage,
        },
      ],
    });
    await router.push('/admin/community-shield/55');
    await router.isReady();

    const wrapper = mount(AdminIncidentDetailPage, {
      global: {
        plugins: [pinia, router],
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="admin-incident-detail"]').exists()).toBe(true);
    expect(wrapper.get('[data-testid="original-item-body"]').text()).toContain('Arabic demo content');
    expect(wrapper.get('[data-testid="surrounding-context-block"]').text()).toContain(
      'Server exchange context',
    );
    expect(wrapper.get('[data-testid="replies-block"]').text()).toContain('Please stop');
    expect(wrapper.get('[data-testid="related-items-block"]').text()).toContain('Telegram');
    expect(wrapper.get('[data-testid="reporter-notes-block"]').text()).toContain(
      'Needs translation help',
    );
    expect(wrapper.find('[data-testid="classification-block"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="admin-denied"]').exists()).toBe(false);

    await wrapper.get('input[value="hate"]').setValue(true);
    await wrapper.get('[data-testid="save-classification"]').trigger('click');
    await flushPromises();

    expect(updateIncidentMock).toHaveBeenCalledWith(2, 55, {
      safety_classification: 'hate',
    });
  });

  it('member does not receive admin classification controls on the report page', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    membersMock.mockResolvedValue([]);
    await store.loadContext();

    const wrapper = await mountMemberPage(pinia);
    await wrapper.get('[data-testid="report-concern-cta"]').trigger('click');

    expect(wrapper.find('[data-testid="classification-block"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="save-classification"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="admin-review-link"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="analyze-with-ai"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="ai-analysis-block"]').exists()).toBe(false);
  });

  it('admin can request AI analysis and render structured advisory results', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(beta.id);
    contextMock.mockResolvedValue(
      contextFor(beta, 'admin', [
        'organization.view',
        'organization.manage',
        'incidents.manage',
      ]),
    );
    membersMock.mockResolvedValue([]);
    incidentMock.mockResolvedValue(
      sampleIncident({
        id: 55,
        organization_id: 2,
        status: 'open',
        original_item_content: 'Arabic demo content',
      }),
    );
    aiAnalysesMock.mockResolvedValue([]);

    let resolveAnalysis!: (value: IncidentAiAnalysis) => void;
    requestAiAnalysisMock.mockReturnValue(
      new Promise<IncidentAiAnalysis>((resolve) => {
        resolveAnalysis = resolve;
      }),
    );
    await store.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/admin/community-shield', component: { template: '<div />' } },
        {
          path: '/admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: AdminIncidentDetailPage,
        },
      ],
    });
    await router.push('/admin/community-shield/55');
    await router.isReady();

    const wrapper = mount(AdminIncidentDetailPage, {
      global: {
        plugins: [pinia, router],
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="analyze-with-ai"]').exists()).toBe(true);
    expect(wrapper.get('[data-testid="analyze-with-ai"]').text()).toContain('Analyze with AI');
    expect(wrapper.get('[data-testid="ai-disclaimer"]').text()).toContain('advisory');
    expect(wrapper.get('[data-testid="ai-privacy-note"]').text()).toContain('configured AI provider');

    await wrapper.get('[data-testid="analyze-with-ai"]').trigger('click');
    await flushPromises();
    expect(wrapper.find('[data-testid="ai-loading"]').exists()).toBe(true);

    resolveAnalysis(sampleAiAnalysis());
    await flushPromises();

    expect(requestAiAnalysisMock).toHaveBeenCalledWith(2, 55);
    expect(wrapper.get('[data-testid="ai-signals"]').text()).toContain('Religious Identity Targeting');
    expect(wrapper.get('[data-testid="ai-classification"]').text()).toContain(
      'Potential coded/visual hate',
    );
    expect(wrapper.get('[data-testid="ai-confidence"]').text()).toContain('Moderate');
    expect(wrapper.get('[data-testid="ai-uncertainty"]').text()).toContain('incomplete');
    expect(wrapper.get('[data-testid="ai-alternative"]').text()).toContain('quoting');
    expect(wrapper.get('[data-testid="ai-recommended-action"]').text()).toContain(
      'Human review recommended',
    );
    expect(wrapper.get('[data-testid="analyze-with-ai"]').text()).toContain('Run New Analysis');
  });

  it('failed AI analysis renders a safe error state and rerun keeps prior analyses', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(beta.id);
    contextMock.mockResolvedValue(
      contextFor(beta, 'admin', [
        'organization.view',
        'organization.manage',
        'incidents.manage',
      ]),
    );
    membersMock.mockResolvedValue([]);
    incidentMock.mockResolvedValue(sampleIncident({ id: 55, organization_id: 2 }));
    const first = sampleAiAnalysis({ id: 901 });
    aiAnalysesMock.mockResolvedValue([first]);
    requestAiAnalysisMock.mockResolvedValue(
      sampleAiAnalysis({
        id: 902,
        status: 'failed',
        analysis: null,
        error_message: 'AI analysis unavailable.',
      }),
    );
    await store.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/admin/community-shield', component: { template: '<div />' } },
        {
          path: '/admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: AdminIncidentDetailPage,
        },
      ],
    });
    await router.push('/admin/community-shield/55');
    await router.isReady();

    const wrapper = mount(AdminIncidentDetailPage, {
      global: {
        plugins: [pinia, router],
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="ai-analysis-901"]').exists()).toBe(true);

    await wrapper.get('[data-testid="analyze-with-ai"]').trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="ai-analysis-902"]').exists()).toBe(true);
    expect(wrapper.get('[data-testid="ai-failed-state"]').text()).toContain(
      'AI analysis unavailable',
    );
    expect(wrapper.text()).not.toContain('No harmful content detected');
    expect(wrapper.find('[data-testid="ai-analysis-901"]').exists()).toBe(true);
  });

  it('organization switching isolates AI analyses on admin detail', async () => {
    const store = useOrganizationStore();
    store.persistCurrentOrganization(beta.id);
    contextMock.mockResolvedValue(
      contextFor(beta, 'admin', [
        'organization.view',
        'organization.manage',
        'incidents.manage',
      ]),
    );
    membersMock.mockResolvedValue([]);
    incidentMock.mockResolvedValue(sampleIncident({ id: 55, organization_id: 2 }));
    aiAnalysesMock.mockResolvedValue([sampleAiAnalysis({ id: 901, incident_id: 55 })]);
    await store.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/admin/community-shield', component: { template: '<div />' } },
        {
          path: '/admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: AdminIncidentDetailPage,
        },
      ],
    });
    await router.push('/admin/community-shield/55');
    await router.isReady();

    const wrapper = mount(AdminIncidentDetailPage, {
      global: {
        plugins: [pinia, router],
      },
    });
    await flushPromises();
    expect(wrapper.find('[data-testid="ai-analysis-901"]').exists()).toBe(true);

    contextMock.mockResolvedValue(
      contextFor(alpha, 'member', ['organization.view', 'incidents.view']),
    );
    await store.switchOrganization(alpha.id);
    await flushPromises();

    expect(wrapper.find('[data-testid="admin-denied"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="analyze-with-ai"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="ai-analysis-901"]').exists()).toBe(false);
  });
});

async function mountMemberPage(pinia: ReturnType<typeof createPinia>) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/community-shield', component: CommunityShieldPage },
      { path: '/admin/community-shield', component: { template: '<div />' } },
    ],
  });
  await router.push('/community-shield');
  await router.isReady();

  return mount(CommunityShieldPage, {
    global: {
      plugins: [pinia, router],
    },
  });
}
