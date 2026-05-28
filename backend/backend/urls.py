"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static

from users.views import UserViewSet

@csrf_exempt
def health_check(request):
    """Health check endpoint for Render deployment"""
    from django.db import connection
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    health_status = {
        'status': 'healthy',
        'service': 'backboneos-backend',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check migration status
    try:
        # Capture output from showmigrations command
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        call_command('showmigrations', '--plan', verbosity=0)
        migration_output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check if there are unapplied migrations
        unapplied_migrations = '[ ]' in migration_output
        if unapplied_migrations:
            health_status['checks']['migrations'] = 'unhealthy: pending migrations'
            health_status['status'] = 'unhealthy'
        else:
            health_status['checks']['migrations'] = 'healthy: all migrations applied'
    except Exception as e:
        health_status['checks']['migrations'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    return JsonResponse(health_status)

@csrf_exempt
def api_root_view(request):
    """API catalog endpoint (relocated from /)."""
    return JsonResponse({
        'message': 'BackboneOS API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'dashboard': '/',
                'products_ui': '/products/',
                'entities_ui': '/entities/',
                'interactions_ui': '/interactions/',
                'api': {
                'world': '/api/world/',
                'products': '/api/products/',
                'entities': '/api/entities/',
                'interactions': '/api/interactions/',
                'our-institution': '/api/our-institution/',
                'campaigns': '/api/campaigns/',
                'offers': '/api/offers/',
                'offers_ui': '/offers/',
            }
        }
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('dashboard.urls')),
    path('products/', include('products.template_urls')),
    path('entities/', include('entities.template_urls')),
    path('interactions/', include('interactions.template_urls')),
    path('campaigns/', include('campaigns.template_urls')),
    path('offers/', include('offers.template_urls')),
    path('users/', include('users.urls')),
    path('api/', api_root_view, name='api-catalog'),
    path('api/auth/', include('users.urls')),
    path('api/world/', include('world.urls')),
    path('api/products/', include('products.urls')),
    path('api/entities/', include('entities.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/our-institution/', include('our_institution.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/offers/', include('offers.urls')),
    path('api/websites/', include('websites.urls')),
    path('api/users/', UserViewSet.as_view({'get': 'list'}), name='user-list'),
]

# Serve static files in both development and production
# In production, Django will serve static files when DEBUG=False
# This is necessary for Render deployment where static files are served by Django
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)