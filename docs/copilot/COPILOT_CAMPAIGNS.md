# COPILOT: Aplicación Campaigns

## 🎯 Propósito

Sistema de **campañas comerciales** con targeting semántico y analytics de performance.

## 📊 Modelos Principales

### Campaign

```python
# Campaña comercial completa
class Campaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    # Targeting semántico
    target_industries = models.ManyToManyField('world.Industry', blank=True)
    target_countries = models.ManyToManyField('world.Country', blank=True)
    target_organization_types = models.ManyToManyField('world.OrganizationType', blank=True)

    # Configuración temporal
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    # Presupuesto y objetivos
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey('world.Currency', default=1)
    target_audience_size = models.PositiveIntegerField(null=True, blank=True)

    # Objetivos de conversión
    conversion_goal = models.CharField(max_length=50, default='lead_generation')
    expected_conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    cost_per_conversion_target = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Estado y metadatos
    status = models.CharField(max_length=20, default='draft')  # draft, active, paused, completed
    campaign_type = models.CharField(max_length=50, default='marketing')
    priority_level = models.PositiveIntegerField(default=5)

    # Tracking
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### CampaignTouchpoint

```python
# Touchpoints específicos de la campaña
class CampaignTouchpoint(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='touchpoints')

    # Configuración del touchpoint
    name = models.CharField(max_length=200)
    touchpoint_type = models.CharField(max_length=50)  # email, social, web, phone

    # Contenido y configuración
    content = models.TextField()
    content_format = models.CharField(max_length=20, default='html')  # html, text, json

    # Targeting específico del touchpoint
    target_segment = models.CharField(max_length=100, blank=True)
    personalization_rules = models.JSONField(default=dict)

    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    execution_order = models.PositiveIntegerField(default=1)

    # Analytics y tracking
    is_active = models.BooleanField(default=True)
    delivery_status = models.CharField(max_length=20, default='pending')

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🚀 Endpoints API (7 endpoints completos)

### CRUD de Campañas

```
GET    /api/campaigns/campaigns/              # Lista campañas
POST   /api/campaigns/campaigns/              # Crear campaña
GET    /api/campaigns/campaigns/{id}/         # Detalle campaña
PUT    /api/campaigns/campaigns/{id}/         # Actualizar campaña
DELETE /api/campaigns/campaigns/{id}/         # Eliminar campaña
```

### Gestión de Touchpoints

```
GET    /api/campaigns/campaigns/{id}/touchpoints/ # Touchpoints de campaña
POST   /api/campaigns/campaigns/{id}/touchpoints/ # Crear touchpoint
```

### Analytics de Campañas

```
GET    /api/campaigns/analytics/overview/     # Dashboard de campañas
```

## 📈 Analytics Empresariales

### Dashboard de Campañas

- Performance general de campañas activas
- ROI por campaña y tipo
- Análisis de conversión por targeting
- Métricas de engagement y alcance

### Performance Analysis

- Cost per conversion por campaña
- Conversion rate por segmento target
- Análisis de budget vs results
- Optimización de touchpoints

### Targeting Analytics

- Efectividad por industria target
- Performance por geografía
- Análisis por tipo de organización
- Optimización de audience segmentation

## 💡 Patrones de Uso

### Crear Campaña Completa

```python
campaign_data = {
    "name": "Q4 Enterprise CRM Campaign",
    "description": "Campaña dirigida a empresas tecnológicas para CRM Enterprise",

    # Targeting semántico
    "target_industries": [5, 8],  # Technology, Software
    "target_countries": [1, 2, 3],  # USA, Canada, Mexico
    "target_organization_types": [1],  # Corporation

    # Configuración temporal
    "start_date": "2024-10-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",

    # Presupuesto y objetivos
    "budget": "50000.00",
    "currency": 1,  # USD
    "target_audience_size": 1000,
    "conversion_goal": "qualified_lead",
    "expected_conversion_rate": "3.5",
    "cost_per_conversion_target": "150.00",

    # Metadatos
    "campaign_type": "lead_generation",
    "priority_level": 8,
    "status": "draft"
}
```

### Configurar Touchpoints

```python
touchpoint_data = {
    "campaign": campaign_id,
    "name": "Email Sequence - CRM Benefits",
    "touchpoint_type": "email",
    "content": "<html>Email content with personalization</html>",
    "content_format": "html",

    # Targeting específico
    "target_segment": "enterprise_prospects",
    "personalization_rules": {
        "industry_specific_content": True,
        "company_size_targeting": "500+",
        "decision_maker_focus": "C_level"
    },

    # Scheduling
    "scheduled_at": "2024-10-15T09:00:00Z",
    "execution_order": 1
}
```

### Analytics y Filtrado

