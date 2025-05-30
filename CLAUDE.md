# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a full-stack application with a Django REST Framework backend and Nuxt.js 3 frontend, using PostgreSQL as the database. The project is containerized with Docker.

### Key Components

- **Backend**: Django 5.2.1 + DRF in `backend/` directory

  - Main Django project: `backend/backend/` (settings, urls, wsgi)
  - Main application: `backend/myapp/` (models, views, serializers)
  - Uses PostgreSQL with django-cors-headers for CORS
  - JWT authentication with djangorestframework-simplejwt
  - Token-based authentication with DRF is available, too
  - API endpoints under `/api/`

- **Frontend**: Nuxt.js 3 + TypeScript in `frontend/` directory

  - Uses modern Nuxt 3 features with auto-imports
  - API services in `src/services/` communicate with Django backend
  - Components in `src/components/`

- **Database**: PostgreSQL 14 containerized
  - Default credentials: `myuser`/`mypassword`/`mydatabase`

## Essential Commands

### Docker Development (Primary workflow)

```bash
# Start all services with rebuild
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Quick start script
./start.sh
```

### Django Backend Commands

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend python manage.py test

# Django shell
docker-compose exec backend python manage.py shell
```

### Frontend Commands

```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview build
```

### Database Commands

```bash
# Access PostgreSQL
docker-compose exec db psql -U myuser -d mydatabase

# Create backup
docker-compose exec db pg_dump -U myuser mydatabase > backup.sql
```

## Development URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin

## Configuration

- Environment variables defined in `.env` (copy from `.env.example`)
- Django settings use python-decouple for configuration
- CORS configured for frontend-backend communication
- Database host is `db` within Docker network, `localhost` for local development
