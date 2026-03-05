# Vue.js Framework Reference

## Directory Layout (REQUIRED — Do not deviate)
```
frontend/
├── public/
│   └── index.html            ← HTML entry point (REQUIRED)
├── src/
│   ├── main.js               ← createApp() + use(router) + use(pinia) entry
│   ├── App.vue               ← Root component with <RouterView />
│   ├── components/           ← Reusable SFCs (not page-level)
│   │   └── {ComponentName}.vue
│   ├── views/                ← One .vue file per route (e.g. HomeView.vue)
│   │   └── {PageName}View.vue
│   ├── router/
│   │   └── index.js          ← createRouter() with all route definitions
│   ├── stores/               ← ONE Pinia store per domain
│   │   └── {domain}.js       ← defineStore() with state + actions
│   └── api/                  ← Axios client + one file per backend resource
│       ├── client.js
│       └── {resource}.js
├── package.json              ← REQUIRED — includes vue, vue-router, pinia
└── vite.config.js
```

### Interface Contract Rules
- Stores handle ALL API calls — views/components call store actions, not axios directly.
- Each store exports a composable: `export const use{Domain}Store = defineStore(...)`.
- Views use `<script setup>` syntax exclusively.

## Project Structure
- `src/App.vue` — Root component
- `src/components/` — Reusable components
- `src/views/` — Route-level views
- `src/router/index.js` — Vue Router config
- `src/stores/` — Pinia stores (state management)
- `vite.config.js` — Build config

## Version Compatibility
- Vue 3.5+: Reactive props destructure stable
- Vue 3.4+: `defineModel()` for v-model
- Vue 3.3+: Generic components, `defineSlots()`
- Vue 3.x: Composition API, `<script setup>`, Teleport, Suspense

## Composition API (Vue 3)

### Import Rule (CRITICAL — Missing imports = runtime crash)
ALWAYS import every Composition API utility you use:
```js
import { ref, computed, watch, watchEffect, onMounted, onUnmounted, shallowRef } from 'vue';
```
- `ref()` — Reactive primitive values
- `computed()` — Derived values (MUST be imported to use)
- `watch()` / `watchEffect()` — Side effects (MUST be imported to use)
- `onMounted()`, `onUnmounted()` — Lifecycle (MUST be imported to use)
- `shallowRef()` — For non-reactive objects like WebSocket, Canvas: `const ws = shallowRef(null)`
  - NEVER put a WebSocket or complex object in `ref()` — use `shallowRef()`

## Script Setup (`<script setup>`)
- No explicit return, all top-level bindings exposed to template
- `defineProps()` — Component props
- `defineEmits()` — Component events
- `defineExpose()` — Expose for parent refs

## Routing (vue-router v4)
- `createRouter()`, `createWebHistory()`
- `<router-view>`, `<router-link>`
- `useRouter()`, `useRoute()` composables
- Navigation guards: `beforeEach`, `beforeEnter`

## State Management (Pinia)
- `defineStore()` with setup syntax
- `storeToRefs()` for reactive destructuring
- Persist with `pinia-plugin-persistedstate`:

```js
// main.js — REQUIRED setup
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
app.use(pinia);

// store — enable persistence
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const token = ref(null);
  
  const isAuthenticated = computed(() => !!token.value);
  
  return { user, token, isAuthenticated };
}, { persist: true });
```
- **Rule**: Expired/invalid JWT: check token validity on app load (see Navigation Guard).

## Version Compatibility (Hard Guard)
- **Rule**: ALWAYS check `package.json` before using version-specific APIs.
- Vue 3.4+: `defineModel()` available.
- Vue 3.x: Composition API, `<script setup>`.

## api/client.js — Canonical Axios Pattern
```javascript
import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' }
});

// 1. JWT Injection Interceptor
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`; // EXACT: uppercase A, Bearer prefix
  }
  return config;
});

// 2. Auth Failure Interceptor
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
```

## vite.config.js — Dev Proxy
```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Should match backend local port
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

## router/index.js — Auth Navigation Guard
```javascript
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [/* ... */]
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  
  // 1. Check token validity on app load/navigation
  if (auth.token && !auth.user) {
    try {
      // Validate token by fetching user profile
      const user = await auth.fetchProfile(); 
      if (!user) throw new Error();
    } catch (e) {
      auth.$reset(); // Clear invalid state
      if (to.meta.requiresAuth) return next('/login');
    }
  }

  // 2. Protected routes check
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});
```

## API Action Pattern (Pinia)
```javascript
// stores/game.js
import client from '../api/client';

export const useGameStore = defineStore('game', () => {
  const games = ref([]);

  async function fetchGames() {
    const { data } = await client.get('/games');
    games.value = data;
  }

  return { games, fetchGames };
});
```
