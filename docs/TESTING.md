# Infraestructura de Testing - BackboneOS

> Tras la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md), el proyecto es un único proceso Django (API REST + CRM HTML). El testing es **Django/pytest**; la antigua suite de frontend (Vitest/React) se eliminó junto con el paquete Next.js.

## Stack de testing

- **Django TestCase / pytest**: modelos, API, vistas HTML
- **pytest-django**: integración con Django
- **factory_boy**: datos de prueba (`test_factories.py` por app)
- **Coverage.py**: cobertura (umbral por defecto 80 % en scripts)
- **Configuración**: `DJANGO_SETTINGS_MODULE=backend.test_settings` (SQLite + estáticos simples)
- **Docker tests**: `backend.docker_test_settings` vía `docker-compose.test.yml` y `run_tests_docker.sh`

## Organización de tests

Cada app coloca sus tests junto al código. Las apps con CRM añaden tests de vistas HTML y factories:

```
backend/
├── users/tests.py
├── world/tests.py
├── entities/tests.py
├── entities/tests_template_views.py
├── entities/test_factories.py
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
├── dashboard/tests.py
├── websites/tests/
└── connectors/tests/
```

| Tipo | Archivo | Cubre |
|------|---------|-------|
| API | `tests.py` | ViewSets DRF, serializers, permisos |
| CRM HTML | `tests_template_views.py` | login, render, POST, redirects |
| Datos | `test_factories.py` | factories reutilizables |
| Integración | `tests/` (p. ej. connectors) | flujos end-to-end |

## Ejecutar tests

### Recomendado: Docker aislado

Desde `backend/`:

```bash
./run_tests_docker.sh --coverage --html-report
./run_tests_docker.sh --type unit --coverage
./run_tests_docker.sh --app users --coverage
./run_tests_docker.sh --parallel --workers 8
./run_tests_docker.sh --interactive
```

Opciones principales (`./run_tests_docker.sh --help`):

| Opción | Descripción |
|--------|-------------|
| `-t, --type` | `unit`, `integration`, `api`, `performance`, `smoke`, `all` |
| `-c, --coverage` | Cobertura |
| `-p, --parallel` | Paralelo |
| `-a, --app` | App concreta |
| `-m, --markers` | Marcadores pytest |
| `-h, --html-report` | Informe HTML de cobertura |
| `-f, --fail-under` | Umbral mínimo (default 80) |

Usa `docker-compose.test.yml` (PostgreSQL y Redis de test en puertos dedicados).

### Compose de desarrollo (rápido)

```bash
docker compose run --rm \
  -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test
```

App o módulo concreto:

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test campaigns

docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test products.tests_template_views
```

### Runner local (`backend/`)

Con dependencias instaladas en el host:

```bash
./run_tests.sh --coverage --html-report
./run_tests.sh --type api --parallel --workers 8
./run_tests.sh --app users --coverage
```

### Comando de gestión Django

```bash
docker compose exec backend python manage.py run_tests --type=unit
docker compose exec backend python manage.py run_tests --coverage --html-report
docker compose exec backend python manage.py test_coverage
```

### pytest directo

```bash
cd backend
DJANGO_SETTINGS_MODULE=backend.test_settings pytest
DJANGO_SETTINGS_MODULE=backend.test_settings pytest --cov=. --cov-report=html
```

## Cobertura

```bash
cd backend
./run_tests_docker.sh --coverage --html-report --xml-report
# o
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  sh -c "coverage run manage.py test && coverage report"
```

Los informes HTML/XML se generan según flags del script; revisar salida del comando para la ruta exacta.

## Gate consolidado (CRM)

Subconjunto usado durante la consolidación del frontend (dashboard + CRM HTML + APIs clave):

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

## Contrato de tests HTML del CRM

Los `tests_template_views.py` verifican por app:

- **Autenticación**: `@login_required` en páginas del CRM.
- **Render**: 200 y plantilla que extiende `base_dashboard.html`.
- **Escritura**: POST válidos llaman `services.py`, persisten relaciones y redirigen.
- **Substrato (interactions)**: interacciones solo lectura; touchpoints con CRUD donde aplique.
- **API**: subconjuntos de `tests.py` confirman que `/api/...` no regresó.

## Datos de prueba (desarrollo)

Scripts en la raíz de `backend/` para poblar datos de demo (usuarios, productos, entidades, campañas, ofertas). Ejemplos:

```bash
docker compose exec backend python manage.py create_organization_structure
docker compose exec backend python create_offers_data.py
docker compose exec backend python create_campaigns_data.py
```

Usuarios de prueba típicos (si los crea el script de setup): `admin`, `manager`, `sales`, `marketing` con contraseña documentada en el script correspondiente.

## Deuda conocida (no bloqueante)

- Suite completa de `products`: fixtures de Division y drift de JSON de analytics.
- Cobertura global: ejecutar `./run_tests_docker.sh --coverage` para métricas actuales (no mantener cifras fijas en documentación).
- Gaps de `websites`: ver [backend/websites.md](backend/websites.md#deuda-viva-de-pruebas).

## Troubleshooting Docker

| Problema | Acción |
|----------|--------|
| Servicios test no listos | Reintentar; revisar `docker compose -f docker-compose.test.yml ps` |
| Puerto en uso | Ajustar puertos en `docker-compose.test.yml` |
| BD de test corrupta | Ejecutar sin `--keep-db` o limpiar volúmenes de test |

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

## Estado de la suite

No se publican contadores fijos en esta guía. Para el estado actual:

```bash
cd backend && ./run_tests_docker.sh --coverage
```

---

> Relacionado: [BACKEND.md](BACKEND.md), [backend/README.md](../backend/README.md), [FRONTEND_COMPONENTS.md](FRONTEND_COMPONENTS.md), [tracking/README.md](tracking/README.md).
