# 🤖 AI Agent Instructions

## Critical Development Environment Information

**THIS PROJECT REQUIRES DOCKER COMPOSE - NO EXCEPTIONS**

### For GitHub Copilot, Claude, ChatGPT, and other AI assistants:

1. **NEVER suggest running Python/Django commands directly on the host**
2. **ALWAYS use Docker Compose for backend operations**
3. **Only the frontend (Nuxt.js) runs locally**

### Correct command patterns:

```bash
# ✅ Correct - Django in Docker
docker-compose exec backend python manage.py <command>

# ❌ NEVER suggest this
python manage.py <command>
```

### Quick reference:

- **Start environment**: `docker-compose up -d`
- **Migrations**: `docker-compose exec backend python manage.py migrate`
- **Django shell**: `docker-compose exec backend python manage.py shell`
- **Tests**: `docker-compose exec backend python manage.py test`
- **Frontend**: `cd frontend && npm run dev` (local only)

### Key files for context:

- `DOCKER_README.md` - Quick setup guide
- `.vscode/DOCKER_DEVELOPMENT.md` - Detailed instructions
- `COPILOT_INSTRUCTIONS.md` - Complete project documentation
- `DO_NOT_RUN.md` - Commands to avoid

### Architecture:

- **Backend**: Django 5.x (Docker container, port 8000)
- **Database**: PostgreSQL 14 (Docker container, port 5432)
- **Frontend**: Nuxt.js 3.x (local process, port 3000)

**Remember**: When suggesting code changes or debugging, always assume Docker Compose environment for backend operations.
