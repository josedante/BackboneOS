# API Reference - BackboneOS

## 🔗 Estructura de la API

### Endpoints Principales

#### Autenticación

```
POST /api/auth/login/          # Login JWT
POST /api/auth/refresh/        # Refresh token
POST /api/auth/logout/         # Logout
```

#### Usuarios

```
GET    /api/users/             # Lista de usuarios
GET    /api/users/{id}/        # Detalle de usuario
POST   /api/users/             # Crear usuario
PUT    /api/users/{id}/        # Actualizar usuario
DELETE /api/users/{id}/        # Eliminar usuario
```

#### Gestión de Entidades

```
/api/entities/people/              # Personas físicas
/api/entities/people/{id}/profile/ # Perfil semántico personal
/api/entities/organizations/       # Organizaciones
/api/entities/organizations/{id}/analytics/ # Analytics organizacional
/api/entities/contacts/            # Detalles de contacto
/api/entities/addresses/           # Direcciones físicas
```

#### Estructura Organizacional (Our Institution)

```
/api/our-institution/organization/     # Organización propietaria
/api/our-institution/divisions/        # Divisiones empresariales
/api/our-institution/seats/            # Sedes y oficinas
/api/our-institution/units/            # Unidades (con jerarquía)
/api/our-institution/positions/        # Posiciones/cargos
/api/our-institution/teams/            # Equipos transversales
```

#### Campo Semántico (World)

```
/api/world/countries/          # Países
/api/world/industries/         # Industrias (jerárquicas)
/api/world/functions/          # Funciones organizacionales
/api/world/skills/             # Habilidades y competencias
/api/world/market-segments/    # Segmentos de mercado
/api/world/descriptors/        # Descriptores globales
/api/world/tags/              # Sistema de tags
```

#### Gestión de Productos

```
/api/products/divisions/           # Divisiones organizacionales
/api/products/divisions/{id}/categories/  # Categorías por división
/api/products/divisions/{id}/products/    # Productos por división
/api/products/categories/          # Categorías (jerárquicas)
/api/products/categories/tree/     # Árbol completo de categorías
/api/products/products/            # CRUD productos
/api/products/products/search_advanced/  # Búsqueda semántica
/api/products/analytics/dashboard/ # Dashboard de analytics
```

#### Gestión de Ofertas Comerciales

```
/api/offers/offerings/             # CRUD completo de ofertas
/api/offers/offerings/choices/     # Choices para formularios
/api/offers/offerings/currently_valid/  # Ofertas válidas ahora
/api/offers/offerings/by_product/  # Ofertas por producto específico
/api/offers/offerings/by_channel/  # Ofertas por canal específico
/api/offers/offerings/analytics/   # Dashboard empresarial completo
/api/offers/offerings/{id}/duplicate/  # Duplicar oferta con relaciones
```

#### Gestión de Interacciones

```
/api/interactions/mediums/         # Medios de comunicación
/api/interactions/channels/        # Canales específicos
/api/interactions/action-types/    # Tipos de acciones
/api/interactions/actions/         # Acciones de usuario
/api/interactions/agents/          # Agentes (browsers, humans, bots)
/api/interactions/touchpoints/     # Puntos de contacto
/api/interactions/interactions/    # Interacciones del customer journey
/api/interactions/interactions/analytics/ # Analytics de interacciones
/api/interactions/agents/analytics/       # Analytics de agentes
/api/interactions/touchpoints/analytics/  # Analytics de touchpoints
```

#### Gestión de Campañas Comerciales

```
# CRUD de Campañas
/api/campaigns/campaigns/              # CRUD completo de campañas
/api/campaigns/campaigns/choices/      # Choices para formularios
/api/campaigns/campaigns/analytics/    # Dashboard completo de analytics

# Endpoints especializados de campañas
/api/campaigns/campaigns/active_now/      # Campañas activamente vigentes
/api/campaigns/campaigns/scheduled/       # Campañas programadas (futuras)
/api/campaigns/campaigns/{id}/product_analytics/    # Analytics de productos
/api/campaigns/campaigns/{id}/bundle_analytics/     # Analytics de bundles
/api/campaigns/campaigns/{id}/target_summary/       # Resumen de targeting
/api/campaigns/campaigns/{id}/compatible_offerings/ # Ofertas compatibles
/api/campaigns/campaigns/finished/        # Campañas ya finalizadas
/api/campaigns/campaigns/by_division/     # Campañas agrupadas por división
/api/campaigns/campaigns/by_team/         # Campañas agrupadas por equipo
/api/campaigns/campaigns/{id}/subcampaigns/  # Subcampañas de una campaña
/api/campaigns/campaigns/{id}/touchpoints/   # Touchpoints de una campaña
/api/campaigns/campaigns/{id}/duplicate/     # Duplicar campaña completa

# CRUD de Relaciones Campaña-Touchpoint
/api/campaigns/campaign-touchpoints/       # CRUD relaciones campaña-touchpoint
/api/campaigns/campaign-touchpoints/by_campaign/     # Touchpoints por campaña
/api/campaigns/campaign-touchpoints/by_touchpoint/   # Campañas por touchpoint
/api/campaigns/campaign-touchpoints/analytics/       # Analytics de relaciones
```

## 📊 Filtros y Capacidades Avanzadas

### Filtros Comunes

Todos los endpoints soportan:

- **Búsqueda**: `?search=término`
- **Ordenamiento**: `?ordering=campo,-campo_desc`
- **Paginación**: `?page=1&page_size=20`
- **Filtros específicos**: Según el modelo

### Capacidades Especiales

- **Filtros Jerárquicos**: Por división, unidad padre, etc.
- **Búsquedas Semánticas**: En nombres, códigos y descripciones
- **Métricas Automáticas**: Conteos automáticos en respuestas
- **Serializers Contextuales**: Diferentes niveles de detalle según el endpoint
