<template>
  <header class="page-header" :data-testid="testId">
    <div v-if="eyebrow" class="eyebrow">{{ eyebrow }}</div>
    <h1>{{ title }}</h1>
    <p v-if="description" class="lede">{{ description }}</p>
    <div v-if="$slots.actions" class="actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
  eyebrow?: string;
  testId?: string;
}>();
</script>

<style scoped>
.page-header {
  margin-bottom: var(--space-2);
}

.page-header h1 {
  margin: 0 0 var(--space-3);
}

.page-header .lede {
  margin-bottom: var(--space-4);
}

.page-header .actions {
  margin-top: var(--space-4);
}
</style>
