## Staging Environments and Previews

### Staging per Tenant
- Mirror prod stack with `env=staging` and isolated DB/Redis.
- Distinct domains; update CORS/CSRF and `ALLOWED_HOSTS` accordingly.

### TTL and Cost Control
- Auto-suspend staging after inactivity; configurable TTL.

### Promotion
- Promote by reusing immutable images (retag) and re-applying blueprint.


