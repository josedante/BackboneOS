# Single-Tenant Frontend Consolidation — Handoff & Progress

Use this document to resume work in a **new agent session** without re-deriving context. Read [`.cursor/rules/consolidated-frontend.mdc`](../../.cursor/rules/consolidated-frontend.mdc) before changing backend code.

Optional: attach the Cursor plan `frontend_consolidation_roadmap` for full narrative; **this file is the in-repo source of truth** for status and next steps.

---

## Current next action

**Do Phase 1 + Phase 2 for `entities`** — extract selectors/services, then HTML at `/entities/` (same pattern as products).

1. Add `entities/selectors.py` and extend `entities/services.py` for shared reads/writes.
2. Add `entities/template_views.py`, templates under `entities/templates/entities/`, and `template_urls.py` with namespace `entities_html`.
3. Mount at `/entities/` in [`backend/backend/urls.py`](../../backend/backend/urls.py); enable sidebar link.
4. Run `dashboard.tests` + relevant entity/product regression tests; update this doc with commit SHA.

---

## Topological workflow (per app)

```text
dashboard home (done) → products P2 (done) → entities P1+P2 (next) → …
```

Complete **Phase 1 → Phase 2** per app after the shared layout exists. Do **not** delete Next.js routes (Phase 5) or the frontend Docker service (Phase 6) until HTML is verified.

See also [`docs/APPS.md`](../APPS.md).

---

## Layer conventions (mandatory)

| Module | Responsibility | Used by |
|--------|----------------|---------|
| `selectors.py` | Read-only: querysets, aggregates, dashboard dicts | DRF, `template_views` |
| `services.py` | Writes: mutations, transactions | DRF actions, POST handlers |

Rules: single Django process; preserve `/api/...` DRF; no HTTP loopback from templates; shared selectors; `{% extends "base_dashboard.html" %}` for app pages.

---

## Global phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | This tracking document | done |
| 1 | Service/selector extraction per app | in_progress — **`products` done** (writes in `services.py`) |
| 2 | Django template views per app | in_progress — **`products` done**; **`entities` next** |
| 3 | Shared base layout + Tailwind CSS | **done** — [`base_dashboard.html`](../../backend/templates/base_dashboard.html), compiled [`static/dist/styles.css`](../../backend/static/dist/styles.css) |
| 4 | Session auth on HTML | **partial done** — `/login/`, `@login_required` on `/` and `/products/` |
| 5 | Remove Next.js routes per app | pending |
| 6 | Docker/docs cleanup | pending |

---

## Dashboard home (milestone complete)

Replaces [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx) (mock stats/actions/activity).

| Item | Location |
|------|----------|
| App | [`backend/dashboard/`](../../backend/dashboard/) |
| Selector | [`dashboard/selectors.py`](../../backend/dashboard/selectors.py) → `get_home_context()` (v1 static; v2 real counts later) |
| View | [`dashboard/template_views.py`](../../backend/dashboard/template_views.py) → `home` |
| Templates | [`backend/templates/base_dashboard.html`](../../backend/templates/base_dashboard.html), [`templates/dashboard/home.html`](../../backend/templates/dashboard/home.html), [`templates/includes/`](../../backend/templates/includes/) |
| CSS source | [`backend/static/src/input.css`](../../backend/static/src/input.css) (shadcn tokens + dashboard layout) |
| CSS output | [`backend/static/dist/styles.css`](../../backend/static/dist/styles.css) via Tailwind v3 CLI |
| Tests | [`dashboard/tests.py`](../../backend/dashboard/tests.py) |

### URLs

| Path | Handler |
|------|---------|
| `/` | HTML dashboard (`dashboard:home`) — requires login |
| `/login/` | Session login |
| `/logout/` | Session logout (POST) |
| `/api/` | JSON API catalog (`api-catalog`) — was JSON at `/` before migration |

**Note:** URL name `api-catalog` avoids clash with DRF router `api-root` from [`our_institution`](../../backend/our_institution/urls.py).

### Access

- **Django CRM UI:** http://localhost:8000/ (after `docker-compose up backend`)
- **Next.js (legacy):** http://localhost:3000/ until Phase 5

### Commit

`4d7334b` — feat(dashboard): migrate homepage to Django templates at /

---

## Products HTML (Phase 2 complete)

Replaces [`frontend/src/app/products/page.tsx`](../../frontend/src/app/products/page.tsx) and [`frontend/src/app/products/[id]/page.tsx`](../../frontend/src/app/products/[id]/page.tsx).

| Item | Location |
|------|----------|
| Reads | [`products/selectors.py`](../../backend/products/selectors.py) — `get_products_list_context`, `get_product_detail_context`, `get_product_form_options` |
| Writes | [`products/services.py`](../../backend/products/services.py) — `create_product`, `update_product`, `delete_product` (shared with DRF) |
| Forms | [`products/forms.py`](../../backend/products/forms.py) |
| Views | [`products/template_views.py`](../../backend/products/template_views.py) |
| URLconf | [`products/template_urls.py`](../../backend/products/template_urls.py) — namespace `products_html` |
| Templates | [`products/templates/products/`](../../backend/products/templates/products/) — `list.html`, `create.html`, `detail.html` |
| Tests | [`products/tests_template_views.py`](../../backend/products/tests_template_views.py) |

