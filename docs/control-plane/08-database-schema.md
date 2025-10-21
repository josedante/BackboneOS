## Database Schema (Control Plane)

### Core Entities
- Tenant(id, slug, name, plan, region, status, createdBy, createdAt, updatedAt)
- Environment(id, tenantId→Tenant.id, type[prod|staging], slug, status, createdAt, updatedAt)
- ServiceInstance(id, environmentId, type, name, renderServiceId, plan, region, desiredConfig, runtimeStatus)
- BlueprintTemplate(id, name, path, version, checksum)
- Deploy(id, environmentId, blueprintVersion, status, renderDeployId, startedAt, completedAt, actor)
- Secret(id, scope, key, valueEncrypted, rotationPolicy, lastRotatedAt)
- EnvVar(id, environmentId, serviceId, key, valueOrRef, isSecret)
- Connector(id, slug, name, description)
- ConnectorVersion(id, connectorId, version, sourceRef, requirementsPin, migrations)
- ConnectorInstallation(id, environmentId, connectorVersionId, configEncrypted, enabled, healthStatus)
- Domain(id, environmentId, hostname, certificateStatus, dnsProviderRef)
- AuditEvent(id, actor, scope, action, before, after, createdAt, requestId)

### Relationships
- Tenant 1—N Environment
- Environment 1—N ServiceInstance
- Environment 1—N Deploy, Domain, ConnectorInstallation
- Connector 1—N ConnectorVersion

### Suggested Indexes
- Tenant.slug UNIQUE
- Environment(tenantId, type) UNIQUE
- Deploy(environmentId, startedAt DESC)
- ConnectorInstallation(environmentId, connectorVersionId) UNIQUE


