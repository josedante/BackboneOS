from rest_framework.routers import DefaultRouter
from .views import (
    OurOrganizationViewSet,
    SeatViewSet,
    UnitViewSet,
    PositionViewSet,
    TeamViewSet,
)

router = DefaultRouter()
router.register(r'organization', OurOrganizationViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'units', UnitViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'teams', TeamViewSet)

urlpatterns = router.urls
