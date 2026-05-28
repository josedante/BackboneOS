# BackboneOS Operator UI (Django Templates)

> **Deprecated:** The standalone Next.js `frontend/` package was removed in **Phase 6** of [frontend consolidation](consolidation/FRONTEND_CONSOLIDATION.md). This file is kept as a pointer for historical links.

## Current stack

| Concern | Location |
|---------|----------|
| CRM pages | [`backend/templates/`](../backend/templates/) — `base_dashboard.html`, app templates under `*/templates/` |
| Styles | [`backend/static/src/input.css`](../backend/static/src/input.css) → `npm run tailwind:build` in [`backend/`](../backend/) |
| Session auth | `/login/`, `/logout/` — [`backend/templates/registration/`](../backend/templates/registration/) |
| User management | Django Admin — `/admin/` (sidebar **Users** link) |
| REST API | `/api/...` — unchanged for integrations and webhooks |

## Local development

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
cd backend && npm run tailwind:build   # when CSS changes
```

Open http://localhost:8000/login/

## Future work

- **Users HTML** — operator CRUD in templates (replacing Admin-only flow)
- **Analytics HTML** — dashboard cards/charts wired to existing selectors/APIs

See [FRONTEND_CONSOLIDATION.md](consolidation/FRONTEND_CONSOLIDATION.md) for full migration history.
