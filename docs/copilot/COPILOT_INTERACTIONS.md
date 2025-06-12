# COPILOT: Aplicación Interactions

## 🎯 Propósito

Sistema completo de **Customer Journey** con analytics empresariales avanzados.

## 📊 Modelos del Customer Journey (8 modelos)

### Medium

```python
# Canal de comunicación (email, phone, web, etc.)
class Medium(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # digital, traditional, direct
    cost_per_interaction = models.DecimalField(max_digits=10, decimal_places=2)
```

### Channel

```python
# Fuente específica dentro de un medium
class Channel(models.Model):
    name = models.CharField(max_length=100)
    medium = models.ForeignKey(Medium)
    is_owned = models.BooleanField(default=True)  # owned vs paid media
```

### Action

```python
# Tipo de acción en el customer journey
class Action(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # awareness, consideration, decision
    conversion_weight = models.DecimalField(max_digits=5, decimal_places=2)
```

### Agent

```python
# Agente que ejecuta la acción (persona o sistema)
class Agent(models.Model):
    agent_type = models.CharField(max_length=20)  # human, system, automated
    identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
```

### Session

```python
# Sesión de interacciones relacionadas
class Session(models.Model):
    entity = models.ForeignKey('entities.Person' | 'entities.Organization')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True)
    session_type = models.CharField(max_length=50)
```

### Touchpoint

```python
# Punto específico de contacto configurado
class Touchpoint(models.Model):
    name = models.CharField(max_length=100)
    channel = models.ForeignKey(Channel)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
```

### Interaction

```python
# Interacción individual en el customer journey
class Interaction(models.Model):
    entity = models.ForeignKey('entities.Person' | 'entities.Organization')
    session = models.ForeignKey(Session, null=True)
    action = models.ForeignKey(Action)
    touchpoint = models.ForeignKey(Touchpoint)
    agent = models.ForeignKey(Agent, null=True)
    timestamp = models.DateTimeField()
    metadata = models.JSONField(default=dict)
    outcome = models.CharField(max_length=50)
```

### InteractionOutcome

```python
# Resultado específico de interacciones
class InteractionOutcome(models.Model):
    interaction = models.ForeignKey(Interaction)
    outcome_type = models.CharField(max_length=50)
    outcome_value = models.JSONField(default=dict)
    measured_at = models.DateTimeField()
```

## 🚀 Endpoints API (27 endpoints completos)

### Mediums y Channels

```
GET    /api/interactions/mediums/              # Lista mediums
POST   /api/interactions/mediums/              # Crear medium
GET    /api/interactions/mediums/{id}/analytics/ # Analytics por medium

GET    /api/interactions/channels/             # Lista channels
POST   /api/interactions/channels/             # Crear channel
GET    /api/interactions/channels/{id}/performance/ # Performance por channel
```

### Actions y Agents

```
GET    /api/interactions/actions/              # Lista actions
POST   /api/interactions/actions/              # Crear action
GET    /api/interactions/actions/{id}/conversion-rates/ # Tasas de conversión

GET    /api/interactions/agents/               # Lista agents
POST   /api/interactions/agents/               # Crear agent
GET    /api/interactions/agents/{id}/performance/ # Performance por agent
```

### Sessions y Customer Journey

```
GET    /api/interactions/sessions/             # Lista sessions
POST   /api/interactions/sessions/             # Crear session
GET    /api/interactions/sessions/{id}/journey/ # Customer journey completo
GET    /api/interactions/sessions/{id}/analytics/ # Analytics de sesión

GET    /api/interactions/touchpoints/          # Lista touchpoints
POST   /api/interactions/touchpoints/          # Crear touchpoint
PUT    /api/interactions/touchpoints/{id}/     # Actualizar configuración
```

### Interactions Core

```
GET    /api/interactions/interactions/         # Lista interacciones
POST   /api/interactions/interactions/         # Crear interacción
GET    /api/interactions/interactions/{id}/    # Detalle interacción
GET    /api/interactions/interactions/analytics/ # Analytics globales

GET    /api/interactions/outcomes/             # Lista outcomes
POST   /api/interactions/outcomes/             # Crear outcome
```

### Analytics Empresariales

