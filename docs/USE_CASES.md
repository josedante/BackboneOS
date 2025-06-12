# Casos de Uso - BackboneOS

## 🎯 Casos de Uso del Sistema

### Campo Semántico para CRM

1. **Perfilado Semántico de Clientes**

   ```python
   # Construcción de perfil multidimensional
   client_profile = {
       'industry': Industry.objects.get(name="Financial Services"),
       'skills': Skill.objects.filter(name__in=["Python", "Data Analysis"]),
       'market_segments': MarketSegment.objects.filter(descriptors__name="Enterprise")
   }
   ```

2. **Segmentación Conceptual**
   ```python
   # Segmentación basada en ontología empresarial
   tech_clients = Client.objects.filter(
       industry__parent__name="Technology",
       market_segments__descriptors__name="SaaS"
   )
   ```

### Gestión de Entidades para CRM

1. **Perfilado Semántico de Personas**

   ```python
   # Perfil completo con clasificación semántica
   person_profile = person.get_semantic_profile()
   # Retorna: academic_degree, industries, skills, functions, comunicación
   ```

2. **Analytics Organizacional**

   ```python
   # Segmentación de organizaciones por contexto semántico
   tech_orgs = Organization.objects.select_related('industry', 'country')
       .filter(industry__parent__name="Technology", is_active=True)
   ```

3. **Gestión de Contactos Verificados**
   ```python
   # Contactos principales y verificados para marketing
   verified_contacts = ContactDetail.objects.filter(
       is_verified=True, is_primary=True, is_active=True
   )
   ```

### Estructura Organizacional para Gestión Interna

1. **Navegación Jerárquica Organizacional**

   ```python
   # Estructura completa con paths y métricas
   from our_institution.models import Division, Unit, Position

   # Divisiones con conteos automáticos
   divisions = Division.objects.filter(is_active=True)
   for division in divisions:
       print(f"{division.name}: {division.units_count} unidades, {division.positions_count} posiciones")

   # Unidades con jerarquía completa
   units = Unit.objects.select_related('division', 'parent')
   for unit in units:
       print(unit.full_path)  # "Tecnología y Desarrollo > Gerencia de Desarrollo > Equipo Frontend"
   ```

2. **API para Gestión Organizacional**

   ```bash
   # Endpoints con filtrado jerárquico
   GET /api/our-institution/divisions/
   GET /api/our-institution/units/?division=1
   GET /api/our-institution/positions/?unit=1
   GET /api/our-institution/teams/?division=1
   ```

3. **Comandos de Gestión Automatizada**

   ```bash
   # Crear estructura organizacional completa
   docker-compose exec backend python manage.py create_organization_structure

   # Métricas esperadas: 1 organización, 3 divisiones, 8 unidades, 10 posiciones, 4 equipos, 2 sedes
   ```

### Sistema de Productos para Comercial

1. **Catalogación Inteligente**

   ```python
   # Organización por divisiones y categorías
   tech_products = Product.objects.filter(
       category__division__code="TECH",
       category__parent__name="Desarrollo Web"
   )
   ```

2. **Analytics Comerciales**
   ```python
   # Dashboard de métricas de productos
   GET /api/products/analytics/dashboard/
   GET /api/products/analytics/divisions/
   GET /api/products/analytics/pricing/
   ```

### Sistema de Ofertas Comerciales

1. **Gestión de Ofertas con Segmentación**

   ```python
   # Ofertas específicas por canal y audiencia
   enterprise_offers = ProductOffering.objects.filter(
       target_industries__name="Financial Services",
       target_channels__name="Enterprise Sales",
       is_active=True,
       valid_from__lte=timezone.now(),
       valid_until__gte=timezone.now()
   )
   ```

2. **Analytics de Performance Comercial**

   ```python
   # Dashboard de métricas empresariales
   GET /api/offers/offerings/analytics/
   # Retorna: total de ofertas, por estado, por canal, métricas temporales
   ```

3. **Duplicación Inteligente de Ofertas**

   ```bash
   # Duplicar oferta con todas las relaciones
   POST /api/offers/offerings/{id}/duplicate/
   # Crea copia exacta con industrias, canales, funciones y geografías
   ```

### Framework de Interacciones Customer Journey

1. **Seguimiento Jobs-to-be-Done**

   ```python
   # Interacciones por etapa del trabajo del cliente
   awareness_interactions = Interaction.objects.filter(
       jtbd_stage='awareness',
       touchpoint__touchpoint_class__name='Digital Marketing'
   )
   ```

2. **Analytics de Touchpoints**

   ```python
   # Performance de puntos de contacto
   GET /api/interactions/touchpoints/analytics/
   # Métricas: interacciones por touchpoint, conversión, efectividad
   ```

3. **Optimización de Canales**

   ```python
   # Analytics de canales de comunicación
   GET /api/interactions/channels/analytics/
   # Insights: volume por canal, performance, ROI
   ```

