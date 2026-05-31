# App Interactions — detalle técnico

Substrato de customer journey: medios, canales, touchpoints, sesiones e interacciones. El CRM expone lectura; la captura ocurre en apps contextuales y en `websites`/`connectors`.

## Semántica `no_action`

La acción `no_action` representa interacciones **sin acción explícita del usuario**:

1. **Eventos inferidos** — el sistema deduce el hecho (inicio/fin de sesión, lectura de página, abandono, nivel de engagement).
2. **Acciones hacia el usuario** — la organización inicia el contacto (email, SMS, push, llamada, entrega de contenido).

Ejemplo de payload inferido: `inference_reason` en metadata de la interacción.

## Campo `content_type` en Touchpoint

Campo opcional en `Touchpoint` para clasificar el enfoque del contenido:

| Valor | Significado |
|-------|-------------|
| `affinity` | Afinidad |
| `category` | Categoría |
| `product` | Producto |
| `brand` | Marca |

Definido en `interactions/models.py`; visible en Django Admin (listado y filtros).

## API y CRM

- API REST bajo `/api/interactions/`
- CRM HTML: listados de touchpoints e interacciones (solo lectura para interacciones)
- Escritura compartida vía `services.py` — ver [BACKEND_API_PATTERNS.md](../BACKEND_API_PATTERNS.md)

## Tests

- `interactions/tests.py` — API
- `interactions/tests_template_views.py` — vistas HTML
- `interactions/test_factories.py` — datos de prueba

Ver [TESTING.md](../TESTING.md).

## Relacionado

- [interactions/README.md](../../backend/interactions/README.md)
- [websites.md](websites.md)
- [connectors.md](connectors.md)
