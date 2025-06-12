# 🐳 Docker Development Environment - MANDATORY

## ⚠️ CRITICAL: This project REQUIRES Docker Compose

**NO EXCEPTIONS - ALL Django commands MUST run inside Docker containers**

## Quick Start

```bash
# Start the environment (REQUIRED)
docker-compose up -d

# Run migrations (in Docker)
docker-compose exec backend python manage.py migrate

# Start frontend (local)
cd frontend && npm run dev
```

## Available VS Code Tasks

Use `Ctrl+Shift+P` > "Tasks: Run Task":

- 🐳 Docker: Iniciar entorno completo
- 🐳 Django: Migraciones (en Docker)
- 🐳 Django: Tests (en Docker)
- 💻 Frontend: Desarrollo (local)

## Architecture

- **Backend**: Django in Docker container (port 8000)
- **Database**: PostgreSQL in Docker container (port 5432)
- **Cache & Broker**: Redis in Docker container (port 6379)
- **Task Worker**: Celery worker for async processing
- **Task Scheduler**: Celery Beat for periodic tasks
- **Task Monitor**: Flower dashboard (port 5555)
- **Frontend**: Nuxt.js running locally (port 3000)

## Important Files

- `docker-compose.yml` - Service definitions
- `.vscode/tasks.json` - Pre-configured tasks
- `.vscode/DOCKER_DEVELOPMENT.md` - Detailed instructions
- `COPILOT_INSTRUCTIONS.md` - Complete project documentation