### Sistema de Campañas Comerciales

1. **Gestión de Campañas Multi-canal**

   ```python
   # Campañas con targeting semántico
   from campaigns.models import Campaign, CampaignTouchpoint

   # Crear campaña con segmentación inteligente
   campaign = Campaign.objects.create(
       name="Lead Generation MBA Q1 2025",
       code="LG-MBA-Q1",
       description="Campaña de generación de leads para MBA",
       start_date=date(2025, 1, 1),
       end_date=date(2025, 3, 31),
       budget=25000.00,
       content_type="product",
       funnel_stage="think",
       division=Division.objects.get(code="MKT")
   )

   # Asignar targeting semántico
   campaign.related_industries.set([
       Industry.objects.get(name="Financial Services"),
       Industry.objects.get(name="Technology")
   ])
   campaign.target_segments.set([
       MarketSegment.objects.get(name="Enterprise"),
       MarketSegment.objects.get(name="C-Level")
   ])
   ```

2. **Asignación de Touchpoints con Peso y Prioridad**

   ```python
   # Configurar touchpoints para la campaña
   touchpoints_config = [
       {"touchpoint": "Landing Page MBA", "weight": 3.0, "priority": 1, "budget": 8000},
       {"touchpoint": "Email Newsletter", "weight": 2.0, "priority": 2, "budget": 5000},
       {"touchpoint": "LinkedIn Ads", "weight": 2.5, "priority": 1, "budget": 7000},
       {"touchpoint": "Webinar Registration", "weight": 4.0, "priority": 1, "budget": 5000}
   ]

   for config in touchpoints_config:
       touchpoint = Touchpoint.objects.get(name=config["touchpoint"])
       CampaignTouchpoint.objects.create(
           campaign=campaign,
           touchpoint=touchpoint,
           weight=config["weight"],
           priority=config["priority"],
           budget_allocated=config["budget"],
           expected_conversions=random.randint(50, 200)
       )
   ```

3. **Analytics de Performance de Campañas**

   ```python
   # Dashboard completo de analytics
   GET /api/campaigns/campaigns/analytics/

   # Respuesta esperada:
   {
       "total_campaigns": 25,
       "active_campaigns": 8,
       "scheduled_campaigns": 5,
       "finished_campaigns": 12,
       "total_budget": "125000.00",
       "average_budget": "5000.00",
       "by_division": [
           {"division__name": "Marketing", "count": 15, "total_budget": "75000.00"},
           {"division__name": "Ventas", "count": 10, "total_budget": "50000.00"}
       ],
       "by_funnel_stage": [
           {"funnel_stage": "see", "count": 8},
           {"funnel_stage": "think", "count": 6},
           {"funnel_stage": "do", "count": 7},
           {"funnel_stage": "care", "count": 4}
       ],
       "top_channels": [
           {"channel__name": "Email", "campaign_count": 12},
           {"channel__name": "Social Media", "campaign_count": 8}
       ]
   }
   ```

4. **Filtrado Avanzado por Estado y Segmentación**

   ```python
   # Campañas activas con filtros específicos
   GET /api/campaigns/campaigns/active_now/?funnel_stage=think&content_type=product

   # Campañas por división y presupuesto
   GET /api/campaigns/campaigns/?division=1&budget_min=10000&budget_max=50000

   # Búsqueda semántica en campañas
   GET /api/campaigns/campaigns/?search=MBA&related_industries=1
   ```

5. **Duplicación y Gestión de Subcampañas**

   ```python
   # Duplicar campaña exitosa
   POST /api/campaigns/campaigns/{id}/duplicate/
   # Crea copia con todas las relaciones: touchpoints, industrias, segmentos

   # Crear estructura jerárquica
   parent_campaign = Campaign.objects.get(code="BF2024")

   subcampaigns = [
       {"name": "Black Friday - Email", "code": "BF2024-EMAIL"},
       {"name": "Black Friday - Social", "code": "BF2024-SOCIAL"},
       {"name": "Black Friday - Retargeting", "code": "BF2024-RETARG"}
   ]

   for sub_data in subcampaigns:
       Campaign.objects.create(
           parent=parent_campaign,
           name=sub_data["name"],
           code=sub_data["code"],
           start_date=parent_campaign.start_date,
           end_date=parent_campaign.end_date,
           funnel_stage=parent_campaign.funnel_stage,
           division=parent_campaign.division
       )
   ```

6. **Analytics de Relaciones Campaña-Touchpoint**

   ```python
   # Métricas de asignación de touchpoints
   GET /api/campaigns/campaign-touchpoints/analytics/

   # Touchpoints por campaña específica
   GET /api/campaigns/campaigns/{id}/touchpoints/

   # Campañas que usan un touchpoint específico
   GET /api/campaigns/campaign-touchpoints/by_touchpoint/?touchpoint=5
   ```
