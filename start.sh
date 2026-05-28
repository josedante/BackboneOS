#!/bin/bash

# Start BackboneOS (Django backend + PostgreSQL + Redis)

echo "Starting BackboneOS..."

if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Building and starting containers..."
docker-compose down
docker-compose up --build -d

echo "Waiting for services..."
sleep 10

echo "Running migrations..."
docker-compose exec backend python manage.py migrate

echo ""
echo "Application ready."
echo ""
echo "Services:"
echo "  - CRM (Django):  http://localhost:8000/"
echo "  - Django Admin:  http://localhost:8000/admin/"
echo "  - REST API:      http://localhost:8000/api/"
echo ""
echo "Logs:  docker-compose logs -f"
echo "Stop:  docker-compose down"
