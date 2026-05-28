# Componentes del CRM (Plantillas Django)

> El paquete Next.js `frontend/` se eliminó en la Fase 6 de la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md). El CRM de operador se renderiza con **plantillas Django** servidas por el mismo proceso que la API REST. Este documento describe esa interfaz; no hay componentes React/SPA.

## Visión general

La interfaz es **server-rendered** con herencia de plantillas de Django. No existe un bundle de JavaScript de aplicación: el único JS es un pequeño script inline para abrir/cerrar el sidebar en móvil ([`base_dashboard.html`](../backend/templates/base_dashboard.html)).

> HTMX y Alpine.js están permitidos por la regla de arquitectura ([`.cursor/rules/consolidated-frontend.mdc`](../.cursor/rules/consolidated-frontend.mdc)) para hidratación dinámica futura, pero **no se usan actualmente**.

## Layout base

### `base_dashboard.html`

**Ubicación**: [`backend/templates/base_dashboard.html`](../backend/templates/base_dashboard.html)

Layout raíz del que extienden todas las páginas del CRM. Define el shell (sidebar + main), carga el CSS compilado y expone los bloques de extensión.

```django
{% extends "base_dashboard.html" %}

{% block title %}Products{% endblock %}

{% block content %}
  <!-- contenido de la página -->
{% endblock %}
```

**Bloques disponibles**:

| Bloque | Propósito |
|--------|-----------|
| `title` | `<title>` del documento |
| `extra_head` | CSS/meta adicionales en `<head>` |
| `content` | Contenido principal de la página |
| `extra_js` | Scripts al final del `<body>` |

**Características**:

- Carga un único stylesheet: `{% static 'dist/styles.css' %}` (Tailwind compilado en build).
- Renderiza los flash messages de `django.contrib.messages` (ver más abajo).
- Incluye `includes/sidebar.html` y `includes/header.html`.
- Script inline para el toggle del sidebar en móvil (overlay + clases `is-open`/`is-visible`).

### `includes/sidebar.html`

**Ubicación**: [`backend/templates/includes/sidebar.html`](../backend/templates/includes/sidebar.html)

Navegación principal. Los enlaces usan `{% url %}` con los namespaces HTML de cada app y marcan el estado activo comparando `request.resolver_match`.

| Ítem | Destino | Estado |
|------|---------|--------|
| Dashboard | `dashboard:home` | activo por `view_name` |
| Users | `admin:index` (Django Admin) | — |
| Products | `products_html:list` | activo por `namespace` |
| Entities | `entities_html:list` | activo por `namespace` |
| Interactions | `interactions_html:list` | activo por `namespace` |
| Campaigns | `campaigns_html:list` | activo por `namespace` |
| Offers | `offers_html:list` | activo por `namespace` |
| Analytics | `#` (`is-disabled`) | "Coming soon" |
| Settings | `#` (`is-disabled`) | "Coming soon" |

Ejemplo del patrón de estado activo:

```django
<a href="{% url 'products_html:list' %}"
   class="{% if request.resolver_match.namespace == 'products_html' %}is-active{% endif %}">
  Products
</a>
```

### `includes/header.html`

**Ubicación**: [`backend/templates/includes/header.html`](../backend/templates/includes/header.html)

Barra superior con el botón de menú (móvil), el título de página y el bloque de usuario.

- **Título**: `{{ page_title|default:"Dashboard" }}` — las vistas pasan `page_title` en el contexto.
- **Usuario**: `{{ user.get_full_name|default:user.username }}` cuando `user.is_authenticated`.
- **Logout**: formulario `POST` a `{% url 'logout' %}` con `{% csrf_token %}` (no es un enlace GET).

## Flash messages

Los mensajes se emiten desde las vistas con `django.contrib.messages` y se renderizan en `base_dashboard.html`:

```django
{% if messages %}
<ul class="dashboard-messages" role="status">
  {% for message in messages %}
  <li class="dashboard-message dashboard-message-{{ message.tags|default:'info' }}">{{ message }}</li>
  {% endfor %}
</ul>
{% endif %}
```

