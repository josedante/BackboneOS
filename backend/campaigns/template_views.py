"""
Login-required HTML views for the campaigns CRM.

Operator-editable campaigns and campaign–touchpoint links. Interaction capture
remains in contextual apps (substrate); this section does not log interactions.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    CampaignCreateForm,
    CampaignTouchpointForm,
    CampaignUpdateForm,
    campaign_create_to_service_payload,
)
from .selectors import (
    get_campaign_detail_context,
    get_campaign_touchpoint_detail_context,
    get_campaigns_hub_context,
)
from .services import (
    create_campaign,
    create_campaign_touchpoint,
    delete_campaign,
    delete_campaign_touchpoint,
    update_campaign,
    update_campaign_touchpoint,
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
        form.add_error(None, getattr(exc, 'messages', None) or [str(exc)])


def _parse_list_params(request):
    tab = request.GET.get('tab', 'campaigns')
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


def _parse_filter_params(request):
    def _uuid_param(name):
        raw = request.GET.get(name, '').strip()
        return raw or None

    return {
        'content_type': request.GET.get('content_type', '').strip(),
        'funnel_stage': request.GET.get('funnel_stage', '').strip(),
        'division_id': _uuid_param('division'),
        'status': request.GET.get('status', '').strip(),
        'campaign_id': _uuid_param('campaign'),
    }


@login_required
def campaigns_hub(request):
    """Tabbed hub: campaigns list vs campaign–touchpoint links."""
    tab, search, page, page_size = _parse_list_params(request)
    filters = _parse_filter_params(request)
    context = get_campaigns_hub_context(
        tab=tab,
        search=search,
        page=page,
        page_size=page_size,
        **filters,
    )
    context['page_title'] = 'Campañas'
    return render(request, 'campaigns/list.html', context)


@login_required
def campaign_create(request):
    form = CampaignCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            campaign = create_campaign(data=campaign_create_to_service_payload(form))
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, f'Campaña "{campaign.name}" creada.')
            return redirect('campaigns_html:detail', pk=campaign.pk)

    return render(
        request,
        'campaigns/create.html',
        {'form': form, 'page_title': 'Nueva campaña'},
    )


@login_required
def campaign_detail(request, pk):
    detail = get_campaign_detail_context(pk)
    campaign = detail['campaign']
    form = CampaignUpdateForm(request.POST or None, instance=campaign)

    if request.method == 'POST' and form.is_valid():
        try:
            update_campaign(campaign, data=form.to_service_payload(), partial=False)
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Campaña actualizada.')
            return redirect('campaigns_html:detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': campaign.name,
    }
    return render(request, 'campaigns/detail.html', context)


@login_required
@require_POST
def campaign_delete(request, pk):
    detail = get_campaign_detail_context(pk)
    campaign = detail['campaign']
    name = campaign.name
    delete_campaign(campaign)
    messages.success(request, f'Campaña "{name}" eliminada.')
    return redirect('campaigns_html:list')


@login_required
def campaign_touchpoint_create(request):
    initial = {}
    campaign_id = request.GET.get('campaign', '').strip()
    if campaign_id:
        initial['campaign'] = campaign_id
    form = CampaignTouchpointForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        try:
            link = create_campaign_touchpoint(data=form.to_service_payload())
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Enlace campaña–touchpoint creado.')
            return redirect('campaigns_html:touchpoint_detail', pk=link.pk)

    return render(
        request,
        'campaigns/touchpoint_create.html',
        {'form': form, 'page_title': 'Nuevo enlace touchpoint'},
    )


@login_required
def campaign_touchpoint_detail(request, pk):
    detail = get_campaign_touchpoint_detail_context(pk)
    link = detail['link']
    form = CampaignTouchpointForm(request.POST or None, instance=link)

    if request.method == 'POST' and form.is_valid():
        try:
            update_campaign_touchpoint(
                link, data=form.to_service_payload(), partial=False
            )
        except ValidationError as exc:
            _validation_errors_to_form(form, exc)
        else:
            messages.success(request, 'Enlace actualizado.')
            return redirect('campaigns_html:touchpoint_detail', pk=pk)

    context = {
        **detail,
        'form': form,
        'page_title': f'{link.campaign.name} → {link.touchpoint.name}',
    }
    return render(request, 'campaigns/touchpoint_detail.html', context)


@login_required
@require_POST
def campaign_touchpoint_delete(request, pk):
    detail = get_campaign_touchpoint_detail_context(pk)
    link = detail['link']
    delete_campaign_touchpoint(link)
    messages.success(request, 'Enlace eliminado.')
    return redirect(f"{reverse('campaigns_html:list')}?tab=touchpoints")
