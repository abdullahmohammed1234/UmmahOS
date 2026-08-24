<template>
  <div class="multi-msa-network" data-testid="multi-msa-tree">
    <div class="network-visual" aria-hidden="true">
      <svg class="network-lines" viewBox="0 0 400 300">
        <line
          v-for="(org, i) in organizations"
          :key="'line-' + org"
          :x1="200"
          :y1="150"
          :x2="nodePositions[i]?.x ?? 200"
          :y2="nodePositions[i]?.y ?? 150"
          stroke="rgba(42, 157, 143, 0.35)"
          stroke-width="1.5"
          class="network-line"
          :style="{ '--line-delay': `${0.3 + i * 0.15}s` }"
        />
      </svg>
      <div class="network-center">UmmahOS</div>
      <div
        v-for="(org, i) in organizations"
        :key="org"
        class="network-node"
        :class="{ future: org.includes('Future') }"
        :style="{
          left: `${nodePositions[i]?.x ?? 0}px`,
          top: `${nodePositions[i]?.y ?? 0}px`,
          '--node-delay': `${0.4 + i * 0.15}s`,
        }"
      >
        {{ org }}
      </div>
    </div>
    <p class="network-caption muted">
      One platform. Many communities. Isolated data.
    </p>
    <p class="demo-note muted">Demo organizations — seeded for evaluation.</p>
  </div>
</template>

<script setup lang="ts">
const organizations = ['MSA Alpha', 'MSA Beta', 'MSA Gamma', 'Future MSA'];

const nodePositions = [
  { x: 200, y: 40 },
  { x: 60, y: 220 },
  { x: 200, y: 260 },
  { x: 340, y: 220 },
];
</script>

<style scoped>
.multi-msa-network {
  text-align: center;
}

.network-visual {
  position: relative;
  width: 400px;
  height: 300px;
  margin: 0 auto var(--space-4);
}

.network-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.network-line {
  stroke-dasharray: 200;
  stroke-dashoffset: 200;
  animation: drawLine 1s ease forwards;
  animation-delay: var(--line-delay);
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}

.network-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 88px;
  height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-emerald);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  box-shadow: var(--shadow-glow);
  z-index: 2;
}

.network-node {
  position: absolute;
  transform: translate(-50%, -50%);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
  animation: fadeSlideIn 0.5s ease backwards;
  animation-delay: var(--node-delay);
}

.network-node.future {
  border-style: dashed;
  color: var(--text-muted);
}

.network-caption {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-2);
}

.demo-note {
  font-size: var(--text-xs);
  margin: 0;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

@media (max-width: 480px) {
  .network-visual {
    transform: scale(0.85);
    transform-origin: center;
  }
}

@media (prefers-reduced-motion: reduce) {
  .network-line,
  .network-node {
    animation: none;
    stroke-dashoffset: 0;
  }
}
</style>
