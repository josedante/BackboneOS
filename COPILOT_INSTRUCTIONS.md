# Instrucciones de Copilot para BackboneOS

Eres un desarrollador experto FullStack. Excelente en la computación en la nube, particularmente AWS; Desarrollo de backend en Python/Django; y el desarrollo frontend con Vuejs y React.

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
│   ├── world/                 # ✅ App de datos globales COMPLETA
│   │   ├── models.py          # 15+ modelos de referencia global
│   │   ├── views.py           # ViewSets con filtrado/búsqueda
│   │   ├── serializers.py     # Serializers completos + choice
│   │   ├── admin.py           # Admin interface configurada
│   │   ├── urls.py            # API endpoints estructurados
│   │   ├── migrations/        # Migraciones con índices optimizados
│   │   └── INDEX_OPTIMIZATION.md  # Documentación performance
│   └── products/              # ✅ App de PRODUCTOS COMPLETA
│       ├── models.py          # ProductCategory, Product, Modality, Customization
│       ├── views.py           # ViewSets con filtrado/búsqueda avanzada
│       ├── serializers.py     # Serializers optimizados (list/detail/create)
│       ├── admin.py           # Admin interface con optimizaciones
│       ├── urls.py            # API endpoints + analytics
│       ├── analytics.py       # Dashboard y analytics de productos
│       ├── migrations/        # Migraciones con constraints e índices
│       └── tests.py           # Tests unitarios
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
  - **`products`** ✅ Sistema de gestión de productos (COMPLETA)

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
   - **Usar app `products`** para gestión de catálogo, pricing y configuración comercial
   - Aprovechar ontología empresarial existente (Industry, Skills, MarketSegments)
   - Implementar lógica de negocio basada en contexto semántico
   - Utilizar analytics de productos para insights comerciales
2. **Frontend**: Usar composables existentes (`useAuth`)
3. **API**: Extender servicios en `src/services/` con capacidades semánticas y de productos
4. **Autenticación**: Ya implementada y funcional
5. **Campo Semántico**: Utilizar endpoints `/api/world/` para construcción de perfiles conceptuales
6. **Gestión de Productos**: Aprovechar endpoints `/api/products/` para catálogo y analytics comerciales

### Para debugging:

1. **Backend**: Logs en Docker `docker-compose logs backend`
2. **Frontend**: DevTools en http://localhost:3000
3. **Database**: Acceso directo via docker-compose

## Estado del Proyecto

### ✅ Completado

- Arquitectura Django + Nuxt.js
- Sistema de autenticación completo
- **Aplicación World**: **Campo semántico empresarial** (ontología y taxonomías para CRM)
- **Aplicación Products**: **Sistema completo de gestión de productos** con analytics
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
   - **`products`**: **Sistema completo de gestión de productos** con analytics
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
