<template>
  <div class="ai-human-comparison">
    <article class="comparison-panel ai-panel">
      <header>
        <span class="panel-tag">Advisory</span>
        <h3>AI Context Analysis</h3>
      </header>
      <ul class="panel-items">
        <li><span class="item-key">Signals</span><span class="item-val">Potential harm patterns detected</span></li>
        <li><span class="item-key">Classification</span><span class="item-val">Harassment — possible</span></li>
        <li><span class="item-key">Confidence</span><span class="item-val confidence-mid">Moderate (62%)</span></li>
        <li><span class="item-key">Uncertainty</span><span class="item-val">Missing reply context</span></li>
      </ul>
      <footer class="panel-footer muted">AI analysis does not determine the final outcome.</footer>
    </article>

    <article class="comparison-panel human-panel">
      <header>
        <span class="panel-tag authoritative">Authoritative</span>
        <h3>Human Review</h3>
      </header>
      <div class="action-grid">
        <button v-for="action in actions" :key="action" type="button" class="action-chip" disabled>
          {{ action }}
        </button>
      </div>
      <ul class="panel-items compact">
        <li><span class="item-key">Reviewer</span><span class="item-val">Trained safety lead</span></li>
        <li><span class="item-key">Decision</span><span class="item-val">Pending review</span></li>
      </ul>
      <footer class="panel-footer">Humans make the final determination.</footer>
    </article>
  </div>
</template>

<script setup lang="ts">
const actions = ['Confirm', 'Uncertain', 'Request Context', 'Escalate', 'Close'];
</script>

<style scoped>
.ai-human-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.comparison-panel {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
}

.ai-panel {
  background: rgba(37, 99, 168, 0.04);
  border-color: rgba(37, 99, 168, 0.18);
  border-left: 4px solid var(--info);
}

.human-panel {
  background: var(--primary-soft);
  border-color: rgba(20, 92, 62, 0.22);
  border-left: 4px solid var(--primary);
}

.comparison-panel header {
  margin-bottom: var(--space-5);
}

.panel-tag {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: var(--font-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--info);
  margin-bottom: var(--space-2);
}

.panel-tag.authoritative {
  color: var(--primary);
}

.comparison-panel h3 {
  margin: 0;
  font-size: var(--text-xl);
}

.panel-items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.panel-items.compact {
  margin-top: var(--space-4);
}

.panel-items li {
  display: grid;
  gap: var(--space-1);
}

.item-key {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.item-val {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.confidence-mid {
  color: var(--warning);
  font-weight: var(--font-medium);
}

.action-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.action-chip {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid rgba(20, 92, 62, 0.25);
  background: var(--surface-elevated);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--primary);
  cursor: default;
}

.panel-footer {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
  font-size: var(--text-sm);
  font-style: italic;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .ai-human-comparison {
    grid-template-columns: 1fr;
  }
}
</style>
