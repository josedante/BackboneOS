# BackboneOS - Instrucciones Core de Copilot

## 🎯 Información Esencial

**BackboneOS** es un CRM moderno con arquitectura Django + Nuxt.js + PostgreSQL.

### Stack Tecnológico

- **Backend**: Django 5.x + DRF (🐳 Docker obligatorio)
- **Frontend**: Nuxt.js 3.17.4 + TypeScript (💻 local)
- **BD**: PostgreSQL 14 (🐳 Docker obligatorio)
- **Auth**: JWT + Token-based

### URLs de Desarrollo

- **Frontend**: http://localhost:3000 (Nuxt.js)
- **Backend API**: http://localhost:8000/api/ (Django)
- **Admin**: http://localhost:8000/admin (Django)

## 🐳 Comandos Docker OBLIGATORIOS

### Iniciar Desarrollo

```bash
# Iniciar entorno completo
docker-compose up -d

# Frontend (único comando local)
cd frontend && npm run dev
```

### Comandos Django (SIEMPRE con docker-compose exec)

```bash
# Migraciones
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py makemigrations

# Shell y gestión
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py createsuperuser

# Tests
docker-compose exec backend python manage.py test
```

### ⚠️ COMANDOS PROHIBIDOS

```bash
# ❌ NUNCA usar directamente:
python manage.py runserver
python manage.py migrate
pip install -r requirements.txt
```

## 📱 Aplicaciones Django

### Apps Principales (6 aplicaciones completas)

1. **`entities`** - Gestión de personas y organizaciones
2. **`world`** - Datos globales de referencia (países, industrias, etc.)
3. **`products`** - Catálogo y gestión de productos
4. **`interactions`** - Customer journey (27 endpoints)
5. **`offers`** - Ofertas comerciales
6. **`campaigns`** - Campañas comerciales

### Estructura Backend

```
backend/
├── backend/          # Configuración Django
├── users/           # Sistema de usuarios base
├── entities/        # ✅ Personas y organizaciones
├── world/          # ✅ Datos de referencia global
├── products/       # ✅ Catálogo de productos
├── interactions/   # ✅ Customer journey completo
├── offers/         # ✅ Sistema de ofertas
└── campaigns/      # ✅ Campañas comerciales
```

## 🔐 Autenticación

### Sistema JWT Implementado

- **Composable**: `useAuth.ts`
- **Middleware**: `auth.ts`
- **Cookies**: Seguras por ambiente
- **Login**: Página funcional en `/login`

### Endpoints Auth

```bash
POST /api/auth/login/
POST /api/auth/logout/
GET /api/auth/user/
```

## 🛠️ Convenciones de Desarrollo

### Naming Conventions

- **Modelos**: PascalCase (`Person`, `Organization`)
- **Campos**: snake_case (`created_at`, `is_active`)
- **Endpoints**: kebab-case (`/customer-journey/`)
- **Archivos**: snake_case (`user_service.ts`)

### Estructura API

```
/api/entities/          # Entidades base
/api/world/            # Datos globales
/api/products/         # Productos
/api/interactions/     # Customer journey
/api/offers/           # Ofertas
/api/campaigns/        # Campañas
```

## 📊 Características CRM

### Entidades Core

- **Person**: Personas físicas con perfilado semántico
- **Organization**: Empresas con clasificación industrial
- **ContactDetail**: Sistema unificado de contactos
- **IndividualProfile**: Extensión semántica personal

### Customer Journey

- **8 modelos**: Medium, Channel, Action, Agent, Session, Touchpoint, Interaction
- **27 endpoints**: Analytics completos de customer journey
- **Analytics**: Dashboard empresarial de interacciones

### Productos y Ofertas

- **ProductCategory**: Categorización semántica
- **Product**: Catálogo con modalidades
- **ProductOffering**: Ofertas con segmentación
- **Campaign**: Campañas con targeting semántico

## 🚀 Comandos Frecuentes

### Docker

```bash
docker-compose up -d              # Iniciar
docker-compose down               # Detener
docker-compose logs -f backend    # Ver logs
```

### Frontend

```bash
cd frontend
npm install                       # Instalar deps
npm run dev                       # Desarrollo
npm run build                     # Build
```

### Django

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell
```

## 📚 Documentación Específica

Para detalles específicos de cada aplicación, consultar:

- **Entities**: `docs/copilot/COPILOT_ENTITIES.md`
- **Interactions**: `docs/copilot/COPILOT_INTERACTIONS.md`
- **Products**: `docs/copilot/COPILOT_PRODUCTS.md`
- **World**: `docs/copilot/COPILOT_WORLD.md`
- **Offers**: `docs/copilot/COPILOT_OFFERS.md`
- **Campaigns**: `docs/copilot/COPILOT_CAMPAIGNS.md`

## 🎯 Desarrollo Diario

### Flujo Típico

1. `docker-compose up -d` (iniciar backend)
2. `cd frontend && npm run dev` (iniciar frontend)
3. Desarrollar con hot-reload activo
4. Usar VS Code tasks para comandos comunes

### Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests (cuando estén configurados)
cd frontend && npm run test
```

---

**RECORDATORIO**: Siempre usar Docker para backend. El frontend es la única excepción que corre localmente.
