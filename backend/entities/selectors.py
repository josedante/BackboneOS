"""
Read-only query layer for the entities app.

Consumed by DRF viewsets and Django template views. Mutations belong in
``services.py`` — never fetch data via HTTP to the REST API from templates.
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404

from .models import ContactDetail, IndividualProfile, Organization, Person, PhysicalAddress

# --- Queryset factories (mirror entities/views.py optimizations) ---


def people_active_queryset(*, action: str = 'list') -> QuerySet:
    """
    Active people with relations prefetched for list or detail.

    List HTML only shows ``is_active=True`` records, matching the DRF default.
    """
    qs = (
        Person.objects.select_related(
            'country_of_nationality',
            'id_type',
            'gender',
            'marital_status',
        )
        .prefetch_related(
            Prefetch(
                'contacts',
                queryset=ContactDetail.objects.filter(is_active=True),
            ),
            'individualprofile',
        )
        .filter(is_active=True)
    )
    if action == 'retrieve':
        qs = qs.prefetch_related(
            Prefetch(
                'physicaladdress_set',
                queryset=PhysicalAddress.objects.filter(is_active=True).select_related(
                    'country'
                ),
            ),
        )
    return qs


def organizations_active_queryset(*, action: str = 'list') -> QuerySet:
    """Active organizations with FK relations for list or detail."""
    qs = (
        Organization.objects.select_related('org_type', 'industry', 'country', 'id_type')
        .filter(is_active=True)
    )
    if action == 'retrieve':
        qs = qs.prefetch_related(
            Prefetch(
                'physicaladdress_set',
                queryset=PhysicalAddress.objects.filter(is_active=True).select_related(
                    'country'
                ),
            ),
        )
    return qs


def contacts_active_queryset() -> QuerySet:
    return ContactDetail.objects.select_related('person', 'organization').filter(
        is_active=True
    )


def addresses_active_queryset() -> QuerySet:
    return PhysicalAddress.objects.select_related(
        'owner_person', 'owner_org', 'country'
    ).filter(is_active=True)


def profiles_active_queryset() -> QuerySet:
    return (
        IndividualProfile.objects.select_related('person', 'academic_degree')
        .prefetch_related('industries', 'skills', 'functions')
        .filter(is_active=True)
    )


# --- Search helpers (DRF SearchFilter parity for HTML lists) ---


def people_list_filter(qs: QuerySet, *, search: str = '') -> QuerySet:
    """Apply text search across person names, id_number, and contact channels."""
    if not search:
        return qs
    term = search.strip()
    return qs.filter(
        Q(first_name__icontains=term)
        | Q(middle_name__icontains=term)
        | Q(last_name__icontains=term)
        | Q(second_last_name__icontains=term)
        | Q(id_number__icontains=term)
        | Q(contacts__email__icontains=term)
        | Q(contacts__phone__icontains=term)
    ).distinct()


def organizations_list_filter(qs: QuerySet, *, search: str = '') -> QuerySet:
    if not search:
        return qs
    term = search.strip()
    return qs.filter(
        Q(name__icontains=term)
        | Q(legal_name__icontains=term)
        | Q(id_number__icontains=term)
        | Q(main_address__icontains=term)
    ).distinct()


def person_primary_contact_display(person: Person) -> dict | None:
    """Shape primary contact for list templates (matches API list serializer intent)."""
    primary = person.primary_contact
    if not primary:
        return None
    return {
        'type': 'email' if primary.email else 'phone',
        'value': primary.email or primary.phone,
        'verified': primary.verified,
    }


def build_profile_summary(person: Person) -> dict | None:
    """
    Profile card data for person detail templates.

    Mirrors ``PersonDetailSerializer.get_profile`` without running DRF.
    """
    try:
        profile = person.individualprofile
    except IndividualProfile.DoesNotExist:
        return None
    return {
        'id': profile.id,
        'academic_degree': profile.academic_degree.name if profile.academic_degree else None,
        'industries_count': profile.industries.count(),
        'skills_count': profile.skills.count(),
        'functions_count': profile.functions.count(),
        'preferred_contact_medium': profile.get_preferred_contact_medium_display(),
        'allows_marketing': profile.allows_marketing,
    }


# --- Page context builders ---


def get_entities_list_context(
    *,
    tab: str = 'people',
    search: str = '',
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Build tabbed list context for ``/entities/``.

    ``tab`` is a query param because Next.js used a single ``/entities`` route
  with people/organizations tabs — preserve that UX in Django.
    """
    if tab not in ('people', 'organizations'):
        tab = 'people'

    people_qs = people_list_filter(
        people_active_queryset(action='list').order_by('-created_at'),
        search=search,
    )
    orgs_qs = organizations_list_filter(
        organizations_active_queryset(action='list').order_by('-created_at'),
        search=search,
    )

    people_count = people_qs.count()
    orgs_count = orgs_qs.count()

    # Only paginate the active tab's queryset to avoid double OFFSET work.
    if tab == 'people':
        people_paginator = Paginator(people_qs, page_size)
        people_page_obj = people_paginator.get_page(page)
        orgs_page_obj = None
    else:
        orgs_paginator = Paginator(orgs_qs, page_size)
        orgs_page_obj = orgs_paginator.get_page(page)
        people_page_obj = None

    # Precompute display helpers for people rows on the current page.
    people_rows = []
    if people_page_obj is not None:
        for person in people_page_obj.object_list:
            people_rows.append(
                {
                    'person': person,
                    'primary_contact': person_primary_contact_display(person),
                }
            )

    return {
        'tab': tab,
        'search': search,
        'page': page,
        'page_size': page_size,
        'people_count': people_count,
        'orgs_count': orgs_count,
        'people_page_obj': people_page_obj,
        'orgs_page_obj': orgs_page_obj,
        'people_rows': people_rows,
    }


