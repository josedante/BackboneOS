# Arquitectura del Sistema BackboneOS

## 🏗️ Arquitectura General

BackboneOS es una aplicación full-stack moderna que combina:

- **Operator UI**: Django templates + Tailwind (`backend/templates/`, `backend/static/`)
- **Backend**: Django 5.x + Django REST Framework
- **Base de Datos**: PostgreSQL 14
- **Caché y Sesiones**: Redis 7 con django-redis
- **Procesamiento Asíncrono**: Celery Worker + Beat
- **Monitoreo de Tareas**: Flower Dashboard
- **Containerización**: Docker + Docker Compose (backend, DB, Redis, Celery)

## 🎯 Valor Empresarial del Ecosistema

BackboneOS representa un **ecosistema CRM completo** donde cada aplicación aporta valor específico:

### 🔄 Flujo de Valor Comercial

```
World (Ontología) → Entities (Clientes) → Products (Catálogo) → Offers (Comercialización) → Campaigns (Promoción) → Interactions (Journey)
```

- **World App**: Define el **vocabulario empresarial** para segmentación precisa
- **Entities App**: Gestiona **personas y organizaciones** con perfilado semántico
- **Products App**: Estructura el **catálogo de valor** organizacional
- **Offers App**: Transforma productos en **ofertas comerciales** con pricing dinámico
- **Campaigns App**: Planifica **estructuras de marketing** y enlaces campaña–touchpoint
- **Interactions App**: Registra y optimiza el **customer journey** completo (substrato)
- **Our Institution App**: Proporciona **contexto organizacional** para todas las operaciones

### 💡 Ventaja Competitiva

La integración semántica entre todas las apps permite:

- **Segmentación Inteligente**: Ofertas dirigidas por industria, función, y perfil semántico
- **Pricing Contextual**: Precios específicos por canal, geografía y audiencia
- **Analytics Integrados**: Insights de performance desde producto hasta conversión
- **Customer Journey Completo**: Tracking desde awareness hasta advocacy
- **Escalabilidad Empresarial**: Arquitectura preparada para crecimiento masivo

## URLs de Acceso (desarrollo)

- **CRM**: http://localhost:8000/ (login en `/login/`)
- **API REST**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/ (gestión de usuarios)

## 🛠️ Stack Tecnológico

### Backend (Django)

- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Base de Datos**: PostgreSQL 14 (Docker)
- **Caché**: Redis 7 con django-redis para optimización de rendimiento
- **Sesiones**: Redis como backend de sesiones con fallback a base de datos
- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based (implementado)
- **CORS**: django-cors-headers configurado

### Interfaz de Operador (Django templates)

> El paquete standalone Next.js `frontend/` se eliminó en la Fase 6 de la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md). El CRM ahora se renderiza con plantillas Django en el mismo proceso que la API.

- **Renderizado**: Plantillas Django con herencia (`{% extends "base_dashboard.html" %}`), sin SPA
- **Estilos**: Tailwind CSS compilado en build (`backend/package.json`, `npm run tailwind:build`), servido como estático por WhiteNoise; `static/dist/` en `.gitignore`
- **Formularios**: `forms.py` por app (captura server-rendered)
- **Autenticación**: sesión Django (`@login_required`, `/login/`, `/logout/`)
- **Hidratación dinámica**: HTMX / Alpine.js permitidos por la regla de arquitectura, **no usados actualmente**

## 🔄 Arquitectura de Comunicación

### Flujo de Datos y Servicios

