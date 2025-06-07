# BackboneOS - CRM Full-Stack

> **Sistema de gestión de relaciones con clientes (CRM) construido con arquitectura moderna**

BackboneOS (https://backboneos.com/), es el sistema CRM que se convertirá en el sistema operativo para la única función que Peter Druker consideró esencial en un negocio: la creación de clientes debería convertirse en una empresa SaaS.

BackboneOS es una aplicación full-stack moderna que combina:

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Nuxt.js 3.17.4 + TypeScript 5.8.3
- **Base de Datos**: PostgreSQL 14
- **Containerización**: Docker + Docker Compose (desarrollo híbrido)

## 🏗️ Arquitectura del Sistema

### Campo Semántico Empresarial (World App)

BackboneOS incluye un **sistema de ontología empresarial** que define el vocabulario y taxonomías organizacionales:

- **Clasificación Geográfica**: Países, regiones y mercados
- **Ontología Sectorial**: Industrias jerárquicas con sectores y subsectores
- **Taxonomía de Competencias**: Skills, funciones y roles organizacionales
- **Segmentación de Mercado**: Clasificación multi-dimensional de mercados
- **Sistema de Descriptores**: Etiquetado semántico universal

### Sistema de Gestión de Entidades (Entities App)

Núcleo semántico de gestión de personas y organizaciones:

- **Perfilado Semántico**: Clasificación multidimensional de personas y organizaciones
- **Gestión de Contactos**: Sistema unificado de comunicación omnicanal
- **Analytics Organizacional**: Inteligencia de mercado y demografía
- **Direcciones Físicas**: Gestión flexible de ubicaciones múltiples
- **Compliance**: GDPR ready con consentimientos y privacidad

### Sistema de Estructura Organizacional (Our Institution App)

Gestión completa de la estructura organizacional propietaria:

- **Jerarquía Organizacional**: `Organization → Division → Unit → Position` y equipos transversales
- **Arquitectura Sin Redundancia**: Relaciones optimizadas y constraints únicos contextuales
- **Gestión de Sedes**: Ubicaciones físicas con categorización (HQ, Sucursales, Oficinas)
- **API REST Completa**: Endpoints con filtrado jerárquico y métricas automatizadas
- **Comandos de Gestión**: Automatización para crear estructura organizacional

### Sistema de Gestión de Productos (Products App)

Sistema completo de catálogo comercial con:

- **Estructura Divisional**: Organización por divisiones empresariales
- **Clasificación Jerárquica**: Categorías y subcategorías de productos
- **Motor de Personalización**: Configuración y adaptación de productos
- **Analytics Comerciales**: Dashboard de insights y métricas
- **Pricing Multi-moneda**: Gestión avanzada de precios

### Sistema de Interacciones (Interactions App)

Framework completo de gestión de customer journey:

- **Jobs-to-be-Done Framework**: Seguimiento de etapas del trabajo del cliente
- **Touchpoints Management**: Gestión de puntos de contacto omnicanal
- **Session Tracking**: Monitoreo de sesiones y comportamiento
- **Agent Analytics**: Análisis de performance de agentes
- **Channel Optimization**: Optimización de canales de comunicación

## 📁 Estructura del Proyecto

```
BackboneOS/
├── backend/                    # Backend Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── backend/               # Configuración Django
│   │   ├── settings.py        # python-decouple, CORS
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── users/                 # App de usuarios y autenticación
│   │   ├── models.py          # ExampleModel implementado
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   ├── entities/              # ✅ Sistema de Gestión de Entidades (COMPLETA)
│   │   ├── models.py          # Person, Organization, ContactDetail, IndividualProfile
│   │   ├── views.py           # ViewSets con perfilado semántico
│   │   ├── serializers.py     # Serializers optimizados para CRM
│   │   ├── admin.py           # Interface administrativa completa
│   │   ├── urls.py            # API endpoints de entidades
│   │   ├── migrations/        # Migraciones con índices estratégicos
│   │   ├── INDEX_OPTIMIZATION.md  # Documentación de performance
│   │   └── README.md          # Documentación completa de la app
│   ├── our_institution/       # ✅ Sistema de Estructura Organizacional (COMPLETA)
│   │   ├── models.py          # OurOrganization, Division, Unit, Position, Team, Seat
│   │   ├── views.py           # ViewSets con jerarquía organizacional optimizada
│   │   ├── serializers.py     # Serializers con información contextual
│   │   ├── admin.py           # Interface administrativa para estructura organizacional
│   │   ├── urls.py            # API endpoints de estructura organizacional
│   │   ├── tests.py           # Tests unitarios completos (14 tests exitosos)
│   │   ├── migrations/        # Migraciones con constraints e índices
│   │   ├── management/        # Comandos de gestión automatizada
│   │   ├── COMPLETION_REPORT.md  # Reporte de implementación completa
│   │   └── README.md          # Documentación técnica completa
│   ├── world/                 # ✅ Campo Semántico Empresarial (COMPLETA)
│   │   ├── models.py          # 15+ modelos de ontología empresarial
│   │   ├── views.py           # ViewSets con filtrado/búsqueda semántica
│   │   ├── serializers.py     # Serializers completos + choice
│   │   ├── admin.py           # Interface administrativa optimizada
│   │   ├── urls.py            # API endpoints estructurados
│   │   ├── migrations/        # Migraciones con índices optimizados
│   │   └── INDEX_OPTIMIZATION.md  # Documentación de performance
│   ├── products/              # ✅ Sistema de Gestión de Productos (COMPLETA)
│   │   ├── models.py          # Division, ProductCategory, Product, Modality
│   │   ├── views.py           # ViewSets con filtrado/búsqueda avanzada
│   │   ├── serializers.py     # Serializers optimizados (list/detail/create)
│   │   ├── admin.py           # Interface administrativa con optimizaciones
│   │   ├── urls.py            # API endpoints + analytics
│   │   ├── analytics.py       # Dashboard y analytics comerciales
│   │   ├── migrations/        # Migraciones con constraints e índices
│   │   └── tests.py           # Tests unitarios
│   └── interactions/          # ✅ Sistema de Interacciones (COMPLETA)
│       ├── models.py          # Medium, Channel, Agent, Session, Touchpoint, Interaction
│       ├── views.py           # ViewSets con analytics y framework JTBD
│       ├── serializers.py     # Serializers contextuales para customer journey
│       ├── admin.py           # Interface administrativa optimizada
│       ├── urls.py            # 27 API endpoints funcionales
│       ├── migrations/        # Migraciones con índices para performance
│       └── README.md          # Documentación completa del sistema
├── frontend/                  # Frontend Nuxt.js (NO containerizado)
│   ├── composables/
│   │   └── useAuth.ts        # ✅ Sistema auth JWT completo
│   ├── src/
│   │   ├── components/
│   │   │   └── UserList.vue
│   │   └── services/
│   │       ├── api.ts        # ✅ API service centralizado
│   │       └── userService.ts
│   ├── pages/
│   │   ├── index.vue
│   │   ├── login.vue         # ✅ Autenticación implementada
│   │   ├── analytics/        # Páginas de analytics
│   │   ├── customers/        # Gestión de clientes
│   │   ├── leads/           # Gestión de leads
│   │   ├── products/        # Gestión de productos
│   │   └── reports/         # Reportes y dashboards
│   ├── middleware/
│   │   └── auth.ts           # ✅ Middleware de autenticación
│   ├── plugins/
│   │   └── auth.client.ts    # ✅ Plugin cliente
│   ├── nuxt.config.ts        # ✅ Configuración completa
│   └── package.json          # ✅ Nuxt 3.17.4 + TypeScript 5.8.3
├── docker-compose.yml        # ⚠️ Frontend ejecuta localmente
├── .env                      # Variables de entorno
├── CLAUDE.md                 # ✅ Guía técnica del proyecto
├── COMMANDS.md               # Comandos de desarrollo
├── DEPLOYMENT.md             # Guía de deployment
└── README.md
```

## ⚠️ Configuración de Desarrollo Híbrida

**IMPORTANTE**: BackboneOS utiliza una arquitectura híbrida donde el backend y la base de datos están containerizados, pero el frontend se ejecuta localmente para optimizar el desarrollo.

### URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js local)
- **Backend API**: http://localhost:8000/api/ (Docker)
- **Django Admin**: http://localhost:8000/admin (Docker)

## 🚀 Instalación y Ejecución

### Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd Proyecto-OpenSource

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar Backend + Database (Docker)
docker-compose up -d

# 4. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 5. Crear estructura organizacional (opcional)
docker-compose exec backend python manage.py create_organization_structure

# 6. Crear superusuario (opcional)
docker-compose exec backend python manage.py createsuperuser

# 7. Frontend (Local - OBLIGATORIO)
cd frontend
npm install
npm run dev
```

### Script de Inicio Automático

```bash
# Hacer ejecutable y ejecutar
chmod +x start.sh
./start.sh
```

## 🛠️ Stack Tecnológico

### Backend (Django)

- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Base de Datos**: PostgreSQL 14 (Docker)
- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based (implementado)
- **CORS**: django-cors-headers configurado
- **Aplicaciones**:
  - `users` (no `myapp`) con `ExampleModel`
  - **`entities`** ✅ Gestión de personas y organizaciones (COMPLETA)
  - **`our_institution`** ✅ Estructura organizacional propietaria (COMPLETA)
  - **`world`** ✅ Campo semántico empresarial (COMPLETA)
  - **`products`** ✅ Sistema de gestión de productos (COMPLETA)
  - **`interactions`** ✅ Framework de customer journey (COMPLETA)

### Frontend (Nuxt.js)

- **Framework**: Nuxt.js 3.17.4
- **Lenguaje**: TypeScript 5.8.3
- **UI Framework**: Nuxt UI 3.1.3
- **Módulos**: @nuxt/content, @nuxt/fonts, @nuxt/icon, @nuxt/image, @nuxt/scripts, @nuxt/test-utils
- **Autenticación**: ✅ Sistema completo implementado
- **HTTP Client**: API service con $fetch
- **Linting**: ESLint 9.27.0

---

## 🏢 Sistema Our Institution - Estructura Organizacional

### 🎯 Propósito

La aplicación `our_institution` implementa un **sistema completo de gestión de estructura organizacional** para BackboneOS, proporcionando una representación jerárquica y semánticamente rica de la organización propietaria del sistema CRM.

### 🏗️ Arquitectura de Modelos

#### Jerarquía Organizacional

```
OurOrganization (Organización Propietaria)
├── Division (Divisiones Empresariales)
│   ├── Unit (Unidades Organizacionales) [Jerárquica]
│   │   └── Position (Cargos/Posiciones)
│   └── Team (Equipos Transversales)
└── Seat (Sedes/Oficinas)
```

#### Modelos Implementados

- **`OurOrganization`**: Identidad institucional única del sistema BackboneOS

  - **Constraint**: Solo una organización puede estar activa
  - **Integración**: Conectada con `world.Country`, `world.Industry`, `world.OrganizationType`
  - **Métricas**: Conteos automáticos de divisiones, sedes, unidades, equipos y posiciones

- **`Division`**: Grandes áreas organizacionales (Tecnología, Comercial, Operaciones)

  - **Constraint**: `(organization, name)` y `(organization, code)` únicos
  - **Métricas**: Conteos de unidades, equipos y posiciones por división

- **`Unit`**: Estructura jerárquica con soporte padre-hijo ilimitado

  - **Constraint**: `(division, code)` único por división
  - **Navegación**: Path completo automático (`division > parent > unit`)
  - **Relación**: `division` obligatorio (CASCADE)

- **`Position`**: Posiciones específicas dentro de unidades organizacionales

  - **Constraint**: `(unit, code)` único por unidad
  - **Navegación**: Acceso a organización vía `unit.division.organization`
  - **Relación**: `unit` obligatorio (CASCADE)

- **`Team`**: Equipos que cruzan múltiples unidades dentro de una división

  - **Constraint**: `(division, code)` y `(division, name)` únicos
  - **Relación**: `division` obligatorio (CASCADE)

- **`Seat`**: Ubicaciones físicas de la organización
  - **Categorías**: HQT (Sede Principal), SUB (Sucursal), OFF (Oficina), LOC (Local)
  - **Relación**: Directa con organización

### 🔌 API REST de Estructura Organizacional

#### Endpoints Disponibles

```bash
# Gestión organizacional
GET /api/our-institution/organization/     # Organización propietaria
GET /api/our-institution/divisions/        # Divisiones empresariales
GET /api/our-institution/seats/            # Sedes y oficinas

# Estructura jerárquica
GET /api/our-institution/units/            # Unidades (con jerarquía)
GET /api/our-institution/positions/        # Posiciones/cargos
GET /api/our-institution/teams/            # Equipos transversales
```

#### Capacidades de Filtrado

- **Filtros Jerárquicos**: Por división, unidad padre, etc.
- **Búsquedas**: En nombres, códigos y descripciones
- **Ordenamiento**: Multifacético con `?ordering=name,created_at`
- **Métricas**: Conteos automáticos en respuestas

### 🛠️ Comandos de Gestión

```bash
# Crear estructura organizacional completa
docker-compose exec backend python manage.py create_organization_structure

# Recrear desde cero (elimina datos existentes)
docker-compose exec backend python manage.py create_organization_structure --reset
```

#### Estructura Creada Automáticamente

- **Organización**: BackboneOS (Backbone Operating Systems SAC)
- **3 Divisiones**: Tecnología, Comercial, Operaciones
- **8 Unidades** con jerarquía padre-hijo
- **10 Posiciones** distribuidas por unidades
- **4 Equipos** transversales por división
- **2 Sedes**: Principal y Comercial

### 🧪 Sistema de Pruebas

```bash
# Ejecutar tests de our_institution
docker-compose exec backend python manage.py test our_institution

# Tests implementados (14 tests, 100% éxito)
# - Tests de modelo (unicidad, constraints, jerarquías)
# - Tests de integración (estructura organizacional completa)
```

### 🎯 Valor para BackboneOS CRM

- **Gestión Organizacional Nativa**: Estructura empresarial real en el CRM
- **Flexibilidad**: Soporte para reorganizaciones futuras
- **Trazabilidad**: Historial de cambios organizacionales
- **Integración CRM**: Base para ownership en leads/oportunidades
- **Contexto Organizacional**: Estructura para reporting y analytics
- **Workflow Empresarial**: Ruteo de procesos por división/unidad

---

- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based
- **CORS**: django-cors-headers configurado

### Frontend (Nuxt.js)

- **Framework**: Nuxt.js 3.17.4
- **Lenguaje**: TypeScript 5.8.3
- **UI Framework**: Nuxt UI 3.1.3
- **Módulos**: @nuxt/content, @nuxt/fonts, @nuxt/icon, @nuxt/image
- **HTTP Client**: API service con $fetch
- **Linting**: ESLint 9.27.0

### Aplicaciones Django

#### ✅ Users App

- Gestión de usuarios y autenticación
- Modelos de usuario extendidos
- Sistema JWT implementado

#### ✅ World App - Campo Semántico Empresarial

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

#### ✅ Entities App - Sistema de Gestión de Entidades

**Núcleo semántico de personas y organizaciones**

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

#### ✅ Our Institution App - Sistema de Estructura Organizacional

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

#### ✅ Products App - Sistema de Gestión de Productos

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

#### ✅ Interactions App - Sistema de Interacciones

**Framework completo de gestión de customer journey**

- **🎯 Jobs-to-be-Done**: `Interaction` con etapas JTBD (8 modelos)
- **📡 Touchpoints**: `Touchpoint`, `TouchpointClass` (puntos de contacto)
- **🔄 Sesiones**: `Session` (seguimiento de comportamiento)
- **🤖 Agentes**: `Agent` (browsers, humans, bots)
- **📢 Canales**: `Medium`, `Channel`, `Action`, `ActionType`

**Características Avanzadas**:

- **27 Endpoints API**: Completamente funcionales y testeados
- **Analytics Dashboard**: Métricas de customer journey y performance
- **Integración Semántica**: Conexión completa con World App
- **Performance Optimizada**: < 60ms tiempo promedio de respuesta
- **Framework JTBD**: Seguimiento completo del trabajo del cliente

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

/api/interactions/actions/ # Acciones específicas
/api/interactions/agents/ # Agentes (browsers, humanos, bots)
/api/interactions/agents/analytics/ # Analytics de agentes
/api/interactions/sessions/ # Sesiones de usuario
/api/interactions/touchpoint-classes/ # Clases de touchpoints
/api/interactions/touchpoints/ # Puntos de contacto
/api/interactions/touchpoints/analytics/ # Analytics de touchpoints
/api/interactions/interactions/ # Interacciones completas
/api/interactions/interactions/analytics/ # Analytics de interacciones

````

## 💻 Comandos de Desarrollo

### Backend (Docker)

```bash
# Migraciones
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Shell de Django
docker-compose exec backend python manage.py shell

# Tests
docker-compose exec backend python manage.py test

# Ver logs
docker-compose logs -f backend

# Reconstruir contenedores
docker-compose up --build -d

# Detener servicios
docker-compose down
````

### Frontend (Local)

```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview build
npm run preview

# Linting
npm run lint
```

### Base de Datos

```bash
# Acceso directo a PostgreSQL
docker-compose exec postgres psql -U postgres -d backboneos

# Backup de base de datos
docker-compose exec postgres pg_dump -U postgres backboneos > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres backboneos < backup.sql
```

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

## 📊 Estado del Proyecto

### ✅ Funcionalidades Completadas

- ✅ **Arquitectura Full-Stack**: Django + Nuxt.js + PostgreSQL
- ✅ **Sistema de Autenticación**: JWT + composables + middleware
- ✅ **Sistema de Entidades**: Gestión de personas y organizaciones con perfilado semántico (Entities App)
- ✅ **Estructura Organizacional**: Sistema completo de gestión organizacional propietaria (Our Institution App)
- ✅ **Campo Semántico Empresarial**: Ontología y taxonomías completas (World App)
- ✅ **Sistema de Productos**: Gestión de catálogo con analytics (Products App)
- ✅ **Sistema de Interacciones**: Framework completo de customer journey (Interactions App)
- ✅ **API REST Completa**: Endpoints estructurados con filtrado avanzado
- ✅ **Optimización DB**: Índices estratégicos y consultas optimizadas
- ✅ **Interface Administrativa**: Django Admin configurado
- ✅ **Testing Implementado**: Tests unitarios con coverage completo
- ✅ **Comandos de Gestión**: Automatización para inicialización de datos
- ✅ **Configuración por Ambientes**: Desarrollo y producción

### 🔄 En Desarrollo

- 🔄 **CRM Completo**: Lead management, pipeline de ventas
- 🔄 **Dashboard Analytics**: Métricas empresariales avanzadas
- 🔄 **Testing Automatizado**: Tests unitarios y de integración
- 🔄 **Deployment**: Configuración de producción
- 🔄 **Performance**: Optimización adicional de consultas

### 📋 Roadmap

- 📋 **Gestión de Clientes**: CRUD completo con perfilado semántico
- 📋 **Pipeline de Ventas**: Oportunidades, cotizaciones, seguimiento
- 📋 **Reportes Avanzados**: Business Intelligence integrado
- 📋 **Mobile App**: Aplicación móvil con React Native
- 📋 **Integraciones**: APIs externas y webhooks

## 🛡️ Seguridad y Performance

### Características de Seguridad

- **Autenticación JWT**: Tokens seguros con refresh automático
- **CORS Configurado**: Políticas de origen cruzado
- **Variables de Entorno**: Configuración sensible protegida
- **Validaciones Django**: Validaciones robustas en backend
- **Sanitización Frontend**: Protección XSS en Nuxt.js

### Optimizaciones de Performance

- **Índices de BD**: Optimización de consultas documentada
- **Serializers Contextuales**: Diferentes niveles de detalle
- **Prefetch Related**: Consultas optimizadas para relaciones
- **Cache de API**: Estrategias de cache implementadas

## 📚 Documentación Adicional

- **CLAUDE.md**: Guía técnica completa del proyecto
- **COMMANDS.md**: Lista de comandos de desarrollo
- **DEPLOYMENT.md**: Guía de deployment y producción
- **world/INDEX_OPTIMIZATION.md**: Optimización de consultas semánticas
- **entities/INDEX_OPTIMIZATION.md**: Optimización de performance para entidades
- **our_institution/README.md**: Documentación completa del sistema organizacional
- **our_institution/COMPLETION_REPORT.md**: Reporte de implementación y tests
- **products/README.md**: Documentación del sistema de productos
- **interactions/README.md**: Documentación del framework de interacciones
- **SECURITY_AUDIT_REPORT.md**: Reporte de auditoría de seguridad

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

> **BackboneOS** - Sistema CRM empresarial con ontología semántica y gestión avanzada de productos
