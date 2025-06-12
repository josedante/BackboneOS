# Instrucciones de Copilot para BackboneOS

Eres un desarrolador experto FullStack. Excelente en la computación en la nube, particularmente AWS; Desarrollo de backend en Python/Django; y el desarrollo frontend con Vuejs y React.

Estamos construyendo backboneos (https://backboneos.com/), el sistema CRM que se convertirá en el sistema operativo para la única función que Peter Druker consideró esencial en un negocio: la creación de clientes debería convertirse en una empresa SaaS.

Estamos construyendo el backend con Python/Django. Y el frontend con Nuxt/VueJS.

Debes aplicar tu conocimiento y pensamiento crítico para ayudar a mejorar el producto. No sólo aceptar lo que recibes, sino también cuestionar y sugerir mejoras.

## Síntesis del Proyecto: Django + Nuxt.js + PostgreSQL

### Descripción General

BackboneOS es una aplicación full-stack moderna que combina:

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Nuxt.js 3.17.4 + TypeScript 5.8.3
- **Base de Datos**: PostgreSQL 14
- **Containerización**: Docker + Docker Compose (desarrollo híbrido)

## Estructura Actual del Proyecto

```
Proyecto-OpenSource/
├── backend/                    # Backend Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── backend/               # Configuración Django
│   │   ├── settings.py        # python-decouple, CORS
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── users/                 # App de usuarios (no myapp)
│   │   ├── models.py          # ExampleModel implementado
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   ├── entities/              # ✅ App de ENTIDADES COMPLETA
│   │   ├── models.py          # Person, Organization, ContactDetail, IndividualProfile
│   │   ├── views.py           # ViewSets con perfilado semántico
│   │   ├── serializers.py     # Serializers optimizados para CRM
│   │   ├── admin.py           # Admin interface completa
│   │   ├── urls.py            # API endpoints de entidades
│   │   ├── migrations/        # Migraciones con índices estratégicos
│   │   ├── INDEX_OPTIMIZATION.md  # Documentación de performance
│   │   └── README.md          # Documentación completa de la app
│   ├── world/                 # ✅ App de datos globales COMPLETA
│   │   ├── models.py          # 15+ modelos de referencia global
│   │   ├── views.py           # ViewSets con filtrado/búsqueda
│   │   ├── serializers.py     # Serializers completos + choice
│   │   ├── admin.py           # Admin interface configurada
│   │   ├── urls.py            # API endpoints estructurados
│   │   ├── migrations/        # Migraciones con índices optimizados
│   │   └── INDEX_OPTIMIZATION.md  # Documentación performance
│   ├── products/              # ✅ App de PRODUCTOS COMPLETA
│   │   ├── models.py          # ProductCategory, Product, Modality, Customization
│   │   ├── views.py           # ViewSets con filtrado/búsqueda avanzada
│   │   ├── serializers.py     # Serializers optimizados (list/detail/create)
│   │   ├── admin.py           # Admin interface con optimizaciones
│   │   ├── urls.py            # API endpoints + analytics
│   │   ├── analytics.py       # Dashboard y analytics de productos
│   │   ├── migrations/        # Migraciones con constraints e índices
│   │   └── tests.py           # Tests unitarios
│   └── interactions/          # ✅ App de INTERACCIONES COMPLETA
│       ├── models.py          # 8 modelos: Medium, Channel, Action, Agent, Session, Touchpoint, Interaction
│       ├── views.py           # 8 ViewSets con analytics avanzados de customer journey
│       ├── serializers.py     # 24 serializers contextuales optimizados
│       ├── admin.py           # Interface administrativa completa
│       ├── urls.py            # 27 endpoints API completamente funcionales
│       ├── analytics.py       # Analytics empresariales de customer journey
│       ├── migrations/        # Migraciones con índices de performance
│       ├── fixtures/          # Datos iniciales para mediums, channels, actions
│       ├── tests.py           # Suite de pruebas 100% exitosa
│       └── README.md          # Documentación técnica completa (746 líneas)
│   └── offers/                # ✅ App de OFERTAS COMERCIALES COMPLETA
│       ├── models.py          # ProductOffering con segmentación semántica
│       ├── views.py           # ViewSet con 10 endpoints + analytics empresariales
│       ├── serializers.py     # 5 serializers contextuales optimizados
│       ├── admin.py           # Interface administrativa con acciones en lote
│       ├── urls.py            # 10 endpoints API completamente funcionales
│       ├── migrations/        # Migraciones con índices estratégicos
│       ├── tests.py           # Tests unitarios y de integración
│       ├── README.md          # Documentación del sistema de ofertas
│       └── COMPLETION_REPORT.md # Reporte completo de implementación
│   └── campaigns/             # ✅ App de CAMPAÑAS COMERCIALES COMPLETA
│       ├── models.py          # Campaign, CampaignTouchpoint con targeting semántico
│       ├── views.py           # ViewSets con 7 endpoints + analytics empresariales
│       ├── serializers.py     # 8 serializers contextuales optimizados
│       ├── admin.py           # Interface administrativa completa
│       ├── urls.py            # 7 endpoints API completamente funcionales
│       ├── migrations/        # Migraciones con índices estratégicos
│       ├── tests.py           # Tests unitarios y de integración
│       └── README.md          # Documentación completa del sistema de campañas
├── frontend/                  # Frontend Nuxt.js COMPLETO
│   ├── composables/
│   │   └── useAuth.ts        # ✅ Sistema auth completo
│   ├── src/
│   │   ├── components/
│   │   │   └── UserList.vue
│   │   └── services/
│   │       ├── api.ts        # ✅ API service centralizado
│   │       └── userService.ts
│   ├── pages/
│   │   ├── index.vue
│   │   └── login.vue         # ✅ Página de login
│   ├── middleware/
│   │   └── auth.ts           # ✅ Middleware auth
│   ├── plugins/
│   │   └── auth.client.ts    # ✅ Plugin cliente
│   ├── nuxt.config.ts        # ✅ Módulos completos
│   └── package.json          # ✅ Nuxt 3.17.4
├── docker-compose.yml        # ⚠️ Frontend comentado
├── .env                      # Variables de entorno
├── CLAUDE.md                 # ✅ Guía del proyecto
├── COMMANDS.md               # Comandos disponibles
├── DEPLOYMENT.md             # Deployment guide
└── README.md
```

## 🐳 CONFIGURACIÓN DE DESARROLLO OBLIGATORIA

### ⚠️ CRÍTICO: SIEMPRE USAR DOCKER COMPOSE

**ESTE PROYECTO USA ARQUITECTURA HÍBRIDA CON DOCKER COMPOSE - NO HAY EXCEPCIONES:**

- ✅ **Backend Django**: OBLIGATORIAMENTE en contenedor Docker
- ✅ **PostgreSQL**: OBLIGATORIAMENTE en contenedor Docker
- ✅ **Frontend Nuxt.js**: Ejecuta localmente (no containerizado)

### 🚫 COMANDOS PROHIBIDOS (NO USAR NUNCA):

```bash
# ❌ NUNCA ejecutar directamente en el host:
python manage.py runserver
python manage.py migrate
python manage.py shell
pip install -r requirements.txt
python manage.py createsuperuser
python manage.py test

# ❌ NUNCA instalar PostgreSQL localmente
brew install postgresql
apt-get install postgresql
```

### ✅ COMANDOS CORRECTOS OBLIGATORIOS:

```bash
# ✅ SIEMPRE iniciar con Docker Compose
docker-compose up -d

# ✅ TODOS los comandos Django van con docker-compose exec:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py test
docker-compose exec backend python manage.py makemigrations

# ✅ Frontend local (única excepción)
cd frontend
npm install
npm run dev
```

### 🎯 Para GitHub Copilot y otros agentes:

1. **NUNCA sugerir comandos Python directos en el host**
2. **SIEMPRE anteponer `docker-compose exec backend` a comandos Django**
3. **SIEMPRE verificar que Docker Compose esté ejecutándose**
4. **NUNCA asumir instalación local de Python/Django**
5. **SIEMPRE usar las tareas de VS Code configuradas**

### URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js local)
- **Backend API**: http://localhost:8000/api/ (Docker)
- **Django Admin**: http://localhost:8000/admin (Docker)

## Tecnologías Implementadas

### Backend (🐳 EN DOCKER SIEMPRE)

- **Framework**: Django 5.x (en contenedor)
- **API**: Django REST Framework (en contenedor)
- **Base de Datos**: PostgreSQL 14 (en contenedor Docker)
- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based (implementado)
- **CORS**: django-cors-headers configurado
- **Aplicaciones**:
  - `users` (no `myapp`) con `ExampleModel`
  - **`entities`** ✅ Sistema de gestión de entidades (COMPLETA)
  - **`world`** ✅ Datos globales de referencia (COMPLETA)
  - **`products`** ✅ Sistema de gestión de productos (COMPLETA)
  - **`interactions`** ✅ Sistema de gestión de customer journey (COMPLETA)

### Frontend (💻 LOCAL)

- **Framework**: Nuxt.js 3.17.4
- **Lenguaje**: TypeScript 5.8.3
- **UI Framework**: Nuxt UI 3.1.3
- **Módulos**: @nuxt/content, @nuxt/fonts, @nuxt/icon, @nuxt/image, @nuxt/scripts, @nuxt/test-utils
- **Autenticación**: ✅ Sistema completo implementado
- **HTTP Client**: API service con $fetch
- **Linting**: ESLint 9.27.0

## Características Implementadas

### ✅ Sistema de Autenticación Completo

- **Composable**: `useAuth.ts` con gestión de tokens JWT
- **Cookies Seguras**: Configuración por ambiente (dev/prod)
- **Middleware**: `auth.ts` para proteger rutas
- **Plugin**: `auth.client.ts` para inicialización
- **Páginas**: Login funcional
- **Seguridad**: Diferentes configs para desarrollo y producción

### ✅ Servicios API Estructurados

- **API Service**: Centralizado en `src/services/api.ts`
- **User Service**: Específico en `userService.ts`
- **Runtime Config**: Variables de entorno de Nuxt

### ✅ Componentes Base

- **UserList**: Componente de lista de usuarios
- **Páginas**: Index y login implementadas

### ✅ Aplicación Entities - Sistema de Gestión de Entidades (COMPLETA)

La aplicación `entities` es el **núcleo semántico de gestión de personas y organizaciones** en BackboneOS. Proporciona la infraestructura fundamental para perfilado semántico, gestión de contactos, direcciones y análisis organizacional en el contexto CRM.

#### **Concepto de Sistema de Entidades en BackboneOS**

Un **sistema de entidades** gestiona las identidades fundamentales del CRM antes de que participen en ciclos comerciales. La app `entities` actúa como:

- **Registro Humanista**: Preserva la perspectiva centrada en personas e instituciones
- **Núcleo Semántico**: Integración profunda con el campo semántico empresarial
- **Base Relacional**: Fundamento para leads, clientes, oportunidades
- **Centro de Contactos**: Gestión unificada de comunicación omnicanal
- **Motor de Perfilado**: Clasificación semántica multidimensional

#### **Modelos del Sistema de Entidades**

**Entidades Centrales:**

- `Person`: Personas físicas con información demográfica completa y perfilado semántico
- `Organization`: Entidades corporativas con clasificación industrial y contexto geográfico
- `ContactDetail`: Sistema unificado de contactos para personas y organizaciones
- `IndividualProfile`: Extensión semántica personal con capacidades CRM avanzadas
- `PhysicalAddress`: Gestión flexible de direcciones múltiples por entidad

#### **Integración Semántica con World App**

**Perfilado Semántico Personal:**

- Clasificación por industrias, habilidades y funciones organizacionales
- Nivel educativo y certificaciones académicas
- Contexto geográfico y regulatorio (tipos de identificación)

**Clasificación Organizacional:**

- Tipificación por industria y tipo de organización
- Análisis de mercado y segmentación estratégica
- Compliance regulatorio y identificación empresarial

#### **Características CRM Avanzadas**

**Analytics Organizacional:**

- Inteligencia de mercado por industria y geografía
- Segmentación demográfica y empresarial
- Métricas de penetración y oportunidades

**Gestión de Contactos:**

- Comunicación omnicanal con verificación
- Compliance GDPR y gestión de consentimientos
- Preferencias de comunicación personalizadas

**Optimización de Performance:**

- Índices estratégicos documentados para búsquedas semánticas
- Consultas optimizadas con select_related y prefetch_related
- Patrones de consulta para analytics empresariales

#### **Casos de Uso en CRM**

1. **Perfilado Semántico de Clientes**: Clasificación multidimensional usando vocabulario empresarial
2. **Gestión de Contactos**: Sistema unificado de comunicación con verificación
3. **Analytics Organizacional**: Inteligencia de mercado y análisis demográfico
4. **Segmentación de Mercado**: Agrupación por contexto semántico empresarial
5. **Compliance y Privacidad**: Gestión GDPR con consentimientos y preferencias

#### **Endpoints API Disponibles**

```
/api/entities/people/              # Personas físicas
/api/entities/people/{id}/profile/ # Perfil semántico personal
/api/entities/organizations/       # Organizaciones
/api/entities/organizations/{id}/analytics/ # Analytics organizacional
/api/entities/contacts/            # Detalles de contacto
/api/entities/addresses/           # Direcciones físicas
```

#### **Valor del Sistema de Entidades para la Organización**

- **Base Humanista**: Perspectiva centrada en personas antes que en roles comerciales
- **Perfilado Semántico**: Clasificación inteligente basada en ontología empresarial
- **Contacto Unificado**: Gestión omnicanal con verificación y compliance
- **Analytics de Mercado**: Inteligencia organizacional y demográfica
- **Escalabilidad CRM**: Fundamento sólido para funcionalidades comerciales avanzadas
- **Integridad Referencial**: Preservación del histórico con soft delete
- **Performance Optimizada**: Consultas eficientes con índices estratégicos

### ✅ Aplicación World - Campo Semántico Empresarial (COMPLETA)

La aplicación `world` es una **ontología empresarial** y **sistema de campo semántico** que define el universo conceptual y taxonómico para toda la organización que utiliza BackboneOS como CRM.

#### **Concepto de Campo Semántico en BackboneOS**

Un **campo semántico** es el conjunto de conceptos, términos y relaciones que definen el vocabulario empresarial de una organización. La app `world` actúa como:

- **Diccionario Empresarial**: Vocabulario controlado y normalizado
- **Taxonomía Organizacional**: Jerarquías conceptuales que reflejan la estructura del negocio
- **Ontología de Dominio**: Relaciones semánticas entre conceptos empresariales
- **Contexto Semántico**: Marco de referencia para interpretar y categorizar información
- **Lenguaje Común**: Terminología estándar para toda la organización

#### **Modelos como Campos Semánticos Empresariales**

**Campo Semántico Geográfico:**

- `Country`: Dimensión territorial del mercado y operaciones
- `Region`: Segmentación geográfica estratégica

**Campo Semántico Organizacional:**

- `Industry`: Ecosistema sectorial con jerarquía semántica (sector → subsector → nicho)
- `FunctionOrResponsibility`: Taxonomía de roles y responsabilidades empresariales
- `OrganizationType`: Tipología de estructuras organizacionales
- `OrganizationalIDType`: Marco regulatorio de identificación empresarial
- `Position`: Jerarquía de cargos y niveles organizacionales

**Campo Semántico de Competencias:**

- `Skill`: Ontología de habilidades y competencias profesionales
- `AcademicDegree`: Taxonomía educativa y certificaciones
- `PersonalIDType`: Marco regulatorio de identificación personal

**Campo Semántico de Clasificación:**

- `DescriptorFamily`: Meta-taxonomías para organizar descriptores
- `WorldDescriptor`: Sistema universal de etiquetado semántico
- `MarketSegment`: Segmentación de mercado multi-dimensional
- `Tag`: Sistema de folksonomía colaborativa

#### **Características del Campo Semántico**

**Taxonomías Jerárquicas:**

- Estructuras padre-hijo que reflejan la ontología del negocio
- Múltiples niveles de granularidad semántica (macro → micro conceptos)
- Navegación conceptual intuitiva y contextual

**Consistencia Semántica:**

- **Vocabulario Controlado**: Términos normalizados y validados
- **Desambiguación**: Contexto claro para conceptos polisémicos
- **Relaciones Semánticas**: Vínculos conceptuales explícitos

**Evolución del Campo Semántico:**

- **Adaptabilidad**: Incorporación de nuevos conceptos empresariales
- **Versionado**: Evolución controlada del vocabulario organizacional
- **Coherencia**: Mantenimiento de la integridad semántica

**Optimización Semántica:**

- **Índices de base de datos** para búsquedas conceptuales rápidas
- **Queries semánticos** optimizados para navegación taxonómica
- **Cache semántico** para conceptos frecuentemente utilizados

**API REST Completa:**

- ViewSets para todos los modelos con filtrado, búsqueda y ordenamiento
- Serializers duales: completos y "choice" para formularios
- Endpoints estructurados en `/api/world/`

**Integración con Django Admin:**

- Interface administrativa completa para gestión de datos
- Filtros y búsquedas configuradas para cada modelo
- Gestión eficiente de relaciones jerárquicas

#### **Casos de Uso del Campo Semántico en CRM**

1. **Perfilado Semántico de Clientes**: Clasificación multidimensional usando vocabulario empresarial
2. **Segmentación Conceptual**: Agrupación de leads/clientes por campos semánticos
3. **Análisis de Mercado Ontológico**: Comprensión profunda del ecosistema empresarial
4. **Personalización Contextual**: Adaptación de contenido basada en el perfil semántico
5. **Inteligencia de Negocio Semántica**: Insights basados en relaciones conceptuales
6. **Automatización Inteligente**: Workflows basados en contexto semántico
7. **Búsqueda Conceptual**: Encontrar información por significado, no solo por palabras clave
8. **Recomendaciones Semánticas**: Sugerencias basadas en proximidad conceptual

#### **Endpoints API Disponibles**

```
/api/world/countries/          # Países
/api/world/industries/         # Industrias (jerárquicas)
/api/world/functions/          # Funciones organizacionales
/api/world/skills/             # Habilidades
/api/world/market-segments/    # Segmentos de mercado
/api/world/descriptors/        # Descriptores globales
/api/world/tags/              # Sistema de tags
# ... y más
```

#### **Valor del Campo Semántico para la Organización**

- **Lenguaje Empresarial Unificado**: Vocabulario común para toda la organización
- **Inteligencia Contextual**: Comprensión profunda del dominio empresarial
- **Escalabilidad Semántica**: Crecimiento ordenado del conocimiento organizacional
- **Interoperabilidad**: Integración semántica con sistemas externos
- **Trazabilidad Conceptual**: Historia y evolución de conceptos empresariales
- **Automatización Inteligente**: Decisiones basadas en contexto semántico
- **Ventaja Competitiva**: Conocimiento estructurado del mercado y la industria

### ✅ Aplicación Products - Sistema de Gestión de Productos (COMPLETA)

La aplicación `products` implementa un **sistema completo de gestión de catálogo de productos** con capacidades avanzadas de clasificación, personalización y análisis, integrado directamente con el campo semántico empresarial de `world`.

#### **Concepto de Sistema de Productos en BackboneOS**

Un **sistema de productos** es el componente que gestiona todo el catálogo de productos/servicios de la organización, permitiendo clasificación jerárquica, personalización, pricing dinámico y análisis de mercado. La app `products` actúa como:

- **Catálogo Central**: Gestión unificada de productos y servicios
- **Clasificación Semántica**: Organización basada en taxonomías empresariales
- **Motor de Personalización**: Configuración y adaptación de productos
- **Centro de Pricing**: Gestión de precios multi-moneda
- **Hub Analítico**: Insights de rendimiento y oportunidades

#### **Modelos del Sistema de Productos**

**Estructura Organizacional:**

- `Division`: **División empresarial** que agrupa categorías de productos a nivel organizacional
  - Campos: `name`, `code`, `description`
  - Propiedades computadas: `categories_count`, `products_count`
  - Relación: Una división puede tener múltiples categorías
  - Propósito: Estructurar productos por áreas de negocio (Tecnología, Consultoría, etc.)

**Clasificación y Organización:**

- `ProductCategory`: Taxonomía jerárquica de categorías con navegación multi-nivel
  - Relación con `Division`: Cada categoría puede pertenecer a una división
  - Propiedades extendidas: `full_path` incluye división, `absolute_level` considera jerarquía completa
- `Product`: Entidad central con información completa y relaciones semánticas
- `Modality`: Modalidades de entrega/ejecución de productos (presencial, virtual, híbrido)
- `Customization`: Tipos de personalización disponible por producto

#### **API REST Avanzada para Productos**

**Endpoints Principales:**

```
/api/products/divisions/           # Gestión de divisiones organizacionales
/api/products/divisions/{id}/categories/  # Categorías por división
/api/products/divisions/{id}/products/    # Productos por división
/api/products/divisions/{id}/summary/     # Resumen estadístico por división
/api/products/categories/          # Gestión de categorías
/api/products/categories/tree/     # Árbol completo de categorías
/api/products/categories/{id}/products/  # Productos por categoría
/api/products/modalities/          # Modalidades de productos
/api/products/customizations/      # Tipos de personalización
/api/products/products/            # CRUD completo de productos
/api/products/products/stats/      # Estadísticas de productos
/api/products/products/search_advanced/  # Búsqueda semántica avanzada
/api/products/products/{id}/duplicate/   # Duplicación de productos
```

**Filtrado Avanzado:**

- **Filtros Jerárquicos**: Por categoría incluyendo subcategorías
- **Filtros Semánticos**: Por industrias, skills, segmentos de mercado
- **Filtros de Negocio**: Precio, duración, personalización, moneda
- **Búsqueda Semántica**: En descriptores, tags y contenido

**Serializers Optimizados:**

- `ProductListSerializer`: Optimizado para listados con propiedades calculadas
- `ProductDetailSerializer`: Completo con todas las relaciones
- `ProductCreateUpdateSerializer`: Simplificado para operaciones de escritura

#### **Sistema de Analytics de Productos**

**Dashboard de Analytics (`/api/products/analytics/`):**

- **Métricas Generales**: Total productos, categorías, modalidades
- **Análisis de Pricing**: Estadísticas por moneda, distribución de precios
- **Segmentación**: Análisis por segmentos de mercado
- **Tendencias**: Crecimiento y patrones temporales
- **Personalización**: Métricas de productos customizables

**Endpoints de Analytics Especializados:**

```
/api/products/analytics/dashboard/           # Dashboard principal de productos
/api/products/analytics/divisions/           # Analytics específicos por división
/api/products/analytics/categories/          # Analytics por categoría
/api/products/analytics/market-segmentation/ # Análisis de segmentación
/api/products/analytics/pricing/             # Análisis de precios
/api/products/analytics/growth/              # Análisis de crecimiento
/api/products/analytics/recommendations/     # Recomendaciones de productos
```

#### **Características Avanzadas**

**Optimización de Performance:**

- **Consultas Optimizadas**: `select_related` y `prefetch_related` estratégicos
- **Índices de Base de Datos**: En campos críticos para búsquedas
- **Cache**: Implementación de cache en endpoints de analytics
- **Serializers Contextuales**: Diferentes niveles de detalle según uso

**Validaciones de Negocio:**

- **Constraints de BD**: Precios positivos, monedas válidas
- **Validaciones Django**: Lógica de negocio en modelos
- **Integridad Referencial**: Manejo de eliminaciones con SET_NULL

**Interface Administrativa:**

- **Admin Optimizado**: Consultas eficientes con prefetch
- **Filtros Inteligentes**: Por categoría, segmentos, industrias
- **Acciones en Lote**: Activar/desactivar/duplicar productos
- **Campos Calculados**: Displays formateados para mejor UX

#### **Casos de Uso del Sistema de Productos en CRM**

1. **Catalogación Inteligente**: Organización semántica del portafolio de productos
2. **Targeting Preciso**: Matching de productos con perfiles de clientes
3. **Configuración Dinámica**: Personalización basada en contexto empresarial
4. **Análisis de Portafolio**: Insights de rendimiento y oportunidades
5. **Pricing Estratégico**: Gestión de precios basada en segmentación
6. **Recomendaciones Automáticas**: Sugerencias basadas en perfil semántico
7. **Reporting Avanzado**: Analytics multidimensional de productos
8. **Integración CRM**: Conexión directa con oportunidades y cotizaciones

#### **Valor del Sistema de Productos para la Organización**

- **Catálogo Centralizado**: Gestión unificada de todo el portafolio
- **Clasificación Inteligente**: Organización basada en ontología empresarial
- **Flexibility Comercial**: Adaptación a diferentes mercados y segmentos
- **Insights de Negocio**: Analíticas que impulsan decisiones estratégicas
- **Eficiencia Operativa**: Automatización de procesos de gestión de productos
- **Escalabilidad**: Crecimiento ordenado del catálogo
- **Ventaja Competitiva**: Inteligencia comercial basada en datos

### ✅ Aplicación Interactions - Sistema de Gestión de Customer Journey (COMPLETA)

La aplicación `interactions` es el **sistema central de gestión de customer journey** de BackboneOS. Proporciona un framework completo para registrar, analizar y optimizar todas las interacciones entre la organización y sus clientes potenciales a lo largo de todo el proceso comercial, implementando el marco conceptual **Jobs-to-be-Done**.

#### **Concepto de Sistema de Interacciones en BackboneOS**

Un **sistema de interacciones** gestiona el customer journey completo desde el primer contacto hasta la advocacy, proporcionando visibilidad total del comportamiento del cliente. La app `interactions` actúa como:

- **Centro de Customer Journey**: Registro completo de todas las interacciones
- **Motor de Analytics**: Insights avanzados de comportamiento y performance
- **Framework JTBD**: Implementación del modelo Jobs-to-be-Done
- **Hub de Touchpoints**: Gestión centralizada de puntos de contacto
- **Sistema de Tracking**: Seguimiento omnicanal de actividades

#### **Modelos del Sistema de Interacciones**

**Infraestructura de Comunicación:**

- `Medium`: Medios de comunicación fundamentales (Email, Web, Teléfono, Redes Sociales)
- `Channel`: Canales específicos por medium (Gmail, WhatsApp Business, Instagram)
- `ActionType`: Tipos de acciones categorizadas (View, Click, Download, Form Submit)
- `Action`: Acciones específicas con metadatos (Clic en CTA, Descarga PDF, Registro)

**Agentes y Sesiones:**

- `Agent`: Agentes de interacción (navegadores, sistemas, personas, bots) con identificación única
- `TouchpointClass`: Clases de puntos de contacto (Landing Page, Form, Event, Email Campaign)
- `Touchpoint`: Puntos de contacto específicos con asignación de staff y contexto semántico

**Interacciones Centrales:**

- `Interaction`: Registro completo de interacciones con contexto temporal, espacial y semántico

#### **Integración Semántica Multi-App**

**Integración con World App:**

```python
# Contexto semántico en Touchpoints
related_industries = models.ManyToManyField('world.Industry', blank=True)
related_functions = models.ManyToManyField('world.FunctionOrResponsibility', blank=True)
related_skills = models.ManyToManyField('world.Skill', blank=True)
related_descriptors = models.ManyToManyField('world.WorldDescriptor', blank=True)
```

**Integración con Entities App:**

```python
# Relaciones con personas y organizaciones
person = models.ForeignKey('entities.Person', null=True, blank=True)
organization = models.ForeignKey('entities.Organization', null=True, blank=True)
```

**Integración con Products App:**

```python
# Contexto de productos
product = models.ForeignKey('products.Product', null=True, blank=True)
```

#### **API REST Completa - 27 Endpoints**

**Gestión de Mediums:**

```
GET/POST    /api/interactions/mediums/              # CRUD completo
GET/PUT     /api/interactions/mediums/{id}/         # Detalle y actualización
GET         /api/interactions/mediums/choices/      # Choices para formularios
```

**Gestión de Channels:**

```
GET/POST    /api/interactions/channels/             # CRUD completo
GET/PUT     /api/interactions/channels/{id}/        # Detalle y actualización
GET         /api/interactions/channels/choices/     # Choices para formularios
```

**Gestión de Actions:**

```
GET/POST    /api/interactions/action-types/         # Tipos de acción
GET/POST    /api/interactions/actions/              # Acciones específicas
GET         /api/interactions/actions/choices/      # Choices para formularios
```

**Gestión de Agents:**

```
GET/POST    /api/interactions/agents/               # CRUD completo
GET         /api/interactions/agents/by_type/       # Filtrar por tipo
GET         /api/interactions/agents/analytics/     # Analytics de agentes
```

**Gestión de Touchpoints:**

```
GET/POST    /api/interactions/touchpoints/          # CRUD completo
GET         /api/interactions/touchpoints/by_funnel_stage/ # Filtrar por etapa
GET         /api/interactions/touchpoints/{id}/interactions/ # Interacciones del touchpoint
GET         /api/interactions/touchpoints/analytics/ # Analytics de touchpoints
```

**Gestión de Interactions:**

```
GET/POST    /api/interactions/interactions/         # CRUD completo
GET         /api/interactions/interactions/analytics/ # Analytics general
GET         /api/interactions/interactions/funnel_analysis/ # Análisis de funnel
GET         /api/interactions/interactions/geographic_distribution/ # Distribución geográfica
POST        /api/interactions/interactions/bulk_create/ # Creación en lote
```

#### **Jobs-to-be-Done Framework Implementado**

**Etapas del Customer Journey:**

```python
JOB_STAGES = [
    ('awareness', 'Consciencia'),        # Cliente descubre que tiene un problema
    ('consideration', 'Consideración'),   # Cliente evalúa soluciones
    ('decision', 'Decisión'),            # Cliente decide comprar
    ('onboarding', 'Incorporación'),     # Cliente aprende a usar el producto
    ('usage', 'Uso'),                    # Cliente usa el producto regularmente
    ('advocacy', 'Recomendación'),       # Cliente recomienda el producto
    ('any', 'Cualquiera')                # Para filtros amplios
]
```

**Aplicaciones del Framework:**

- **Analytics por Etapa**: Distribución de interacciones por etapa JTBD
- **Optimización del Funnel**: Análisis de flujo entre etapas
- **Identificación de Fricción**: Puntos de abandono en el customer journey
- **Personalización**: Contenido específico según etapa del cliente

#### **Sistema de Analytics Empresariales**

**Dashboard de Analytics General:**

```json
{
  "total_interactions": 11,
  "unique_sessions": 8,
  "avg_duration_seconds": 165.1,
  "by_channel": [{ "channel__name": "WhatsApp", "count": 3 }],
  "by_action": [{ "action__name": "Clic", "count": 4 }],
  "by_jtbd_stage": [{ "jtbd_stage": "awareness", "count": 6 }]
}
```

**Analytics de Agentes:**

- Distribución por tipo (browser, system, human, bot)
- Performance de agentes individuales
- Métricas de interacciones por agente

**Analytics de Touchpoints:**

- Performance por etapa del funnel
- Distribución por clases de touchpoint
- Top performers y métricas de conversión

**Análisis Geográfico:**

- Distribución geográfica de interacciones
- Heatmaps de actividad por ubicación
- Análisis territorial de engagement

#### **Características Avanzadas**

**Filtros y Búsquedas Sofisticadas:**

- Filtros por etapa JTBD, touchpoint, agente, canal
- Rangos de fechas para análisis temporal
- Filtros geográficos y por duración
- Búsquedas semánticas en contexto empresarial

**Optimización de Performance:**

- Consultas optimizadas con `select_related` y `prefetch_related`
- Tiempo de respuesta promedio: **42.5ms** (Excelente)
- Serializers contextuales para diferentes casos de uso
- Paginación automática en todos los listados

**Sistema de Permisos Dinámico:**

```python
def get_permission_classes():
    if settings.DEBUG:
        return [AllowAny]  # Sin autenticación en desarrollo
    else:
        return [IsAuthenticated]  # Autenticación JWT en producción
```

#### **Casos de Uso en CRM**

1. **Customer Journey Tracking**: Registro completo de todas las interacciones del cliente
2. **Analytics de Performance**: Métricas de touchpoints, agentes y canales
3. **Optimización de Funnel**: Identificación de puntos de fricción y abandono
4. **Segmentación Comportamental**: Clasificación basada en patrones de interacción
5. **Personalización Contextual**: Contenido específico según etapa del journey
6. **Geolocalización de Mercado**: Análisis territorial de engagement
7. **Performance de Equipos**: Métricas de representantes y staff asignado
8. **Automatización Inteligente**: Triggers basados en comportamiento

#### **Endpoints API Disponibles**

```
# Gestión de infraestructura
/api/interactions/mediums/              # Medios de comunicación
/api/interactions/channels/             # Canales específicos
/api/interactions/action-types/         # Tipos de acciones
/api/interactions/actions/              # Acciones específicas

# Gestión de agentes y touchpoints
/api/interactions/agents/               # Agentes de interacción
/api/interactions/touchpoint-classes/   # Clases de touchpoints
/api/interactions/touchpoints/          # Puntos de contacto

# Gestión de interacciones
/api/interactions/interactions/         # Interacciones centrales

# Analytics especializados
/api/interactions/interactions/analytics/          # Dashboard general
/api/interactions/interactions/funnel_analysis/    # Análisis de funnel
/api/interactions/interactions/geographic_distribution/ # Distribución geográfica
/api/interactions/agents/analytics/                # Analytics de agentes
/api/interactions/touchpoints/analytics/           # Analytics de touchpoints
```

#### **Testing y Calidad**

**Cobertura Completa:**

- ✅ **27 endpoints probados**: 100% de cobertura funcional
- ✅ **Tasa de éxito**: 100% (27/27 pruebas exitosas)
- ✅ **Performance**: Tiempo promedio 42.5ms (Excelente)
- ✅ **Scripts automatizados**: `test_complete_interactions_api.py`

**Estado del Sistema:**

- 🚀 **COMPLETAMENTE LISTO PARA PRODUCCIÓN**
- ✅ **API Endpoints Funcionando**
- ✅ **Analytics Disponibles**
- ✅ **Filtros y Búsquedas**
- ✅ **Integración Semántica**
- ✅ **Performance Excelente**

#### **Fixtures y Datos Iniciales**

**Fixtures Incluidos:**

- `initial_mediums.json`: Mediums básicos (Email, Web, Teléfono, Redes Sociales)
- `initial_channels.json`: Canales iniciales por medium
- `initial_action_types.json`: Tipos de acción fundamentales
- `initial_actions.json`: Acciones básicas por tipo

**Comandos de Inicialización:**

```bash
python manage.py loaddata interactions/initial_mediums.json
python manage.py loaddata interactions/initial_channels.json
python manage.py loaddata interactions/initial_action_types.json
python manage.py loaddata interactions/initial_actions.json
```

#### **Valor del Sistema de Interacciones para la Organización**

- **Visibilidad Total**: Customer journey completo desde awareness hasta advocacy
- **Insights Accionables**: Analytics empresariales para optimización de conversion
- **Framework JTBD**: Implementación del modelo Jobs-to-be-Done para mejor comprensión del cliente
- **Integración Semántica**: Contexto empresarial completo en cada interacción
- **Performance Excelente**: Respuestas rápidas para experiencias fluidas
- **Escalabilidad**: Arquitectura preparada para crecimiento masivo
- **ROI Medible**: Métricas precisas de performance de touchpoints y canales
- **Automatización Inteligente**: Base para workflows automatizados basados en comportamiento

### ✅ Aplicación Offers - Sistema de Gestión de Ofertas Comerciales (COMPLETA)

La aplicación `offers` es el **sistema central de gestión de ofertas comerciales** de BackboneOS. Proporciona un framework completo para crear, gestionar y analizar todas las ofertas de productos con segmentación semántica avanzada, pricing dinámico y analytics empresariales.

#### **Concepto de Sistema de Ofertas en BackboneOS**

Un **sistema de ofertas** gestiona la comercialización de productos del catálogo bajo condiciones específicas de precio, temporalidad, canales y audiencia. La app `offers` actúa como:

- **Centro de Comercialización**: Gestión completa de ofertas activas de la organización
- **Motor de Pricing**: Precios específicos y condiciones comerciales por oferta
- **Sistema Temporal**: Ofertas con vigencia limitada y renovación automática
- **Hub de Segmentación**: Targeting por canales, industrias, funciones y geografía
- **Analytics Comercial**: Insights de performance y ROI por oferta

#### **Modelo Principal: ProductOffering**

**Características Centrales:**

- `ProductOffering`: Oferta comercial con precio específico, temporalidad y segmentación
- Integración directa con `products.Product` como base de la oferta
- Soporte para suscripciones con `auto_renew` y `duration_days`
- Segmentación por `channels`, `seats`, `target_segments`
- Metadata JSON para configuraciones avanzadas de campaña

#### **Integración Semántica Multi-App**

**Integración con Products App:**

```python
# Base del producto ofertado
product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
```

**Integración con World App:**

```python
# Segmentación semántica empresarial
target_segments = models.ManyToManyField('world.MarketSegment', blank=True)
related_industries = models.ManyToManyField('world.Industry', blank=True)
related_functions = models.ManyToManyField('world.FunctionOrResponsibility', blank=True)
descriptors = models.ManyToManyField('world.WorldDescriptor', blank=True)
tags = models.ManyToManyField('world.Tag', blank=True)
```

**Integración con Interactions App:**

```python
# Canales de comercialización
channels = models.ManyToManyField('interactions.Channel', blank=True)
```

**Integración con Our Institution App:**

```python
# Limitación geográfica por sedes
seats = models.ManyToManyField('our_institution.Seat', blank=True)
```

#### **API REST Completa - 10 Endpoints**

**Gestión Central de Ofertas:**

```
GET/POST    /api/offers/offerings/              # CRUD completo
GET/PUT/DEL /api/offers/offerings/{id}/         # Detalle y operaciones
GET         /api/offers/offerings/choices/      # Choices para formularios
```

**Endpoints Especializados:**

```
GET         /api/offers/offerings/currently_valid/    # Ofertas actualmente válidas
GET         /api/offers/offerings/by_product/         # Ofertas por producto
GET         /api/offers/offerings/by_channel/         # Ofertas por canal
GET         /api/offers/offerings/analytics/          # Analytics empresariales
POST        /api/offers/offerings/{id}/duplicate/     # Duplicar oferta
```

#### **Sistema de Analytics Empresariales**

**Dashboard de Analytics Completo:**

```json
{
  "total_offerings": 5,
  "active_offerings": 5,
  "expired_offerings": 0,
  "future_offerings": 2,
  "by_currency": [{"currency_code": "USD", "count": 5, "avg_price": 10180.0}],
  "by_product_category": [...],
  "by_channel": [...],
  "by_market_segment": [...],
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

**Métricas Empresariales:**

- Distribución por moneda con precios promedio
- Análisis por categoría de producto (top 10)
- Performance por canal (top 10)
- Segmentación de mercado basada en campo semántico
- Estadísticas de precios (min, max, promedio, valor total)
- Estadísticas de duración para suscripciones
- Top productos más ofertados
- Ofertas recientes y tendencias

#### **Características Comerciales Avanzadas**

**Temporal y Pricing:**

```python
# Vigencia temporal
valid_from = models.DateField(null=True, blank=True)
valid_until = models.DateField(null=True, blank=True)

# Suscripciones
auto_renew = models.BooleanField(default=False)
duration_days = models.PositiveIntegerField(null=True, blank=True)

# Pricing multi-moneda
price = models.DecimalField(max_digits=12, decimal_places=2)
currency_code = models.CharField(max_length=3, default='USD')
```

**Propiedades Computadas:**

```python
@property
def is_currently_valid(self):
    """Verifica si la oferta está actualmente válida"""

@property
def price_display(self):
    """Formato amigable: USD 1,400.00"""
```

**Filtros y Búsquedas Sofisticadas:**

- Filtros por validez actual, moneda, auto-renovación
- Rangos de fechas y precios
- Filtros por producto, categoría, división
- Filtros semánticos por canales, segmentos, industrias
- Búsquedas en nombre, código, descripción, producto

#### **Serializers Contextuales Optimizados**

**5 Serializers Especializados:**

```python
ProductOfferingListSerializer      # Listados optimizados
ProductOfferingDetailSerializer    # Detalle con relaciones semánticas
ProductOfferingCreateUpdateSerializer  # CRUD con validaciones
ProductOfferingChoiceSerializer    # Formularios (ID, name, display_name)
ProductOfferingAnalyticsSerializer # Estructura de métricas
```

**Validaciones de Negocio:**

- Código único por oferta
- Fechas válidas (valid_from ≤ valid_until)
- Precios positivos
- Integridad referencial con productos

#### **Interface Administrativa Empresarial**

**Django Admin Optimizado:**

```python
# Características avanzadas
- List display con métricas clave
- Filtros por múltiples dimensiones semánticas
- Búsqueda en campos relacionados
- Fieldsets organizados por contexto empresarial
- Filter horizontal para relaciones M2M
- Acciones en lote (activar/desactivar/duplicar)
- Consultas optimizadas con select_related/prefetch_related
```

**Acciones Disponibles:**

1. **Activar ofertas** en lote
2. **Desactivar ofertas** en lote
3. **Duplicar ofertas** preservando relaciones M2M
4. **Filtros inteligentes** por categoría, segmentos, industrias
5. **Campos calculados** para mejor experiencia de usuario

#### **Casos de Uso Comerciales en CRM**

1. **Gestión de Campañas**: Ofertas temporales con metadata de campaña
2. **Suscripciones Empresariales**: Paquetes anuales con auto-renovación
3. **Segmentación Avanzada**: Targeting por industria, función, canal
4. **Pricing Dinámico**: Precios específicos por oferta y audiencia
5. **Analytics de Performance**: ROI por canal, producto y segmento
6. **Duplicación Rápida**: Reutilización de ofertas exitosas
7. **Gestión Temporal**: Control de vigencia y expiración automática
8. **Reporting Ejecutivo**: Dashboard con métricas empresariales

#### **Endpoints API Disponibles**

```
# Gestión de ofertas
/api/offers/offerings/              # CRUD completo de ofertas
/api/offers/offerings/choices/      # Choices para formularios
/api/offers/offerings/currently_valid/  # Ofertas válidas ahora

# Filtros especializados
/api/offers/offerings/by_product/   # Ofertas por producto específico
/api/offers/offerings/by_channel/   # Ofertas por canal específico

# Analytics y duplicación
/api/offers/offerings/analytics/    # Dashboard empresarial completo
/api/offers/offerings/{id}/duplicate/  # Duplicar oferta con relaciones
```

#### **Optimización y Performance**

**Consultas Optimizadas:**

```python
# ViewSet con prefetch estratégico
queryset = ProductOffering.objects.select_related(
    'product', 'product__category', 'product__category__division'
).prefetch_related(
    'channels', 'seats', 'target_segments', 'related_industries',
    'related_functions', 'descriptors', 'tags'
)
```

**Índices de Base de Datos:**

```python
class Meta:
    indexes = [
        models.Index(fields=['is_active']),
        models.Index(fields=['valid_from']),
        models.Index(fields=['valid_until']),
        models.Index(fields=['currency_code']),
    ]
```

#### **Testing y Calidad**

**Suite de Tests Completa:**

- Tests del modelo (propiedades computadas, validaciones)
- Tests de API (CRUD, filtros, endpoints especializados)
- Tests de validación (código único, fechas, precios)
- Tests de duplicación y analytics
- Datos de prueba realistas con casos de uso diversos

#### **Datos de Prueba**

**5 Ofertas de Ejemplo:**

1. **Oferta Black Friday**: Descuento temporal con metadata de campaña
2. **Consultoría Anual**: Paquete de suscripción con auto-renovación
3. **Desarrollo Web Premium**: Oferta futura con configuración avanzada
4. **Capacitación Virtual**: Programa con duración específica
5. **Análisis de Datos Q1**: Servicio completo con metadata técnica

#### **Valor del Sistema de Ofertas para la Organización**

- **Comercialización Inteligente**: Separación clara entre producto y oferta comercial
- **Segmentación Semántica**: Targeting preciso basado en campo semántico empresarial
- **Analytics Comerciales**: Insights de performance y ROI por oferta
- **Flexibilidad Temporal**: Gestión de campañas con vigencia limitada
- **Suscripciones Empresariales**: Soporte completo para modelos recurrentes
- **Escalabilidad Comercial**: Múltiples ofertas por producto con diferentes condiciones
- **Automatización**: Workflows basados en temporalidad y renovación
- **Ventaja Competitiva**: Inteligencia comercial basada en datos semánticos

### ✅ Aplicación Campaigns - Sistema de Gestión de Campañas Comerciales (COMPLETA)

La aplicación `campaigns` gestiona **campañas comerciales** como estructuras organizadas y planificadas para promocionar productos o servicios a través de múltiples canales y puntos de contacto.

#### **Concepto de Campaña en BackboneOS**

Una **campaña** en BackboneOS es mucho más que un simple contenedor de marketing. Es una **estructura empresarial inteligente** que:

- Tiene una **intención estratégica** definida (segmentos, industrias, temporalidad, presupuesto)
- Se articula mediante **canales y touchpoints** específicos
- Puede tener **subcampañas** como unidades operativas independientes
- Se integra con el **campo semántico** de BackboneOS para facilitar targeting y análisis

#### **Modelos del Sistema de Campañas**

**`Campaign` - Iniciativa de Marketing/Ventas:**

```python
class Campaign(BaseUUIDModelWithActiveStatus):
    # Identificación y descripción
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    # Temporalidad y presupuesto
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Clasificación estratégica
    content_type = models.CharField(
        choices=[("affinity", "Afinidad"), ("category", "Categoría"),
                ("product", "Producto"), ("brand", "Marca")]
    )

    # Etapa del embudo de ventas
    funnel_stage = models.CharField(
        choices=[("see", "Ver"), ("think", "Pensar"),
                ("do", "Hacer"), ("care", "Cuidar"), ("any", "Cualquiera")]
    )

    # Organización
    division = models.ForeignKey('our_institution.Division')
    team = models.ForeignKey('our_institution.Team')

    # Canales y segmentación semántica
    channels = models.ManyToManyField('interactions.Channel')
    related_industries = models.ManyToManyField('world.Industry')
    related_functions = models.ManyToManyField('world.FunctionOrResponsibility')
    target_segments = models.ManyToManyField('world.MarketSegment')
    descriptors = models.ManyToManyField('world.WorldDescriptor')
    tags = models.ManyToManyField('world.Tag')

    # Jerarquía (subcampañas)
    parent = models.ForeignKey('self', related_name='subcampaigns')
```

**`CampaignTouchpoint` - Relación Campaña-Punto de Contacto:**

```python
class CampaignTouchpoint(models.Model):
    campaign = models.ForeignKey('Campaign')
    touchpoint = models.ForeignKey('interactions.Touchpoint')

    # Configuración de planificación
    weight = models.FloatField(default=1.0)
    priority = models.PositiveIntegerField(default=0)
    expected_conversions = models.PositiveIntegerField()
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2)
```

#### **Características Avanzadas del Sistema**

**Targeting Semántico Multimodal:**

- **Segmentación por Industrias**: Campaigns dirigidas a sectores específicos
- **Targeting por Funciones**: Campañas para roles empresariales específicos
- **Geografía Semántica**: Combinación de ubicación y características empresariales
- **Descriptores Empresariales**: Etiquetado avanzado basado en campo semántico

**Gestión Temporal Inteligente:**

- **Estados Dinámicos**: Activa, programada, finalizada, inactiva (calculados en tiempo real)
- **Propiedad `is_active_now`**: Validación automática de vigencia actual
- **Fechas Flexibles**: Inicio obligatorio, fin opcional para campañas permanentes
- **Análisis Temporal**: Filtros y analytics por períodos específicos

**Presupuesto Multi-nivel:**

- **Presupuesto de Campaña**: Control presupuestario general
- **Presupuesto por Touchpoint**: Asignación específica a puntos de contacto
- **Peso y Prioridad**: Distribución inteligente de recursos
- **Métricas de ROI**: Análisis de retorno de inversión por nivel

**Estructura Jerárquica:**

```python
# Ejemplo de jerarquía
Campaña_Padre: "Black Friday 2024"
├── Subcampaña: "Black Friday - Email Marketing"
├── Subcampaña: "Black Friday - Redes Sociales"
└── Subcampaña: "Black Friday - Retargeting"
```

#### **Clasificaciones Estratégicas**

**Tipos de Contenido Comunicacional:**

| Tipo       | Significado                                | Ejemplo                           |
| ---------- | ------------------------------------------ | --------------------------------- |
| `affinity` | Contenido que apela a emociones y valores  | Campaña de responsabilidad social |
| `category` | Contenido de línea temática amplia         | Campaña de "Educación Online"     |
| `product`  | Contenido específico de producto/servicio  | Campaña de "MBA Ejecutivo"        |
| `brand`    | Contenido de posicionamiento institucional | Campaña de "Somos Líderes"        |

**Etapas del Embudo de Ventas:**

| Etapa   | Propósito                    | Estrategia                       | Ejemplos                  |
| ------- | ---------------------------- | -------------------------------- | ------------------------- |
| `see`   | **Ver** - Awareness          | Brand awareness, contenido viral | Display ads, social media |
| `think` | **Pensar** - Consideración   | Educación, comparativos          | Webinars, whitepapers     |
| `do`    | **Hacer** - Conversión       | CTAs directos, ofertas           | Landing pages, demos      |
| `care`  | **Cuidar** - Retención       | Fidelización, upselling          | Programas de lealtad      |
| `any`   | **Cualquiera** - Transversal | Campañas multiobjetivo           | Campañas institucionales  |

#### **API REST Completa**

**Endpoints de Campañas (`/api/campaigns/campaigns/`):**

```
# CRUD básico
GET/POST /api/campaigns/campaigns/              # Listar/crear campañas
GET/PUT/PATCH/DELETE /api/campaigns/campaigns/{id}/  # Operaciones específicas

