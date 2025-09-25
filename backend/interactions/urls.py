"""
URLs para la aplicación interactions.

Esta aplicación maneja todas las interacciones del CRM, incluyendo canales,
medios, tipos de acción, acciones, agentes e interacciones.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para las APIs REST
router = DefaultRouter()

# Registrar ViewSets para cada modelo
router.register(r'mediums', views.MediumViewSet, basename='medium')
router.register(r'channels', views.ChannelViewSet, basename='channel')
router.register(r'action-types', views.ActionTypeViewSet, basename='actiontype')
router.register(r'actions', views.ActionViewSet, basename='action')
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'touchpoint-types', views.TouchpointTypeViewSet, basename='touchpointtype')
router.register(r'touchpoints', views.TouchpointViewSet, basename='touchpoint')
router.register(r'interactions', views.InteractionViewSet, basename='interaction')

urlpatterns = [
    # API endpoints principales
    path('', include(router.urls)),
]
