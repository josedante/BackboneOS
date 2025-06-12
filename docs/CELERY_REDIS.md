# 🚀 Celery y Redis - Procesamiento Asíncrono

## 📋 Resumen

BackboneOS utiliza **Celery** con **Redis** como broker para el procesamiento asíncrono de tareas, optimizando el rendimiento y la experiencia del usuario.

## 🏗️ Arquitectura de Servicios

### Redis (Multi-Propósito)

Redis actúa como:

- **DB 0**: Broker de Celery (cola de tareas)
- **DB 1**: Caché de Django (consultas, sesiones)
- **DB 2**: Backend de resultados de Celery

```yaml
# docker-compose.yml
redis:
  image: redis:7
  container_name: redis
  ports:
    - "6379:6379"
  volumes:
    - ../redis_data:/data
  restart: unless-stopped
```

### Celery Worker

Procesa tareas en segundo plano:

```yaml
celery:
  build: ./backend
  command: celery -A backend worker -l info
  depends_on:
    - backend
    - redis
  volumes:
    - ./backend:/app
  env_file:
    - .env
```

### Celery Beat

Programador de tareas periódicas:

```yaml
celery-beat:
  build: ./backend
  command: celery -A backend beat -l info
  depends_on:
    - backend
    - redis
  volumes:
    - ./backend:/app
  env_file:
    - .env
```

### Flower Dashboard

Monitoreo web de Celery:

```yaml
flower:
  image: mher/flower
  command: celery -A backend flower --port=5555
  ports:
    - "5555:5555"
  depends_on:
    - redis
    - backend
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/2
```

## ⚙️ Configuración en Django

### settings.py - Configuración de Celery

```python
# =============================================================================
# CONFIGURACIÓN DE CELERY
# =============================================================================
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
```

### settings.py - Configuración de Redis

```python
# =============================================================================
# CONFIGURACIÓN DE REDIS Y CACHÉ
# =============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("DJANGO_REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
            "IGNORE_EXCEPTIONS": True,  # Evita errores si Redis no está disponible
        },
        "KEY_PREFIX": "backend_cache",  # Prefijo para evitar colisiones
        "TIMEOUT": 300,  # Timeout por defecto de 5 minutos
    }
}
```

## 🎯 Casos de Uso

### Tareas Asíncronas Típicas

1. **Envío de Emails**

   - Confirmaciones de registro
   - Notificaciones de campaña
   - Reportes automáticos

2. **Procesamiento de Datos**

   - Importación de archivos CSV
   - Generación de reportes complejos
   - Análisis de interacciones

3. **Mantenimiento**
   - Limpieza de sesiones expiradas
   - Backups programados
   - Sincronización de datos externos

### Tareas Programadas (Beat)

- **Diarias**: Limpieza de caché, backup incremental
- **Semanales**: Reportes de KPIs, análisis de tendencias
- **Mensuales**: Archivado de datos antiguos, auditoría

## 🔧 Comandos de Desarrollo

### Gestión de Servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs de Celery Worker
docker-compose logs -f celery

# Ver logs de Celery Beat
docker-compose logs -f celery-beat

# Acceder a Flower Dashboard
open http://localhost:5555
```

### Monitoreo y Debugging

```bash
# Inspeccionar workers activos
docker-compose exec backend celery -A backend inspect active

# Ver estadísticas de workers
docker-compose exec backend celery -A backend inspect stats

# Listar tareas registradas
docker-compose exec backend celery -A backend inspect registered
```

## 📊 Flower Dashboard

### Acceso y Características

- **URL**: http://localhost:5555
- **Características**:
  - Monitoreo en tiempo real de workers
  - Historial de tareas ejecutadas
  - Estadísticas de rendimiento
  - Control de workers (reinicio, apagado)
  - Visualización de colas de tareas

### Métricas Importantes

- **Worker Status**: Estados de los workers (activo, inactivo)
- **Task Success Rate**: Porcentaje de tareas exitosas
- **Processing Time**: Tiempo promedio de procesamiento
- **Queue Length**: Número de tareas pendientes

## 🚨 Troubleshooting

### Problemas Comunes

1. **Redis no disponible**

   ```bash
   # Verificar estado del contenedor
   docker-compose ps redis

   # Reiniciar Redis
   docker-compose restart redis
   ```

2. **Celery Worker no procesa tareas**

   ```bash
   # Ver logs detallados
   docker-compose logs celery

   # Reiniciar worker
   docker-compose restart celery
   ```

3. **Flower no accesible**

   ```bash
   # Verificar puerto y dependencias
   docker-compose ps flower

   # Reiniciar Flower
   docker-compose restart flower
   ```

### Comandos de Diagnóstico

```bash
# Estado completo de Celery
docker-compose exec backend celery -A backend status

# Ping a workers
docker-compose exec backend celery -A backend inspect ping

# Verificar conexión Redis
docker-compose exec redis redis-cli ping
```

## 🔐 Seguridad

### Consideraciones de Producción

1. **Autenticación Redis**: Configurar contraseña
2. **Flower Access**: Restricción por IP o autenticación
3. **SSL/TLS**: Encrypting communication entre servicios
4. **Firewall**: Limitar acceso a puertos internos

### Variables de Entorno

```bash
# .env example
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/2
DJANGO_REDIS_URL=redis://redis:6379/1
USE_REDIS_SESSIONS=true
```

## 📈 Optimización

### Configuración de Performance

1. **Connection Pooling**: Máximo 50 conexiones Redis
2. **Task Routing**: Rutas específicas por tipo de tarea
3. **Result Expiration**: Limpieza automática de resultados
4. **Worker Concurrency**: Ajuste según CPU/memoria

### Mejores Prácticas

- Tareas idempotentes (pueden ejecutarse múltiples veces)
- Timeouts apropiados para evitar workers colgados
- Logging detallado para debugging
- Monitoreo continuo con Flower
- Backup regular de datos Redis críticos
