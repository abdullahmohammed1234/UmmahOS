<template>
  <div class="switcher" data-testid="organization-switcher">
    <div class="switcher-header">
      <AppIcon name="org" size="sm" />
      <span class="label-text">Organization</span>
    </div>
    <label class="switcher-label">
      <select
        class="switcher-select"
        :value="organization.currentOrganization?.id ?? ''"
        :disabled="organization.availableOrganizations.length < 2 || organization.isLoading"
        :aria-label="'Switch organization, currently ' + (organization.currentOrganization?.name ?? 'none')"
        data-testid="org-switcher-select"
        @change="onChange"
      >
        <option
          v-for="item in organization.availableOrganizations"
          :key="item.id"
          :value="item.id"
        >
          {{ item.name }}
        </option>
      </select>
      <AppIcon name="chevron" size="sm" class="select-chevron" />
    </label>
    <p v-if="organization.currentOrganization" class="org-hint" data-testid="current-org-name">
      <span class="role-badge">{{ organization.currentRole ?? 'member' }}</span>
      in <strong>{{ organization.currentOrganization.name }}</strong>
    </p>
    <ul v-if="memberships.length > 1" class="org-roles" data-testid="org-role-list">
      <li v-for="membership in memberships" :key="membership.id">
        {{ membership.organization.name }}:
        {{ membership.role.slug.replace(/_/g, ' ') }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import AppIcon from '@/components/icons/AppIcon.vue';
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();
const memberships = computed(() => useAuthStore().memberships);

async function onChange(event: Event): Promise<void> {
  const value = Number((event.target as HTMLSelectElement).value);
  await organization.switchOrganization(value);
}
</script>

<style scoped>
.switcher {
  display: grid;
  gap: var(--space-2);
}

.switcher-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--primary);
}

.label-text {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.switcher-label {
  position: relative;
  display: block;
}

.switcher-select {
  appearance: none;
  border: 1px solid rgba(20, 92, 62, 0.2);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-8) var(--space-3) var(--space-3);
  background: var(--surface-elevated);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  color: var(--text-primary);
  width: 100%;
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.switcher-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: var(--focus-ring);
}

.switcher-select:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.select-chevron {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%) rotate(90deg);
  pointer-events: none;
  color: var(--text-muted);
}

.org-hint {
  font-size: var(--text-xs);
  margin: 0;
  line-height: var(--leading-normal);
  color: var(--text-muted);
}

.org-hint strong {
  color: var(--primary);
  font-weight: var(--font-semibold);
}

.org-roles {
  margin: 0;
  padding-left: var(--space-4);
  font-size: var(--text-xs);
  color: var(--text-muted);
  display: grid;
  gap: 0.2rem;
}

.org-roles strong {
  color: var(--text-primary);
  text-transform: capitalize;
}

.role-badge {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius-full);
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: var(--font-semibold);
  font-size: 0.65rem;
  text-transform: capitalize;
}
</style>