### URLs

| Path | Handler |
|------|---------|
| `/products/` | List + filters + pagination (`products_html:list`) |
| `/products/new/` | Create (`products_html:create`) |
| `/products/<uuid>/` | Detail + full edit form (`products_html:detail`) |
| `/products/<uuid>/delete/` | POST delete (`products_html:delete`) |
| `/api/products/` | DRF (unchanged) |

### Commit

Pending commit on branch (base before this work: `252ca4f`). Update this line after merge.

---

## App rollout

| App | Phase 1 | Phase 2 | Notes |
|-----|---------|---------|-------|
| **dashboard** | n/a | home done | Shared shell for all apps |
| **products** | done | **done** | P1: `87ac531`, `fb3ded6`; P2: see Products HTML section |
| entities | pending | pending | **next** |
| interactions | pending | pending | — |
| campaigns | pending | pending | — |
| offers | pending | pending | — |

---

## `products` app reference

### URLs

| Surface | Prefix |
|---------|--------|
| REST API | `/api/products/` |
| HTML | `/products/` (`products_html` namespace) |

### Phase 2 selectors (in use)

| Page | Selector(s) |
|------|-------------|
| Product list | `get_products_list_context()` → `products_list_queryset`, `get_product_analytics_dashboard()['overview']` |
| Product detail | `get_product_detail_context()` → `get_bundle_info` |
| Forms | `get_product_form_options()` |

### Next.js to retire later (Phase 5)

- [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx) — superseded by Django `/`
- [`frontend/src/app/products/page.tsx`](../../frontend/src/app/products/page.tsx)
- [`frontend/src/app/products/[id]/page.tsx`](../../frontend/src/app/products/[id]/page.tsx)

---

## Tailwind build (Phase 3)

Toolchain lives under [`backend/`](../../backend/): [`package.json`](../../backend/package.json), [`tailwind.config.js`](../../backend/tailwind.config.js) (theme ported from [`frontend/tailwind.config.js`](../../frontend/tailwind.config.js)).

```bash
cd backend
npm install
npm run tailwind:build    # writes static/dist/styles.css (minified)
npm run tailwind:watch    # local dev rebuild
```

- **Templates** load `{% static 'dist/styles.css' %}` only (no separate `dashboard.css`).
- **`static/dist/styles.css`** is gitignored (`dist/` in root `.gitignore`); run `tailwind:build` locally or rely on Docker/CI (`Dockerfile`, `Dockerfile.prod` builder stage).
- **docker-compose dev** mounts `./backend:/app`, which overwrites image-built `static/dist/` — run `npm run tailwind:build` (or `tailwind:watch`) on the host when styling changes.

Production images run `npm ci`, `tailwind:build`, and `collectstatic` in the `Dockerfile.prod` builder; runtime remains a single Python process (`entrypoint.sh` may re-run `collectstatic` idempotently).

---

## Verification / test gate

```bash
cd backend && npm install && npm run tailwind:build

docker build -f backend/Dockerfile -t backboneos-test backend

# Dashboard + products API + HTML (22 tests):
docker run --rm -v "$(pwd)/backend:/app" -w /app \
  -e DJANGO_SETTINGS_MODULE=backend.test_settings \
  backboneos-test python manage.py test dashboard.tests products.tests.ProductsAPITests products.tests_template_views
```

`manage.py check` should report no issues.

### Known test debt (not blocking)

- Full `products` suite: Division fixtures, analytics JSON drift — see earlier notes.
- HTML tests use `backend.test_settings` (SQLite + simple staticfiles storage).

---

## Phase 2 checklist (`products`)

- [x] `template_views.py` + selectors only (writes via `services.py`)
- [x] `templates/products/*.html` extend `base_dashboard.html`
- [x] `/products/` URL mount (`products.template_urls`, not DRF `urls.py`)
- [x] Sidebar Products link → `products_html:list`
- [x] `ProductsAPITests` + `dashboard.tests` + `tests_template_views` green
- [x] Doc updated (commit SHA pending)

---

## Architecture

```mermaid
flowchart LR
  subgraph ingress [Ingress]
    Home["GET /"]
    ProductsUI["GET /products/"]
    API["DRF /api/..."]
  end
  subgraph dashboard_app [dashboard]
    SelD["selectors.get_home_context"]
    Base["base_dashboard.html"]
  end
  subgraph products_app [products]
    TV["template_views"]
    SelP["selectors.py"]
    Svc["services.py"]
  end
  Home --> SelD --> Base
  ProductsUI --> TV --> SelP --> Base
  TV --> Svc
  API --> SelP
  API --> Svc
```
