"""
Single write path for ProductOffering mutations.

Used by DRF viewsets and Django template views. Offers are operator-editable
commercial configuration (not a substrate). Accepts scalar fields, FK ids or
instances, and M2M via ``*_ids`` lists or model instance lists from DRF/forms.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ProductOffering

# M2M payload keys → model relation names.
_M2M_ID_KEYS: dict[str, str] = {
    'channels_ids': 'channels',
    'seats_ids': 'seats',
    'target_segments_ids': 'target_segments',
    'related_industries_ids': 'related_industries',
    'related_functions_ids': 'related_functions',
    'descriptors_ids': 'descriptors',
    'tags_ids': 'tags',
}

_SCALAR_FIELDS = frozenset({
    'name',
    'code',
    'description',
    'price',
    'currency_code',
    'valid_from',
    'valid_until',
    'auto_renew',
    'duration_days',
    'landing_url',
    'metadata',
    'is_active',
})


def validate_offering_code(code: str, *, exclude_pk=None) -> None:
    """Unique offering code — shared with serializers and HTML forms."""
    qs = ProductOffering.objects.filter(code=code)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError({'code': 'Ya existe una oferta con este código.'})


def validate_offering_dates(valid_from, valid_until) -> None:
    """Date range must not have end before start (aligns with model ``clean()``)."""
    if valid_from and valid_until and valid_from > valid_until:
        raise ValidationError({
            'valid_until': 'La fecha de inicio no puede ser posterior a la fecha de fin.',
        })


def validate_offering_price(price) -> None:
    """Commercial price must be strictly positive."""
    if price is not None and price <= 0:
        raise ValidationError({'price': 'El precio debe ser mayor a cero.'})


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


def _resolve_product_id(data: dict) -> bool:
    """Pop product instance or id onto ``product_id``; return True if key was present."""
    if 'product_id' in data:
        return True
    if 'product' not in data:
        return False
    value = data.pop('product')
    data['product_id'] = value.pk if value else None
    return True


def _apply_m2m(
    offering: ProductOffering,
    m2m: dict[str, list | None],
    *,
    for_update: bool,
) -> None:
    for relation, ids in m2m.items():
        if for_update and ids is None:
            continue
        getattr(offering, relation).set(ids or [])


def _build_scalar_kwargs(data: dict) -> dict:
    return {key: data[key] for key in _SCALAR_FIELDS if key in data}


@transaction.atomic
def create_offering(*, data: dict) -> ProductOffering:
    """Create an offering and assign M2M relations in one transaction."""
    payload = dict(data)
    m2m = _extract_m2m(payload, for_update=False)
    had_product = _resolve_product_id(payload)
    scalars = _build_scalar_kwargs(payload)

    code = scalars.get('code')
    if code:
        validate_offering_code(code)
    validate_offering_dates(scalars.get('valid_from'), scalars.get('valid_until'))
    if 'price' in scalars:
        validate_offering_price(scalars['price'])

    fk_kwargs = {}
    if had_product:
        fk_kwargs['product_id'] = payload.get('product_id')
    elif not payload.get('product_id'):
        raise ValidationError({'product': 'El producto es obligatorio.'})

    offering = ProductOffering(**scalars, **fk_kwargs)
    offering.full_clean()
    offering.save()
    _apply_m2m(offering, m2m, for_update=False)
    return offering


@transaction.atomic
def update_offering(
    offering: ProductOffering,
    *,
    data: dict,
    partial: bool = False,
) -> ProductOffering:
    """Update offering; omitted M2M keys leave relations unchanged."""
    payload = dict(data)
    had_product = _resolve_product_id(payload)
    m2m = _extract_m2m(payload, for_update=True)
    scalars = _build_scalar_kwargs(payload)

    if 'code' in scalars:
        validate_offering_code(scalars['code'], exclude_pk=offering.pk)

    start = scalars.get('valid_from', offering.valid_from)
    end = scalars.get('valid_until', offering.valid_until)
    if any(k in scalars for k in ('valid_from', 'valid_until')):
        validate_offering_dates(start, end)
    if 'price' in scalars:
        validate_offering_price(scalars['price'])

    if had_product:
        offering.product_id = payload.get('product_id')

    for attr, value in scalars.items():
        setattr(offering, attr, value)

    offering.full_clean()
    offering.save()
    _apply_m2m(offering, m2m, for_update=True)
    return offering


@transaction.atomic
def delete_offering(offering: ProductOffering) -> None:
    """Hard-delete an offering (matches DRF ModelViewSet destroy)."""
    offering.delete()


@transaction.atomic
def duplicate_offering(offering: ProductOffering) -> ProductOffering:
    """
    Deep-copy an offering including M2M targeting relations.

    Copy is created inactive so operators can adjust dates/code before publishing.
    """
    stamp = int(timezone.now().timestamp())
    new_offering = ProductOffering.objects.create(
        name=f'{offering.name} (Copia)',
        code=f'{offering.code}_copy_{stamp}',
        description=offering.description,
        product=offering.product,
        price=offering.price,
        currency_code=offering.currency_code,
        valid_from=offering.valid_from,
        valid_until=offering.valid_until,
        auto_renew=offering.auto_renew,
        duration_days=offering.duration_days,
        landing_url=offering.landing_url,
        metadata=offering.metadata,
        is_active=False,
    )
    new_offering.channels.set(offering.channels.all())
    new_offering.seats.set(offering.seats.all())
    new_offering.target_segments.set(offering.target_segments.all())
    new_offering.related_industries.set(offering.related_industries.all())
    new_offering.related_functions.set(offering.related_functions.all())
    new_offering.descriptors.set(offering.descriptors.all())
    new_offering.tags.set(offering.tags.all())
    return new_offering


def offering_write_payload_from_request(request, validated_data: dict) -> dict:
    """
    Merge DRF validated scalars/M2M with raw ``*_ids`` lists from request.data.

    Used by ``ProductOfferingViewSet`` perform_create / perform_update.
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
    if 'product_id' in request.data:
        payload['product_id'] = request.data.get('product_id') or None
    return payload
