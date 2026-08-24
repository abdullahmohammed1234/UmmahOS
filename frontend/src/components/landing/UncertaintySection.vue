<template>
  <div class="uncertainty-section">
    <h3>Uncertainty is not failure.</h3>
    <p class="uncertainty-lede">
      When the AI lacks enough context, the system does not force a conclusion. It routes the case
      toward human review.
    </p>
    <div class="confidence-levels">
      <div v-for="level in levels" :key="level.label" class="confidence-card" :class="level.tone">
        <div class="confidence-bar">
          <div class="confidence-fill" :style="{ width: level.width }" />
        </div>
        <span class="confidence-label">{{ level.label }}</span>
        <span class="confidence-desc">{{ level.desc }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const levels = [
  { label: 'High confidence', width: '85%', tone: 'high', desc: 'Clear signals — still advisory' },
  { label: 'Moderate confidence', width: '55%', tone: 'mid', desc: 'Review recommended' },
  { label: 'Uncertain', width: '25%', tone: 'low', desc: 'Routes to human review' },
];
</script>

<style scoped>
.uncertainty-section {
  text-align: center;
  max-width: 640px;
  margin: 0 auto;
}

.uncertainty-section h3 {
  margin-bottom: var(--space-3);
  font-size: var(--text-2xl);
}

.uncertainty-lede {
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-8);
}

.confidence-levels {
  display: grid;
  gap: var(--space-4);
  text-align: left;
}

.confidence-card {
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
}

.confidence-bar {
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--background-alt);
  margin-bottom: var(--space-3);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.confidence-card.high .confidence-fill {
  background: var(--primary);
}

.confidence-card.mid .confidence-fill {
  background: var(--warning);
}

.confidence-card.low .confidence-fill {
  background: var(--accent);
}

.confidence-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-1);
}

.confidence-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
}
</style>
