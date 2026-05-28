# Infraestructura de Testing - BackboneOS

> Tras la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md), el proyecto es un único proceso Django (API REST + CRM HTML). El testing es **Django/pytest**; la antigua suite de frontend (Vitest/React) se eliminó junto con el paquete Next.js.

## Stack de Testing

- **Django TestCase**: tests de modelos, API y vistas HTML
- **pytest**: runner de tests de Python
- **factory_boy**: generación de datos de prueba (`test_factories.py` por app)
- **Coverage.py**: análisis de cobertura
- **Configuración de tests**: `backend.test_settings` (SQLite + almacenamiento de estáticos simple)

## Organización de Tests

Cada app coloca sus tests junto al código. Las apps con CRM añaden tests de vistas HTML y factories:

```
backend/
├── users/tests.py
├── world/tests.py
├── entities/tests.py
├── entities/tests_template_views.py     # vistas HTML del CRM
├── entities/test_factories.py           # factory_boy
├── our_institution/tests.py
├── products/tests.py
├── products/tests_template_views.py
├── interactions/tests.py
├── interactions/tests_template_views.py
├── interactions/test_factories.py
├── campaigns/tests.py
├── campaigns/tests_template_views.py
├── campaigns/test_factories.py
├── offers/tests.py
├── offers/tests_template_views.py
├── offers/test_factories.py
└── dashboard/tests.py
```

| Tipo | Archivo | Cubre |
|------|---------|-------|
| API | `tests.py` | ViewSets DRF, serializers, permisos |
| CRM HTML | `tests_template_views.py` | vistas de plantilla: login requerido, render, POST de formularios, redirecciones |
| Datos | `test_factories.py` | factories `factory_boy` reutilizables |

## Ejecutar Tests

### Todos los tests

```bash
docker compose run --rm \
  -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test
```

### App específica / subconjunto

```bash
# App completa
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test campaigns

# Solo las vistas HTML de una app
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test products.tests_template_views
```

### Cobertura

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  sh -c "coverage run manage.py test && coverage report"
```

## Gate consolidado (CRM)

El gate de regresión usado durante la consolidación cubre dashboard + las vistas HTML de interactions, entities, campaigns y offers (más subconjuntos de API). Reporta **67 tests, OK**:

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test \
    dashboard.tests \
    products.tests.ProductsAPITests products.tests_template_views \
    entities.tests.PersonAPITest entities.tests.OrganizationAPITest \
    entities.tests.PersonViewSetTests entities.tests.OrganizationViewSetTests \
    entities.tests_template_views \
    interactions.tests.InteractionAPITests interactions.tests.TouchpointAPITests \
    interactions.tests_template_views \
    campaigns.tests campaigns.tests_template_views \
    offers.tests offers.tests_template_views
```

`python manage.py check` no debe reportar incidencias.

## Qué verifican los tests de vistas HTML

Los `tests_template_views.py` cubren, por app, el contrato del CRM:

- **Autenticación**: las páginas requieren login (`@login_required`).
- **Render**: la vista responde 200 y usa la plantilla correcta que extiende `base_dashboard.html`.
- **Escritura**: los POST válidos invocan `services.py`, persisten FK/M2M y muestran flash + redirect.
- **Substrato (interactions)**: no hay rutas de create/edit/delete de interacciones (solo lectura); sí existen para touchpoints.
- **API intacta**: los subconjuntos de `tests.py` confirman que `/api/...` no cambió.

## Deuda de tests conocida (no bloqueante)

- Suite completa de `products`: fixtures de Division y drift de JSON de analytics.
- Los tests HTML usan `backend.test_settings` (SQLite + staticfiles simple).

## Documentación de testing del backend

Guías operativas más detalladas viven junto al backend:

- [`backend/TESTING.md`](../backend/TESTING.md) - guía de testing del backend
- [`backend/DOCKER_TESTING.md`](../backend/DOCKER_TESTING.md) - testing dentro de Docker
- [`backend/TESTING_STATUS.md`](../backend/TESTING_STATUS.md) - estado/resultados

## CI (planificado)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r backend/requirements.txt
      - run: |
          cd backend
          DJANGO_SETTINGS_MODULE=backend.test_settings python manage.py test
```

---

> Relacionado: [BACKEND.md](BACKEND.md) (capa selectors/services), [FRONTEND_COMPONENTS.md](FRONTEND_COMPONENTS.md) (CRM), [FRONTEND_CONSOLIDATION.md](consolidation/FRONTEND_CONSOLIDATION.md) (historial).
