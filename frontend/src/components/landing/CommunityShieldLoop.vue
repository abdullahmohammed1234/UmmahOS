<template>
  <div class="shield-loop" data-testid="community-shield-loop">
    <ol class="shield-loop-track">
      <li v-for="(step, index) in steps" :key="step.label" class="shield-loop-step" :class="step.tone">
        <span class="step-index">{{ String(index + 1).padStart(2, '0') }}</span>
        <strong>{{ step.label }}</strong>
        <span v-if="index < steps.length - 1" class="step-arrow" aria-hidden="true">↓</span>
      </li>
    </ol>
    <p class="shield-loop-caption muted">
      Community Shield — from report to outcome. AI assists. Humans decide.
    </p>
  </div>
</template>

<script setup lang="ts">
const steps = [
  { label: 'Report', tone: '' },
  { label: 'Context', tone: '' },
  { label: 'AI Analysis', tone: 'ai' },
  { label: 'Human Review', tone: 'human' },
  { label: 'Evidence', tone: '' },
  { label: 'Outcome', tone: '' },
];
</script>

<style scoped>
.shield-loop {
  max-width: 28rem;
  margin: var(--space-8) auto 0;
}

.shield-loop-track {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.shield-loop-step {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: var(--text-base);
}

.shield-loop-step.ai {
  border-left: 4px solid var(--info);
  background: rgba(37, 99, 168, 0.04);
}

.shield-loop-step.human {
  border-left: 4px solid var(--primary);
  background: var(--primary-soft);
}

.step-index {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  color: var(--primary);
  min-width: 1.75rem;
}

.step-arrow {
  position: absolute;
  left: 1.35rem;
  bottom: -0.85rem;
  color: var(--text-muted);
  font-size: var(--text-sm);
  z-index: 1;
}

.shield-loop-caption {
  margin-top: var(--space-5);
  text-align: center;
  font-size: var(--text-sm);
}

@media (min-width: 768px) {
  .shield-loop {
    max-width: none;
  }

  .shield-loop-track {
    grid-template-columns: repeat(6, 1fr);
    gap: var(--space-3);
  }

  .shield-loop-step {
    flex-direction: column;
    text-align: center;
    min-height: 5.5rem;
    padding: var(--space-4) var(--space-3);
  }

  .step-arrow {
    left: 50%;
    bottom: -0.75rem;
    transform: translateX(-50%);
  }
}
</style>
