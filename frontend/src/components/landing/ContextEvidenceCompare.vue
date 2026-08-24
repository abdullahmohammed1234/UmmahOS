<template>
  <div class="context-compare" data-testid="community-shield-before-after">
    <article class="compare-card before">
      <p class="compare-tag">Before</p>
      <h3>Screenshot</h3>
      <div class="screenshot-frame" aria-hidden="true">
        <span class="screenshot-bar" />
        <span class="screenshot-bar short" />
        <span class="screenshot-crop">Cropped. Isolated. Easy to misread.</span>
      </div>
      <p class="muted">A single image without conversation, copies, or timestamps.</p>
    </article>

    <div class="compare-arrow" aria-hidden="true">→</div>

    <article class="compare-card after">
      <p class="compare-tag after-tag">After</p>
      <h3>Structured context</h3>
      <ul class="context-fields">
        <li v-for="field in fields" :key="field">{{ field }}</li>
      </ul>
    </article>
  </div>
</template>

<script setup lang="ts">
const fields = [
  'Incident',
  'Platform',
  'Original item',
  'Context',
  'Replies',
  'Related copies',
  'Language',
  'Notes',
  'Classification',
];
</script>

<style scoped>
.context-compare {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--space-5);
  align-items: stretch;
}

.compare-card {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  background: var(--surface);
}

.compare-card.before {
  background: rgba(155, 44, 44, 0.04);
  border-color: rgba(155, 44, 44, 0.14);
}

.compare-card.after {
  background: var(--primary-soft);
  border-color: rgba(20, 92, 62, 0.2);
}

.compare-tag {
  margin: 0 0 var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--danger);
}

.after-tag {
  color: var(--primary);
}

.compare-card h3 {
  margin: 0 0 var(--space-4);
}

.screenshot-frame {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  min-height: 8rem;
  border-radius: var(--radius-md);
  border: 1px dashed rgba(155, 44, 44, 0.28);
  background: var(--surface-elevated);
  margin-bottom: var(--space-4);
}

.screenshot-bar {
  height: 0.55rem;
  width: 70%;
  border-radius: var(--radius-full);
  background: rgba(155, 44, 44, 0.18);
}

.screenshot-bar.short {
  width: 42%;
}

.screenshot-crop {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.context-fields {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.context-fields li {
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-full);
  background: var(--surface-elevated);
  border: 1px solid rgba(20, 92, 62, 0.18);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--primary);
}

.compare-arrow {
  display: flex;
  align-items: center;
  font-size: var(--text-2xl);
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .context-compare {
    grid-template-columns: 1fr;
  }

  .compare-arrow {
    justify-content: center;
    transform: rotate(90deg);
  }
}
</style>
