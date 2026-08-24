<template>
  <main class="login-page">
    <section class="login-card panel stack">
      <div class="login-header">
        <RouterLink to="/" class="brand-link">
          <span class="brand-mark" aria-hidden="true">U</span>
          <span class="eyebrow">UmmahOS</span>
        </RouterLink>
        <h1>Sign in to your MSA workspace</h1>
        <p class="muted">
          One account can belong to multiple independent organizations. After sign-in you choose
          which MSA you are operating in.
        </p>
      </div>
      <form class="stack" @submit.prevent="onSubmit">
        <label class="field">
          <span>Email</span>
          <input
            v-model="email"
            type="email"
            autocomplete="username"
            required
            data-testid="login-email"
          />
        </label>
        <label class="field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            data-testid="login-password"
          />
        </label>
        <p v-if="auth.error" class="error" data-testid="login-error">{{ auth.error }}</p>
        <button class="button" type="submit" :disabled="auth.isLoading" data-testid="login-submit">
          {{ auth.isLoading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
      <p class="muted back-link">
        <RouterLink to="/">← Back to UmmahOS overview</RouterLink>
      </p>
      <p class="muted demo-hint">
        Demo credentials are documented in <code>docs/DEMO_RUNBOOK.md</code>.
      </p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
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
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: var(--space-6);
}

.login-card {
  width: min(420px, 100%);
  padding: var(--space-8);
}

.login-header {
  margin-bottom: var(--space-2);
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  margin-bottom: var(--space-4);
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

h1 {
  margin: 0 0 var(--space-3);
  font-size: var(--text-2xl);
}

.back-link {
  font-size: var(--text-sm);
  margin: 0;
}

.back-link a {
  color: var(--primary);
}

.demo-hint {
  font-size: var(--text-xs);
  margin: 0;
}

.demo-hint code {
  font-size: inherit;
}
</style>