# Endpoints especializados
GET /api/campaigns/campaigns/choices/           # Choices para formularios
GET /api/campaigns/campaigns/active_now/        # Campañas actualmente activas
GET /api/campaigns/campaigns/scheduled/         # Campañas programadas (futuras)
GET /api/campaigns/campaigns/finished/          # Campañas finalizadas
GET /api/campaigns/campaigns/by_division/       # Campañas por división
GET /api/campaigns/campaigns/by_team/           # Campañas por equipo
GET /api/campaigns/campaigns/{id}/subcampaigns/ # Subcampañas
GET /api/campaigns/campaigns/{id}/touchpoints/  # Touchpoints de campaña
POST /api/campaigns/campaigns/{id}/duplicate/   # Duplicar campaña
GET /api/campaigns/campaigns/analytics/         # Analytics completo
```

**Endpoints de Relaciones (`/api/campaigns/campaign-touchpoints/`):**

```
# CRUD de relaciones
GET/POST /api/campaigns/campaign-touchpoints/   # Listar/crear relaciones
GET/PUT/PATCH/DELETE /api/campaigns/campaign-touchpoints/{id}/  # Operaciones

# Analytics especializados
GET /api/campaigns/campaign-touchpoints/by_campaign/     # Por campaña
GET /api/campaigns/campaign-touchpoints/by_touchpoint/   # Por touchpoint
GET /api/campaigns/campaign-touchpoints/analytics/       # Analytics relaciones
```

#### **Filtros y Búsqueda Avanzada**

**Filtros de Campañas:**

- **Texto**: `name`, `code`, `description`
- **Fechas**: `start_date_from/to`, `end_date_from/to`
- **Presupuesto**: `budget_min/max`, `has_budget`
- **Estratégicos**: `content_type`, `funnel_stage`
- **Organizacionales**: `division`, `team`, `parent`
- **Estados**: `is_active`, `is_active_now`, `has_end_date`
- **Relaciones**: `has_subcampaigns`, `has_touchpoints`
- **Semánticos**: `channels`, `related_industries`, `related_functions`, `target_segments`

**Búsqueda de Texto Completo:**

```python
search_fields = ['name', 'code', 'description', 'division__name',
                'team__name', 'related_industries__name',
                'target_segments__name']
