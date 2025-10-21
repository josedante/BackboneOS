## Observability and Metrics

### Logs and Tracing
- Structured logs with `tenant`, `env`, `service`, `requestId`.
- Sentry: per-tenant project or tenant tag; sampling controls.

### Metrics
- CPU/mem, request rate, Celery tasks, queue depth, DB/Redis health.
- Usage metering for cost estimates: cpuMs, memMbMs, storageGb, egressGb.

### Alerts & SLOs
- Error rate, latency, saturation; budget alerts per tenant.


