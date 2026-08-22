<template>
  <section class="panel content">
    <h1>Members</h1>
    <p class="muted">
      Memberships shown here belong to {{ organization.currentOrganization?.name ?? 'the current organization' }} only.
    </p>
    <p v-if="!organization.canViewMembers" class="error">
      You do not have permission to view members in this organization.
    </p>
    <table v-else>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="member in organization.members" :key="member.id">
          <td>{{ member.user.name }}</td>
          <td>{{ member.user.email }}</td>
          <td>{{ member.role.name }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();
</script>

<style scoped>
.content {
  padding: 1.25rem 1.4rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  text-align: left;
  padding: 0.7rem 0.4rem;
  border-bottom: 1px solid var(--line);
}
</style>