```

#### **Analytics Dashboard Empresarial**

**Métricas Básicas:**

- Total de campañas, activas, programadas, finalizadas
- Análisis organizacional por división y equipo
- Distribución por canales e industrias
- Estadísticas financieras (presupuesto total, promedio, min/max)

**Analytics Especializados:**

```json
{
  "total_campaigns": 25,
  "active_campaigns": 8,
  "scheduled_campaigns": 5,
  "finished_campaigns": 12,
  "total_budget": "125000.00",
  "average_budget": "5000.00",
  "by_division": [
    { "division__name": "Marketing", "count": 15, "total_budget": "75000.00" },
    { "division__name": "Ventas", "count": 10, "total_budget": "50000.00" }
  ],
  "by_funnel_stage": [
    { "funnel_stage": "see", "count": 8 },
    { "funnel_stage": "think", "count": 6 },
    { "funnel_stage": "do", "count": 7 },
    { "funnel_stage": "care", "count": 4 }
  ],
  "top_channels": [
    { "channel__name": "Email", "campaign_count": 12 },
    { "channel__name": "Social Media", "campaign_count": 8 }
  ]
}
```

#### **Serializers Contextuales**

**Serializers Especializados:**

- **`CampaignListSerializer`**: Optimizado para listados con contadores
- **`CampaignDetailSerializer`**: Completo con relaciones anidadas
- **`CampaignCreateUpdateSerializer`**: Simplificado para CRUD
- **`CampaignChoiceSerializer`**: Para formularios con displays
- **`CampaignAnalyticsSerializer`**: Estructura de métricas empresariales

**Características de Serialización:**

- **Displays formatados**: Presupuesto ($X,XXX.XX), duración (X días)
- **Estados calculados**: Activa, programada, finalizada
- **Contadores dinámicos**: Canales, touchpoints, subcampañas, segmentos
- **Relaciones optimizadas**: select_related y prefetch_related

#### **Casos de Uso Comerciales en CRM**

1. **Campañas de Awareness**: Campañas `see` con múltiples canales para brand building
2. **Lead Generation**: Campañas `think` enfocadas en captura y educación
3. **Conversión Directa**: Campañas `do` con CTAs específicos y landing pages
4. **Customer Success**: Campañas `care` para retención y expansion
5. **Campañas Jerárquicas**: Estructura padre-hijo para organización estratégica
6. **Targeting Semántico**: Segmentación basada en industria, función y geografía
7. **Analytics de Performance**: ROI por campaña, canal y touchpoint
8. **Gestión Presupuestaria**: Control multi-nivel de inversión comercial

#### **Valor del Sistema de Campañas para la Organización**

- **Organización Estratégica**: Estructura clara para iniciativas comerciales
- **Targeting Inteligente**: Segmentación basada en campo semántico empresarial
- **Control Presupuestario**: Gestión multi-nivel de inversión comercial
- **Analytics Empresariales**: Insights de performance y ROI por campaña
- **Jerarquía Operativa**: Subcampañas para organización táctica
- **Integración Touchpoints**: Conexión directa con customer journey
- **Automatización Temporal**: Estados dinámicos basados en fechas
- **Ventaja Competitiva**: Inteligencia comercial basada en datos estructurados

## Comandos de Desarrollo

### Inicio del Proyecto

```bash
# 1. Backend + Database (Docker)
docker-compose up -d

