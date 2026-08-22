<template>
  <label class="switcher">
    <span class="muted">Current organization</span>
    <select
      :value="organization.currentOrganization?.id ?? ''"
      :disabled="organization.availableOrganizations.length < 2 || organization.isLoading"
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
  </label>
</template>

<script setup lang="ts">
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();

async function onChange(event: Event): Promise<void> {
  const value = Number((event.target as HTMLSelectElement).value);
  await organization.switchOrganization(value);
}
</script>

<style scoped>
.switcher {
  display: grid;
  gap: 0.3rem;
  min-width: 220px;
}

.switcher span {
  font-size: 0.8rem;
}

select {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.55rem 0.7rem;
  background: #fff;
}
</style>
