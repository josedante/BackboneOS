# COPILOT: Aplicación Offers

## 🎯 Propósito

Sistema de **ofertas comerciales** con segmentación semántica y targeting empresarial.

## 📊 Modelo Principal

### ProductOffering

```python
# Oferta comercial completa con segmentación
class ProductOffering(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    # Productos incluidos
    included_products = models.ManyToManyField('products.Product', through='OfferingProduct')

    # Pricing y condiciones
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    currency = models.ForeignKey('world.Currency', default=1)

    # Segmentación semántica
    target_industries = models.ManyToManyField('world.Industry', blank=True)
    target_organization_types = models.ManyToManyField('world.OrganizationType', blank=True)
    target_countries = models.ManyToManyField('world.Country', blank=True)

    # Validez temporal
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)

    # Estado y visibilidad
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)

    # Metadatos empresariales
    offering_type = models.CharField(max_length=50, default='standard')
    priority_level = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### OfferingProduct

```python
# Relación productos-oferta con configuración específica
class OfferingProduct(models.Model):
    offering = models.ForeignKey(ProductOffering)
    product = models.ForeignKey('products.Product')

    # Configuración específica para esta oferta
    quantity = models.PositiveIntegerField(default=1)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Orden y visibilidad
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_optional = models.BooleanField(default=False)
```

## 🚀 Endpoints API (10 endpoints completos)

### CRUD de Ofertas

```
GET    /api/offers/offerings/                 # Lista ofertas
POST   /api/offers/offerings/                 # Crear oferta
GET    /api/offers/offerings/{id}/            # Detalle oferta
PUT    /api/offers/offerings/{id}/            # Actualizar oferta
DELETE /api/offers/offerings/{id}/            # Eliminar oferta
```

### Gestión de Productos en Ofertas

```
GET    /api/offers/offerings/{id}/products/   # Productos de la oferta
POST   /api/offers/offerings/{id}/products/   # Añadir producto a oferta
PUT    /api/offers/offerings/{id}/products/{product_id}/ # Actualizar configuración
DELETE /api/offers/offerings/{id}/products/{product_id}/ # Quitar producto
```

### Analytics Empresariales

```
GET    /api/offers/analytics/overview/        # Dashboard de ofertas
GET    /api/offers/analytics/performance/     # Performance por oferta
```

## 📈 Analytics Empresariales

### Dashboard de Ofertas

- Ofertas más solicitadas/efectivas
- Performance por tipo de oferta
- Análisis de conversión por segmento
- ROI por oferta comercial

### Performance Analysis

- Tasa de conversión por oferta
- Análisis de pricing vs demanda
- Efectividad por segmentación
- Métricas de engagement

### Segmentation Analytics

- Performance por industria target
- Efectividad por geografía
- Análisis por tipo de organización
- Optimización de targeting

## 💡 Patrones de Uso

### Crear Oferta Completa

```python
offering_data = {
    "name": "CRM Enterprise Bundle",
    "description": "Paquete completo CRM para empresas",
    "base_price": "999.99",
    "discount_percentage": "15.00",
    "currency": 1,  # USD

    # Segmentación semántica
    "target_industries": [5, 8, 12],  # Technology, Finance, Healthcare
    "target_organization_types": [1, 2],  # Corporation, LLC
    "target_countries": [1, 2, 3],  # USA, Canada, Mexico

    # Productos incluidos
    "products": [
        {
            "product": 1,  # CRM Core
            "quantity": 1,
            "discount_percentage": "10.00",
            "is_featured": True
        },
        {
            "product": 3,  # Analytics Module
            "quantity": 1,
            "discount_percentage": "20.00"
        }
    ],

    # Validez
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_until": "2024-12-31T23:59:59Z"
}
```

### Búsqueda y Filtrado Semántico

```python
# Ofertas por segmentación
/api/offers/offerings/?target_industries=5&target_countries=1
/api/offers/offerings/?target_organization_types=1&is_active=true

# Ofertas por precio y vigencia
/api/offers/offerings/?price_min=100&price_max=1000&active_now=true
/api/offers/offerings/?offering_type=premium&requires_approval=false

# Búsqueda por contenido
/api/offers/offerings/?search=CRM&has_product=1
```

### Analytics Contextuales

```python
# Performance por segmento
/api/offers/analytics/performance/?segment_by=industry&time_period=last_quarter

