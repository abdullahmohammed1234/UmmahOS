<template>
  <div class="workflow" :aria-label="ariaLabel">
    <template v-for="(step, index) in steps" :key="step">
      <span class="workflow-step">{{ step }}</span>
      <span v-if="index < steps.length - 1" class="workflow-arrow" aria-hidden="true">↓</span>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  steps: string[];
  ariaLabel?: string;
}>();
</script>

<style scoped>
.workflow {
  flex-direction: column;
  align-items: stretch;
}

.workflow-step {
  text-align: center;
  justify-content: center;
}

.workflow-arrow {
  text-align: center;
  padding: var(--space-1) 0;
}

@media (min-width: 640px) {
  .workflow {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }

  .workflow-arrow {
    padding: 0;
  }
}
</style>
