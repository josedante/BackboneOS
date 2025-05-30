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
│   └── users/                 # App de usuarios (no myapp)
│       ├── models.py          # ExampleModel implementado
│       ├── views.py
│       ├── urls.py
│       └── serializers.py
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
- **Aplicación**: `users` (no `myapp`) con `ExampleModel`

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

1. **Backend**: Crear en app `users` (no `myapp`)
2. **Frontend**: Usar composables existentes (`useAuth`)
3. **API**: Extender servicios en `src/services/`
4. **Autenticación**: Ya implementada y funcional

### Para debugging:

1. **Backend**: Logs en Docker `docker-compose logs backend`
2. **Frontend**: DevTools en http://localhost:3000
3. **Database**: Acceso directo via docker-compose

## Estado del Proyecto

### ✅ Completado

- Arquitectura Django + Nuxt.js
- Sistema de autenticación completo
- Servicios API estructurados
- Configuración por ambientes
- Containerización híbrida
- Componentes base de usuario
- Configuración de seguridad

### ⏳ En Desarrollo

- Funcionalidades completas de CRUD
- Testing automatizado
- Deployment en producción
- Optimización de performance

## Consideraciones Importantes

1. **El frontend NO está en Docker** - ejecutar localmente
2. **App principal**: `users` (no `myapp`)
3. **Autenticación**: Sistema completo ya implementado
4. **Configuración**: Via python-decouple y runtime config
5. **CORS**: Configurado para desarrollo local

Esta configuración permite desarrollo eficiente con hot-reload del frontend y servicios backend estables en Docker.
