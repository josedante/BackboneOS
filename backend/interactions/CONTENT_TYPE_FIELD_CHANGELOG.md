# 🆕 Nuevo Campo `content_type` en Touchpoint

## Resumen

Se ha agregado el campo opcional `content_type` al modelo `Touchpoint` para clasificar el enfoque estratégico del contenido asociado a cada punto de contacto dentro del customer journey.

## Cambios Realizados

### 1. Modelo Touchpoint (`interactions/models.py`)

```python
# Nuevas constantes para choices
AFFINITY = 'affinity'
CATEGORY = 'category'
PRODUCT = 'product'
BRAND = 'brand'
CONTENT_TYPE_CHOICES = [
    (AFFINITY, 'Afinidad'),
    (CATEGORY, 'Categoría'),
    (PRODUCT, 'Producto'),
    (BRAND, 'Marca'),
]

# Nuevo campo
content_type = models.CharField(
    max_length=20,
    choices=CONTENT_TYPE_CHOICES,
    blank=True,
    null=True,
    verbose_name="Tipo de contenido comunicacional",
    help_text="Clasificación del enfoque estratégico del contenido asociado a este touchpoint"
)
```

### 2. Admin de Django (`interactions/admin.py`)

- ✅ Agregado `content_type` a `list_display`
- ✅ Agregado `content_type` a `list_filter`
- ✅ Agregado `content_type` al fieldset "Configuración de Negocio"

### 3. Migración de Base de Datos

- ✅ Migración creada y aplicada
- ✅ Campo agregado como opcional (nullable)

## Valores del Campo

| Valor      | Significado                                              | Ejemplos de Uso                    |
| ---------- | -------------------------------------------------------- | ---------------------------------- |
| `affinity` | Contenido que apela a emociones, valores o identidad    | `/ranking-y-reputacion`, `/valores` |
| `category` | Contenido que representa una línea temática amplia      | `/maestrias`, `/especializaciones` |
| `product`  | Contenido enfocado en un producto o servicio específico | `/mba`, `/programa-ejecutivo`      |
| `brand`    | Contenido orientado al posicionamiento institucional    | `/nosotros`, `/historia`           |

## Ejemplos de Uso

### En Django Shell

```python
from interactions.models import Touchpoint

# Crear touchpoint para página de MBA
mba_touchpoint = Touchpoint.objects.create(
    name="Página MBA",
    url="https://example.com/mba",
    content_type="product",
    description="Página principal del programa MBA"
)

# Crear touchpoint institucional
about_touchpoint = Touchpoint.objects.create(
    name="Página Nosotros",
    url="https://example.com/nosotros",
    content_type="brand",
    description="Página institucional sobre la organización"
)

# Filtrar por tipo de contenido
product_touchpoints = Touchpoint.objects.filter(content_type="product")
brand_touchpoints = Touchpoint.objects.filter(content_type="brand")
```

### En el Admin de Django

1. Ve a **Admin > Interactions > Touchpoints**
2. El campo `content_type` aparece en:
   - Lista de touchpoints (columna visible)
   - Filtros laterales (para filtrar por tipo)
   - Formulario de edición (sección "Configuración de Negocio")

## Análisis y Reportes

Este campo permite análisis estratégicos como:

```python
# Distribución de touchpoints por tipo de contenido
from django.db.models import Count
from interactions.models import Touchpoint

distribution = Touchpoint.objects.values('content_type').annotate(
    count=Count('id')
).order_by('-count')

# Interacciones por tipo de contenido
from interactions.models import Interaction

interaction_analysis = Interaction.objects.filter(
    touchpoint__content_type__isnull=False
).values('touchpoint__content_type').annotate(
    total_interactions=Count('id')
)
```

## Compatibilidad

- ✅ **Retrocompatible**: El campo es opcional y nullable
- ✅ **Touchpoints existentes**: No se ven afectados, mantendrán `content_type=None`
- ✅ **APIs**: Los serializers existentes seguirán funcionando

## Migración Aplicada

```bash
# Comando ejecutado
docker-compose exec backend python manage.py makemigrations interactions
docker-compose exec backend python manage.py migrate
```

---

**Fecha**: 12 de junio de 2025  
**Versión**: v1.1.0  
**Autor**: Desarrollo BackboneOS
