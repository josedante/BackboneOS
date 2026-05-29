# PRD: BackboneOS Upstream Contributions

**Status:** Proposed
**Author:** The Backbone Group (downstream fork maintainers)
**Target repository:** `josedante/BackboneOS` (`main`)
**Date:** 2026-05-29

---

## 1. Context

A downstream production fork of BackboneOS (deployed on Render) accumulated a
handful of improvements that are generic, useful to any operator, and not tied
to the fork's branding or deployment. This document specifies those improvements
so the upstream maintainers can implement them directly.

The two forks have diverged in opposite directions:

- **Upstream** consolidated the CRM UI into Django templates and removed the
  Next.js frontend (single-service architecture).
- **The downstream fork** retained Next.js and focused on production deployment.

Because of that, the proposals below are written **against upstream's current
single-service architecture**, not copied verbatim from the fork. Anything tied
to Next.js, the fork's domains/accounts, or its split settings is explicitly out
of scope (Section 7).

## 2. Goals and non-goals

**Goals**
- Add continuous integration (upstream currently has none).
- Fix a latent Flower health-check failure in `render.yaml`.
- Add a generic, idempotent management command to register tracked websites that
  bootstraps all obligatory prerequisite records.
- Open a discussion on Render plan-tier portability (no forced change).

**Non-goals**
- No changes to application data models.
- No changes to the consolidated Django UI.
- No introduction of fork-specific configuration.

## 3. Summary of proposals

| ID | Proposal | Type | Files | Risk |
|----|----------|------|-------|------|
| P1 | GitHub Actions CI for backend tests | Build | `.github/workflows/ci.yml` (new) | Low |
| P2 | Flower health check `/` → `/healthz` | Build | `render.yaml` | Low |
| P3 | Generic `register_website` command | Build | `backend/websites/management/commands/register_website.py` (new) + test (new) | Low |
| P4 | Render plan-tier portability | RFC / discussion | `render.yaml` (later) | n/a |

Suggested order: P1 and P2 first (trivial, obviously correct), then P3, with P4
opened as an issue for maintainer input before any code.

---

## 4. P1 — Continuous Integration for backend tests

### 4.1 Problem
Upstream has no `.github/` directory and therefore no automated testing on
pushes or pull requests. Regressions in the ~200-test backend suite are only
caught manually.

### 4.2 Rationale
A Dockerized test stack already exists at `backend/docker-compose.test.yml`. It
defines a `test-backend` service that waits for Postgres/Redis, migrates with
`backend.docker_test_settings`, and runs `python manage.py run_tests --type=all
--coverage --html-report --xml-report`. CI only needs to invoke it.

### 4.3 Requirements
1. New workflow `.github/workflows/ci.yml`.
2. Triggers: `push` to `main` and `pull_request` targeting `main`.
3. Runs the existing test compose file and **fails the job when tests fail**.
4. Must target the `test-backend` service explicitly. The downstream fork's
   original used `--exit-code-from backend`, which is wrong for this repo (the
   service is named `test-backend`, not `backend`) and would also start the
   never-exiting `test-runner`/`test-celery` helper containers.

### 4.4 Reference implementation
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Backend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run backend tests via Docker Compose
        run: |
          docker compose -f backend/docker-compose.test.yml up \
            --build --abort-on-container-exit --exit-code-from test-backend test-backend
```

Naming `test-backend` as the `up` target starts only its `depends_on`
(`test-db`, `test-redis`) while leaving the long-running helper services out.

### 4.5 Acceptance criteria
- A PR with a failing backend test shows a red `CI / Backend Tests` check.
- A PR with passing tests shows green.
- No AWS/registry/deploy steps (Render auto-deploys on merge to `main`).

### 4.6 Risks / notes
- First run builds the backend image; expect a few minutes. Optional follow-up:
  cache Docker layers.

---

## 5. P2 — Fix Flower health check

### 5.1 Problem
In `render.yaml`, the Flower monitoring service runs with `--basic_auth` but its
health check targets `/`:

```yaml
dockerCommand: celery -A backend flower --port=$PORT --basic_auth=$FLOWER_USER:$FLOWER_PASSWORD
...
healthCheckPath: /        # returns HTTP 401 because of basic auth
```

With basic auth enabled, `/` returns `401`, so Render marks the service
unhealthy and can restart/fail the deploy.

### 5.2 Requirements
1. Change the Flower service's `healthCheckPath` from `/` to `/healthz`
   (Flower's built-in unauthenticated health endpoint).
2. Leave the backend web service's `healthCheckPath: /health/` unchanged — that
   is a real Django route (`backend/backend/urls.py`), not Flower's endpoint.

### 5.3 Reference implementation
```yaml
    healthCheckPath: /healthz  # Flower's unauthenticated endpoint; / returns 401 under --basic_auth
