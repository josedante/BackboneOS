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
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static

@csrf_exempt
def health_check(request):
    """Health check endpoint for Render deployment"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'backboneos-backend',
        'timestamp': timezone.now().isoformat()
    })

@csrf_exempt
def root_view(request):
    """Root endpoint for the API"""
    return JsonResponse({
        'message': 'BackboneOS API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'api': {
                'world': '/api/world/',
                'products': '/api/products/',
                'entities': '/api/entities/',
                'interactions': '/api/interactions/',
                'our-institution': '/api/our-institution/',
                'campaigns': '/api/campaigns/',
                'offers': '/api/offers/',
            }
        }
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', root_view, name='root'),
    path('users/', include('users.urls')),
    path('api/world/', include('world.urls')),
    path('api/products/', include('products.urls')),
    path('api/entities/', include('entities.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/our-institution/', include('our_institution.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/offers/', include('offers.urls')),
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]