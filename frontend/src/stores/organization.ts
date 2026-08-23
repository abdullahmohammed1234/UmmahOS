import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { organizationApi } from '@/services/organizations';
import type { Membership, Organization, OrganizationContext } from '@/types';
import { useAuthStore } from '@/stores/auth';

const CURRENT_ORG_KEY = 'ummahos.current_organization_id';

export const useOrganizationStore = defineStore('organization', () => {
  const currentOrganizationId = ref<number | null>(readStoredOrganizationId());
  const context = ref<OrganizationContext | null>(null);
  const members = ref<Membership[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const memberships = computed(() => useAuthStore().memberships);

  const availableOrganizations = computed(() =>
    memberships.value.map((membership) => membership.organization),
  );

  const currentOrganization = computed<Organization | null>(() => {
    if (context.value) {
      return context.value.organization;
    }

    return (
      availableOrganizations.value.find((organization) => organization.id === currentOrganizationId.value)
      ?? availableOrganizations.value[0]
      ?? null
    );
  });

  const currentRole = computed(() => context.value?.role ?? currentMembership.value?.role.slug ?? null);

  const currentMembership = computed(
    () => memberships.value.find((membership) => membership.organization.id === currentOrganization.value?.id) ?? null,
  );

  const permissions = computed(() => context.value?.permissions ?? []);

  const canManageOrganization = computed(() => permissions.value.includes('organization.manage'));
  const canViewMembers = computed(() => permissions.value.includes('members.view'));
  const canManageMembers = computed(() => permissions.value.includes('members.manage'));
  const canManageContent = computed(() => permissions.value.includes('content.manage'));
  const canManageEvents = computed(() => permissions.value.includes('events.manage'));
  const canManageCourses = computed(() => permissions.value.includes('courses.manage'));
  const canManageIncidents = computed(() => permissions.value.includes('incidents.manage'));
  const isOrganizationAdmin = computed(() => canManageOrganization.value);

  function readStoredOrganizationId(): number | null {
    const raw = window.localStorage.getItem(CURRENT_ORG_KEY);
    return raw ? Number(raw) : null;
  }

  function persistCurrentOrganization(organizationId: number | null): void {
    currentOrganizationId.value = organizationId;

    if (organizationId) {
      window.localStorage.setItem(CURRENT_ORG_KEY, String(organizationId));
    } else {
      window.localStorage.removeItem(CURRENT_ORG_KEY);
    }
  }

  function ensureCurrentOrganization(): number | null {
    if (
      currentOrganizationId.value
      && availableOrganizations.value.some((organization) => organization.id === currentOrganizationId.value)
    ) {
      return currentOrganizationId.value;
    }

    const first = availableOrganizations.value[0]?.id ?? null;
    persistCurrentOrganization(first);

    return first;
  }

  async function switchOrganization(organizationId: number): Promise<void> {
    const allowed = availableOrganizations.value.some((organization) => organization.id === organizationId);

    if (!allowed) {
      throw new Error('You are not a member of that organization.');
    }

    persistCurrentOrganization(organizationId);
    await loadContext();
  }

  async function loadContext(): Promise<void> {
    const organizationId = ensureCurrentOrganization();

    if (!organizationId) {
      context.value = null;
      members.value = [];
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      context.value = await organizationApi.context(organizationId);

      if (context.value.permissions.includes('members.view')) {
        members.value = await organizationApi.members(organizationId);
      } else {
        members.value = [];
      }
    } catch (err) {
      error.value = 'Unable to load the current organization.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateCurrentOrganization(payload: Partial<Pick<Organization, 'name' | 'slug' | 'status'>>): Promise<void> {
    if (!currentOrganization.value) {
      throw new Error('No current organization.');
    }

    await organizationApi.update(currentOrganization.value.id, payload);
    await loadContext();
  }

  function reset(): void {
    persistCurrentOrganization(null);
    context.value = null;
    members.value = [];
    error.value = null;
  }

  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission);
  }

  return {
    currentOrganizationId,
    currentOrganization,
    currentRole,
    currentMembership,
    context,
    members,
    permissions,
    availableOrganizations,
    canManageOrganization,
    canViewMembers,
    canManageMembers,
    canManageContent,
    canManageEvents,
    canManageCourses,
    canManageIncidents,
    isOrganizationAdmin,
    isLoading,
    error,
    switchOrganization,
    loadContext,
    updateCurrentOrganization,
    reset,
    hasPermission,
    persistCurrentOrganization,
  };
});
