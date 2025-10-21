## Repo Access and Builds

### Repository Access
- Read-only access to BackboneOS repo (or mirrored template) via PAT/SSH key with least privilege.
- Optional separate blueprints repo where rendered tenant blueprints are committed.

### Image Build Strategy (Per Tenant)
1. Generate `requirements.connectors.txt` from tenant connector selections.
2. Build backend/worker images with connectors baked in; produce SBOM.
3. Tag images with `ghcr.io/backboneos/{service}:${tenant}-${env}-${sha}`.
4. Push to registry; store artifact refs on Build/Artifact records.
5. Apply blueprint referencing the new images.

### Caching and Speed
- Use build cache (registry-backed) and pinned `requirements.lock` to ensure reproducibility.
- Separate layers: base → app deps → connectors deps → app code.

### Promotion
- Promote staging → prod by retagging immutable images and re-applying blueprint (no rebuild).

### Connectors Bake
- Input: tenant connector manifest (name, version, config).
- Output: frozen `requirements.connectors.txt`, migrations run during deploy.


