"""
Single write path for Campaign and CampaignTouchpoint mutations.

Used by DRF viewsets and Django template views. Campaigns are operator-editable
configuration (not a substrate like interactions). Accepts scalar fields, FK ids
or instances, and M2M via ``*_ids`` lists or model instance lists from DRF/forms.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Campaign, CampaignTouchpoint

# M2M payload keys → model relation names.
_M2M_ID_KEYS: dict[str, str] = {
    'channels_ids': 'channels',
    'target_products_ids': 'target_products',
    'target_categories_ids': 'target_categories',
    'target_offers_ids': 'target_offers',
    'related_industries_ids': 'related_industries',
    'related_functions_ids': 'related_functions',
    'target_segments_ids': 'target_segments',
    'descriptors_ids': 'descriptors',
    'tags_ids': 'tags',
}

# DRF CampaignCreateUpdateSerializer may pass these relation names directly.
_M2M_RELATION_NAMES = frozenset(_M2M_ID_KEYS.values())

_SCALAR_FIELDS = frozenset({
    'name',
    'code',
    'description',
    'start_date',
    'end_date',
    'budget',
    'content_type',
    'funnel_stage',
    'metadata',
    'is_active',
})

_CAMPAIGN_TOUCHPOINT_SCALAR_FIELDS = frozenset({
    'campaign',
    'touchpoint',
    'weight',
    'priority',
    'expected_conversions',
    'budget_allocated',
    'metadata',
})


def validate_campaign_code(code: str, *, exclude_pk=None) -> None:
    """Unique campaign code — shared with serializers and HTML forms."""
    qs = Campaign.objects.filter(code=code)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError({'code': 'Ya existe una campaña con este código.'})


def validate_campaign_dates(
    start_date,
    end_date,
    *,
    budget=None,
) -> None:
    """
    Business rules for campaign dates and budget.

    Shared with ``CampaignCreateUpdateSerializer.validate``.
    """
    errors = {}
    if start_date and end_date and start_date > end_date:
        errors['end_date'] = 'La fecha de inicio no puede ser posterior a la fecha de fin.'
    if budget is not None and budget < 0:
        errors['budget'] = 'El presupuesto no puede ser negativo.'
    if errors:
        raise ValidationError(errors)


def validate_campaign_touchpoint_data(data: dict) -> None:
    """Weight, conversions, and budget must be non-negative when set."""
    errors = {}
    weight = data.get('weight')
    if weight is not None and weight < 0:
        errors['weight'] = 'El peso no puede ser negativo.'
    expected = data.get('expected_conversions')
    if expected is not None and expected < 0:
        errors['expected_conversions'] = 'Las conversiones esperadas no pueden ser negativas.'
    budget = data.get('budget_allocated')
    if budget is not None and budget < 0:
        errors['budget_allocated'] = 'El presupuesto asignado no puede ser negativo.'
    if errors:
        raise ValidationError(errors)


def _coerce_id_list(value: Any) -> list | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            if v in (None, ''):
                continue
            out.append(getattr(v, 'pk', v))
        return out
    if value == '':
        return []
    return [getattr(value, 'pk', value)]


def _extract_m2m(data: dict, *, for_update: bool) -> dict[str, list | None]:
    """
    Pull M2M id lists from ``*_ids`` keys or relation names (DRF instance lists).

    On create, missing keys mean empty relations. On update, missing keys mean
    leave unchanged; explicit empty list clears the relation.
    """
    extracted: dict[str, list | None] = {}
    for key, relation in _M2M_ID_KEYS.items():
        if key in data:
            extracted[relation] = _coerce_id_list(data.pop(key))
            continue
        if relation in data:
            extracted[relation] = _coerce_id_list(data.pop(relation))
            continue
        extracted[relation] = None if for_update else []
    return extracted


def _resolve_fk_id(data: dict, field: str, id_field: str) -> bool:
    """Pop FK instance or id onto ``data[id_field]``; return True if key was present."""
    if id_field in data:
        return True
    if field not in data:
        return False
    value = data.pop(field)
    data[id_field] = value.pk if value else None
    return True


def _apply_m2m(campaign: Campaign, m2m: dict[str, list | None], *, for_update: bool) -> None:
    for relation, ids in m2m.items():
        if for_update and ids is None:
            continue
        getattr(campaign, relation).set(ids or [])


def _build_scalar_kwargs(data: dict, fields: frozenset) -> dict:
    return {key: data[key] for key in fields if key in data}


@transaction.atomic
def create_campaign(*, data: dict) -> Campaign:
    """Create a campaign and assign M2M relations in one transaction."""
    payload = dict(data)
    m2m = _extract_m2m(payload, for_update=False)
    had_division = _resolve_fk_id(payload, 'division', 'division_id')
    had_team = _resolve_fk_id(payload, 'team', 'team_id')
    had_parent = _resolve_fk_id(payload, 'parent', 'parent_id')
    scalars = _build_scalar_kwargs(payload, _SCALAR_FIELDS)

    code = scalars.get('code')
    if code:
        validate_campaign_code(code)
    validate_campaign_dates(
        scalars.get('start_date'),
        scalars.get('end_date'),
        budget=scalars.get('budget'),
    )

    fk_kwargs = {}
    if had_division:
        fk_kwargs['division_id'] = payload.get('division_id')
    if had_team:
        fk_kwargs['team_id'] = payload.get('team_id')
    if had_parent:
        fk_kwargs['parent_id'] = payload.get('parent_id')

    campaign = Campaign(**scalars, **fk_kwargs)
    campaign.full_clean()
    campaign.save()
    _apply_m2m(campaign, m2m, for_update=False)
    return campaign


@transaction.atomic
def update_campaign(
    campaign: Campaign,
    *,
    data: dict,
    partial: bool = False,
) -> Campaign:
    """Update campaign; omitted M2M keys leave relations unchanged."""
    payload = dict(data)
    had_division = _resolve_fk_id(payload, 'division', 'division_id')
    had_team = _resolve_fk_id(payload, 'team', 'team_id')
    had_parent = _resolve_fk_id(payload, 'parent', 'parent_id')
    m2m = _extract_m2m(payload, for_update=True)
    scalars = _build_scalar_kwargs(payload, _SCALAR_FIELDS)

    if 'code' in scalars:
        validate_campaign_code(scalars['code'], exclude_pk=campaign.pk)
    start = scalars.get('start_date', campaign.start_date)
    end = scalars.get('end_date', campaign.end_date)
    budget = scalars.get('budget', campaign.budget)
    if any(k in scalars for k in ('start_date', 'end_date', 'budget')):
        validate_campaign_dates(start, end, budget=budget)

    if had_division:
        campaign.division_id = payload.get('division_id')
    if had_team:
        campaign.team_id = payload.get('team_id')
    if had_parent:
        campaign.parent_id = payload.get('parent_id')

    for attr, value in scalars.items():
        setattr(campaign, attr, value)

    campaign.full_clean()
    campaign.save()
    _apply_m2m(campaign, m2m, for_update=True)
    return campaign


@transaction.atomic
def delete_campaign(campaign: Campaign) -> None:
    """Hard-delete a campaign (matches DRF ModelViewSet destroy)."""
    campaign.delete()


@transaction.atomic
def duplicate_campaign(campaign: Campaign) -> Campaign:
    """
    Deep-copy a campaign: scalars, M2M targets, and CampaignTouchpoint rows.

    Copies start inactive (``is_active=False``) so operators can review before launch.
    """
    stamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_campaign = Campaign.objects.create(
        name=f'{campaign.name} (Copia)',
        code=f'{campaign.code}_copy_{stamp}',
        description=campaign.description,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        budget=campaign.budget,
        content_type=campaign.content_type,
        funnel_stage=campaign.funnel_stage,
        division=campaign.division,
        team=campaign.team,
        metadata=campaign.metadata,
        is_active=False,
    )
    new_campaign.channels.set(campaign.channels.all())
    new_campaign.related_industries.set(campaign.related_industries.all())
    new_campaign.related_functions.set(campaign.related_functions.all())
    new_campaign.target_segments.set(campaign.target_segments.all())
    new_campaign.descriptors.set(campaign.descriptors.all())
    new_campaign.tags.set(campaign.tags.all())
    new_campaign.target_products.set(campaign.target_products.all())
    new_campaign.target_categories.set(campaign.target_categories.all())
    new_campaign.target_offers.set(campaign.target_offers.all())

    for ct in campaign.campaigntouchpoint_set.all():
        CampaignTouchpoint.objects.create(
            campaign=new_campaign,
            touchpoint=ct.touchpoint,
            weight=ct.weight,
            priority=ct.priority,
            expected_conversions=ct.expected_conversions,
            budget_allocated=ct.budget_allocated,
            metadata=ct.metadata,
        )
    return new_campaign


@transaction.atomic
def create_campaign_touchpoint(*, data: dict) -> CampaignTouchpoint:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _CAMPAIGN_TOUCHPOINT_SCALAR_FIELDS)
    validate_campaign_touchpoint_data(scalars)
    link = CampaignTouchpoint(**scalars)
    link.full_clean()
    link.save()
    return link


@transaction.atomic
def update_campaign_touchpoint(
    link: CampaignTouchpoint,
    *,
    data: dict,
    partial: bool = False,
) -> CampaignTouchpoint:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _CAMPAIGN_TOUCHPOINT_SCALAR_FIELDS)
    merged = {f: getattr(link, f) for f in _CAMPAIGN_TOUCHPOINT_SCALAR_FIELDS}
    merged.update(scalars)
    validate_campaign_touchpoint_data(merged)
    for attr, value in scalars.items():
        setattr(link, attr, value)
    link.full_clean()
    link.save()
    return link


@transaction.atomic
def delete_campaign_touchpoint(link: CampaignTouchpoint) -> None:
    link.delete()


def campaign_write_payload_from_request(request, validated_data: dict) -> dict:
    """
    Merge DRF validated scalars/M2M with raw ``*_ids`` lists from request.data.

    Used by ``CampaignViewSet`` perform_create / perform_update.
    """
    payload = dict(validated_data)
    for key in _M2M_ID_KEYS:
        if key in request.data:
            raw = (
                request.data.getlist(key)
                if hasattr(request.data, 'getlist')
                else request.data.get(key)
            )
            payload[key] = raw
    for fk in ('division_id', 'team_id', 'parent_id'):
        if fk in request.data:
            payload[fk] = request.data.get(fk) or None
    return payload


def campaign_touchpoint_write_payload_from_request(request, validated_data: dict) -> dict:
    """Pass-through for touchpoint junction writes (no extra M2M on request)."""
    return dict(validated_data)
