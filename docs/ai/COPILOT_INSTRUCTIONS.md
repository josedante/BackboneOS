# BackboneOS - Instrucciones de Copilot

## 🎯 Visión del Proyecto

**BackboneOS** es un CRM moderno que se convierte en el sistema operativo para la creación de clientes según Peter Drucker.

## 🏗️ Arquitectura

### Stack Tecnológico

- **Backend + CRM UI**: Django 5.x + DRF + templates (🐳 Docker obligatorio)
- **Base de Datos**: PostgreSQL 14 (🐳 Docker obligatorio)
- **Cache & Broker**: Redis 7 (🐳 Docker)
- **Task Queue**: Celery Worker + Beat (🐳 Docker)
- **Monitoring**: Flower Dashboard (🐳 Docker)
- **Auth**: JWT + Token-based

### URLs de Desarrollo

- **CRM**: http://localhost:8000/
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin
- **Flower**: http://localhost:5555
- **Redis**: localhost:6379

## 🐳 Comandos Docker CRÍTICOS

### Comandos Correctos

```bash
# Iniciar desarrollo
docker compose up -d
cd backend && npm run tailwind:build   # si cambiaste estilos CRM

# Django (SIEMPRE con docker-compose exec)
docker-compose exec backend python manage.py startapp
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py createsuperuser
```

### ❌ Comandos Prohibidos

```bash
# NUNCA usar directamente:
python manage.py runserver
python manage.py startapp
python manage.py migrate
pip install -r requirements.txt
```

## 🚀 Servicios de Infraestructura

### Redis (Multi-DB Setup)

- **DB 0**: Celery broker (cola de tareas)
- **DB 1**: Django cache (consultas, sesiones)
- **DB 2**: Celery results (resultados de tareas)
- **Comandos**:
  ```bash
  docker-compose exec redis redis-cli ping
  docker-compose logs -f redis
  ```

### Celery Worker

- **Función**: Procesamiento asíncrono
- **Casos de uso**: Emails, reportes, archivos
- **Comandos**:
  ```bash
  docker-compose logs -f celery
  docker-compose exec backend celery -A backend inspect active
  ```

### Celery Beat

- **Función**: Tareas programadas
- **Casos de uso**: Limpieza, backups, sincronización
- **Comandos**:
  ```bash
  docker-compose logs -f celery-beat
  docker-compose exec backend celery -A backend inspect stats
  ```

### Flower Dashboard

- **URL**: http://localhost:5555
- **Función**: Monitoreo de Celery
- **Características**: Workers, tasks, estadísticas

## 📱 Aplicaciones Django (6 Apps Completas)

### 1. **entities** - Gestión de Entidades

- **Modelos**: Person, Organization, ContactDetail, IndividualProfile
- **Propósito**: Núcleo semántico CRM para personas y organizaciones
- **API**: Sistema completo de perfilado semántico

### 2. **world** - Datos Globales

- **Modelos**: 15+ modelos (Country, Industry, EducationLevel, etc.)
- **Propósito**: Vocabulario empresarial y contexto semántico
- **API**: Datos de referencia con búsqueda semántica

### 3. **products** - Catálogo

- **Modelos**: ProductCategory, Product, Modality, Customization
- **Propósito**: Gestión completa de productos con analytics
- **API**: CRUD + búsqueda + analytics empresariales

### 4. **interactions** - Customer Journey

- **Modelos**: 8 modelos (Medium, Channel, Action, etc.)
- **Propósito**: Sistema completo de customer journey
- **API**: 27 endpoints + analytics avanzados

### 5. **offers** - Ofertas Comerciales

- **Modelos**: ProductOffering con segmentación semántica
- **Propósito**: Gestión de ofertas con targeting empresarial
- **API**: 10 endpoints + analytics de performance

### 6. **campaigns** - Campañas

- **Modelos**: Campaign, CampaignTouchpoint
- **Propósito**: Campañas con targeting semántico
- **API**: 7 endpoints + analytics de ROI

