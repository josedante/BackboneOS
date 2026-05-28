"""
Login-required HTML views for the offers CRM.

Operator-editable product offerings. Reads use selectors only; writes call
services (no REST loopback).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    ProductOfferingCreateForm,
    ProductOfferingUpdateForm,
    create_form_to_service_payload,
)
from .selectors import get_offering_detail_context, get_offerings_list_context
from .services import create_offering, delete_offering, update_offering


def _validation_errors_to_form(form, exc: ValidationError):
    """Attach Django ValidationError message_dict entries to form fields."""
    if hasattr(exc, 'message_dict'):
        for field, errs in exc.message_dict.items():
            if field == '__all__' or field not in form.fields:
                form.add_error(None, errs)
            else:
                form.add_error(field, errs)
    else:
        form.add_error(None, getattr(exc, 'messages', None) or [str(exc)])


def _parse_list_params(request):
    search = request.GET.get('q', '').strip()
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
    except (TypeError, ValueError):
        page_size = 20
    return search, page, page_size


def _parse_filter_params(request):
    def _uuid_param(name):
        raw = request.GET.get(name, '').strip()
        return raw or None

    return {
        'is_active': request.GET.get('is_active', '').strip() or None,
        'product_id': _uuid_param('product'),
        'category_id': _uuid_param('category'),
        'currency_code': request.GET.get('currency_code', '').strip(),
        'validity_status': request.GET.get('validity_status', '').strip(),
        'min_price': request.GET.get('min_price', '').strip() or None,
        'max_price': request.GET.get('max_price', '').strip() or None,
    }


@login_required
def offering_list(request):
    search, page, page_size = _parse_list_params(request)
    filters = _parse_filter_params(request)
    context = get_offerings_list_context(
        search=search,
        page=page,
        page_size=page_size,
        **filters,
    )
    context['page_title'] = 'Ofertas'
    return render(request, 'offers/list.html', context)


@login_required
def offering_create(request):
    form = ProductOfferingCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            offering = create_offering(data=create_form_to_service_payload(form))
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Oferta "{offering.name}" creada.')
            return redirect('offers_html:detail', pk=offering.pk)

    return render(
        request,
        'offers/create.html',
        {
            'form': form,
            'page_title': 'Nueva oferta',
        },
    )


@login_required
def offering_detail(request, pk):
    detail = get_offering_detail_context(pk)
    offering = detail['offering']
    form = ProductOfferingUpdateForm(request.POST or None, instance=offering)

    if request.method == 'POST' and form.is_valid():
        try:
            update_offering(offering, data=form.to_service_payload(), partial=False)
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Oferta "{offering.name}" actualizada.')
            return redirect('offers_html:detail', pk=offering.pk)

    return render(
        request,
        'offers/detail.html',
        {
            'offering': offering,
            'product': detail['product'],
            'form': form,
            'page_title': offering.name,
        },
    )


@login_required
@require_POST
def offering_delete(request, pk):
    detail = get_offering_detail_context(pk)
    name = detail['offering'].name
    delete_offering(detail['offering'])
    messages.success(request, f'Oferta "{name}" eliminada.')
    return redirect('offers_html:list')
