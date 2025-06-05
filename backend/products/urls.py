from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ModalityViewSet, 
    CustomizationViewSet, ProductViewSet
)
from .analytics import (
    product_analytics_dashboard, category_analytics,
    market_segmentation_analytics, pricing_analytics,
    growth_analytics, product_recommendations
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet)
router.register(r'modalities', ModalityViewSet)
router.register(r'customizations', CustomizationViewSet)
router.register(r'products', ProductViewSet)

app_name = 'products'

urlpatterns = [
    # API endpoints principales
    path('', include(router.urls)),
    
    # Analytics endpoints
    path('analytics/dashboard/', product_analytics_dashboard, name='analytics-dashboard'),
    path('analytics/categories/', category_analytics, name='analytics-categories'),
    path('analytics/market-segmentation/', market_segmentation_analytics, name='analytics-market'),
    path('analytics/pricing/', pricing_analytics, name='analytics-pricing'),
    path('analytics/growth/', growth_analytics, name='analytics-growth'),
    path('analytics/recommendations/', product_recommendations, name='analytics-recommendations'),
]
