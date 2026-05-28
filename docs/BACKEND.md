# Backend Django - BackboneOS

## 🎯 Backend Django Application

### 📋 Información General

El backend de BackboneOS está construido con Django 5.x + Django REST Framework, diseñado como una **API REST robusta** que sirve datos al frontend y cualquier cliente futuro de manera completamente desacoplada.

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
- **django-cors-headers**: Configuración CORS para frontend
- **JWT Authentication**: Autenticación basada en tokens
- **Django Admin**: Interface administrativa completa

### Containerización

- **Docker**: Containerización del backend
- **Docker Compose**: Orquestación de servicios (backend + PostgreSQL)

## 🏗️ Arquitectura Backend

### Estructura de Aplicaciones Django

```
backend/
├── 📁 backend/              # Configuración principal de Django
│   ├── settings.py         # Configuración con python-decouple
│   ├── urls.py            # URLs principales y API routing
│   ├── wsgi.py            # WSGI application
│   └── fields.py          # Campos personalizados
├── 📁 users/               # ✅ Gestión de usuarios y autenticación
├── 📁 world/               # ✅ Campo semántico empresarial (COMPLETO)
├── 📁 entities/            # ✅ Gestión de entidades (COMPLETO)
├── 📁 our_institution/     # ✅ Estructura organizacional (COMPLETO)
├── 📁 products/            # ✅ Sistema de productos (COMPLETO)
├── 📁 interactions/        # ✅ Framework de interacciones (COMPLETO)
├── 📁 offers/              # ✅ Sistema de ofertas (COMPLETO)
├── 📄 manage.py            # CLI de Django
├── 📄 requirements.txt     # Dependencias Python
└── 📄 Dockerfile          # Configuración Docker
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

## 🔌 API REST Architecture

### Estructura de URLs Base

```
/api/
├── auth/                   # Autenticación JWT
├── users/                  # Gestión de usuarios
├── world/                  # Campo semántico empresarial
├── entities/               # Gestión de entidades
├── our-institution/        # Estructura organizacional
├── products/               # Catálogo de productos
├── interactions/           # Framework de interacciones
└── offers/                 # Ofertas comerciales
```

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

# Tests con coverage
coverage run manage.py test
coverage report
```

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

## 📚 Documentación Específica de Apps

- **[World App](../backend/world/INDEX_OPTIMIZATION.md)** - Optimización de consultas semánticas
- **[Entities App](../backend/entities/INDEX_OPTIMIZATION.md)** - Performance de entidades
- **[Our Institution App](../backend/our_institution/README.md)** - Estructura organizacional
- **[Products App](../backend/products/README.md)** - Sistema de productos
- **[Interactions App](../backend/interactions/README.md)** - Framework de interacciones
- **[Offers App](../backend/offers/README.md)** - Sistema de ofertas comerciales

---

> **Backend BackboneOS** - API REST robusta y escalable para el ecosistema CRM
