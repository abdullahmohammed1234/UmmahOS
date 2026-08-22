import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { authApi } from '@/services/auth';
import { TOKEN_KEY } from '@/services/api';
import type { User } from '@/types';

const USER_KEY = 'ummahos.auth_user';

function readStoredUser(): User | null {
  const raw = window.localStorage.getItem(USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(window.localStorage.getItem(TOKEN_KEY));
  const user = ref<User | null>(readStoredUser());
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => Boolean(token.value && user.value));
  const memberships = computed(() => user.value?.memberships ?? []);

  function persist(nextToken: string | null, nextUser: User | null): void {
    token.value = nextToken;
    user.value = nextUser;

    if (nextToken) {
      window.localStorage.setItem(TOKEN_KEY, nextToken);
    } else {
      window.localStorage.removeItem(TOKEN_KEY);
    }

    if (nextUser) {
      window.localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    } else {
      window.localStorage.removeItem(USER_KEY);
    }
  }

  async function login(email: string, password: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const result = await authApi.login(email, password);
      persist(result.token, result.user);
    } catch (err) {
      error.value = 'Unable to sign in with those credentials.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCurrentUser(): Promise<void> {
    if (!token.value) {
      return;
    }

    const nextUser = await authApi.me();
    persist(token.value, nextUser);
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) {
        await authApi.logout();
      }
    } finally {
      persist(null, null);
    }
  }

  return {
    token,
    user,
    isLoading,
    error,
    isAuthenticated,
    memberships,
    login,
    fetchCurrentUser,
    logout,
    persist,
  };
});
