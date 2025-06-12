# COPILOT: Aplicación Products

## 🎯 Propósito

Sistema completo de **gestión de productos** con categorización semántica y analytics empresariales.

## 📊 Modelos Principales

### ProductCategory

```python
# Categorización semántica de productos
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent_category = models.ForeignKey('self', null=True)  # Jerarquía
    canonical_url = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
```

### Product

```python
# Producto base con información completa
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory)
    sku = models.CharField(max_length=50, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    canonical_url = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Modality

```python
# Modalidades de entrega/consumo del producto
class Modality(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    delivery_method = models.CharField(max_length=50)  # digital, physical, service
    duration_type = models.CharField(max_length=20)    # one_time, recurring, subscription
```

### ProductModality

```python
# Relación producto-modalidad con pricing específico
class ProductModality(models.Model):
    product = models.ForeignKey(Product)
    modality = models.ForeignKey(Modality)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
```

### Customization

```python
# Opciones de personalización de productos
class Customization(models.Model):
    name = models.CharField(max_length=100)
    customization_type = models.CharField(max_length=50)  # color, size, feature
    available_options = models.JSONField(default=list)
    price_impact = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

### ProductCustomization

```python
# Customizaciones disponibles por producto
class ProductCustomization(models.Model):
    product = models.ForeignKey(Product)
    customization = models.ForeignKey(Customization)
    is_required = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
```

## 🚀 Endpoints API

### Categorías

```
GET    /api/products/categories/              # Lista categorías
POST   /api/products/categories/              # Crear categoría
GET    /api/products/categories/{id}/         # Detalle categoría
GET    /api/products/categories/{id}/products/ # Productos por categoría
```

### Productos Core

```
GET    /api/products/products/                # Lista productos
POST   /api/products/products/                # Crear producto
GET    /api/products/products/{id}/           # Detalle producto
PUT    /api/products/products/{id}/           # Actualizar producto
DELETE /api/products/products/{id}/           # Eliminar producto
```

### Modalidades y Customización

```
GET    /api/products/modalities/              # Lista modalidades
POST   /api/products/modalities/              # Crear modalidad
GET    /api/products/products/{id}/modalities/ # Modalidades del producto

GET    /api/products/customizations/          # Lista customizaciones
POST   /api/products/customizations/          # Crear customización
GET    /api/products/products/{id}/customizations/ # Customizaciones del producto
```

### Analytics de Productos

```
GET    /api/products/analytics/overview/      # Dashboard general
GET    /api/products/analytics/category-performance/ # Performance por categoría
GET    /api/products/analytics/product-insights/ # Insights por producto
GET    /api/products/products/{id}/analytics/ # Analytics específico del producto
```

### Búsqueda y Filtrado

```
GET    /api/products/search/?q=term           # Búsqueda por texto
GET    /api/products/products/?category=id    # Filtrar por categoría
GET    /api/products/products/?price_min=100&price_max=500 # Filtrar por precio
GET    /api/products/products/?modality=digital # Filtrar por modalidad
```

## 📈 Analytics Empresariales

### Dashboard de Productos

- Productos más vendidos/solicitados
- Performance por categoría
- Análisis de pricing y márgenes
- Tendencias de demanda

### Category Performance

- Métricas por categoría de producto
- Comparación entre categorías
- Análisis de penetración de mercado
- Oportunidades de expansión

### Product Insights

- Ciclo de vida del producto
- Análisis de customizaciones populares
- Modalidades más demandadas
- Correlación precio-demanda

## 💡 Patrones de Uso

### Crear Producto Completo

```python
product_data = {
    "name": "CRM Professional",
    "description": "Sistema CRM completo para empresas",
    "category": category_id,
    "sku": "CRM-PRO-001",
    "base_price": "299.99",
    "modalities": [
        {
            "modality": saas_modality_id,
            "price_adjustment": "0.00"
        },
        {
            "modality": onpremise_modality_id,
            "price_adjustment": "500.00"
        }
    ],
    "customizations": [
        {
            "customization": users_limit_id,
            "is_required": True
        }
    ]
}
```

### Búsqueda Avanzada

```python
# Búsqueda semántica por categoría
/api/products/search/?q=CRM&category=software

# Filtrado por modalidad y precio
/api/products/products/?modality=subscription&price_max=200

# Productos con customizaciones específicas
/api/products/products/?has_customization=color&has_customization=size
```

### Analytics por Contexto

```python
# Performance en período específico
/api/products/analytics/category-performance/?start_date=2024-01-01&end_date=2024-12-31

# Insights por segmento de mercado
/api/products/analytics/product-insights/?segment=enterprise&category=software
```

## 🔍 Funcionalidades CRM

### Catálogo Semántico

- Categorización jerárquica de productos
- URLs canónicas para SEO
- Clasificación por modalidad de entrega
- Metadatos de productos estructurados

### Pricing Dinámico

- Precio base por producto
- Ajustes por modalidad
- Impacto de customizaciones
- Cálculo automático de precio final

### Customización Avanzada

- Opciones configurables por producto
- Validación de combinaciones
- Impacto en precio y disponibilidad
- Gestión de inventario por variante

## ⚡ Optimizaciones

### Índices Estratégicos

- Búsqueda por nombre y SKU
- Filtrado por categoría y estado activo
- Consultas por rango de precios
- Ordenamiento por popularidad

### Consultas Optimizadas

```python
# Prefetch para evitar N+1
Product.objects.select_related(
    'category'
).prefetch_related(
    'productmodality_set__modality',
    'productcustomization_set__customization'
)
```

### Caché de Analytics

- Cache de métricas frecuentes
- Precálculo de analytics diarios
- Invalidación inteligente de cache
- Agregaciones optimizadas

## 🧪 Testing y Datos

### Tests de Productos

```bash
# Suite completa de tests
docker-compose exec backend python manage.py test products

# Tests específicos de analytics
docker-compose exec backend python manage.py test products.tests.AnalyticsTests
```

### Datos de Demostración

```python
# Crear catálogo de demo
docker-compose exec backend python manage.py shell
>>> exec(open('populate_products.py').read())

# Mejorar datos existentes
>>> exec(open('enhance_products_data.py').read())
```

### Validaciones

```python
# Validar URLs canónicas
>>> exec(open('validate_canonical_url.py').read())

# Tests de URLs incluidas
>>> exec(open('test_included_products.py').read())
```

## 📊 Métricas de Performance

### KPIs de Productos

- Conversion rate por producto
- Time-to-purchase por categoría
- Customer lifetime value por producto
- Churn rate por modalidad

### Analytics Comerciales

- Revenue por producto y categoría
- Margen de contribución
- Análisis de cross-selling
- Predicción de demanda

## 🔗 Integración con Otras Apps

### Entities

- Preferencias de producto por perfil semántico
- Historial de productos por entidad
- Segmentación de productos por demografía

### Interactions

- Customer journey de discovery de productos
- Tracking de engagement con productos
- Attribution de interacciones a productos

### Offers

- Productos incluidos en ofertas comerciales
- Pricing especial por offer
- Bundling de productos relacionados

### Campaigns

- Productos promocionados en campañas
- Targeting de productos por segmento
- Performance de productos en campaigns
