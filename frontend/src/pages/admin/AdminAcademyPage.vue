<template>
  <section class="panel content stack">
    <div class="actions">
      <div>
        <h1>Academy</h1>
        <p class="muted">Organization-scoped course foundation. No lessons or grading yet.</p>
      </div>
      <RouterLink v-if="organization.canManageCourses" class="button" to="/admin/academy/new">
        Create
      </RouterLink>
    </div>
    <p v-if="!organization.canManageCourses" class="error">
      You cannot manage Academy in this organization.
    </p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="isLoading" class="muted">Loading…</p>
    <table v-else>
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ item.status }}</td>
          <td class="actions">
            <RouterLink :to="{ name: 'admin-course-edit', params: { id: item.id } }">Edit</RouterLink>
            <button class="button secondary" type="button" @click="togglePublish(item)">
              {{ item.status === 'published' ? 'Unpublish' : 'Publish' }}
            </button>
            <button class="button danger" type="button" @click="onDelete(item.id)">Delete</button>
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
import type { Course } from '@/types';

const items = ref<Course[]>([]);
const { organization, isLoading, error } = useOrganizationQuery(async (organizationId) => {
  if (!organization.canManageCourses) {
    items.value = [];
    return;
  }

  items.value = await communityApi.courses(organizationId);
});

async function togglePublish(course: Course): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId) {
    return;
  }

  const nextStatus = course.status === 'published' ? 'draft' : 'published';
  const updated = await communityApi.updateCourse(organizationId, course.id, { status: nextStatus });
  items.value = items.value.map((item) => (item.id === course.id ? updated : item));
}

async function onDelete(id: number): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId || !window.confirm('Delete this course?')) {
    return;
  }

  await communityApi.deleteCourse(organizationId, id);
  items.value = items.value.filter((item) => item.id !== id);
}
</script>
