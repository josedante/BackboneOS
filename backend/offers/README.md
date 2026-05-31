# 🎯 App Offers - Sistema de Gestión de Ofertas Comerciales

## ✅ Estado del Proyecto: **IMPLEMENTADA CON MEJORAS RECIENTES**

La aplicación `offers` está **funcionalmente completa** con todas las características empresariales implementadas, incluyendo API REST completa, analytics avanzados, segmentación semántica y optimizaciones de performance. **Recientemente actualizada** con fixes críticos y mejoras de estabilidad.

## 🎯 Propósito

La aplicación `offers` representa las **ofertas comerciales activas** de la organización. Cada instancia del modelo `ProductOffering` define cómo se ofrece un producto del catálogo bajo condiciones específicas de precio, duración, canal, contexto o audiencia.

Este sistema actúa como el **centro de comercialización** que transforma productos del catálogo en ofertas comerciales concretas con pricing dinámico, temporalidad y segmentación avanzada.

## 🧱 Integración con BackboneOS

### Relaciones con otras apps

| Componente              | Ubicación              | Relación                         | Propósito              |
| ----------------------- | ---------------------- | -------------------------------- | ---------------------- |
| Producto base           | `products.Product`     | FK: `product`                    | Define qué se ofrece   |
| Canales disponibles     | `interactions.Channel` | M2M: `channels`                  | Dónde se puede vender  |
| Sedes de disponibilidad | `our_institution.Seat` | M2M: `seats`                     | Ubicaciones permitidas |
| Segmentación semántica  | `world.*`              | M2M: industrias, funciones, etc. | A quién se dirige      |
| Campañas objetivo       | `campaigns.Campaign`   | M2M: `target_offers`             | Campañas que usan esta oferta |

### Campo Semántico Empresarial

La app `offers` aprovecha completamente el **campo semántico** de BackboneOS:

```python
# Segmentación semántica avanzada
related_industries = models.ManyToManyField('world.Industry', blank=True)
related_functions = models.ManyToManyField('world.FunctionOrResponsibility', blank=True)
target_segments = models.ManyToManyField('world.MarketSegment', blank=True)
descriptors = models.ManyToManyField('world.WorldDescriptor', blank=True)
tags = models.ManyToManyField('world.Tag', blank=True)
```

## 🧩 Modelo Principal: `ProductOffering`

### Características Clave

- 🔗 **Vinculado a un producto** principal del catálogo
- 💰 **Define precio específico** y condiciones comerciales concretas
- 📅 **Puede ser temporal** (válido desde/hasta)
- 🔄 **Soporta suscripciones** con duración y renovación automática
- 🌐 **Se limita por canal, sede, segmento, industria**, etc.
- 🧠 **Campos semánticos** heredados del diseño de BackboneOS
- 🎯 **Metadata JSON** para configuraciones avanzadas

### Propiedades Computadas

```python
@property
def is_currently_valid(self):
    """Verifica si la oferta está actualmente válida"""

@property
def price_display(self):
    """Formato amigable del precio"""
    return f"{self.currency_code} {self.price:,.2f}"
```

## 🔌 API REST Completa - 10 Endpoints

### Endpoints Principales

```bash
# CRUD completo
GET/POST     /api/offers/offerings/
GET/PUT/DEL  /api/offers/offerings/{id}/

# Endpoints especializados
GET          /api/offers/offerings/choices/            # Para formularios
GET          /api/offers/offerings/currently_valid/    # Ofertas válidas ahora
GET          /api/offers/offerings/by_product/         # Por producto específico
GET          /api/offers/offerings/by_channel/         # Por canal específico
GET          /api/offers/offerings/analytics/          # Dashboard completo
POST         /api/offers/offerings/{id}/duplicate/     # Duplicar oferta
```

### Filtros Avanzados

```bash
# Filtros disponibles
?is_active=true
?currency_code=USD
?auto_renew=true
?valid_from__gte=2025-01-01
?valid_until__lte=2025-12-31
?price__gte=1000&price__lte=5000
?product__category=1
?channels=1,2,3
?target_segments=1
?related_industries=1
?currently_valid=true
?product=123
?min_price=500
?max_price=2000

# Búsquedas
?search=crm
?search=consultoria
?ordering=-price
?ordering=valid_from
```

## 📊 Analytics Empresariales

### Dashboard de Analytics (`/api/offers/offerings/analytics/`)

```json
{
  "total_offerings": 5,
  "active_offerings": 5,
  "expired_offerings": 0,
  "future_offerings": 2,
  "by_currency": [
    {"currency_code": "USD", "count": 5, "avg_price": 10180.0}
  ],
  "by_product_category": [...],
  "by_channel": [...],
  "price_statistics": {
    "min_price": 1400.0,
    "max_price": 25000.0,
    "avg_price": 10180.0,
    "total_value": 50900.0
  },
  "duration_statistics": {...},
  "top_products": [...],
  "recent_offerings": [...]
}
```

### Métricas Disponibles

