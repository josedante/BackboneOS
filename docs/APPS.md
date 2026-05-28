# Aplicaciones Django - BackboneOS

## 📱 Aplicaciones Implementadas

### ✅ World App - Campo Semántico Empresarial

**Ontología y taxonomías para CRM empresarial**

- **🌍 Clasificación Geográfica**: `Country`, `Region`
- **🏭 Ontología Sectorial**: `Industry` (jerárquica con sectores/subsectores)
- **👔 Taxonomía Organizacional**: `FunctionOrResponsibility`, `OrganizationType`, `Position`
- **🎯 Competencias**: `Skill`, `AcademicDegree`
- **📊 Segmentación**: `MarketSegment`, `DescriptorFamily`, `WorldDescriptor`
- **🏷️ Etiquetado**: `Tag` (sistema de folksonomía)

**Características**:

- **API REST Completa**: ViewSets con filtrado, búsqueda y ordenamiento
- **Serializers Duales**: Completos y "choice" para formularios
- **Optimización DB**: Índices estratégicos documentados
- **Admin Interface**: Gestión eficiente de datos jerárquicos

### ✅ Entities App - Sistema de Gestión de Entidades

**Núcleo semántico de personas y organizaciones**

**HTML UI:** Django templates at `/entities/` (tabbed people/organizations CRM; see [`docs/consolidation/FRONTEND_CONSOLIDATION.md`](consolidation/FRONTEND_CONSOLIDATION.md)).

- **👤 Personas**: `Person` (información demográfica + perfilado semántico)
- **🏢 Organizaciones**: `Organization` (entidades corporativas con clasificación)
- **📞 Contactos**: `ContactDetail` (sistema unificado de comunicación)
- **👔 Perfiles**: `IndividualProfile` (extensión semántica personal)
- **📍 Direcciones**: `PhysicalAddress` (gestión flexible de ubicaciones)

**Características CRM**:

- **Perfilado Semántico**: Integración con World App para clasificación
- **Analytics Organizacional**: Inteligencia de mercado y demografía
- **Compliance GDPR**: Consentimientos y gestión de privacidad
- **Contactos Verificados**: Sistema de validación omnicanal
- **Optimización Performance**: Índices estratégicos documentados

### ✅ Our Institution App - Sistema de Estructura Organizacional

**Gestión completa de la estructura organizacional propietaria**

- **🏢 Organización**: `OurOrganization` (identidad institucional única)
- **🏭 Divisiones**: `Division` (áreas empresariales: Tecnología, Comercial, Operaciones)
- **🏢 Unidades**: `Unit` (estructura jerárquica con soporte padre-hijo ilimitado)
- **👔 Posiciones**: `Position` (cargos específicos dentro de unidades)
- **👥 Equipos**: `Team` (equipos transversales por división)
- **🏬 Sedes**: `Seat` (ubicaciones físicas con categorización)

**Características Avanzadas**:

- **Jerarquía Sin Redundancia**: Arquitectura optimizada con constraints únicos contextuales
- **API REST Completa**: 6 endpoints con filtrado jerárquico y métricas automatizadas
- **Comandos de Gestión**: Automatización para crear estructura organizacional completa
- **Tests Comprensivos**: 14 tests unitarios con 100% de éxito
- **Métricas Automáticas**: Conteos de elementos relacionados en tiempo real
- **Navegación Semántica**: Paths completos y relaciones contextuales

### ✅ Products App - Sistema de Gestión de Productos

**Catálogo comercial avanzado con analytics**

- **🏢 Estructura Divisional**: `Division` (organización empresarial)
- **📂 Clasificación**: `ProductCategory` (jerárquica multi-nivel)
- **📦 Productos**: `Product` (entidad central con relaciones semánticas)
- **⚙️ Configuración**: `Modality`, `Customization`

**Características Avanzadas**:

- **Analytics Dashboard**: Métricas comerciales y de rendimiento
- **Pricing Multi-moneda**: Gestión avanzada de precios
- **Búsqueda Semántica**: Integración con World App
- **Filtrado Avanzado**: Por división, categoría, segmentos
- **Serializers Optimizados**: List/Detail/Create especializados

