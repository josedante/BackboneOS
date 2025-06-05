from django.db.models import Count, Avg, Q, F, Sum, Case, When, DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Product, ProductCategory, Modality


@api_view(['GET'])
@permission_classes([])
def product_analytics_dashboard(request):
    """Dashboard principal de analytics de productos"""
    
    # Métricas generales
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = ProductCategory.objects.filter(is_active=True).count()
    total_modalities = Modality.objects.filter(is_active=True).count()
    
    # Productos con/sin precio
    products_with_price = Product.objects.filter(
        is_active=True, base_price__isnull=False
    ).count()
    products_without_price = total_products - products_with_price
    
    # Productos personalizables
    customizable_products = Product.objects.filter(
        is_active=True, customization__isnull=False
    ).count()
    
    # Promedio de precios por moneda
    price_stats = Product.objects.filter(
        is_active=True, base_price__isnull=False
    ).values('currency_code').annotate(
        avg_price=Avg('base_price'),
        min_price=Avg('base_price'),
        max_price=Avg('base_price'),
        count=Count('id')
    )
    
    # Productos creados en los últimos 30 días
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_products = Product.objects.filter(
        is_active=True, created_at__gte=thirty_days_ago
    ).count()
    
    return Response({
        'overview': {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_modalities': total_modalities,
            'products_with_price': products_with_price,
            'products_without_price': products_without_price,
            'customizable_products': customizable_products,
            'recent_products': recent_products
        },
        'price_stats': list(price_stats),
        'growth': {
            'products_last_30_days': recent_products
        }
    })


@api_view(['GET'])
@permission_classes([])
def category_analytics(request):
    """Analytics por categorías"""
    
    # Distribución de productos por categoría
    category_distribution = ProductCategory.objects.filter(
        is_active=True
    ).annotate(
        products_count=Count('product', filter=Q(product__is_active=True)),
        avg_price=Avg('product__base_price', filter=Q(product__is_active=True)),
        total_value=Sum('product__base_price', filter=Q(product__is_active=True))
    ).order_by('-products_count')
    
    # Categorías más populares (por número de productos)
    top_categories = category_distribution[:10]
    
    # Categorías por nivel jerárquico
    level_stats = []
    
    # Calcular nivel jerárquico manualmente ya que 'level' es una propiedad
    def calculate_level_stats():
        stats = {}
        all_categories = ProductCategory.objects.filter(is_active=True)
        
        for category in all_categories:
            level = category.level  # Usar la propiedad calculada
            if level not in stats:
                stats[level] = 0
            stats[level] += 1
        
        return [{'level': level, 'count': count} for level, count in sorted(stats.items())]
    
    level_stats = calculate_level_stats()
    
    # Jerarquía completa con contadores
    def build_hierarchy(parent=None, level=0):
        categories = ProductCategory.objects.filter(
            parent=parent, is_active=True
        ).annotate(
            products_count=Count('product', filter=Q(product__is_active=True))
        )
        
        hierarchy = []
        for category in categories:
            node = {
                'id': str(category.id),
                'name': category.name,
                'code': category.code,
                'level': level,
                'products_count': category.products_count,
                'children': build_hierarchy(category, level + 1)
            }
            hierarchy.append(node)
        
        return hierarchy
    
    hierarchy = build_hierarchy()
    
    return Response({
        'distribution': [
            {
                'id': str(cat.id),
                'name': cat.name,
                'code': cat.code,
                'full_path': cat.full_path,
                'level': cat.level,
                'products_count': cat.products_count,
                'avg_price': float(cat.avg_price or 0),
                'total_value': float(cat.total_value or 0)
            }
            for cat in category_distribution
        ],
        'top_categories': [
            {
                'name': cat.name,
                'products_count': cat.products_count,
                'avg_price': float(cat.avg_price or 0)
            }
            for cat in top_categories
        ],
        'level_stats': level_stats,
        'hierarchy': hierarchy
    })