```

### 5.4 Acceptance criteria
- The Flower service passes Render health checks while `--basic_auth` remains on.
- The backend service health check is untouched.

---

## 6. P3 — Generic `register_website` management command

### 6.1 Problem
Operators need a repeatable way to register the websites that send tracking
events. The downstream fork has a `register_tbg_website` command, but it
hard-codes the fork's domains and organization and assumes an organization
already exists. Upstream needs a **generic, brandless** equivalent that also
**bootstraps every obligatory prerequisite** so it works on a fresh database.

### 6.2 Obligatory prerequisite chain
A `Website` cannot exist without a `Division`, and a `Division` cannot exist
without an `OurOrganization`:

```
OurOrganization (name)
        └── Division (organization, name, code)
                └── Website (name, base_url, division)
                        └── Channel  (created automatically by Website.save())
```

Field facts (from `backend/our_institution/models.py` and
`backend/websites/models.py`):
- `OurOrganization`: only `name` is required; `org_type`/`industry`/`country`
  are nullable and must **not** be created.
- `Division`: requires `organization`, `name`, `code`; unique constraints on
  `(organization, name)` and `(organization, code)`.
- `Website`: requires `name`, `base_url` (unique), `division`. Its `save()`
  override auto-creates the tracking `Channel` via
  `_get_or_create_website_channel()`, so the command must **not** create a
  channel manually.
- `Seat`, `Unit`, `Position`, `Team` are **not** prerequisites for a website and
  must not be created.

### 6.3 Critical constraint — active-organization singleton
`OurOrganization.clean()` enforces that only one instance may be active at a
time. However, `get_or_create()` / `create()` bypass `clean()`. Therefore the
command must:
- **Prefer an existing active `OurOrganization`** when one exists.
- Only create an organization when none is active.
- **Never silently create a second active organization.**
- If `--organization` names a different org than the existing active one,
  **silently fall back to the existing active org** (the requested name is
  ignored, with an informational message). It must not create a second active
  org and must not error.

Note: the model helper `Website._get_default_division()` blindly does
`get_or_create(name="Default Organization")` and ignores the singleton rule. The
command must **not** reuse it; it must implement organization resolution that
respects the invariant.

### 6.4 Command interface
File: `backend/websites/management/commands/register_website.py`

| Argument | Required | Default | Purpose |
|----------|----------|---------|---------|
| `--url <base_url>` | Yes, unless `--from-file` | — | Single website to register |
| `--name <name>` | No | website domain | Display name |
| `--organization <name>` | No | active org, else `Default Organization` | Org to attach to |
| `--division <name>` | No | `Default Division` | Division to attach to |
| `--division-code <code>` | No | initials of division name, else `DEFAULT` | Division code |
| `--from-file <path.json>` | No | — | Bulk register from a JSON list |
| `--dry-run` | No | off | Print actions, write nothing |

`--from-file` expects a JSON list; only `base_url` is required per entry:
```json
[
  {"base_url": "https://example.com", "name": "Example", "division": "Marketing"},
  {"base_url": "https://blog.example.com"}
]
```

### 6.5 Behavior
1. Validate that `--url` or `--from-file` is provided (else error).
2. Resolve the organization once per run (Section 6.3 rules). If `--organization`
   names a different org than an already-active one, **silently fall back to the
   existing active org** (ignore the requested name, print an informational
   message) rather than violating the singleton.
3. For each site: ensure the `Division` exists (reuse or create), then create the
   `Website` (which auto-creates the `Channel`), or **reactivate** it if it
   exists with `active=False`, or report it as already active.
4. All writes for a non-dry run happen inside a single `transaction.atomic()`.
5. `--dry-run` performs no writes and clearly labels would-be actions.

### 6.6 Reference implementation
```python
"""
Register owned websites for BackboneOS tracking.

This command bootstraps the full prerequisite chain so it works on an empty
database:

    OurOrganization  ->  Division  ->  Website  ->  Channel (auto on save)

It is idempotent: existing organizations, divisions and websites are reused,
and a website that was previously soft-deleted (active=False) is reactivated.
"""

