from __future__ import annotations

from datetime import datetime, timedelta

from django.db.models import Avg, Count, Max, Min, Q, QuerySet, Sum
from django.db.models.functions import TruncMonth
from our_institution.models import Division

from .models import Customization, Modality, Product, ProductCategory


# --- Queryset factories ---


def divisions_queryset(*, prefetch_categories: bool = True) -> QuerySet:
    qs = Division.objects.all()
    if prefetch_categories:
        qs = qs.select_related().prefetch_related('categories')
    return qs


def division_active_categories(division) -> QuerySet:
    return division.categories.filter(is_active=True)


def division_active_products(division) -> QuerySet:
    return Product.objects.filter(
        category__division=division,
        is_active=True,
    ).select_related('category', 'customization').prefetch_related('modalities')


def categories_base_queryset(*, annotate_counts: bool = True) -> QuerySet:
    qs = ProductCategory.objects.filter(is_active=True).select_related('parent')
    if annotate_counts:
        qs = qs.annotate(
            products_count=Count('product', filter=Q(product__is_active=True)),
            subcategories_count=Count(
                'subcategories', filter=Q(subcategories__is_active=True)
            ),
        )
    return qs


def category_tree_roots(*, base_queryset: QuerySet | None = None) -> QuerySet:
    qs = base_queryset if base_queryset is not None else categories_base_queryset()
    return qs.filter(parent__isnull=True)


def products_for_category_tree(category) -> QuerySet:
    descendant_categories = category.get_descendants()
    category_ids = [category.id] + [cat.id for cat in descendant_categories]
    return Product.objects.filter(
        category__id__in=category_ids,
        is_active=True,
    ).select_related('category', 'customization').prefetch_related('modalities')


def products_active_queryset() -> QuerySet:
    return Product.objects.filter(is_active=True)


def products_list_queryset(*, action: str = 'list') -> QuerySet:
    queryset = products_active_queryset()
    if action == 'list':
        return queryset.select_related('category', 'customization').prefetch_related(
            'modalities', 'target_segments'
        )
    if action == 'retrieve':
        return queryset.select_related('category', 'customization').prefetch_related(
            'modalities',
            'target_segments',
            'related_industries',
            'related_functions',
            'related_skills',
            'descriptors',
            'tags',
        )
    return queryset


def products_search_advanced(*, query: str, base_qs: QuerySet | None = None) -> QuerySet:
    qs = base_qs if base_qs is not None else products_active_queryset()
    return qs.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(category__name__icontains=query)
        | Q(tags__name__icontains=query)
        | Q(descriptors__name__icontains=query)
        | Q(related_skills__name__icontains=query)
        | Q(related_industries__name__icontains=query)
    ).distinct()


def product_included_queryset(product) -> QuerySet:
    return product.included_products.filter(is_active=True)


def product_parent_bundles_queryset(product) -> QuerySet:
    return product.included_in_products.filter(is_active=True)


# --- Aggregations ---