- **Distribución por moneda** con precios promedio
- **Análisis por categoría de producto** (top 10)
- **Performance por canal** (top 10)
- **Segmentación de mercado**
- **Estadísticas de precios** (min, max, promedio, total)
- **Estadísticas de duración** para suscripciones
- **Top productos** más ofertados
- **Ofertas recientes** (últimas 5)

## 🛠️ Serializers Contextuales

### Optimizados por Caso de Uso

```python
# Para listados rápidos
ProductOfferingListSerializer  # Campos esenciales + propiedades computadas

# Para detalles completos
ProductOfferingDetailSerializer  # Incluye relaciones semánticas

# Para operaciones CRUD
ProductOfferingCreateUpdateSerializer  # Validaciones de negocio

# Para formularios
ProductOfferingChoiceSerializer  # Solo ID, nombre y display_name

# Para analytics
ProductOfferingAnalyticsSerializer  # Estructura de métricas
```

### Validaciones de Negocio

- **Código único** por oferta
- **Fechas válidas** (inicio ≤ fin)
- **Precios positivos**
- **Integridad referencial** con productos

## 🔧 Interface Administrativa

### Django Admin Optimizado

```python
# Características del admin
- List display con información clave
- Filtros por múltiples dimensiones
- Búsqueda en campos relacionados
- Fieldsets organizados semánticamente
- Filter horizontal para M2M
- Acciones en lote (activar/desactivar/duplicar)
- Consultas optimizadas con select_related/prefetch_related
```

### Acciones Disponibles

1. **Activar ofertas** en lote
2. **Desactivar ofertas** en lote
3. **Duplicar ofertas** con relaciones M2M
4. **Filtros inteligentes** por categoría, segmentos, industrias
5. **Campos calculados** para mejor UX

## 🧪 Testing y Calidad

### Tests Implementados

```python
# Tests del modelo
- Representación string correcta
- Propiedades computadas (price_display, is_currently_valid)
- Validaciones de fechas
- Casos edge (sin fechas, expiradas, futuras)

# Tests de la API
- CRUD completo (Create, Read, Update, Delete)
- Filtros avanzados (moneda, fechas, precios)
- Endpoints especializados (currently_valid, analytics)
- Duplicación de ofertas
- Validaciones de negocio
```

### Datos de Prueba

- **5 ofertas de ejemplo** creadas automáticamente
- **Diferentes casos de uso**: suscripciones, ofertas temporales, paquetes anuales
- **Múltiples monedas y rangos de precios**
- **Relaciones semánticas** configuradas
- **Metadata JSON** con configuraciones avanzadas

## 📈 Casos de Uso Empresariales

### 1. Gestión de Campañas Comerciales

```python
# Oferta Black Friday con metadata avanzada
{
  "name": "Oferta Black Friday - CRM Premium",
  "code": "BF2024_CRM_PREM",
  "price": 1400.00,
  "valid_from": "2025-06-06",
  "valid_until": "2025-07-06",
  "metadata": {
    "campaign": "black_friday_2024",
    "discount_percentage": 30,
    "priority": "high"
  }
}
```

### 2. Suscripciones y Renovaciones

```python
# Paquete anual con auto-renovación
{
  "name": "Consultoría Estratégica - Paquete Anual",
  "auto_renew": true,
  "duration_days": 365,
  "price": 25000.00
}
```

### 3. Segmentación Semántica

```python
# Oferta dirigida a industrias y funciones específicas
offering.related_industries.set([tech_industry, fintech_industry])
offering.related_functions.set([cto_function, dev_manager_function])
offering.channels.set([web_channel, email_channel])
```

### 4. Analytics y Reportes

- **Dashboard ejecutivo** con métricas clave
- **Análisis de performance** por canal y producto
- **Segmentación de mercado** basada en campo semántico
- **Forecasting** de ingresos por ofertas activas
- **ROI por canal** y segmento

## 🚀 Performance y Escalabilidad

### Optimizaciones Implementadas

```python
# Consultas optimizadas en ViewSets
queryset = ProductOffering.objects.select_related(
    'product', 'product__category', 'product__category__division'
).prefetch_related(
    'channels', 'seats', 'target_segments', 'related_industries',
    'related_functions', 'descriptors', 'tags'
)

# Índices de base de datos
class Meta:
    indexes = [
        models.Index(fields=['is_active']),
        models.Index(fields=['valid_from']),
        models.Index(fields=['valid_until']),
        models.Index(fields=['currency_code']),
    ]
```

### Capacidades

- **Filtros complejos** con performance óptima
- **Paginación automática** en todos los listados
- **Consultas N+1** eliminadas
- **Serializers contextuales** para diferentes casos de uso
- **Cache** preparado para implementar en analytics

## 🧠 ¿Por qué separar de `products`?

Separar `ProductOffering` en su propia app permite:

- ✅ **Mantener el catálogo limpio** y estructurado
- ✅ **Separar conceptos**: _valor_ (producto) vs _comercialización_ (oferta)
- ✅ **Múltiples ofertas por producto** con diferentes condiciones
- ✅ **Escalar con lógica comercial compleja** (campañas, A/B testing, reglas dinámicas)
- ✅ **Analytics específicos** de performance comercial
- ✅ **Flexibilidad temporal** (ofertas que nacen y mueren)