# 2. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 3. Crear superusuario (opcional)
docker-compose exec backend python manage.py createsuperuser

# 4. Frontend (Local - OBLIGATORIO)
cd frontend
npm install
npm run dev
```

### Comandos Frecuentes

#### Django (Docker)

```bash
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py test
```

#### Frontend (Local)

```bash
cd frontend
npm run dev      # Desarrollo
npm run build    # Build producción
npm run preview  # Preview build
```

## Patrón de Desarrollo

### Para nuevas funcionalidades:

1. **Backend**:
   - Crear en app `users` para funcionalidad de usuarios
   - **Usar app `entities`** como núcleo semántico para gestión de personas y organizaciones
   - **Usar app `world`** como campo semántico para perfilado, segmentación y clasificación
   - **Usar app `products`** para gestión de catálogo, pricing y configuración comercial
   - **Usar app `interactions`** para registrar y analizar customer journey e interacciones
   - Aprovechar perfilado semántico de entidades (Person, Organization)
   - Implementar lógica de negocio basada en contexto semántico
   - Utilizar analytics de entidades, productos e interacciones para insights comerciales
   - Aplicar framework Jobs-to-be-Done para análisis de customer journey
2. **Frontend**: Usar composables existentes (`useAuth`)
3. **API**: Extender servicios en `src/services/` con capacidades semánticas, de productos, de interacciones y de ofertas
4. **Autenticación**: Ya implementada y funcional
5. **Sistema de Entidades**: Utilizar endpoints `/api/entities/` para gestión de personas y organizaciones
6. **Campo Semántico**: Utilizar endpoints `/api/world/` para construcción de perfiles conceptuales
7. **Gestión de Productos**: Aprovechar endpoints `/api/products/` para catálogo y analytics comerciales
8. **Customer Journey**: Utilizar endpoints `/api/interactions/` para tracking completo de interacciones
9. **Ofertas Comerciales**: Utilizar endpoints `/api/offers/` para gestión de ofertas, campañas y analytics comerciales

### Para debugging:

1. **Backend**: Logs en Docker `docker-compose logs backend`
2. **Frontend**: DevTools en http://localhost:3000
3. **Database**: Acceso directo via docker-compose
4. **Testing Interactions**: Ejecutar `python test_complete_interactions_api.py` para verificar funcionalidad

## Estado del Proyecto

### ✅ Completado

- Arquitectura Django + Nuxt.js
- Sistema de autenticación completo
- **Aplicación Entities**: **Sistema de gestión de entidades** (personas y organizaciones con perfilado semántico)
- **Aplicación World**: **Campo semántico empresarial** (ontología y taxonomías para CRM)
- **Aplicación Products**: **Sistema completo de gestión de productos** con analytics
- **Aplicación Interactions**: **Sistema completo de gestión de customer journey** (27 endpoints, 100% funcional)
- **Aplicación Offers**: **Sistema completo de gestión de ofertas comerciales** (10 endpoints, analytics empresariales)
- **Aplicación Campaigns**: **Sistema completo de gestión de campañas comerciales** (7 endpoints, targeting semántico)
- Servicios API estructurados
- Configuración por ambientes
- Containerización híbrida
- Componentes base de usuario
- Configuración de seguridad
- **Optimización de base de datos**: Índices estratégicos documentados

### ⏳ En Desarrollo

- Funcionalidades completas de CRUD
- Testing automatizado
- Deployment en producción
- Optimización de performance

## Consideraciones Importantes

1. **El frontend NO está en Docker** - ejecutar localmente
2. **Aplicaciones Django**:
   - `users`: Gestión de usuarios y autenticación
   - **`entities`**: **Sistema de gestión de entidades** (personas y organizaciones con perfilado semántico)
   - **`world`**: **Campo semántico empresarial** (ontología y taxonomías para CRM)
   - **`products`**: **Sistema completo de gestión de productos** con analytics
   - **`interactions`**: **Sistema completo de gestión de customer journey** (27 endpoints, Jobs-to-be-Done)
3. **Sistema de Entidades**: La app `entities` gestiona personas y organizaciones como base del CRM
4. **Campo Semántico**: La app `world` define el vocabulario y contexto conceptual
5. **Customer Journey**: La app `interactions` registra y analiza todas las interacciones del cliente
6. **Configuración**: Via python-decouple y runtime config
7. **CORS**: Configurado para desarrollo local
8. **Performance**: Consultar documentación de INDEX_OPTIMIZATION para queries optimizados
9. **Ontología Empresarial**: Aprovechar taxonomías jerárquicas para clasificación semántica
10. **Jobs-to-be-Done**: Framework implementado para análisis de customer journey

## Patrones de Uso del Campo Semántico World

### Para Perfilado Semántico de Clientes

```python
# Backend - Construcción de perfil semántico
from world.models import Industry, Skill, Country, MarketSegment

