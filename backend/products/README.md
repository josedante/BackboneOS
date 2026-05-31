# Sistema de Gestión de Productos - BackboneOS

## 📋 Descripción General

La aplicación `products` implementa un **sistema completo de gestión de catálogo de productos** con capacidades avanzadas de clasificación jerárquica, personalización, pricing dinámico y análisis de mercado, integrado directamente con el campo semántico empresarial de la aplicación `world`.

## 🎯 Concepto y Propósito

### Sistema de Productos en BackboneOS

Un **sistema de productos** es el componente que gestiona todo el catálogo de productos/servicios de la organización, permitiendo clasificación jerárquica, personalización, pricing dinámico y análisis de mercado. La app `products` actúa como:

- **🏢 Catálogo Central**: Gestión unificada de productos y servicios
- **🏷️ Clasificación Semántica**: Organización basada en taxonomías empresariales
- **⚙️ Motor de Personalización**: Configuración y adaptación de productos
- **💰 Centro de Pricing**: Gestión de precios multi-moneda
- **📊 Hub Analítico**: Insights de rendimiento y oportunidades

## 🏗️ Arquitectura de Modelos

### 1. **Division** - Estructura Organizacional

División empresarial que agrupa categorías de productos a nivel organizacional.

```python
class Division(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
```

**Características:**

- **Propósito**: Estructurar productos por áreas de negocio (Tecnología, Consultoría, etc.)
- **Propiedades computadas**: `categories_count`, `products_count`
- **Relación**: Una división puede tener múltiples categorías
- **Analytics**: `get_revenue_summary()` para métricas financieras

### 2. **ProductCategory** - Taxonomía Jerárquica

Categorías organizadas en estructura de árbol con múltiples niveles.

```python
class ProductCategory(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    division = models.ForeignKey(Division, ...)  # Relación con División
    parent = models.ForeignKey('self', ...)      # Jerarquía autorreferencial
```

**Características:**

- **Jerarquía Completa**: División > Categoría > Subcategoría > Producto
- **Propiedades extendidas**:
  - `full_path`: Incluye división en la ruta ("Tecnología > Desarrollo Web > Frontend")
  - `absolute_level`: Considera jerarquía completa incluyendo división
- **Navegación**: `get_descendants()` para obtener subcategorías recursivamente

### 3. **Modality** - Modalidades de Entrega

Formas de ejecución y entrega de productos/servicios.

```python
class Modality(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)  # Virtual, Presencial, Híbrido
    description = models.TextField(blank=True)
```

### 4. **Customization** - Niveles de Personalización

Tipos y niveles de personalización disponibles para productos.

```python
class Customization(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100)              # Básica, Intermedia, Avanzada
    description = models.TextField(blank=True)
```

### 5. **Product** - Entidad Central

Producto o servicio con información completa y relaciones semánticas.

```python
class Product(BaseUUIDModelWithActiveStatus):
    # Información básica
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    canonical_url = models.URLField(max_length=500, blank=True, null=True)

    # Productos incluidos (Bundle System)
    included_products = models.ManyToManyField('self',
                                               symmetrical=False,
                                               blank=True,
                                               related_name='included_in_products')

    # Clasificación y configuración
    category = models.ForeignKey(ProductCategory, ...)
    modalities = models.ManyToManyField(Modality, ...)
    customization = models.ForeignKey(Customization, ...)

    # Características del producto
    duration = models.DurationField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, ...)
    currency_code = models.CharField(max_length=3, default='PEN')

    # Integración con campo semántico (world app)
    target_segments = models.ManyToManyField(MarketSegment, ...)
    related_industries = models.ManyToManyField(Industry, ...)
    related_functions = models.ManyToManyField(FunctionOrResponsibility, ...)
    related_skills = models.ManyToManyField(Skill, ...)
    descriptors = models.ManyToManyField(WorldDescriptor, ...)
    tags = models.ManyToManyField(Tag, ...)
```

**Propiedades Calculadas:**

- `is_customizable`: Verifica si permite personalización
- `has_canonical_url`: Verifica si tiene URL canónica configurada
- `is_bundle`: Verifica si es un bundle (tiene productos incluidos)
- `is_included_in_bundles`: Verifica si está incluido en otros productos
- `price_display`: Precio formateado con moneda
- `bundle_price_display`: Precio total del bundle (producto + incluidos)
- `duration_display`: Duración en formato legible
- `get_target_audience()`: Descripción del público objetivo
- `get_modalities_display()`: Modalidades como string
- `get_included_products_display()`: Productos incluidos como string
- `get_total_included_price()`: Precio total de productos incluidos

