"""
Read-only query layer for the campaigns app.

Consumed by DRF viewsets and Django template views. Mutations belong in
``services.py`` — never fetch data via HTTP to the REST API from templates.
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, QuerySet, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from interactions.models import Channel, Touchpoint
from offers.models import ProductOffering
from our_institution.models import Division, Team
from products.models import Product, ProductCategory

from .models import Campaign, CampaignTouchpoint

_FORM_FK_LIMIT = 500


def campaigns_active_queryset(*, action: str = 'list') -> QuerySet:
    """
    Active campaigns with relations prefetched (DRF + HTML base queryset).

    ``action='retrieve'`` adds touchpoint links and product targets for detail.
    """
    qs = (
        Campaign.objects.select_related('division', 'team', 'parent')
        .filter(is_active=True)
    )
    if action == 'list':
        return qs.prefetch_related(
            'channels',
            'target_segments',
            'subcampaigns',
        )
    if action == 'retrieve':
        return qs.prefetch_related(
            'channels',
            'related_industries',
            'related_functions',
            'target_segments',
            'descriptors',
            'tags',
            'target_products',
            'target_categories',
            'target_offers',
            'subcampaigns',
            'campaigntouchpoint_set__touchpoint',
        )
    return qs


def campaign_touchpoints_queryset() -> QuerySet:
    """All campaign–touchpoint links for list/detail HTML."""
    return CampaignTouchpoint.objects.select_related(
        'campaign',
        'touchpoint',
        'touchpoint__channel',
    ).order_by('campaign__name', 'priority', 'touchpoint__name')


def campaigns_list_filter(
    qs: QuerySet,
    *,
    search: str = '',
    content_type: str = '',
    funnel_stage: str = '',
    division_id=None,
    status: str = '',
) -> QuerySet:
    """
    Apply HTML list filters.

    ``status`` mirrors common API slices:
      - ``active_now``: started and not ended (or open-ended)
      - ``scheduled``: start_date in the future
      - ``finished``: end_date before today
    """
    if search:
        term = search.strip()
        qs = qs.filter(
            Q(name__icontains=term)
            | Q(code__icontains=term)
            | Q(description__icontains=term)
            | Q(division__name__icontains=term)
            | Q(team__name__icontains=term)
        ).distinct()

    if content_type:
        qs = qs.filter(content_type=content_type)
    if funnel_stage:
        qs = qs.filter(funnel_stage=funnel_stage)
    if division_id:
        qs = qs.filter(division_id=division_id)

    today = timezone.now().date()
    if status == 'active_now':
        qs = qs.filter(
            is_active=True,
            start_date__lte=today,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
    elif status == 'scheduled':
        qs = qs.filter(is_active=True, start_date__gt=today)
    elif status == 'finished':
        qs = qs.filter(end_date__lt=today)

    return qs


def campaign_touchpoints_list_filter(
    qs: QuerySet,
    *,
    search: str = '',
    campaign_id=None,
) -> QuerySet:
    if search:
        term = search.strip()
        qs = qs.filter(
            Q(campaign__name__icontains=term)
            | Q(campaign__code__icontains=term)
            | Q(touchpoint__name__icontains=term)
            | Q(touchpoint__code__icontains=term)
        )
    if campaign_id:
        qs = qs.filter(campaign_id=campaign_id)
    return qs


def get_campaign_status_label(campaign: Campaign) -> str:
    """Human-readable lifecycle label for templates."""
    today = timezone.now().date()
    if not campaign.is_active:
        return 'inactiva'
    if campaign.start_date and campaign.start_date > today:
        return 'programada'
    if campaign.is_active_now:
        return 'activa'
    return 'finalizada'


def get_campaign_analytics_full() -> dict:
    """
    Full analytics payload for DRF ``CampaignViewSet.analytics``.

    Includes inactive campaigns (matches legacy viewset behavior).
    """
    queryset = Campaign.objects.all()
    today = timezone.now().date()

    total_campaigns = queryset.count()
    active_campaigns = (
        queryset.filter(
            is_active=True,
            start_date__lte=today,
        )
        .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        .count()
    )
    scheduled_campaigns = queryset.filter(
        is_active=True,
        start_date__gt=today,
    ).count()
    finished_campaigns = queryset.filter(end_date__lt=today).count()

    by_division = list(
        queryset.values('division__name')
        .annotate(
            count=Count('id'),
            total_budget=Sum('budget'),
            avg_budget=Avg('budget'),
        )
        .order_by('-count')
    )
    by_team = list(
        queryset.values('team__name')
        .annotate(count=Count('id'), total_budget=Sum('budget'))
        .order_by('-count')
    )
    by_channel = list(
        queryset.values('channels__name')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')
    )
    by_industry = list(
        queryset.values('related_industries__name')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')
    )
    by_segment = list(
        queryset.values('target_segments__name')
        .annotate(count=Count('id', distinct=True))
        .order_by('-count')
    )

    budget_stats = queryset.filter(budget__gt=0).aggregate(
        total_budget=Sum('budget'),
        avg_budget=Avg('budget'),
        min_budget=Min('budget'),
        max_budget=Max('budget'),
    )

    campaigns_with_dates = queryset.filter(
        start_date__isnull=False,
        end_date__isnull=False,
    )
    duration_stats = {
        'total_campaigns_with_duration': campaigns_with_dates.count(),
        'avg_duration_days': 0,
        'min_duration_days': 0,
        'max_duration_days': 0,
    }
    if campaigns_with_dates.exists():
        durations = [(c.end_date - c.start_date).days for c in campaigns_with_dates]
        duration_stats.update(
            {
                'avg_duration_days': sum(durations) / len(durations),
                'min_duration_days': min(durations),
                'max_duration_days': max(durations),
            }
        )

    top_campaigns = list(
        queryset.filter(budget__gt=0)
        .order_by('-budget')[:5]
        .values('id', 'name', 'code', 'budget', 'start_date', 'end_date')
    )
    recent_campaigns = list(
        queryset.filter(is_active=True)
        .order_by('-created_at')[:5]
        .values('id', 'name', 'code', 'start_date', 'created_at')
    )
    upcoming_campaigns = list(
        queryset.filter(is_active=True, start_date__gt=today)
        .order_by('start_date')[:5]
        .values('id', 'name', 'code', 'start_date')
    )

    return {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'scheduled_campaigns': scheduled_campaigns,
        'finished_campaigns': finished_campaigns,
        'by_division': by_division,
        'by_team': by_team,
        'by_channel': by_channel,
        'by_industry': by_industry,
        'by_segment': by_segment,
        'budget_statistics': budget_stats,
        'duration_statistics': duration_stats,
        'top_campaigns': top_campaigns,
        'recent_campaigns': recent_campaigns,
        'upcoming_campaigns': upcoming_campaigns,
    }


def get_campaign_analytics_overview() -> dict:
    """
    Summary metrics for the campaigns hub (subset of DRF ``analytics`` action).

    Includes inactive campaigns in totals where the API analytics does.
    """
    queryset = Campaign.objects.all()
    today = timezone.now().date()

    active_campaigns = queryset.filter(
        is_active=True,
        start_date__lte=today,
    ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today)).count()

    scheduled_campaigns = queryset.filter(
        is_active=True,
        start_date__gt=today,
    ).count()

    finished_campaigns = queryset.filter(end_date__lt=today).count()

    budget_stats = queryset.filter(budget__gt=0).aggregate(
        total_budget=Sum('budget'),
        avg_budget=Avg('budget'),
    )

    return {
        'total_campaigns': queryset.count(),
        'active_campaigns': active_campaigns,
        'scheduled_campaigns': scheduled_campaigns,
        'finished_campaigns': finished_campaigns,
        'total_budget': budget_stats['total_budget'] or 0,
        'avg_budget': budget_stats['avg_budget'] or 0,
    }


def get_campaigns_list_context(
    *,
    search: str = '',
    content_type: str = '',
    funnel_stage: str = '',
    division_id=None,
    status: str = '',
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Paginated campaign rows for the hub campaigns tab."""
    queryset = campaigns_list_filter(
        campaigns_active_queryset(action='list'),
        search=search,
        content_type=content_type,
        funnel_stage=funnel_stage,
        division_id=division_id,
        status=status,
    ).order_by('-start_date', 'name')

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    return {
        'campaigns': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'search': search,
        'content_type': content_type,
        'funnel_stage': funnel_stage,
        'division_id': division_id,
        'status': status,
        'page_size': page_size,
        'content_type_choices': Campaign._meta.get_field('content_type').choices,
        'funnel_stage_choices': Campaign.FUNNEL_STAGES,
        'divisions': Division.objects.filter(is_active=True).order_by('name')[:_FORM_FK_LIMIT],
    }


