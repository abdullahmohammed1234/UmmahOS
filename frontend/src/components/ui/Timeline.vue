<template>
  <div class="timeline" :data-testid="testId" role="list">
    <div
      v-for="(item, index) in items"
      :key="item.key ?? index"
      class="timeline-item"
      :class="{ done: item.done, active: item.active }"
      role="listitem"
    >
      <span class="timeline-dot" aria-hidden="true">{{ item.done ? '✓' : '' }}</span>
      <div class="timeline-content">
        <strong>{{ item.label }}</strong>
        <p v-if="item.description" class="muted">{{ item.description }}</p>
        <p v-if="item.date" class="timeline-date muted">{{ item.date }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TimelineItem {
  key?: string | number;
  label: string;
  description?: string;
  date?: string;
  done?: boolean;
  active?: boolean;
}

defineProps<{
  items: TimelineItem[];
  testId?: string;
}>();
</script>

<style scoped>
.timeline-content strong {
  display: block;
  font-size: var(--text-sm);
}

.timeline-content p {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
}

.timeline-date {
  font-size: var(--text-xs);
}
</style>
