# Sistema de Resolución de Touchpoints

Framework Django para creación automática y configurable de touchpoints en canales web, email, WhatsApp y conectores personalizados.

**Documentación completa:** [docs/backend/connectors.md](../../docs/backend/connectors.md)

---

## Características

- Resolución automática de touchpoints desde datos de eventos
- Reglas de mapeo configurables en Django Admin
- Arquitectura v2.0 agnóstica al sujeto (sin `TouchpointInferenceProtocol`)
- Sistema de fallback con reintentos y backoff exponencial
- Monitoreo, métricas, alertas e integración con Sentry
- Comandos de gestión CLI y suite de pruebas de integración

## Inicio rápido

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View'
)

touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)
```

### Procesar evento web

```python
from websites.models import WebInteraction

interactions = WebInteraction.process_page_view_event({
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products',
    'user_agent': 'Mozilla/5.0...'
})
```

## Componentes principales

| Módulo | Descripción |
|--------|-------------|
| `connectors/protocols.py` | `TouchpointHint`, protocolos de resolver y mapping provider |
| `connectors/resolvers.py` | `DefaultTouchpointResolver`, `CachedTouchpointResolver` |
| `connectors/mapping_providers.py` | `DatabaseMappingProvider`, `CachedMappingProvider` |
| `connectors/models.py` | `TouchpointMappingRule`, `FailedEvent` |
| `connectors/fallback.py` | Almacenamiento y reintento de eventos fallidos |
| `connectors/tasks.py` | Tareas Celery de reintento |
| `connectors/metrics.py` | Seguimiento de rendimiento |

## Comandos de gestión

```bash
python manage.py backfill_touchpoints --batch-size=100
python manage.py test_touchpoint_resolution --connector-type=web
python manage.py manage_mapping_rules list
python manage.py manage_touchpoint_cache stats
python manage.py monitor_touchpoint_system --health-check
python manage.py cleanup_touchpoint_events --retention-days=30
```

## Admin

| Recurso | URL |
|---------|-----|
| Eventos fallidos | `/admin/connectors/failedevent/` |
| Reglas de mapeo | `/admin/connectors/touchpointmappingrule/` |
| Eventos de resolución | `/admin/connectors/touchpointresolutionevent/` |
| Alertas | `/admin/connectors/touchpointalert/` |
| Dashboard | `/admin/connectors/touchpointmappingrule/dashboard/` |

## Pruebas

```bash
python manage.py test connectors.tests
python manage.py test connectors.tests.test_touchpoint_resolution_integration
```

## Configuración

```python
# settings.py
TOUCHPOINT_RESOLUTION = {
    'DEFAULT_CACHE_TTL': 3600,
    'MAX_RESOLUTION_TIME_MS': 1000,
    'ENABLE_MONITORING': True,
}

FAILED_EVENT_RETRY_CONFIG = {
    'web': 5,
    'email': 3,
    'default': 3
}
```

## Documentación

Documentación completa en **[docs/backend/connectors.md](../../docs/backend/connectors.md)**: arquitectura v2.0, API, fallback, ejemplos, admin, migración, referencia rápida, pruebas e integración planificada con `sales`.