# Análisis de conversión
/api/offers/analytics/overview/?offering_type=standard&group_by=country

# Métricas por producto incluido
/api/offers/analytics/product-inclusion/?product_id=1&period=last_6_months
```

## 🔍 Funcionalidades CRM

### Segmentación Semántica

- Targeting por industria específica
- Segmentación por tipo de organización
- Filtrado geográfico por países
- Criterios combinados de targeting

### Pricing Dinámico

- Precio base personalizable
- Descuentos por oferta general
- Descuentos específicos por producto
- Override de precios por contexto

### Gestión de Productos

- Bundling de productos relacionados
- Configuración de cantidades
- Productos opcionales vs obligatorios
- Orden de presentación personalizable

### Validez Temporal

- Fechas de inicio y fin configurables
- Ofertas permanentes (sin fecha fin)
- Control de visibilidad temporal
- Análisis de performance histórica

## ⚡ Optimizaciones

### Índices Estratégicos

```python
# Búsqueda por segmentación
INDEX: (target_industries, is_active, valid_from, valid_until)
INDEX: (target_countries, is_public, offering_type)
INDEX: (created_at, priority_level)

# Filtrado por pricing
INDEX: (base_price, discount_percentage, currency)
```

### Consultas Optimizadas

```python
# Prefetch para evitar N+1
ProductOffering.objects.select_related(
    'currency'
).prefetch_related(
    'included_products__category',
    'target_industries',
    'target_countries',
    'target_organization_types'
)
```

### Cálculo de Precios

```python
# Precio final calculado dinámicamente
def calculate_final_price(self):
    base = self.base_price or 0
    discount = (base * self.discount_percentage / 100)
    return base - discount

# Precio por producto en oferta
def product_final_price(self, product):
    offering_product = self.offeringproduct_set.get(product=product)
    base_price = offering_product.price_override or product.base_price
    discount = base_price * offering_product.discount_percentage / 100
    return base_price - discount
```

## 🧪 Testing y Datos

### Tests de Ofertas

```bash
# Suite completa de tests
docker-compose exec backend python manage.py test offers

# Tests específicos de pricing
docker-compose exec backend python manage.py test offers.tests.PricingTests

# Tests de segmentación
docker-compose exec backend python manage.py test offers.tests.SegmentationTests
```

### Datos de Demostración

```python
# Crear ofertas de demo
docker-compose exec backend python manage.py shell
>>> exec(open('create_offers_data.py').read())
```

### Validaciones de Negocio

```python
# Validar coherencia de precios
def clean(self):
    if self.valid_until and self.valid_until <= self.valid_from:
        raise ValidationError("valid_until debe ser posterior a valid_from")

    if self.discount_percentage < 0 or self.discount_percentage > 100:
        raise ValidationError("discount_percentage debe estar entre 0 y 100")
```

## 📊 Métricas de Performance

### KPIs de Ofertas

- Conversion rate por oferta
- Average order value por oferta
- Customer acquisition cost por oferta
- Lifetime value de clientes por oferta

### Analytics de Segmentación

- Performance por industria target
- Efectividad por geografía
- ROI por tipo de organización
- Análisis de penetración de mercado

## 🔗 Integración con Otras Apps

### Products (Bundling)

```python
# Productos incluidos en ofertas
ProductOffering.included_products → Product (ManyToMany)
OfferingProduct.price_override → Pricing específico
```

### Entities (Targeting)

```python
# Segmentación por perfil semántico
Organization.industry → target_industries
Organization.organization_type → target_organization_types
PhysicalAddress.country → target_countries
```

### Interactions (Tracking)

```python
# Customer journey de ofertas
Interaction.metadata = {"offering_id": offering.id, "action": "viewed_offer"}
Session tracking para análisis de conversión
```

### Campaigns (Promoción)

```python
# Ofertas promocionadas en campañas
Campaign.promoted_offerings → ProductOffering (ManyToMany)
CampaignTouchpoint.content → Oferta específica
```

### World (Contexto)

```python
# Datos de referencia para segmentación
target_industries → world.Industry
target_countries → world.Country
target_organization_types → world.OrganizationType
currency → world.Currency
```
