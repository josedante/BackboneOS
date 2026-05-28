"""
Read-only query layer for the offers app.

Consumed by DRF viewsets and Django template views. Mutations belong in
``services.py`` — never fetch data via HTTP to the REST API from templates.
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, QuerySet, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from interactions.models import Channel
from our_institution.models import Seat
from products.models import Product, ProductCategory

from .models import ProductOffering
from .serializers import ProductOfferingListSerializer

_FORM_FK_LIMIT = 500


def offerings_base_queryset(*, action: str = 'list') -> QuerySet:
    """
    Base queryset with relations prefetched for list or detail surfaces.

    ``action='retrieve'`` loads full M2M targeting fields for the detail form.
    """
    qs = ProductOffering.objects.select_related(
        'product',
        'product__category',
        'product__category__division',
    )
    if action == 'list':
        return qs.prefetch_related('channels', 'target_segments')
    if action == 'retrieve':
        return qs.prefetch_related(
            'channels',
            'seats',
            'target_segments',
            'related_industries',
            'related_functions',
            'descriptors',
            'tags',
        )
    return qs


def _validity_q(*, valid_now: bool) -> Q:
    """
    Build Q filter for current validity (mirrors ``ProductOffering.is_currently_valid``).

    Valid now: (no start OR start <= today) AND (no end OR end >= today).
    """
    today = timezone.now().date()
    if valid_now:
        return (
            Q(valid_from__isnull=True) | Q(valid_from__lte=today)
        ) & (
            Q(valid_until__isnull=True) | Q(valid_until__gte=today)
        )
    # Expired or future — inverse slices used via validity_status in list filter.
    return Q()


def offerings_list_filter(
    qs: QuerySet,
    *,
    search: str = '',
    is_active: str | None = None,
    product_id=None,
    category_id=None,
    currency_code: str = '',
    validity_status: str = '',
    min_price: str | None = None,
    max_price: str | None = None,
) -> QuerySet:
    """
    Apply HTML list filters.

    ``validity_status``: ``valid_now``, ``expired``, ``future`` (empty = no filter).
    """
    if search:
        term = search.strip()
        qs = qs.filter(
            Q(name__icontains=term)
            | Q(code__icontains=term)
            | Q(description__icontains=term)
            | Q(product__name__icontains=term)
            | Q(product__code__icontains=term)
        ).distinct()

    if is_active in ('true', '1'):
        qs = qs.filter(is_active=True)
    elif is_active in ('false', '0'):
        qs = qs.filter(is_active=False)

    if product_id:
        qs = qs.filter(product_id=product_id)
    if category_id:
        qs = qs.filter(product__category_id=category_id)
    if currency_code:
        qs = qs.filter(currency_code=currency_code)

    today = timezone.now().date()
    if validity_status == 'valid_now':
        qs = qs.filter(_validity_q(valid_now=True))
    elif validity_status == 'expired':
        qs = qs.filter(valid_until__lt=today)
    elif validity_status == 'future':
        qs = qs.filter(valid_from__gt=today)

    if min_price not in (None, ''):
        qs = qs.filter(price__gte=min_price)
    if max_price not in (None, ''):
        qs = qs.filter(price__lte=max_price)

    return qs.order_by('-valid_from', 'name')


def offerings_api_filter(qs: QuerySet, *, request_params) -> QuerySet:
    """
    DRF-only query-param filters (``currently_valid``, ``product``, price range).

    Keeps ViewSet ``get_queryset`` thin while sharing the base queryset factory.
    """
    currently_valid = request_params.get('currently_valid')
    today = timezone.now().date()
    if currently_valid == 'true':
        qs = qs.filter(_validity_q(valid_now=True))
    elif currently_valid == 'false':
        qs = qs.filter(
            Q(valid_until__lt=today) | Q(valid_from__gt=today)
        )

    product_id = request_params.get('product')
    if product_id:
        qs = qs.filter(product_id=product_id)

    min_price = request_params.get('min_price')
    max_price = request_params.get('max_price')
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    return qs


def get_offering_analytics_overview() -> dict:
    """
    Summary metrics for the offers list hub (subset of full DRF analytics).

    Includes inactive offerings in totals, matching the API analytics action.
    """
    queryset = ProductOffering.objects.all()
    today = timezone.now().date()

    active_offerings = queryset.filter(is_active=True).count()
    expired_offerings = queryset.filter(valid_until__lt=today).count()
    future_offerings = queryset.filter(valid_from__gt=today).count()

    return {
        'total_offerings': queryset.count(),
        'active_offerings': active_offerings,
        'expired_offerings': expired_offerings,
        'future_offerings': future_offerings,
    }


def get_offering_analytics_full(*, base_queryset: QuerySet | None = None) -> dict:
    """
    Full analytics payload for DRF ``analytics`` action.

    ``base_queryset`` allows the ViewSet to pass a filtered queryset (filters/search).
    """
    qs = base_queryset if base_queryset is not None else offerings_base_queryset()
    today = timezone.now().date()

    total_offerings = qs.count()
    active_offerings = qs.filter(is_active=True).count()
    expired_offerings = qs.filter(valid_until__lt=today).count()
    future_offerings = qs.filter(valid_from__gt=today).count()

    by_currency = list(
        qs.values('currency_code')
        .annotate(count=Count('id'), avg_price=Avg('price'))
        .order_by('-count')
    )

    by_product_category = list(
        qs.select_related('product__category')
        .values('product__category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    by_channel = list(
        qs.prefetch_related('channels')
        .values('channels__name')
        .annotate(count=Count('id'))
        .filter(channels__name__isnull=False)
        .order_by('-count')[:10]
    )

    by_market_segment = list(
        qs.prefetch_related('target_segments')
        .values('target_segments__name')
        .annotate(count=Count('id'))
        .filter(target_segments__name__isnull=False)
        .order_by('-count')[:10]
    )

    price_statistics = qs.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price'),
        total_value=Sum('price'),
    )

    duration_statistics = qs.filter(duration_days__isnull=False).aggregate(
        min_duration=Min('duration_days'),
        max_duration=Max('duration_days'),
        avg_duration=Avg('duration_days'),
    )

    top_products = list(
        qs.select_related('product')
        .values('product__name')
        .annotate(offerings_count=Count('id'))
        .order_by('-offerings_count')[:10]
    )

    recent_offerings = ProductOfferingListSerializer(
        qs.order_by('-created_at')[:5],
        many=True,
    ).data

    return {
        'total_offerings': total_offerings,
        'active_offerings': active_offerings,
        'expired_offerings': expired_offerings,
        'future_offerings': future_offerings,
        'by_currency': by_currency,
        'by_product_category': by_product_category,
        'by_channel': by_channel,
        'by_market_segment': by_market_segment,
        'price_statistics': price_statistics,
        'duration_statistics': duration_statistics,
        'top_products': top_products,
        'recent_offerings': recent_offerings,
    }


def get_offerings_list_context(
    *,
    search: str = '',
    is_active: str | None = None,
    product_id=None,
    category_id=None,
    currency_code: str = '',
    validity_status: str = '',
    min_price: str | None = None,
    max_price: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Build paginated list context for the offers CRM index page."""
    queryset = offerings_list_filter(
        offerings_base_queryset(action='list'),
        search=search,
        is_active=is_active,
        product_id=product_id,
        category_id=category_id,
        currency_code=currency_code,
        validity_status=validity_status,
        min_price=min_price,
        max_price=max_price,
    )

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    currency_codes = (
        ProductOffering.objects.values_list('currency_code', flat=True)
        .distinct()
        .order_by('currency_code')
    )

    return {
        'offerings': page_obj.object_list,
        'page_obj': page_obj,
        'search': search,
        'is_active': is_active or '',
        'product_id': product_id,
        'category_id': category_id,
        'currency_code': currency_code,
        'validity_status': validity_status,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'page_size': page_size,
        'overview': get_offering_analytics_overview(),
        'products': Product.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'categories': ProductCategory.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'currency_codes': list(currency_codes),
    }


def get_offering_detail_context(pk) -> dict:
    """Single offering for detail template with product and discount context."""
    offering = get_object_or_404(offerings_base_queryset(action='retrieve'), pk=pk)
    return {
        'offering': offering,
        'product': offering.product,
    }


def get_offering_form_options() -> dict:
    """FK/M2M querysets for offering create/update forms."""
    from world.models import (  # noqa: PLC0415 — lazy import avoids circular deps
        FunctionOrResponsibility,
        Industry,
        MarketSegment,
        Tag,
        WorldDescriptor,
    )

    return {
        'products': Product.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'channels': Channel.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'seats': Seat.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'target_segments': MarketSegment.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'related_industries': Industry.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'related_functions': FunctionOrResponsibility.objects.filter(
            is_active=True
        ).order_by('name')[:_FORM_FK_LIMIT],
        'descriptors': WorldDescriptor.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'tags': Tag.objects.filter(is_active=True).order_by('name')[:_FORM_FK_LIMIT],
    }
