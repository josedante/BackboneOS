## Blueprints and Templating

### Naming Conventions
- `db-${tenant}`
- `redis-${tenant}`
- `backend-${env}-${tenant}`
- `worker-${env}-${tenant}`
- `beat-${env}-${tenant}`
- optional `frontend-${env}-${tenant}`

### Variables
- tenant, env (prod/staging), region
- plans: plan_backend, plan_workers, db_plan, redis_plan
- domains: custom_backend_domain, frontend_origin
- security: sentry_dsn, cors, csrf, SECRET_KEY

### Reconciliation Loop
1) Render parametric blueprint from tenant values
2) Commit to control-plane blueprints repo
3) Trigger Render Blueprint deploy hook
4) Receive webhooks → update Deploy record
5) Periodic drift detection and corrective apply

### Template Location
- See `templates/render-tenant.yaml` for the parametric blueprint used per environment.


