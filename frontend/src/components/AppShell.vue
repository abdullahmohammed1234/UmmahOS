<template>
  <div class="shell">
    <a class="skip-link" href="#app-main">Skip to content</a>
    <!-- Mobile top bar -->
    <header class="mobile-topbar" data-testid="mobile-topbar">
      <button
        class="menu-toggle"
        type="button"
        aria-label="Open navigation menu"
        aria-controls="app-sidebar"
        :aria-expanded="mobileNavOpen"
        data-testid="mobile-nav-toggle"
        @click="mobileNavOpen = true"
      >
        <AppIcon name="menu" />
      </button>
      <RouterLink :to="{ name: 'dashboard' }" class="mobile-brand">
        <BrandMark size="sm" aria-hidden="true" />
        <strong>UmmahOS</strong>
      </RouterLink>
      <span class="mobile-org" data-testid="mobile-current-org">
        {{ organization.currentOrganization?.name ?? '…' }}
        <span v-if="organization.currentRole" class="mobile-role">
          · {{ organization.currentMembership?.role?.name || organization.currentRole }}
        </span>
      </span>
    </header>

    <!-- Sidebar -->
    <aside
      id="app-sidebar"
      class="sidebar"
      :class="{ open: mobileNavOpen }"
      data-testid="app-sidebar"
      aria-label="Main navigation"
    >
      <div class="sidebar-header">
        <RouterLink :to="{ name: 'dashboard' }" class="brand" @click="closeMobileNav">
          <BrandMark aria-hidden="true" />
          <div class="brand-text">
            <strong>UmmahOS</strong>
            <span class="brand-tagline">Community infrastructure</span>
          </div>
        </RouterLink>
        <button
          v-if="mobileNavOpen"
          class="sidebar-close"
          type="button"
          aria-label="Close navigation menu"
          @click="mobileNavOpen = false"
        >
          <AppIcon name="close" />
        </button>
      </div>

      <div class="org-block" data-testid="org-switcher-block">
        <OrganizationSwitcher />
      </div>

      <nav class="sidebar-nav" aria-label="Primary">
        <div class="nav-group">
          <p class="nav-label">Community</p>
          <RouterLink :to="{ name: 'dashboard' }" exact-active-class="active" @click="closeMobileNav">
            <AppIcon name="home" size="sm" />
            <span>Home</span>
          </RouterLink>
          <RouterLink to="/announcements" active-class="active" @click="closeMobileNav">
            <AppIcon name="announcements" size="sm" />
            <span>Announcements</span>
          </RouterLink>
          <RouterLink to="/resources" active-class="active" @click="closeMobileNav">
            <AppIcon name="resources" size="sm" />
            <span>Resources</span>
          </RouterLink>
          <RouterLink to="/events" active-class="active" @click="closeMobileNav">
            <AppIcon name="events" size="sm" />
            <span>Events</span>
          </RouterLink>
        </div>

        <div class="nav-group nav-group-featured">
          <p class="nav-label">Community Shield</p>
          <RouterLink
            to="/community-shield"
            exact-active-class="active"
            data-testid="nav-community-shield"
            @click="closeMobileNav"
          >
            <AppIcon name="shield" size="sm" />
            <span>Community Shield</span>
          </RouterLink>
          <RouterLink
            v-if="!organization.canReviewIncidents"
            to="/community-shield?action=report"
            active-class="active"
            data-testid="nav-report-concern"
            @click="closeMobileNav"
          >
            <AppIcon name="reports" size="sm" />
            <span>Report a Concern</span>
          </RouterLink>
          <RouterLink
            v-if="organization.canReviewIncidents"
            to="/community-shield/review-queue"
            active-class="active"
            data-testid="nav-review-queue"
            @click="closeMobileNav"
          >
            <AppIcon name="queue" size="sm" />
            <span>Review Queue</span>
          </RouterLink>
          <RouterLink
            to="/community-shield/my-reports"
            active-class="active"
            data-testid="nav-my-reports"
            @click="closeMobileNav"
          >
            <AppIcon name="reports" size="sm" />
            <span>My Reports</span>
          </RouterLink>
          <RouterLink
            v-if="organization.canManageIncidents"
            to="/admin/community-shield"
            active-class="active"
            data-testid="nav-admin-reports"
            @click="closeMobileNav"
          >
            <AppIcon name="reports" size="sm" />
            <span>Reports / management</span>
          </RouterLink>
        </div>

        <div class="nav-group">
          <p class="nav-label">Academy</p>
          <RouterLink
            to="/academy"
            exact-active-class="active"
            data-testid="nav-academy-courses"
            @click="closeMobileNav"
          >
            <AppIcon name="courses" size="sm" />
            <span>Courses</span>
          </RouterLink>
          <RouterLink
            to="/academy/community-safety"
            active-class="active"
            data-testid="nav-community-safety"
            @click="closeMobileNav"
          >
            <AppIcon name="shield" size="sm" />
            <span>Community Safety</span>
          </RouterLink>
          <RouterLink
            to="/academy/progress"
            active-class="active"
            data-testid="nav-academy-progress"
            @click="closeMobileNav"
          >
            <AppIcon name="progress" size="sm" />
            <span>My Progress</span>
          </RouterLink>
        </div>

        <div v-if="organization.canViewEducationPatterns" class="nav-group">
          <p class="nav-label">Education</p>
          <RouterLink
            to="/admin/education/patterns"
            active-class="active"
            data-testid="nav-learning-patterns"
            @click="closeMobileNav"
          >
            <AppIcon name="patterns" size="sm" />
            <span>Learning Patterns</span>
          </RouterLink>
        </div>

        <div v-if="organization.isOrganizationAdmin" class="nav-group">
          <p class="nav-label">Organization</p>
          <RouterLink to="/admin" exact-active-class="active" @click="closeMobileNav">
            <AppIcon name="dashboard" size="sm" />
            <span>Dashboard</span>
          </RouterLink>
          <RouterLink to="/members" active-class="active" @click="closeMobileNav">
            <AppIcon name="members" size="sm" />
            <span>Members</span>
          </RouterLink>
          <RouterLink to="/admin/announcements" active-class="active" @click="closeMobileNav">
            <AppIcon name="announcements" size="sm" />
            <span>Announcements</span>
          </RouterLink>
          <RouterLink to="/admin/events" active-class="active" @click="closeMobileNav">
            <AppIcon name="events" size="sm" />
            <span>Events</span>
          </RouterLink>
          <RouterLink to="/admin/resources" active-class="active" @click="closeMobileNav">
            <AppIcon name="resources" size="sm" />
            <span>Resources</span>
          </RouterLink>
          <RouterLink to="/admin/academy" active-class="active" @click="closeMobileNav">
            <AppIcon name="courses" size="sm" />
            <span>Academy</span>
          </RouterLink>
          <RouterLink
            v-if="organization.canManageOrganization"
            to="/settings"
            active-class="active"
            @click="closeMobileNav"
          >
            <AppIcon name="settings" size="sm" />
            <span>Settings</span>
          </RouterLink>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar" aria-hidden="true">{{ userInitials }}</div>
          <div class="user-details">
            <span class="user-name">{{ auth.user?.name }}</span>
            <span class="user-role badge neutral">
              {{ organization.currentMembership?.role?.name || organization.currentRole || 'no role' }}
            </span>
          </div>
        </div>
        <button class="button ghost small logout-btn" type="button" @click="onLogout">
          <AppIcon name="logout" size="sm" />
          Sign out
        </button>
        <p class="ai-tagline muted">AI assists. Humans decide.</p>
      </div>
    </aside>

    <div
      v-if="mobileNavOpen"
      class="sidebar-overlay"
      aria-hidden="true"
      @click="mobileNavOpen = false"
    />

    <main id="app-main" class="main-content" tabindex="-1">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { RouterLink, RouterView, useRouter } from 'vue-router';
