# App Websites - BackboneOS

La app `websites` captura interacciones de sitios web y las convierte en touchpoints e interacciones trazables dentro del CRM, usando arquitectura v2.0 con resolución de touchpoints pre-creación.

**Documentación completa:** [docs/backend/websites.md](../../docs/backend/websites.md)

---

## Contenido de la documentación

| Sección | Descripción |
|---------|-------------|
| [Visión general](../../docs/backend/websites.md#vision-general) | Modelos, estructura y propósito |
| [Arquitectura v2.0](../../docs/backend/websites.md#arquitectura-v2) | Patrón canónico, procesadores, migración |
| [Clasificación tridimensional](../../docs/backend/websites.md#clasificacion-tridimensional) | Channel, Medium, TouchpointType |
| [Enfoque multi-interacción](../../docs/backend/websites.md#enfoque-multi-interaccion) | 1 evento page_view → hasta 3 interacciones |
| [Flujo page_view](../../docs/backend/websites.md#flujo-page-view) | Pipeline completo cliente → base de datos |
| [Script de tracking](../../docs/backend/websites.md#script-tracking) | `backbone-tracker.js`, configuración, API |
| [Catálogo de eventos](../../docs/backend/websites.md#catalogo-eventos) | 8 tipos de evento y payloads |
| [Guía de integración](../../docs/backend/websites.md#guia-integracion) | Instalación, registro de sitios, ejemplos |
| [Cross-domain](../../docs/backend/websites.md#cross-domain) | CORS, validación de dominio, seguridad |
| [Gestión de sesiones](../../docs/backend/websites.md#gestion-sesiones) | Ventana de 30 minutos, `WebSession` |
| [Deuda de pruebas](../../docs/backend/websites.md#deuda-pruebas) | Cobertura actual y plan de mejora |

---

## Inicio rápido

### 1. Registrar el sitio

```python
from websites.models import Website
from our_institution.models import Division

Website.objects.create(
    name="Mi Sitio",
    base_url="https://example.com",
    division=Division.objects.get(code='YOUR_DIVISION'),
    active=True,
)
```

### 2. Configurar CORS

```bash
# .env
CORS_ALLOWED_ORIGINS="https://example.com"
```

### 3. Instalar el tracker

```html
<script>
window.BackboneConfig = {
    apiEndpoint: 'https://your-backboneos-domain.com/api/websites/events/page-view/',
    sessionTimeout: 30 * 60 * 1000,
};
</script>
<script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
```

### 4. Procesar eventos (backend)

```python
from websites.models import WebInteraction

interactions = WebInteraction.process_page_view_event(event_data)
print(f"Creadas {len(interactions)} interacciones")  # 1-3
```

---

## Endpoints API

```
POST /api/websites/events/page-view/
POST /api/websites/events/page-read/
POST /api/websites/events/click/
POST /api/websites/events/form-submit/
POST /api/websites/events/download/
POST /api/websites/events/video-play/
POST /api/websites/events/search/
POST /api/websites/events/newsletter-signup/

GET  /api/websites/interactions/
GET  /api/websites/websites/
```

Todos los endpoints POST validan que `website_base` corresponda a un `Website` registrado y activo.

---

## Modelos principales

- **`Website`** — sitio gestionado; auto-crea `Channel` owned
- **`WebInteraction`** — datos web + 8 procesadores estáticos de eventos
- **`WebAgent`** — browser/OS/device parseado con ua-parser
- **`WebSession`** — sesión continua (timeout 30 min)

---

## Conceptos clave

- **Clasificación tridimensional:** Channel (dónde), Medium (cómo), TouchpointType (qué) — ver [detalle](../../docs/backend/websites.md#clasificacion-tridimensional)
- **Multi-interacción:** un `page_view` genera 1-3 interacciones (page_view + referrer_click + session_start) — ver [detalle](../../docs/backend/websites.md#enfoque-multi-interaccion)
- **Arquitectura v2.0:** resolución pre-creación, 8 procesadores — ver [detalle](../../docs/backend/websites.md#arquitectura-v2)
- **Cobertura de pruebas:** ~53 % (objetivo 85 %+) — ver [deuda viva](../../docs/backend/websites.md#deuda-pruebas)