client_profile = {
    'industry': Industry.objects.get(name="Financial Services"),
    'skills': Skill.objects.filter(name__in=["Python", "Data Analysis"]),
    'market_segments': MarketSegment.objects.filter(descriptors__name="Enterprise")
}

# Frontend - Selector semántico multi-dimensional
const clientProfile = {
    industry: await $fetch('/api/world/industries/'),
    skills: await $fetch('/api/world/skills/'),
    segments: await $fetch('/api/world/market-segments/')
}
```

### Para Búsqueda Conceptual y Semántica

```python
# Aprovechar relaciones semánticas para búsquedas inteligentes
/api/world/industries/?parent=null&search=tech          # Industrias tech de primer nivel
/api/world/descriptors/?family=1&level=2               # Descriptores específicos por familia
/api/world/market-segments/?descriptors__name=saas     # Segmentos relacionados con SaaS
```

### Para Taxonomías Organizacionales

```python
# Navegación semántica de la estructura empresarial
tech_industry = Industry.objects.get(name="Technology")
fintech_children = tech_industry.children.filter(name__icontains="fintech")

# Construcción de contexto semántico completo
semantic_context = {
    'industry_path': tech_industry.get_ancestors(),  # Jerarquía completa
    'related_skills': Skill.objects.filter(industry_context=tech_industry),
    'market_segments': MarketSegment.objects.filter(descriptors__industry=tech_industry)
}
```

### Para Análisis Semántico de CRM

```python
# Segmentación basada en campo semántico
clients_by_semantic_profile = Client.objects.annotate(
    semantic_score=Case(
        When(industry__parent__name="Technology", then=Value(3)),
        When(skills__name__in=ai_skills, then=Value(2)),
        default=Value(1)
    )
).filter(semantic_score__gte=2)