@api_view(['GET'])
@permission_classes([])
def market_segmentation_analytics(request):
    """Analytics de segmentación de mercado"""
    
    # Productos por segmento de mercado
    segment_stats = Product.objects.filter(
        is_active=True
    ).values(
        'target_segments__name',
        'target_segments__segment_type'
    ).annotate(
        products_count=Count('id', distinct=True),
        avg_price=Avg('base_price'),
        total_value=Sum('base_price')
    ).order_by('-products_count')
    
    # Productos por industria
    industry_stats = Product.objects.filter(
        is_active=True
    ).values(
        'related_industries__name',
        'related_industries__code'
    ).annotate(
        products_count=Count('id', distinct=True),
        avg_price=Avg('base_price')
    ).order_by('-products_count')[:15]
    
    # Productos por habilidades más demandadas
    skill_stats = Product.objects.filter(
        is_active=True
    ).values(
        'related_skills__name',
        'related_skills__skill_type'
    ).annotate(
        products_count=Count('id', distinct=True)
    ).order_by('-products_count')[:20]
    
    # Análisis de modalidades
    modality_stats = Product.objects.filter(
        is_active=True
    ).values(
        'modalities__name'
    ).annotate(
        products_count=Count('id', distinct=True),
        avg_price=Avg('base_price')
    ).order_by('-products_count')
    
    # Matriz de segmentación: Industria x Modalidad
    segmentation_matrix = Product.objects.filter(
        is_active=True,
        related_industries__isnull=False,
        modalities__isnull=False
    ).values(
        'related_industries__name',
        'modalities__name'
    ).annotate(
        products_count=Count('id', distinct=True)
    ).order_by('-products_count')[:50]
    
    return Response({
        'market_segments': [
            {
                'segment_name': item['target_segments__name'] or 'Sin segmento',
                'segment_type': item['target_segments__segment_type'],
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0),
                'total_value': float(item['total_value'] or 0)
            }
            for item in segment_stats
        ],
        'industries': [
            {
                'industry_name': item['related_industries__name'] or 'Sin industria',
                'industry_code': item['related_industries__code'],
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0)
            }
            for item in industry_stats
        ],
        'skills': [
            {
                'skill_name': item['related_skills__name'] or 'Sin habilidad',
                'skill_type': item['related_skills__skill_type'],
                'products_count': item['products_count']
            }
            for item in skill_stats
        ],
        'modalities': [
            {
                'modality_name': item['modalities__name'] or 'Sin modalidad',
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0)
            }
            for item in modality_stats
        ],
        'segmentation_matrix': [
            {
                'industry': item['related_industries__name'],
                'modality': item['modalities__name'],
                'products_count': item['products_count']
            }
            for item in segmentation_matrix
        ]
    })


@api_view(['GET'])
@permission_classes([])
def pricing_analytics(request):
    """Analytics de pricing"""
    
    # Distribución de precios por rangos
    price_ranges = [
        (0, 100, 'Hasta $100'),
        (100, 500, '$100 - $500'),
        (500, 1000, '$500 - $1,000'),
        (1000, 2500, '$1,000 - $2,500'),
        (2500, 5000, '$2,500 - $5,000'),
        (5000, float('inf'), 'Más de $5,000')
    ]
    
    price_distribution = []
    for min_price, max_price, label in price_ranges:
        if max_price == float('inf'):
            count = Product.objects.filter(
                is_active=True,
                base_price__gte=min_price
            ).count()
        else:
            count = Product.objects.filter(
                is_active=True,
                base_price__gte=min_price,
                base_price__lt=max_price
            ).count()
        
        price_distribution.append({
            'range': label,
            'count': count,
            'min_price': min_price,
            'max_price': max_price if max_price != float('inf') else None
        })
    
    # Precios por categoría
    category_pricing = ProductCategory.objects.filter(
        is_active=True,
        product__is_active=True,
        product__base_price__isnull=False
    ).annotate(
        avg_price=Avg('product__base_price'),
        min_price=Avg('product__base_price'),
        max_price=Avg('product__base_price'),
        products_count=Count('product', distinct=True)
    ).order_by('-avg_price')
    
    # Precios por modalidad
    modality_pricing = Modality.objects.filter(
        is_active=True,
        product__is_active=True,
        product__base_price__isnull=False
    ).annotate(
        avg_price=Avg('product__base_price'),
        products_count=Count('product', distinct=True)
    ).order_by('-avg_price')
    
    # Análisis de competitividad por industria
    industry_pricing = Product.objects.filter(
        is_active=True,
        base_price__isnull=False,
        related_industries__isnull=False
    ).values(
        'related_industries__name'
    ).annotate(
        avg_price=Avg('base_price'),
        min_price=Avg('base_price'),
        max_price=Avg('base_price'),
        products_count=Count('id', distinct=True)
    ).order_by('-avg_price')[:10]
    
    return Response({
        'price_distribution': price_distribution,
        'category_pricing': [
            {
                'category_name': cat.name,
                'avg_price': float(cat.avg_price),
                'min_price': float(cat.min_price),
                'max_price': float(cat.max_price),
                'products_count': cat.products_count
            }
            for cat in category_pricing[:10]
        ],
        'modality_pricing': [
            {
                'modality_name': mod.name,
                'avg_price': float(mod.avg_price),
                'products_count': mod.products_count
            }
            for mod in modality_pricing
        ],
        'industry_pricing': [
            {
                'industry_name': item['related_industries__name'],
                'avg_price': float(item['avg_price']),
                'min_price': float(item['min_price']),
                'max_price': float(item['max_price']),
                'products_count': item['products_count']
            }
            for item in industry_pricing
        ]
    })


