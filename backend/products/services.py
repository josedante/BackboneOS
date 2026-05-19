from __future__ import annotations

from django.db.models import Avg, Count, Min, Max, Q, QuerySet

from .models import Product


def duplicate_product(product: Product) -> Product:
    """Create a deep copy of a product, including all M2M relationships."""
    new_product = Product.objects.get(pk=product.pk)
    new_product.pk = None
    new_product.name = f"{product.name} (Copia)"
    new_product.code = f"{product.code}_COPY_{product.id}"
    new_product.save()

    new_product.included_products.set(product.included_products.all())
    new_product.modalities.set(product.modalities.all())
    new_product.target_segments.set(product.target_segments.all())
    new_product.related_industries.set(product.related_industries.all())
    new_product.related_functions.set(product.related_functions.all())
    new_product.related_skills.set(product.related_skills.all())
    new_product.descriptors.set(product.descriptors.all())
    new_product.tags.set(product.tags.all())

    return new_product


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
