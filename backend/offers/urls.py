from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductOfferingViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'offerings', ProductOfferingViewSet, basename='productoffering')

app_name = 'offers'

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints disponibles:
# GET/POST     /api/offers/offerings/                    # CRUD completo
# GET/PUT/DEL  /api/offers/offerings/{id}/               # Detalle y operaciones
# GET          /api/offers/offerings/choices/            # Choices para formularios
# GET          /api/offers/offerings/currently_valid/    # Ofertas válidas actualmente
# GET          /api/offers/offerings/by_product/         # Ofertas por producto
# GET          /api/offers/offerings/by_channel/         # Ofertas por canal
# GET          /api/offers/offerings/analytics/          # Analytics completo
# POST         /api/offers/offerings/{id}/duplicate/     # Duplicar oferta
# POST         /api/offers/offerings/bulk_create/        # Creación en lote
# GET          /api/offers/offerings/export/             # Exportación de datos
