import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import AppShell from '@/components/AppShell.vue';
import OrganizationSwitcher from '@/components/OrganizationSwitcher.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import type { Membership, Organization, OrganizationContext, User } from '@/types';

const contextMock = vi.fn();
const membersMock = vi.fn();

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
    user: { id: 1, name: 'Demo User', email: 'demo@example.com' },
    organization: org,
    role: { id: 1, name: role, slug: role },
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

describe('Application shell', () => {
  const alpha = organization(1, 'Demo MSA Alpha');

  beforeEach(() => {
    window.localStorage.clear();
    contextMock.mockReset();
    membersMock.mockReset();
    membersMock.mockResolvedValue([]);
  });

  function setupStore(org: Organization = alpha): ReturnType<typeof createPinia> {
    const pinia = createPinia();
    setActivePinia(pinia);

    const auth = useAuthStore();
    const user: User = {
      id: 1,
      name: 'Demo User',
      email: 'demo@example.com',
      memberships: [membership(10, org, 'member')],
    };
    auth.persist('test-token', user);

    contextMock.mockResolvedValue(contextFor(org, 'member', ['organization.view', 'incidents.view']));

    const store = useOrganizationStore();
    store.persistCurrentOrganization(org.id);
    return pinia;
  }

  it('shows organization switcher with current organization name', async () => {
    const pinia = setupStore();
    await useOrganizationStore().loadContext();

    const wrapper = mount(OrganizationSwitcher, { global: { plugins: [pinia] } });
    await flushPromises();

    expect(wrapper.find('[data-testid="organization-switcher"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="current-org-name"]').text()).toContain('Demo MSA Alpha');
    expect(wrapper.find('[data-testid="org-switcher-select"]').exists()).toBe(true);
  });

  it('renders sidebar navigation with Community Shield links', async () => {
    const pinia = setupStore();
    await useOrganizationStore().loadContext();

    const wrapper = mount(AppShell, {
      global: {
        plugins: [pinia],
        stubs: { RouterView: true, RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    expect(wrapper.find('[data-testid="app-sidebar"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="org-switcher-block"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Community Shield');
    expect(wrapper.text()).toContain('AI assists. Humans decide.');
  });

  it('shows mobile navigation toggle and current org in top bar', async () => {
    const pinia = setupStore();
    await useOrganizationStore().loadContext();

    const wrapper = mount(AppShell, {
      global: {
        plugins: [pinia],
        stubs: { RouterView: true, RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    expect(wrapper.find('[data-testid="mobile-nav-toggle"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="mobile-current-org"]').text()).toContain('Demo MSA Alpha');
  });
});
