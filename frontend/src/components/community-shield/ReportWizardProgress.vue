<template>
  <nav class="wizard-progress" aria-label="Report progress">
    <ol class="progress-list">
      <li
        v-for="(step, index) in steps"
        :key="step.id"
        class="progress-item"
        :class="{
          active: index === currentStep,
          complete: index < currentStep,
        }"
      >
        <button
          type="button"
          class="progress-btn"
          :aria-current="index === currentStep ? 'step' : undefined"
          :disabled="index > currentStep && !allowJumpAhead"
          @click="emit('go-to', index)"
        >
          <span class="step-marker" aria-hidden="true">
            <span v-if="index < currentStep" class="step-check">✓</span>
            <span v-else class="step-num">{{ step.number }}</span>
          </span>
          <span class="step-text">
            <span class="step-label">{{ step.label }}</span>
          </span>
        </button>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
export interface WizardStep {
  id: string;
  label: string;
  number: string;
}

defineProps<{
  steps: WizardStep[];
  currentStep: number;
  allowJumpAhead?: boolean;
}>();

const emit = defineEmits<{
  'go-to': [index: number];
}>();
</script>

<style scoped>
.wizard-progress {
  margin-bottom: var(--space-4);
}

.progress-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.progress-item {
  position: relative;
  padding-left: 0;
}

/* Vertical connector between steps */
.progress-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 1.125rem;
  top: 2.75rem;
  bottom: -0.25rem;
  width: 2px;
  background: var(--border);
  transform: translateX(-50%);
}

.progress-item.complete:not(:last-child)::after {
  background: var(--primary);
}

.progress-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: var(--space-2) var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
  text-align: left;
}

.progress-btn:disabled {
  cursor: default;
}

.progress-btn:not(:disabled):hover {
  background: var(--primary-soft);
}

.step-marker {
  flex-shrink: 0;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border);
  background: var(--surface-elevated);
  transition: border-color var(--transition-fast), background var(--transition-fast),
    color var(--transition-fast);
}

.step-num {
  font-size: 0.65rem;
  font-weight: var(--font-bold);
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.step-check {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  color: #fff;
  line-height: 1;
}

.progress-item.active .step-marker {
  border-color: var(--primary);
  background: var(--primary-soft);
  box-shadow: 0 0 0 3px rgba(20, 92, 62, 0.12);
}

.progress-item.active .step-num {
  color: var(--primary);
}

.progress-item.complete .step-marker {
  border-color: var(--primary);
  background: var(--primary);
}

.step-text {
  flex: 1;
  min-width: 0;
  padding-top: 0.1rem;
}

.step-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  line-height: var(--leading-snug);
}

.progress-item.active .step-label {
  color: var(--primary);
}

.progress-item.complete .step-label {
  color: var(--text-secondary);
}

.progress-item.active .progress-btn {
  background: var(--primary-soft);
}
</style>