def get_campaign_touchpoints_list_context(
    *,
    search: str = '',
    campaign_id=None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Paginated campaign–touchpoint links for the hub touchpoints tab."""
    queryset = campaign_touchpoints_list_filter(
        campaign_touchpoints_queryset(),
        search=search,
        campaign_id=campaign_id,
    )
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    return {
        'campaign_touchpoints': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'search': search,
        'campaign_id': campaign_id,
        'page_size': page_size,
        'filter_campaigns': Campaign.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
    }


def get_campaigns_hub_context(
    *,
    tab: str = 'campaigns',
    search: str = '',
    content_type: str = '',
    funnel_stage: str = '',
    division_id=None,
    status: str = '',
    campaign_id=None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Tabbed list context for ``/campaigns/``.

    Only paginates the active tab (same pattern as interactions/entities hubs).
    """
    if tab not in ('campaigns', 'touchpoints'):
        tab = 'campaigns'

    campaigns_qs = campaigns_list_filter(
        campaigns_active_queryset(action='list'),
        search=search,
        content_type=content_type,
        funnel_stage=funnel_stage,
        division_id=division_id,
        status=status,
    )
    touchpoints_qs = campaign_touchpoints_list_filter(
        campaign_touchpoints_queryset(),
        search=search,
        campaign_id=campaign_id,
    )

    campaigns_count = campaigns_qs.count()
    touchpoints_count = touchpoints_qs.count()

    if tab == 'campaigns':
        list_ctx = get_campaigns_list_context(
            search=search,
            content_type=content_type,
            funnel_stage=funnel_stage,
            division_id=division_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        touchpoint_rows = []
        touchpoint_page_obj = None
    else:
        list_ctx = {}
        tp_ctx = get_campaign_touchpoints_list_context(
            search=search,
            campaign_id=campaign_id,
            page=page,
            page_size=page_size,
        )
        touchpoint_rows = tp_ctx['campaign_touchpoints']
        touchpoint_page_obj = tp_ctx['page_obj']

    return {
        'tab': tab,
        'search': search,
        'page_size': page_size,
        'campaigns_count': campaigns_count,
        'touchpoints_count': touchpoints_count,
        'analytics': get_campaign_analytics_overview(),
        'campaigns': list_ctx.get('campaigns', []) if tab == 'campaigns' else [],
        'page_obj': list_ctx.get('page_obj') if tab == 'campaigns' else touchpoint_page_obj,
        'campaign_touchpoints': touchpoint_rows,
        'content_type': content_type,
        'funnel_stage': funnel_stage,
        'division_id': division_id,
        'status': status,
        'campaign_id': campaign_id,
        'content_type_choices': Campaign._meta.get_field('content_type').choices,
        'funnel_stage_choices': Campaign.FUNNEL_STAGES,
        'divisions': Division.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'filter_campaigns': Campaign.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
    }


def get_campaign_detail_context(pk) -> dict:
    """Single campaign for detail template: subcampaigns, links, status."""
    campaign = get_object_or_404(campaigns_active_queryset(action='retrieve'), pk=pk)
    subcampaigns = campaign.subcampaigns.filter(is_active=True).order_by('name')
    links = campaign.campaigntouchpoint_set.select_related('touchpoint').order_by(
        '-priority', 'touchpoint__name'
    )
    return {
        'campaign': campaign,
        'status_label': get_campaign_status_label(campaign),
        'subcampaigns': subcampaigns,
        'campaign_touchpoints': links,
        'target_summary': campaign.get_target_summary(),
    }


def get_campaign_form_options() -> dict:
    """FK/M2M querysets for campaign create/update forms."""
    return {
        'divisions': Division.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'teams': Team.objects.filter(is_active=True).select_related('division').order_by(
            'name'
        )[:_FORM_FK_LIMIT],
        'parent_campaigns': Campaign.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'channels': Channel.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'products': Product.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'categories': ProductCategory.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'offers': ProductOffering.objects.filter(is_active=True).select_related(
            'product'
        ).order_by('name')[:_FORM_FK_LIMIT],
        'content_type_choices': Campaign._meta.get_field('content_type').choices,
        'funnel_stage_choices': Campaign.FUNNEL_STAGES,
    }


def get_campaign_touchpoint_detail_context(pk) -> dict:
    link = get_object_or_404(campaign_touchpoints_queryset(), pk=pk)
    return {'campaign_touchpoint': link, 'link': link}


def get_campaign_touchpoint_form_options() -> dict:
    return {
        'campaigns': Campaign.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'touchpoints': Touchpoint.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
    }
