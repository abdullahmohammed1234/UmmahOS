<template>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <strong>UmmahOS</strong>
        <span class="muted">Digital infrastructure for MSAs</span>
      </div>
      <OrganizationSwitcher />
      <div class="session">
        <span>{{ auth.user?.name }}</span>
        <span class="badge">{{ organization.currentRole ?? 'no role' }}</span>
        <button class="button secondary" type="button" @click="onLogout">Sign out</button>
      </div>
    </header>

    <div class="layout page">
      <nav class="nav panel">
        <p class="nav-label">Community</p>
        <RouterLink to="/" exact-active-class="active">Home</RouterLink>
        <RouterLink to="/announcements" active-class="active">Announcements</RouterLink>
        <RouterLink to="/resources" active-class="active">Resources</RouterLink>
        <RouterLink to="/events" active-class="active">Events</RouterLink>
        <RouterLink to="/academy" active-class="active">Academy</RouterLink>
        <RouterLink to="/community-shield" active-class="active">Community Shield</RouterLink>

        <template v-if="organization.isOrganizationAdmin">
          <p class="nav-label">Organization</p>
          <RouterLink to="/admin" exact-active-class="active">Dashboard</RouterLink>
          <RouterLink to="/members" active-class="active">Members</RouterLink>
          <RouterLink to="/admin/announcements" active-class="active">Announcements</RouterLink>
          <RouterLink to="/admin/events" active-class="active">Events</RouterLink>
          <RouterLink to="/admin/resources" active-class="active">Resources</RouterLink>
          <RouterLink to="/admin/academy" active-class="active">Academy</RouterLink>
          <RouterLink to="/admin/community-shield" active-class="active">Community Shield</RouterLink>
          <RouterLink
            v-if="organization.canManageOrganization"
            to="/settings"
            active-class="active"
          >
            Settings
          </RouterLink>
        </template>
      </nav>
      <main>
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router';
import OrganizationSwitcher from '@/components/OrganizationSwitcher.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';

const auth = useAuthStore();
const organization = useOrganizationStore();
const router = useRouter();

async function onLogout(): Promise<void> {
  organization.reset();
  await auth.logout();
  await router.push({ name: 'login' });
}
</script>

<style scoped>
.shell {
  min-height: 100vh;
}

.topbar {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 253, 248, 0.86);
}

.brand {
  display: grid;
}

.brand strong {
  font-size: 1.35rem;
}

.session {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.layout {
  display: grid;
  grid-template-columns: 210px 1fr;
  gap: 1.25rem;
  padding: 1.5rem 0 3rem;
}

.nav {
  display: grid;
  align-content: start;
  padding: 0.75rem;
}

.nav-label {
  margin: 0.85rem 0.8rem 0.2rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.nav-label:first-child {
  margin-top: 0.2rem;
}

.nav a {
  text-decoration: none;
  padding: 0.7rem 0.8rem;
  border-radius: 12px;
}

.nav a.active {
  background: rgba(31, 107, 74, 0.12);
}

@media (max-width: 720px) {
  .topbar,
  .layout {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
