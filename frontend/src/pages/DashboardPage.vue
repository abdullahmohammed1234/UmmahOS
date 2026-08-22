<template>
  <section class="stack">
    <article class="panel content">
      <p class="muted">Current organization</p>
      <h1>{{ organization.currentOrganization?.name ?? 'No organization' }}</h1>
      <p v-if="organization.currentOrganization" class="muted">
        {{ organization.currentOrganization.slug }} · {{ organization.currentOrganization.status }}
      </p>
      <p v-else class="muted">This account is not a member of any MSA yet.</p>
    </article>

    <div class="grid">
      <article class="panel content">
        <h2>Your role here</h2>
        <p>{{ organization.currentRole ?? 'None' }}</p>
        <p class="muted">
          Roles are organization-scoped. Admin in one MSA does not grant admin in another.
        </p>
      </article>
      <article class="panel content">
        <h2>Permissions in this MSA</h2>
        <ul>
          <li v-for="permission in organization.permissions" :key="permission">{{ permission }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();
</script>

<style scoped>
.content,
.grid article {
  padding: 1.25rem 1.4rem;
}

h1,
h2,
p {
  margin-top: 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

ul {
  margin: 0;
  padding-left: 1.1rem;
}

@media (max-width: 720px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