@api_view(['GET'])
@permission_classes([])
def growth_analytics(request):
    """Analytics de crecimiento temporal"""
    
    # Productos creados por mes (últimos 12 meses)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    monthly_growth = Product.objects.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        products_created=Count('id'),
        active_products=Count('id', filter=Q(is_active=True))
    ).order_by('month')
    
    # Crecimiento por categoría
    category_growth = Product.objects.filter(
        created_at__gte=twelve_months_ago
    ).values(
        'category__name'
    ).annotate(
        products_created=Count('id')
    ).order_by('-products_created')[:10]
    
    # Tendencias de pricing (últimos 6 meses)
    six_months_ago = datetime.now() - timedelta(days=180)
    
    pricing_trends = Product.objects.filter(
        created_at__gte=six_months_ago,
        base_price__isnull=False
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        avg_price=Avg('base_price'),
        products_count=Count('id')
    ).order_by('month')
    
    return Response({
        'monthly_growth': [
            {
                'month': item['month'].strftime('%Y-%m'),
                'products_created': item['products_created'],
                'active_products': item['active_products']
            }
            for item in monthly_growth
        ],
        'category_growth': [
            {
                'category_name': item['category__name'] or 'Sin categoría',
                'products_created': item['products_created']
            }
            for item in category_growth
        ],
        'pricing_trends': [
            {
                'month': item['month'].strftime('%Y-%m'),
                'avg_price': float(item['avg_price']),
                'products_count': item['products_count']
            }
            for item in pricing_trends
        ]
    })


@api_view(['GET'])
@permission_classes([])
def product_recommendations(request):
    """Recomendaciones basadas en análisis de datos"""
    
    # Categorías con pocos productos (oportunidades)
    underutilized_categories = ProductCategory.objects.filter(
        is_active=True
    ).annotate(
        products_count=Count('product', filter=Q(product__is_active=True))
    ).filter(products_count__lte=2).order_by('products_count')[:10]
    
    # Productos sin precio (acción requerida)
    products_without_price = Product.objects.filter(
        is_active=True,
        base_price__isnull=True
    ).count()
    
    # Productos sin categoría
    products_without_category = Product.objects.filter(
        is_active=True,
        category__isnull=True
    ).count()
    
    # Modalidades poco utilizadas
    underutilized_modalities = Modality.objects.filter(
        is_active=True
    ).annotate(
        products_count=Count('product', filter=Q(product__is_active=True))
    ).filter(products_count__lte=1).order_by('products_count')
    
    # Análisis de gaps en el mercado
    # Industrias sin productos específicos
    from world.models import Industry
    industries_without_products = Industry.objects.filter(
        is_active=True
    ).annotate(
        products_count=Count('product', filter=Q(product__is_active=True))
    ).filter(products_count=0)[:10]
    
    return Response({
        'opportunities': {
            'underutilized_categories': [
                {
                    'name': cat.name,
                    'products_count': cat.products_count,
                    'full_path': cat.full_path
                }
                for cat in underutilized_categories
            ],
            'products_without_price': products_without_price,
            'products_without_category': products_without_category,
            'underutilized_modalities': [
                {
                    'name': mod.name,
                    'products_count': mod.products_count
                }
                for mod in underutilized_modalities
            ],
            'industries_without_products': [
                {
                    'name': ind.name,
                    'code': ind.code
                }
                for ind in industries_without_products
            ]
        },
        'recommendations': [
            {
                'type': 'pricing',
                'priority': 'high',
                'message': f'Hay {products_without_price} productos sin precio definido',
                'action': 'Definir precios para productos activos'
            } if products_without_price > 0 else None,
            {
                'type': 'categorization',
                'priority': 'medium',
                'message': f'Hay {products_without_category} productos sin categoría',
                'action': 'Asignar categorías a productos huérfanos'
            } if products_without_category > 0 else None,
            {
                'type': 'market_expansion',
                'priority': 'low',
                'message': f'Se encontraron {len(industries_without_products)} industrias sin productos',
                'action': 'Considerar desarrollo de productos para estas industrias'
            } if len(industries_without_products) > 0 else None
        ]
    })