## 🌐 API REST Completa

### Endpoints Principales

```
🏢 DIVISIONES
/api/products/divisions/                    # CRUD divisiones
/api/products/divisions/{id}/categories/    # Categorías por división
/api/products/divisions/{id}/products/      # Productos por división
/api/products/divisions/{id}/summary/       # Resumen estadístico

🏷️ CATEGORÍAS
/api/products/categories/                   # CRUD categorías
/api/products/categories/tree/              # Árbol completo de categorías
/api/products/categories/{id}/products/     # Productos por categoría

📋 MODALIDADES Y PERSONALIZACIÓN
/api/products/modalities/                   # Modalidades de productos
/api/products/customizations/               # Tipos de personalización

📦 PRODUCTOS
/api/products/products/                     # CRUD completo de productos
/api/products/products/stats/               # Estadísticas de productos
/api/products/products/search_advanced/     # Búsqueda semántica avanzada
/api/products/products/{id}/duplicate/      # Duplicación de productos
/api/products/products/{id}/included_products/        # Productos incluidos
/api/products/products/{id}/add_included_product/     # Agregar producto incluido
/api/products/products/{id}/remove_included_product/  # Remover producto incluido
/api/products/products/{id}/parent_products/          # Productos padre (que incluyen este)
/api/products/products/{id}/bundle_info/              # Información completa del bundle
```

### Sistema de Filtrado Avanzado

#### Filtros Jerárquicos

- Por categoría incluyendo subcategorías automáticamente
- Por división con cascada a categorías y productos
- Por nivel de jerarquía específico

#### Filtros Semánticos (Integración con World App)

- Por industrias relacionadas
- Por habilidades/competencias requeridas
- Por segmentos de mercado objetivo
- Por descriptores globales y tags

#### Filtros de Negocio

- Rango de precios (min/max)
- Duración del producto (min/max días)
- Moneda específica
- Productos personalizables/estándar
- Productos con/sin precio definido
- Productos con/sin URL canónica

#### Búsqueda Semántica

```python
# Búsqueda en descriptores, tags, contenido y URLs canónicas
?semantic_search=python+data+science
?search=https://empresa.com  # Búsqueda por URL canónica
```

### Serializers Optimizados

#### **ProductListSerializer** - Listados Optimizados

```python
# Campos incluidos para performance en listados
['id', 'name', 'code', 'category_name', 'division_name',
 'price_display', 'duration_display', 'modalities_summary',
 'is_customizable', 'has_canonical_url', 'canonical_url',
 'target_audience_summary', 'included_products_count', 'is_bundle']
```

#### **ProductDetailSerializer** - Vista Completa

```python
# Incluye todas las relaciones y propiedades calculadas
+ related_industries, related_skills, target_segments
+ descriptors, tags, full_path, absolute_level
+ canonical_url, has_canonical_url
+ included_products, parent_products, bundle_price_display, is_bundle
```

#### **ProductCreateUpdateSerializer** - Operaciones de Escritura

```python
# Simplificado para crear/actualizar sin campos calculados
- campos read_only, + validaciones de negocio
```

## 📊 Sistema de Analytics Avanzado

### Dashboard Principal de Analytics

```
/api/products/analytics/dashboard/
```

**Métricas Generales:**

- Total productos activos/inactivos
- Distribución por categorías y divisiones
- Análisis de pricing multi-moneda
- Productos personalizables vs estándar

### Analytics Especializados

#### 🏢 Analytics por División

```
/api/products/analytics/divisions/
```

- Comparativa entre divisiones
- Métricas de productos y categorías por división
- Análisis de precios promedio por división
- Top divisiones por volumen de productos

#### 🏷️ Analytics de Categorías

```
/api/products/analytics/categories/
```

- Distribución de productos por categoría
- Categorías más populares
- Análisis de profundidad jerárquica
- Performance por nivel de categoría

#### 🎯 Segmentación de Mercado

```
/api/products/analytics/market-segmentation/
```

- Análisis por segmentos de mercado
- Mapping industria-productos
- Distribución de habilidades requeridas
- Targeting effectiveness

#### 💰 Analytics de Pricing

```
/api/products/analytics/pricing/
```

- Estadísticas por moneda
- Distribución de rangos de precios
- Análisis de productos sin precio
- Precio promedio por categoría/división

#### 📈 Analytics de Crecimiento

```
/api/products/analytics/growth/
```

- Tendencias temporales de creación
- Crecimiento por división/categoría
- Evolución del catálogo
- Proyecciones de crecimiento

