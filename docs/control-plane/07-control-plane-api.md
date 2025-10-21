## Control Plane API

### Auth
- OAuth2/JWT. Roles: viewer, operator, admin.

### Endpoints (REST)
- POST `/tenants` — create tenant
- GET `/tenants/{id}` — detail
- PATCH `/tenants/{id}` — update config
- DELETE `/tenants/{id}` — delete (safe)
- POST `/tenants/{id}/environments` — create staging/prod
- POST `/tenants/{id}/deploys` — trigger deploy
- GET `/tenants/{id}/deploys` — list
- POST `/tenants/{id}/connectors/install` — install/upgrade connector
- PATCH `/tenants/{id}/secrets/rotate` — rotate secrets

### Webhooks
- POST `/webhooks/render` — deploy status, service events

### Response Fragments
- Tenant: id, slug, status, plan, region, createdAt
- Environment: id, type, status, blueprintVersion, desiredState, actualState
- Deploy: id, status, startedAt, completedAt, logsRef


