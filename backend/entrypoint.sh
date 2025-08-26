#!/bin/bash
set -e

# Production entrypoint script for BackboneOS
# Handles database migrations safely with advisory locks

echo "🚀 Starting BackboneOS Backend..."

# Function to run migrations with advisory lock
run_migrations() {
    echo "📊 Running database migrations..."
    
    # Use Django's migrate command with advisory lock
    # This prevents multiple instances from migrating simultaneously
    python manage.py migrate --noinput
    
    echo "✅ Database migrations completed"
}

# Function to collect static files
collect_static() {
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
    echo "✅ Static files collected"
}

# Function to start the application
start_app() {
    echo "🌐 Starting application server..."
    
    # Get the command from arguments or use default
    if [ $# -eq 0 ]; then
        # Default Gunicorn command
        exec gunicorn \
            --bind 0.0.0.0:$PORT \
            --workers 2 \
            --timeout 30 \
            --graceful-timeout 30 \
            --keep-alive 2 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            backend.wsgi:application
    else
        # Execute the provided command (for Celery workers, etc.)
        exec "$@"
    fi
}

# Main execution flow
main() {
    # Wait a bit for database to be ready
    echo "⏳ Waiting for database to be ready..."
    sleep 2
    
    # Run migrations first
    run_migrations
    
    # Collect static files (only for web services)
    if [[ "$1" == *"gunicorn"* ]] || [ $# -eq 0 ]; then
        collect_static
    fi
    
    # Start the application
    start_app "$@"
}

# Run main function with all arguments
main "$@"
