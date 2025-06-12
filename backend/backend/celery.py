import os
from celery import Celery

# Establece el settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Crea la instancia de la app de Celery
app = Celery('backend')

# Carga la configuración desde Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubre tareas en todas las apps instaladas
app.autodiscover_tasks()
