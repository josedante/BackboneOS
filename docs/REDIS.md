# Configuración de Redis y Caché

## Descripción General

Este proyecto utiliza Redis como sistema de caché y almacenamiento de sesiones para mejorar el rendimiento y la escalabilidad del backend Django.

## Características Implementadas

### 🚀 Caché de Aplicación

- **Backend**: `django_redis.cache.RedisCache`
- **Timeout por defecto**: 5 minutos
- **Prefijo de llaves**: `backend_cache`
- **Conexiones máximas**: 50

### 👤 Sesiones de Usuario

- **Motor de sesiones**: Redis (con fallback a base de datos)
- **Duración**: 24 horas
- **Optimización**: Solo guarda cuando se modifica

### 🔧 Variables de Entorno

```env
# Redis Configuration
DJANGO_REDIS_URL=redis://127.0.0.1:6379/1
USE_REDIS_SESSIONS=true
```

## Uso en el Código

### Caché Manual

```python
from django.core.cache import cache

# Guardar en caché
cache.set('mi_llave', 'mi_valor', timeout=300)

# Recuperar del caché
valor = cache.get('mi_llave')

# Eliminar del caché
cache.delete('mi_llave')
```

### Decoradores de Caché

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@cache_page(60 * 15)  # 15 minutos
def mi_vista(request):
    return JsonResponse(datos)

# Para vistas basadas en clases
@method_decorator(cache_page(60 * 15), name='dispatch')
class MiAPIView(APIView):
    pass
```

### Caché de Queryset en Django REST Framework

```python
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
import hashlib

class OptimizedAPIView(APIView):
    def get(self, request):
        # Crear clave única basada en parámetros
        cache_key = f"api_data_{hashlib.md5(str(request.GET).encode()).hexdigest()}"

        # Intentar obtener del caché
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Si no está en caché, obtener datos
        data = self.get_data()

        # Guardar en caché por 15 minutos
        cache.set(cache_key, data, 60 * 15)

        return Response(data)
```

### Caché de Templates

```python
# En views.py
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@cache_page(60 * 15)
@vary_on_headers('User-Agent', 'Accept-Language')
def mi_vista_template(request):
    return render(request, 'mi_template.html', context)
```

## Configuración en Docker

### docker-compose.yml

```yaml
redis:
  image: redis:7
  container_name: redis
  ports:
    - "6379:6379"
  volumes:
    - ../redis_data:/data
  restart: unless-stopped
```

### Configuración en settings.py

```python
# Configuración de Redis optimizada
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

## Monitoreo y Diagnóstico

### Verificar Conexión Redis

```bash
# En el contenedor Redis
docker exec -it redis redis-cli ping

# Verificar llaves en caché
docker exec -it redis redis-cli keys "backend_cache:*"

# Ver información del servidor Redis
docker exec -it redis redis-cli info
```

### Estadísticas de Caché

```python
# En Django shell
from django.core.cache import cache
from django_redis import get_redis_connection

# Limpiar caché
cache.clear()

# Obtener conexión directa a Redis
redis_conn = get_redis_connection("default")

# Ver estadísticas
print(redis_conn.info())

# Ver todas las llaves
keys = redis_conn.keys("backend_cache:*")
print(f"Llaves en caché: {len(keys)}")
```

### Métricas de Rendimiento

```python
# utils/cache_metrics.py
from django.core.cache import cache
from django_redis import get_redis_connection
import time

class CacheMetrics:
    @staticmethod
    def get_cache_stats():
        """Obtiene estadísticas del caché Redis"""
        try:
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()

            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def measure_cache_performance(key, fetch_function, timeout=300):
        """Mide el rendimiento del caché vs base de datos"""
        # Medir tiempo con caché
        start_time = time.time()
        cached_result = cache.get(key)
        if cached_result is None:
            cached_result = fetch_function()
            cache.set(key, cached_result, timeout)
        cache_time = time.time() - start_time

        # Medir tiempo sin caché (eliminando primero)
        cache.delete(key)
        start_time = time.time()
        db_result = fetch_function()
        db_time = time.time() - start_time

        return {
            'cache_time': cache_time,
            'db_time': db_time,
            'improvement': f"{((db_time - cache_time) / db_time * 100):.2f}%"
        }
```

## Troubleshooting

### Redis No Disponible

El sistema tiene configurado `IGNORE_EXCEPTIONS: True`, por lo que la aplicación funcionará aunque Redis no esté disponible, usando la base de datos como fallback.

**Síntomas:**

- Aplicación funciona pero más lenta
- Logs muestran errores de conexión a Redis

**Soluciones:**

```bash
# Verificar estado del contenedor Redis
docker ps | grep redis

# Reiniciar Redis
docker-compose restart redis

# Ver logs de Redis
docker-compose logs redis
```

### Memoria Redis Llena

```bash
# Ver uso de memoria
docker exec -it redis redis-cli info memory

# Limpiar caché específico
docker exec -it redis redis-cli --scan --pattern "backend_cache:*" | xargs docker exec -i redis redis-cli del

# Configurar política de expulsión (en redis.conf)
# maxmemory-policy allkeys-lru
```

### Limpieza de Caché

```bash
# Limpiar todo el caché Redis
docker exec -it redis redis-cli FLUSHDB

# Limpiar solo llaves con patrón específico
docker exec -it redis redis-cli --scan --pattern "backend_cache:user:*" | xargs docker exec -i redis redis-cli del
```

### Depuración de Llaves de Caché

```python
# management/commands/debug_cache.py
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

class Command(BaseCommand):
    help = 'Debug Redis cache keys'

    def handle(self, *args, **options):
        redis_conn = get_redis_connection("default")

        # Listar todas las llaves
        keys = redis_conn.keys("backend_cache:*")

        for key in keys:
            ttl = redis_conn.ttl(key)
            size = len(redis_conn.get(key) or b'')
            self.stdout.write(f"Key: {key.decode()}, TTL: {ttl}s, Size: {size} bytes")
```

## Mejores Prácticas

### 1. Naming Conventions

```python
# Usar nombres descriptivos y consistentes
USER_PROFILE_CACHE = "user:profile:{user_id}"
PRODUCT_LIST_CACHE = "products:list:{category}:{page}"
API_RESPONSE_CACHE = "api:response:{endpoint}:{params_hash}"
```

### 2. Manejo de Invalidación

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    # Invalidar caché relacionado al producto
    cache.delete(f"product:detail:{instance.id}")
    cache.delete_many([
        f"products:list:category:{instance.category}",
        "products:featured",
        "products:latest"
    ])
```

### 3. Timeouts Apropiados

```python
# Timeouts recomendados por tipo de dato
CACHE_TIMEOUTS = {
    'user_session': 60 * 60 * 24,      # 24 horas
    'product_list': 60 * 15,           # 15 minutos
    'static_content': 60 * 60 * 6,     # 6 horas
    'api_response': 60 * 5,            # 5 minutos
    'heavy_computation': 60 * 60,      # 1 hora
}
```

## Referencias

- [Django-Redis Documentation](https://django-redis.readthedocs.io/)
- [Redis Commands Reference](https://redis.io/commands)
- [Django Caching Framework](https://docs.djangoproject.com/en/4.0/topics/cache/)
- [Redis Best Practices](https://redis.io/docs/manual/clients-guide/)
