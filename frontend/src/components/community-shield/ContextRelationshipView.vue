<template>
  <section class="context-map" data-testid="context-relationship-view">
    <header class="context-map-header">
      <h2>{{ title }}</h2>
      <p class="muted">
        Only fields that were actually recorded are shown. Missing pieces stay empty — they are not invented.
      </p>
    </header>

    <div class="context-diagram" aria-label="Evidence relationship diagram">
      <div class="diagram-row related-top">
        <article v-if="relatedItems.length" class="diagram-node">
          <span class="node-label">Related item</span>
          <p class="node-body">{{ relatedItems[0] ? platformLabel(relatedItems[0].platform) : '' }}</p>
        </article>
        <p v-else class="diagram-node empty">No related items</p>
      </div>

      <div class="diagram-connector down" aria-hidden="true">│</div>

      <div class="diagram-row middle">
        <article v-if="replies.length" class="diagram-node side">
          <span class="node-label">Reply</span>
          <p class="node-body">{{ replies.length }} recorded</p>
        </article>
        <p v-else class="diagram-node side empty">No replies</p>

        <div class="diagram-connector horizontal" aria-hidden="true">────►</div>

        <article class="diagram-node center original">
          <span class="node-label">Original item</span>
          <p class="node-title">{{ originalTitle }}</p>
          <p class="node-meta muted">
            {{ platformLabel(incident.platform) }}
            <template v-if="incident.visibility"> · {{ visibilityLabel(incident.visibility) }}</template>
          </p>
        </article>

        <div class="diagram-connector horizontal" aria-hidden="true">◄────</div>

        <article v-if="relatedItems.length > 1" class="diagram-node side">
          <span class="node-label">Related item</span>
          <p class="node-body">{{ platformLabel(relatedItems[1]?.platform ?? relatedItems[0]?.platform ?? '') }}</p>
        </article>
        <p v-else-if="relatedItems.length === 1" class="diagram-node side empty muted">—</p>
        <p v-else class="diagram-node side empty">No related items</p>
      </div>

      <div class="diagram-connector down" aria-hidden="true">│</div>

      <ol class="diagram-flow">
        <li :class="{ muted: !surroundingContext }">
          Context{{ surroundingContext ? '' : ' not provided' }}
        </li>
        <li :class="{ ai: aiPresent, muted: !aiPresent }">
          {{ aiPresent ? 'AI Analysis (advisory)' : 'AI Analysis not yet available' }}
        </li>
        <li :class="{ human: humanPresent, muted: !humanPresent }">
          {{ humanPresent ? 'Human Review (authoritative)' : 'Human Review pending' }}
        </li>
        <li>{{ outcomeLabel }}</li>
      </ol>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { platformLabel, reviewOutcomeLabel, visibilityLabel } from '@/utils/communityShield';

interface RelatedItemView {
  id?: number;
  platform: string;
  description?: string | null;
  observed_at?: string | null;
}

interface ReplyView {
  id?: number;
  content?: string;
}

interface IncidentView {
  platform: string;
  visibility?: string;
  original_item_title?: string | null;
  original_item_content?: string | null;
  original_item_posted_at?: string | null;
  surrounding_context?: string | null;
  review_outcome?: string | null;
  replies?: ReplyView[];
  related_items?: RelatedItemView[];
}

const props = withDefaults(
  defineProps<{
    incident: IncidentView;
    title?: string;
    aiPresent?: boolean;
    humanPresent?: boolean;
  }>(),
  {
    title: 'Context and evidence relationship',
    aiPresent: false,
    humanPresent: false,
  },
);

const replies = computed(() => props.incident.replies ?? []);
const relatedItems = computed(() => props.incident.related_items ?? []);

const originalTitle = computed(
  () =>
    props.incident.original_item_title
    || props.incident.original_item_content
    || 'Original item details were not provided',
);

const surroundingContext = computed(() => props.incident.surrounding_context);

const outcomeLabel = computed(() => {
  if (props.incident.review_outcome) {
    return `Outcome: ${reviewOutcomeLabel(props.incident.review_outcome)}`;
  }
  return 'Outcome not yet recorded';
});
</script>

<style scoped>
.context-map {
  padding: var(--space-5) var(--space-6);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  background: var(--surface);
}

.context-map-header h2 {
  margin: 0 0 var(--space-2);
  font-size: var(--text-lg);
}

.context-diagram {
  margin-top: var(--space-5);
  display: grid;
  justify-items: center;
  gap: var(--space-2);
}

.diagram-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  width: 100%;
  flex-wrap: wrap;
}

.diagram-row.related-top {
  max-width: 14rem;
}

.diagram-row.middle {
  max-width: 100%;
}

.diagram-node {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--surface-elevated);
  min-width: 7rem;
  text-align: center;
}

.diagram-node.original {
  min-width: 11rem;
  border-color: rgba(20, 92, 62, 0.28);
  background: var(--primary-soft);
}

.diagram-node.empty {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.node-label {
  display: block;
  margin-bottom: var(--space-1);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--primary);
}

.node-title {
  margin: 0 0 var(--space-1);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.node-body,
.node-meta {
  margin: 0;
  font-size: var(--text-sm);
}

.diagram-connector {
  color: var(--text-muted);
  font-size: var(--text-sm);
  line-height: 1;
}

.diagram-connector.down {
  font-family: monospace;
}

.diagram-flow {
  margin: var(--space-2) 0 0;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border);
  background: var(--background-alt);
  width: 100%;
  max-width: 20rem;
  list-style: none;
  display: grid;
  gap: var(--space-2);
  text-align: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.diagram-flow li.ai {
  color: var(--info);
}

.diagram-flow li.human {
  color: var(--primary);
}

@media (max-width: 640px) {
  .diagram-connector.horizontal {
    display: none;
  }

  .diagram-row.middle {
    flex-direction: column;
  }
}
</style>
