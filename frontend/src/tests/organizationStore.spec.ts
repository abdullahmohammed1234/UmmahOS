import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
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

describe('organization store', () => {
  const alpha = organization(1, 'Demo MSA Alpha');
  const beta = organization(2, 'Demo MSA Beta');

  beforeEach(() => {
    window.localStorage.clear();
    setActivePinia(createPinia());
    contextMock.mockReset();
    membersMock.mockReset();

    const auth = useAuthStore();
    const user: User = {
      id: 4,
      name: 'Multi Org User',
      email: 'multi.user@example.com',
      memberships: [
        membership(10, alpha, 'member'),
        membership(11, beta, 'admin'),
      ],
    };
    auth.persist('test-token', user);
  });

  it('switches the current organization and reloads organization-scoped context', async () => {
    contextMock
      .mockResolvedValueOnce(contextFor(alpha, 'member', ['organization.view', 'members.view']))
      .mockResolvedValueOnce(contextFor(beta, 'admin', ['organization.view', 'organization.manage', 'members.manage']));
    membersMock.mockResolvedValue([]);

    const store = useOrganizationStore();
    store.persistCurrentOrganization(alpha.id);
    await store.loadContext();

    expect(store.currentOrganization?.name).toBe('Demo MSA Alpha');
    expect(store.currentRole).toBe('member');
    expect(store.canManageOrganization).toBe(false);

    await store.switchOrganization(beta.id);

    expect(store.currentOrganization?.name).toBe('Demo MSA Beta');
    expect(store.currentRole).toBe('admin');
    expect(store.canManageOrganization).toBe(true);
    expect(contextMock).toHaveBeenNthCalledWith(1, 1);
    expect(contextMock).toHaveBeenNthCalledWith(2, 2);
    expect(window.localStorage.getItem('ummahos.current_organization_id')).toBe('2');
  });

  it('rejects switching to an organization the user does not belong to', async () => {
    const store = useOrganizationStore();

    await expect(store.switchOrganization(99)).rejects.toThrow(
      'You are not a member of that organization.',
    );
  });
});
