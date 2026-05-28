# Single-Tenant Frontend Consolidation — Progress Tracker

Rules: [`.cursor/rules/consolidated-frontend.mdc`](../../.cursor/rules/consolidated-frontend.mdc)

Master plan: Cursor plan `frontend_consolidation_roadmap` (do not edit the plan file in-repo).

## Test gate (per app)

```bash
docker-compose exec backend python manage.py test <app_label>
```

## Global phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | This tracking document | done |
| 1 | Service/selector extraction per app | in_progress |
| 2 | Django template views + `templates/<app>/` per app | pending |
| 3 | Shared base layout, HTMX/Alpine static assets | pending |
| 4 | URL mount + session auth gates for HTML | pending |
| 5 | Decommission Next.js routes per app | pending |
| 6 | Docker/docs cleanup (remove frontend service) | pending |

## App rollout order

| App | Phase 1 | Phase 2 | Commit (Phase 1) |
|-----|---------|---------|------------------|
| products | done | pending | (commit below) |
| entities | pending | pending | — |
| interactions | pending | pending | — |
| campaigns | pending | pending | — |
| offers | pending | pending | — |

## products app

- **API (preserved):** `/api/products/`
- **Templates (Phase 2):** `backend/products/templates/products/`
- **Layer:** `backend/products/selectors.py` (reads), `backend/products/services.py` (writes)
- **Phase 1 gate:** `ProductsAPITests` (10 tests) passes — validates selector wiring for viewsets.
- **Fixtures:** `test_factories.py` added; `ProductsAPITests` and `tests_analytics` use `create_test_division()`.
- **Remaining:** Legacy model/integration tests still need `organization` on all `Division` creates; analytics tests expect older JSON keys (`optimization_opportunities`, etc.).
