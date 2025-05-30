# Síntesis del Proyecto: Django + Nuxt.js + PostgreSQL

## Descripción General

Esta es una aplicación full-stack moderna que combina:

- **Backend**: Django + Django REST Framework
- **Frontend**: Nuxt.js 3 + TypeScript (configuración desde cero)
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
├── frontend/                  # Frontend Nuxt.js (nueva configuración)
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
- **Autenticación**: Both JWT and Token-based authentication are supported
- **CORS**: django-cors-headers para comunicación frontend-backend

### Frontend (Nuevo Nuxt.js)

- **Framework**: Nuxt.js 3.13.0
- **Lenguaje**: TypeScript 5.6.3
- **UI Framework**: Nuxt UI 2.18.4
- **Estado**: Pinia 2.2.4 con @pinia/nuxt
- **Routing**: Auto-routing de Nuxt
- **HTTP Client**: $fetch nativo de Nuxt
- **Linting**: ESLint 9.12.0
- **SSR/SPA**: Configuración híbrida

### DevOps

- **Containerización**: Docker + Docker Compose
- **Proxy**: Nitro dev proxy para desarrollo
- **Variables de Entorno**: Runtime config de Nuxt

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

- **Composables**: `useApi` para llamadas a la API
- **Cliente API**: `$fetch` con configuración base
- **Componentes**: Sistema de componentes Vue 3
- **Store**: Pinia integrado
- **Páginas**: Sistema de routing automático de Nuxt
- **SSR**: Renderizado del lado del servidor

### Configuración Docker

- **Backend Service**: Django en puerto 8000
- **Frontend Service**: Nuxt.js en puerto 3000
- **Database Service**: PostgreSQL 14

## Inicio Rápido

### Con Docker (Recomendado)

```bash
# 1. Eliminar carpeta frontend existente
rm -rf frontend

# 2. Crear nueva estructura
# (Los archivos se crearán automáticamente)

# 3. Ejecutar script de inicio
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

# 4. Instalar dependencias frontend
docker-compose exec frontend npm install
```

## URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js)
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin

## Configuración Nuxt.js

### Características Implementadas

- ✅ Configuración base de Nuxt.js 3
- ✅ TypeScript con strict mode
- ✅ Nuxt UI para componentes
- ✅ Pinia para estado global
- ✅ Composable useApi para API
- ✅ Proxy para desarrollo
- ✅ ESLint configurado
- ✅ Docker containerizado

### Próximos Pasos

- ⏳ Crear páginas principales
- ⏳ Implementar autenticación
- ⏳ Crear componentes de usuario
- ⏳ Configurar testing
- ⏳ Optimización de performance

## Comandos Útiles

### Frontend

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build de producción
- `npm run generate` - Generación estática
- `npm run lint` - Linting
- `npm run type-check` - Verificación de tipos

### Backend

- `python manage.py runserver` - Servidor de desarrollo
- `python manage.py migrate` - Migrar base de datos

Este proyecto está configurado con Nuxt.js desde cero, proporcionando una base sólida para desarrollo full-stack moderno con SSR, TypeScript y una arquitectura escalable.