import AppIcon from '@/components/icons/AppIcon.vue';
import BrandMark from '@/components/BrandMark.vue';
import OrganizationSwitcher from '@/components/OrganizationSwitcher.vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';

const auth = useAuthStore();
const organization = useOrganizationStore();
const router = useRouter();
const mobileNavOpen = ref(false);

const userInitials = computed(() => {
  const name = auth.user?.name ?? '';
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    const first = parts[0]?.[0] ?? '';
    const last = parts[parts.length - 1]?.[0] ?? '';
    return (first + last).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase() || '?';
});

function closeMobileNav(): void {
  mobileNavOpen.value = false;
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    mobileNavOpen.value = false;
  }
}

async function onLogout(): Promise<void> {
  organization.reset();
  await auth.logout();
  await router.push({ name: 'login' });
}

watch(mobileNavOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
});

onMounted(() => {
  window.addEventListener('keydown', onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown);
  document.body.style.overflow = '';
});
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

.skip-link {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  z-index: 400;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  transform: translateY(-200%);
  transition: transform var(--transition-fast);
}

.skip-link:focus {
  transform: translateY(0);
}

.mobile-topbar {
  display: none;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--surface);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  z-index: 200;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-5) var(--space-4);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
  color: inherit;
}

.brand-text {
  display: grid;
  gap: 0.1rem;
}

