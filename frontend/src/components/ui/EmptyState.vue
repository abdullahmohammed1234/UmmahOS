<template>
  <div class="state-panel panel" :data-testid="testId">
    <slot name="icon">
      <div class="state-icon" aria-hidden="true">{{ icon }}</div>
    </slot>
    <h3>{{ title }}</h3>
    <p v-if="description" class="muted">{{ description }}</p>
    <div v-if="$slots.action" class="actions">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    description?: string;
    icon?: string;
    testId?: string;
  }>(),
  { icon: '○' },
);
</script>

<style scoped>
.state-icon {
  font-size: 2rem;
  opacity: 0.5;
}
</style>
