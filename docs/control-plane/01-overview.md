## BackboneOS Control Plane — Overview

### Purpose
Enable dedicated per-tenant environments on Render for BackboneOS customers. The control plane provisions, configures, and manages each tenant’s full stack, builds per-tenant images with selected connectors, and exposes a self-service API/UI to update configuration safely.

### Architecture
- Dedicated stack per tenant:
  - Backend API (Django) with migrations
  - Celery worker and beat
  - Redis (keyvalue service)
  - Postgres (managed database)
  - Django serves operator HTML CRM on the backend web service (no separate Next.js deploy)
  - Optional Flower (operational visibility)
- Per-tenant staging environment (same topology) for validation and promotion.

### Responsibilities of the Control Plane
- Persist tenant configuration, secrets, and desired state.
- Generate parameterized Render blueprints and apply idempotently.
- Build per-tenant images (bake connector set) and manage promotions.
- Orchestrate secrets, CORS/CSRF/ALLOWED_HOSTS, domains, and SSL.
- Provide APIs for lifecycle ops (create/update/pause/resume/delete) and deployment.
- Observe, meter, and audit per tenant.

### Integration with This Repo
- Read access to BackboneOS repo (or a mirrored template) to build per-tenant images.
- The blueprint mirrors `render.yaml` components with tenantized names and env vars.
- Django settings are env-var driven; the control plane maps per-tenant values to Render env var groups.

### Staging Environments
- One staging per tenant: isolated DB/Redis, separate domains, distinct CORS/CSRF and `ALLOWED_HOSTS`.
- Time-to-live and auto-suspend to control cost; promotion to prod via image tag + blueprint re-apply.


