# BackboneOS - Servicios de Infraestructura

## Resumen de Servicios

| Servicio       | Puerto | Función                          | URL                     |
| -------------- | ------ | -------------------------------- | ----------------------- |
| Django Backend | 8000   | CRM HTML + API REST + Admin      | http://localhost:8000   |
| PostgreSQL     | 5432   | Base de Datos                    | localhost:5432          |
| Redis          | 6379   | Cache + Broker                   | localhost:6379          |
| Celery Worker  | -      | Tareas Asíncronas                | (background)            |
| Celery Beat    | -      | Tareas Programadas               | (background)            |
| Flower         | 5555   | Monitor Celery                   | http://localhost:5555   |

## URLs de Acceso Rápido

```bash
open http://localhost:8000/          # CRM (login en /login/)
open http://localhost:8000/admin/    # Django Admin (usuarios)
open http://localhost:5555/          # Flower
curl http://localhost:8000/api/      # API REST
```

## Comandos de Inicio Rápido

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
cd backend && npm run tailwind:build   # si cambiaste estilos del CRM
open http://localhost:8000/login/
```

Ver [DOCKER_README.md](operations/DOCKER_README.md) y [FRONTEND_CONSOLIDATION.md](consolidation/FRONTEND_CONSOLIDATION.md).