def get_product_stats(queryset: QuerySet) -> dict:
    """Return aggregated statistics for the given product queryset."""
    category_stats = (
        queryset.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    modality_stats = (
        queryset.values('modalities__name')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')[:10]
    )
    industry_stats = (
        queryset.values('related_industries__name')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')[:10]
    )

    price_data = queryset.filter(base_price__isnull=False).aggregate(
        avg_price=Avg('base_price'),
        min_price=Min('base_price'),
        max_price=Max('base_price'),
        products_with_price=Count('id'),
    )
    duration_data = queryset.filter(duration__isnull=False).aggregate(
        products_with_duration=Count('id'),
    )

    return {
        'total_products': queryset.count(),
        'by_category': {
            item['category__name'] or 'Sin categoría': item['count']
            for item in category_stats
        },
        'by_modality': {
            item['modalities__name'] or 'Sin modalidad': item['count']
            for item in modality_stats
        },
        'by_industry': {
            item['related_industries__name'] or 'Sin industria': item['count']
            for item in industry_stats
        },
        'price_stats': {
            'average': float(price_data['avg_price'] or 0),
            'minimum': float(price_data['min_price'] or 0),
            'maximum': float(price_data['max_price'] or 0),
            'products_with_price': price_data['products_with_price'],
            'products_without_price': queryset.filter(base_price__isnull=True).count(),
        },
        'duration_stats': {
            'products_with_duration': duration_data['products_with_duration'],
            'products_without_duration': queryset.filter(duration__isnull=True).count(),
        },
    }


def get_division_summary(division) -> dict:
    """Return category/product counts and price aggregates for a division."""
    products_qs = Product.objects.filter(category__division=division, is_active=True)
    products_with_price = products_qs.filter(base_price__isnull=False)

    price_stats: dict = {}
    if products_with_price.exists():
        agg = products_with_price.aggregate(
            avg_price=Avg('base_price'),
            min_price=Min('base_price'),
            max_price=Max('base_price'),
        )
        price_stats = {
            'products_with_price': products_with_price.count(),
            'avg_price': agg['avg_price'],
            'min_price': agg['min_price'],
            'max_price': agg['max_price'],
        }

    return {
        'categories_count': division.categories.filter(is_active=True).count(),
        'products_count': products_qs.count(),
        'price_statistics': price_stats,
    }


def get_bundle_info(product) -> dict:
    """Return bundle metrics and included products queryset for serialization in views."""
    included_qs = product_included_queryset(product)
    return {
        'included_products_qs': included_qs,
        'total_included_price': product.get_total_included_price(),
        'bundle_price_display': product.get_bundle_price_display(),
        'is_bundle': product.is_bundle,
        'included_count': included_qs.count(),
    }


# --- Analytics ---


def _category_level_stats() -> list[dict]:
    stats: dict[int, int] = {}
    for category in ProductCategory.objects.filter(is_active=True):
        level = category.level
        stats[level] = stats.get(level, 0) + 1
    return [{'level': level, 'count': count} for level, count in sorted(stats.items())]


def _category_hierarchy(parent=None, level=0) -> list[dict]:
    categories = ProductCategory.objects.filter(parent=parent, is_active=True).annotate(
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
            'children': _category_hierarchy(category, level + 1),
        }
        hierarchy.append(node)
    return hierarchy


def get_division_analytics_dashboard() -> dict:
    divisions_stats = Division.objects.filter(is_active=True).annotate(
        categories_count=Count('categories', filter=Q(categories__is_active=True)),
        products_count=Count(
            'categories__product', filter=Q(categories__product__is_active=True)
        ),
        avg_price=Avg(
            'categories__product__base_price',
            filter=Q(categories__product__is_active=True),
        ),
        products_with_price=Count(
            'categories__product',
            filter=Q(
                categories__product__is_active=True,
                categories__product__base_price__isnull=False,
            ),
        ),
    ).values(
        'id',
        'name',
        'code',
        'categories_count',
        'products_count',
        'avg_price',
        'products_with_price',
    )

    top_divisions_by_products = divisions_stats.order_by('-products_count')[:5]

    division_distribution = []
    for division in divisions_stats:
        if division['products_count'] > 0:
            division_distribution.append(
                {
                    'division': division['name'],
                    'products_count': division['products_count'],
                    'categories_count': division['categories_count'],
                    'avg_price': division['avg_price'],
                }
            )

    divisions_stats_list = list(divisions_stats)

    return {
        'divisions_overview': {
            'total_divisions': Division.objects.filter(is_active=True).count(),
            'divisions_with_products': len(
                [d for d in divisions_stats_list if d['products_count'] > 0]
            ),
            'top_divisions': list(top_divisions_by_products),
            'distribution': division_distribution,
        },
        'summary': {
            'total_categories_across_divisions': sum(
                d['categories_count'] for d in divisions_stats_list
            ),
            'total_products_across_divisions': sum(
                d['products_count'] for d in divisions_stats_list
            ),
            'avg_products_per_division': (
                sum(d['products_count'] for d in divisions_stats_list)
                / len(divisions_stats_list)
                if divisions_stats_list
                else 0
            ),
        },
    }


def get_product_analytics_dashboard() -> dict:
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = ProductCategory.objects.filter(is_active=True).count()
    total_modalities = Modality.objects.filter(is_active=True).count()
    total_divisions = Division.objects.filter(is_active=True).count()

    products_with_price = Product.objects.filter(
        is_active=True, base_price__isnull=False
    ).count()
    products_without_price = total_products - products_with_price

    customizable_products = Product.objects.filter(
        is_active=True, customization__isnull=False
    ).count()

    price_stats = Product.objects.filter(
        is_active=True, base_price__isnull=False
    ).values('currency_code').annotate(
        avg_price=Avg('base_price'),
        min_price=Avg('base_price'),
        max_price=Avg('base_price'),
        count=Count('id'),
    )

    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_products = Product.objects.filter(
        is_active=True, created_at__gte=thirty_days_ago
    ).count()

    return {
        'overview': {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_modalities': total_modalities,
            'total_divisions': total_divisions,
            'products_with_price': products_with_price,
            'products_without_price': products_without_price,
            'customizable_products': customizable_products,
            'recent_products': recent_products,
        },
        'price_stats': list(price_stats),
        'growth': {
            'products_last_30_days': recent_products,
        },
    }


def get_category_analytics() -> dict:
    category_distribution = ProductCategory.objects.filter(is_active=True).annotate(
        products_count=Count('product', filter=Q(product__is_active=True)),
        avg_price=Avg('product__base_price', filter=Q(product__is_active=True)),
        total_value=Sum('product__base_price', filter=Q(product__is_active=True)),
    ).order_by('-products_count')

    top_categories = category_distribution[:10]
    level_stats = _category_level_stats()
    hierarchy = _category_hierarchy()

    return {
        'distribution': [
            {
                'id': str(cat.id),
                'name': cat.name,
                'code': cat.code,
                'full_path': cat.full_path,
                'level': cat.level,
                'products_count': cat.products_count,
                'avg_price': float(cat.avg_price or 0),
                'total_value': float(cat.total_value or 0),
            }
            for cat in category_distribution
        ],
        'top_categories': [
            {
                'name': cat.name,
                'products_count': cat.products_count,
                'avg_price': float(cat.avg_price or 0),
            }
            for cat in top_categories
        ],
        'level_stats': level_stats,
        'hierarchy': hierarchy,
    }


def get_market_segmentation_analytics() -> dict:
    segment_stats = (
        Product.objects.filter(is_active=True)
        .values('target_segments__name', 'target_segments__segment_type')
        .annotate(
            products_count=Count('id', distinct=True),
            avg_price=Avg('base_price'),
            total_value=Sum('base_price'),
        )
        .order_by('-products_count')
    )

    industry_stats = (
        Product.objects.filter(is_active=True)
        .values('related_industries__name', 'related_industries__code')
        .annotate(
            products_count=Count('id', distinct=True),
            avg_price=Avg('base_price'),
        )
        .order_by('-products_count')[:15]
    )

    skill_stats = (
        Product.objects.filter(is_active=True)
        .values('related_skills__name', 'related_skills__skill_type')
        .annotate(products_count=Count('id', distinct=True))
        .order_by('-products_count')[:20]
    )

    modality_stats = (
        Product.objects.filter(is_active=True)
        .values('modalities__name')
        .annotate(
            products_count=Count('id', distinct=True),
            avg_price=Avg('base_price'),
        )
        .order_by('-products_count')
    )

    segmentation_matrix = (
        Product.objects.filter(
            is_active=True,
            related_industries__isnull=False,
            modalities__isnull=False,
        )
        .values('related_industries__name', 'modalities__name')
        .annotate(products_count=Count('id', distinct=True))
        .order_by('-products_count')[:50]
    )

    return {
        'market_segments': [
            {
                'segment_name': item['target_segments__name'] or 'Sin segmento',
                'segment_type': item['target_segments__segment_type'],
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0),
                'total_value': float(item['total_value'] or 0),
            }
            for item in segment_stats
        ],
        'industries': [
            {
                'industry_name': item['related_industries__name'] or 'Sin industria',
                'industry_code': item['related_industries__code'],
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0),
            }
            for item in industry_stats
        ],
        'skills': [
            {
                'skill_name': item['related_skills__name'] or 'Sin habilidad',
                'skill_type': item['related_skills__skill_type'],
                'products_count': item['products_count'],
            }
            for item in skill_stats
        ],
        'modalities': [
            {
                'modality_name': item['modalities__name'] or 'Sin modalidad',
                'products_count': item['products_count'],
                'avg_price': float(item['avg_price'] or 0),
            }
            for item in modality_stats
        ],
        'segmentation_matrix': [
            {
                'industry': item['related_industries__name'],
                'modality': item['modalities__name'],
                'products_count': item['products_count'],
            }
            for item in segmentation_matrix
        ],
    }


