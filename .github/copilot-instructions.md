# Síntesis del Proyecto: Django + Nuxt.js + PostgreSQL

## Descripción General

Esta es una aplicación full-stack moderna que combina:

- **Backend**: Django + Django REST Framework
- **Frontend**: Nuxt.js 3 + TypeScript (migración en progreso desde Vue.js)
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker + Docker Compose

## Estructura del Proyecto

```
Proyecto-OpenSource/
├── backend/                    # Backend Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── backend/               # Configuración Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── myapp/                 # Aplicación principal
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── serializers.py
├── frontend/                  # Frontend Nuxt.js (migración desde Vue.js)
│   ├── package.json
│   ├── nuxt.config.ts         # Configuración Nuxt
│   ├── Dockerfile
│   └── src/
│       ├── app.vue            # App principal Nuxt
│       ├── components/
│       ├── composables/       # Composables Nuxt
│       ├── plugins/          # Plugins Nuxt
│       ├── middleware/       # Middleware Nuxt
│       ├── pages/            # Páginas con routing automático
│       └── services/         # Servicios API
├── docker-compose.yml        # Orquestación Docker
├── .env                      # Variables de entorno
├── start.sh                  # Script de inicio
└── README.md
```

## Tecnologías Utilizadas

### Backend

- **Framework**: Django 5.2.1
- **API**: Django REST Framework 3.16.0
- **Base de Datos**: PostgreSQL con psycopg2
- **Autenticación**: Token-based authentication
- **CORS**: django-cors-headers para comunicación frontend-backend

### Frontend (Migración a Nuxt.js)

- **Framework**: Nuxt.js 3 (migración desde Vue.js 3.5.13)
- **Lenguaje**: TypeScript 5.8.0
- **Build Tool**: Vite integrado en Nuxt
- **Estado**: Pinia 3.0.1 (compatible con Nuxt)
- **Routing**: Auto-routing de Nuxt (migración desde Vue Router)
- **HTTP Client**: $fetch nativo de Nuxt + Axios 1.9.0
- **Testing**: Vitest + Playwright
- **Linting**: ESLint + Prettier
- **SSR/SPA**: Configuración híbrida con Nuxt

### DevOps

- **Containerización**: Docker + Docker Compose
- **Proxy**: Configuración CORS para desarrollo
- **Variables de Entorno**: python-decouple

## Características Principales

### API REST

El backend expone endpoints para:

- `GET /api/users/` - Lista de usuarios
- `GET /api/users/{id}/` - Detalle de usuario
- `POST /api/users/` - Crear usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `DELETE /api/users/{id}/` - Eliminar usuario
- `POST /api/auth/login/` - Autenticación

### Frontend Modular (Nuxt.js)

- **Composables**: `useUser` y `useAuth` (migración desde services)
- **Cliente API**: `$fetch` con interceptores para autenticación
- **Componentes**: `UserList` para mostrar usuarios
- **Store**: `useCounterStore` con Pinia
- **Páginas**: Sistema de routing automático de Nuxt
- **SSR**: Renderizado del lado del servidor opcional

### Configuración Docker

- **Backend Service**: Django en puerto 8000
- **Frontend Service**: Nuxt.js en puerto 3000 (cambio desde 5173)
- **Database Service**: PostgreSQL 14

## Inicio Rápido

### Con Docker (Recomendado)

```bash
# Ejecutar script de inicio
chmod +x start.sh
./start.sh
```

### Manual

```bash
# 1. Configurar variables
cp .env.example .env

# 2. Levantar servicios
docker-compose up --build -d

# 3. Migrar base de datos
docker-compose exec backend python manage.py migrate

# 4. Crear superusuario (opcional)
docker-compose exec backend python manage.py createsuperuser
```

## URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js)
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin

## Migración Vue.js → Nuxt.js

### Estado de Migración

- ✅ Configuración base de Nuxt.js
- ✅ Migración de componentes principales
- 🔄 Migración de servicios a composables
- 🔄 Configuración de SSR/SPA
- ⏳ Optimización de performance
- ⏳ Testing con Nuxt

### Cambios Principales

- **Routing**: De Vue Router a auto-routing de Nuxt
- **Estado**: Pinia integrado con Nuxt
- **API**: De Axios a $fetch nativo
- **Build**: Vite integrado en Nuxt
- **Estructura**: Carpeta `pages/` para routing automático

## Comandos Útiles

Ver COMMANDS.md para comandos de desarrollo, Docker y solución de problemas.

## Scripts de Desarrollo

- start.sh: Script automatizado de inicio
- **Frontend**: `npm run dev`, `npm run build`, `npm run generate`
- **Backend**: `python manage.py runserver`, `python manage.py migrate`

Este proyecto está configurado para desarrollo con hot-reload tanto en frontend como backend, y usa Docker para un entorno consistente entre desarrolladores. La migración a Nuxt.js mejora el SEO, performance y experiencia de desarrollo.
