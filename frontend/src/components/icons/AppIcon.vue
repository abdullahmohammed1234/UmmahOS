<template>
  <svg
    class="app-icon"
    :class="[`icon-${name}`, { 'icon-sm': size === 'sm', 'icon-lg': size === 'lg' }]"
    :width="dimension"
    :height="dimension"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- Home -->
    <template v-if="name === 'home'">
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5" />
    </template>

    <!-- Megaphone -->
    <template v-else-if="name === 'announcements'">
      <path d="M3 11v2a4 4 0 0 0 4 4h1" />
      <path d="M7 7v10" />
      <path d="M11 5.5 19 3v18l-8-2.5V5.5Z" />
    </template>

    <!-- Folder -->
    <template v-else-if="name === 'resources'">
      <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" />
    </template>

    <!-- Calendar -->
    <template v-else-if="name === 'events'">
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M16 3v4M8 3v4M3 10h18" />
    </template>

    <!-- Book -->
    <template v-else-if="name === 'courses'">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
    </template>

    <!-- Shield -->
    <template v-else-if="name === 'shield'">
      <path d="M12 2 4 5v6c0 5 3.5 9.5 8 11 4.5-1.5 8-6 8-11V5l-8-3Z" />
    </template>

    <!-- Chart -->
    <template v-else-if="name === 'progress'">
      <path d="M3 3v18h18" />
      <path d="M7 14l4-4 3 3 5-6" />
    </template>

    <!-- File -->
    <template v-else-if="name === 'reports'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Z" />
      <path d="M14 2v6h6M8 13h8M8 17h5" />
    </template>

    <!-- Inbox -->
    <template v-else-if="name === 'queue'">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.5 5.5a2 2 0 0 1-2.2 0L3 7" />
    </template>

    <!-- Lightbulb -->
    <template v-else-if="name === 'patterns'">
      <path d="M9 18h6M10 22h4" />
      <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2Z" />
    </template>

    <!-- Layout -->
    <template v-else-if="name === 'dashboard'">
      <rect x="3" y="3" width="7" height="9" rx="1" />
      <rect x="14" y="3" width="7" height="5" rx="1" />
      <rect x="14" y="12" width="7" height="9" rx="1" />
      <rect x="3" y="16" width="7" height="5" rx="1" />
    </template>

    <!-- Users -->
    <template v-else-if="name === 'members'">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
    </template>

    <!-- Settings -->
    <template v-else-if="name === 'settings'">
      <circle cx="12" cy="12" r="3" />
      <path
        d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
      />
    </template>

    <!-- Menu -->
    <template v-else-if="name === 'menu'">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </template>

    <!-- Close -->
    <template v-else-if="name === 'close'">
      <path d="M18 6 6 18M6 6l12 12" />
    </template>

    <!-- Logout -->
    <template v-else-if="name === 'logout'">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <path d="M16 17l5-5-5-5M21 12H9" />
    </template>

    <!-- Chevron -->
    <template v-else-if="name === 'chevron'">
      <path d="m9 18 6-6-6-6" />
    </template>

    <!-- Building -->
    <template v-else-if="name === 'org'">
      <rect x="4" y="2" width="16" height="20" rx="2" />
      <path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01" />
    </template>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export type AppIconName =
  | 'home'
  | 'announcements'
  | 'resources'
  | 'events'
  | 'courses'
  | 'shield'
  | 'progress'
  | 'reports'
  | 'queue'
  | 'patterns'
  | 'dashboard'
  | 'members'
  | 'settings'
  | 'menu'
  | 'close'
  | 'logout'
  | 'chevron'
  | 'org';

const props = withDefaults(
  defineProps<{
    name: AppIconName;
    size?: 'sm' | 'md' | 'lg';
  }>(),
  { size: 'md' },
);

const dimension = computed(() => {
  if (props.size === 'sm') return 16;
  if (props.size === 'lg') return 22;
  return 18;
});
</script>

<style scoped>
.app-icon {
  flex-shrink: 0;
  display: block;
}
</style>
