"""
Login-required HTML views for the entities CRM.

Reads use selectors only; writes call services (no REST loopback).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    OrganizationCreateForm,
    OrganizationUpdateForm,
    PersonCreateForm,
    PersonUpdateForm,
    organization_create_to_service_payload,
    person_create_to_service_payload,
)
from interactions.selectors import get_entity_interactions_timeline

from .selectors import (
    get_entities_list_context,
    get_organization_detail_context,
    get_person_detail_context,
)
from .services import (
    create_individual_profile,
    create_organization,
    create_person,
    delete_organization,
    delete_person,
    update_organization,
    update_person,
)


def _validation_errors_to_form(form, exc: ValidationError):
    """Attach Django ValidationError message_dict entries to form fields."""
    if hasattr(exc, 'message_dict'):
        for field, errs in exc.message_dict.items():
            if field == '__all__' or field not in form.fields:
                form.add_error(None, errs)
            else:
                form.add_error(field, errs)
    else:
        messages_list = getattr(exc, 'messages', None) or [str(exc)]
        form.add_error(None, messages_list)


@login_required
def entities_list(request):
    tab = request.GET.get('tab', 'people')
    search = request.GET.get('q', '').strip()
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
    except (TypeError, ValueError):
        page_size = 20

    context = get_entities_list_context(
        tab=tab,
        search=search,
        page=page,
        page_size=page_size,
    )
    context['page_title'] = 'Entidades'
    return render(request, 'entities/list.html', context)


@login_required
def person_create(request):
    form = PersonCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            person = create_person(data=person_create_to_service_payload(form))
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Persona "{person.full_name}" creada.')
            return redirect('entities_html:person_detail', pk=person.pk)

    return render(
        request,
        'entities/person_create.html',
        {'form': form, 'page_title': 'Nueva persona'},
    )


@login_required
def person_detail(request, pk):
    detail = get_person_detail_context(pk)
    person = detail['person']
    form = PersonUpdateForm(request.POST or None, instance=person)

    if request.method == 'POST' and form.is_valid():
        try:
            update_person(person, data=form.to_service_payload(), partial=False)
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Persona actualizada.')
            return redirect('entities_html:person_detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': person.full_name or 'Persona',
        # Cross-cutting read: everything this customer has done across touchpoints.
        'interactions_timeline': get_entity_interactions_timeline(person=person),
    }
    return render(request, 'entities/person_detail.html', context)


@login_required
@require_POST
def person_create_profile(request, pk):
    detail = get_person_detail_context(pk)
    person = detail['person']
    try:
        create_individual_profile(person, data={})
    except ValidationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, 'Perfil individual creado.')
    return redirect('entities_html:person_detail', pk=pk)


@login_required
@require_POST
def person_delete(request, pk):
    detail = get_person_detail_context(pk)
    person = detail['person']
    name = person.full_name or 'Persona'
    delete_person(person)
    messages.success(request, f'Persona "{name}" eliminada.')
    return redirect('entities_html:list')


@login_required
def organization_create(request):
    form = OrganizationCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            org = create_organization(data=organization_create_to_service_payload(form))
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Organización "{org.name}" creada.')
            return redirect('entities_html:org_detail', pk=org.pk)

    return render(
        request,
        'entities/organization_create.html',
        {'form': form, 'page_title': 'Nueva organización'},
    )


@login_required
def organization_detail(request, pk):
    detail = get_organization_detail_context(pk)
    organization = detail['organization']
    form = OrganizationUpdateForm(request.POST or None, instance=organization)

    if request.method == 'POST' and form.is_valid():
        try:
            update_organization(organization, data=form.to_service_payload(), partial=False)
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Organización actualizada.')
            return redirect('entities_html:org_detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': organization.name,
        'interactions_timeline': get_entity_interactions_timeline(organization=organization),
    }
    return render(request, 'entities/organization_detail.html', context)


@login_required
@require_POST
def organization_delete(request, pk):
    detail = get_organization_detail_context(pk)
    organization = detail['organization']
    name = organization.name
    delete_organization(organization)
    messages.success(request, f'Organización "{name}" eliminada.')
    return redirect('entities_html:list')
