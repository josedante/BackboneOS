"""
Single write path for Person, Organization, and IndividualProfile mutations.

Used by DRF viewsets and Django template views. Validation helpers are shared
with serializers to prevent drift between API and HTML forms.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import IndividualProfile, Organization, Person

_PERSON_SCALAR_FIELDS = frozenset({
    'first_name',
    'middle_name',
    'last_name',
    'second_last_name',
    'gender',
    'birthday',
    'marital_status',
    'country_of_nationality',
    'id_type',
    'id_number',
    'portrait',
    'is_active',
})

_ORG_SCALAR_FIELDS = frozenset({
    'name',
    'legal_name',
    'org_type',
    'industry',
    'id_type',
    'id_number',
    'main_address',
    'country',
    'is_active',
})

_PROFILE_SCALAR_FIELDS = frozenset({
    'academic_degree',
    'accepts_privacy_policy',
    'allows_marketing',
    'preferred_contact_medium',
    'is_active',
})


def validate_person_document(
    id_type,
    id_number: str,
    *,
    exclude_pk=None,
) -> None:
    """Enforce unique (id_type, id_number) for persons — shared with serializers."""
    if not id_type or not id_number:
        return
    qs = Person.objects.filter(id_type=id_type, id_number=id_number)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError(
            'Ya existe una persona con este tipo y número de documento.'
        )


def validate_organization_document(
    id_type,
    id_number: str,
    *,
    exclude_pk=None,
) -> None:
    if not id_type or not id_number:
        return
    qs = Organization.objects.filter(id_type=id_type, id_number=id_number)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError(
            'Ya existe una organización con este tipo y número de documento.'
        )


def _resolve_fk(value: Any):
    """Return model instance unchanged; callers pass instances from forms/DRF."""
    return value


def _build_scalar_kwargs(data: dict, fields: frozenset) -> dict:
    return {key: data[key] for key in fields if key in data}


@transaction.atomic
def create_person(*, data: dict) -> Person:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _PERSON_SCALAR_FIELDS)
    validate_person_document(
        scalars.get('id_type'),
        scalars.get('id_number', ''),
    )
    person = Person(**{k: _resolve_fk(v) for k, v in scalars.items()})
    person.full_clean()
    person.save()
    return person


@transaction.atomic
def update_person(person: Person, *, data: dict, partial: bool = False) -> Person:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _PERSON_SCALAR_FIELDS)
    id_type = scalars.get('id_type', person.id_type)
    id_number = scalars.get('id_number', person.id_number)
    if 'id_type' in scalars or 'id_number' in scalars:
        validate_person_document(id_type, id_number or '', exclude_pk=person.pk)
    for attr, value in scalars.items():
        setattr(person, attr, _resolve_fk(value))
    person.full_clean()
    person.save()
    return person


@transaction.atomic
def delete_person(person: Person) -> None:
    """Hard-delete (matches current DRF destroy on PersonViewSet)."""
    person.delete()


@transaction.atomic
def create_organization(*, data: dict) -> Organization:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _ORG_SCALAR_FIELDS)
    # Minimal HTML create may omit id_number; model requires a value (blank=False).
    if not scalars.get('id_number'):
        scalars['id_number'] = f'N-{uuid.uuid4().hex[:8]}'
    validate_organization_document(
        scalars.get('id_type'),
        scalars.get('id_number', ''),
    )
    org = Organization(**{k: _resolve_fk(v) for k, v in scalars.items()})
    org.full_clean()
    org.save()
    return org


@transaction.atomic
def update_organization(
    organization: Organization,
    *,
    data: dict,
    partial: bool = False,
) -> Organization:
    payload = dict(data)
    scalars = _build_scalar_kwargs(payload, _ORG_SCALAR_FIELDS)
    id_type = scalars.get('id_type', organization.id_type)
    id_number = scalars.get('id_number', organization.id_number)
    if 'id_type' in scalars or 'id_number' in scalars:
        validate_organization_document(
            id_type, id_number or '', exclude_pk=organization.pk
        )
    for attr, value in scalars.items():
        setattr(organization, attr, _resolve_fk(value))
    organization.full_clean()
    organization.save()
    return organization


@transaction.atomic
def delete_organization(organization: Organization) -> None:
    organization.delete()


@transaction.atomic
def create_individual_profile(person: Person, *, data: dict | None = None) -> IndividualProfile:
    """
    Create semantic profile for a person.

    Raises ValidationError if a profile already exists (HTML + API parity).
    """
    if hasattr(person, 'individualprofile'):
        raise ValidationError('La persona ya tiene un perfil individual.')

    payload = dict(data or {})
    scalars = _build_scalar_kwargs(payload, _PROFILE_SCALAR_FIELDS)
    profile = IndividualProfile(person=person, **{k: _resolve_fk(v) for k, v in scalars.items()})
    if 'accepts_privacy_policy' not in scalars:
        profile.accepts_privacy_policy = False
    if 'allows_marketing' not in scalars:
        profile.allows_marketing = False
    if 'preferred_contact_medium' not in scalars:
        profile.preferred_contact_medium = 'EM'
    profile.full_clean()
    profile.save()

    # Optional M2M from API body
    for relation in ('industries', 'skills', 'functions'):
        ids_key = f'{relation}_ids'
        if ids_key in payload:
            getattr(profile, relation).set(payload[ids_key] or [])
        elif relation in payload:
            getattr(profile, relation).set(payload[relation] or [])

    return profile


def person_write_payload_from_validated(validated_data: dict) -> dict:
    """Normalize DRF validated_data for ``create_person`` / ``update_person``."""
    return dict(validated_data)


def organization_write_payload_from_validated(validated_data: dict) -> dict:
    return dict(validated_data)