def get_person_detail_context(pk) -> dict:
    """Person detail with nested contacts, addresses, and profile summary."""
    person = get_object_or_404(people_active_queryset(action='retrieve'), pk=pk)
    contacts = list(person.contacts.filter(is_active=True))
    addresses = list(person.physicaladdress_set.filter(is_active=True))
    return {
        'person': person,
        'contacts': contacts,
        'addresses': addresses,
        'profile_summary': build_profile_summary(person),
    }


def get_organization_detail_context(pk) -> dict:
    """Organization detail with active addresses."""
    organization = get_object_or_404(
        organizations_active_queryset(action='retrieve'), pk=pk
    )
    addresses = list(organization.physicaladdress_set.filter(is_active=True))
    return {
        'organization': organization,
        'addresses': addresses,
    }


def get_entities_form_options() -> dict:
    """FK querysets and choice tuples for entity HTML forms."""
    from world.models import (  # noqa: PLC0415 — avoid import cycles at module load
        AcademicDegree,
        Country,
        Gender,
        Industry,
        MaritalStatus,
        OrganizationalIDType,
        OrganizationType,
        PersonalIDType,
    )

    return {
        'countries': Country.objects.filter(is_active=True).order_by('name'),
        'genders': Gender.objects.filter(is_active=True).order_by('display_order', 'name'),
        'marital_statuses': MaritalStatus.objects.filter(is_active=True).order_by(
            'display_order', 'name'
        ),
        'personal_id_types': PersonalIDType.objects.filter(is_active=True).order_by('name'),
        'organization_types': OrganizationType.objects.filter(is_active=True).order_by(
            'name'
        ),
        'industries': Industry.objects.filter(is_active=True).order_by('name'),
        'organizational_id_types': OrganizationalIDType.objects.filter(
            is_active=True
        ).order_by('name'),
        'academic_degrees': AcademicDegree.objects.filter(is_active=True).order_by('name'),
        'contact_medium_choices': IndividualProfile._meta.get_field(
            'preferred_contact_medium'
        ).choices,
    }
