"""
Django forms for offers HTML views.

Product offerings are operator-editable commercial configuration. ``to_service_payload()``
maps cleaned data to the dict expected by ``services`` — same write path as DRF.
"""

from __future__ import annotations

from django import forms

from products.models import Product

from .models import ProductOffering
from .selectors import get_offering_form_options


class ProductOfferingCreateForm(forms.ModelForm):
    """Minimal fields for new offerings (parity with products create flow)."""

    class Meta:
        model = ProductOffering
        fields = [
            'name',
            'code',
            'description',
            'product',
            'price',
            'currency_code',
            'valid_from',
            'valid_until',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by(
            'name'
        )


class ProductOfferingUpdateForm(forms.ModelForm):
    """Full offering edit on detail page including targeting M2M."""

    class Meta:
        model = ProductOffering
        fields = [
            'name',
            'code',
            'description',
            'product',
            'price',
            'currency_code',
            'valid_from',
            'valid_until',
            'auto_renew',
            'duration_days',
            'landing_url',
            'is_active',
            'channels',
            'seats',
            'target_segments',
            'related_industries',
            'related_functions',
            'descriptors',
            'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(),
            'auto_renew': forms.CheckboxInput(),
            'landing_url': forms.URLInput(),
            'channels': forms.CheckboxSelectMultiple(),
            'seats': forms.CheckboxSelectMultiple(),
            'target_segments': forms.CheckboxSelectMultiple(),
            'related_industries': forms.CheckboxSelectMultiple(),
            'related_functions': forms.CheckboxSelectMultiple(),
            'descriptors': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_offering_form_options()
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by(
            'name'
        )
        self.fields['duration_days'].required = False
        self.fields['landing_url'].required = False
        self.fields['channels'].queryset = options['channels']
        self.fields['seats'].queryset = options['seats']
        self.fields['target_segments'].queryset = options['target_segments']
        self.fields['related_industries'].queryset = options['related_industries']
        self.fields['related_functions'].queryset = options['related_functions']
        self.fields['descriptors'].queryset = options['descriptors']
        self.fields['tags'].queryset = options['tags']

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        cleaned = self.cleaned_data
        return {
            'name': cleaned['name'],
            'code': cleaned['code'],
            'description': cleaned.get('description', ''),
            'product_id': cleaned['product'].pk,
            'price': cleaned['price'],
            'currency_code': cleaned.get('currency_code') or 'USD',
            'valid_from': cleaned.get('valid_from'),
            'valid_until': cleaned.get('valid_until'),
            'auto_renew': cleaned.get('auto_renew', False),
            'duration_days': cleaned.get('duration_days'),
            'landing_url': cleaned.get('landing_url') or None,
            'is_active': cleaned.get('is_active', True),
            'channels_ids': [c.pk for c in cleaned.get('channels', [])],
            'seats_ids': [s.pk for s in cleaned.get('seats', [])],
            'target_segments_ids': [s.pk for s in cleaned.get('target_segments', [])],
            'related_industries_ids': [i.pk for i in cleaned.get('related_industries', [])],
            'related_functions_ids': [f.pk for f in cleaned.get('related_functions', [])],
            'descriptors_ids': [d.pk for d in cleaned.get('descriptors', [])],
            'tags_ids': [t.pk for t in cleaned.get('tags', [])],
        }


def create_form_to_service_payload(form: ProductOfferingCreateForm) -> dict:
    if not form.is_valid():
        raise ValueError('Form must be valid before building service payload')
    cleaned = form.cleaned_data
    return {
        'name': cleaned['name'],
        'code': cleaned['code'],
        'description': cleaned.get('description', ''),
        'product_id': cleaned['product'].pk,
        'price': cleaned['price'],
        'currency_code': cleaned.get('currency_code') or 'USD',
        'valid_from': cleaned.get('valid_from'),
        'valid_until': cleaned.get('valid_until'),
        'is_active': cleaned.get('is_active', True),
    }
