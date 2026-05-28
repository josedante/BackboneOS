#!/bin/bash

# BackboneOS development environment setup (Docker Compose — backend only)
# Operator CRM is Django templates at http://localhost:8000/

set -e

echo "Configuring BackboneOS development environment..."
echo

if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "Dependencies verified"
echo

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ".env created"
else
    echo ".env already exists"
fi

echo
echo "Starting Docker services..."

docker-compose up -d --build

echo "Waiting for the database..."
sleep 5

echo "Running migrations..."
docker-compose exec backend python manage.py migrate

echo
echo "Environment ready."
echo
echo "URLs:"
echo "   - CRM dashboard: http://localhost:8000/ (login at /login/)"
echo "   - Django Admin:  http://localhost:8000/admin/"
echo "   - REST API:      http://localhost:8000/api/"
echo
echo "Useful commands:"
echo "   - Logs:       docker-compose logs -f backend"
echo "   - Shell:      docker-compose exec backend python manage.py shell"
echo "   - Superuser:  docker-compose exec backend python manage.py createsuperuser"
echo "   - Tailwind:   cd backend && npm run tailwind:build"
echo "   - Stop:       docker-compose down"
echo
echo "Run Django management commands with: docker-compose exec backend python manage.py ..."
