<template>
  <div class="hero-visual" aria-hidden="true">
    <div class="visual-glow" />

    <div class="visual-card central-card float">
      <span class="card-label">INCIDENT</span>
      <div class="card-row">
        <span class="pill">Reddit</span>
        <span class="pill muted-pill">Post</span>
        <span class="pill muted-pill">Public</span>
      </div>
      <div class="card-content">Original item captured with full context…</div>
    </div>

    <div class="flow-column">
      <div
        v-for="(step, i) in flowSteps"
        :key="step.label"
        class="flow-node"
        :style="{ '--delay': `${i * 0.12}s` }"
      >
        <div v-if="i > 0" class="connector" />
        <div class="node-card" :class="step.tone">
          <span class="node-num">{{ String(i + 1).padStart(2, '0') }}</span>
          <span class="node-label">{{ step.label }}</span>
        </div>
      </div>
    </div>

    <div class="ecosystem-ring">
      <svg class="ecosystem-lines" viewBox="0 0 280 280">
        <line
          v-for="node in ecosystemNodes"
          :key="'line-' + node.label"
          x1="140"
          y1="140"
          :x2="node.lineX"
          :y2="node.lineY"
          stroke="rgba(42, 157, 143, 0.3)"
          stroke-width="1.5"
        />
      </svg>
      <div class="ecosystem-center">UmmahOS</div>
      <div
        v-for="(node, i) in ecosystemNodes"
        :key="node.label"
        class="ecosystem-node"
        :class="{ highlight: node.highlight }"
        :style="{
          left: `${node.x}px`,
          top: `${node.y}px`,
          '--node-delay': `${0.4 + i * 0.15}s`,
        }"
      >
        <span>{{ node.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const flowSteps = [
  { label: 'Context', tone: 'context' },
  { label: 'AI Assistance', tone: 'ai' },
  { label: 'Human Review', tone: 'human' },
  { label: 'Evidence', tone: 'evidence' },
  { label: 'Outcome', tone: 'outcome' },
  { label: 'Learning', tone: 'learning' },
  { label: 'ADAPT', tone: 'adapt' },
];

/** Precomputed positions on a 280×280 ring — nodes sit outside the 72px center */
const ecosystemNodes = [
  { label: 'Community Shield', highlight: true, x: 140, y: 18, lineX: 140, lineY: 48 },
  { label: 'Academy', highlight: false, x: 228, y: 198, lineX: 198, lineY: 168 },
  { label: 'Operations', highlight: false, x: 52, y: 198, lineX: 82, lineY: 168 },
];
</script>

<style scoped>
.hero-visual {
  position: relative;
  min-height: 540px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.visual-glow {
  position: absolute;
  inset: 10% 5%;
  background: var(--gradient-glow);
  border-radius: 50%;
  pointer-events: none;
}

.central-card {
  position: absolute;
  top: 4%;
  left: 50%;
  transform: translateX(-50%);
  width: min(280px, 90%);
  padding: var(--space-4);
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 3;
}

.float {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateX(-50%) translateY(0);
  }
  50% {
    transform: translateX(-50%) translateY(-8px);
  }
}

.card-label {
  display: block;
  font-size: 0.65rem;
  font-weight: var(--font-bold);
  letter-spacing: 0.1em;
  color: var(--primary);
  margin-bottom: var(--space-2);
}

.card-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-3);
}

.pill {
  font-size: var(--text-xs);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-full);
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: var(--font-medium);
}

.muted-pill {
  background: var(--background-alt);
  color: var(--text-muted);
}

.card-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

.flow-column {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-45%);
  display: grid;
  gap: var(--space-1);
  z-index: 2;
}

.flow-node {
  position: relative;
  animation: fadeSlideIn 0.6s ease backwards;
  animation-delay: var(--delay);
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateX(12px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.connector {
  position: absolute;
  left: 1.1rem;
  top: -0.55rem;
  width: 2px;
  height: 0.55rem;
  background: var(--border);
}

.node-card {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  min-width: 140px;
}

.node-num {
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: var(--font-bold);
}

.node-card.ai {
  border-color: rgba(37, 99, 168, 0.25);
  background: rgba(37, 99, 168, 0.04);
}

.node-card.human {
  border-color: rgba(20, 92, 62, 0.3);
  background: var(--primary-soft);
}

.node-card.adapt {
  border-color: rgba(42, 157, 143, 0.35);
  background: var(--accent-soft);
}

.ecosystem-ring {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 280px;
  height: 280px;
}

.ecosystem-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.ecosystem-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-emerald);
  color: #fff;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.04em;
  box-shadow: var(--shadow-glow);
  z-index: 2;
}

.ecosystem-node {
  position: absolute;
  transform: translate(-50%, -50%);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 0.65rem;
  font-weight: var(--font-semibold);
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
  z-index: 3;
  animation: fadeSlideIn 0.5s ease backwards;
  animation-delay: var(--node-delay);
}

.ecosystem-node.highlight {
  background: var(--primary-soft);
  border-color: rgba(20, 92, 62, 0.35);
  color: var(--primary);
}

@media (prefers-reduced-motion: reduce) {
  .float,
  .flow-node,
  .ecosystem-node {
    animation: none;
  }
}

@media (max-width: 900px) {
  .hero-visual {
    min-height: 460px;
    transform: scale(0.88);
    transform-origin: center top;
  }

  .flow-column {
    right: -8px;
    transform: translateY(-40%) scale(0.9);
  }

  .ecosystem-ring {
    left: -10px;
    bottom: -10px;
    transform: scale(0.9);
  }
}
</style>