```
GET    /api/interactions/customer-journey-analytics/ # Analytics completos
GET    /api/interactions/conversion-funnel/          # Embudo de conversión
GET    /api/interactions/attribution-analysis/       # Análisis de atribución
GET    /api/interactions/cohort-analysis/            # Análisis de cohortes
GET    /api/interactions/retention-metrics/          # Métricas de retención
```

## 📈 Analytics Empresariales

### Customer Journey Completo

- Mapeo de todas las interacciones por entidad
- Análisis de patrones de comportamiento
- Identificación de puntos de fricción
- Optimización de touchpoints

### Conversion Funnel

- Embudo de conversión por etapas
- Tasas de conversión por action
- Análisis de drop-off points
- Optimización de journey paths

### Attribution Analysis

- Atribución first-touch y last-touch
- Modelos de atribución multi-touch
- Contribución por medium y channel
- ROI por touchpoint

### Performance Metrics

- Métricas por agent y touchpoint
- Análisis de efectividad de campaigns
- Comparación de mediums y channels
- KPIs de customer engagement

## 💡 Patrones de Uso

### Registrar Customer Journey

```python
# Crear sesión y registrar interacciones
session_data = {
    "entity": person_id,
    "session_type": "website_visit",
    "interactions": [
        {
            "action": "page_view",
            "touchpoint": "homepage",
            "metadata": {"page_url": "/", "duration": 30}
        },
        {
            "action": "form_submission",
            "touchpoint": "contact_form",
            "outcome": "lead_generated"
        }
    ]
}
```

### Analytics por Entidad

```python
# Customer journey específico
/api/interactions/sessions/?entity={entity_id}
/api/interactions/interactions/?entity={entity_id}&ordering=-timestamp

# Analytics de comportamiento
/api/interactions/customer-journey-analytics/?entity={entity_id}
```

### Performance de Touchpoints

```python
# Análisis de efectividad
/api/interactions/touchpoints/{id}/performance/
/api/interactions/channels/{id}/performance/
/api/interactions/mediums/{id}/analytics/
```

## 🔍 Filtrado y Búsqueda

### Por Dimensiones Temporales

```python
?start_date=2024-01-01&end_date=2024-12-31
?last_30_days=true
?cohort_month=2024-06
```

### Por Contexto Empresarial

```python
?medium=email&channel=newsletter
?action_category=consideration
?outcome=conversion
?agent_type=human
```

### Analytics Avanzados

```python
?group_by=medium,channel
?segment_by=entity_type
?funnel_analysis=true
?attribution_model=last_touch
```

## ⚡ Optimizaciones

### Índices Estratégicos

- Búsqueda por timestamp y entity
- Filtrado por medium, channel, action
- Agregaciones por outcome y session
- Consultas de analytics empresariales

### Consultas Optimizadas

```python
# Prefetch para analytics
Interaction.objects.select_related(
    'action', 'touchpoint__channel__medium', 'agent'
).prefetch_related(
    'outcomes'
)
```

## 🧪 Testing y Datos de Prueba

### Tests Completos

```bash
# Suite de pruebas 100% exitosa
docker-compose exec backend python manage.py test interactions

# Tests específicos de analytics
docker-compose exec backend python manage.py test interactions.tests.AnalyticsTests
```

### Datos de Demostración

```python
# Crear customer journey de demo
docker-compose exec backend python manage.py shell
>>> exec(open('demo_interactions_advanced.py').read())
```

### Fixtures Incluidas

- `fixtures_mediums.json` - Mediums iniciales
- `fixtures_channels.json` - Channels por medium
- `fixtures_actions.json` - Actions por categoría
- `initial_action_types.json` - Tipos de acción estándar

## 🔗 Integración con Otras Apps

### Entities

- Customer journey por Person y Organization
- Segmentación de interacciones por perfil semántico
- Analytics demográficos de comportamiento

### Products

- Interacciones relacionadas con productos específicos
- Customer journey de discovery y purchase
- Analytics de product engagement

### Offers y Campaigns

- Tracking de efectividad de ofertas
- Medición de performance de campañas
- Attribution analysis para initiatives comerciales

### World

- Contexto geográfico de interacciones
- Análisis por industria y segmento
- Clasificación cultural de comportamientos
