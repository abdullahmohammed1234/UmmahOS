import { ref, watch } from 'vue';
import { useOrganizationStore } from '@/stores/organization';

export function useOrganizationQuery(loader: (organizationId: number) => Promise<void>) {
  const organization = useOrganizationStore();
  const isLoading = ref(false);
  const error = ref('');

  watch(
    () => organization.currentOrganization?.id,
    async (organizationId) => {
      if (!organizationId) {
        return;
      }

      isLoading.value = true;
      error.value = '';

      try {
        await loader(organizationId);
      } catch {
        error.value = 'Unable to load this page for the current organization.';
      } finally {
        isLoading.value = false;
      }
    },
    { immediate: true },
  );

  return { organization, isLoading, error };
}