Un único proceso Django sirve el CRM HTML y la API REST, compartiendo la [capa de servicios y selectores](BACKEND.md#-capa-de-servicios-y-selectores):

```
Cliente externo / webhooks / tracking ──→ API REST  ┐
Navegador del operador ──────────────────→ CRM HTML ┤
                                                     │ (mismo proceso Django :8000)
                              ┌──────────────────────┴──────────────┐
                              │  selectors.py (lecturas)             │
                              │  services.py  (escrituras)           │
                              └──────────────────────┬──────────────┘
                                                     │
                                              PostgreSQL :5432
                                                     │
                                              ┌──────┴──────┐
                                              │  Redis :6379│
                                              └──────┬──────┘
                          ┌──────────────────────────┼──────────────────────┐
                     Celery Worker            Celery Beat                  Flower
                     (Async Tasks)            (Scheduled)             (Monitor :5555)
```

### Comunicación Entre Servicios

- **Navegador (operador) → Backend**: peticiones HTTP a las vistas de plantilla (`template_views`)
- **Cliente externo / webhooks → Backend**: peticiones HTTP a la API REST (`/api/...`)
- **CRM y API → datos**: ambas superficies llaman a `selectors`/`services` (sin loopback HTTP interno)
- **Backend → Redis**: Caché y sesiones
- **Backend → PostgreSQL**: ORM queries y transacciones
- **Celery Worker ← Redis**: Consume tareas del broker
- **Celery Beat → Redis**: Programa tareas periódicas
- **Flower ← Redis**: Monitorea estado de workers

### Separación de Responsabilidades

**Lógica compartida (selectors / services)** 🧩

- **`selectors.py`**: lecturas, querysets optimizados y contextos para plantillas y API
- **`services.py`**: escrituras, transacciones y validaciones de negocio compartidas
- Fuente canónica de la convención: [BACKEND.md](BACKEND.md#-capa-de-servicios-y-selectores)

**API REST (DRF)** 🎯

- **Superficie de integración**: clientes externos, webhooks (Meta/Shopify) y scripts de tracking
- **Endpoints estructurados** con filtrado avanzado; delegan en `selectors`/`services`
- **Autenticación**: JWT tokens

**CRM de Operador (plantillas Django)** 🖥️

- **Interfaz de Usuario**: páginas server-rendered que extienden `base_dashboard.html`
- **Captura de datos**: formularios Django que escriben vía `services.py`
- **Autenticación**: sesión Django (`@login_required`)

## 🚀 Servicios de Infraestructura

### Redis (Caché y Broker)

- **Puerto**: 6379
- **Funciones**:
  - Caché de aplicación (DB 1)
  - Broker de Celery (DB 0)
  - Backend de resultados Celery (DB 2)
  - Sesiones de usuario (con fallback a DB)
- **Configuración**: Persistencia en volumen Docker
- **Optimización**: Pool de conexiones y manejo de excepciones

### Celery Worker

- **Función**: Procesamiento asíncrono de tareas
- **Casos de Uso**:
  - Envío de emails
  - Procesamiento de archivos
  - Generación de reportes
  - Tareas de limpieza de datos
- **Configuración**: Auto-restart y logging
- **Escalabilidad**: Múltiples workers según carga

### Celery Beat

- **Función**: Programador de tareas periódicas
- **Casos de Uso**:
  - Limpieza de sesiones expiradas
  - Backups automáticos
  - Sincronización de datos
  - Reportes periódicos
- **Configuración**: Persistencia de schedule

### Flower Dashboard

- **Puerto**: 5555
- **Función**: Monitoreo y administración de Celery
- **Características**:
  - Estado de workers en tiempo real
  - Historial de tareas
  - Estadísticas de rendimiento
  - Interfaz web intuitiva
- **Acceso**: http://localhost:5555

### API preservada para integraciones

La API REST se mantiene como superficie de integración de primera clase, independiente del CRM:

1. **Backend expone API REST** completa e independiente
2. **Clientes externos, webhooks y tracking** la consumen de forma desacoplada
3. **Documentación API** permite múltiples clientes
4. **Testing independiente** de cada capa
5. **Lógica compartida**: API y CRM reutilizan `selectors`/`services` sin duplicación

## 🌐 Configuración de Desarrollo

### Proceso único containerizado

Tras la consolidación, el desarrollo usa un **único proceso Django containerizado** (no hay servidor frontend separado):

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
cd backend && npm run tailwind:build   # solo cuando cambian los estilos
```

**Ventajas:**

- 🔒 **Ambiente Consistente**: PostgreSQL, Redis y Django idénticos en todos los ambientes
- 🚀 **Deploy Simple**: una sola imagen Docker; en runtime un único proceso Python
- 🔧 **Dependencias Aisladas**: sin conflictos de Python/pip locales
- 📊 **Datos Persistentes**: base de datos compartida entre desarrolladores
- 🎨 **CSS en build**: Tailwind se compila en build (o con `tailwind:watch` en el host durante desarrollo, ya que `docker-compose` monta `./backend:/app` y sobreescribe el `dist/` de la imagen)
