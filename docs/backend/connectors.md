# Sistema de Resolución de Touchpoints (connectors)

Documentación consolidada del framework Django para creación automática y configurable de touchpoints en múltiples canales de comunicación (web, email, WhatsApp y conectores personalizados).

**Versión de arquitectura:** 2.0 (diseño agnóstico al sujeto)  
**Última actualización:** enero 2025

---

## Tabla de contenidos

1. [Visión general](#visión-general)
2. [Inicio rápido](#inicio-rápido)
3. [Arquitectura v2.0](#arquitectura-v20)
4. [Referencia de API](#referencia-de-api)
5. [Sistema de fallback y recuperación](#sistema-de-fallback-y-recuperación)
6. [Historial del sistema de fallback](#historial-del-sistema-de-fallback)
7. [Ejemplos de uso](#ejemplos-de-uso)
8. [Interfaz de administración](#interfaz-de-administración)
9. [Guía de migración v1.0 a v2.0](#guía-de-migración-v10-a-v20)
10. [Referencia rápida](#referencia-rápida)
11. [Pruebas de integración](#pruebas-de-integración)
12. [Captura contextual: integración sales (planificado)](#captura-contextual-integración-sales-planificado)

---

## Visión general

### Características

- **Resolución automática de touchpoints:** creación inteligente basada en datos de interacción
- **Reglas de mapeo configurables:** reglas administrables desde Django Admin
- **Soporte multicanal:** web, email, WhatsApp y conectores personalizados
- **Fallback y recuperación de eventos:** reintentos automáticos con backoff exponencial
- **Monitoreo de rendimiento:** métricas, alertas y registros de salud del sistema
- **Interfaz de administración:** dashboards, analítica y gestión de eventos fallidos
- **Comandos de gestión:** herramientas CLI para operaciones y mantenimiento
- **Pruebas de integración:** suite end-to-end
- **Arquitectura extensible:** diseño basado en protocolos
- **Integración con Sentry:** seguimiento de errores y rendimiento

### Componentes principales

| Componente | Propósito |
|------------|-----------|
| `TouchpointHint` | Dataclass con metadatos del touchpoint extraídos de eventos |
| `TouchpointResolverProtocol` | Interfaz de resolución agnóstica al sujeto |
| `MappingProviderProtocol` | Interfaz de búsqueda de reglas de mapeo |
| `DefaultTouchpointResolver` | Lógica central de resolución |
| `CachedTouchpointResolver` | Resolver con caché para alto volumen |
| `DatabaseMappingProvider` | Proveedor de reglas respaldado por base de datos |
| `CachedMappingProvider` | Proveedor con caché |
| `TouchpointMappingRule` | Modelo de reglas configurables |

### Conectores soportados

- **Web:** interacciones de sitio web (page views, formularios, etc.)
- **Email:** aperturas, clics, rebotes (paquete independiente planificado)
- **WhatsApp:** mensajes y medios (paquete independiente planificado)
- **Personalizados:** extensibles mediante el mismo patrón de hints y resolvers

### Flujo de resolución (v2.0)

```
Datos del evento → TouchpointHint → Búsqueda de regla → Creación de touchpoint
     (raw)         (estructurado)      (transforma)         (crea)
```

**Cambio arquitectónico clave:** ya no se requiere que los objetos conector implementen `TouchpointInferenceProtocol`. Los hints se construyen directamente desde datos crudos y los resolvers reciben parámetros explícitos (`hint`, `connector_type`, `source_identifier`).

### Estado del sistema

| Área | Estado |
|------|--------|
| Framework central | Completo |
| Conector web | Completo |
| Monitoreo | Completo |
| Admin | Completo |
| Comandos de gestión | Completo |
| Pruebas de integración | Completo |
| Conector email | Planificado (paquete independiente) |
| Conector WhatsApp | Planificado (paquete independiente) |

---

## Inicio rápido

### 1. Resolución básica

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

### 2. Crear regla de mapeo

```python
from connectors.models import TouchpointMappingRule

rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='example.com',
    event_code='web.page_view',
    touchpoint_code='web.home_page_view',
    touchpoint_label='Home Page View',
    channel_code='web',
    medium_code='organic',
    priority=100,
    is_active=True
)
```

### 3. Monitorear rendimiento

```python
from connectors.metrics import track_resolution

with track_resolution('web', {'url': 'example.com'}) as tracker:
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
    tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)
```

### 4. Procesar evento web

```python
from websites.models import WebInteraction

event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products/laptop',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'user_agent': 'Mozilla/5.0...'
}

interactions = WebInteraction.process_page_view_event(event_data)
```

### Comandos de gestión frecuentes

```bash
# Backfill de touchpoints faltantes
python manage.py backfill_touchpoints --batch-size=100

# Probar resolución
python manage.py test_touchpoint_resolution --connector-type=web --event-code=web.page_view

# Gestionar reglas
python manage.py manage_mapping_rules list
python manage.py manage_mapping_rules create \
    --connector-type=web \
    --event-code=web.form_submit \
    --touchpoint-code=web.contact_form \
    --priority=100

# Caché
python manage.py manage_touchpoint_cache clear
python manage.py manage_touchpoint_cache warm
python manage.py manage_touchpoint_cache stats

# Monitoreo
python manage.py monitor_touchpoint_system --health-check

# Limpieza
python manage.py cleanup_touchpoint_events --retention-days=30 --dry-run
```

### Configuración

```python
# settings.py
TOUCHPOINT_RESOLUTION = {
    'DEFAULT_CACHE_TTL': 3600,
    'MAX_RESOLUTION_TIME_MS': 1000,
    'ENABLE_MONITORING': True,
    'RETENTION_DAYS': {
        'detailed_events': 90,
        'aggregated_metrics': 365,
    }
}

TOUCHPOINT_MONITORING = {
    'ENABLE_ALERTS': True,
    'ALERT_THRESHOLDS': {
        'error_rate': 0.05,
        'resolution_time_ms': 1000,
    }
}
```

Variables de entorno:

```bash
TOUCHPOINT_CACHE_TTL=3600
TOUCHPOINT_MONITORING_ENABLED=true
TOUCHPOINT_ALERT_EMAIL=admin@example.com
```

---

## Arquitectura v2.0

### v1.0 (dependiente del sujeto) — obsoleto

```python
class WebInteraction(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(...)

touchpoint = resolver.resolve(web_interaction)
```

### v2.0 (agnóstico al sujeto) — actual

```python
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

### Diagrama de flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                         FUENTE DEL EVENTO                        │
│              (Navegador, app móvil, API, etc.)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Datos crudos  │
                    │  del evento    │
                    └────────┬───────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ build_hint_from_     │
                 │ event_data()         │
                 └──────────┬───────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ TouchpointHint │
                    └────────┬───────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │   DefaultTouchpointResolver        │
        │   .resolve(hint, connector_type,   │
        │            source_identifier)      │
        └────────────┬───────────────────────┘
                     │
                     ├──────────────────────────┐
                     ▼                          ▼
           ┌─────────────────┐      ┌──────────────────┐
           │ MappingProvider │      │ Crear/obtener    │
           │ .lookup_mapping │      │ Channel, Medium, │
           └────────┬────────┘      │ TouchpointType   │
                    │               └──────────┬───────┘
                    ▼                          │
           ┌─────────────────┐                │
           │ Aplicar regla   │                │
           │ (opcional)      │                │
           └────────┬────────┘                │
                    └──────────┬──────────────┘
                               ▼
                    ┌──────────────────┐
                    │   Touchpoint     │
                    └──────────┬───────┘
                               ▼
                    ┌──────────────────┐
                    │   Interaction    │
                    └──────────┬───────┘
                               ▼
                 ┌─────────────────────────┐
                 │ Interacción específica  │
                 │ del conector            │
                 │ (WebInteraction, etc.)  │
                 └─────────────────────────┘
```

### TouchpointHint

```python
@dataclass(frozen=True)
class TouchpointHint:
    code: Optional[str] = None
    channel_code: Optional[str] = None
    medium_code: Optional[str] = None
    touchpoint_type_code: Optional[str] = None
    label: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

Los hints son inmutables (`frozen=True`).

### DefaultTouchpointResolver

```python
class DefaultTouchpointResolver:
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        mapping_rule = self.mapping_provider.lookup_mapping(
            connector_type=connector_type,
            source_identifier=source_identifier,
            hint=hint
        )
        if mapping_rule:
            hint = self._apply_mapping_rule(hint, mapping_rule)
        return self._get_or_create_touchpoint(hint)
```

### Clasificación tridimensional

Cada touchpoint se clasifica en tres dimensiones:

| Dimensión | Pregunta | Ejemplos |
|-----------|----------|----------|
| **Canal (WHERE)** | ¿Dónde ocurrió? | `web`, `email`, `mobile_app`, `social`, `api` |
| **Medio (HOW)** | ¿Cómo llegó? | `organic`, `cpc`, `paid`, `social`, `email`, `referral` |
| **Tipo (WHAT)** | ¿Qué tipo de touchpoint? | `web_page`, `web_form`, `email_open`, `email_click`, `mobile_screen` |

Ejemplo:

```python
TouchpointHint(
    code='web.product_view',
    channel_code='web',           # WHERE: sitio web
    medium_code='cpc',             # HOW: búsqueda de pago
    touchpoint_type_code='web_page',  # WHAT: vista de página
    label='Product Page View'
)
```

### Procesamiento de eventos web (flujo completo)

```python
class WebInteraction:
    @classmethod
    def process_page_view_event(cls, event_data: dict):
        website, _ = Website.objects.get_or_create(
            base_url=event_data['website_base']
        )

        hint = cls.build_touchpoint_hint_from_event_data(event_data, website)

        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        touchpoint = resolver.resolve(
            hint,
            connector_type='web',
            source_identifier=website.base_url
        )

        agent = cls._get_or_create_agent(event_data.get('user_agent'))
        action, _ = Action.objects.get_or_create(code='page_view')

        interaction = Interaction.objects.create(
            touchpoint=touchpoint,
            action=action,
            agent=agent,
            occurred_at=event_data.get('occurred_at')
        )

        web_interaction = cls.objects.create(
            interaction=interaction,
            website=website,
            url=event_data['full_url'],
            utm_source=event_data.get('utm_source'),
            utm_medium=event_data.get('utm_medium'),
        )

        return [web_interaction]
```

### Beneficios de v2.0

1. **Pruebas más simples:** no se necesitan clases mock de conectores
2. **Mayor flexibilidad:** hints desde cualquier fuente de datos
3. **Mejor rendimiento:** resolución antes de crear la interacción
4. **Código más claro:** parámetros explícitos, sin dependencias ocultas del estado del objeto

### Historial de versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 2.0 | 2025-01 | Arquitectura agnóstica al sujeto, resolución pre-creación |
| 1.0 | 2024-12 | Arquitectura dependiente del sujeto con `TouchpointInferenceProtocol` |

---

## Referencia de API

### TouchpointResolverProtocol

```python
class TouchpointResolverProtocol(Protocol):
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        ...
```

### MappingProviderProtocol

```python
class MappingProviderProtocol(Protocol):
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        ...
```

**Prioridad de resolución de reglas:**

1. Coincidencia específica: `source_identifier` + `event_code`
2. Coincidencia por conector: `connector_type` + `event_code`
3. Coincidencia global: solo `event_code`

### CachedTouchpointResolver

```python
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

resolver = CachedTouchpointResolver(
    mapping_provider=CachedMappingProvider(),
    cache_timeout=3600,
    use_cache=True
)

touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
```

### TouchpointMappingRule — campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `connector_type` | CharField | Tipo de conector (`web`, `email`, etc.) |
| `source_identifier` | CharField | Identificador de origen (dominio, patrón) |
| `event_code` | CharField | Código de evento a coincidir |
| `touchpoint_code` | CharField | Código de touchpoint destino |
| `touchpoint_label` | CharField | Etiqueta legible |
| `channel_code` | CharField | Canal destino |
| `medium_code` | CharField | Medio destino |
| `touchpoint_type_code` | CharField | Tipo de touchpoint destino |
| `priority` | IntegerField | Prioridad (mayor = más específico) |
| `is_active` | BooleanField | Regla activa |
| `metadata` | JSONField | Metadatos adicionales |

### Comandos de gestión

#### test_touchpoint_resolution

```bash
python manage.py test_touchpoint_resolution
python manage.py test_touchpoint_resolution --scenario=web
python manage.py test_touchpoint_resolution --verbose
python manage.py test_touchpoint_resolution --create-mapping-rules
```

Escenarios: `basic`, `mapping`, `web`, `email`, `whatsapp`, `all`

#### manage_mapping_rules

```bash
python manage.py manage_mapping_rules list
python manage.py manage_mapping_rules list --connector-type=web
python manage.py manage_mapping_rules create \
    --connector-type=web \
    --source-identifier=example.com \
    --event-code=web.page_view \
    --touchpoint-code=web.home_page \
    --priority=150
python manage.py manage_mapping_rules update --id=123 --priority=200
python manage.py manage_mapping_rules delete --id=123
python manage.py manage_mapping_rules activate --id=123
python manage.py manage_mapping_rules deactivate --id=123
```

#### manage_touchpoint_cache

```bash
python manage.py manage_touchpoint_cache stats
python manage.py manage_touchpoint_cache clear
python manage.py manage_touchpoint_cache warm
python manage.py manage_touchpoint_cache test-performance --iterations=1000
```

#### monitor_touchpoint_system

```bash
python manage.py monitor_touchpoint_system health
python manage.py monitor_touchpoint_system metrics
python manage.py monitor_touchpoint_system metrics --hours=24
python manage.py monitor_touchpoint_system metrics --export=metrics.json
```

#### backfill_touchpoints

```bash
python manage.py backfill_touchpoints
python manage.py backfill_touchpoints --connector-type=web
python manage.py backfill_touchpoints --batch-size=100 --limit=1000 --dry-run
```

### Monitoreo de rendimiento

```python
from connectors.metrics import track_resolution
from connectors.monitoring_models import TouchpointResolutionEvent, TouchpointResolutionMetrics

with track_resolution('web', {'url': 'example.com'}) as tracker:
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
    tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)

# Eventos recientes
recent = TouchpointResolutionEvent.objects.filter(
    occurred_at__gte=datetime.now() - timedelta(hours=1)
).order_by('-occurred_at')

# Errores
errors = TouchpointResolutionEvent.objects.filter(error_occurred=True).order_by('-occurred_at')[:10]
```

### Códigos HTTP (API de eventos)

| Código | Significado | Acción del cliente |
|--------|-------------|-------------------|
| `201` | Creado | Evento procesado correctamente |
| `202` | Aceptado | Evento almacenado para reintento automático |
| `400` | Bad Request | Error del cliente; corregir y reintentar |
| `500` | Server Error | Fallo catastrófico (procesamiento + fallback fallaron) |

Respuesta `201`:

```json
{
  "success": true,
  "message": "Successfully processed page view event",
  "interactions_created": 3,
  "interaction_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

Respuesta `202` (fallback):

```json
{
  "success": false,
  "error": "Event processing failed but has been queued for retry",
  "fallback_id": "6d542e78-8a12-4743-81e8-3a4c79077779",
  "message": "Your event will be processed automatically"
}
```

### Buenas prácticas de API

1. Construir hints desde datos crudos, no hardcodear valores genéricos
2. Resolver touchpoints **antes** de crear `Interaction`
3. Usar `CachedTouchpointResolver` en escenarios de alto volumen
4. Preferir métodos de procesamiento de eventos (`WebInteraction.process_page_view_event`)
5. Registrar métricas con `track_resolution`

---

## Sistema de fallback y recuperación

> Versión: 1.0 | Estado: listo para producción

### Descripción

Cuando ocurren errores críticos del sistema (5xx) durante el procesamiento de eventos, el sistema almacena el evento para reintento con backoff exponencial, evitando pérdida de datos durante fallos temporales.

### Flujo del sistema

```
Evento API → Procesamiento
                ├─ Éxito → 201 Created
                ├─ Error cliente (4xx) → 400 Bad Request (no se almacena)
                ├─ Error sistema (5xx) → FailedEvent → 202 Accepted
                └─ Fallo catastrófico → 500 Internal Server Error

Celery Beat (cada 5 min) → retry_failed_events_task
                ├─ Éxito → status='processed'
                ├─ Fallo → backoff exponencial
                └─ Max reintentos → status='failed'
```

### Modelo FailedEvent

Módulo: `connectors/models.py`

| Campo | Descripción |
|-------|-------------|
| `id` | UUID |
| `connector_type` | Tipo de conector (`web`, `email`, `payment`, etc.) |
| `event_type` | Tipo de evento (`page_view`, `form_submit`, etc.) |
| `source_identifier` | Identificador de origen |
| `raw_payload` | Datos originales del evento (JSON) |
| `status` | `pending`, `retrying`, `processed`, `failed`, `abandoned` |
| `error_message` | Mensaje de error |
| `error_trace` | Traceback completo |
| `retry_count` | Intentos realizados |
| `first_failed_at` | Timestamp del primer fallo |
| `last_retry_at` | Timestamp del último reintento |
| `next_retry_at` | Próximo reintento programado |
| `processed_at` | Timestamp de procesamiento exitoso |
| `interaction_ids` | IDs de interacciones creadas tras éxito |

### API de fallback

Módulo: `connectors/fallback.py`

#### store_failed_event()

```python
from connectors.fallback import store_failed_event

failed_event = store_failed_event(
    connector_type='web',
    event_type='page_view',
    raw_payload={'full_url': 'https://example.com', ...},
    error_message='Database connection timeout',
    error_trace='Traceback (most recent call last)...',
    source_identifier='example.com'
)
```

#### retry_failed_event()

```python
from connectors.fallback import retry_failed_event
from connectors.models import FailedEvent

event = FailedEvent.objects.get(pk=event_id)
success = retry_failed_event(event)
```

#### get_events_ready_for_retry()

```python
from connectors.fallback import get_events_ready_for_retry

events = get_events_ready_for_retry()
```

### Métodos del modelo

| Método | Descripción |
|--------|-------------|
| `get_max_retries()` | Máximo de reintentos según `FAILED_EVENT_RETRY_CONFIG` |
| `calculate_next_retry()` | Próximo reintento: `now + (60s * 2^retry_count)` |
| `mark_processing()` | `status='retrying'`, actualiza `last_retry_at` |
| `mark_success(interaction_ids)` | `status='processed'`, guarda IDs |
| `mark_failed(error_message, error_trace)` | `status='failed'` |

### Estrategia de reintentos

| Reintento | Retraso | Tiempo acumulado |
|-----------|---------|------------------|
| 1 | ~1 min | 1 min |
| 2 | ~2 min | 3 min |
| 3 | ~4 min | 7 min |
| 4 | ~8 min | 15 min |
| 5 | ~16 min | 31 min |

### Configuración

```python
# settings.py
FAILED_EVENT_RETRY_CONFIG = {
    'web': 5,
    'email': 3,
    'payment': 10,
    'default': 3
}

CELERY_BEAT_SCHEDULE = {
    'retry-failed-events': {
        'task': 'connectors.retry_failed_events',
        'schedule': 300.0,  # 5 minutos
        'options': {'expires': 60.0}
    }
}
```

### Tareas Celery

| Tarea | Nombre | Descripción |
|-------|--------|-------------|
| `retry_failed_events_task` | `connectors.retry_failed_events` | Procesa hasta 50 eventos cada 5 min |
| `retry_single_event_task` | `connectors.retry_single_event` | Reintento manual de un evento |

```python
from connectors.tasks import retry_failed_events_task

result = retry_failed_events_task()
# {'success': 5, 'failed': 2, 'total': 7, 'failure_rate': 0.286}
```

### Clasificación de errores

| Categoría | Ejemplos | Almacenado en fallback | Nivel Sentry |
|-----------|----------|------------------------|--------------|
| Cliente (4xx) | JSON inválido, campos faltantes | No | `warning` |
| Sistema (5xx) | Timeout DB, excepciones inesperadas | Sí | `error` |
| Catastrófico | Fallo de procesamiento y almacenamiento | No (500) | `fatal` |

### Admin de eventos fallidos

**URL:** `/admin/connectors/failedevent/`

Acciones personalizadas:

- Reintentar eventos seleccionados
- Abandonar eventos seleccionados
- Resetear contador de reintentos

### Métricas y alertas

Umbrales recomendados:

| Métrica | Advertencia | Crítico |
|---------|-------------|---------|
| Tamaño de cola | > 100 eventos | > 500 eventos |
| Tasa de fallo | > 10% | > 25% |
| Fallo en lote de reintentos | > 30% | > 50% |
| Fallos catastróficos | > 0 | > 5/hora |

Consultas útiles:

```python
pending_count = FailedEvent.objects.filter(status='pending').count()
processed = FailedEvent.objects.filter(status='processed').count()
total = FailedEvent.objects.count()
success_rate = (processed / total * 100) if total > 0 else 0
```

### Despliegue

```bash
docker compose exec backend python manage.py migrate
docker compose restart backend celery celery-beat
docker compose exec celery celery -A backend inspect registered | grep retry
```

### Solución de problemas

**Eventos atascados en `retrying`:**

```python
stuck_events = FailedEvent.objects.filter(
    status='retrying',
    last_retry_at__lt=timezone.now() - timedelta(minutes=10)
)
stuck_events.update(status='pending', next_retry_at=timezone.now())
```

**Alta tasa de fallos:** identificar patrones de error, corregir causa raíz, resetear reintentos desde admin.

**Cola creciente:** aumentar workers Celery, reducir intervalo de Beat, aumentar tamaño de lote.

---

## Historial del sistema de fallback

> Fecha de release: octubre 2025 | Versión: 1.0

### Archivos nuevos

| Archivo | Descripción |
|---------|-------------|
| `connectors/models.py` | Modelo `FailedEvent` |
| `connectors/fallback.py` | `store_failed_event`, `retry_failed_event`, `get_events_ready_for_retry` |
| `connectors/tasks.py` | Tareas Celery de reintento |
| `connectors/admin.py` | `FailedEventAdmin` |
| `connectors/migrations/0002_failedevent.py` | Migración de tabla |

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `websites/views.py` | Manejo de errores en 8 vistas de eventos |
| `backend/settings.py` | `FAILED_EVENT_RETRY_CONFIG`, `CELERY_BEAT_SCHEDULE` |

Vistas actualizadas: `PageViewEventView`, `PageReadEventView`, `ClickEventView`, `FormSubmitEventView`, `DownloadEventView`, `VideoPlayEventView`, `SearchEventView`, `NewsletterSignupEventView`

### Cambio de comportamiento HTTP

| Antes | Después |
|-------|---------|
| 500 en todos los errores | 202 para errores de sistema |
| Sin reintentos | Reintento automático |
| Errores perdidos | Almacenados en `FailedEvent` |

### Tabla `connectors_failedevent`

Índices en: `status`, `next_retry_at`, `connector_type`

---

## Ejemplos de uso

### Resolución simple

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
    label='Web Page View',
    metadata={'url': '/products/laptop'}
)

touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
```

### E-commerce: página de producto

```python
from connectors.models import TouchpointMappingRule
from websites.models import WebInteraction

TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='shop.example.com',
    event_code='web.page_view',
    touchpoint_code='web.product_page',
    touchpoint_label='Product Page View',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    priority=200,
    is_active=True
)

event_data = {
    'event_type': 'page_view',
    'website_base': 'https://shop.example.com',
    'full_url': 'https://shop.example.com/products/laptop-dell-xps',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'user_agent': 'Mozilla/5.0...',
}

interactions = WebInteraction.process_page_view_event(event_data)
```

### Formulario con UTM

```python
event_data = {
    'event_type': 'form_submit',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/contact',
    'utm_source': 'facebook',
    'utm_medium': 'cpc',
    'utm_campaign': 'lead_gen_2025',
    'user_agent': 'Mozilla/5.0...',
    'payload': {'form_type': 'contact'}
}

interactions = WebInteraction.process_form_submit_event(event_data)
```

### Eventos de app móvil

```python
def process_mobile_event(event_data: dict):
    hint = TouchpointHint(
        code=f"mobile.{event_data['screen_name']}",
        channel_code='mobile_app',
        medium_code='app',
        touchpoint_type_code='mobile_screen',
        label=f"Mobile {event_data['screen_name'].replace('_', ' ').title()}",
        metadata={
            'device_type': event_data.get('device_type'),
            'app_version': event_data.get('app_version'),
        }
    )

    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    touchpoint = resolver.resolve(
        hint,
        connector_type='mobile',
        source_identifier=event_data.get('app_id', 'ios_app')
    )
    # ... crear agent, action, interaction
    return touchpoint
```

### Procesamiento por lotes

```python
from django.db import transaction
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

def process_events_batch(events: list[dict], batch_size: int = 100):
    cached_provider = CachedMappingProvider()
    cached_provider.warm_cache()
    resolver = CachedTouchpointResolver(cached_provider)

    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        with transaction.atomic():
            for event in batch:
                if event['event_type'] == 'page_view':
                    WebInteraction.process_page_view_event(event)
                elif event['event_type'] == 'form_submit':
                    WebInteraction.process_form_submit_event(event)
```

### Webhook con manejo de fallback

```python
import json, traceback
import sentry_sdk
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from connectors.fallback import store_failed_event

@csrf_exempt
def webhook_handler(request):
    try:
        data = json.loads(request.body)
        interactions = WebInteraction.process_page_view_event(data)
        return JsonResponse({'success': True}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
    except Exception as e:
        error_trace = traceback.format_exc()
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('has_fallback', 'true')
            sentry_sdk.capture_exception(e)
        failed_event = store_failed_event(
            connector_type='web',
            event_type='page_view',
            raw_payload=data,
            error_message=str(e),
            error_trace=error_trace,
            source_identifier=data.get('website_base', '')
        )
        return JsonResponse({
            'success': False,
            'error': 'Event processing failed but has been queued for retry',
            'fallback_id': str(failed_event.pk)
        }, status=202)
```

---

## Interfaz de administración

### Interfaces disponibles

| Recurso | URL |
|---------|-----|
| Eventos fallidos | `/admin/connectors/failedevent/` |
| Reglas de mapeo | `/admin/connectors/touchpointmappingrule/` |
| Eventos de resolución | `/admin/connectors/touchpointresolutionevent/` |
| Métricas de resolución | `/admin/connectors/touchpointresolutionmetrics/` |
| Alertas | `/admin/connectors/touchpointalert/` |
| Salud del sistema | `/admin/connectors/touchpointsystemhealth/` |
| Métricas de caché | `/admin/connectors/touchpointcachemetrics/` |

### Vistas personalizadas

| Vista | URL |
|-------|-----|
| Dashboard | `/admin/connectors/touchpointmappingrule/dashboard/` |
| Analítica | `/admin/connectors/touchpointmappingrule/analytics/` |
| Rendimiento | `/admin/connectors/touchpointmappingrule/performance/` |
| Métricas AJAX | `/admin/connectors/touchpointmappingrule/ajax/metrics/` |
| Health check | `/admin/connectors/touchpointmappingrule/health-check/` |

### Reglas de mapeo

Campos clave: `connector_type`, `source_identifier`, `event_code`, `touchpoint_code`, `channel_code`, `medium_code`, `priority`, `is_active`.

Acciones: activar/desactivar en lote, exportar/importar JSON, probar reglas.

### Eventos fallidos

Filtros: tipo de conector, tipo de evento, estado, rango de fechas.  
Búsqueda: ID, `source_identifier`, mensaje de error, `interaction_ids`.

Estados: `pending`, `retrying`, `processed`, `failed`, `abandoned`

### Umbrales de monitoreo

| Métrica | Objetivo |
|---------|----------|
| Tasa de éxito | > 95% |
| Tiempo de resolución | < 100 ms promedio |
| Tasa de acierto de caché | > 80% |
| Tasa de error | < 5% |
| Cola de eventos fallidos | < 100 eventos |

### Mantenimiento recomendado

- **Diario:** alertas, tasa de error, cola de eventos fallidos
- **Semanal:** tendencias de rendimiento, tasa de éxito de reintentos
- **Mensual:** uso de reglas, limpieza de eventos procesados
- **Trimestral:** políticas de retención, configuración de reintentos

---

## Guía de migración v1.0 a v2.0

### Cambios incompatibles

#### 1. Eliminado: TouchpointInferenceProtocol

Antes:

```python
class CustomConnector(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(...)
```

Después:

```python
def build_hint_from_event(event_data: dict) -> TouchpointHint:
    return TouchpointHint(
        code=event_data['event_type'],
        channel_code=event_data['channel'],
        medium_code=event_data.get('medium'),
        touchpoint_type_code=event_data.get('type'),
        label=event_data.get('label', ''),
        metadata=event_data.get('metadata', {})
    )
```

#### 2. Nueva firma del resolver

Antes: `resolver.resolve(subject: TouchpointInferenceProtocol)`  
Después: `resolver.resolve(hint, *, connector_type, source_identifier='')`

#### 3. Nueva firma del mapping provider

Antes: `lookup_mapping(subject, hint)`  
Después: `lookup_mapping(*, connector_type, source_identifier, hint)`

### Pasos de migración

1. Eliminar imports de `TouchpointInferenceProtocol`
2. Reemplazar `infer_touchpoint_hint()` por `build_touchpoint_hint_from_event_data()`
3. Actualizar llamadas a `resolver.resolve()` con la nueva firma
4. Mover resolución de touchpoint **antes** de crear `Interaction`
5. Eliminar clases mock de conectores en tests
6. Actualizar comandos de gestión

### Patrón de procesamiento de eventos

```python
@classmethod
def process_event(cls, event_data: dict):
    hint = cls.build_touchpoint_hint_from_event_data(event_data, website)
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier=website.base_url)
    interaction = Interaction.objects.create(touchpoint=touchpoint, action=action, agent=agent)
    return cls.objects.create(interaction=interaction, ...)
```

### Checklist

- [ ] Eliminar `TouchpointInferenceProtocol`
- [ ] Eliminar `infer_touchpoint_hint()`
- [ ] Añadir `build_touchpoint_hint_from_event_data()`
- [ ] Actualizar `resolver.resolve()` y `lookup_mapping()`
- [ ] Resolución pre-creación de interacciones
- [ ] Actualizar tests y comandos de gestión
- [ ] Ejecutar: `python manage.py test connectors.tests`

---

## Referencia rápida

### Prioridades de reglas de mapeo

| Prioridad | Uso |
|-----------|-----|
| 200+ | Reglas de alta prioridad (campañas específicas) |
| 100-199 | Reglas estándar |
| 50-99 | Reglas de baja prioridad |
| 1-49 | Reglas por defecto |

### Códigos de canal

| Canal | Código |
|-------|--------|
| Web | `web` |
| Email | `email` |
| WhatsApp | `whatsapp` |
| Móvil | `mobile` |
| API | `api` |

### Códigos de medio

| Medio | Código |
|-------|--------|
| Orgánico | `organic` |
| Pagado | `paid` / `cpc` |
| Directo | `direct` |
| Referido | `referral` |
| Social | `social` |
| Email | `email` |
| Newsletter | `newsletter` |

### Códigos de evento

**Web:** `web.page_view`, `web.form_submit`, `web.button_click`, `web.download`

**Email:** `email.open`, `email.click`, `email.bounce`, `email.unsubscribe`

**WhatsApp:** `whatsapp.message_received`, `whatsapp.message_sent`, `whatsapp.media_received`, `whatsapp.media_sent`

### Comandos de gestión

| Comando | Propósito |
|---------|-----------|
| `backfill_touchpoints` | Rellenar touchpoints faltantes |
| `test_touchpoint_resolution` | Probar lógica de resolución |
| `manage_mapping_rules` | CRUD de reglas |
| `manage_touchpoint_cache` | Gestión de caché |
| `monitor_touchpoint_system` | Monitoreo del sistema |
| `cleanup_touchpoint_events` | Limpieza de datos |

### Consejos de rendimiento

```python
# select_related
interactions = Interaction.objects.select_related('touchpoint', 'action', 'agent')

# Resolver con caché
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider
resolver = CachedTouchpointResolver(CachedMappingProvider())
```

### Solución de problemas

```bash
python manage.py test_touchpoint_resolution --connector-type=web --verbose
python manage.py monitor_touchpoint_system --health-check
```

```python
from connectors.monitoring_models import TouchpointResolutionEvent
TouchpointResolutionEvent.objects.filter(error_occurred=True).order_by('-occurred_at')[:10]
```

---

## Pruebas de integración

Guía para la suite de pruebas en `backend/connectors/tests/`.

### Categorías de pruebas

| Archivo | Clases principales | Propósito |
|---------|-------------------|-----------|
| `test_admin_integration.py` | `AdminInterfaceIntegrationTest`, `AdminWorkflowIntegrationTest`, etc. | Admin, CRUD, dashboards, caché |
| `test_management_commands_integration.py` | `ManagementCommandsIntegrationTest`, etc. | Comandos CLI |
| `test_monitoring_integration.py` | `MetricsCollectionIntegrationTest`, `AlertingSystemIntegrationTest`, etc. | Métricas, alertas, retención |
| `test_touchpoint_resolution_integration.py` | `CompleteResolutionWorkflowTest`, `PerformanceIntegrationTest`, etc. | Flujos end-to-end |

### Ejecución

```bash
# Todas las pruebas de connectors
python manage.py test connectors.tests

# Por categoría
python manage.py test connectors.tests.test_admin_integration
python manage.py test connectors.tests.test_management_commands_integration
python manage.py test connectors.tests.test_monitoring_integration
python manage.py test connectors.tests.test_touchpoint_resolution_integration

# Clase específica
python manage.py test connectors.tests.test_touchpoint_resolution_integration.CompleteResolutionWorkflowTest

# Runner personalizado
python manage.py test --testrunner=connectors.tests.test_integration_runner.IntegrationTestRunner
```

### Cobertura verificada

- Registro y CRUD en admin
- Comandos: backfill, reglas, caché, monitoreo, limpieza
- Métricas, alertas, salud del sistema
- Flujos completos de resolución, reglas personalizadas, manejo de errores
- Rendimiento bajo carga y procesamiento concurrente

### Benchmarks de rendimiento

| Métrica | Objetivo |
|---------|----------|
| Tiempo de resolución | < 100 ms promedio |
| Operaciones en lote | < 10 s para 100 ítems |
| Procesamiento concurrente | < 5 s para 50 requests |
| Memoria (suite completa) | < 512 MB |

### Depuración

```bash
python manage.py test --debug-mode --verbosity=2
python manage.py test --parallel
coverage run --source='.' manage.py test connectors.tests
coverage report
```

### Problemas comunes

```bash
# Reset de base de datos de prueba
python manage.py test --keepdb --debug-mode

# Limpiar caché de prueba
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

---

## Captura contextual: integración sales (planificado)

> **Estado:** planificado — no implementado en producción  
> **Importante:** la app `sales` **no está incluida en `INSTALLED_APPS`**. El contenido siguiente documenta diseño y planes de integración futuros con el sistema de touchpoints.

### Contexto

La app `sales` define modelos para oportunidades comerciales, sesiones de venta y listas de contacto. La integración con `connectors` permitiría resolución automática de touchpoints para interacciones comerciales, con canales por división organizacional.

### Estado actual de modelos sales

| Modelo | Descripción | Integración touchpoint |
|--------|-------------|------------------------|
| `SalesOpportunity` | Oportunidad comercial con persona/organización y producto | Sin integración (planificado) |
| `SalesSession` | Subclase de `Interaction`; sesiones de contacto | Creación manual de touchpoint (planificado: resolver automático) |
| `ProductAcquisition` | Subclase de `Interaction`; adquisiciones | Creación manual (planificado) |
| `SalesSource` | Catálogo de fuentes | N/A |
| `ContactList` | Listas filtradas de oportunidades | N/A |

### Estructura de canales

- Cada división tiene un canal de ventas: `"Ventas - {division_name}"`
- Los canales se relacionan con touchpoints, no directamente con interacciones
- Función existente: `get_sales_channel_for_division()`

### Plan de integración (fases)

#### Fase 1: Implementación de protocolo/resolver

- Resolver específico: `SalesTouchpointResolver` (extiende `DefaultTouchpointResolver`)
- Proveedor de mapeo: `SalesMappingProvider`
- Resolución de canal por división
- Integración en `SalesSession` y ciclo de vida de `SalesOpportunity`

#### Fase 2: Reglas de mapeo

- Mapeos por medio de contacto comercial
- Códigos de touchpoint por división
- Mapeos de etapas del embudo

#### Fase 3: Pruebas

- Unitarias: inferencia de hints por medio de contacto, resolución de canal
- Integración: flujos end-to-end de sesiones y oportunidades

#### Fase 4: Documentación y migración

- Migración gradual de creación manual a automática
- Compatibilidad hacia atrás durante transición

### Códigos de touchpoint planificados

```
sales.session.{medium}           # Sesión por medio de contacto
sales.opportunity.{stage}        # Cambios de etapa de oportunidad
sales.acquisition.{product_type} # Adquisiciones de producto
```

### Códigos de canal planificados

```
sales.{division_code}            # Canal por división
sales                            # Canal genérico (fallback)
```

### Prioridad de resolución de canal

1. **División del representante** (máxima prioridad): `sales_{representative_division_code}`
   - Representantes humanos: posición/unidad/equipo en estructura organizacional
   - Agentes IA: metadata, organización representada o división de persona operadora
2. **División del producto** (fallback): `sales_{product_division_code}`
3. **Canal genérico** (mínima prioridad): `sales`

### Soporte de agentes IA

- Agentes con `agent_type='ai'` como representantes válidos
- Asignación de división vía metadata (`division_code`), organización representada o persona operadora
- Metadata adicional: `representative_type`, `agent_type`, `agent_name`, `agent_metadata`

### Estructura de metadata planificada

```json
{
  "opportunity_id": "uuid",
  "representative_id": "uuid",
  "division": "division_name",
  "product_id": "uuid",
  "stage": "opportunity_stage",
  "outcome": "session_outcome"
}
```

### Patrón de resolver específico por app

Patrón establecido para apps que extienden el framework de touchpoints:

#### 1. Resolver específico

```python
# apps/{app_name}/resolvers.py
from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint

class {AppName}TouchpointResolver(DefaultTouchpointResolver):
    """Resolver con lógica específica de la app."""

    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        # Lógica específica de la app (v2.0: parámetros explícitos)
        return super().resolve(hint, connector_type=connector_type, source_identifier=source_identifier)
```

#### 2. Proveedor de mapeo específico

```python
class {AppName}MappingProvider:
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ):
        # Reglas de negocio específicas de la app
        ...
```

#### 3. Integración en modelos

```python
# apps/{app_name}/models.py
from .resolvers import {AppName}TouchpointResolver, {AppName}MappingProvider

class {AppModel}(Interaction):
    def save(self, *args, **kwargs):
        if not self.touchpoint:
            try:
                hint = self.build_touchpoint_hint_from_event_data(...)
                resolver = {AppName}TouchpointResolver({AppName}MappingProvider())
                self.touchpoint = resolver.resolve(
                    hint,
                    connector_type='{app}',
                    source_identifier=...
                )
            except Exception:
                self._create_manual_touchpoint()
        super().save(*args, **kwargs)
```

> **Nota de migración:** la documentación original del patrón referenciaba `TouchpointInferenceProtocol` (v1.0). En v2.0, los hints se construyen desde datos crudos y se pasan explícitamente al resolver.

#### Implementación de referencia: websites

- `WebTouchpointResolver`: análisis UTM, referrer, lógica web
- Resolución de canal específico por sitio
- Detección de app nativa vía user agent

#### Implementación planificada: sales

- `SalesTouchpointResolver`: canales por división, contexto de oportunidad
- `SalesMappingProvider`: reglas comerciales específicas
- Regla de negocio: el canal lo determina la división del representante, no del producto

### Progreso del plan (referencia histórica)

| Paso | Estado |
|------|--------|
| Crear `SalesTouchpointResolver` y `SalesMappingProvider` | Completado (código en repo, app no instalada) |
| Implementar protocolo en `SalesSession` | Completado (código en repo) |
| Touchpoints en ciclo de vida de `SalesOpportunity` | Pendiente |
| Reglas de mapeo por defecto | Pendiente |
| Pruebas comprehensivas | Pendiente |
| Documentación de códigos de touchpoint | Pendiente |

### Criterios de éxito

1. Todas las interacciones comerciales crean touchpoints apropiados
2. Resolución dentro de límites de tiempo aceptables
3. Touchpoints reflejan contexto comercial y división correctamente
4. Código documentado y testeable
5. Funcionalidad existente intacta

### Dependencias

- App `connectors` (este documento)
- App `interactions` (modelos `Interaction`, `Touchpoint`, `Channel`)
- App `our_institution` (estructura de divisiones)
- App `products` (relaciones de producto)

### Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Compatibilidad hacia atrás | Mantener creación manual como fallback |
| Rendimiento | Caché para canales y touchpoints frecuentes |
| Integridad de datos | Validación y manejo de errores en resolución |
| Cobertura de pruebas | Tests unitarios e integración antes de activar en `INSTALLED_APPS` |

---

## Solución de problemas general

### Regla de mapeo no aplicada

- Verificar prioridad de la regla
- Confirmar coincidencia de `source_identifier`
- Confirmar que `is_active=True`

### Resolución lenta

- Revisar rendimiento de base de datos
- Simplificar reglas de mapeo
- Activar caché (`CachedTouchpointResolver`)

### Alta tasa de error

- Revisar logs y Sentry
- Validar calidad de datos de entrada
- Revisar reglas de mapeo

### Comandos de depuración

```bash
python manage.py test_touchpoint_resolution --connector-type=web --verbose
python manage.py monitor_touchpoint_system --health-check
```
