<template>
  <section class="panel content stack" data-testid="learning-patterns-page">
    <div>
      <h1>Learning Patterns</h1>
      <p class="muted">
        Patterns extracted from confirmed Community Shield reviews for education planning.
      </p>
    </div>

    <p v-if="!organization.canViewEducationPatterns" class="error" data-testid="patterns-denied">
      You cannot view learning patterns in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading learning patterns…</p>
    <p v-else-if="items.length === 0" class="muted">No learning patterns yet.</p>

    <table v-else data-testid="learning-patterns-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Type</th>
          <th>Status</th>
          <th>Objective</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>
            <RouterLink :to="{ name: 'admin-learning-pattern-detail', params: { id: item.id } }">
              {{ item.title }}
            </RouterLink>
          </td>
          <td>{{ patternTypeLabel(item.pattern_type) }}</td>
          <td>{{ item.status }}</td>
          <td>{{ item.learning_objective }}</td>
          <td class="actions">
            <button
              v-if="organization.canManageEducationPatterns && item.status === 'draft'"
              class="button secondary"
              type="button"
              data-testid="approve-pattern"
              :disabled="busyId === item.id"
              @click="approve(item.id)"
            >
              Approve
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationQuery } from '@/composables/useOrganizationQuery';
import type { LearningPattern } from '@/types';
import { patternTypeLabel } from '@/utils/education';

const items = ref<LearningPattern[]>([]);
const busyId = ref<number | null>(null);

const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canViewEducationPatterns) {
    items.value = [];
    return;
  }

  items.value = await communityApi.learningPatterns(organizationId);
});

async function approve(patternId: number): Promise<void> {
  const organizationId = organization.currentOrganization?.id;
  if (!organizationId) {
    return;
  }

  busyId.value = patternId;
  try {
    const updated = await communityApi.approveLearningPattern(organizationId, patternId);
    items.value = items.value.map((item) => (item.id === patternId ? updated : item));
  } finally {
    busyId.value = null;
  }
}
</script>
