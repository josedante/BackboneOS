# 🚀 BackboneOS - Servicios de Infraestructura

## 📋 Resumen de Servicios

| Servicio       | Puerto | Función             | URL                   |
| -------------- | ------ | ------------------- | --------------------- |
| Django Backend | 8000   | API REST + Admin    | http://localhost:8000 |
| Nuxt Frontend  | 3000   | Interfaz de Usuario | http://localhost:3000 |
| PostgreSQL     | 5432   | Base de Datos       | localhost:5432        |
| Redis          | 6379   | Cache + Broker      | localhost:6379        |
| Celery Worker  | -      | Tareas Asíncronas   | (background)          |
| Celery Beat    | -      | Tareas Programadas  | (background)          |
| Flower         | 5555   | Monitor Celery      | http://localhost:5555 |

## 🎯 URLs de Acceso Rápido

```bash
# Interfaces Web
open http://localhost:3000    # Frontend (Nuxt.js)
open http://localhost:8000/admin  # Django Admin
open http://localhost:5555    # Flower Dashboard

# APIs
curl http://localhost:8000/api/    # Backend API
```

## ⚡ Comandos de Inicio Rápido

### Desarrollo Completo

```bash
# 1. Iniciar todos los servicios Docker
docker-compose up -d

# 2. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 3. Iniciar frontend (en terminal separado)
cd frontend && npm run dev

# 4. Abrir dashboards
open http://localhost:3000
open http://localhost:5555
```

### Solo Backend + Servicios

```bash
# Iniciar solo servicios de backend
docker-compose up -d backend db redis celery celery-beat flower

# Verificar estado
docker-compose ps
```

## 🔧 Comandos de Monitoreo

### Estado de Servicios

```bash
# Ver todos los contenedores
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Logs por servicio
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f flower
docker-compose logs -f redis
```

### Diagnóstico Redis

```bash
# Test de conectividad
docker-compose exec redis redis-cli ping

# Información del servidor
docker-compose exec redis redis-cli info

# Monitorear comandos en tiempo real
docker-compose exec redis redis-cli monitor
```

### Diagnóstico Celery

```bash
# Estado de workers
docker-compose exec backend celery -A backend inspect active

# Estadísticas detalladas
docker-compose exec backend celery -A backend inspect stats

# Tareas registradas
docker-compose exec backend celery -A backend inspect registered

# Ping a workers
docker-compose exec backend celery -A backend inspect ping
```

## 📊 Tareas de VS Code

Usa `Ctrl+Shift+P` > "Tasks: Run Task" para acceder a:

### 🐳 Docker Tasks

- **🐳 Docker: Iniciar entorno completo**
- **🐳 Docker: Detener todos los servicios**
- **🐳 Django: Migraciones (en Docker)**
- **🐳 Django: Crear superusuario (en Docker)**

### 📊 Monitoring Tasks

- **🐳 Logs: Backend**
- **🐳 Logs: Celery Worker**
- **🐳 Logs: Celery Beat**
- **🐳 Logs: Flower Dashboard**
- **🐳 Logs: Redis**

### 🔧 Diagnostic Tasks

- **🌸 Flower: Abrir Dashboard**
- **🔧 Celery: Estado de Workers**
- **🔧 Celery: Estadísticas**
- **🔧 Redis: Ping Test**

### 💻 Frontend Tasks

- **💻 Frontend: Desarrollo (local)**
- **💻 Frontend: Instalar dependencias**

## 🚨 Troubleshooting

### Problema: Servicios no inician

```bash
# Detener todo y limpiar
docker-compose down
docker system prune -f

# Rebuilder e iniciar
docker-compose up -d --build
```

### Problema: Redis no conecta

```bash
# Verificar contenedor
docker-compose ps redis

# Reiniciar Redis
docker-compose restart redis

# Verificar logs
docker-compose logs redis
```

### Problema: Celery no procesa tareas

```bash
# Verificar workers
docker-compose exec backend celery -A backend inspect active

# Reiniciar workers
docker-compose restart celery

# Ver logs detallados
docker-compose logs celery
```

### Problema: Frontend no encuentra backend

```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/api/

# Verificar configuración de frontend
cat frontend/.env
```

## 🔐 Configuración de Producción

### Variables de Entorno Críticas

```bash
# .env (para producción)
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Redis URLs para producción
DJANGO_REDIS_URL=redis://redis-prod:6379/1
CELERY_BROKER_URL=redis://redis-prod:6379/0
CELERY_RESULT_BACKEND=redis://redis-prod:6379/2

# Configuración de seguridad
USE_REDIS_SESSIONS=true
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Docker Compose para Producción

```yaml
# docker-compose.prod.yml (ejemplo)
version: "3.8"
services:
  backend:
    build: ./backend
    environment:
      - DEBUG=False
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass yourpassword
    volumes:
      - redis_data_prod:/data

  celery:
    build: ./backend
    command: celery -A backend worker -l info --concurrency=4

  flower:
    image: mher/flower
    environment:
      - FLOWER_BASIC_AUTH=admin:securepassword
```

## 📈 Métricas y Monitoreo

### Flower Dashboard Métricas

- **Worker Status**: Estado de workers activos/inactivos
- **Task Success Rate**: Porcentaje de tareas exitosas
- **Processing Time**: Tiempo promedio de procesamiento
- **Queue Length**: Número de tareas en cola

### Redis Métricas

```bash
# Uso de memoria
docker-compose exec redis redis-cli info memory

# Número de claves
docker-compose exec redis redis-cli dbsize

# Estadísticas de comandos
docker-compose exec redis redis-cli info commandstats
```

### Django Health Check

```bash
# Verificar salud de la aplicación
curl http://localhost:8000/api/health/

# Verificar autenticación
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/me/
```
