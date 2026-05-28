from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer, JSONRenderer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.conf import settings

from .models import ProductOffering
from .selectors import (
    get_offering_analytics_full,
    offerings_api_filter,
    offerings_base_queryset,
)
from .serializers import (
    ProductOfferingListSerializer, ProductOfferingDetailSerializer,
    ProductOfferingCreateUpdateSerializer, ProductOfferingChoiceSerializer,
    ProductOfferingAnalyticsSerializer
)
from .services import (
    create_offering,
    delete_offering,
    duplicate_offering,
    offering_write_payload_from_request,
    update_offering,
)


def get_permission_classes():
    """Permisos dinámicos según ambiente"""
    if settings.DEBUG:
        return [permissions.AllowAny]
    else:
        return [permissions.IsAuthenticated]


def get_analytics_permission_classes():
    """Permisos específicos para analytics - siempre requiere autenticación"""
    return [permissions.IsAuthenticated]


class _PassthroughRenderer(BaseRenderer):
    """Allow ``?format=csv|xlsx`` on custom actions without 404 from content negotiation."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class CSVExportRenderer(_PassthroughRenderer):
    media_type = 'text/csv'
    format = 'csv'


class XLSXExportRenderer(_PassthroughRenderer):
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'


class ProductOfferingViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de ofertas de productos"""
    # Prevent ``…/offerings/export/`` from matching the detail route (pk='export').
    lookup_value_regex = (
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    )
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, CSVExportRenderer, XLSXExportRenderer]
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
        """Delegate queryset shaping and API filters to selectors."""
        action = 'retrieve' if self.action == 'retrieve' else 'list'
        queryset = offerings_base_queryset(action=action)
        return offerings_api_filter(queryset, request_params=self.request.query_params)

    def perform_create(self, serializer):
        payload = offering_write_payload_from_request(self.request, serializer.validated_data)
        offering = create_offering(data=payload)
        serializer.instance = offering

    def perform_update(self, serializer):
        payload = offering_write_payload_from_request(self.request, serializer.validated_data)
        partial = self.action == 'partial_update'
        offering = update_offering(serializer.instance, data=payload, partial=partial)
        serializer.instance = offering

    def perform_destroy(self, instance):
        delete_offering(instance)
    
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
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        """Analytics completo de ofertas"""
        queryset = self.filter_queryset(self.get_queryset())
        analytics_data = get_offering_analytics_full(base_queryset=queryset)
        serializer = ProductOfferingAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar una oferta"""
        offering = self.get_object()
        new_offering = duplicate_offering(offering)
        serializer = ProductOfferingDetailSerializer(new_offering)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bulk_create(self, request):
        """Creación en lote de ofertas"""
        offers_data = request.data.get('offers', [])
        if not offers_data:
            return Response(
                {'error': 'Se requiere el campo "offers" con lista de ofertas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_offers = []
        errors = []
        
        for i, offer_data in enumerate(offers_data):
            serializer = ProductOfferingCreateUpdateSerializer(data=offer_data)
            if serializer.is_valid():
                offer = create_offering(data=serializer.validated_data)
                created_offers.append(offer)
            else:
                errors.append({
                    'index': i,
                    'errors': serializer.errors
                })
        
        if errors:
            return Response(
                {
                    'message': f'Se crearon {len(created_offers)} ofertas con {len(errors)} errores',
                    'created': len(created_offers),
                    'errors': errors
                },
                status=status.HTTP_207_MULTI_STATUS
            )
        
        serializer = ProductOfferingDetailSerializer(created_offers, many=True)
        return Response(
            {
                'message': f'Se crearon {len(created_offers)} ofertas exitosamente',
                'offers': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def export(self, request):
        """Exportación de ofertas en diferentes formatos"""
        format_type = request.query_params.get('format', 'json').lower()
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="offers.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Nombre', 'Código', 'Producto', 'Precio', 'Moneda',
                'Fecha Inicio', 'Fecha Fin', 'Activa'
            ])
            
            for offer in queryset:
                writer.writerow([
                    str(offer.id),
                    offer.name,
                    offer.code,
                    offer.product.name,
                    str(offer.price),
                    offer.currency_code,
                    offer.valid_from,
                    offer.valid_until,
                    offer.is_active
                ])
            
            return response
        
        elif format_type == 'xlsx':
            # Para Excel se podría usar openpyxl u otra librería
            return Response(
                {'error': 'Formato XLSX no implementado aún'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        
        else:
            # JSON por defecto
            serializer = ProductOfferingDetailSerializer(queryset, many=True)
            return Response(serializer.data)
