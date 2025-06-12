#!/bin/bash

# 🐳 BackboneOS Development Environment Setup
# Este script configura el entorno de desarrollo híbrido con Docker Compose

set -e

echo "🐳 Configurando entorno de desarrollo BackboneOS..."
echo

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker Desktop."
    exit 1
fi

# Verificar que Docker Compose está disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está disponible. Por favor instala Docker Compose."
    exit 1
fi

# Verificar que Node.js está instalado para el frontend
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js para el frontend."
    exit 1
fi

echo "✅ Dependencias verificadas"
echo

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database settings (Docker)
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=db
DB_PORT=5432

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo "✅ Archivo .env creado"
else
    echo "✅ Archivo .env ya existe"
fi

echo
echo "🐳 Iniciando servicios Docker..."

# Construir e iniciar contenedores
docker-compose up -d --build

echo "⏳ Esperando que la base de datos esté lista..."
sleep 5

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
docker-compose exec backend python manage.py migrate

# Instalar dependencias del frontend
echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
cd ..

echo
echo "🎉 ¡Entorno configurado correctamente!"
echo
echo "📍 URLs disponibles:"
echo "   - Backend API: http://localhost:8000/api/"
echo "   - Django Admin: http://localhost:8000/admin"
echo "   - Frontend: http://localhost:3000 (ejecutar: cd frontend && npm run dev)"
echo
echo "🛠️  Comandos útiles:"
echo "   - Ver logs: docker-compose logs -f backend"
echo "   - Django shell: docker-compose exec backend python manage.py shell"
echo "   - Crear superuser: docker-compose exec backend python manage.py createsuperuser"
echo "   - Parar servicios: docker-compose down"
echo
echo "⚠️  RECORDATORIO: Todos los comandos Django deben ejecutarse con 'docker-compose exec backend'"
