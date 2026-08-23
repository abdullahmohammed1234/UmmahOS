import type { Membership, Organization, OrganizationContext } from '@/types';
import { api } from '@/services/api';
import { unwrapData } from '@/services/unwrap';

export function organizationPath(organizationId: number | string, suffix = ''): string {
  return `/organizations/${organizationId}${suffix}`;
}

export const organizationApi = {
  async list(): Promise<Organization[]> {
    const { data } = await api.get<Organization[] | { data: Organization[] }>('/organizations');
    return unwrapData(data);
  },

  async show(organizationId: number | string): Promise<Organization> {
    const { data } = await api.get<Organization | { data: Organization }>(
      organizationPath(organizationId),
    );
    return unwrapData(data);
  },

  async context(organizationId: number | string): Promise<OrganizationContext> {
    const { data } = await api.get<OrganizationContext | { data: OrganizationContext }>(
      organizationPath(organizationId, '/context'),
    );
    return unwrapData(data);
  },

  async members(organizationId: number | string): Promise<Membership[]> {
    const { data } = await api.get<Membership[] | { data: Membership[] }>(
      organizationPath(organizationId, '/members'),
    );
    return unwrapData(data);
  },

  async update(
    organizationId: number | string,
    payload: Partial<Pick<Organization, 'name' | 'slug' | 'status'>>,
  ): Promise<Organization> {
    const { data } = await api.patch<Organization | { data: Organization }>(
      organizationPath(organizationId),
      payload,
    );
    return unwrapData(data);
  },
};
