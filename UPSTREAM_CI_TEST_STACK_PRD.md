# PRD: Fix Docker CI Test Stack (P1 Follow-up)

**Status:** Proposed  
**Author:** The Backbone Group (downstream fork maintainers)  
**Target repository:** `josedante/BackboneOS` (`main`)  
**Date:** 2026-05-29  
**Related:** [UPSTREAM_CONTRIBUTIONS_PRD.md](./UPSTREAM_CONTRIBUTIONS_PRD.md) — P1 (CI workflow)

---

## 1. Context

P1 added GitHub Actions CI (`.github/workflows/ci.yml`) that runs the existing
Docker test stack (`backend/docker-compose.test.yml`). **CI is currently red on
every push** because the stack invokes Django management commands that Django
never discovers.

This is not a database connectivity failure. The `test-db` and `test-redis`
services start and pass health checks; the `test-backend` container exits before
connecting to Postgres.

Observed failure (GitHub Actions log):

```
backboneos-test-backend  | Waiting for database...
backboneos-test-backend  | Unknown command: 'wait_for_db'
backboneos-test-backend  | Type 'manage.py help' for usage.
backboneos-test-backend exited with code 1
```

The downstream production fork (`thebackbonegroup/backboneos`) hits the same
failure after syncing P1. **This fix belongs upstream** so all forks benefit and
CI actually meets P1's acceptance criteria.

---

## 2. Goals and non-goals

**Goals**

- Make `backend/docker-compose.test.yml` runnable end-to-end via `manage.py`.
- Unblock P1 CI: failing tests → red check; passing tests → green check.
- Preserve existing developer workflows (`run_tests_docker.sh`, docs referencing
  `run_tests`, `wait_for_db`, `test_coverage`).
- Use conventional Django patterns (no project-package hacks).

**Non-goals**

- Do not add the Django **project package** (`backend/backend/`) to
  `INSTALLED_APPS`. That package holds settings, URLs, WSGI, and abstract base
  models — it is not a domain app and registering it as one is non-standard.
- No changes to application data models or business logic.
- No fork-specific configuration (domains, Render env groups, branding).

---

## 3. Root cause

Three infrastructure management commands live under the **project package**:

```
backend/backend/management/commands/
  wait_for_db.py
  run_tests.py
  test_coverage.py
```

Django discovers management commands only from apps listed in `INSTALLED_APPS`.
The project package is not listed there (correctly — see non-goals above), so
`python manage.py wait_for_db` and `python manage.py run_tests` fail everywhere:
CI, `docker-compose.test.yml`, and `run_tests_docker.sh`.

The Docker test stack and these commands pre-date P1; P1 exposed the latent
bug by running them automatically on every push.

---

## 4. Summary of proposals

| ID | Proposal | Type | Primary files | Risk |
|----|----------|------|---------------|------|
| P1-fix-A | Move infra commands to a `core` app | Refactor | New `backend/core/`, delete old command paths, update docs | Low |
| P1-fix-B | Replace custom commands in compose with shell + pytest | CI-only | `backend/docker-compose.test.yml` | Low–Med |
| P1-fix-C | Fix `POSTGRES_HOST` default in docker test settings | Bugfix | `backend/backend/docker_test_settings.py` | Trivial |

**Recommended:** **P1-fix-A** (idiomatic, fixes local dev and CI). Land **P1-fix-C**
in the same PR. **P1-fix-B** is acceptable if maintainers want zero new apps and
can accept that `run_tests_docker.sh` still needs a separate fix.

Suggested order: **P1-fix-A + P1-fix-C** as one PR; verify CI green on `main`.

---

## 5. P1-fix-A — Move commands to a `core` app (recommended)

### 5.1 Problem

Infrastructure commands are in the wrong package for Django's discovery rules.

### 5.2 Rationale

A small `core` app (no models, or only shared non-migrated utilities) is a
common pattern for cross-cutting management commands. Commands keep their names
(`wait_for_db`, `run_tests`, `test_coverage`); callers (`docker-compose.test.yml`,
shell scripts, docs) require no flag or argument changes.

### 5.3 Requirements

1. Create Django app `core` under `backend/core/` with `AppConfig` and empty
   `models.py` (or no models module).
2. Add `'core'` to `INSTALLED_APPS` in `backend/backend/settings/base.py`.
3. **Move** (do not duplicate) these files:
   - `backend/backend/management/commands/wait_for_db.py`
     → `backend/core/management/commands/wait_for_db.py`
   - `backend/backend/management/commands/run_tests.py`
     → `backend/core/management/commands/run_tests.py`
   - `backend/backend/management/commands/test_coverage.py`
     → `backend/core/management/commands/test_coverage.py`
4. Remove empty `backend/backend/management/` tree if nothing remains.
5. Update references in documentation only if paths are cited explicitly
   (`TESTING.md`, `DOCKER_TESTING.md`, `TESTING_STATUS.md`); command invocations
   stay the same.
6. Do **not** move domain commands that already live in real apps (e.g.
   `websites/management/commands/register_website.py`).

### 5.4 Reference layout

