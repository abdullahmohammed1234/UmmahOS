<template>
  <div class="problem-comparison">
    <div class="comparison-side today">
      <div class="side-header">
        <span class="side-tag">Today</span>
        <h3>Fragmented tools</h3>
      </div>
      <div class="tools-grid">
        <div v-for="tool in fragmentedTools" :key="tool" class="tool-chip broken">
          {{ tool }}
        </div>
      </div>
      <svg class="broken-lines" viewBox="0 0 200 120" aria-hidden="true">
        <path
          d="M30 60 L70 40 M70 40 L110 70 M110 70 L150 35 M150 35 L170 80"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-dasharray="4 4"
          fill="none"
          opacity="0.4"
        />
        <circle cx="30" cy="60" r="4" fill="currentColor" opacity="0.3" />
        <circle cx="70" cy="40" r="4" fill="currentColor" opacity="0.3" />
        <circle cx="110" cy="70" r="4" fill="currentColor" opacity="0.3" />
        <circle cx="150" cy="35" r="4" fill="currentColor" opacity="0.3" />
        <circle cx="170" cy="80" r="4" fill="currentColor" opacity="0.3" />
      </svg>
      <ul class="pain-list">
        <li>Screenshot only — context lost</li>
        <li>No structured review path</li>
        <li>No outcome tracking</li>
      </ul>
    </div>

    <div class="comparison-divider" aria-hidden="true">
      <span>→</span>
    </div>

    <div class="comparison-side with-ummahos">
      <div class="side-header">
        <span class="side-tag success">With UmmahOS</span>
        <h3>One connected ecosystem</h3>
      </div>
      <div class="connected-hub">
        <svg class="hub-lines" viewBox="0 0 300 260" aria-hidden="true">
          <line
            v-for="cap in capabilities"
            :key="'line-' + cap.label"
            x1="150"
            y1="130"
            :x2="cap.lineX"
            :y2="cap.lineY"
            stroke="rgba(20, 92, 62, 0.25)"
            stroke-width="1.5"
          />
        </svg>
        <div class="hub-center">UmmahOS</div>
        <div
          v-for="(cap, i) in capabilities"
          :key="cap.label"
          class="hub-spoke"
          :style="{ left: `${cap.x}px`, top: `${cap.y}px`, '--i': i }"
        >
          {{ cap.label }}
        </div>
      </div>
      <ul class="gain-list">
        <li>Structured evidence with full context</li>
        <li>Human review with AI assistance</li>
        <li>Outcome tracking through learning</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const fragmentedTools = [
  'Google Forms',
  'Discord',
  'WhatsApp',
  'Spreadsheets',
  'Screenshots',
  'Email',
];

/** Fixed positions on 300×260 canvas — spokes sit clear of the 80px center hub */
const capabilities = [
  { label: 'Safety', x: 150, y: 24, lineX: 150, lineY: 54 },
  { label: 'Academy', x: 258, y: 78, lineX: 222, lineY: 98 },
  { label: 'Events', x: 258, y: 182, lineX: 222, lineY: 162 },
  { label: 'Resources', x: 150, y: 236, lineX: 150, lineY: 206 },
  { label: 'Review', x: 42, y: 182, lineX: 78, lineY: 162 },
  { label: 'Outcomes', x: 42, y: 78, lineX: 78, lineY: 98 },
];
</script>

<style scoped>
.problem-comparison {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--space-6);
  align-items: stretch;
}

.comparison-side {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
}

.today {
  background: rgba(155, 44, 44, 0.03);
  border-color: rgba(155, 44, 44, 0.12);
}

.with-ummahos {
  background: var(--primary-soft);
  border-color: rgba(20, 92, 62, 0.2);
}

.side-header {
  margin-bottom: var(--space-5);
}

.side-tag {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--danger);
  margin-bottom: var(--space-2);
}

.side-tag.success {
  color: var(--primary);
}

.side-header h3 {
  margin: 0;
  font-size: var(--text-xl);
}

.tools-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.tool-chip {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  background: var(--surface);
  border: 1px dashed var(--border);
  color: var(--text-secondary);
}

.tool-chip.broken {
  opacity: 0.85;
}

.broken-lines {
  width: 100%;
  height: 80px;
  color: var(--danger);
  margin-bottom: var(--space-4);
}

.pain-list,
.gain-list {
  margin: 0;
  padding-left: var(--space-5);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.comparison-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  color: var(--text-muted);
  padding: 0 var(--space-2);
}

.connected-hub {
  position: relative;
  width: 300px;
  height: 260px;
  margin: 0 auto var(--space-4);
}

.hub-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.hub-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-emerald);
  color: #fff;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  box-shadow: var(--shadow-glow);
  z-index: 2;
}

.hub-spoke {
  position: absolute;
  transform: translate(-50%, -50%);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--surface-elevated);
  border: 1px solid rgba(20, 92, 62, 0.25);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--primary);
  white-space: nowrap;
  z-index: 3;
  animation: fadeIn 0.4s ease backwards;
  animation-delay: calc(var(--i) * 0.08s);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.92);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

@media (max-width: 768px) {
  .problem-comparison {
    grid-template-columns: 1fr;
  }

  .comparison-divider {
    transform: rotate(90deg);
    padding: var(--space-2) 0;
  }

  .connected-hub {
    transform: scale(0.9);
    transform-origin: center;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hub-spoke {
    animation: none;
  }
}
</style>
