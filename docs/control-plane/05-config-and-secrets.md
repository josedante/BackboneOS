## Configuration and Secrets

### Configuration Model
- Layers: global defaults → plan defaults → tenant overrides → environment overrides (prod/staging).
- Validated by JSON Schema (see `schemas/tenant-config.schema.json`).

### Secret Management
- Encrypted at rest in the control plane (KMS/HSM), with rotation.
- Scoped: tenant/environment/service; mapped to Render env var groups.
- Rotation playbooks and automatic re-deploy when secrets change.

### Service Mapping (Django/Celery/Frontend)
- `DATABASE_URL`, `REDIS_URL` from managed services.
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` from domain config.
- `SECRET_KEY`, `SENTRY_DSN` via env var group `env-${env}-${tenant}`.

### Change Workflow
1) Validate config against schema
2) Persist desired state and audit diff
3) Render blueprint and apply; reconcile until actual = desired


