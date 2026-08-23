<template>
  <section class="panel content">
    <h1>Members</h1>
    <p class="muted">
      Memberships shown here belong to {{ organization.currentOrganization?.name ?? 'the current organization' }} only.
      Roles apply only inside this organization.
    </p>
    <p v-if="!organization.canViewMembers" class="error">
      You do not have permission to view members in this organization.
    </p>
    <template v-else>
      <p v-if="roleError" class="error">{{ roleError }}</p>
      <p v-if="roleMessage" class="muted">{{ roleMessage }}</p>
      <table>
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
            <td>
              <select
                v-if="organization.canManageMembers"
                :value="member.role.slug"
                data-testid="member-role-select"
                @change="onRoleChange(member.id, ($event.target as HTMLSelectElement).value)"
              >
                <option v-for="role in ROLE_OPTIONS" :key="role.slug" :value="role.slug">
                  {{ role.name }}
                </option>
              </select>
              <span v-else>{{ member.role.name }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { organizationApi } from '@/services/organizations';
import { useOrganizationStore } from '@/stores/organization';

const organization = useOrganizationStore();
const roleError = ref<string | null>(null);
const roleMessage = ref<string | null>(null);

const ROLE_OPTIONS = [
  { slug: 'admin', name: 'Admin' },
  { slug: 'member', name: 'Member' },
  { slug: 'community_safety_reviewer', name: 'Community Safety Reviewer' },
];

async function onRoleChange(membershipId: number, role: string): Promise<void> {
  if (!organization.currentOrganization) {
    return;
  }

  roleError.value = null;
  roleMessage.value = null;

  try {
    await organizationApi.updateMembership(organization.currentOrganization.id, membershipId, {
      role,
    });
    await organization.loadContext();
    roleMessage.value = 'Role updated for this organization only.';
  } catch {
    roleError.value = 'Unable to update that membership role.';
  }
}
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

select {
  min-width: 220px;
}
</style>