## 🎯 Product Integration Enhancements

### ✅ Integración con Campañas

La app `offers` ahora está **completamente integrada** con el sistema de campañas:

- **Relación directa**: Las campañas pueden targetear ofertas específicas via `target_offers`
- **Analytics compartidos**: Métricas de performance de ofertas en campañas
- **Compatibilidad automática**: API para encontrar ofertas compatibles con productos objetivo
- **Bundles soportados**: Las ofertas pueden apuntar a productos bundle via `product.included_products`

### 🔗 Arquitectura de Relaciones

```python
# ProductOffering → Product (ForeignKey)
class ProductOffering(BaseUUIDModelWithActiveStatus):
    product = models.ForeignKey('products.Product', ...)
    
# Campaign → ProductOffering (ManyToMany)
class Campaign(BaseUUIDModelWithActiveStatus):
    target_offers = models.ManyToManyField('offers.ProductOffering', ...)
    target_products = models.ManyToManyField('products.Product', ...)
    target_categories = models.ManyToManyField('products.ProductCategory', ...)
```

### 📊 Analytics Integrados

- **Performance por oferta**: Métricas de conversión y revenue por oferta en campañas
- **Análisis de bundles**: Estadísticas específicas para productos bundle
- **Resumen de targeting**: Conteos y totales de productos, categorías y ofertas objetivo
- **Ofertas compatibles**: API para encontrar ofertas que coincidan con productos objetivo

## 🔮 Extensiones Futuras

La app `offers` está diseñada para extenderse con:

- [x] **Integración con campañas** (`campaigns` app) ✅ **IMPLEMENTADO**
- [ ] **Soporte para bundles dinámicos** y upsells
- [ ] **Motor de reglas de elegibilidad** y precios personalizados
- [ ] **A/B testing** de ofertas
- [ ] **Análisis de conversion** por canal
- [ ] **Recomendaciones automáticas** basadas en perfil semántico
- [ ] **Integración con pasarelas de pago**
- [ ] **Workflows de aprobación** para ofertas

## 🛠️ Comandos de Gestión

### Desarrollo

```bash
# Migraciones
python manage.py makemigrations offers
python manage.py migrate offers

# Crear datos de prueba
python create_offers_data.py

# Shell de prueba
python manage.py shell
>>> from offers.models import ProductOffering
>>> ProductOffering.objects.filter(is_currently_valid=True)
```

### Testing

```bash
# Ejecutar tests
python manage.py test offers

# Verificar API
curl http://localhost:8000/api/offers/offerings/
curl http://localhost:8000/api/offers/offerings/analytics/
curl http://localhost:8000/api/offers/offerings/currently_valid/
```

## 📍 URLs Disponibles

### Frontend/Desarrollo

- **Lista de ofertas**: http://localhost:8000/api/offers/offerings/
- **Admin de Django**: http://localhost:8000/admin/offers/productoffering/
- **Analytics**: http://localhost:8000/api/offers/offerings/analytics/
- **Ofertas válidas**: http://localhost:8000/api/offers/offerings/currently_valid/

### Documentación API

La API sigue las convenciones REST estándar con filtros avanzados, búsquedas semánticas, paginación automática y analytics empresariales.

---

## ✅ Resumen de Implementación

### ✅ Completado 100%

1. **✅ Modelo ProductOffering** con relaciones semánticas completas
2. **✅ Serializers contextuales** para diferentes casos de uso
3. **✅ ViewSet completo** con 10 endpoints especializados
4. **✅ Filtros avanzados** y búsquedas semánticas
5. **✅ Analytics empresariales** con dashboard completo
6. **✅ Interface administrativa** optimizada
7. **✅ Tests unitarios** y de integración
8. **✅ Datos de prueba** realistas
9. **✅ Documentación completa**
10. **✅ Optimizaciones de performance**
11. **✅ Product Integration Enhancements** con campañas
12. **✅ Relación ForeignKey** optimizada con productos

### 🎯 Estado Actual: FUNCIONAL CON MEJORAS RECIENTES

La aplicación `offers` está **funcionalmente completa y estable**, siguiendo todos los patrones de calidad de BackboneOS. **Recientemente actualizada** con fixes críticos que resuelven problemas de serialización, validación y autenticación. Lista para uso en producción con monitoreo de los endpoints restantes.

### 🔧 Mejoras Recientes Implementadas

- **✅ Serialización UUID**: Corregido problema de comparación UUID vs string en API
- **✅ Validación de Fechas**: Fix en tests de validación temporal de ofertas
- **✅ Autenticación**: Configuración mejorada de ALLOWED_HOSTS para testing
- **✅ Relaciones de Productos**: Corregido acceso a relaciones ManyToMany en serializers
- **✅ Tests de Negocio**: Validaciones de precio y lógica comercial corregidas
- **Tests**: ver [docs/TESTING.md](../../docs/TESTING.md)

## Documentación

- [docs/APPS.md](../../docs/APPS.md)
- [docs/TESTING.md](../../docs/TESTING.md)
- [backend/README.md](../README.md)

---

© BackboneOS — Sistema de gestión comercial de nueva generación.