## 🔐 Autenticación Implementada

### Sistema JWT Completo

- **Composable**: `useAuth.ts`
- **Middleware**: `auth.ts`
- **Login**: Página funcional
- **Cookies**: Seguras por ambiente

### Endpoints Auth

```
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/user/
```

## 🛠️ Convenciones

### Naming

- **Modelos**: PascalCase (`Person`, `Organization`)
- **Campos**: snake_case (`created_at`, `is_active`)
- **Endpoints**: kebab-case (`/customer-journey/`)

### API Structure

```
/api/entities/          # Entidades base
/api/world/            # Datos globales
/api/products/         # Productos
/api/interactions/     # Customer journey
/api/offers/           # Ofertas
/api/campaigns/        # Campañas
```

## 🚀 Comandos Frecuentes

### Docker

```bash
docker-compose up -d              # Iniciar
docker-compose down               # Detener
docker-compose logs -f backend    # Logs
```

### CRM styles

```bash
cd backend && npm run tailwind:build
```

### Django

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py test
```

## 📈 Características CRM

### Perfilado Semántico

- Clasificación por industria y función
- Contexto geográfico y cultural
- Integración con vocabulario empresarial

### Customer Journey Completo

- 8 modelos para tracking completo
- Analytics empresariales avanzados
- Attribution analysis multi-touch

### Comercialización

- Ofertas con segmentación semántica
- Campañas con targeting empresarial
- Analytics de ROI y performance

## 📚 Documentación Específica

### Arquitectura y Servicios

- **Arquitectura General**: `docs/ARCHITECTURE.md`
- **Servicios de Infraestructura**: `docs/SERVICES_REFERENCE.md`
- **Celery y Redis**: `docs/CELERY_REDIS.md`
- **Configuración Redis**: `docs/REDIS.md`

### Aplicaciones Django

- **Entities**: `docs/copilot/COPILOT_ENTITIES.md`
- **Interactions**: `docs/copilot/COPILOT_INTERACTIONS.md`
- **Products**: `docs/copilot/COPILOT_PRODUCTS.md`
- **World**: `docs/copilot/COPILOT_WORLD.md`

### Desarrollo y Deployment

- **Comandos**: `docs/operations/COMMANDS.md`
- **Docker**: `docs/operations/DOCKER_README.md`
- **Deployment**: `docs/operations/DEPLOYMENT.md`
- **Estado del Proyecto**: `docs/PROJECT_STATUS.md`
- **Offers**: `docs/copilot/COPILOT_OFFERS.md`
- **Campaigns**: `docs/copilot/COPILOT_CAMPAIGNS.md`

## 🎯 Desarrollo Diario

### Flujo Típico

1. `docker compose up -d` (backend + DB + Redis)
2. Abrir http://localhost:8000/login/
3. `cd backend && npm run tailwind:watch` si editas CSS del CRM
4. Usar VS Code tasks para comandos Django en Docker

### Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Template HTML tests (consolidation gate)
docker compose run --rm -e DJANGO_SETTINGS_MODULE=backend.test_settings backend \
  python manage.py test dashboard.tests products.tests_template_views
```

## 💡 Mejores Prácticas

### Para nuevas funcionalidades:

1. **Backend**: Usar apps existentes como base semántica
2. **Templates**: Extender `base_dashboard.html` y selectors/services compartidos
3. **API**: Extender servicios con capacidades semánticas
4. **Autenticación**: Ya implementada y funcional
5. **Entidades**: Utilizar para gestión de personas y organizaciones
6. **Campo Semántico**: Usar para perfilado y clasificación
7. **Customer Journey**: Aprovechar para tracking de interacciones

### Para debugging:

1. **Backend**: `docker-compose logs backend`
2. **CRM**: DevTools en http://localhost:8000
3. **Database**: Acceso directo via docker compose

---

**RECORDATORIO**: Siempre usar Docker para backend. CRM HTML y API viven en el mismo servicio Django.
