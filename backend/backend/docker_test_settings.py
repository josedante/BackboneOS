"""
Docker-specific test settings for BackboneOS project.

This module contains Django settings specifically configured for testing
within the Docker Compose environment. It extends the base settings with
Docker-specific configurations for:
- PostgreSQL database connection within Docker network
- Redis connection within Docker network
- Docker-specific service discovery
- Test-specific environment variables
"""

import os
import sys
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add the project root to Python path
sys.path.insert(0, str(BASE_DIR))

# Import base settings
from .settings import *

# =============================================================================
# DOCKER-SPECIFIC TEST CONFIGURATION
# =============================================================================

# Override DEBUG for tests
DEBUG = True

# Allow testserver for Django test client
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='testserver,localhost,127.0.0.1,test-backend,test-runner').split(',')

# Disable migrations for faster test execution
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# =============================================================================
# DATABASE CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use PostgreSQL within Docker network for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='test_mydatabase'),
        'USER': config('POSTGRES_USER', default='myuser'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='mypassword'),
        'HOST': config('POSTGRES_HOST', default='db'),  # Docker service name
        'PORT': config('POSTGRES_PORT', default='5432'),
        'TEST': {
            'NAME': 'test_mydatabase',
        },
        'OPTIONS': {
        },
    }
}

# =============================================================================
# REDIS CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use Redis within Docker network for testing
REDIS_URL = config('REDIS_URL', default='redis://redis:6379/1')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Cache configuration for Docker
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {"max_connections": 50},
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': "backend_test_cache",
        'TIMEOUT': 300,
    }
}

# =============================================================================
# SESSION CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use Redis for sessions in Docker testing
# DB-backed sessions in tests so Client.login works without a live Redis cache.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False

# =============================================================================
# CELERY CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use synchronous execution for Celery tasks in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# EMAIL CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING CONFIGURATION FOR DOCKER TESTING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'docker': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'docker',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/test.log',  # Docker volume mount
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'backend': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# SECURITY CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Disable security features for testing
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# =============================================================================
# PASSWORD VALIDATION FOR DOCKER TESTING
# =============================================================================

# Use minimal password validation for testing
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 1,
        }
    },
]

# =============================================================================
# REST FRAMEWORK CONFIGURATION FOR DOCKER TESTING
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow all for testing
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# =============================================================================
# JWT CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Shorter token lifetimes for testing
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=10),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# =============================================================================
# CORS CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Allow all origins for testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# STATIC FILES CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use static files finder for testing (Django 5 STORAGES overrides base Whitenoise manifest)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STORAGES = {
    **STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# =============================================================================
# MEDIA FILES CONFIGURATION FOR DOCKER TESTING
# =============================================================================

# Use temporary file storage for testing
MEDIA_ROOT = '/app/test_media'  # Docker volume mount
MEDIA_URL = '/test_media/'

# =============================================================================
# DOCKER-SPECIFIC SETTINGS
# =============================================================================

# Disable Sentry for testing
SENTRY_DSN = None

# Disable user activity logging for testing
LOG_USER_ACTIVITY = False

# Test-specific timezone
TIME_ZONE = 'UTC'

# =============================================================================
# PASSWORD HASHERS FOR DOCKER TESTING
# =============================================================================

# Use fast password hashers for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# =============================================================================
# TEST DATA CONFIGURATION FOR DOCKER
# =============================================================================

# Fixtures directory for test data
FIXTURE_DIRS = [
    '/app/fixtures',  # Docker volume mount
]

# =============================================================================
# PERFORMANCE TESTING CONFIGURATION FOR DOCKER
# =============================================================================

# Disable query logging for performance tests
if 'test' in sys.argv and '--performance' in sys.argv:
    LOGGING['loggers']['django.db.backends']['level'] = 'ERROR'

# =============================================================================
# COVERAGE CONFIGURATION FOR DOCKER
# =============================================================================

# Coverage settings
COVERAGE_MODULE_EXCLUDES = [
    'tests$',
    'settings$',
    '__pycache__',
    'migrations',
    'venv',
    'env',
    'manage.py',
    'celery.py',
    'wsgi.py',
    'asgi.py',
]

# =============================================================================
# MOCK EXTERNAL SERVICES FOR DOCKER TESTING
# =============================================================================

# Mock external API calls
MOCK_EXTERNAL_APIS = True

# =============================================================================
# DOCKER NETWORK CONFIGURATION
# =============================================================================

# Docker service discovery
DOCKER_SERVICES = {
    'database': 'db',
    'redis': 'redis',
    'backend': 'backend',
    'frontend': 'frontend',
    'celery': 'celery',
    'celery_beat': 'celery-beat',
    'flower': 'flower',
}

# =============================================================================
# TESTING UTILITIES FOR DOCKER
# =============================================================================

# Test-specific middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Remove CORS middleware for testing
if 'corsheaders.middleware.CorsMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('corsheaders.middleware.CorsMiddleware')

# =============================================================================
# DOCKER HEALTH CHECK CONFIGURATION
# =============================================================================

# Health check endpoints for Docker
HEALTH_CHECK_ENDPOINTS = {
    'database': '/health/db/',
    'redis': '/health/redis/',
    'celery': '/health/celery/',
}

# =============================================================================
# ENVIRONMENT VARIABLES FOR DOCKER TESTING
# =============================================================================

# Override environment variables for Docker testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.docker_test_settings')
os.environ.setdefault('TESTING', 'True')
os.environ.setdefault('DOCKER_ENV', 'True')

# =============================================================================
# FINAL CONFIGURATION
# =============================================================================

# Ensure all Docker-specific settings are applied
print("Docker test settings loaded successfully!")
print(f"Database: {DATABASES['default']['ENGINE']} on {DATABASES['default']['HOST']}")
print(f"Redis: {REDIS_URL}")
print(f"Celery: {'Eager' if CELERY_TASK_ALWAYS_EAGER else 'Async'}")
print(f"Debug: {DEBUG}")
print(f"Logging: {LOGGING['root']['level']}")
print(f"Docker Services: {list(DOCKER_SERVICES.keys())}")
