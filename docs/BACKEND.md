# Backend Django - BackboneOS

## 🎯 Backend Django Application

### 📋 Información General

El backend de BackboneOS está construido con Django 5.x + Django REST Framework. Tras la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md) (el paquete Next.js `frontend/` se eliminó en la Fase 6), el backend es un **único proceso Django** que sirve dos superficies sobre la misma base de datos y la misma lógica de negocio:

- **API REST** (`/api/...`) para clientes externos, webhooks de ingestión (p. ej. Meta/Shopify) y scripts de tracking.
- **CRM de operador** renderizado con plantillas Django (`/`, `/products/`, `/entities/`, `/interactions/`, `/campaigns/`, `/offers/`) protegido con autenticación de sesión.

Ambas superficies comparten la lógica de lectura y escritura a través de la [capa de servicios y selectores](#-capa-de-servicios-y-selectores), de modo que no existe duplicación ni llamadas HTTP internas (loopback) entre el CRM y la API.

## 🛠️ Stack Tecnológico Backend

### Core Framework

- **Django**: 5.x (Framework web robusto para Python)
- **Django REST Framework**: API REST completa y documentada
- **Python**: 3.11+ (Lenguaje de programación principal)

### Base de Datos

- **PostgreSQL**: 14 (Base de datos relacional principal)
- **Psycopg2**: Conector Python-PostgreSQL optimizado

### Configuración y Seguridad

- **python-decouple**: Gestión de variables de entorno
- **django-cors-headers**: CORS para clientes externos de la API (el CRM es same-origin)
- **JWT Authentication**: Autenticación basada en tokens para la API REST
- **Autenticación de sesión**: `@login_required`, `/login/`, `/logout/` para el CRM HTML
- **Django Admin**: Interface administrativa completa (gestión de usuarios)

### Interfaz de Operador (CRM HTML)

- **Plantillas Django**: herencia con `{% extends "base_dashboard.html" %}` (sin SPA)
- **Tailwind CSS**: compilado en tiempo de build (`backend/package.json`, `npm run tailwind:build`) y servido como estático por WhiteNoise; `static/dist/` está en `.gitignore`
- **Formularios Django**: `forms.py` por app para captura server-rendered
- **Hidratación dinámica**: HTMX / Alpine.js están permitidos por la regla de arquitectura para necesidades futuras, pero **no se usan actualmente**

### Containerización

- **Docker**: Containerización del backend (proceso Python único en runtime)
- **Docker Compose**: Orquestación de servicios (backend, PostgreSQL, Redis, Celery)

## 🏗️ Arquitectura Backend

### Estructura de Aplicaciones Django

```
backend/
├── 📁 backend/              # Configuración principal de Django
│   ├── settings/           # Configuración modular con python-decouple
│   ├── urls.py            # URLs principales, API routing y montaje de rutas HTML
│   ├── wsgi.py            # WSGI application
│   └── fields.py          # Campos personalizados
├── 📁 users/               # ✅ Gestión de usuarios y autenticación
├── 📁 world/               # ✅ Campo semántico empresarial (COMPLETO)
├── 📁 entities/            # ✅ Gestión de entidades (COMPLETO) + CRM HTML
├── 📁 our_institution/     # ✅ Estructura organizacional (COMPLETO)
├── 📁 products/            # ✅ Sistema de productos (COMPLETO) + CRM HTML
├── 📁 interactions/        # ✅ Framework de interacciones (COMPLETO) + CRM HTML (substrato)
├── 📁 offers/              # ✅ Sistema de ofertas (COMPLETO) + CRM HTML
├── 📁 campaigns/           # ✅ Campañas comerciales (COMPLETO) + CRM HTML
├── 📁 websites/            # ✅ Tracking e interacciones web
├── 📁 connectors/          # ✅ Resolución de touchpoints
├── 📁 core/                # Comandos de gestión compartidos
├── 📁 dashboard/           # ✅ Home del CRM y layout compartido (base_dashboard.html)
├── 📄 README.md            # Punto de entrada del backend
├── 📁 templates/           # Plantillas raíz compartidas (base_dashboard, includes/, registration/)
├── 📁 static/              # src/input.css (fuente Tailwind) → dist/styles.css (build)
├── 📄 package.json         # Toolchain Tailwind (tailwind:build / tailwind:watch)
├── 📄 manage.py            # CLI de Django
├── 📄 requirements.txt     # Dependencias Python
└── 📄 Dockerfile          # Configuración Docker
```

#### Estructura típica de una app con CRM HTML

Las apps que exponen tanto API como CRM siguen este patrón de módulos:

```
products/
├── models.py              # Modelos de datos
├── selectors.py           # 🔵 Lecturas: querysets, agregados, contextos de plantilla
├── services.py            # 🟢 Escrituras: mutaciones y transacciones (API + HTML)
├── serializers.py         # DRF (sin lógica de escritura/M2M; delega en services)
├── views.py               # ViewSets DRF (delegan en selectors/services)
├── forms.py               # Formularios Django para el CRM HTML
├── template_views.py      # Vistas HTML del CRM (leen selectors, escriben services)
├── template_urls.py       # URLconf HTML (namespace `<app>_html`)
├── urls.py                # URLconf de la API REST
├── templates/<app>/       # Plantillas que extienden base_dashboard.html
├── tests.py               # Tests de API
├── tests_template_views.py# Tests de las vistas HTML
└── test_factories.py      # factory_boy para datos de prueba
```

### Aplicaciones Django Especializadas

**🌍 World App - Campo Semántico**

- **Propósito**: Ontología empresarial y vocabulario semántico
- **Modelos**: Country, Industry, Skill, MarketSegment, etc.
- **API**: 15+ endpoints con filtrado jerárquico

**👤 Entities App - Gestión de Entidades**

- **Propósito**: Personas, organizaciones y contactos
- **Modelos**: Person, Organization, ContactDetail, etc.
- **API**: Perfilado semántico y analytics organizacional

**🏢 Our Institution App - Estructura Organizacional**

- **Propósito**: Estructura interna de la organización
- **Modelos**: Division, Unit, Position, Team, Seat
- **API**: Jerarquía organizacional con métricas

**📦 Products App - Catálogo de Productos**

- **Propósito**: Gestión de productos y categorías
- **Modelos**: Product, ProductCategory, Division, etc.
- **API**: Catálogo con analytics comerciales

**🔄 Interactions App - Customer Journey**

- **Propósito**: Framework de interacciones y touchpoints
- **Modelos**: Interaction, Touchpoint, Session, Agent, etc.
- **API**: 27 endpoints para customer journey completo

**💼 Offers App - Ofertas Comerciales**

- **Propósito**: Centro de comercialización con pricing
- **Modelos**: ProductOffering con segmentación avanzada
- **API**: Ofertas con targeting y analytics
- **CRM**: CRUD de operador en `/offers/`

**🎯 Campaigns App - Campañas Comerciales**

- **Propósito**: Estructuras de marketing planificadas y enlaces campaña–touchpoint
- **Modelos**: Campaign, CampaignTouchpoint con targeting semántico
- **API**: Campañas con analytics y acción `duplicate`
- **CRM**: CRUD de operador en `/campaigns/`

**🧭 Dashboard App - Home del CRM**

- **Propósito**: Página de inicio del CRM y layout compartido para todas las apps
- **Plantillas**: `base_dashboard.html`, `includes/header.html`, `includes/sidebar.html`
- **Selector**: `get_home_context()` (v1 estático; conteos reales en una versión posterior)

## 🧩 Capa de Servicios y Selectores

> Convención **obligatoria** introducida en la consolidación del frontend. Es la fuente canónica; otros documentos enlazan aquí en lugar de re-explicarla.

Toda la lógica de datos vive en dos módulos por app, y **tanto las vistas DRF como las vistas de plantilla llaman exactamente a las mismas funciones**:

| Módulo | Responsabilidad | Usado por |
|--------|-----------------|-----------|
| `selectors.py` | Solo lectura: querysets, agregados, optimizaciones (`select_related`/`prefetch_related`), diccionarios de contexto para el dashboard | ViewSets DRF (`get_queryset`, acciones `analytics`), `template_views` |
| `services.py` | Escrituras: mutaciones, transacciones, validaciones de negocio compartidas (`validate_*`) | Acciones DRF (`perform_create`/`perform_update`/`perform_destroy`), handlers POST del CRM |

Reglas derivadas (ver [`.cursor/rules/consolidated-frontend.mdc`](../.cursor/rules/consolidated-frontend.mdc)):

1. **Proceso único**: el contenedor en runtime es un único proceso Python/Django. Node/npm solo se usa en build para compilar Tailwind.
2. **Preservar la API REST**: no eliminar ni modificar los endpoints públicos de DRF; son obligatorios para webhooks externos y tracking.
3. **Sin loopback**: las vistas HTML nunca hacen peticiones HTTP a la propia API; obtienen datos vía `selectors`.
4. **Serializers sin lógica de escritura**: la lógica de escritura y M2M se retiró de `serializers.py`; los ViewSets delegan en `services.py`. Las validaciones compartidas (p. ej. `validate_interaction_entities`) se invocan desde el serializer `validate` y desde el servicio.
5. **Herencia de plantillas**: las páginas del CRM usan `{% extends "base_dashboard.html" %}`.

```mermaid
flowchart LR
  API["DRF /api/..."]
  HTML["template_views (CRM)"]
  Sel["selectors.py (lecturas)"]
  Svc["services.py (escrituras)"]
  DB[("PostgreSQL")]
  API --> Sel
  API --> Svc
  HTML --> Sel
  HTML --> Svc
  Sel --> DB
  Svc --> DB
```

## 🔌 API REST Architecture

### Estructura de URLs Base

```
/api/                       # Catálogo JSON de la API (URL name `api-catalog`)
├── auth/                   # Autenticación JWT
├── users/                  # Gestión de usuarios
├── world/                  # Campo semántico empresarial
├── entities/               # Gestión de entidades
├── our-institution/        # Estructura organizacional
├── products/               # Catálogo de productos
├── interactions/           # Framework de interacciones
├── offers/                 # Ofertas comerciales
└── campaigns/              # Campañas comerciales
```

Las rutas HTML del CRM se montan en paralelo desde los `template_urls.py` de cada app
(`/`, `/products/`, `/entities/`, `/interactions/`, `/campaigns/`, `/offers/`, `/login/`, `/logout/`).
El catálogo JSON, que antes vivía en `/`, se movió a `/api/` con el nombre `api-catalog`
para evitar el conflicto con el `api-root` del router de DRF.

### Características de la API

**🔒 Autenticación y Seguridad**

- **JWT Tokens**: Autenticación stateless
- **Permission Classes**: Control de acceso granular
- **CORS Headers**: Configurado para desarrollo híbrido
- **Rate Limiting**: Protección contra abuso (futuro)

**📊 Serializers Contextuales**

- **List Serializers**: Información resumida para listados
- **Detail Serializers**: Información completa para vistas detalle
- **Choice Serializers**: Datos para formularios y selects
- **Analytics Serializers**: Métricas y estadísticas

**🔍 Filtrado y Búsqueda Avanzada**

- **Django Filter**: Filtrado por múltiples campos
- **Search Fields**: Búsqueda full-text en campos relevantes
- **Ordering**: Ordenamiento multifacético
- **Pagination**: Paginación automática configurada

## 💾 Gestión de Datos

### Modelos y Relaciones

**🔗 Relaciones Semánticas**

- **Foreign Keys**: Relaciones directas optimizadas
- **Many-to-Many**: Relaciones complejas con through models
- **Generic Relations**: Flexibilidad para relaciones polimórficas
- **Constraints**: Unicidad contextual y validaciones de negocio

**📈 Optimización de Performance**

- **Índices Estratégicos**: Documentados en cada app
- **Select Related**: Consultas optimizadas para foreign keys
- **Prefetch Related**: Optimización de many-to-many
- **Database Functions**: Consultas complejas optimizadas

### Migraciones y Esquema

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations

# Revertir migraciones
python manage.py migrate app_name 0001
```

## 🛠️ Comandos de Gestión

### Comandos Personalizados

**📊 Inicialización de Datos**

```bash
# Crear estructura organizacional completa
python manage.py create_organization_structure

# Crear datos de prueba para ofertas
python create_offers_data.py

# Poblar datos de productos
python populate_products.py

# Crear divisiones de productos
python create_divisions_data.py
```

**🧪 Testing y Validación**

```bash
# Ejecutar todos los tests
python manage.py test

# Tests de una app específica
python manage.py test our_institution

# Tests de las vistas HTML del CRM (por app)
python manage.py test products.tests_template_views

# Tests con coverage
coverage run manage.py test
coverage report
```

> Las apps con CRM incluyen `tests_template_views.py` (vistas HTML) y `test_factories.py` (datos de prueba con `factory_boy`). Ver [TESTING.md](TESTING.md) para el gate consolidado y la configuración `backend.test_settings`.

### Gestión de Base de Datos

```bash
# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell

# Dump de datos
python manage.py dumpdata app_name > fixtures.json

# Cargar fixtures
python manage.py loaddata fixtures.json
```

## 🐳 Containerización

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose Services

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
    depends_on:
      - postgres

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: backboneos
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 🔧 Configuración y Settings

### Variables de Entorno

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/backboneos
CORS_ALLOWED_ORIGINS=https://your-app.example.com
JWT_SECRET_KEY=your-jwt-secret
```

### Settings Modulares

```python
# backend/settings.py
from decouple import config

# Base configuration
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

# Database
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# CORS for external API clients (operator CRM is same-origin Django HTML)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
```

## 📊 Monitoring y Logging

### Django Admin

**🎛️ Interface Administrativa Completa**

- **User Management**: Gestión de usuarios y permisos
- **Data Management**: CRUD completo de todos los modelos
- **Bulk Actions**: Acciones en lote para gestión eficiente
- **Custom Actions**: Acciones personalizadas por modelo
- **Search & Filters**: Búsqueda y filtrado avanzado

### Logging Configuration

```python
# Configuración de logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## 🚀 Deployment y Producción

### Configuración de Producción

```python
# Configuración específica para producción
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = '/app/staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Health Checks

```python
# Health check endpoint
@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': timezone.now()
    })
```

## 🔮 Roadmap Backend

### Próximas Funcionalidades

1. **📈 Analytics Avanzados**

   - Métricas en tiempo real
   - Business Intelligence integrado
   - Reports customizables

2. **🔔 Notificaciones**

   - Sistema de notificaciones push
   - Email notifications
   - Webhooks para integraciones

3. **🌐 Integraciones**

   - APIs de terceros
   - Conectores CRM externos
   - Sincronización de datos

4. **🔒 Seguridad Avanzada**

   - Rate limiting
   - API key management
   - Audit trails

5. **⚡ Performance**
   - Redis caching
   - Database optimization
   - Query monitoring

## Documentación específica

- **[backend/README.md](../backend/README.md)** — arranque, tests, índice de apps
- **[websites.md](backend/websites.md)** — tracking web
- **[connectors.md](backend/connectors.md)** — touchpoints y fallback
- **[interactions.md](backend/interactions.md)** — substrato de journey
- **[DATABASE_INDEXES.md](DATABASE_INDEXES.md)** — política de índices
- **README por app**: `world`, `entities`, `our_institution`, `products`, `interactions`, `offers`, `campaigns`, `websites`, `connectors`, `users`
- **[Consolidación del Frontend](consolidation/FRONTEND_CONSOLIDATION.md)** — migración del CRM a plantillas Django

---

> **Backend BackboneOS** - API REST robusta y escalable para el ecosistema CRM