# Dashboard con insights semánticos
semantic_analytics = {
    'top_industries': Industry.objects.annotate(client_count=Count('clients')),
    'skill_demand': Skill.objects.annotate(demand_score=Count('client_profiles')),
    'market_trends': MarketSegment.objects.annotate(growth_rate=Avg('clients__revenue'))
}
```

## Patrones de Uso del Sistema de Entidades

### Para Perfilado Semántico de Personas

```python
# Backend - Construcción de perfil semántico completo
from entities.models import Person, IndividualProfile
from world.models import Industry, Skill, FunctionOrResponsibility, AcademicDegree

# Crear persona con perfil semántico
person = Person.objects.create(
    first_name="Ana",
    last_name="García",
    country_of_nationality_id=1,  # País desde world app
    gender="F"
)

# Perfil semántico extendido
profile = IndividualProfile.objects.create(
    person=person,
    academic_degree_id=1,  # Desde world app
    allows_marketing=True
)
profile.industries.set([1, 2])  # Industrias tech
profile.skills.set([1, 2, 3])  # Python, Django, etc.

# Obtener perfil semántico completo
semantic_profile = person.get_semantic_profile()
# Retorna: academic_degree, industries, skills, functions, comunicación

# Frontend - Selector semántico
const personProfile = {
    industries: await $fetch('/api/world/industries/'),
    skills: await $fetch('/api/world/skills/'),
    functions: await $fetch('/api/world/functions/'),
    degrees: await $fetch('/api/world/academic-degrees/')
}
```

### Para Analytics Organizacional

```python
# Segmentación de organizaciones por contexto semántico
from entities.models import Organization
from world.models import Industry, OrganizationType

