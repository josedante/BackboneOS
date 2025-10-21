## Security and Compliance

### Access Control
- Least privilege tokens for Git and Render; short-lived credentials where possible.
- RBAC in control plane: viewer/operator/admin per tenant/env.

### Secrets
- Encrypted at rest with KMS/HSM; audit rotation and access.

### Compliance
- Data residency by Render region; retention policies; export/delete workflows (GDPR).

### Audit
- Immutable audit log for config changes, deploys, and secret access.


