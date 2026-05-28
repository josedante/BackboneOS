# Docker Development Environment - MANDATORY

## CRITICAL: This project REQUIRES Docker Compose

**NO EXCEPTIONS - ALL Django commands MUST run inside Docker containers**

## Quick Start

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
cd backend && npm run tailwind:build   # CRM CSS when templates/styles change
```

Open http://localhost:8000/login/

## Available VS Code Tasks

Use `Ctrl+Shift+P` > "Tasks: Run Task":

- Docker: start full stack
- Django: migrations (in Docker)
- Django: tests (in Docker)

## Architecture

- **Backend**: Django in Docker (port 8000) — HTML CRM + REST API + Admin
- **Database**: PostgreSQL (port 5432)
- **Cache & Broker**: Redis (port 6379)
- **Task Worker**: Celery worker
- **Task Scheduler**: Celery Beat
- **Task Monitor**: Flower (port 5555)
- **Styles**: Tailwind build in `backend/` (`npm run tailwind:build`), not a separate frontend container

## Important Files

- `docker-compose.yml` - Service definitions (backend-only; no Next.js service)
- `docs/operations/DOCKER_DEVELOPMENT.md` - Detailed instructions
- `docs/consolidation/FRONTEND_CONSOLIDATION.md` - UI consolidation status
