# Django + Vue.js + PostgreSQL Application

Este proyecto es una aplicación full-stack construida con:

- **Backend**: Django + Django REST Framework
- **Frontend**: Vue.js 3 + TypeScript + Vite
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker + Docker Compose

## Estructura del Proyecto

```
proyecto-opensource/
├── backend/                 # Backend Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── myproject/          # Configuración principal
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── myapp/              # Aplicación Django
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── serializers.py
├── frontend/               # Frontend Vue.js
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── src/
│       ├── App.vue
│       ├── components/
│       ├── services/       # Servicios API
│       └── views/
├── docker-compose.yml      # Configuración Docker
├── .env                    # Variables de entorno
└── README.md
```

## Requisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local del frontend)
- Python 3.9+ (para desarrollo local del backend)

## Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

1. Clona el repositorio:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Proyecto-OpenSource
   ```

2. Crea el archivo `.env` en la raíz del proyecto:

   ```bash
   cp .env.example .env
   ```

3. Levanta todos los servicios:

   ```bash
   docker-compose up --build
   ```

4. Accede a las aplicaciones:
   - **Frontend Vue.js**: http://localhost:5173
   - **Backend Django**: http://localhost:8000
   - **Admin Django**: http://localhost:8000/admin

### Opción 2: Desarrollo Local

#### Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend (Vue.js)

```bash
cd frontend
npm install
npm run dev
```

## Pasos para Comenzar

### 1. Iniciar Docker

Asegúrate de que Docker Desktop esté ejecutándose en tu Mac.

### 2. Inicio Rápido

```bash
# Hacer ejecutable el script de inicio
chmod +x start.sh

# Ejecutar el script de inicio
./start.sh
```

### 3. Inicio Manual

Si prefieres hacerlo paso a paso:

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Construir y ejecutar contenedores
docker-compose up --build -d

# 3. Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# 4. Crear superusuario (opcional)
docker-compose exec backend python manage.py createsuperuser
```

### 4. Verificar que Todo Funciona

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

## Tecnologías Utilizadas

- **Backend**: Django 4.x, Django REST Framework, PostgreSQL
- **Frontend**: Vue.js 3, TypeScript, Vite, Axios
- **Containerización**: Docker, Docker Compose
- **Herramientas**: ESLint, Prettier, Vitest

## Estructura de la API

El backend Django expone una API REST en `/api/` que incluye:

- `GET /api/users/` - Lista de usuarios
- `GET /api/users/{id}/` - Detalle de usuario
- `POST /api/users/` - Crear usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `DELETE /api/users/{id}/` - Eliminar usuario
- `POST /api/auth/login/` - Autenticación

## Desarrollo

### Comandos Útiles

#### Docker

```bash
# Reconstruir servicios
docker-compose up --build

# Ver logs
docker-compose logs -f

# Ejecutar comandos en contenedores
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Detener servicios
docker-compose down
```

#### Frontend

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build

# Ejecutar tests
npm run test:unit

# Linting
npm run lint
```

#### Backend

```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test

# Shell de Django
python manage.py shell
```
