# Comandos Útiles para el Proyecto Django (API + CRM HTML) + PostgreSQL

## Docker Commands

### Gestión de Contenedores

```bash
# Ejecutar todos los servicios
docker-compose up

# Ejecutar en background
docker-compose up -d

# Reconstruir contenedores
docker-compose up --build

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f redis
docker-compose logs -f celery
docker-compose logs -f celery-beat
docker-compose logs -f flower
```

### Servicios de Infraestructura

```bash
# Redis commands
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli info
docker-compose exec redis redis-cli monitor

# Celery commands
docker-compose exec backend celery -A backend inspect active
docker-compose exec backend celery -A backend inspect stats
docker-compose exec backend celery -A backend status
docker-compose exec backend celery -A backend inspect registered

# Flower dashboard
open http://localhost:5555
```

### Django Commands

```bash
# Ejecutar comandos Django dentro del contenedor
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py shell

# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Ejecutar tests
docker-compose exec backend python manage.py test
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U myuser -d mydatabase

# Crear backup
docker-compose exec db pg_dump -U myuser mydatabase > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U myuser mydatabase < backup.sql
```

## Desarrollo Local

### Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### CRM styles (Tailwind in backend)

```bash
cd backend
npm install
npm run tailwind:build
npm run tailwind:watch
```

## URLs Importantes

- CRM: http://localhost:8000/
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin
- Usuarios API: http://localhost:8000/api/users/

## Solución de Problemas

### Puerto ocupado

```bash
# Verificar qué proceso usa el puerto (backend único en :8000)
lsof -ti:8000

# Matar proceso en puerto específico
kill -9 $(lsof -ti:8000)
```

### Problemas con Docker

```bash
# Limpiar contenedores y imágenes
docker-compose down --volumes --rmi all
docker system prune -f

# Reconstruir desde cero
docker-compose build --no-cache
```

### Reset de Base de Datos

```bash
# Eliminar volumen de PostgreSQL
docker-compose down -v
docker volume rm proyecto-opensource_postgres_data
docker-compose up --build
```
