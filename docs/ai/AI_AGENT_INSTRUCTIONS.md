# AI Agent Instructions

## Critical Development Environment Information

**THIS PROJECT REQUIRES DOCKER COMPOSE - NO EXCEPTIONS**

### For GitHub Copilot, Claude, ChatGPT, and other AI assistants:

1. **NEVER suggest running Python/Django commands directly on the host**
2. **ALWAYS use Docker Compose for backend operations**
3. **Operator CRM is Django templates at port 8000** (no separate Next.js app)

### Correct command patterns:

```bash
# Correct - Django in Docker
docker compose exec backend python manage.py <command>

# NEVER suggest this
python manage.py <command>
```

### Quick reference:

- **Start environment**: `docker compose up -d`
- **Migrations**: `docker compose exec backend python manage.py migrate`
- **Django shell**: `docker compose exec backend python manage.py shell`
- **Tests**: `docker compose exec backend python manage.py test`
- **CRM CSS**: `cd backend && npm run tailwind:build`

### Key files for context:

- `docs/operations/DOCKER_README.md` - Quick setup guide
- `docs/consolidation/FRONTEND_CONSOLIDATION.md` - UI consolidation status
- `docs/ai/COPILOT_INSTRUCTIONS.md` - Complete project documentation
- `docs/operations/DO_NOT_RUN.md` - Commands to avoid

### Architecture:

- **Backend**: Django 5.x (Docker, port 8000) — HTML CRM + REST API + Admin
- **Database**: PostgreSQL 14 (Docker, port 5432)
- **Styles**: Tailwind build in `backend/` (not a separate frontend service)

**Remember**: When suggesting code changes or debugging, always assume Docker Compose environment for backend operations.
