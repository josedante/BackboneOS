from django.shortcuts import render
from django.db.models import Q, Count, Avg, Min, Max, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, BasePermission
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from .models import Division, ProductCategory, Modality, Customization, Product
from .serializers import (
    DivisionSerializer, ProductCategorySerializer, ProductCategoryTreeSerializer,
    ModalitySerializer, CustomizationSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer
)


class DivisionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    has_categories = django_filters.BooleanFilter(method='filter_has_categories')
    
    class Meta:
        model = Division
        fields = ['is_active']
    
    def filter_has_categories(self, queryset, name, value):
        if value:
            return queryset.filter(categories__isnull=False).distinct()
        return queryset.filter(categories__isnull=True)


class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DivisionFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Division.objects.select_related().prefetch_related('categories')

    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """Obtener todas las categorías de una división"""
        division = self.get_object()
        categories = division.categories.filter(is_active=True)
        serializer = ProductCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtener todos los productos de una división"""
        division = self.get_object()
        products = Product.objects.filter(
            category__division=division,
            is_active=True
        ).select_related('category', 'customization').prefetch_related('modalities')
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Resumen estadístico de la división"""
        division = self.get_object()
        
        # Contar categorías
        categories_count = division.categories.filter(is_active=True).count()
        
        # Contar productos
        products_count = Product.objects.filter(
            category__division=division,
            is_active=True
        ).count()
        
        # Estadísticas de precios
        products_with_price = Product.objects.filter(
            category__division=division,
            is_active=True,
            base_price__isnull=False
        )
        
        price_stats = {}
        if products_with_price.exists():
            price_agg = products_with_price.aggregate(
                avg_price=Avg('base_price'),
                min_price=Min('base_price'),
                max_price=Max('base_price')
            )
            price_stats = {
                'products_with_price': products_with_price.count(),
                'avg_price': price_agg['avg_price'],
                'min_price': price_agg['min_price'],
                'max_price': price_agg['max_price']
            }
        
        return Response({
            'division': DivisionSerializer(division, context={'request': request}).data,
            'categories_count': categories_count,
            'products_count': products_count,
            'price_statistics': price_stats
        })


class ProductCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    division = django_filters.ModelChoiceFilter(queryset=Division.objects.filter(is_active=True))
    level = django_filters.NumberFilter(method='filter_by_level')
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = ProductCategory
        fields = ['is_active', 'parent', 'division']
    
    def filter_by_level(self, queryset, name, value):
        """Filtrar por nivel de jerarquía"""
        # Usamos SQL raw para filtrar por nivel calculado
        return queryset.extra(
            where=[
                """
                (
                    WITH RECURSIVE category_hierarchy AS (
                        SELECT id, parent_id, 0 as level 
                        FROM products_productcategory 
                        WHERE id = products_productcategory.id
                        UNION ALL
                        SELECT pc.id, pc.parent_id, ch.level + 1
                        FROM products_productcategory pc
                        JOIN category_hierarchy ch ON pc.id = ch.parent_id
                    )
                    SELECT level FROM category_hierarchy 
                    WHERE id = products_productcategory.id 
                    LIMIT 1
                ) = %s
                """
            ],
            params=[value]
        )
    
    def filter_has_products(self, queryset, name, value):
        """Filtrar categorías que tienen productos"""
        if value:
            return queryset.annotate(
                products_count=Count('product', filter=Q(product__is_active=True))
            ).filter(products_count__gt=0)
        return queryset


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtros de precio
    min_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name='base_price')
    
    # Filtros de categoría (incluye subcategorías)
    category_tree = django_filters.ModelChoiceFilter(
        queryset=ProductCategory.objects.filter(is_active=True),
        method='filter_category_tree'
    )
    
    # Filtros M2M
    industries = django_filters.ModelMultipleChoiceFilter(
        field_name='related_industries',
        queryset=None,  # Se define en __init__
        conjoined=False  # OR en lugar de AND
    )
    skills = django_filters.ModelMultipleChoiceFilter(
        field_name='related_skills',
        queryset=None,
        conjoined=False
    )
    segments = django_filters.ModelMultipleChoiceFilter(
        field_name='target_segments',
        queryset=None,
        conjoined=False
    )
    modalities = django_filters.ModelMultipleChoiceFilter(
        field_name='modalities',
        queryset=Modality.objects.filter(is_active=True),
        conjoined=False
    )
    
    # Filtros de duración
    min_duration_days = django_filters.NumberFilter(method='filter_min_duration_days')
    max_duration_days = django_filters.NumberFilter(method='filter_max_duration_days')
    
    # Filtros booleanos
    is_customizable = django_filters.BooleanFilter(method='filter_customizable')
    has_price = django_filters.BooleanFilter(method='filter_has_price')
    
    # Búsqueda semántica en descriptores
    semantic_search = django_filters.CharFilter(method='filter_semantic_search')
    
    class Meta:
        model = Product
        fields = [
            'is_active', 'category', 'customization', 'currency_code'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Importación lazy para evitar problemas circulares
        from world.models import Industry, Skill, MarketSegment
        self.filters['industries'].queryset = Industry.objects.filter(is_active=True)
        self.filters['skills'].queryset = Skill.objects.filter(is_active=True)
        self.filters['segments'].queryset = MarketSegment.objects.filter(is_active=True)
    
    def filter_category_tree(self, queryset, name, value):
        """Filtrar productos por categoría incluyendo subcategorías"""
        if value:
            # Obtener todas las subcategorías
            descendant_categories = value.get_descendants()
            category_ids = [value.id] + [cat.id for cat in descendant_categories]
            return queryset.filter(category__id__in=category_ids)
        return queryset
    
    def filter_min_duration_days(self, queryset, name, value):
        """Filtrar por duración mínima en días"""
        from datetime import timedelta
        min_duration = timedelta(days=value)
        return queryset.filter(duration__gte=min_duration)
    
    def filter_max_duration_days(self, queryset, name, value):
        """Filtrar por duración máxima en días"""
        from datetime import timedelta
        max_duration = timedelta(days=value)
        return queryset.filter(duration__lte=max_duration)
    
    def filter_customizable(self, queryset, name, value):
        """Filtrar productos personalizables"""
        if value:
            return queryset.filter(customization__isnull=False)
        else:
            return queryset.filter(customization__isnull=True)
    
    def filter_has_price(self, queryset, name, value):
        """Filtrar productos con/sin precio"""
        if value:
            return queryset.filter(base_price__isnull=False)
        else:
            return queryset.filter(base_price__isnull=True)
    
    def filter_semantic_search(self, queryset, name, value):
        """Búsqueda semántica en descriptores y tags"""
        return queryset.filter(
            Q(descriptors__name__icontains=value) |
            Q(tags__name__icontains=value) |
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ).distinct()


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.filter(is_active=True).select_related('parent')
    serializer_class = ProductCategorySerializer
    filterset_class = ProductCategoryFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'level', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Anotar con contadores para optimización
        return queryset.annotate(
            products_count=Count('product', filter=Q(product__is_active=True)),
            subcategories_count=Count('subcategories', filter=Q(subcategories__is_active=True))
        )
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Endpoint para obtener el árbol completo de categorías"""
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = ProductCategoryTreeSerializer(root_categories, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtener productos de una categoría (incluyendo subcategorías)"""
        category = self.get_object()
        descendant_categories = category.get_descendants()
        category_ids = [category.id] + [cat.id for cat in descendant_categories]
        
        products = Product.objects.filter(
            category__id__in=category_ids,
            is_active=True
        ).select_related('category', 'customization').prefetch_related('modalities')
        
        # Aplicar paginación
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ModalityViewSet(viewsets.ModelViewSet):
    queryset = Modality.objects.filter(is_active=True)
    serializer_class = ModalitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticatedOrReadOnly]