#### 🤖 Recomendaciones Inteligentes

```
/api/products/analytics/recommendations/
```

- Productos similares por contexto semántico
- Recomendaciones basadas en segmentación
- Cross-selling opportunities
- Gap analysis del catálogo

## 🔧 Características Avanzadas

### Optimización de Performance

#### Consultas Optimizadas

```python
# En listados
queryset.select_related('category', 'customization')
       .prefetch_related('modalities', 'target_segments')

# En detalles
queryset.select_related('category', 'customization')
       .prefetch_related('modalities', 'target_segments',
                        'related_industries', 'related_functions',
                        'related_skills', 'descriptors', 'tags')
```

#### Índices de Base de Datos

```python
indexes = [
    models.Index(fields=['is_active']),
    models.Index(fields=['name']),
    models.Index(fields=['code']),
    models.Index(fields=['category', 'is_active']),
    models.Index(fields=['base_price']),
    models.Index(fields=['division', 'is_active']),  # Para categorías
]
```

### Validaciones de Negocio

#### Constraints de Base de Datos

```python
constraints = [
    # Precios positivos
    models.CheckConstraint(
        check=models.Q(base_price__gte=0) | models.Q(base_price__isnull=True),
        name='positive_base_price'
    ),
    # Monedas válidas
    models.CheckConstraint(
        check=models.Q(currency_code__in=['PEN', 'USD', 'EUR']),
        name='valid_currency_code'
    ),
]
```

#### Validaciones Django

```python
def clean(self):
    # Validar precio positivo
    if self.base_price is not None and self.base_price <= Decimal('0'):
        raise ValidationError({'base_price': 'El precio debe ser mayor a 0'})
```

#### Campos de Referencia Externa

- **`canonical_url`**: URL externa opcional que referencia la página oficial del producto
- **`has_canonical_url`**: Propiedad calculada que indica si el producto tiene URL canónica configurada
- Filtro administrativo `HasCanonicalUrlFilter` para productos con/sin URL canónica

### Interface Administrativa Optimizada

#### Listas con Información Relevante

```python
list_display = (
    'name', 'code', 'category', 'price_display', 'duration_display',
    'target_audience_summary', 'modalities_summary', 'is_customizable',
    'has_canonical_url_display'
)
```

#### Filtros Inteligentes

```python
list_filter = (
    'is_active', 'category', 'modalities', 'currency_code',
    'target_segments', 'related_industries', 'customization',
    HasCanonicalUrlFilter
)
```

#### Acciones en Lote

- Activar/desactivar productos masivamente
- Duplicar productos con variaciones
- Exportar catálogo filtrado

## 🎯 Casos de Uso en CRM

### 1. **Catalogación Inteligente**

Organización semántica del portafolio basada en ontología empresarial.

```python
# Ejemplo: Productos para sector financiero
financial_products = Product.objects.filter(
    related_industries__name__icontains="Financial",
    target_segments__name__in=["Enterprise", "Corporate"]
)
```

### 2. **Targeting Preciso**

Matching de productos con perfiles específicos de clientes.

```python
# Productos para CTOs en tecnología
cto_tech_products = Product.objects.filter(
    related_functions__name__icontains="CTO",
    related_industries__parent__name="Technology",
    related_skills__name__in=["Leadership", "Technical Strategy"]
)
```

### 3. **Configuración Dinámica**

Personalización basada en contexto empresarial del cliente.

```python
# Productos personalizables para grandes empresas
customizable_enterprise = Product.objects.filter(
    customization__isnull=False,
    target_segments__name="Enterprise"
).prefetch_related('modalities')
```

### 4. **Análisis de Portafolio**

Insights para decisiones estratégicas de producto.

```python
# Dashboard ejecutivo
portfolio_analysis = {
    'by_division': Division.analytics_summary(),
    'pricing_analysis': Product.pricing_statistics(),
    'market_coverage': MarketSegment.product_coverage(),
    'skill_gaps': Skill.uncovered_skills()
}
```

### 5. **Pricing Estratégico**

Gestión de precios basada en segmentación y competencia.

```python
# Análisis de precio por segmento
segment_pricing = Product.objects.values('target_segments__name')\
    .annotate(
        avg_price=Avg('base_price'),
        products_count=Count('id')
    ).order_by('-avg_price')
```

### 6. **Recomendaciones Automáticas**

Sugerencias basadas en perfil semántico del cliente.

```python
# Sistema de recomendaciones
recommendations = ProductRecommendationEngine.get_recommendations(
    client_profile={
        'industry': client.industry,
        'size': client.market_segment,
        'functions': client.key_functions,
        'skills_needed': client.skill_gaps
    }
)
```