### ✅ Interactions App - Sistema de Interacciones

**Framework completo de gestión de customer journey**

- **🎯 Jobs-to-be-Done**: `Interaction` con etapas JTBD (8 modelos)
- **📡 Touchpoints**: `Touchpoint`, `TouchpointType` (puntos de contacto)
- **🔄 Sesiones**: `Session` (seguimiento de comportamiento)
- **🤖 Agentes**: `Agent` (browsers, humans, bots)
- **📢 Canales**: `Medium`, `Channel`, `Action`, `ActionType`

**Características Avanzadas**:

- **27 Endpoints API**: Completamente funcionales y testeados
- **Analytics Dashboard**: Métricas de customer journey y performance
- **Integración Semántica**: Conexión completa con World App
- **Performance Optimizada**: < 60ms tiempo promedio de respuesta
- **Framework JTBD**: Seguimiento completo del trabajo del cliente

### ✅ Offers App - Sistema de Ofertas Comerciales

**Sistema central de gestión de ofertas comerciales con:**

- **Centro de Comercialización**: Gestión completa de ofertas activas de la organización
- **Motor de Pricing**: Precios específicos y condiciones comerciales por oferta
- **Sistema Temporal**: Ofertas con vigencia limitada y renovación automática
- **Hub de Segmentación**: Targeting por canales, industrias, funciones y geografía
- **Analytics Comercial**: Insights de performance y ROI por oferta

**Características Avanzadas**:

- **Django HTML CRM**: `/offers/` — list, create, detail, delete (`offers_html` namespace; `@login_required`)
- **Segmentación Semántica**: Ofertas dirigidas por industria, función y geografía
- **Pricing Dinámico**: Precios específicos por canal y audiencia
- **Analytics Empresariales**: Dashboard completo con métricas de performance
- **Duplicación Inteligente**: Copiar ofertas con todas las relaciones
- **Validación Temporal**: Control automático de vigencia de ofertas
- **🔧 Fixes Recientes**: Serialización UUID, validación de fechas, autenticación
- **📊 Estado de Tests**: 89% éxito (83/93 tests pasando) - mejoras significativas

### ✅ Campaigns App - Sistema de Gestión de Campañas Comerciales

**Framework completo de campañas de marketing y ventas**

- **HTML CRM (consolidated frontend):** http://localhost:8000/campaigns/ — operator CRUD for campaigns and campaign–touchpoint links (`campaigns_html` namespace). DRF remains at `/api/campaigns/`.

- **🎯 Campañas**: `Campaign` (estructura planificada para promoción multi-canal)
- **📍 Touchpoints**: `CampaignTouchpoint` (relación campaña-punto de contacto)
- **📈 Embudo de Ventas**: Gestión por etapas (Ver, Pensar, Hacer, Cuidar)
- **🎨 Tipos de Contenido**: Afinidad, Categoría, Producto, Oferta, Marca
- **🏗️ Estructura Jerárquica**: Campañas padre e hijas para organización
- **🎯 Product Integration**: Targeting directo de productos, ofertas y categorías

**Características Avanzadas**:

- **Targeting Semántico**: Segmentación por industrias, funciones y geografía
- **🎯 Product Integration**: Targeting directo de productos, ofertas y categorías
- **📊 Analytics Avanzados**: Performance de productos, bundles y revenue
- **Gestión Temporal**: Campañas con fechas de inicio/fin y estado automático
- **Presupuesto Multi-nivel**: Control presupuestario por campaña y touchpoint
- **Analytics Dashboard**: Métricas de performance y ROI por campaña
- **API REST Completa**: 11 endpoints con filtrado avanzado y analytics
- **Duplicación Inteligente**: Copia de campañas con todas las relaciones
- **Touchpoints Ponderados**: Asignación de peso y prioridad por punto de contacto
- **🔧 Fixes Recientes**: Corrección de imports, campos de modelo y validaciones
- **📈 Índices Optimizados**: Índices compuestos para consultas frecuentes

### ✅ Users App

- Gestión de usuarios y autenticación
- Modelos de usuario extendidos
- Sistema JWT implementado
