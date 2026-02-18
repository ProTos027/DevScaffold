# Vue.js Framework Reference

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
- `ref()` — Reactive primitive values
- `reactive()` — Reactive objects
- `computed()` — Derived values
- `watch()` / `watchEffect()` — Side effects
- `onMounted()`, `onUnmounted()` — Lifecycle

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
- Persist with `pinia-plugin-persistedstate`

## API Calls
- Use `axios` with composables pattern
- `useFetch` custom composable recommended