def get_pricing_analytics() -> dict:
    price_ranges = [
        (0, 100, 'Hasta $100'),
        (100, 500, '$100 - $500'),
        (500, 1000, '$500 - $1,000'),
        (1000, 2500, '$1,000 - $2,500'),
        (2500, 5000, '$2,500 - $5,000'),
        (5000, float('inf'), 'Más de $5,000'),
    ]

    price_distribution = []
    for min_price, max_price, label in price_ranges:
        if max_price == float('inf'):
            count = Product.objects.filter(
                is_active=True, base_price__gte=min_price
            ).count()
        else:
            count = Product.objects.filter(
                is_active=True,
                base_price__gte=min_price,
                base_price__lt=max_price,
            ).count()

        price_distribution.append(
            {
                'range': label,
                'count': count,
                'min_price': min_price,
                'max_price': max_price if max_price != float('inf') else None,
            }
        )

    category_pricing = (
        ProductCategory.objects.filter(
            is_active=True,
            product__is_active=True,
            product__base_price__isnull=False,
        )
        .annotate(
            avg_price=Avg('product__base_price'),
            min_price=Avg('product__base_price'),
            max_price=Avg('product__base_price'),
            products_count=Count('product', distinct=True),
        )
        .order_by('-avg_price')
    )

    modality_pricing = (
        Modality.objects.filter(
            is_active=True,
            product__is_active=True,
            product__base_price__isnull=False,
        )
        .annotate(
            avg_price=Avg('product__base_price'),
            products_count=Count('product', distinct=True),
        )
        .order_by('-avg_price')
    )

    industry_pricing = (
        Product.objects.filter(
            is_active=True,
            base_price__isnull=False,
            related_industries__isnull=False,
        )
        .values('related_industries__name')
        .annotate(
            avg_price=Avg('base_price'),
            min_price=Avg('base_price'),
            max_price=Avg('base_price'),
            products_count=Count('id', distinct=True),
        )
        .order_by('-avg_price')[:10]
    )

    return {
        'price_distribution': price_distribution,
        'category_pricing': [
            {
                'category_name': cat.name,
                'avg_price': float(cat.avg_price),
                'min_price': float(cat.min_price),
                'max_price': float(cat.max_price),
                'products_count': cat.products_count,
            }
            for cat in category_pricing[:10]
        ],
        'modality_pricing': [
            {
                'modality_name': mod.name,
                'avg_price': float(mod.avg_price),
                'products_count': mod.products_count,
            }
            for mod in modality_pricing
        ],
        'industry_pricing': [
            {
                'industry_name': item['related_industries__name'],
                'avg_price': float(item['avg_price']),
                'min_price': float(item['min_price']),
                'max_price': float(item['max_price']),
                'products_count': item['products_count'],
            }
            for item in industry_pricing
        ],
    }


