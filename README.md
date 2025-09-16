# 🦴 BackboneOS - CRM Full-Stack

> 🐳 **CONFIGURACIÓN OBLIGATORIA**: Este proyecto usa Docker Compose. Ver [DOCKER_README.md](DOCKER_README.md) para setup rápido.

> **Sistema de gestión de relaciones con clientes (CRM) construido con arquitectura moderna**

BackboneOS es el sistema CRM que se convertirá en el sistema operativo para la única función que Peter Druker consideró esencial en un negocio: la creación de clientes.

## 🚀 Inicio Rápido

```bash
# Script automatizado
./setup-dev.sh

# O paso a paso:
docker-compose up -d                                    # Backend + DB
docker-compose exec backend python manage.py migrate   # Migraciones
cd frontend && npm run dev                              # Frontend
```

## 🏗️ Arquitectura del Sistema

BackboneOS es una aplicación full-stack moderna que combina:

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Nuxt.js 3.17.4 + TypeScript 5.8.3
- **Base de Datos**: PostgreSQL 14
- **Caché y Sesiones**: Redis 7 con django-redis
- **Procesamiento Asíncrono**: Celery con Redis broker
- **Monitoreo de Tareas**: Flower Dashboard
- **Containerización**: Docker + Docker Compose (desarrollo híbrido)

### 🎯 Ecosistema de Aplicaciones

BackboneOS incluye **7 aplicaciones Django especializadas** que forman un ecosistema CRM completo:

- **🌍 World App**: Campo semántico empresarial con ontología y taxonomías
- **👤 Entities App**: Gestión de personas y organizaciones con perfilado semántico
- **🏢 Our Institution App**: Estructura organizacional propietaria completa
- **📦 Products App**: Sistema de catálogo comercial con analytics
- **💼 Offers App**: Centro de comercialización con pricing dinámico
- **🎯 Campaigns App**: Sistema de gestión de campañas comerciales multi-canal
- **🔄 Interactions App**: Framework completo de customer journey

### 🔄 Flujo de Valor Comercial

```
World (Ontología) → Entities (Clientes) → Products (Catálogo) → Offers (Comercialización) → Campaigns (Promoción) → Interactions (Journey)
```

## ⚠️ Configuración de Desarrollo Híbrida

**IMPORTANTE**: BackboneOS utiliza una arquitectura híbrida donde el backend y la base de datos están containerizados, pero el frontend se ejecuta localmente para optimizar el desarrollo.

### 🌐 URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js local)
- **Backend API**: http://localhost:8000/api/ (Docker)
- **Django Admin**: http://localhost:8000/admin (Docker)
- **Flower Dashboard**: http://localhost:5555 (Monitoreo de Celery)
- **Redis**: localhost:6379 (Caché y broker)

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

# 6. Crear datos de prueba de ofertas (opcional)
docker-compose exec backend python create_offers_data.py

# 7. Crear datos de prueba de campañas (opcional)
docker-compose exec backend python create_campaigns_data.py

# 8. Crear superusuario (opcional)
docker-compose exec backend python manage.py createsuperuser

# 8. Frontend (Local - OBLIGATORIO)
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

## 💻 Comandos de Desarrollo

### Backend (Docker)

```bash
# Migraciones
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Tests
docker-compose exec backend python manage.py test

# Ver logs
docker-compose logs -f backend
```

### Frontend (Local)

```bash
cd frontend

# Desarrollo
npm run dev

# Build para producción
npm run build

# Linting
npm run lint
```

## 📚 Documentación

La documentación del proyecto está organizada de forma modular para facilitar la navegación y el mantenimiento:

### 🗺️ [Navegación de Documentación](docs/NAVIGATION.md)

**Índice completo y mapa de navegación** - Encuentra rápidamente lo que necesitas

### 📖 Documentación Principal

- **[🏗️ Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Stack tecnológico y diseño de comunicación API-First
- **[🖥️ Backend Django](docs/BACKEND.md)** - API REST, aplicaciones Django y containerización
- **[🌐 Frontend Nuxt.js](docs/FRONTEND.md)** - SPA TypeScript, autenticación y componentes UI
- **[🧪 Testing](docs/TESTING.md)** - Infraestructura de testing moderna con Vitest

### 📱 Aplicaciones y Funcionalidades

- **[🔧 Aplicaciones Django](docs/APPS.md)** - 6 apps especializadas del ecosistema CRM
- **[🔗 API Reference](docs/API.md)** - 50+ endpoints REST con filtrado avanzado
- **[🎯 Casos de Uso](docs/USE_CASES.md)** - Ejemplos prácticos con código Python

### 📊 Gestión y Estado

- **[📈 Estado del Proyecto](docs/PROJECT_STATUS.md)** - Progreso, testing y roadmap
- **[📁 Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)** - Organización de archivos y carpetas

### 🛠️ Documentación Técnica Adicional

- **[🔴 Redis y Caché](docs/REDIS.md)** - Configuración de Redis, caché y sesiones optimizadas
- **[CLAUDE.md](CLAUDE.md)** - Guía técnica completa para desarrollo
- **[COMMANDS.md](COMMANDS.md)** - Comandos de desarrollo y deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Configuración de producción
- **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** - Auditoría de seguridad

## 📊 Estado del Proyecto

### ✅ Funcionalidades Completadas

- ✅ **Arquitectura Full-Stack**: Django + Nuxt.js + PostgreSQL
- ✅ **Sistema de Autenticación**: JWT + composables + middleware
- ✅ **7 Aplicaciones Django**: World, Entities, Our Institution, Products, Interactions, Offers, Campaigns
- ✅ **API REST Completa**: 50+ endpoints con filtrado avanzado
- ✅ **Optimización DB**: Índices estratégicos y consultas optimizadas
- ✅ **Testing Implementado**: Tests unitarios con coverage completo
- ✅ **Comandos de Gestión**: Automatización para inicialización de datos

### 🔄 En Desarrollo

- 🔄 **CRM Completo**: Lead management, pipeline de ventas
- 🔄 **Dashboard Analytics**: Métricas empresariales avanzadas
- 🔄 **Performance**: Optimización adicional de consultas

### 📋 Roadmap

- 📋 **Pipeline de Ventas**: Oportunidades, cotizaciones, seguimiento
- 📋 **Reportes Avanzados**: Business Intelligence integrado
- 📋 **Mobile App**: Aplicación móvil con React Native

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