class CustomizationViewSet(viewsets.ModelViewSet):
    queryset = Customization.objects.filter(is_active=True)
    serializer_class = CustomizationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductViewPermission(BasePermission):
    """
    Permiso personalizado para productos:
    - Lectura pública limitada (sin precios sensibles)
    - Escritura solo para usuarios autenticados
    - Analytics y estadísticas solo para usuarios autenticados
    """
    
    def has_permission(self, request, view):
        # Endpoints completamente protegidos
        protected_actions = ['stats', 'search_advanced', 'duplicate']
        
        if view.action in protected_actions:
            return request.user.is_authenticated
        
        # CRUD: Solo lectura pública, escritura autenticada
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated
            
        # Lectura permitida (GET)
        return True


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description', 'category__name', 'tags__name']
    ordering_fields = ['name', 'code', 'base_price', 'created_at', 'updated_at']
    ordering = ['name']
    permission_classes = [ProductViewPermission]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Optimizaciones de consulta
        if self.action == 'list':
            return queryset.select_related(
                'category', 'customization'
            ).prefetch_related(
                'modalities', 'target_segments'
            )
        elif self.action == 'retrieve':
            return queryset.select_related(
                'category', 'customization'
            ).prefetch_related(
                'modalities', 'target_segments', 'related_industries',
                'related_functions', 'related_skills', 'descriptors', 'tags'
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    @method_decorator(cache_page(60 * 5))  # Cache por 5 minutos
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de productos"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total_products': queryset.count(),
            'by_category': {},
            'by_modality': {},
            'by_industry': {},
            'price_stats': {},
            'duration_stats': {}
        }
        
        # Estadísticas por categoría
        category_stats = queryset.values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        stats['by_category'] = {item['category__name'] or 'Sin categoría': item['count'] for item in category_stats}
        
        # Estadísticas por modalidad
        modality_stats = queryset.values(
            'modalities__name'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')[:10]
        stats['by_modality'] = {item['modalities__name'] or 'Sin modalidad': item['count'] for item in modality_stats}
        
        # Estadísticas por industria
        industry_stats = queryset.values(
            'related_industries__name'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')[:10]
        stats['by_industry'] = {item['related_industries__name'] or 'Sin industria': item['count'] for item in industry_stats}
        
        # Estadísticas de precios
        price_data = queryset.filter(base_price__isnull=False).aggregate(
            avg_price=Avg('base_price'),
            min_price=Min('base_price'),
            max_price=Max('base_price'),
            products_with_price=Count('id')
        )
        stats['price_stats'] = {
            'average': float(price_data['avg_price'] or 0),
            'minimum': float(price_data['min_price'] or 0),
            'maximum': float(price_data['max_price'] or 0),
            'products_with_price': price_data['products_with_price'],
            'products_without_price': queryset.filter(base_price__isnull=True).count()
        }
        
        # Estadísticas de duración
        duration_data = queryset.filter(duration__isnull=False).aggregate(
            products_with_duration=Count('id')
        )
        stats['duration_stats'] = {
            'products_with_duration': duration_data['products_with_duration'],
            'products_without_duration': queryset.filter(duration__isnull=True).count()
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def search_advanced(self, request):
        """Búsqueda avanzada con análisis semántico"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Parámetro q requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Búsqueda en múltiples campos con pesos
        queryset = self.get_queryset().filter(
            Q(name__icontains=query) |  # Peso alto
            Q(description__icontains=query) |  # Peso medio
            Q(category__name__icontains=query) |  # Peso medio
            Q(tags__name__icontains=query) |  # Peso bajo
            Q(descriptors__name__icontains=query) |  # Peso bajo
            Q(related_skills__name__icontains=query) |  # Peso bajo
            Q(related_industries__name__icontains=query)  # Peso bajo
        ).distinct()
        
        # Aplicar filtros adicionales
        queryset = self.filter_queryset(queryset)
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar un producto"""
        product = self.get_object()
        
        # Crear copia
        new_product = Product.objects.get(pk=product.pk)
        new_product.pk = None
        new_product.name = f"{product.name} (Copia)"
        new_product.code = f"{product.code}_COPY_{product.id}"
        new_product.save()
        
        # Copiar relaciones M2M
        new_product.modalities.set(product.modalities.all())
        new_product.target_segments.set(product.target_segments.all())
        new_product.related_industries.set(product.related_industries.all())
        new_product.related_functions.set(product.related_functions.all())
        new_product.related_skills.set(product.related_skills.all())
        new_product.descriptors.set(product.descriptors.all())
        new_product.tags.set(product.tags.all())
        
        serializer = ProductDetailSerializer(new_product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