```python
# Performance por segmento
/api/campaigns/analytics/overview/?segment_by=industry&time_period=current_quarter

# Campañas por estado y tipo
/api/campaigns/campaigns/?status=active&campaign_type=lead_generation

# Análisis de ROI
/api/campaigns/analytics/overview/?metric=roi&group_by=target_countries
```

## 🔍 Funcionalidades CRM

### Targeting Semántico Avanzado

- Segmentación por industria específica
- Targeting geográfico multinacional
- Clasificación por tipo de organización
- Combinación de criterios de targeting

### Gestión de Presupuesto

- Control de budget por campaña
- Tracking de cost per conversion
- Análisis de ROI en tiempo real
- Optimización de spend allocation

### Orchestration de Touchpoints

- Secuenciación de comunicaciones
- Personalización por segmento
- Scheduling inteligente
- Multi-channel coordination

### Objetivos de Conversión

- Definición de goals específicos
- Tracking de conversion rates
- Análisis de customer journey
- Optimización de conversion paths

## ⚡ Optimizaciones

### Índices Estratégicos

```python
# Filtrado por targeting
INDEX: (target_industries, status, start_date, end_date)
INDEX: (target_countries, campaign_type, priority_level)
INDEX: (status, created_at, budget)

# Analytics y performance
INDEX: (conversion_goal, expected_conversion_rate)
INDEX: (touchpoints.scheduled_at, touchpoints.delivery_status)
```

### Consultas Optimizadas

```python
# Prefetch para evitar N+1
Campaign.objects.select_related(
    'currency', 'created_by'
).prefetch_related(
    'target_industries',
    'target_countries',
    'target_organization_types',
    'touchpoints'
)
```

### Cálculos de Performance

```python
# Métricas calculadas dinámicamente
def calculate_roi(self):
    total_revenue = self.get_attributed_revenue()
    total_cost = self.budget or 0
    if total_cost > 0:
        return ((total_revenue - total_cost) / total_cost) * 100
    return 0

def calculate_actual_conversion_rate(self):
    total_interactions = self.get_total_interactions()
    total_conversions = self.get_total_conversions()
    if total_interactions > 0:
        return (total_conversions / total_interactions) * 100
    return 0
```

## 🧪 Testing y Datos

### Tests de Campañas

```bash
# Suite completa de tests
docker-compose exec backend python manage.py test campaigns

# Tests específicos de targeting
docker-compose exec backend python manage.py test campaigns.tests.TargetingTests

# Tests de analytics
docker-compose exec backend python manage.py test campaigns.tests.AnalyticsTests
```

### Datos de Demostración

```python
# Crear campañas de demo
docker-compose exec backend python manage.py shell
>>> exec(open('create_campaigns_data.py').read())
```

### Validaciones de Negocio

```python
def clean(self):
    # Validar fechas
    if self.end_date and self.end_date <= self.start_date:
        raise ValidationError("end_date debe ser posterior a start_date")

    # Validar presupuesto
    if self.budget and self.budget <= 0:
        raise ValidationError("budget debe ser mayor a 0")

    # Validar targeting
    if not any([
        self.target_industries.exists(),
        self.target_countries.exists(),
        self.target_organization_types.exists()
    ]):
        raise ValidationError("Debe especificar al menos un criterio de targeting")
```

## 📊 Métricas de Performance

### KPIs de Campañas

- **Reach**: Alcance total de la campaña
- **Engagement Rate**: Tasa de engagement por touchpoint
- **Conversion Rate**: Tasa de conversión por objetivo
- **Cost per Conversion**: Costo por conversión efectiva
- **ROI**: Retorno de inversión de la campaña
- **Customer Acquisition Cost**: Costo de adquisición por cliente

### Analytics de Touchpoints

- **Delivery Rate**: Tasa de entrega exitosa
- **Open Rate**: Tasa de apertura (email/content)
- **Click-through Rate**: CTR por touchpoint
- **Response Rate**: Tasa de respuesta por canal

## 🔗 Integración con Otras Apps

### Entities (Targeting)

```python
# Segmentación por perfil semántico
Person.individual_profile.industry → target_industries
Organization.industry → target_industries
Organization.organization_type → target_organization_types
PhysicalAddress.country → target_countries
```

### Interactions (Tracking)

```python
# Customer journey de campañas
Interaction.metadata = {
    "campaign_id": campaign.id,
    "touchpoint_id": touchpoint.id,
    "campaign_action": "touchpoint_engagement"
}
```

### Offers (Promoción)

```python
# Ofertas promocionadas en campañas
CampaignTouchpoint.content → Referencias a ProductOffering
Campaign.promoted_offerings → Ofertas específicas de la campaña
```

### Products (Promoción)

```python
# Productos promocionados
CampaignTouchpoint.content → Product references
Campaign targeting → Productos relevantes por industria
```

### World (Contexto)

```python
# Datos de referencia para targeting
target_industries → world.Industry
target_countries → world.Country
target_organization_types → world.OrganizationType
currency → world.Currency
```