.brand-text strong {
  font-size: var(--text-base);
  font-family: var(--font-display);
}

.brand-tagline {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.sidebar-close {
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: var(--space-1);
  color: var(--text-muted);
  display: flex;
}

.org-block {
  margin: 0 var(--space-3) var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--primary-soft) 0%, var(--accent-soft) 100%);
  border: 1px solid rgba(20, 92, 62, 0.15);
}

.sidebar-nav {
  flex: 1;
  padding: 0 var(--space-2) var(--space-3);
  overflow-y: auto;
}

.nav-group {
  margin-bottom: var(--space-2);
}

.nav-group-featured {
  padding: var(--space-2);
  margin: var(--space-2) var(--space-1);
  border-radius: var(--radius-lg);
  background: rgba(20, 92, 62, 0.04);
  border: 1px solid rgba(20, 92, 62, 0.08);
}

.nav-label {
  margin: var(--space-3) var(--space-3) var(--space-1);
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: var(--font-bold);
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar-nav a:hover {
  background: var(--primary-soft);
  color: var(--primary);
}

.sidebar-nav a.active {
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: var(--font-semibold);
  box-shadow: inset 3px 0 0 var(--primary);
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--border-subtle);
  display: grid;
  gap: var(--space-3);
}

.user-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-full);
  background: var(--gradient-emerald);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  flex-shrink: 0;
}

.user-details {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  width: fit-content;
}

.logout-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  justify-content: flex-start;
  padding-left: 0;
}

.ai-tagline {
  font-size: var(--text-xs);
  margin: 0;
  font-style: italic;
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: var(--space-8) var(--space-8) var(--space-16);
  min-width: 0;
  background:
    radial-gradient(circle at top right, rgba(42, 157, 143, 0.04), transparent 40%),
    var(--background);
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .mobile-topbar {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--topbar-height);
    padding: 0 var(--space-4);
    background: var(--surface);
    border-bottom: 1px solid var(--border-subtle);
    z-index: 150;
  }

  .menu-toggle {
    border: 1px solid var(--border);
    background: var(--surface-elevated);
    border-radius: var(--radius-md);
    padding: var(--space-2);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
  }

  .mobile-brand {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    text-decoration: none;
    color: inherit;
  }

  .mobile-org {
    margin-left: auto;
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    color: var(--primary);
    max-width: 8rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    box-shadow: var(--shadow-xl);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-close {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 36, 25, 0.45);
    z-index: 199;
  }

  .main-content {
    margin-left: 0;
    padding-top: calc(var(--topbar-height) + var(--space-6));
    padding-inline: var(--space-4);
  }
}

@media (min-width: 769px) {
  .sidebar-close {
    display: none;
  }
}
</style>
