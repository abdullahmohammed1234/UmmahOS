import axios from 'axios';

const TOKEN_KEY = 'ummahos.auth_token';

export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
}

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 15000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem(TOKEN_KEY);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.localStorage.removeItem(TOKEN_KEY);
      window.localStorage.removeItem('ummahos.auth_user');
      window.localStorage.removeItem('ummahos.current_organization_id');

      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  },
);

export { TOKEN_KEY };
