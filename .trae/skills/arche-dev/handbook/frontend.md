# Frontend Conventions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Vue 3 Composition API + `<script setup>` |
| Language | TypeScript (strict mode) |
| Build | Vite |
| Router | vue-router (role-based dynamic imports) |
| State | Pinia |
| HTTP Client | axios (via `src/services/api/`) |
| Testing | vitest + jsdom |
| Lint | ESLint + Prettier |
| Type Check | vue-tsc --noEmit |

## Code Splitting by Role

The frontend splits code into 3 role-based chunks:

| Role | Router | Components | Chunk loaded |
|------|--------|-----------|--------------|
| Guest (unauthenticated) | GuestLayout | blog/ | Blog chunk only |
| Authenticated user | PlatformShell | blog/ + user/ | Blog + Platform chunks |
| Admin | ConsoleLayout | blog/ + user/ + admin/ | All chunks |

Vite dynamic imports ensure unauthenticated users never load admin code:

```typescript
const AdminRoutes = () => import("@/views/admin/AdminDashboard.vue");
```

## Component Architecture

### Layer Hierarchy

```
src/components/
├── ui/              # Design system primitives — ArButton, ArCard, ArInput, etc.
├── blog/            # Public-facing blog components — PostCard, PostEditor, etc.
├── admin/           # Admin-only components — ModerationPanel, UserTable, etc.
├── user/            # Authenticated user components — UserCard, UserMenu
└── ...
src/layouts/
├── BaseLayout.vue   # Base shell (header + sidebar + footer)
├── BaseHeader.vue
├── BaseSidebar.vue
├── FooterBar.vue
├── GuestLayout.vue  # Unauthenticated users
├── UserLayout.vue   # Authenticated users
├── PlatformShell.vue
├── BlogShell.vue
└── ConsoleLayout.vue # Admin
```

### Design System

All UI primitives use the `Ar` prefix:

`ArButton`, `ArCard`, `ArTable`, `ArInput`, `ArAvatar`, `ArBadge`, `ArDivider`, `ArPagination`, `ArTag`, `ArWheelPicker`

These are self-built components, not from naive-ui. Do not import naive-ui components directly.

## API Call Convention

All API calls go through `src/services/api/`:

```
src/services/api/
├── index.ts          # axios instance with interceptors (auth, error handling)
├── generated.d.ts    # Auto-generated TypeScript types from OpenAPI schema
└── ...
```

### Error Handling Pattern

Follow the conventions in `frontend/docs/api-call-policy.md`. The standard pattern is:

```typescript
import { api } from "@/services/api";

async function fetchData() {
  try {
    const { data } = await api.get("/items");
    return data;
  } catch (error) {
    // handled by interceptor
    throw error;
  }
}
```

### API Type Generation

```bash
npm run generate:api
# Fetches running backend's OpenAPI schema → generates src/services/api/generated.d.ts
```

Run this after backend endpoint changes. CI verifies the generated file is up-to-date.

## Routing Convention

Role-based route files:

```
src/router/
├── index.ts           # Main router setup
├── blog-routes.ts     # Public routes
├── platform-routes.ts # Authenticated routes
└── admin-routes.ts    # Admin routes
```

## Component Naming

- Multi-word component names (Vue style guide recommendation)
- Prefix with area: `BlogPost`, `AdminUserTable`, `UserMenu`
- File names: `PascalCase.vue`

## Testing

```bash
npm run test:run       # Single run (vitest + jsdom)
npm run test           # Watch mode
```

Test files co-locate with components: `ComponentName.spec.ts`
