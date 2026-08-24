<template>
  <section class="shield-showcase" id="community-shield">
    <div class="showcase-inner landing-wide">
      <div class="showcase-copy">
        <p class="eyebrow">Community Shield</p>
        <h2>Context changes everything.</h2>
        <p class="lede">
          Preserve context. Protect people. Respond responsibly. Community Shield helps members
          document concerning online content while preserving the full story for trained reviewers.
        </p>
      </div>

      <div class="incident-demo">
        <div
          v-for="(block, i) in contextBlocks"
          :key="block.label"
          class="context-block"
          :class="{ active: activeBlock === i }"
          @mouseenter="activeBlock = i"
        >
          <span class="block-label">{{ block.label }}</span>
          <p class="block-preview">{{ block.preview }}</p>
        </div>
      </div>

      <p class="showcase-message">
        A screenshot alone loses the story. <strong>UmmahOS preserves the story.</strong>
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

const contextBlocks = [
  { label: 'Original Item', preview: 'The reported post with timestamp and permalink.' },
  { label: 'Context', preview: 'Surrounding thread and conversation flow.' },
  { label: 'Replies', preview: 'Responses that clarify intent or escalate harm.' },
  { label: 'Related Copies', preview: 'Cross-posts and reposts across platforms.' },
  { label: 'Language', preview: 'Translation notes and cultural context markers.' },
  { label: 'AI Analysis', preview: 'Advisory signals — classification and confidence.' },
  { label: 'Human Review', preview: 'Authoritative decision by trained reviewers.' },
];

const activeBlock = ref(0);
let interval: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  interval = setInterval(() => {
    activeBlock.value = (activeBlock.value + 1) % contextBlocks.length;
  }, 2800);
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.shield-showcase {
  background: var(--gradient-dark);
  color: var(--text-on-dark);
  padding: var(--space-20) 0;
  position: relative;
  overflow: hidden;
}

.shield-showcase::before {
  content: '';
  position: absolute;
  top: -20%;
  right: -10%;
  width: 50%;
  height: 80%;
  background: radial-gradient(circle, rgba(42, 157, 143, 0.15), transparent 65%);
  pointer-events: none;
}

.showcase-inner {
  position: relative;
  z-index: 1;
}

.showcase-copy {
  max-width: 36rem;
  margin-bottom: var(--space-10);
}

.showcase-copy .eyebrow {
  color: var(--accent-mint);
}

.showcase-copy h2 {
  color: var(--text-on-dark);
  font-size: clamp(1.75rem, 4vw, var(--text-4xl));
  margin-bottom: var(--space-4);
}

.showcase-copy .lede {
  color: var(--text-on-dark-muted);
  font-size: var(--text-lg);
}

.incident-demo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

.context-block {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: background var(--transition-base), border-color var(--transition-base),
    transform var(--transition-base);
  cursor: default;
}

.context-block.active {
  background: rgba(42, 157, 143, 0.12);
  border-color: rgba(42, 157, 143, 0.35);
  transform: translateY(-2px);
}

.block-label {
  display: block;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent-mint);
  margin-bottom: var(--space-2);
}

.block-preview {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-on-dark-muted);
  line-height: var(--leading-relaxed);
}

.context-block.active .block-preview {
  color: var(--text-on-dark);
}

.showcase-message {
  font-size: var(--text-lg);
  color: var(--text-on-dark-muted);
  margin: 0;
}

.showcase-message strong {
  color: var(--accent-mint);
}
</style>
