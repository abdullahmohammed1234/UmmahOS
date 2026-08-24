<template>
  <div class="ummahos-loop" data-testid="product-story-workflow">
    <ol class="loop-track">
      <li v-for="(step, index) in steps" :key="step.label" class="loop-step" :class="step.tone">
        <span class="loop-index">{{ String(index + 1).padStart(2, '0') }}</span>
        <strong>{{ step.label }}</strong>
        <span class="loop-hint">{{ step.hint }}</span>
        <span v-if="index < steps.length - 1" class="loop-arrow" aria-hidden="true">↓</span>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
const steps = [
  { label: 'Concern', hint: 'A member notices something concerning', tone: 'start' },
  { label: 'Context', hint: 'Original item, replies, and related copies', tone: '' },
  { label: 'AI Assistance', hint: 'Advisory signals, not a verdict', tone: 'ai' },
  { label: 'Human Review', hint: 'A trained reviewer decides', tone: 'human' },
  { label: 'Evidence', hint: 'A structured package, ready to export', tone: '' },
  { label: 'Outcome', hint: 'What happened next is tracked', tone: '' },
  { label: 'Learning', hint: 'Confirmed patterns become lessons', tone: '' },
  { label: 'ADAPT', hint: 'Practice adapts to the learner', tone: 'adapt' },
];
</script>

<style scoped>
.ummahos-loop {
  max-width: 36rem;
  margin: 0 auto;
}

.loop-track {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.loop-step {
  position: relative;
  display: grid;
  grid-template-columns: 3rem 1fr;
  column-gap: var(--space-4);
  row-gap: 0.15rem;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}

.loop-step.ai {
  border-left: 4px solid var(--info);
  background: rgba(37, 99, 168, 0.04);
}

.loop-step.human {
  border-left: 4px solid var(--primary);
  background: var(--primary-soft);
}

.loop-step.adapt {
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
}

.loop-index {
  grid-row: 1 / span 2;
  align-self: center;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  color: var(--primary);
}

.loop-step strong {
  font-size: var(--text-base);
}

.loop-hint {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.loop-arrow {
  position: absolute;
  left: 1.15rem;
  bottom: -1.05rem;
  z-index: 1;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

@media (min-width: 900px) {
  .ummahos-loop {
    max-width: none;
  }

  .loop-track {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-3);
  }

  .loop-step {
    flex: 1 1 140px;
    max-width: 160px;
    grid-template-columns: 1fr;
    text-align: center;
    min-height: 9.5rem;
  }

  .loop-index {
    grid-row: auto;
  }

  .loop-arrow {
    left: auto;
    right: -0.85rem;
    top: 50%;
    bottom: auto;
    transform: translateY(-50%) rotate(-90deg);
  }
}
</style>
