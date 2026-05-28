# BackboneOS Frontend (Next.js — Phase 5 partial)

> **Phase 5:** CRM dashboard, products, and entities UI moved to **Django templates** at port 8000. This package remains for **users**, **analytics**, and **JWT login** until Phase 6 decommission. See [docs/consolidation/FRONTEND_CONSOLIDATION.md](../docs/consolidation/FRONTEND_CONSOLIDATION.md).

A Next.js 15 app with App Router, TypeScript, and Tailwind CSS.

## Features

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- React Query (users/analytics pages)
- JWT authentication with cookie refresh (`authApi`)

## URLs

| URL | Served by |
|-----|-----------|
| http://localhost:8000/ | Django CRM (session auth) |
| http://localhost:3000/ | Next landing → link to Django CRM |
| http://localhost:3000/users | Next |
| http://localhost:3000/analytics | Next |
| http://localhost:3000/login | Next (JWT) |
| http://localhost:3000/products/* | **Redirects** to Django `/products/*` |
| http://localhost:3000/entities/* | **Redirects** to Django `/entities/*` |

## Environment

```bash
cp .env.example .env.local   # or use repo root .env
```

```bash
# REST API (JWT, users)
NEXT_PUBLIC_API_BASE=http://localhost:8000

# Django HTML CRM base (defaults to NEXT_PUBLIC_API_BASE in dev)
# NEXT_PUBLIC_DJANGO_UI_BASE=http://localhost:8000
```

In production, API and UI hosts may differ; set `NEXT_PUBLIC_DJANGO_UI_BASE` explicitly for sidebar and redirect targets.

## Getting Started

```bash
npm install
npm run dev
```

Open http://localhost:3000. Use **Open CRM dashboard** or go directly to http://localhost:8000/login/.

### Scripts

- `npm run dev` — development server
- `npm run build` — production build
- `npm run start` — production server
- `npm run lint` — ESLint
- `npm run type-check` — TypeScript

## Project Structure (after Phase 5)

```
src/
├── app/
│   ├── analytics/       # Next — analytics dashboard
│   ├── users/           # Next — user management
│   ├── login/           # Next — JWT login
│   ├── page.tsx         # Landing (links to Django CRM)
│   ├── layout.tsx
│   └── providers.tsx
├── components/
│   ├── analytics/
│   ├── layout/          # sidebar.tsx — Django + Next split nav
│   └── users/
└── lib/
    ├── api.ts           # authApi + usersApi only
    ├── django-ui.ts     # Django UI base URL helper
    └── utils.ts
```

Removed in Phase 5: `app/products/**`, `app/entities/**`, mock dashboard components, CRM API clients in `api.ts`.

## API client (`src/lib/api.ts`)

Phase 5 scope:

- `authApi` — JWT login, current user, logout
- `usersApi` — user CRUD for `/users` page

CRM REST helpers (`productsApi`, `entitiesApi`, etc.) were removed; Django templates use `selectors`/`services` directly.

## Backend reference

When extending remaining Next pages, reference Django models and serializers under `backend/` — see consolidation doc for CRM apps now on templates.

## Deployment

Render.com: set `NEXT_PUBLIC_API_BASE` and optionally `NEXT_PUBLIC_DJANGO_UI_BASE`. Redirects in `next.config.js` use the Django UI base at build time.

SSL: development may disable cert verification for `localhost` / `orb.local`; production uses full verification.
