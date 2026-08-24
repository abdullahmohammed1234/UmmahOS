<template>
  <div class="academy-adapt-flow">
    <div class="flow-steps">
      <div v-for="(step, i) in steps" :key="step.label" class="flow-step" :style="{ '--i': i }">
        <div class="step-card" :class="step.tone">
          <span class="step-icon" aria-hidden="true">{{ step.icon }}</span>
          <span class="step-name">{{ step.label }}</span>
        </div>
        <div v-if="i < steps.length - 1" class="flow-arrow" aria-hidden="true">↓</div>
      </div>
    </div>
    <p class="flow-caption">
      UmmahOS closes the loop between community experience and education.
    </p>
  </div>
</template>

<script setup lang="ts">
const steps = [
  { label: 'Confirmed Pattern', icon: '◆', tone: 'pattern' },
  { label: 'Academy Lesson', icon: '▤', tone: 'lesson' },
  { label: 'Scenario', icon: '◇', tone: 'scenario' },
  { label: 'Learner Response', icon: '◉', tone: 'response' },
  { label: 'ADAPT', icon: '◈', tone: 'adapt' },
  { label: 'Next Challenge', icon: '→', tone: 'next' },
];
</script>

<style scoped>
.academy-adapt-flow {
  padding: var(--space-6) 0;
}

.flow-steps {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: var(--space-2);
}

.flow-step {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  animation: fadeIn 0.4s ease backwards;
  animation-delay: calc(var(--i) * 0.08s);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-card {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  box-shadow: var(--shadow-xs);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.step-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.step-card.pattern {
  border-color: rgba(20, 92, 62, 0.25);
  background: var(--primary-soft);
}

.step-card.adapt,
.step-card.next {
  border-color: rgba(42, 157, 143, 0.3);
  background: var(--accent-soft);
}

.step-icon {
  font-size: var(--text-xs);
  color: var(--primary);
  opacity: 0.7;
}

.flow-arrow {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.flow-caption {
  text-align: center;
  margin-top: var(--space-6);
  color: var(--text-muted);
  font-size: var(--text-base);
}

@media (max-width: 768px) {
  .flow-steps {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .flow-step {
    animation: none;
  }
}
</style>
