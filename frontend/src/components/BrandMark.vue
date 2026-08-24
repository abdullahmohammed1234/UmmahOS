<template>
  <img
    class="brand-logo"
    :class="sizeClass"
    src="/logo.png"
    alt=""
    width="36"
    height="36"
    decoding="async"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg';
  }>(),
  { size: 'md' },
);

const sizeClass = computed(() => `size-${props.size}`);
</script>

<style scoped>
.brand-logo {
  display: block;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  background: #0a0a0a;
}

.size-sm {
  width: 1.75rem;
  height: 1.75rem;
}

.size-md {
  width: 2.25rem;
  height: 2.25rem;
}

.size-lg {
  width: 2.75rem;
  height: 2.75rem;
}
</style>
