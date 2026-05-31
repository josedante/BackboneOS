import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,192.168.97.4,192.168.107.4,backend.proyecto-opensource.orb.local',
).split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_redis',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'core',
    'users',
    'world',
    'websites',
    'products',
    'entities',
    'interactions',
    'our_institution',
    'offers',
    'campaigns',
    'connectors',
    'dashboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_database_url = config('DATABASE_URL', default=None)

if _database_url:
    from urllib.parse import urlparse
    _db = urlparse(_database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _db.path[1:],
            'USER': _db.username,
            'PASSWORD': _db.password,
            'HOST': _db.hostname,
            'PORT': _db.port,
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME', default='mydatabase'),
            'USER': config('DATABASE_USER', default='myuser'),
            'PASSWORD': config('DATABASE_PASSWORD', default='mypassword'),
            'HOST': config('DATABASE_HOST', default='db'),
            'PORT': config('DATABASE_PORT', default='5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Session auth (HTML dashboard)
# ---------------------------------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ---------------------------------------------------------------------------
# Auth cookies
# ---------------------------------------------------------------------------
COOKIE_SAMESITE = config('COOKIE_SAMESITE', default='None' if DEBUG else 'Lax')
COOKIE_SECURE = config('COOKIE_SECURE', default=True, cast=bool)

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CookieJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny' if DEBUG else 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ---------------------------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------------------------
_cors_origins_raw = config('CORS_ALLOWED_ORIGINS', default=None)
CORS_ALLOWED_ORIGINS = (
    [o.strip() for o in _cors_origins_raw.split(',') if o.strip()]
    if _cors_origins_raw
    else []
)
CORS_ALLOW_CREDENTIALS = True

_csrf_default = 'https://backend.proyecto-opensource.orb.local' if DEBUG else ''
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in config('CSRF_TRUSTED_ORIGINS', default=_csrf_default).split(',')
    if o.strip()
]

# ---------------------------------------------------------------------------
# Redis / Cache / Sessions
# ---------------------------------------------------------------------------
_redis_url = config('REDIS_URL', default=None)
_redis_location = _redis_url if _redis_url else config('DJANGO_REDIS_URL', default='redis://127.0.0.1:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': _redis_location,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'backend_cache',
        'TIMEOUT': 300,
    }
}

if config('USE_REDIS_SESSIONS', default=True, cast=bool):
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    SESSION_COOKIE_AGE = 86400
    SESSION_SAVE_EVERY_REQUEST = False
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

WEB_SESSION_DURATION_SECONDS = config('WEB_SESSION_DURATION_SECONDS', default=1800, cast=int)

FAILED_EVENT_RETRY_CONFIG = {
    'default': 5,
    'web': 5,
    'email': 10,
    'whatsapp': 8,
    'sms': 8,
    'payment': 20,
    'api': 3,
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
if _redis_url:
    CELERY_BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = _redis_url
else:
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
    CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/2')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE_FILENAME = '/tmp/celerybeat-schedule'
CELERY_BEAT_MAX_LOOP_INTERVAL = 5

CELERY_BEAT_SCHEDULE = {
    'retry-failed-events': {
        'task': 'connectors.retry_failed_events',
        'schedule': 300.0,
        'options': {'expires': 60.0},
    },
}

CELERY_RESULT_EXPIRES = config('CELERY_RESULT_EXPIRES', default=3600, cast=int)

CELERY_TASK_ROUTES = {
    'users.*': {'queue': 'users'},
    'products.*': {'queue': 'products'},
    'entities.*': {'queue': 'entities'},
    'interactions.*': {'queue': 'interactions'},
    'campaigns.*': {'queue': 'campaigns'},
    'offers.*': {'queue': 'offers'},
}

CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

LOG_USER_ACTIVITY = config('LOG_USER_ACTIVITY', default=False, cast=bool)
