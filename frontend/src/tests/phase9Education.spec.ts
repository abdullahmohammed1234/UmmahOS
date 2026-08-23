import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import AppShell from '@/components/AppShell.vue';
import AcademyPage from '@/pages/AcademyPage.vue';
import AdaptPracticePage from '@/pages/AdaptPracticePage.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type { Membership, Organization, OrganizationContext, User } from '@/types';
import {
  ADAPT_UNAVAILABLE_MESSAGE,
  LEARNING_PATTERN_FORM_FIELDS,
  LEARNING_PATTERN_TYPE_OPTIONS,
} from '@/utils/education';

const adaptSessionMock = vi.fn();
const coursesMock = vi.fn();
const contextMock = vi.fn();
const membersMock = vi.fn();

vi.mock('@/services/community', () => ({
  communityApi: {
    adaptSession: (...args: unknown[]) => adaptSessionMock(...args),
    courses: (...args: unknown[]) => coursesMock(...args),
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

const memberPermissions = [
  'organization.view',
  'events.view',
  'courses.view',
  'content.view',
  'incidents.view',
];

const reviewerPermissions = [
  ...memberPermissions,
  'incidents.review',
  'education.patterns.view',
  'education.patterns.create',
];

async function mountShell(
  ctx: OrganizationContext = contextFor(alpha, 'member', memberPermissions),
  memberships: Membership[] = [membership(1, alpha, ctx.role ?? 'member')],
) {
  const pinia = createPinia();
  setActivePinia(pinia);

  const auth = useAuthStore();
  const user: User = {
    id: 1,
    name: 'Multi Org User',
    email: 'multi.user@example.com',
    memberships,
  };
  auth.persist('test-token', user);

  const organizationStore = useOrganizationStore();
  organizationStore.persistCurrentOrganization(alpha.id);
  contextMock.mockResolvedValue(ctx);
  membersMock.mockResolvedValue([]);
  await organizationStore.loadContext();

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        component: AppShell,
        children: [
          { path: '', name: 'dashboard', component: { template: '<div />' } },
          { path: 'academy', name: 'academy', component: AcademyPage },
          {
            path: 'academy/community-safety',
            name: 'academy-community-safety',
            component: { template: '<div />' },
          },
          {
            path: 'academy/progress',
            name: 'academy-progress',
            component: { template: '<div />' },
          },
          {
            path: 'academy/adapt-sessions/:sessionId',
            name: 'academy-adapt-practice',
            component: AdaptPracticePage,
          },
          {
            path: 'admin/education/patterns',
            name: 'admin-learning-patterns',
            component: { template: '<div />' },
          },
          { path: 'community-shield', name: 'community-shield', component: { template: '<div />' } },
          {
            path: 'community-shield/review-queue',
            name: 'community-shield-review-queue',
            component: { template: '<div />' },
          },
          { path: 'login', name: 'login', component: { template: '<div />' } },
        ],
      },
    ],
  });

  await router.push({ name: 'academy' });
  await router.isReady();

  const wrapper = mount(AppShell, {
    global: {
      plugins: [pinia, router],
    },
  });

  await flushPromises();
  return { wrapper, organization: organizationStore, router };
}

describe('Phase 9 education UI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    coursesMock.mockResolvedValue([]);
    adaptSessionMock.mockResolvedValue({
      available: false,
      message: ADAPT_UNAVAILABLE_MESSAGE,
      session: {
        id: 9,
        organization_id: 1,
        user_id: 1,
        academy_lesson_id: 3,
        academy_scenario_id: 1,
        adapt_session_id: null,
        adapt_topic_id: null,
        adapt_subject_id: null,
        status: 'unavailable',
        started_at: null,
        completed_at: null,
      },
    });
  });

  it('shows Academy member nav labels for courses, community safety, and progress', async () => {
    const { wrapper } = await mountShell();

    expect(wrapper.find('[data-testid="nav-academy-courses"]').text()).toBe('Courses');
    expect(wrapper.find('[data-testid="nav-community-safety"]').text()).toBe('Community Safety');
    expect(wrapper.find('[data-testid="nav-academy-progress"]').text()).toBe('My Progress');
    expect(wrapper.find('[data-testid="nav-learning-patterns"]').exists()).toBe(false);
  });

  it('shows Learning Patterns nav for reviewers with education.patterns.view', async () => {
    const { wrapper } = await mountShell(
      contextFor(alpha, 'community_safety_reviewer', reviewerPermissions),
      [membership(1, alpha, 'community_safety_reviewer')],
    );

    expect(wrapper.find('[data-testid="nav-learning-patterns"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="nav-learning-patterns"]').text()).toBe('Learning Patterns');
  });

  it('shows the unavailable adaptive practice message', async () => {
    const pinia = createPinia();
    setActivePinia(pinia);

    const auth = useAuthStore();
    auth.persist('test-token', {
      id: 1,
      name: 'Member',
      email: 'member@example.com',
      memberships: [membership(1, alpha, 'member')],
    });

    const organizationStore = useOrganizationStore();
    organizationStore.persistCurrentOrganization(alpha.id);
    contextMock.mockResolvedValue(contextFor(alpha, 'member', memberPermissions));
    membersMock.mockResolvedValue([]);
    await organizationStore.loadContext();

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/academy/adapt-sessions/:sessionId',
          name: 'academy-adapt-practice',
          component: AdaptPracticePage,
        },
        {
          path: '/academy/community-safety',
          name: 'academy-community-safety',
          component: { template: '<div />' },
        },
        {
          path: '/academy/lessons/:lessonId',
          name: 'academy-lesson-detail',
          component: { template: '<div />' },
        },
      ],
    });

    await router.push({ name: 'academy-adapt-practice', params: { sessionId: '9' } });
    await router.isReady();

    const wrapper = mount(AdaptPracticePage, {
      global: {
        plugins: [pinia, router],
      },
    });

    await flushPromises();

    expect(wrapper.find('[data-testid="adapt-unavailable-message"]').text()).toBe(
      ADAPT_UNAVAILABLE_MESSAGE,
    );
    expect(wrapper.text()).toContain(
      'Adaptive practice is temporarily unavailable. You can continue with the lesson.',
    );
  });

  it('defines learning pattern form fields for create flows', () => {
    expect([...LEARNING_PATTERN_FORM_FIELDS]).toEqual([
      'pattern_type',
      'title',
      'summary',
      'learning_objective',
      'domain',
    ]);
    expect(LEARNING_PATTERN_TYPE_OPTIONS.length).toBeGreaterThan(0);
    expect(LEARNING_PATTERN_TYPE_OPTIONS.map((option) => option.value)).toContain(
      'religious_targeting',
    );
  });
});
