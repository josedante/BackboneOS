## Connector Registry and Contract

### Registry
- Metadata: id, slug, name, owner, description, categories, compatibility.
- Versions: semantic versioning, published artifacts, changelog, deprecations.

### Package Contract
- Python package exposing entrypoints for tasks and webhooks.
- Settings manifest (JSON) with required/optional fields and types.
- Health checks and readiness probes.
- Migrations for DB changes; idempotent.

### Installation (Bake)
- Control plane pins version → generates `requirements.connectors.txt` and builds images.
- Installation record stores config (encrypted), status, and health.

### Testing
- Contract tests run in CI (unit + integration) per connector version.


