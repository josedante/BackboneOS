from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .selectors import (
    get_category_analytics,
    get_division_analytics_dashboard,
    get_growth_analytics,
    get_market_segmentation_analytics,
    get_pricing_analytics,
    get_product_analytics_dashboard,
    get_product_recommendations,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def division_analytics_dashboard(request):
    """Dashboard de analytics por división"""
    return Response(get_division_analytics_dashboard())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_analytics_dashboard(request):
    """Dashboard principal de analytics de productos"""
    return Response(get_product_analytics_dashboard())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_analytics(request):
    """Analytics por categorías"""
    return Response(get_category_analytics())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def market_segmentation_analytics(request):
    """Analytics de segmentación de mercado"""
    return Response(get_market_segmentation_analytics())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pricing_analytics(request):
    """Analytics de pricing"""
    return Response(get_pricing_analytics())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def growth_analytics(request):
    """Analytics de crecimiento temporal"""
    return Response(get_growth_analytics())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_recommendations(request):
    """Recomendaciones basadas en análisis de datos"""
    return Response(get_product_recommendations())
