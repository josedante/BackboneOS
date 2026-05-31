# 🦴 BackboneOS - Infraestructura, Atribución y Predicción listas para la era de la IA

BackboneOS es una **infraestructura "Sovereign First-Party" de código abierto** diseñada para capturar, limpiar y unificar cada punto de contacto de tus clientes directamente dentro de tus propios servidores (PostgreSQL/Redis). Es la Columna Vertebral de tu Sistema de Creación de Clientes: integra todos los puntos de contacto, prueba qué funciona y consigue convertir más a menor costo. BackboneOS te ayudará a conocer qué mueve a tus clientes.


> 🐳 **CONFIGURACIÓN OBLIGATORIA**: Este proyecto usa Docker Compose para facilitarte el desarrollo en un ambiente local de tu computadora. Ver [DOCKER_README.md](docs/operations/DOCKER_README.md) para setup rápido.


## 🚀 Inicio Rápido

```bash
# Script automatizado
./setup-dev.sh

# O paso a paso:
docker-compose up -d                                    # Backend + DB + Redis
docker-compose exec backend python manage.py migrate   # Migraciones
cd backend && npm run tailwind:build                    # CSS del CRM (si cambiaste estilos)
```

## Tests

```bash
cd backend && ./run_tests_docker.sh --coverage --html-report
./run_tests_docker.sh --type unit --coverage
```

Guía completa: [docs/TESTING.md](docs/TESTING.md). Punto de entrada del backend: [backend/README.md](backend/README.md).

## 🏗️ Arquitectura del Sistema

BackboneOS es una aplicación full-stack moderna que combina:

- **Operator UI**: Django templates + Tailwind CSS (servido por el mismo proceso backend)
- **Backend**: Django 5.x + Django REST Framework
- **Base de Datos**: PostgreSQL 14
- **Caché y Sesiones**: Redis 7 con django-redis
- **Procesamiento Asíncrono**: Celery con Redis broker
- **Monitoreo de Tareas**: Flower Dashboard
- **Containerización**: Docker + Docker Compose (backend, DB, Redis, Celery)

### 🎯 Ecosistema de Aplicaciones

BackboneOS incluye **aplicaciones Django** de dominio CRM, tracking y conectores (ver [docs/APPS.md](docs/APPS.md)):

- **World**: ontología y taxonomías
- **Entities**: personas y organizaciones
- **Our Institution**: estructura organizacional
- **Products**, **Offers**, **Campaigns**: catálogo y comercialización
- **Interactions**: substrato de customer journey
- **Websites**: tracking e interacciones web
- **Connectors**: resolución de touchpoints
- **Dashboard** / **Users** / **Core**: CRM, autenticación y utilidades

### 🔄 Flujo de Valor Comercial

```
World (Ontología) → Entities (Clientes) → Products (Catálogo) → Offers (Comercialización) → Campaigns (Promoción) → Interactions (Journey)
```

## 🌐 URLs de Acceso

- **CRM (Django templates)**: http://localhost:8000/ — login en `/login/`; products, entities, interactions, campaigns, offers — ver [docs/consolidation/FRONTEND_CONSOLIDATION.md](docs/consolidation/FRONTEND_CONSOLIDATION.md)
- **Gestión de usuarios**: http://localhost:8000/admin/ (Django Admin; enlace **Users** en el sidebar)
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
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

### Estilos CRM (Tailwind en backend)

```bash
cd backend
npm install
npm run tailwind:build    # compila static/dist/styles.css
npm run tailwind:watch    # desarrollo con recarga
```

## 📚 Documentación

La documentación del proyecto está organizada de forma modular para facilitar la navegación y el mantenimiento:

### 🗺️ [Índice de Documentación](docs/README.md) · [Navegación](docs/NAVIGATION.md)

**Índice por categoría y mapa de navegación** - Encuentra rápidamente lo que necesitas

### 📖 Documentación Principal

- **[🏗️ Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Stack tecnológico y diseño de comunicación API-First
- **[🖥️ Backend Django](docs/BACKEND.md)** - API REST, aplicaciones Django y containerización
- **[🌐 Operator UI (Django)](docs/FRONTEND.md)** - Templates, Tailwind, consolidación frontend
- **[🧪 Testing](docs/TESTING.md)** - Infraestructura de testing (Django/pytest + factory_boy)

### 📱 Aplicaciones y Funcionalidades

- **[🔧 Aplicaciones Django](docs/APPS.md)** - Apps del ecosistema CRM y tracking
- **[🔗 API Reference](docs/API.md)** - 50+ endpoints REST con filtrado avanzado
- **[🎯 Casos de Uso](docs/USE_CASES.md)** - Ejemplos prácticos con código Python

### 📊 Gestión y Estado

- **[📈 Estado del Proyecto](docs/PROJECT_STATUS.md)** - Progreso, testing y roadmap
- **[📁 Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)** - Organización de archivos y carpetas

### 🛠️ Documentación Técnica Adicional

- **[🔴 Redis y Caché](docs/REDIS.md)** - Configuración de Redis, caché y sesiones optimizadas
- **[CLAUDE.md](docs/ai/CLAUDE.md)** - Guía técnica completa para desarrollo
- **[COMMANDS.md](docs/operations/COMMANDS.md)** - Comandos de desarrollo y deployment
- **[DEPLOYMENT.md](docs/operations/DEPLOYMENT.md)** - Configuración de producción
- **[SECURITY_AUDIT_REPORT.md](docs/reports/SECURITY_AUDIT_REPORT.md)** - Auditoría de seguridad

## 📊 Estado del Proyecto

### ✅ Funcionalidades Completadas

- ✅ **Arquitectura Single-Process**: Django (HTML CRM + API REST) + PostgreSQL
- ✅ **Sistema de Autenticación**: JWT (API REST) + sesión Django (`@login_required`) para el CRM
- ✅ **Apps Django**: World, Entities, Our Institution, Products, Interactions, Offers, Campaigns, Websites, Connectors, Dashboard
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
