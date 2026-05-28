"""
Login-required HTML views for the interactions section.

Substrate stance: interactions are a system-of-record captured by contextual apps
(sales, support, tracking scripts) via ``services.create_interaction``. This section
is intentionally thin:
  - Interactions: read-only list + detail (back-office inspection, not data entry).
  - Touchpoints: full config CRUD (reference data referenced by contextual apps).

Reads use selectors only; touchpoint writes call services (no REST loopback).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    TouchpointCreateForm,
    TouchpointUpdateForm,
    touchpoint_create_to_service_payload,
    touchpoint_update_to_service_payload,
)
from .selectors import (
    get_interaction_detail_context,
    get_interactions_hub_context,
    get_touchpoint_detail_context,
)
from .services import create_touchpoint, delete_touchpoint, update_touchpoint


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


def _parse_list_params(request):
    tab = request.GET.get('tab', 'interactions')
    search = request.GET.get('q', '').strip()
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
    except (TypeError, ValueError):
        page_size = 20
    return tab, search, page, page_size


def _parse_filter_uuids(request):
    """Optional UUID filters from query string (empty → None)."""
    def _uuid_param(name):
        raw = request.GET.get(name, '').strip()
        return raw or None

    return {
        'touchpoint_id': _uuid_param('touchpoint'),
        'action_id': _uuid_param('action'),
        'channel_id': _uuid_param('channel'),
        'medium_id': _uuid_param('medium'),
        'touchpoint_type_id': _uuid_param('touchpoint_type'),
        'content_type': request.GET.get('content_type', '').strip(),
    }


@login_required
def interactions_hub(request):
    tab, search, page, page_size = _parse_list_params(request)
    filters = _parse_filter_uuids(request)
    context = get_interactions_hub_context(
        tab=tab,
        search=search,
        page=page,
        page_size=page_size,
        **filters,
    )
    context['page_title'] = 'Interacciones'
    return render(request, 'interactions/list.html', context)


@login_required
def interaction_detail(request, pk):
    """Read-only inspection of a single interaction (writes happen in contextual apps)."""
    context = get_interaction_detail_context(pk)
    context['page_title'] = context['entity_display']
    return render(request, 'interactions/interaction_detail.html', context)


@login_required
def touchpoint_create(request):
    form = TouchpointCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            touchpoint = create_touchpoint(
                data=touchpoint_create_to_service_payload(form)
            )
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Touchpoint "{touchpoint.name}" creado.')
            return redirect('interactions_html:touchpoint_detail', pk=touchpoint.pk)

    return render(
        request,
        'interactions/touchpoint_create.html',
        {'form': form, 'page_title': 'Nuevo touchpoint'},
    )


@login_required
def touchpoint_detail(request, pk):
    detail = get_touchpoint_detail_context(pk)
    touchpoint = detail['touchpoint']
    form = TouchpointUpdateForm(request.POST or None, instance=touchpoint)

    if request.method == 'POST' and form.is_valid():
        try:
            update_touchpoint(
                touchpoint,
                data=touchpoint_update_to_service_payload(form),
                partial=False,
            )
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Touchpoint actualizado.')
            return redirect('interactions_html:touchpoint_detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': touchpoint.name,
    }
    return render(request, 'interactions/touchpoint_detail.html', context)


@login_required
@require_POST
def touchpoint_delete(request, pk):
    detail = get_touchpoint_detail_context(pk)
    touchpoint = detail['touchpoint']
    name = touchpoint.name
    delete_touchpoint(touchpoint)
    messages.success(request, f'Touchpoint "{name}" eliminado.')
    return redirect('interactions_html:list')