En las vistas:

```python
from django.contrib import messages
messages.success(request, "Producto creado.")
```

## Plantillas por app

Cada app con CRM coloca sus plantillas bajo `<app>/templates/<app>/` y todas extienden `base_dashboard.html`.

| App | Plantillas | Notas |
|-----|------------|-------|
| dashboard | `dashboard/home.html` | Home del CRM |
| products | `list.html`, `create.html`, `detail.html` | Filtros, paginación, edición con `<details>` |
| entities | `list.html`, `person_create.html`, `person_detail.html`, `organization_create.html`, `organization_detail.html`, `_interactions_timeline.html` | Lista con tabs (people/organizations); timeline incluido |
| interactions | `list.html`, `interaction_detail.html` (solo lectura), `touchpoint_create.html`, `touchpoint_detail.html`, `_touchpoint_form_fields.html` | Substrato: interacciones de solo lectura + config de touchpoints |
| campaigns | `list.html`, `create.html`, `detail.html`, `touchpoint_create.html`, `touchpoint_detail.html` | CRUD de operador + enlaces campaña–touchpoint |
| offers | `list.html`, `create.html`, `detail.html` | CRUD de operador con overview cards |

### Parciales

Las plantillas reutilizables empiezan con guion bajo y se incluyen con `{% include %}`:

- `entities/_interactions_timeline.html` — timeline de interacciones en el detalle de persona/organización.
- `interactions/_touchpoint_form_fields.html` — campos compartidos del formulario de touchpoint.

## Formularios

La captura de datos usa **formularios Django** (`forms.py` por app). Las vistas validan el formulario y delegan la escritura en `services.py` (ver [BACKEND.md](BACKEND.md#-capa-de-servicios-y-selectores)); las plantillas no hacen peticiones a la API.

```python
# Patrón típico en template_views.py
form = ProductForm(request.POST)
if form.is_valid():
    product = create_product(**form.cleaned_data)   # services.py
    messages.success(request, "Producto creado.")
    return redirect("products_html:detail", pk=product.pk)
```

## Estilos

- **Fuente**: [`backend/static/src/input.css`](../backend/static/src/input.css) — tokens estilo shadcn + layout del dashboard.
- **Salida**: `backend/static/dist/styles.css`, compilada con la CLI de Tailwind (`npm run tailwind:build`). Está en `.gitignore`; se genera en build o en el host durante desarrollo.
- **Convención por app**: cada app añade un bloque comentado en `input.css`, p. ej. `/* Products CRM */`, `/* Entities CRM */`, `/* Interactions CRM */`, `/* Campaigns CRM */`, `/* Offers CRM */` (tablas, formularios, badges, secciones `<details>`).

Clases principales del layout: `dashboard-shell`, `dashboard-sidebar`, `dashboard-main`, `dashboard-header`, `dashboard-content`, `dashboard-messages`, estados `is-active`/`is-open`/`is-disabled`.

## Toolchain Tailwind

```bash
cd backend
npm install
npm run tailwind:build    # escribe static/dist/styles.css (minificado)
npm run tailwind:watch    # rebuild en desarrollo
```

En producción, `Dockerfile.prod` ejecuta `npm ci`, `tailwind:build` y `collectstatic` en la fase builder; el runtime sigue siendo un único proceso Python. En `docker-compose` dev, el montaje `./backend:/app` sobreescribe el `dist/` de la imagen, así que conviene ejecutar `tailwind:build`/`tailwind:watch` en el host al cambiar estilos.

## Testing

Las vistas HTML se prueban con `tests_template_views.py` por app (y `test_factories.py` para datos). Ver [TESTING.md](TESTING.md).

---

> Para la API REST consumida por integraciones externas, ver [FRONTEND_API.md](FRONTEND_API.md) y [API.md](API.md). Para el historial de migración, ver [FRONTEND_CONSOLIDATION.md](consolidation/FRONTEND_CONSOLIDATION.md).