```
backend/
  core/
    __init__.py
    apps.py
    models.py          # empty or omitted
    management/
      __init__.py
      commands/
        __init__.py
        wait_for_db.py
        run_tests.py
        test_coverage.py
```

`backend/core/apps.py`:

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
```

`INSTALLED_APPS` (excerpt):

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    # ...
    'core',
    'users',
    'world',
    # ...
]
```

### 5.5 Verification (local)

From repo root:

```bash
docker compose --project-directory . -f backend/docker-compose.test.yml up \
  --build --abort-on-container-exit --exit-code-from test-backend test-backend
```

Or, after `test-db` / `test-redis` are up:

```bash
docker compose --project-directory . -f backend/docker-compose.test.yml \
  run --rm test-backend python manage.py help | grep -E 'wait_for_db|run_tests'
```

Both commands must appear in `manage.py help` output.

### 5.6 Acceptance criteria

- `python manage.py wait_for_db` succeeds when Postgres is reachable.
- `python manage.py run_tests --type=all` runs the test suite.
- GitHub Actions `CI / Backend Tests` is green on `main`.
- A PR that introduces a failing assertion shows a red CI check (P1 criterion
  finally exercisable).

### 5.7 Risks / notes

- `core` must not define concrete models unless migrations are intentional.
- If abstract base models (`BaseUUIDModel`) remain in `backend/backend/models.py`,
  that is unchanged — only commands move.

---

## 6. P1-fix-B — Compose-only alternative (not recommended alone)

### 6.1 Problem

Same as Section 3, but addressed only in the CI entrypoint.

### 6.2 Approach

Replace the `test-backend` command in `docker-compose.test.yml`:

```yaml
command: >
  sh -c "
    echo 'Waiting for database...' &&
    until pg_isready -h test-db -U myuser -d test_mydatabase; do sleep 1; done &&
    echo 'Running migrations...' &&
    python manage.py migrate --settings=backend.docker_test_settings &&
    echo 'Running tests...' &&
    pytest --cov=. --cov-report=xml --cov-report=html
  "
```

`postgresql-client` is already installed in `backend/Dockerfile`, so `pg_isready`
is available.

### 6.3 Drawbacks

- `run_tests_docker.sh` and documented `manage.py run_tests` flows remain broken
  until P1-fix-A is also done.
- pytest invocation must mirror what `run_tests.py` does (markers, settings
  module, coverage paths) or coverage/report behavior may diverge.

Use only as a stopgap if a `core` app is rejected; prefer P1-fix-A.

---

## 7. P1-fix-C — Correct Postgres host default

### 7.1 Problem

In `backend/backend/docker_test_settings.py`, the database host defaults to
`'db'` (production compose service name), but the test compose service is
named `test-db`:

```python
'HOST': config('POSTGRES_HOST', default='db'),  # wrong default for test stack
```

Compose sets `POSTGRES_HOST=test-db` in the `test-backend` environment, so CI
usually works once commands are discovered. The default is still misleading for
local runs without that env var.

### 7.2 Fix

```python
'HOST': config('POSTGRES_HOST', default='test-db'),
```

Low risk; include in the P1-fix-A PR.

---

## 8. CI workflow checklist (no change required if P1-fix-A lands)

Upstream `.github/workflows/ci.yml` should already use:

```yaml
docker compose --project-directory . -f backend/docker-compose.test.yml up \
  --build --abort-on-container-exit --exit-code-from test-backend test-backend
```

The `--project-directory .` flag is required because compose volume and build
paths (`./backend`) are relative to the **repo root**, not `backend/`.

Confirm the workflow matches this; no other workflow changes are needed once
commands are discoverable.

---

## 9. Explicitly rejected approaches

| Approach | Why not |
|----------|---------|
| Add `backend.apps.BackendConfig` to `INSTALLED_APPS` | Works technically but blurs project config vs application code; non-standard |
| Disable CI until tests are rewritten | Leaves P1 acceptance criteria unmet |
| Fork-only patch in downstream | Duplicates maintenance; breaks on every upstream sync |

---

## 10. Documentation updates

After P1-fix-A, update path references in:

- `backend/TESTING_STATUS.md`
- `backend/TESTING.md`
- `backend/DOCKER_TESTING.md`

Change cited locations from
`backend/backend/management/commands/` to
`backend/core/management/commands/`.
Command examples (`python manage.py run_tests …`) stay unchanged.

Optionally add a short note to `UPSTREAM_CONTRIBUTIONS_PRD.md` Section 4.6
(P1 risks) that P1-fix-A must land for CI to pass.

---

## 11. Suggested delivery for maintainers

1. Open issue: **"P1 follow-up: Docker test stack commands not discovered"**
   linking to this PRD.
2. Implement **P1-fix-A + P1-fix-C** in a single PR.
3. Confirm GitHub Actions green on `main`.
4. Downstream forks merge/rebase upstream; no fork-specific CI hacks needed.

---

## 12. Provenance

Discovered while syncing P1 CI into a production fork (`thebackbonegroup/backboneos`).
Failure reproduced on upstream `main` with the same `Unknown command: 'wait_for_db'`
exit. Investigation confirmed Django command discovery rules; no Postgres or Redis
misconfiguration in the compose healthchecks.
