from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Sum, Q, Case, When, Value, F, Min, Max
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.conf import settings

from .models import ProductOffering
from .serializers import (
    ProductOfferingListSerializer, ProductOfferingDetailSerializer,
    ProductOfferingCreateUpdateSerializer, ProductOfferingChoiceSerializer,
    ProductOfferingAnalyticsSerializer
)


def get_permission_classes():
    """Permisos dinámicos según ambiente"""
    if settings.DEBUG:
        return [permissions.AllowAny]
    else:
        return [permissions.IsAuthenticated]


class ProductOfferingViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de ofertas de productos"""
    queryset = ProductOffering.objects.select_related(
        'product', 'product__category', 'product__category__division'
    ).prefetch_related(
        'channels', 'seats', 'target_segments', 'related_industries',
        'related_functions', 'descriptors', 'tags'
    )
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = {
        'is_active': ['exact'],
        'currency_code': ['exact', 'in'],
        'auto_renew': ['exact'],
        'valid_from': ['gte', 'lte', 'exact'],
        'valid_until': ['gte', 'lte', 'exact'],
        'price': ['gte', 'lte', 'exact'],
        'product__category': ['exact'],
        'product__category__division': ['exact'],
        'channels': ['exact'],
        'target_segments': ['exact'],
        'related_industries': ['exact'],
    }
    
    search_fields = [
        'name', 'code', 'description', 'product__name', 'product__code',
        'product__description', 'landing_url'
    ]
    
    ordering_fields = [
        'name', 'code', 'price', 'valid_from', 'valid_until',
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Serializer contextual según acción"""
        if self.action == 'list':
            return ProductOfferingListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductOfferingCreateUpdateSerializer
        elif self.action == 'choices':
            return ProductOfferingChoiceSerializer
        else:
            return ProductOfferingDetailSerializer
    
    def get_queryset(self):
        """Queryset con filtros adicionales"""
        queryset = super().get_queryset()
        
        # Filtro por validez actual
        currently_valid = self.request.query_params.get('currently_valid')
        if currently_valid == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                Q(valid_from__isnull=True) | Q(valid_from__lte=today)
            ).filter(
                Q(valid_until__isnull=True) | Q(valid_until__gte=today)
            )
        elif currently_valid == 'false':
            today = timezone.now().date()
            queryset = queryset.filter(
                Q(valid_until__lt=today) | Q(valid_from__gt=today)
            )
        
        # Filtro por producto
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filtro por rango de precios
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Choices para formularios"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def currently_valid(self, request):
        """Ofertas actualmente válidas"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            is_active=True
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=today)
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=today)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductOfferingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductOfferingListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Ofertas agrupadas por producto"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'Se requiere el parámetro product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(product_id=product_id)
        serializer = ProductOfferingListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_channel(self, request):
        """Ofertas filtradas por canal"""
        channel_id = request.query_params.get('channel_id')
        if not channel_id:
            return Response(
                {'error': 'Se requiere el parámetro channel_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(channels=channel_id)
        serializer = ProductOfferingListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analytics completo de ofertas"""
        today = timezone.now().date()
        
        # Métricas generales
        total_offerings = self.get_queryset().count()
        active_offerings = self.get_queryset().filter(is_active=True).count()
        expired_offerings = self.get_queryset().filter(
            valid_until__lt=today
        ).count()
        future_offerings = self.get_queryset().filter(
            valid_from__gt=today
        ).count()
        
        # Distribución por moneda
        by_currency = list(
            self.get_queryset()
            .values('currency_code')
            .annotate(count=Count('id'), avg_price=Avg('price'))
            .order_by('-count')
        )
        
        # Distribución por categoría de producto
        by_product_category = list(
            self.get_queryset()
            .select_related('product__category')
            .values('product__category__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # Distribución por canal
        by_channel = list(
            self.get_queryset()
            .prefetch_related('channels')
            .values('channels__name')
            .annotate(count=Count('id'))
            .filter(channels__name__isnull=False)
            .order_by('-count')[:10]
        )
        
        # Distribución por segmento de mercado
        by_market_segment = list(
            self.get_queryset()
            .prefetch_related('target_segments')
            .values('target_segments__name')
            .annotate(count=Count('id'))
            .filter(target_segments__name__isnull=False)
            .order_by('-count')[:10]
        )
        
        # Estadísticas de precios
        price_stats = self.get_queryset().aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            total_value=Sum('price')
        )
        
        # Estadísticas de duración
        duration_stats = self.get_queryset().filter(
            duration_days__isnull=False
        ).aggregate(
            min_duration=Min('duration_days'),
            max_duration=Max('duration_days'),
            avg_duration=Avg('duration_days')
        )
        
        # Top productos más ofertados
        top_products = list(
            self.get_queryset()
            .select_related('product')
            .values('product__name')
            .annotate(offerings_count=Count('id'))
            .order_by('-offerings_count')[:10]
        )
        
        # Ofertas recientes
        recent_offerings = ProductOfferingListSerializer(
            self.get_queryset().order_by('-created_at')[:5],
            many=True
        ).data
        
        analytics_data = {
            'total_offerings': total_offerings,
            'active_offerings': active_offerings,
            'expired_offerings': expired_offerings,
            'future_offerings': future_offerings,
            'by_currency': by_currency,
            'by_product_category': by_product_category,
            'by_channel': by_channel,
            'by_market_segment': by_market_segment,
            'price_statistics': price_stats,
            'duration_statistics': duration_stats,
            'top_products': top_products,
            'recent_offerings': recent_offerings,
        }
        
        serializer = ProductOfferingAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar una oferta"""
        offering = self.get_object()
        
        # Crear copia
        new_offering = ProductOffering.objects.create(
            name=f"{offering.name} (Copia)",
            code=f"{offering.code}_copy_{int(timezone.now().timestamp())}",
            description=offering.description,
            product=offering.product,
            price=offering.price,
            currency_code=offering.currency_code,
            auto_renew=offering.auto_renew,
            duration_days=offering.duration_days,
            landing_url=offering.landing_url,
            metadata=offering.metadata,
            is_active=False  # Crear desactivada por defecto
        )
        
        # Copiar relaciones M2M
        new_offering.channels.set(offering.channels.all())
        new_offering.seats.set(offering.seats.all())
        new_offering.target_segments.set(offering.target_segments.all())
        new_offering.related_industries.set(offering.related_industries.all())
        new_offering.related_functions.set(offering.related_functions.all())
        new_offering.descriptors.set(offering.descriptors.all())
        new_offering.tags.set(offering.tags.all())
        
        serializer = ProductOfferingDetailSerializer(new_offering)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
