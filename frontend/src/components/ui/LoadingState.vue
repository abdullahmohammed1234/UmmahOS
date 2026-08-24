<template>
  <div class="loading-state" :data-testid="testId" role="status" aria-live="polite">
    <template v-if="skeleton">
      <div v-for="n in lines" :key="n" class="skeleton skeleton-line" :style="{ width: lineWidth(n) }" />
    </template>
    <p v-else class="muted">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string;
    skeleton?: boolean;
    lines?: number;
    testId?: string;
  }>(),
  {
    message: 'Loading…',
    skeleton: false,
    lines: 3,
  },
);

function lineWidth(index: number): string {
  const widths = ['100%', '85%', '70%', '90%'];
  return widths[(index - 1) % widths.length] ?? '80%';
}
</script>

<style scoped>
.loading-state {
  padding: var(--space-4) 0;
}

.skeleton-line {
  height: 1rem;
  margin-bottom: var(--space-3);
}
</style>
