# Docker Development Setup

Tras la [consolidación del frontend](../consolidation/FRONTEND_CONSOLIDATION.md), el proyecto corre como un **único proceso Django** (API REST + CRM HTML) más PostgreSQL, Redis y Celery. No existe un servicio de frontend separado.

## Development Setup

```bash
# Levantar todos los servicios (backend, db, redis, celery)
docker-compose up -d

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Compilar el CSS del CRM cuando cambien los estilos
cd backend && npm run tailwind:build   # o npm run tailwind:watch
```

El setup de desarrollo usa:
- `backend/Dockerfile` con montaje de volumen (`./backend:/app`) para cambios en caliente del código Python.
- Variables de entorno de desarrollo desde `.env`.

> Nota: como `docker-compose` monta `./backend:/app`, se sobreescribe el `static/dist/` construido en la imagen. Ejecuta `npm run tailwind:build` (o `tailwind:watch`) en el host al cambiar estilos.

## Production Setup

```bash
# Producción
docker-compose -f docker-compose.prod.yml up -d --build
```

El setup de producción usa:
- `backend/Dockerfile.prod`: la fase builder ejecuta `npm ci`, `npm run tailwind:build` y `collectstatic`.
- Sin montaje de volumen (usa la imagen construida).
- Runtime: un único proceso Python; los estáticos se sirven con WhiteNoise.

## Diferencias clave

| Feature | Development | Production |
|---------|-------------|------------|
| Dockerfile | `Dockerfile` | `Dockerfile.prod` |
| Hot reloading (Python) | ✅ Sí (volumen) | ❌ No |
| Volume mounting | ✅ Sí | ❌ No |
| Tailwind | `tailwind:build`/`watch` en host | compilado en build |
| Estáticos | `dist/` montado | `collectstatic` + WhiteNoise |

## Variables de entorno

Ver [`.env.example`](../../.env.example). Variables relevantes del backend: `DEBUG`, `SECRET_KEY`, `DATABASE_*`, `DJANGO_REDIS_URL`, `CELERY_*`, `CORS_ALLOWED_ORIGINS` (solo para clientes externos de la API; el CRM es same-origin).
