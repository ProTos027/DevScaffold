# React Framework Reference

## Directory Layout (REQUIRED — Do not deviate)
```
frontend/
├── public/
│   └── index.html            ← HTML entry point (REQUIRED)
├── src/
│   ├── main.jsx              ← ReactDOM.createRoot entry point
│   ├── App.jsx               ← Root component, sets up <BrowserRouter> + <Routes>
│   ├── components/           ← Reusable UI components (NOT page-level)
│   │   └── {ComponentName}/
│   │       ├── {ComponentName}.jsx
│   │       └── {ComponentName}.module.css
│   ├── pages/                ← One directory per route
│   │   └── {PageName}/
│   │       ├── {PageName}.jsx
│   │       └── {PageName}.module.css  ← MANDATORY: Consistent with components
│   ├── api/                  ← Axios client + one file per backend resource
│   │   ├── client.js         ← axios instance with baseURL + interceptors
│   │   └── {resource}.js     ← functions like fetchItems(), createItem()
│   ├── hooks/                ← Custom hooks (e.g. useAuth.js, useGame.js)
│   └── context/              ← React Context providers (if global state needed)
├── .env                      ← VITE_API_URL=http://localhost:8000
├── package.json              ← REQUIRED — includes react, react-dom, react-router-dom
└── vite.config.js            ← Proxy configuration
```

### Interface Contract Rules
- All API calls go through `src/api/` — NEVER fetch directly from pages/components.
- Component props must be typed (PropTypes or TypeScript if specified).
- Pages receive data via hooks or direct API calls, NOT via prop drilling from App.
- **MANDATORY**: Group Pages into directories with their own `.module.css`, matching the Component pattern.

## Version Compatibility (Hard Guard)
- **Rule**: ALWAYS check `package.json` before using version-specific APIs.
- React 19: `use()`, `useActionState`, `ref` as prop.
- React 18: `createRoot`, `useTransition`, `Suspense`.

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
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
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

## Authentication Patterns
- **Token Storage**: ALWAYS use `localStorage.setItem('token', ...)` for persistence.
- **Protected Routes**: Wrap private pages in an `<AuthGuard>` component.
```javascript
// components/AuthGuard.jsx
const AuthGuard = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};
```

## Styling (Standard)
- **MANDATORY**: Use CSS Modules for all page-level and component-level styling.
- Pattern: `import styles from './ComponentName.module.css';`
- Usage: `<div className={styles.container}>...</div>`
