# App Interactions — Customer Journey (substrato)

## Propósito

Modela medios, canales, agentes, sesiones, touchpoints e interacciones. Es el **registro sistémico** del journey; no es el destino principal de captura de datos (eso ocurre en `websites`, webhooks y futuras apps de ventas/soporte).

## Modelos principales

- `Medium`, `Channel`, `Action`, `ActionType`, `TouchpointType`
- `Touchpoint` (incluye `content_type` opcional)
- `Agent`, `Session`, `Interaction`

## Superficies

| Superficie | Uso |
|----------|-----|
| API REST | `/api/interactions/` — integraciones y scripts |
| CRM HTML | Lectura de interacciones; CRUD de touchpoints donde aplique |
| Servicios | `services.create_interaction` — escritura compartida |

## Tests

- `tests.py`, `tests_template_views.py`, `test_factories.py`
- Guía: [docs/TESTING.md](../../docs/TESTING.md)

## Documentación

- Detalle: [docs/backend/interactions.md](../../docs/backend/interactions.md)
- Panorama de apps: [docs/APPS.md](../../docs/APPS.md)
- Índices DB: [docs/DATABASE_INDEXES.md](../../docs/DATABASE_INDEXES.md)
