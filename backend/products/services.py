"""
Single write path for Product mutations.

Used by DRF viewsets and Django template views. Accepts scalar fields plus
``category_id``, ``customization_id``, ``duration_days``, and ``*_ids`` lists
for M2M relations (tag entries may be slugs because Tag uses slug as PK).
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Product

# Keys popped from payload before Product construction; values are M2M manager names.
_M2M_ID_KEYS: dict[str, str] = {
    'modalities_ids': 'modalities',
    'target_segments_ids': 'target_segments',
    'related_industries_ids': 'related_industries',
    'related_functions_ids': 'related_functions',
    'related_skills_ids': 'related_skills',
    'descriptors_ids': 'descriptors',
    'tags_ids': 'tags',
    'included_products_ids': 'included_products',
}

_SCALAR_FIELDS = frozenset({
    'name',
    'code',
    'description',
    'canonical_url',
    'base_price',
    'currency_code',
    'is_active',
    'duration',
})


def _coerce_id_list(value: Any) -> list | None:
    """Normalize M2M id lists from forms, JSON, or query strings."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [v for v in value if v not in (None, '')]
    if value == '':
        return []
    return [value]


def _extract_m2m(data: dict, *, for_update: bool) -> dict[str, list | None]:
    """
    Pull M2M id lists out of ``data``.

    On create, missing keys mean empty relations. On update, missing keys mean
    "leave unchanged"; explicit empty list clears the relation.
    """
    extracted: dict[str, list | None] = {}
    for key, relation in _M2M_ID_KEYS.items():
        if key not in data:
            extracted[relation] = None if for_update else []
            continue
        extracted[relation] = _coerce_id_list(data.pop(key))
    return extracted


def _resolve_foreign_keys(data: dict) -> tuple[dict | None, dict | None]:
    """Map category/customization from ids or model instances onto FK ids."""
    category_id = data.pop('category_id', None)
    if category_id is None and 'category' in data:
        category = data.pop('category')
        category_id = category.pk if category else None

    customization_id = data.pop('customization_id', None)
    if customization_id is None and 'customization' in data:
        customization = data.pop('customization')
        customization_id = customization.pk if customization else None

    return category_id, customization_id


def _apply_duration_days(data: dict) -> None:
    """Convert ``duration_days`` (int) to ``duration`` timedelta on ``data``."""
    if 'duration_days' not in data:
        return
    raw = data.pop('duration_days')
    if raw in (None, ''):
        data['duration'] = None
        return
    data['duration'] = timedelta(days=int(raw))


def _validate_unique_code(code: str, *, exclude_pk=None) -> None:
    qs = Product.objects.filter(code=code)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError({'code': 'Ya existe un producto con este código.'})


def _validate_base_price(base_price) -> None:
    if base_price is not None and base_price <= 0:
        raise ValidationError({'base_price': 'El precio debe ser mayor a 0.'})


def _apply_m2m(product: Product, m2m: dict[str, list | None], *, for_update: bool) -> None:
    for relation, ids in m2m.items():
        if for_update and ids is None:
            continue
        getattr(product, relation).set(ids or [])


def _build_scalar_kwargs(data: dict) -> dict:
    return {key: data[key] for key in _SCALAR_FIELDS if key in data}


@transaction.atomic
def create_product(*, data: dict) -> Product:
    """Create a product and assign all M2M relations in one transaction."""
    payload = dict(data)
    m2m = _extract_m2m(payload, for_update=False)
    _apply_duration_days(payload)
    category_id, customization_id = _resolve_foreign_keys(payload)
    scalars = _build_scalar_kwargs(payload)

    code = scalars.get('code')
    if code:
        _validate_unique_code(code)
    if 'base_price' in scalars:
        _validate_base_price(scalars['base_price'])

    product = Product(
        category_id=category_id,
        customization_id=customization_id,
        **scalars,
    )
    product.full_clean()
    product.save()
    _apply_m2m(product, m2m, for_update=False)
    return product


@transaction.atomic
def update_product(product: Product, *, data: dict, partial: bool = False) -> Product:
    """
    Update a product. M2M keys omitted from ``data`` are left unchanged.

    Pass explicit empty lists to clear a relation.
    """
    payload = dict(data)
    had_category = 'category_id' in payload or 'category' in payload
    had_customization = 'customization_id' in payload or 'customization' in payload
    m2m = _extract_m2m(payload, for_update=True)
    _apply_duration_days(payload)
    category_id, customization_id = _resolve_foreign_keys(payload)
    scalars = _build_scalar_kwargs(payload)

    if 'code' in scalars:
        _validate_unique_code(scalars['code'], exclude_pk=product.pk)
    if 'base_price' in scalars:
        _validate_base_price(scalars['base_price'])

    if had_category:
        product.category_id = category_id
    if had_customization:
        product.customization_id = customization_id

    for attr, value in scalars.items():
        setattr(product, attr, value)

    product.full_clean()
    product.save()
    _apply_m2m(product, m2m, for_update=True)
    return product


@transaction.atomic
def delete_product(product: Product) -> None:
    """Hard-delete a product (matches DRF destroy)."""
    product.delete()


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


def product_write_payload_from_request(request, validated_data: dict) -> dict:
    """
    Merge DRF validated scalars with raw ``*_ids`` lists from request.data.

    Used by ProductViewSet perform_create / perform_update.
    """
    payload = dict(validated_data)
    for key in _M2M_ID_KEYS:
        if key in request.data:
            raw = request.data.getlist(key) if hasattr(request.data, 'getlist') else request.data.get(key)
            payload[key] = raw
    if 'category_id' in request.data:
        payload['category_id'] = request.data.get('category_id') or None
    if 'customization_id' in request.data:
        payload['customization_id'] = request.data.get('customization_id') or None
    if 'duration_days' in request.data:
        payload['duration_days'] = request.data.get('duration_days')
    return payload