# Analytics por industria y tipo
tech_orgs = Organization.objects.select_related('industry', 'org_type', 'country')
    .filter(industry__parent__name="Technology", is_active=True)
    .values('country__name', 'org_type__name')
    .annotate(count=Count('id'))

# Distribución geográfica de organizaciones
geo_analytics = Organization.objects.select_related('country')
    .filter(is_active=True)
    .values('country__name')
    .annotate(org_count=Count('id'))
    .order_by('-org_count')

# Perfil semántico organizacional
org_profile = organization.get_semantic_profile()
# Retorna: industry, org_type, country

# Frontend - Dashboard organizacional
const orgAnalytics = await $fetch('/api/entities/organizations/analytics/')
const geoDistribution = orgAnalytics.geographic_distribution
```

### Para Gestión de Contactos Unificada

```python
# Sistema de contactos para personas y organizaciones
from entities.models import ContactDetail, Person, Organization

# Contactos verificados para marketing
verified_contacts = ContactDetail.objects.filter(
    is_verified=True,
    is_primary=True,
    is_active=True
).select_related('person', 'organization')

# Contactos por tipo (personas vs organizaciones)
person_contacts = ContactDetail.objects.filter(
    person__isnull=False,
    contact_type="email"
).select_related('person')

org_contacts = ContactDetail.objects.filter(
    organization__isnull=False,
    contact_type="phone"
).select_related('organization')

# Analytics de contactos
contact_metrics = {
    'verified_percentage': ContactDetail.objects.filter(is_verified=True).count() / ContactDetail.objects.count() * 100,
    'marketing_allowed': ContactDetail.objects.filter(person__individualprofile__allows_marketing=True).count(),
    'primary_contacts': ContactDetail.objects.filter(is_primary=True).count()
}

# Frontend - Gestión omnicanal
const contactData = await $fetch('/api/entities/contacts/', {
    params: { verified: true, primary: true }
})
```

### Para Compliance y Privacidad GDPR

```python
# Gestión de consentimientos y privacidad
from entities.models import IndividualProfile

# Perfiles con consentimiento de marketing
marketing_allowed = IndividualProfile.objects.filter(
    allows_marketing=True,
    person__is_active=True
).select_related('person')

# Análisis de compliance
compliance_metrics = {
    'opt_in_rate': IndividualProfile.objects.filter(allows_marketing=True).count(),
    'privacy_compliant': IndividualProfile.objects.filter(
        allows_marketing__isnull=False
    ).count(),
    'contact_preferences': IndividualProfile.objects.values('preferred_contact_method')
        .annotate(count=Count('id'))
}

# Auditoría GDPR
gdpr_audit = Person.objects.filter(
    is_active=True,
    individualprofile__allows_marketing=True
).annotate(
    has_consent=Case(
        When(individualprofile__allows_marketing=True, then=Value(True)),
        default=Value(False)
    )
)

# Frontend - Centro de privacidad
const privacySettings = await $fetch('/api/entities/people/privacy-settings/')
const complianceReport = await $fetch('/api/entities/compliance/gdpr-audit/')
```

## Patrones de Uso del Sistema de Productos

### Para Gestión de Divisiones Organizacionales

```python
# Backend - Estructura organizacional por divisiones
from products.models import Division, ProductCategory, Product

# Crear estructura divisional
tech_division = Division.objects.create(
    name="Tecnología y Desarrollo",
    code="TECH",
    description="División especializada en soluciones tecnológicas"
)

# Organizar productos por división
software_category = ProductCategory.objects.create(
    name="Desarrollo de Software",
    division=tech_division
)

# Analytics por división
division_analytics = {
    'categories_count': tech_division.categories_count,
    'products_count': tech_division.products_count,
    'summary': tech_division.get_revenue_summary()
}

# Frontend - Navegación por divisiones
const divisionsData = await $fetch('/api/products/divisions/')
const divisionProducts = await $fetch(`/api/products/divisions/${divisionId}/products/`)
const divisionSummary = await $fetch(`/api/products/divisions/${divisionId}/summary/`)
```

### Para Clasificación Jerárquica de Productos

```python
# Estructura completa: División > Categoría > Subcategoría > Producto
from products.models import Division, ProductCategory, Product

