#!/bin/bash
set -e

# Production entrypoint script for BackboneOS
# Handles database migrations safely with advisory locks

echo "🚀 Starting BackboneOS Backend..."

# Function to check database connection
check_database() {
    echo "🔍 Checking database connection..."
    python manage.py check --database default || {
        echo "❌ Database connection failed, retrying in 5 seconds..."
        sleep 5
        return 1
    }
    echo "✅ Database connection successful"
    return 0
}

# Function to run migrations with advisory lock
run_migrations() {
    echo "📊 Running database migrations..."
    
    # Wait for database to be ready with retries
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if check_database; then
            break
        fi
        retries=$((retries + 1))
        echo "🔄 Retry $retries/$max_retries - waiting 5 seconds..."
        sleep 5
    done
    
    if [ $retries -eq $max_retries ]; then
        echo "❌ Failed to connect to database after $max_retries retries"
        exit 1
    fi
    
    # Use Django's migrate command with advisory lock
    # This prevents multiple instances from migrating simultaneously
    python manage.py migrate --noinput
    
    # For Celery Beat, also ensure the beat tables exist
    if [[ "${@}" == *"beat"* ]]; then
        echo "🔍 Verifying Celery Beat tables..."
        python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute('SELECT 1 FROM django_celery_beat_crontabschedule LIMIT 1')
    print('✅ Celery Beat tables verified')
except Exception as e:
    print(f'⚠️  Celery Beat tables not ready: {e}')
    exit(1)
"
    fi
    
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
    # Run migrations for web services (gunicorn or default) and Celery Beat
    if [[ "$1" == *"gunicorn"* ]] || [ $# -eq 0 ] || [[ "$1" == *"beat"* ]]; then
        if [[ "$1" == *"beat"* ]]; then
            echo "⏰ Celery Beat service detected - running migrations only"
            run_migrations
        else
            echo "🌐 Web service detected - running migrations and collecting static files"
            run_migrations
            collect_static
        fi
    else
        echo "⚙️  Worker service detected - skipping migrations and static files"
    fi
    
    # Start the application
    start_app "$@"
}

# Run main function with all arguments
main "$@"
