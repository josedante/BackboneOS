# Backend Django — BackboneOS

Punto de entrada para desarrollar y probar el backend. La documentación canónica vive en [`docs/`](../docs/).

## Requisitos

- Docker y Docker Compose ([`docker-compose.yml`](../docker-compose.yml))
- Variables de entorno: copiar [`.env.example`](../.env.example) a `.env`

## Arranque

```bash
# Desde la raíz del repositorio
docker compose up -d
docker compose exec backend python manage.py migrate
```

Estilos del CRM (Tailwind): ver [Desarrollo con Docker](../docs/operations/DOCKER_DEVELOPMENT.md).

```bash
cd backend && npm run tailwind:build
```

## Tests

Guía completa: [docs/TESTING.md](../docs/TESTING.md).

```bash
cd backend

# Entorno Docker aislado (recomendado)
./run_tests_docker.sh --coverage --html-report

# Tipos y apps concretas
./run_tests_docker.sh --type unit --coverage
./run_tests_docker.sh --app users --coverage

# Runner local (requiere dependencias instaladas)
./run_tests.sh --coverage --html-report
```

## Documentación

| Tema | Enlace |
|------|--------|
| Arquitectura backend | [docs/BACKEND.md](../docs/BACKEND.md) |
| Testing | [docs/TESTING.md](../docs/TESTING.md) |
| API REST | [docs/API.md](../docs/API.md) |
| Aplicaciones Django | [docs/APPS.md](../docs/APPS.md) |
| Tracking web | [docs/tracking/README.md](../docs/tracking/README.md) |
| Websites (detalle) | [docs/backend/websites.md](../docs/backend/websites.md) |
| Connectors (detalle) | [docs/backend/connectors.md](../docs/backend/connectors.md) |
| Índice completo | [docs/NAVIGATION.md](../docs/NAVIGATION.md) |

## Aplicaciones instaladas

| App | README | Rol |
|-----|--------|-----|
| `core` | — | Comandos de gestión compartidos |
| `users` | [users/README.md](users/README.md) | Autenticación y usuarios |
| `world` | [world/README.md](world/README.md) | Ontología y taxonomías |
| `entities` | [entities/README.md](entities/README.md) | Personas y organizaciones |
| `our_institution` | [our_institution/README.md](our_institution/README.md) | Estructura organizacional |
| `products` | [products/README.md](products/README.md) | Catálogo comercial |
| `interactions` | [interactions/README.md](interactions/README.md) | Customer journey (substrato) |
| `offers` | [offers/README.md](offers/README.md) | Ofertas comerciales |
| `campaigns` | [campaigns/README.md](campaigns/README.md) | Campañas comerciales |
| `websites` | [websites/README.md](websites/README.md) | Tracking e interacciones web |
| `connectors` | [connectors/README.md](connectors/README.md) | Resolución de touchpoints |
| `dashboard` | — | Home del CRM y layout |

**No instalada:** `sales/` (captura contextual planificada). Ver [docs/backend/connectors.md](../docs/backend/connectors.md).