import json
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from our_institution.models import Division, OurOrganization
from websites.models import Website

DEFAULT_ORGANIZATION_NAME = "Default Organization"
DEFAULT_DIVISION_NAME = "Default Division"


class Command(BaseCommand):
    help = (
        "Register owned websites for tracking, creating any missing prerequisite "
        "organization and division along the way."
    )

    def add_arguments(self, parser):
        parser.add_argument("--url", metavar="BASE_URL",
                            help="Base URL to register (required unless --from-file)")
        parser.add_argument("--name", help="Display name (defaults to the domain)")
        parser.add_argument("--organization",
                            help="Organization name; defaults to the active org, "
                                 "or a new one if none exists")
        parser.add_argument("--division", default=DEFAULT_DIVISION_NAME,
                            help=f'Division name (default: "{DEFAULT_DIVISION_NAME}")')
        parser.add_argument("--division-code", dest="division_code",
                            help="Division code (defaults to the initials of the name)")
        parser.add_argument("--from-file", dest="from_file", metavar="PATH",
                            help="JSON file with a list of websites to register")
        parser.add_argument("--dry-run", action="store_true",
                            help="Show actions without writing anything")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if not options.get("url") and not options.get("from_file"):
            raise CommandError("Provide --url or --from-file.")

        sites = self._load_sites(options)
        if not sites:
            raise CommandError("No websites to register.")

        if dry_run:
            self._register_all(sites, options, dry_run=True)
            self.stdout.write(self.style.WARNING("\nDry run - no changes were made."))
        else:
            with transaction.atomic():
                self._register_all(sites, options, dry_run=False)
            self.stdout.write(self.style.SUCCESS("\nDone."))

    def _register_all(self, sites, options, dry_run):
        organization = self._resolve_organization(options.get("organization"), dry_run)
        division_cache = {}
        for site in sites:
            self.stdout.write(f"\n-> {site['base_url']}")
            self._process_site(site, organization, division_cache, options, dry_run)

    # Organization (respects the single-active-instance invariant) -----------

    def _resolve_organization(self, name, dry_run):
        active = OurOrganization.objects.filter(is_active=True).first()
        if name:
            if active and active.name != name:
                # Respect the single-active-org invariant: fall back silently.
                self.stdout.write(
                    f'Using active organization: "{active}" '
                    f'(ignoring --organization "{name}")'
                )
                return active
            return self._get_or_create_organization(name, dry_run)
        if active:
            self.stdout.write(f'Using active organization: "{active}"')
            return active
        return self._get_or_create_organization(DEFAULT_ORGANIZATION_NAME, dry_run)

    def _get_or_create_organization(self, name, dry_run):
        existing = OurOrganization.objects.filter(name=name).first()
        if existing:
            self.stdout.write(f'Using organization: "{existing}"')
            return existing
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Would create organization: "{name}"'))
            return None
        organization = OurOrganization.objects.create(name=name, is_active=True)
        self.stdout.write(self.style.SUCCESS(f'Created organization: "{organization}"'))
        return organization

    # Division ----------------------------------------------------------------

    def _ensure_division(self, organization, name, code, cache, dry_run):
        cache_key = (organization.pk if organization else None, name)
        if cache_key in cache:
            return cache[cache_key]

        division = None
        if organization is not None:
            division = Division.objects.filter(organization=organization, name=name).first()

        if division:
            self.stdout.write(f'    Division already exists: "{name}"')
        elif dry_run:
            self.stdout.write(self.style.WARNING(f'    Would create Division: "{name}" (code={code})'))
            division = None
        else:
            division = Division.objects.create(
                organization=organization, name=name, code=code,
                description=f"{name} division", is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f'    Created Division: "{name}" (code={code})'))

        cache[cache_key] = division
        return division

    # Website -----------------------------------------------------------------

    def _process_site(self, site, organization, division_cache, options, dry_run):
        base_url = site["base_url"]
        name = site.get("name") or self._domain(base_url)
        division_name = site.get("division") or options["division"]
        division_code = options.get("division_code") or self._derive_code(division_name)

        division = self._ensure_division(organization, division_name, division_code,
                                         division_cache, dry_run)

        existing = Website.objects.filter(base_url=base_url).first()
        if existing:
            if existing.active:
                self.stdout.write(self.style.SUCCESS(f"    Already registered and active: {base_url}"))
            elif dry_run:
                self.stdout.write(self.style.WARNING(f"    Would reactivate Website: {base_url}"))
            else:
                existing.active = True
                existing.save(update_fields=["active"])
                self.stdout.write(self.style.SUCCESS(f"    Reactivated Website: {base_url}"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'    Would create Website: {base_url} (name="{name}", division="{division_name}")'))
            return

        if division is None:
            raise CommandError(f"Cannot create {base_url}: division could not be resolved.")

        # Website.save() creates the associated tracking Channel automatically.
        website = Website.objects.create(name=name, base_url=base_url,
                                         division=division, active=True)
        self.stdout.write(self.style.SUCCESS(
            f"    Created Website: {website} (channel: {website.channel})"))

    # Input loading and helpers ----------------------------------------------

    def _load_sites(self, options):
        sites = []
        from_file = options.get("from_file")
        if from_file:
            try:
                with open(from_file, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                raise CommandError(f"Could not read --from-file {from_file!r}: {exc}")
            if not isinstance(data, list):
                raise CommandError("--from-file must contain a JSON list of website objects.")
            for index, entry in enumerate(data):
                if not isinstance(entry, dict) or not entry.get("base_url"):
                    raise CommandError(
                        f"Entry {index} in --from-file is missing the required 'base_url' field.")
                sites.append(entry)
        if options.get("url"):
            sites.append({"base_url": options["url"], "name": options.get("name"),
                          "division": options.get("division")})
        return sites

    @staticmethod
    def _domain(url):
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.replace("www.", "") or url

    @staticmethod
    def _derive_code(name):
        code = "".join(word[0] for word in name.split() if word).upper()[:20]
        return code or "DEFAULT"
```

### 6.7 Tests (required)
File: `backend/websites/tests/test_register_website_command.py`. The suite runs
on the in-memory SQLite `backend.test_settings`.

Required cases:
1. **Full bootstrap on an empty DB** — org + division + website + channel all
   created; org is active.
2. **Reuse existing active org** — passing only `--url` when an active org exists
   does not create a second org; the website's division belongs to that org.
3. **Explicit-org fallback** — passing `--organization "Other"` while a different
   active org exists falls back to the active org, creates no second org, and
   does not error.
4. **Idempotent re-run** — running twice leaves exactly one org/division/website.
5. **Dry run writes nothing** — counts remain zero.
6. **Reactivation** — an existing `active=False` website is flipped to active
   without duplication.
7. **`--from-file` bulk** — multiple sites registered; an entry without a
   division falls back to the default division.
8. **Validation** — running with neither `--url` nor `--from-file` raises
   `CommandError`.

```python
import json
import tempfile
import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from our_institution.models import Division, OurOrganization
from websites.models import Website


class RegisterWebsiteCommandTests(TestCase):
    def test_bootstraps_full_chain_on_empty_db(self):
        call_command("register_website", url="https://example.com")
        org = OurOrganization.objects.get()
        self.assertEqual(org.name, "Default Organization")
        self.assertTrue(org.is_active)
        division = Division.objects.get()
        self.assertEqual(division.organization, org)
        website = Website.objects.get(base_url="https://example.com")
        self.assertTrue(website.active)
        self.assertEqual(website.division, division)
        self.assertIsNotNone(website.channel)

    def test_reuses_existing_active_organization(self):
        acme = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        call_command("register_website", url="https://example.com")
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertEqual(
            Website.objects.get(base_url="https://example.com").division.organization, acme)

    def test_explicit_organization_falls_back_to_active_org(self):
        acme = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        call_command("register_website", url="https://example.com", organization="Other Org")
        # Falls back to the existing active org; no second org created, no error.
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertFalse(OurOrganization.objects.filter(name="Other Org").exists())
        self.assertEqual(
            Website.objects.get(base_url="https://example.com").division.organization, acme)

    def test_idempotent_rerun(self):
        call_command("register_website", url="https://example.com")
        call_command("register_website", url="https://example.com")
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertEqual(Division.objects.count(), 1)
        self.assertEqual(Website.objects.filter(base_url="https://example.com").count(), 1)

    def test_dry_run_writes_nothing(self):
        call_command("register_website", url="https://example.com", dry_run=True)
        self.assertEqual(OurOrganization.objects.count(), 0)
        self.assertEqual(Division.objects.count(), 0)
        self.assertEqual(Website.objects.count(), 0)

    def test_reactivates_inactive_website(self):
        org = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        division = Division.objects.create(organization=org, name="Marketing",
                                           code="MKT", is_active=True)
        website = Website.objects.create(name="Example", base_url="https://example.com",
                                         division=division, active=False)
        call_command("register_website", url="https://example.com")
        website.refresh_from_db()
        self.assertTrue(website.active)
        self.assertEqual(Website.objects.filter(base_url="https://example.com").count(), 1)

    def test_from_file_bulk_registration(self):
        payload = [
            {"base_url": "https://example.com", "name": "Example", "division": "Marketing"},
            {"base_url": "https://blog.example.com"},
        ]
        fd, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            call_command("register_website", from_file=path)
        finally:
            os.remove(path)
        self.assertTrue(Website.objects.filter(base_url="https://example.com").exists())
        self.assertTrue(Website.objects.filter(base_url="https://blog.example.com").exists())
        self.assertTrue(Division.objects.filter(name="Default Division").exists())
        self.assertTrue(Division.objects.filter(name="Marketing").exists())

    def test_requires_url_or_from_file(self):
        with self.assertRaises(CommandError):
            call_command("register_website")
```

### 6.8 Acceptance criteria
- All eight test cases pass under `backend.test_settings`.
- Running the command on a fresh database creates a working
  org/division/website/channel chain.
- Re-running is a no-op (idempotent).
- No second active organization can ever be created.

---

## 7. P4 — Render plan-tier portability (RFC / discussion)

### 7.1 Problem
The current `render.yaml` assumes a **Render Team plan**, which silently breaks
deploys for anyone on Free/Hobby:
- `previews: generation: automatic` — preview environments require Team.
- The backend service uses a `scaling:` block (`minInstances`/`maxInstances`/
  `targetCPUPercent`) — autoscaling requires Team; Hobby supports only a fixed
  `numInstances`.

### 7.2 Why this is an RFC, not a patch
Forcing Free/Hobby defaults would degrade the experience for Team-plan operators.
The right resolution is a maintainer decision. Options:

- **Option A (recommended):** keep Team features but document them with inline
  comments and a short note in deployment docs, e.g. "preview envs and the
  `scaling:` block require a Team plan; on Hobby, remove `previews:` and replace
  `scaling:` with `numInstances: 1`."
- **Option B:** default to Free/Hobby-compatible config (`numInstances`, no
  `previews:`) and document how to enable Team features.
- **Option C:** ship two profiles / a documented diff.

### 7.3 Deliverable
Open a GitHub issue capturing the above. Only implement a `render.yaml` change
after the maintainers choose an option. No code is proposed here.

---

## 8. Explicitly out of scope

- **CORS/CSRF settings:** the env-driven structure in
  `backend/backend/settings/base.py` is already identical to the downstream fork;
  only fork-specific domain lists differ, which are not upstreamable.
- **Settings package structure:** `settings/{base,development,production}.py`
  already exists upstream (identical); not a contribution.
- The Next.js frontend service, fork-specific domains / env-group names, the
  `backend.settings.production` deploy default, fork workflow `.md` files, and
  any committed `.env`/`test.log` files.

## 9. Provenance

All proposals were extracted from a downstream production fork and scrubbed of
deployment-specific values (domains, env-group names, plan tiers, branding). The
reference implementations in Sections 4–6 were drafted and statically reviewed
against upstream's current `main`; the test suite in 6.7 targets the existing
`backend.test_settings` (in-memory SQLite) and the existing
`backend/docker-compose.test.yml` stack used by P1.

## 10. Suggested delivery for maintainers

1. Land **P1** and **P2** as two small, independent PRs.
2. Land **P3** (command + tests) as a third PR; CI from P1 will exercise it.
3. Open **P4** as an issue; defer any `render.yaml` change until a plan-tier
   policy is chosen.
