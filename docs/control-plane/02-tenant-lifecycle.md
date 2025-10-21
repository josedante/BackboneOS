## Tenant Lifecycle

### States
- provisioning → active → (paused | deleting | failed)
- staging mirrors production with `env=staging`.

### Operations
- Create: validate config, allocate secrets, render blueprint, apply, run migrations, seed data.
- Update: validate diffs, rotate secrets if needed, rebuild images if connector set changed, apply.
- Pause/Resume: scale-to-zero where supported or suspend services; preserve data.
- Delete: snapshot backups, deprovision services, revoke tokens.

### Approvals and Audit
- Optional approval gates for plan/region/connector changes.
- Audit log for all changes and deploys with actor, before/after diffs.


