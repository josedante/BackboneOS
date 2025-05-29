#!/bin/bash

# Script de inicio para el proyecto Django + Vue.js + PostgreSQL

echo "🚀 Iniciando proyecto Django + Vue.js + PostgreSQL..."

# Verificar si Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop."
    exit 1
fi

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
fi

echo "🐳 Construyendo y ejecutando contenedores..."
docker-compose down
docker-compose up --build -d

echo "⏳ Esperando a que los servicios se inicien..."
sleep 10

echo "🔄 Ejecutando migraciones de Django..."
docker-compose exec backend python manage.py migrate

echo "👤 Creando superusuario de Django (opcional)..."
echo "Si deseas crear un superusuario, ejecuta:"
echo "docker-compose exec backend python manage.py createsuperuser"

echo ""
echo "✅ ¡Aplicación lista!"
echo ""
echo "🌐 Servicios disponibles:"
echo "  - Frontend (Vue.js): http://localhost:5173"
echo "  - Backend (Django): http://localhost:8000"
echo "  - Admin Django: http://localhost:8000/admin"
echo ""
echo "📊 Para ver los logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 Para detener los servicios:"
echo "  docker-compose down"
