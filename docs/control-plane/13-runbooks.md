## Runbooks

### Create Tenant
1) Validate config → persist desired state
2) Allocate secrets → render blueprint → apply
3) Run migrations and seed data

### Add/Update Connector
1) Select version → bake images → deploy
2) Verify health checks

### Rotate Secrets
1) Generate new secrets → update env var group → re-deploy

### Rollback
1) Select prior image tags → re-apply blueprint

### Restore DB
1) Select backup → create RestoreRequest → execute and verify


