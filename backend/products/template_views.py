"""
Login-required HTML views for the products CRM.

Reads use selectors only; writes call services (no REST loopback).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductCreateForm, ProductUpdateForm, create_form_to_service_payload
from .selectors import get_product_detail_context, get_products_list_context
from .services import create_product, delete_product, update_product


def _validation_errors_to_form(form, exc: ValidationError):
    """Attach Django ValidationError message_dict entries to form fields."""
    if hasattr(exc, 'message_dict'):
        for field, errs in exc.message_dict.items():
            form.add_error(field if field != '__all__' else None, errs)
    else:
        form.add_error(None, exc.messages)


@login_required
def product_list(request):
    search = request.GET.get('q', '').strip()
    category_id = request.GET.get('category') or None
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
    except (TypeError, ValueError):
        page_size = 20

    context = get_products_list_context(
        search=search,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )
    context['page_title'] = 'Products'
    return render(request, 'products/list.html', context)


@login_required
def product_create(request):
    form = ProductCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            product = create_product(data=create_form_to_service_payload(form))
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Producto "{product.name}" creado.')
            return redirect('products_html:detail', pk=product.pk)

    return render(
        request,
        'products/create.html',
        {
            'form': form,
            'page_title': 'Nuevo producto',
        },
    )


@login_required
def product_detail(request, pk):
    detail = get_product_detail_context(pk)
    product = detail['product']
    form = ProductUpdateForm(request.POST or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        try:
            update_product(product, data=form.to_service_payload(), partial=False)
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Producto actualizado.')
            return redirect('products_html:detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': product.name,
    }
    return render(request, 'products/detail.html', context)


@login_required
@require_POST
def product_delete(request, pk):
    detail = get_product_detail_context(pk)
    product = detail['product']
    name = product.name
    delete_product(product)
    messages.success(request, f'Producto "{name}" eliminado.')
    return redirect('products_html:list')
