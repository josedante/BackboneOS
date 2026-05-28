"""
Read-only query layer for the interactions app.

Consumed by DRF viewsets and Django template views. Mutations belong in
``services.py`` — never fetch data via HTTP to the REST API from templates.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, QuerySet
from django.shortcuts import get_object_or_404

from products.models import Product

from .models import (
    Action,
    Channel,
    Interaction,
    Medium,
    Touchpoint,
    TouchpointType,
)

User = get_user_model()

# Cap FK dropdown querysets on touchpoint config forms — can grow large.
_FORM_FK_LIMIT = 500


def interactions_base_queryset() -> QuerySet:
    """Interactions with relations prefetched (DRF base queryset — includes inactive)."""
    return Interaction.objects.select_related(
        'person',
        'organization',
        'touchpoint',
        'touchpoint__channel',
        'touchpoint__medium',
        'action',
        'agent',
        'representative',
        'product',
    ).order_by('-occurred_at', '-created_at')


def interactions_active_queryset() -> QuerySet:
    """Active-only interactions for HTML lists and analytics."""
    return interactions_base_queryset().filter(is_active=True)


def touchpoints_base_queryset() -> QuerySet:
    """Touchpoints with relations prefetched (DRF base queryset)."""
    return Touchpoint.objects.select_related(
        'touchpoint_type',
        'assigned_staff',
        'product',
        'channel',
        'medium',
        'parent',
    ).prefetch_related(
        'related_industries',
        'related_functions',
        'related_skills',
        'related_descriptors',
    ).order_by('name')


def touchpoints_active_queryset() -> QuerySet:
    """Active-only touchpoints for HTML."""
    return touchpoints_base_queryset().filter(is_active=True)


def interactions_list_filter(
    qs: QuerySet,
    *,
    search: str = '',
    touchpoint_id=None,
    action_id=None,
    channel_id=None,
    start_date=None,
    end_date=None,
    has_location: str | None = None,
    has_duration: str | None = None,
) -> QuerySet:
    """
    Apply HTML/DRF list filters to an interactions queryset.

    ``has_location`` / ``has_duration`` use string query params ``'true'`` / ``'false'``
    to mirror ``InteractionViewSet.get_queryset``.
    """
    if search:
        term = search.strip()
        qs = qs.filter(
            Q(person__first_name__icontains=term)
            | Q(person__last_name__icontains=term)
            | Q(organization__name__icontains=term)
            | Q(source__icontains=term)
            | Q(session_id__icontains=term)
            | Q(user_agent__icontains=term)
            | Q(ip_address__icontains=term)
        ).distinct()

    if touchpoint_id:
        qs = qs.filter(touchpoint_id=touchpoint_id)
    if action_id:
        qs = qs.filter(action_id=action_id)
    if channel_id:
        qs = qs.filter(touchpoint__channel_id=channel_id)
    if start_date:
        qs = qs.filter(occurred_at__gte=start_date)
    if end_date:
        qs = qs.filter(occurred_at__lte=end_date)

    if has_location == 'true':
        qs = qs.filter(latitude__isnull=False, longitude__isnull=False)
    elif has_location == 'false':
        qs = qs.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))

    if has_duration == 'true':
        qs = qs.filter(duration_seconds__gt=0)
    elif has_duration == 'false':
        qs = qs.filter(Q(duration_seconds__isnull=True) | Q(duration_seconds=0))

    return qs


def touchpoints_list_filter(
    qs: QuerySet,
    *,
    search: str = '',
    channel_id=None,
    medium_id=None,
    touchpoint_type_id=None,
    content_type: str = '',
) -> QuerySet:
    """Apply text and FK filters for touchpoint list tab."""
    if search:
        term = search.strip()
        qs = qs.filter(
            Q(name__icontains=term)
            | Q(code__icontains=term)
            | Q(description__icontains=term)
            | Q(url__icontains=term)
        )
    if channel_id:
        qs = qs.filter(channel_id=channel_id)
    if medium_id:
        qs = qs.filter(medium_id=medium_id)
    if touchpoint_type_id:
        qs = qs.filter(touchpoint_type_id=touchpoint_type_id)
    if content_type:
        qs = qs.filter(content_type=content_type)
    return qs


def interaction_entity_display(interaction: Interaction) -> str:
    """Human label for list rows (person, org, or anonymous)."""
    person = interaction.resolved_person
    if person:
        return person.full_name
    org = interaction.resolved_organization
    if org:
        return org.name
    return 'Anónimo'


def touchpoint_recent_interactions(touchpoint: Touchpoint, *, limit: int = 10) -> list[Interaction]:
    """Recent interactions for touchpoint detail (no HTTP to nested API action)."""
    return list(
        interactions_active_queryset()
        .filter(touchpoint=touchpoint)
        [:limit]
    )


def get_interaction_analytics_summary() -> dict:
    """
    Dashboard metrics for interactions list header.

    Logic extracted from ``InteractionViewSet.analytics`` for reuse in HTML and API.
    """
    queryset = interactions_active_queryset()
    total_interactions = queryset.count()
    unique_sessions = (
        queryset.exclude(session_id='').values('session_id').distinct().count()
    )
    by_channel = (
        queryset.filter(touchpoint__channel__isnull=False)
        .values('touchpoint__channel__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    by_action = (
        queryset.values('action__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    avg_duration = queryset.filter(duration_seconds__gt=0).aggregate(
        avg_duration=Avg('duration_seconds')
    )
    return {
        'total_interactions': total_interactions,
        'unique_sessions': unique_sessions,
        'avg_duration_seconds': avg_duration['avg_duration'],
        'by_channel': list(by_channel),
        'by_action': list(by_action),
    }


def get_interactions_hub_context(
    *,
    tab: str = 'interactions',
    search: str = '',
    page: int = 1,
    page_size: int = 20,
    touchpoint_id=None,
    action_id=None,
    channel_id=None,
    medium_id=None,
    touchpoint_type_id=None,
    content_type: str = '',
) -> dict:
    """
    Tabbed list context for ``/interactions/``.

    Only paginates the active tab to avoid double OFFSET work (entities pattern).
    """
    if tab not in ('interactions', 'touchpoints'):
        tab = 'interactions'

    interactions_qs = interactions_list_filter(
        interactions_active_queryset(),
        search=search,
        touchpoint_id=touchpoint_id,
        action_id=action_id,
        channel_id=channel_id,
    )
    touchpoints_qs = touchpoints_list_filter(
        touchpoints_active_queryset(),
        search=search,
        channel_id=channel_id,
        medium_id=medium_id,
        touchpoint_type_id=touchpoint_type_id,
        content_type=content_type,
    )

    interactions_count = interactions_qs.count()
    touchpoints_count = touchpoints_qs.count()

    interaction_rows = []
    interactions_page_obj = None
    touchpoints_page_obj = None

    if tab == 'interactions':
        paginator = Paginator(interactions_qs, page_size)
        interactions_page_obj = paginator.get_page(page)
        for interaction in interactions_page_obj.object_list:
            interaction_rows.append(
                {
                    'interaction': interaction,
                    'entity_display': interaction_entity_display(interaction),
                }
            )
    else:
        paginator = Paginator(touchpoints_qs, page_size)
        touchpoints_page_obj = paginator.get_page(page)

    filter_options = get_interactions_list_filter_options()

    return {
        'tab': tab,
        'search': search,
        'page': page,
        'page_size': page_size,
        'touchpoint_id': touchpoint_id,
        'action_id': action_id,
        'channel_id': channel_id,
        'medium_id': medium_id,
        'touchpoint_type_id': touchpoint_type_id,
        'content_type': content_type,
        'interactions_count': interactions_count,
        'touchpoints_count': touchpoints_count,
        'interactions_page_obj': interactions_page_obj,
        'touchpoints_page_obj': touchpoints_page_obj,
        'interaction_rows': interaction_rows,
        'analytics': get_interaction_analytics_summary(),
        'filter_options': filter_options,
    }


def get_interactions_list_filter_options() -> dict:
    """Small FK lists for hub filter dropdowns."""
    return {
        'touchpoints': Touchpoint.objects.filter(is_active=True).order_by('name')[:200],
        'actions': Action.objects.filter(is_active=True).order_by('name')[:200],
        'channels': Channel.objects.filter(is_active=True).order_by('name'),
        'mediums': Medium.objects.filter(is_active=True).order_by('name'),
        'touchpoint_types': TouchpointType.objects.filter(is_active=True).order_by('name'),
        'content_type_choices': Touchpoint.CONTENT_TYPE_CHOICES,
    }


def get_interaction_detail_context(pk) -> dict:
    """Read-only interaction detail (back-office inspection; no edit form)."""
    interaction = get_object_or_404(interactions_active_queryset(), pk=pk)
    return {
        'interaction': interaction,
        'entity_display': interaction_entity_display(interaction),
    }


def get_entity_interactions_timeline(
    *,
    person=None,
    organization=None,
    limit: int = 25,
) -> list[Interaction]:
    """
    Chronological interactions for a Person or Organization (entities detail pages).

    This is the high-value cross-cutting read: "everything this customer has done".
    Matches both directly-attributed interactions and those resolved via the agent
    (``resolved_person`` / ``resolved_organization`` are computed, so we OR the agent
    relations to mirror them at the query level).
    """
    qs = interactions_active_queryset()
    if person is not None:
        qs = qs.filter(
            Q(person=person)
            | Q(agent__represents_person=person)
            | Q(agent__operated_by=person)
        )
    elif organization is not None:
        qs = qs.filter(
            Q(organization=organization)
            | Q(agent__represents_organization=organization)
        )
    else:
        return []
    return list(qs.distinct()[:limit])


def get_touchpoint_detail_context(pk) -> dict:
    """Touchpoint detail with recent interactions sidebar and edit form options."""
    touchpoint = get_object_or_404(touchpoints_active_queryset(), pk=pk)
    return {
        'touchpoint': touchpoint,
        'recent_interactions': touchpoint_recent_interactions(touchpoint),
        'form_options': get_touchpoint_form_options(),
    }


def get_touchpoint_form_options() -> dict:
    """FK querysets for touchpoint HTML forms."""
    return {
        'channels': Channel.objects.filter(is_active=True).order_by('name'),
        'mediums': Medium.objects.filter(is_active=True).order_by('name'),
        'touchpoint_types': TouchpointType.objects.filter(is_active=True).order_by('name'),
        'products': Product.objects.filter(is_active=True).order_by('name')[:_FORM_FK_LIMIT],
        'staff_users': User.objects.filter(is_active=True).order_by('username')[:200],
        'parent_touchpoints': Touchpoint.objects.filter(is_active=True).order_by('name')[
            :_FORM_FK_LIMIT
        ],
        'content_type_choices': Touchpoint.CONTENT_TYPE_CHOICES,
    }


def paginated_touchpoint_interactions(
    touchpoint: Touchpoint,
    *,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    Paginated interactions for a touchpoint (DRF ``touchpoints/{id}/interactions`` action).
    """
    qs = interactions_active_queryset().filter(touchpoint=touchpoint)
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    return {
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'page_obj': page_obj,
        'results': list(page_obj.object_list),
    }
