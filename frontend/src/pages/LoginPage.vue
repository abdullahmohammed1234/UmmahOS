<template>
  <main class="page login">
    <section class="panel stack">
      <div>
        <p class="eyebrow">UmmahOS</p>
        <h1>Sign in to your MSA workspace</h1>
        <p class="muted">
          One account can belong to multiple independent organizations. After sign-in you choose
          which MSA you are operating in.
        </p>
      </div>
      <form class="stack" @submit.prevent="onSubmit">
        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" autocomplete="username" required />
        </label>
        <label class="field">
          <span>Password</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="auth.error" class="error">{{ auth.error }}</p>
        <button class="button" type="submit" :disabled="auth.isLoading">
          {{ auth.isLoading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';

const auth = useAuthStore();
const organization = useOrganizationStore();
const router = useRouter();
const email = ref('');
const password = ref('');

async function onSubmit(): Promise<void> {
  await auth.login(email.value, password.value);
  await organization.loadContext();
  await router.push({ name: 'dashboard' });
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  align-items: center;
}

.panel {
  padding: 2rem;
}

.eyebrow {
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.8rem;
  color: var(--accent);
}

h1 {
  margin: 0.2rem 0 0.6rem;
}
</style>