def get_growth_analytics() -> dict:
    twelve_months_ago = datetime.now() - timedelta(days=365)

    monthly_growth = (
        Product.objects.filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            products_created=Count('id'),
            active_products=Count('id', filter=Q(is_active=True)),
        )
        .order_by('month')
    )

    category_growth = (
        Product.objects.filter(created_at__gte=twelve_months_ago)
        .values('category__name')
        .annotate(products_created=Count('id'))
        .order_by('-products_created')[:10]
    )

    six_months_ago = datetime.now() - timedelta(days=180)

    pricing_trends = (
        Product.objects.filter(
            created_at__gte=six_months_ago,
            base_price__isnull=False,
        )
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            avg_price=Avg('base_price'),
            products_count=Count('id'),
        )
        .order_by('month')
    )

    return {
        'monthly_growth': [
            {
                'month': item['month'].strftime('%Y-%m'),
                'products_created': item['products_created'],
                'active_products': item['active_products'],
            }
            for item in monthly_growth
        ],
        'category_growth': [
            {
                'category_name': item['category__name'] or 'Sin categoría',
                'products_created': item['products_created'],
            }
            for item in category_growth
        ],
        'pricing_trends': [
            {
                'month': item['month'].strftime('%Y-%m'),
                'avg_price': float(item['avg_price']),
                'products_count': item['products_count'],
            }
            for item in pricing_trends
        ],
    }


