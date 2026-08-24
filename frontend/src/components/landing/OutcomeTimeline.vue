<template>
  <div class="outcome-timeline">
    <p class="timeline-eyebrow">Outcome Tracking</p>
    <h3 class="timeline-headline">Don't stop at "report submitted."</h3>
    <p class="timeline-sub">What happened next?</p>

    <div class="timeline-track">
      <div
        v-for="(step, i) in steps"
        :key="step"
        class="timeline-step"
        :class="{ active: i <= activeIndex }"
        :style="{ '--step-delay': `${i * 0.1}s` }"
      >
        <div class="step-dot">
          <span v-if="i < activeIndex">✓</span>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="step-label">{{ step }}</span>
        <div v-if="i < steps.length - 1" class="step-connector" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

const steps = ['Reported', 'Under Review', 'Decision', 'Outcome', 'Appeal'];
const activeIndex = ref(0);
let interval: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  interval = setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % (steps.length + 1);
    if (activeIndex.value === steps.length) activeIndex.value = 0;
  }, 2000);
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.outcome-timeline {
  text-align: center;
  padding: var(--space-10) 0;
}

.timeline-eyebrow {
  margin: 0 0 var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
}

.timeline-headline {
  margin: 0 0 var(--space-2);
  font-size: var(--text-2xl);
}

.timeline-sub {
  margin: 0 0 var(--space-10);
  color: var(--text-muted);
  font-size: var(--text-lg);
}

.timeline-track {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 0;
  flex-wrap: wrap;
  max-width: 800px;
  margin: 0 auto;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 100px;
  animation: fadeSlideIn 0.5s ease backwards;
  animation-delay: var(--step-delay);
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-dot {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  background: var(--surface);
  border: 2px solid var(--border);
  color: var(--text-muted);
  transition: all var(--transition-base);
  z-index: 1;
}

.timeline-step.active .step-dot {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  box-shadow: 0 0 0 4px var(--primary-soft);
}

.step-label {
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.timeline-step.active .step-label {
  color: var(--primary);
}

.step-connector {
  position: absolute;
  top: 1.25rem;
  left: calc(50% + 1.25rem);
  width: calc(100% - 2.5rem);
  height: 2px;
  background: var(--border);
}

.timeline-step.active .step-connector {
  background: linear-gradient(90deg, var(--primary), var(--border));
}

@media (max-width: 640px) {
  .timeline-track {
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
  }

  .step-connector {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .timeline-step {
    animation: none;
  }
}
</style>
