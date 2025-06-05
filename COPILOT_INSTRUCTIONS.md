# Instrucciones de Copilot para BackboneOS

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
│   └── world/                 # ✅ App de datos globales COMPLETA
│       ├── models.py          # 15+ modelos de referencia global
│       ├── views.py           # ViewSets con filtrado/búsqueda
│       ├── serializers.py     # Serializers completos + choice
│       ├── admin.py           # Admin interface configurada
│       ├── urls.py            # API endpoints estructurados
│       ├── migrations/        # Migraciones con índices optimizados
│       └── INDEX_OPTIMIZATION.md  # Documentación performance
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

## Configuración de Desarrollo

### ⚠️ IMPORTANTE: Arquitectura Híbrida

**El frontend NO está containerizado** - se ejecuta localmente mientras backend y DB están en Docker:

```bash
# Backend + Database (Docker)
docker-compose up -d

# Frontend (Local - REQUERIDO)
cd frontend
npm install
npm run dev
```

### URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js local)
- **Backend API**: http://localhost:8000/api/ (Docker)
- **Django Admin**: http://localhost:8000/admin (Docker)

## Tecnologías Implementadas

### Backend

- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Base de Datos**: PostgreSQL 14 (docker)
- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based (implementado)
- **CORS**: django-cors-headers configurado
- **Aplicaciones**:
  - `users` (no `myapp`) con `ExampleModel`
  - **`world`** ✅ Datos globales de referencia (COMPLETA)

### Frontend

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
   - **Usar app `world`** como campo semántico para perfilado, segmentación y clasificación
   - Aprovechar ontología empresarial existente (Industry, Skills, MarketSegments)
   - Implementar lógica de negocio basada en contexto semántico
2. **Frontend**: Usar composables existentes (`useAuth`)
3. **API**: Extender servicios en `src/services/` con capacidades semánticas
4. **Autenticación**: Ya implementada y funcional
5. **Campo Semántico**: Utilizar endpoints `/api/world/` para construcción de perfiles conceptuales

### Para debugging:

1. **Backend**: Logs en Docker `docker-compose logs backend`
2. **Frontend**: DevTools en http://localhost:3000
3. **Database**: Acceso directo via docker-compose

## Estado del Proyecto

### ✅ Completado

- Arquitectura Django + Nuxt.js
- Sistema de autenticación completo
- **Aplicación World**: **Campo semántico empresarial** (ontología y taxonomías para CRM)
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
   - **`world`**: **Campo semántico empresarial** (ontología y taxonomías para CRM)
3. **Campo Semántico**: La app `world` define el vocabulario y contexto conceptual
4. **Configuración**: Via python-decouple y runtime config
5. **CORS**: Configurado para desarrollo local
6. **Performance**: Consultar `world/INDEX_OPTIMIZATION.md` para queries semánticos eficientes
7. **Ontología Empresarial**: Aprovechar taxonomías jerárquicas para clasificación semántica

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

Esta configuración permite desarrollo eficiente con hot-reload del frontend, servicios backend estables en Docker, y un **campo semántico empresarial robusto** que potencia las capacidades de CRM con inteligencia contextual y clasificación ontológica.