def get_product_recommendations() -> dict:
    from world.models import Industry

    underutilized_categories = (
        ProductCategory.objects.filter(is_active=True)
        .annotate(products_count=Count('product', filter=Q(product__is_active=True)))
        .filter(products_count__lte=2)
        .order_by('products_count')[:10]
    )

    products_without_price = Product.objects.filter(
        is_active=True, base_price__isnull=True
    ).count()

    products_without_category = Product.objects.filter(
        is_active=True, category__isnull=True
    ).count()

    underutilized_modalities = (
        Modality.objects.filter(is_active=True)
        .annotate(products_count=Count('product', filter=Q(product__is_active=True)))
        .filter(products_count__lte=1)
        .order_by('products_count')
    )

    industries_without_products = (
        Industry.objects.filter(is_active=True)
        .annotate(products_count=Count('product', filter=Q(product__is_active=True)))
        .filter(products_count=0)[:10]
    )

    return {
        'opportunities': {
            'underutilized_categories': [
                {
                    'name': cat.name,
                    'products_count': cat.products_count,
                    'full_path': cat.full_path,
                }
                for cat in underutilized_categories
            ],
            'products_without_price': products_without_price,
            'products_without_category': products_without_category,
            'underutilized_modalities': [
                {
                    'name': mod.name,
                    'products_count': mod.products_count,
                }
                for mod in underutilized_modalities
            ],
            'industries_without_products': [
                {
                    'name': ind.name,
                    'code': ind.code,
                }
                for ind in industries_without_products
            ],
        },
        'recommendations': [
            {
                'type': 'pricing',
                'priority': 'high',
                'message': f'Hay {products_without_price} productos sin precio definido',
                'action': 'Definir precios para productos activos',
            }
            if products_without_price > 0
            else None,
            {
                'type': 'categorization',
                'priority': 'medium',
                'message': f'Hay {products_without_category} productos sin categoría',
                'action': 'Asignar categorías a productos huérfanos',
            }
            if products_without_category > 0
            else None,
            {
                'type': 'market_expansion',
                'priority': 'low',
                'message': (
                    f'Se encontraron {len(industries_without_products)} '
                    'industrias sin productos'
                ),
                'action': 'Considerar desarrollo de productos para estas industrias',
            }
            if len(industries_without_products) > 0
            else None,
        ],
    }


# --- HTML template context ---


def get_products_list_context(
    *,
    search: str = '',
    category_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Build paginated list context for the products CRM index page."""
    from django.core.paginator import Paginator

    queryset = products_list_queryset(action='list')
    if search:
        queryset = products_search_advanced(query=search, base_qs=queryset)
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    queryset = queryset.order_by('name')
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    analytics = get_product_analytics_dashboard()
    return {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'search': search,
        'category_id': category_id,
        'page_size': page_size,
        'categories': categories_base_queryset().order_by('name'),
        'overview': analytics.get('overview', {}),
    }


def get_product_detail_context(product_id) -> dict:
    """Load a single product with bundle metadata for the detail template."""
    from django.shortcuts import get_object_or_404

    product = get_object_or_404(products_list_queryset(action='retrieve'), pk=product_id)
    bundle = get_bundle_info(product)
    return {
        'product': product,
        'bundle': bundle,
        'included_products': list(bundle['included_products_qs']),
    }


def get_product_form_options() -> dict:
    """Querysets for product create/update form widgets."""
    from world.models import (  # noqa: PLC0415 — lazy import avoids circular deps
        FunctionOrResponsibility,
        Industry,
        MarketSegment,
        Skill,
        Tag,
        WorldDescriptor,
    )

    return {
        'categories': categories_base_queryset().order_by('name'),
        'modalities': Modality.objects.filter(is_active=True).order_by('name'),
        'customizations': Customization.objects.filter(is_active=True).order_by('name'),
        'target_segments': MarketSegment.objects.filter(is_active=True).order_by('name'),
        'industries': Industry.objects.filter(is_active=True).order_by('name'),
        'functions': FunctionOrResponsibility.objects.filter(is_active=True).order_by('name'),
        'skills': Skill.objects.filter(is_active=True).order_by('name'),
        'descriptors': WorldDescriptor.objects.filter(is_active=True).order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
        'products_for_bundle': products_active_queryset().order_by('name'),
    }
