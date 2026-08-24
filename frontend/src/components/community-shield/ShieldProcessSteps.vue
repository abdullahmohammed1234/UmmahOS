<template>
  <div class="shield-process" :aria-label="ariaLabel" data-testid="shield-workflow">
    <div v-for="(step, index) in steps" :key="step" class="process-step">
      <div class="step-marker">
        <span class="step-index">{{ index + 1 }}</span>
      </div>
      <span class="step-name">{{ step }}</span>
      <span v-if="index < steps.length - 1" class="step-arrow" aria-hidden="true">→</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  steps: string[];
  ariaLabel?: string;
}>();
</script>

<style scoped>
.shield-process {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.process-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.step-marker {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-index {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--accent-mint);
}

.step-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-on-dark);
}

.step-arrow {
  color: rgba(255, 255, 255, 0.35);
  font-size: var(--text-lg);
  margin-right: var(--space-2);
}

@media (max-width: 640px) {
  .shield-process {
    flex-direction: column;
    align-items: flex-start;
  }

  .step-arrow {
    display: none;
  }
}
</style>
