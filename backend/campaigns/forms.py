"""
Django forms for campaigns HTML views.

Campaigns are operator-editable configuration (not a substrate). ``to_service_payload()``
maps cleaned data to the dict expected by ``services`` — same write path as DRF.
"""

from __future__ import annotations

from django import forms

from .models import Campaign, CampaignTouchpoint
from interactions.models import Touchpoint

from .selectors import _FORM_FK_LIMIT, get_campaign_form_options


class CampaignCreateForm(forms.ModelForm):
    """Minimal fields for new campaigns (parity with products create flow)."""

    class Meta:
        model = Campaign
        fields = [
            'name',
            'code',
            'description',
            'start_date',
            'end_date',
            'budget',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(),
        }


class CampaignUpdateForm(forms.ModelForm):
    """Full campaign edit on detail page (v1 M2M: channels + product targets)."""

    class Meta:
        model = Campaign
        fields = [
            'name',
            'code',
            'description',
            'start_date',
            'end_date',
            'budget',
            'content_type',
            'funnel_stage',
            'division',
            'team',
            'parent',
            'is_active',
            'channels',
            'target_products',
            'target_categories',
            'target_offers',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(),
            'channels': forms.CheckboxSelectMultiple(),
            'target_products': forms.CheckboxSelectMultiple(),
            'target_categories': forms.CheckboxSelectMultiple(),
            'target_offers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_campaign_form_options()
        self.fields['division'].queryset = options['divisions']
        self.fields['team'].queryset = options['teams']
        parent_qs = Campaign.objects.filter(is_active=True).order_by('name')
        if self.instance and self.instance.pk:
            parent_qs = parent_qs.exclude(pk=self.instance.pk)
        self.fields['parent'].queryset = parent_qs[:_FORM_FK_LIMIT]
        self.fields['channels'].queryset = options['channels']
        self.fields['target_products'].queryset = options['products']
        self.fields['target_categories'].queryset = options['categories']
        self.fields['target_offers'].queryset = options['offers']
        for fk in ('division', 'team', 'parent'):
            self.fields[fk].required = False

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        cleaned = self.cleaned_data
        return {
            'name': cleaned['name'],
            'code': cleaned['code'],
            'description': cleaned.get('description', ''),
            'start_date': cleaned['start_date'],
            'end_date': cleaned.get('end_date'),
            'budget': cleaned.get('budget') or 0,
            'content_type': cleaned.get('content_type') or None,
            'funnel_stage': cleaned.get('funnel_stage') or Campaign.ANY,
            'is_active': cleaned.get('is_active', True),
            'division_id': cleaned['division'].pk if cleaned.get('division') else None,
            'team_id': cleaned['team'].pk if cleaned.get('team') else None,
            'parent_id': cleaned['parent'].pk if cleaned.get('parent') else None,
            'channels_ids': [c.pk for c in cleaned.get('channels', [])],
            'target_products_ids': [p.pk for p in cleaned.get('target_products', [])],
            'target_categories_ids': [c.pk for c in cleaned.get('target_categories', [])],
            'target_offers_ids': [o.pk for o in cleaned.get('target_offers', [])],
        }


class CampaignTouchpointForm(forms.ModelForm):
    """Link a configured touchpoint to a campaign."""

    class Meta:
        model = CampaignTouchpoint
        fields = [
            'campaign',
            'touchpoint',
            'weight',
            'priority',
            'expected_conversions',
            'budget_allocated',
        ]
        widgets = {
            'expected_conversions': forms.NumberInput(attrs={'min': 0}),
            'priority': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unsliced querysets — ModelChoiceField validation breaks on sliced querysets.
        self.fields['campaign'].queryset = Campaign.objects.filter(is_active=True).order_by(
            'name'
        )
        self.fields['touchpoint'].queryset = Touchpoint.objects.filter(
            is_active=True
        ).order_by('name')

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        return dict(self.cleaned_data)


def campaign_create_to_service_payload(form: CampaignCreateForm) -> dict:
    if not form.is_valid():
        raise ValueError('Form must be valid before building service payload')
    cleaned = form.cleaned_data
    return {
        'name': cleaned['name'],
        'code': cleaned['code'],
        'description': cleaned.get('description', ''),
        'start_date': cleaned['start_date'],
        'end_date': cleaned.get('end_date'),
        'budget': cleaned.get('budget') or 0,
        'is_active': cleaned.get('is_active', True),
    }
