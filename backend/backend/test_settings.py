"""
Test settings for BackboneOS project.

This module contains Django settings specifically configured for testing.
It extends the base settings with test-specific configurations for:
- In-memory SQLite database for fast test execution
- Disabled migrations for faster test setup
- Mock external services
- Test-specific logging configuration
- Simplified authentication for testing
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
# TEST-SPECIFIC CONFIGURATION
# =============================================================================

# Override DEBUG for tests
DEBUG = True

# Add testserver to ALLOWED_HOSTS for testing
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Disable migrations for faster test execution
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# =============================================================================
# DATABASE CONFIGURATION FOR TESTING
# =============================================================================

# Use in-memory SQLite for fast test execution
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# =============================================================================
# CACHE CONFIGURATION FOR TESTING
# =============================================================================

# Use dummy cache for testing (no actual caching)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# =============================================================================
# SESSION CONFIGURATION FOR TESTING
# =============================================================================

# Use database sessions for testing
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# CELERY CONFIGURATION FOR TESTING
# =============================================================================

# Use synchronous execution for Celery tasks in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# =============================================================================
# EMAIL CONFIGURATION FOR TESTING
# =============================================================================

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING CONFIGURATION FOR TESTING
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
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'test.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
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
    },
}

# =============================================================================
# SECURITY CONFIGURATION FOR TESTING
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
# PASSWORD VALIDATION FOR TESTING
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
# REST FRAMEWORK CONFIGURATION FOR TESTING
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
# JWT CONFIGURATION FOR TESTING
# =============================================================================

# Shorter token lifetimes for testing
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=10),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# =============================================================================
# CORS CONFIGURATION FOR TESTING
# =============================================================================

# Allow all origins for testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# STATIC FILES CONFIGURATION FOR TESTING
# =============================================================================

# Use static files finder for testing
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# MEDIA FILES CONFIGURATION FOR TESTING
# =============================================================================

# Use temporary file storage for testing
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/test_media/'

# =============================================================================
# TEST-SPECIFIC SETTINGS
# =============================================================================

# Disable Sentry for testing
SENTRY_DSN = None

# Disable user activity logging for testing
LOG_USER_ACTIVITY = False

# Test-specific timezone
TIME_ZONE = 'UTC'

# =============================================================================
# PASSWORD HASHERS FOR TESTING
# =============================================================================

# Use fast password hashers for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# =============================================================================
# TEST DATA CONFIGURATION
# =============================================================================

# Fixtures directory for test data
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]

# =============================================================================
# PERFORMANCE TESTING CONFIGURATION
# =============================================================================

# Disable query logging for performance tests
if 'test' in sys.argv and '--performance' in sys.argv:
    LOGGING['loggers']['django.db.backends']['level'] = 'ERROR'

# =============================================================================
# COVERAGE CONFIGURATION
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
# MOCK EXTERNAL SERVICES
# =============================================================================

# Mock external API calls
MOCK_EXTERNAL_APIS = True

# Mock Redis for testing
USE_REDIS_SESSIONS = False

# =============================================================================
# TEST DATABASE ROUTERS
# =============================================================================

# Use default database router for testing
DATABASE_ROUTERS = []

# =============================================================================
# TESTING UTILITIES
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
# TESTING APPS
# =============================================================================

# Add testing-specific apps
# INSTALLED_APPS += [
#     'django_nose',  # Alternative test runner
# ]

# =============================================================================
# TESTING COMMANDS
# =============================================================================

# Custom test management command settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# =============================================================================
# ENVIRONMENT VARIABLES FOR TESTING
# =============================================================================

# Override environment variables for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.test_settings')
os.environ.setdefault('TESTING', 'True')

# =============================================================================
# FINAL CONFIGURATION
# =============================================================================

# Ensure all test-specific settings are applied
print("Test settings loaded successfully!")
print(f"Database: {DATABASES['default']['ENGINE']}")
print(f"Cache: {CACHES['default']['BACKEND']}")
print(f"Celery: {'Eager' if CELERY_TASK_ALWAYS_EAGER else 'Async'}")
print(f"Debug: {DEBUG}")
print(f"Logging: {LOGGING['root']['level']}")