# Navegación semántica multinivel
tech_products = Product.objects.filter(
    category__division__code="TECH",
    category__parent__name="Desarrollo Web"
).select_related('category', 'category__division')

# Path completo con división
for product in tech_products:
    print(product.category.full_path)  # "Tecnología y Desarrollo > Desarrollo Web > Frontend"
    print(product.category.absolute_level)  # Nivel incluyendo división

# Frontend - Selector jerárquico
const categoryTree = await $fetch('/api/products/categories/tree/')
const filteredByDivision = categories.filter(cat => cat.division === divisionId)
```

### Para Analytics Divisionales

```python
# Comparativa entre divisiones
/api/products/analytics/divisions/  # Dashboard comparativo de divisiones

# Métricas específicas por división
division_metrics = {
    'total_divisions': Division.objects.filter(is_active=True).count(),
    'divisions_with_products': Division.objects.filter(categories__product__isnull=False).distinct().count(),
    'top_divisions': Division.objects.annotate(
        products_count=Count('categories__product', filter=Q(categories__product__is_active=True))
    ).order_by('-products_count')[:5]
}

# Frontend - Dashboard divisional
const divisionAnalytics = await $fetch('/api/products/analytics/divisions/')
const performanceByDivision = divisionAnalytics.divisions_overview.distribution
```

## Patrones de Uso del Sistema de Interacciones

### Para Registro Completo de Customer Journey

```python
# Backend - Registrar interacción completa con contexto semántico
from interactions.models import Interaction, Touchpoint, Action, Agent, Channel

# Crear interacción con contexto completo
interaction = Interaction.objects.create(
    session_id="unique-session-123",
    person=persona_entity,  # Vinculada a entities app
    touchpoint=landing_page_touchpoint,  # Con contexto semántico de world
    action=click_action,
    agent=browser_agent,
    channel=website_channel,
    product=target_product,  # Vinculada a products app
    jtbd_stage="awareness",  # Framework Jobs-to-be-Done
    duration_seconds=45,
    latitude=-34.6037, longitude=-58.3816,  # Geolocalización
    metadata={"page_url": "/landing", "utm_source": "google", "conversion_score": 85}
)

# Frontend - Tracking de interacciones
const trackInteraction = async (interactionData) => {
    await $fetch('/api/interactions/interactions/', {
        method: 'POST',
        body: {
            session_id: generateSessionId(),
            touchpoint_id: touchpointId,
            action_id: actionId,
            agent_id: agentId,
            jtbd_stage: 'consideration',
            duration_seconds: timeSpent,
            metadata: enrichedContext
        }
    })
}
```

### Para Analytics Avanzados de Customer Journey

```python
# Analytics completo del funnel
funnel_analytics = await $fetch('/api/interactions/interactions/funnel_analysis/')
performance_metrics = {
    'awareness_to_consideration': funnel_analytics.conversion_rates['awareness_consideration'],
    'consideration_to_decision': funnel_analytics.conversion_rates['consideration_decision'],
    'decision_to_onboarding': funnel_analytics.conversion_rates['decision_onboarding'],
    'total_funnel_efficiency': funnel_analytics.overall_conversion_rate
}

# Analytics geográficos
geo_distribution = await $fetch('/api/interactions/interactions/geographic_distribution/')
market_insights = {
    'top_regions': geo_distribution.locations.slice(0, 10),
    'engagement_heatmap': geo_distribution.concentration_areas,
    'territorial_performance': geo_distribution.by_country
}

# Performance de touchpoints
touchpoint_analytics = await $fetch('/api/interactions/touchpoints/analytics/')
optimization_data = {
    'top_performers': touchpoint_analytics.top_touchpoints,
    'conversion_by_stage': touchpoint_analytics.touchpoints_by_stage,
    'class_performance': touchpoint_analytics.touchpoints_by_class
}
```

### Para Segmentación Comportamental Avanzada

```python
# Segmentación basada en patrones de interacción
from django.db.models import Count, Avg, Q

behavioral_segments = Interaction.objects.values(
    'person__id', 'person__first_name', 'person__last_name'
).annotate(
    total_interactions=Count('id'),
    avg_duration=Avg('duration_seconds'),
    funnel_depth=Count('jtbd_stage', filter=Q(jtbd_stage__in=['decision', 'onboarding'])),
    engagement_score=Count('id') * Avg('duration_seconds') / 100
).filter(total_interactions__gte=3).order_by('-engagement_score')

# Identificación de customer journey patterns
journey_patterns = Interaction.objects.values('session_id').annotate(
    journey_length=Count('id'),
    stages_covered=Count('jtbd_stage', distinct=True),
    total_duration=Sum('duration_seconds'),
    conversion_achieved=Case(
        When(jtbd_stage__in=['decision', 'onboarding'], then=Value(True)),
        default=Value(False),
        output_field=BooleanField()
    )
).filter(journey_length__gte=2)

# Frontend - Segmentación dinámica
const segmentUsers = async (criteria) => {
    const segments = await $fetch('/api/interactions/interactions/', {
        params: {
            jtbd_stage: criteria.stage,
            start_date: criteria.dateRange.start,
            end_date: criteria.dateRange.end,
            has_duration: true,
            search: criteria.searchTerm
        }
    })
    return processSegmentation(segments.results)
}
```

### Para Optimización de Performance de Touchpoints

```python
# Análisis de touchpoints por performance
touchpoint_performance = Touchpoint.objects.select_related(
    'touchpoint_class', 'assigned_staff', 'product'
).prefetch_related(
    'related_industries', 'related_functions', 'interactions'
).annotate(
    total_interactions=Count('interactions', filter=Q(interactions__is_active=True)),
    avg_duration=Avg('interactions__duration_seconds'),
    conversion_rate=Count(
        'interactions',
        filter=Q(interactions__jtbd_stage__in=['decision', 'onboarding'])
    ) * 100.0 / Count('interactions'),
    semantic_relevance=Count('related_industries') + Count('related_functions')
).order_by('-total_interactions')

# Identificación de touchpoints de alto valor
high_value_touchpoints = touchpoint_performance.filter(
    total_interactions__gte=10,
    conversion_rate__gte=15.0,
    semantic_relevance__gte=2
)

# Frontend - Dashboard de optimización
const optimizationDashboard = {
    touchpointMetrics: await $fetch('/api/interactions/touchpoints/analytics/'),
    performanceByStage: await $fetch('/api/interactions/touchpoints/by_funnel_stage/'),
    agentMetrics: await $fetch('/api/interactions/agents/analytics/'),
    conversionFunnel: await $fetch('/api/interactions/interactions/funnel_analysis/')
}
```

### Para Automatización Basada en Comportamiento

```python
# Triggers automatizados basados en patrones de interacción
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Interaction)
def analyze_customer_behavior(sender, instance, created, **kwargs):
    if created:
        # Análizar patrón de comportamiento
        recent_interactions = Interaction.objects.filter(
            person=instance.person,
            occurred_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Trigger automático según comportamiento
        if recent_interactions >= 5 and instance.jtbd_stage == 'consideration':
            # Asignar representative para seguimiento
            assign_representative_for_hot_lead(instance.person)

        elif instance.jtbd_stage == 'decision':
            # Notificar a equipo de ventas
            notify_sales_team(instance)

        elif instance.duration_seconds > 300:  # 5 minutos
            # Marcar como engaged user
            mark_as_engaged_user(instance.person)

# Workflows automatizados
def create_automated_workflow(trigger_conditions, actions):
    workflow = {
        'trigger': {
            'jtbd_stage': trigger_conditions['stage'],
            'min_interactions': trigger_conditions['threshold'],
            'timeframe': trigger_conditions['period']
        },
        'actions': [
            {'type': 'assign_staff', 'criteria': 'industry_expert'},
            {'type': 'send_content', 'template': 'consideration_nurture'},
            {'type': 'schedule_followup', 'delay_hours': 24}
        ]
    }
    return workflow

# Frontend - Configuración de workflows
const workflowConfig = {
    awarenessNurture: {
        triggers: { stage: 'awareness', interactions: 3, duration: '7days' },
        actions: ['send_welcome_series', 'assign_marketing_specialist']
    },
    decisionAcceleration: {
        triggers: { stage: 'consideration', interactions: 8, duration: '3days' },
        actions: ['assign_sales_rep', 'offer_demo', 'send_case_studies']
    }
}
```

### Para Análisis de Atribución y ROI

```python
# Análisis de atribución multicanal
attribution_analysis = Interaction.objects.values(
    'channel__name', 'touchpoint__funnel_stage'
).annotate(
    total_interactions=Count('id'),
    unique_persons=Count('person', distinct=True),
    conversions=Count('id', filter=Q(jtbd_stage__in=['decision', 'onboarding'])),
    avg_time_to_conversion=Avg(
        'occurred_at',
        filter=Q(jtbd_stage='decision')
    ),
    roi_score=Count('id') * Count('person', distinct=True) / 100
).order_by('-conversions')

# Análisis de customer lifetime journey
customer_journeys = Interaction.objects.values('person__id').annotate(
    first_interaction=Min('occurred_at'),
    last_interaction=Max('occurred_at'),
    journey_duration=Max('occurred_at') - Min('occurred_at'),
    total_touchpoints=Count('touchpoint', distinct=True),
    channels_used=Count('channel', distinct=True),
    conversion_achieved=Case(
        When(jtbd_stage='advocacy', then=Value(True)),
        default=Value(False)
    )
).filter(total_touchpoints__gte=2)

# Frontend - Dashboard de atribución
const attributionInsights = {
    channelPerformance: await $fetch('/api/interactions/interactions/analytics/'),
    multiTouchAttribution: calculateAttribution(interactions),
    customerLifetimeValue: computeCLV(customerJourneys),
    conversionPaths: mapConversionPaths(interactions)
}
```
