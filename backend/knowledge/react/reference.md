# React Framework Reference

## Project Structure
- `src/App.jsx` — Root component
- `src/components/` — Reusable UI components
- `src/pages/` — Route-level components
- `src/api/` — API client (axios)
- `src/hooks/` — Custom React hooks
- `vite.config.js` — Build config (Vite)

## Version Compatibility
- React 19: New `use()` hook, Server Components, Actions, `ref` as prop
- React 18: Concurrent rendering, `useTransition`, `useDeferredValue`, automatic batching
- React 17: No new features, new JSX transform (no `import React`)

## Hooks (React 16.8+)
- `useState` — Local state
- `useEffect` — Side effects (fetch, subscriptions)
- `useContext` — Read context without Consumer
- `useRef` — DOM refs, mutable values
- `useMemo` / `useCallback` — Memoization
- `useReducer` — Complex state logic

## React 19 Specifics
- `use()` hook for promises and context
- `ref` passed as regular prop (no `forwardRef`)
- `useActionState` replaces `useFormState`
- Server Components (RSC) for data fetching

## React 18 Specifics
- `createRoot` replaces `ReactDOM.render`
- `useTransition` for non-urgent updates
- `Suspense` for lazy loading

## Routing (react-router-dom v6)
- `<BrowserRouter>`, `<Routes>`, `<Route>`
- `useNavigate()` replaces `useHistory()`
- `useParams()` for path params
- Nested routes with `<Outlet />`

## API Calls
- Use `axios` with interceptors for auth
- Pattern: `useEffect` + `useState` for data fetching
- Error handling: try/catch in async functions

## Styling
- CSS Modules: `import styles from './Component.module.css'`
- Inline: `style={{ color: 'red' }}`
- Tailwind: utility-first classes
