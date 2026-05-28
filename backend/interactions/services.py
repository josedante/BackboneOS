"""
Single write path for Interaction and Touchpoint mutations.

Used by DRF viewsets and Django template views. Lookup catalogs (Medium, Channel,
etc.) still use serializer.save() directly until Phase 2b HTML admin.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Interaction, Touchpoint

_INTERACTION_SCALAR_FIELDS = frozenset({
    'person',
    'organization',
    'touchpoint',
    'action',
    'agent',
    'representative',
    'product',
    'occurred_at',
    'duration_seconds',
    'session_id',
    'latitude',
    'longitude',
    'referrer_url',
    'user_agent',
    'ip_address',
    'source',
    'payload',
    'metadata',
    'is_active',
})

_TOUCHPOINT_SCALAR_FIELDS = frozenset({
    'name',
    'code',
    'description',
    'url',
    'external_id',
    'channel',
    'medium',
    'touchpoint_type',
    'content_type',
    'product',
    'assigned_staff',
    'parent',
    'is_active',
})

# World app M2Ms — supported for API payloads; MVP HTML forms omit them.
_TOUCHPOINT_M2M_KEYS: dict[str, str] = {
    'related_industries_ids': 'related_industries',
    'related_functions_ids': 'related_functions',
    'related_skills_ids': 'related_skills',
    'related_descriptors_ids': 'related_descriptors',
}


def validate_interaction_entities(data: dict) -> None:
    """
  At least one of person, organization, or agent must be set.

  B2B: organization may be set with person; B2C: organization often empty.
  Mirrors ``InteractionCreateUpdateSerializer.validate``.
    """
    if not data.get('person') and not data.get('organization') and not data.get('agent'):
        raise ValidationError(
            'Debe especificar al menos una persona, organización o agente.'
        )


def apply_interaction_defaults(interaction: Interaction) -> None:
    """
    Apply model ``clean()`` side effects: infer person/org from agent,
    representative from touchpoint, product from touchpoint.
    """
    interaction.full_clean()


def _build_scalar_kwargs(data: dict, fields: frozenset) -> dict:
    return {key: data[key] for key in fields if key in data}


def _coerce_id_list(value: Any) -> list | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [v for v in value if v not in (None, '')]
    if value == '':
        return []
    return [value]


def _extract_touchpoint_m2m(data: dict, *, for_update: bool) -> dict[str, list | None]:
    """Pull M2M id lists from ``*_ids`` keys or DRF validated model instances."""
    extracted: dict[str, list | None] = {}
    for key, relation in _TOUCHPOINT_M2M_KEYS.items():
        if key in data:
            extracted[relation] = _coerce_id_list(data.pop(key))
            continue
        if relation in data:
            value = data.pop(relation)
            if value is None:
                extracted[relation] = None if for_update else []
            else:
                extracted[relation] = [obj.pk for obj in value]
            continue
        extracted[relation] = None if for_update else []
    return extracted


def _apply_touchpoint_m2m(touchpoint: Touchpoint, m2m: dict[str, list | None]) -> None:
    for relation, ids in m2m.items():
        if ids is None:
            continue
        getattr(touchpoint, relation).set(ids)


def interaction_write_payload_from_request(request_data: dict, validated_data: dict) -> dict:
    """Merge DRF validated_data with raw request body (FK ids as strings)."""
    payload = dict(validated_data)
    for key in _INTERACTION_SCALAR_FIELDS:
        if key in request_data and key not in payload:
            payload[key] = request_data[key]
    return payload


@transaction.atomic
def create_interaction(*, data: dict) -> Interaction:
    payload = dict(data)
    validate_interaction_entities(payload)
    scalars = _build_scalar_kwargs(payload, _INTERACTION_SCALAR_FIELDS)
    interaction = Interaction(**scalars)
    apply_interaction_defaults(interaction)
    interaction.save()
    return interaction


@transaction.atomic
def update_interaction(interaction: Interaction, *, data: dict, partial: bool = False) -> Interaction:
    payload = dict(data)
    if partial:
        for field in _INTERACTION_SCALAR_FIELDS:
            if field in payload:
                setattr(interaction, field, payload[field])
    else:
        scalars = _build_scalar_kwargs(payload, _INTERACTION_SCALAR_FIELDS)
        for key, value in scalars.items():
            setattr(interaction, key, value)

    validate_interaction_entities(
        {
            'person': interaction.person,
            'organization': interaction.organization,
            'agent': interaction.agent,
        }
    )
    apply_interaction_defaults(interaction)
    interaction.save()
    return interaction


def delete_interaction(interaction: Interaction) -> None:
    """Hard-delete (matches current DRF destroy on InteractionViewSet)."""
    interaction.delete()


@transaction.atomic
def create_touchpoint(*, data: dict) -> Touchpoint:
    payload = dict(data)
    m2m = _extract_touchpoint_m2m(payload, for_update=False)
    scalars = _build_scalar_kwargs(payload, _TOUCHPOINT_SCALAR_FIELDS)
    touchpoint = Touchpoint(**scalars)
    touchpoint.full_clean()
    touchpoint.save()
    _apply_touchpoint_m2m(touchpoint, m2m)
    return touchpoint


@transaction.atomic
def update_touchpoint(
    touchpoint: Touchpoint, *, data: dict, partial: bool = False
) -> Touchpoint:
    payload = dict(data)
    m2m = _extract_touchpoint_m2m(payload, for_update=True)
    if partial:
        scalars = _build_scalar_kwargs(payload, _TOUCHPOINT_SCALAR_FIELDS)
        for key, value in scalars.items():
            setattr(touchpoint, key, value)
    else:
        scalars = _build_scalar_kwargs(payload, _TOUCHPOINT_SCALAR_FIELDS)
        for key, value in scalars.items():
            setattr(touchpoint, key, value)
    touchpoint.full_clean()
    touchpoint.save()
    _apply_touchpoint_m2m(touchpoint, m2m)
    return touchpoint


def delete_touchpoint(touchpoint: Touchpoint) -> None:
    """Hard-delete (matches current DRF destroy)."""
    touchpoint.delete()


def validate_interaction_entities_for_drf(data: dict) -> None:
    """Raise DRF ValidationError for serializer integration."""
    try:
        validate_interaction_entities(data)
    except ValidationError as exc:
        raise DRFValidationError(exc.messages) from exc
