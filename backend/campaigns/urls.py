from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CampaignTouchpointViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'campaign-touchpoints', CampaignTouchpointViewSet, basename='campaigntouchpoint')

app_name = 'campaigns'

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints disponibles:
# GET/POST     /api/campaigns/campaigns/                           # CRUD completo de campañas
# GET/PUT/DEL  /api/campaigns/campaigns/{id}/                      # Detalle y operaciones
# GET          /api/campaigns/campaigns/choices/                   # Choices para formularios
# GET          /api/campaigns/campaigns/active_now/                # Campañas activamente activas
# GET          /api/campaigns/campaigns/scheduled/                 # Campañas programadas
# GET          /api/campaigns/campaigns/finished/                  # Campañas finalizadas
# GET          /api/campaigns/campaigns/by_division/               # Campañas por división
# GET          /api/campaigns/campaigns/by_team/                   # Campañas por equipo
# GET          /api/campaigns/campaigns/{id}/subcampaigns/         # Subcampañas de una campaña
# GET          /api/campaigns/campaigns/{id}/touchpoints/          # Touchpoints de una campaña
# POST         /api/campaigns/campaigns/{id}/duplicate/            # Duplicar campaña
# GET          /api/campaigns/campaigns/analytics/                 # Analytics completo

# GET/POST     /api/campaigns/campaign-touchpoints/                # CRUD de relaciones campaña-touchpoint
# GET/PUT/DEL  /api/campaigns/campaign-touchpoints/{id}/           # Detalle y operaciones
# GET          /api/campaigns/campaign-touchpoints/by_campaign/    # Touchpoints por campaña
# GET          /api/campaigns/campaign-touchpoints/by_touchpoint/  # Campañas por touchpoint
# GET          /api/campaigns/campaign-touchpoints/analytics/      # Analytics de relaciones