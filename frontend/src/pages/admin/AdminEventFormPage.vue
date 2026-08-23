<template>
  <section class="panel content stack">
    <RouterLink to="/admin/events">Back to events</RouterLink>
    <h1>{{ isEdit ? 'Edit event' : 'Create event' }}</h1>
    <p v-if="!organization.canManageEvents" class="error">
      You cannot manage events in this organization.
    </p>
    <form v-else class="stack" @submit.prevent="onSubmit">
      <label class="field">
        <span>Title</span>
        <input v-model="title" required />
      </label>
      <label class="field">
        <span>Description</span>
        <textarea v-model="description"></textarea>
      </label>
      <label class="field">
        <span>Location</span>
        <input v-model="location" />
      </label>
      <label class="field">
        <span>Starts at</span>
        <input v-model="startsAt" type="datetime-local" required />
      </label>
      <label class="field">
        <span>Ends at</span>
        <input v-model="endsAt" type="datetime-local" />
      </label>
      <label class="field">
        <span>Registration URL</span>
        <input v-model="registrationUrl" type="url" />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="button" type="submit" :disabled="isSaving">Save</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { communityApi } from '@/services/community';
import { useOrganizationStore } from '@/stores/organization';
import { fromDateTimeLocal, toDateTimeLocal } from '@/utils/date';

const route = useRoute();
const router = useRouter();
const organization = useOrganizationStore();
const title = ref('');
const description = ref('');
const location = ref('');
const startsAt = ref('');
const endsAt = ref('');
const registrationUrl = ref('');
const error = ref('');
const isSaving = ref(false);
const isEdit = computed(() => Boolean(route.params.id));

watch(
  () => [organization.currentOrganization?.id, route.params.id],
  async ([organizationId, id]) => {
    if (!organizationId || !id) {
      title.value = '';
      description.value = '';
      location.value = '';
      startsAt.value = '';
      endsAt.value = '';
      registrationUrl.value = '';
      return;
    }

    try {
      const item = await communityApi.event(Number(organizationId), Number(id));
      title.value = item.title;
      description.value = item.description ?? '';
      location.value = item.location ?? '';
      startsAt.value = toDateTimeLocal(item.starts_at);
      endsAt.value = toDateTimeLocal(item.ends_at);
      registrationUrl.value = item.registration_url ?? '';
    } catch {
      error.value = 'Unable to load this event.';
    }
  },
  { immediate: true },
);

async function onSubmit(): Promise<void> {
  const organizationId = organization.currentOrganization?.id;

  if (!organizationId) {
    return;
  }

  isSaving.value = true;
  error.value = '';

  try {
    const payload = {
      title: title.value,
      description: description.value,
      location: location.value,
      starts_at: fromDateTimeLocal(startsAt.value) ?? undefined,
      ends_at: fromDateTimeLocal(endsAt.value),
      registration_url: registrationUrl.value || null,
    };

    if (isEdit.value) {
      await communityApi.updateEvent(organizationId, Number(route.params.id), payload);
    } else {
      await communityApi.createEvent(organizationId, payload);
    }

    await router.push({ name: 'admin-events' });
  } catch {
    error.value = 'Unable to save this event.';
  } finally {
    isSaving.value = false;
  }
}
</script>