## 🔄 Integración con Otras Apps

### Integración con World App (Campo Semántico)

```python
# Relaciones semánticas en Product
related_industries = models.ManyToManyField(Industry, blank=True)
related_functions = models.ManyToManyField(FunctionOrResponsibility, blank=True)
related_skills = models.ManyToManyField(Skill, blank=True)
target_segments = models.ManyToManyField(MarketSegment, blank=True)
descriptors = models.ManyToManyField(WorldDescriptor, blank=True)
tags = models.ManyToManyField(Tag, blank=True)
```

### Integración con Interactions App

```python
# En Touchpoint
product = models.ForeignKey('products.Product', null=True, blank=True)
```

### Integración con Entities App

```python
# Para asociar productos con organizaciones/personas
# Future: ProductOwnership, ProductResponsible, etc.
```

## 📈 Valor para la Organización

### 🎯 **Ventajas Estratégicas**

- **Catálogo Centralizado**: Gestión unificada de todo el portafolio
- **Clasificación Inteligente**: Organización basada en ontología empresarial
- **Flexibilidad Comercial**: Adaptación a diferentes mercados y segmentos
- **Insights de Negocio**: Analytics que impulsan decisiones estratégicas

### ⚡ **Beneficios Operativos**

- **Eficiencia**: Automatización de procesos de gestión de productos
- **Escalabilidad**: Crecimiento ordenado del catálogo
- **Trazabilidad**: Historia completa de productos y cambios
- **Integración**: Conexión fluida con CRM y otros sistemas

### 🚀 **Ventaja Competitiva**

- **Inteligencia Comercial**: Datos estructurados para mejores decisiones
- **Personalización**: Adaptación rápida a necesidades específicas
- **Time-to-Market**: Lanzamiento ágil de nuevos productos
- **Customer Intelligence**: Mejor comprensión del ajuste producto-mercado

## 🛠️ Comandos de Desarrollo

### Crear Datos de Prueba

```bash
# Poblar productos iniciales
docker-compose exec backend python manage.py shell < populate_products.py

# Agregar datos adicionales
docker-compose exec backend python manage.py shell < enhance_products_data.py

# Crear divisiones
docker-compose exec backend python manage.py shell < create_divisions_data.py
```

### Testing

```bash
# Tests unitarios
docker-compose exec backend python manage.py test products

# Tests de performance
docker-compose exec backend python manage.py shell < products/performance_tests.py
```

### Acceso a APIs

```bash
# Admin interface
http://localhost:8000/admin/products/

# API endpoints
http://localhost:8000/api/products/

# Analytics dashboard
http://localhost:8000/api/products/analytics/dashboard/
```

## 🔮 Roadmap Futuro

### Funcionalidades Planeadas

- [ ] **Product Lifecycle Management**: Estados del producto (Draft, Active, Deprecated)
- [ ] **Version Control**: Gestión de versiones de productos
- [ ] **Pricing Rules**: Motor de reglas de pricing dinámico
- [ ] **Product Bundles**: Agrupación y paquetes de productos
- [ ] **Inventory Integration**: Conexión con sistemas de inventario
- [ ] **A/B Testing**: Experimentación con variantes de productos
- [ ] **ROI Analytics**: Análisis de rentabilidad por producto
- [ ] **Competitive Intelligence**: Comparación con productos competidores

### Integraciones Futuras

- [ ] **E-commerce Integration**: Sincronización con plataformas de venta
- [ ] **ERP Integration**: Conexión con sistemas empresariales
- [ ] **BI Tools**: Integración con Tableau, Power BI, etc.
- [ ] **AI/ML Engine**: Recomendaciones y pricing inteligente

---

## 📚 Referencias y Documentación

- **Modelos**: Ver `models.py` para estructura completa
- **API Docs**: Swagger disponible en `/api/docs/`
- **Analytics**: Ver `analytics.py` para métricas disponibles
- **Performance**: [docs/DATABASE_INDEXES.md](../../docs/DATABASE_INDEXES.md)
- **Testing**: Ejemplos en `tests.py`

---

## Documentación

- [docs/APPS.md](../../docs/APPS.md)
- [docs/TESTING.md](../../docs/TESTING.md) — `products/tests.py`, `products/tests_template_views.py`
- [docs/DATABASE_INDEXES.md](../../docs/DATABASE_INDEXES.md)
- [backend/README.md](../README.md)

---

**BackboneOS Products App — catálogo comercial**
