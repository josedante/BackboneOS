"""
Django forms for products HTML views.

``to_service_payload()`` maps cleaned data to the dict expected by ``services``.
"""

from __future__ import annotations

from django import forms

from .models import Product
from .selectors import get_product_form_options


class ProductCreateForm(forms.ModelForm):
    """Minimal fields for new products (parity with Next.js create dialog)."""

    class Meta:
        model = Product
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(),
        }


class ProductUpdateForm(forms.ModelForm):
    """
    Full product edit form.

    ``duration_days`` is edited as an integer; ``services`` converts it to
    ``DurationField`` before save.
    """

    duration_days = forms.IntegerField(
        required=False,
        min_value=0,
        label='Duración (días)',
        help_text='Dejar vacío si no aplica.',
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'code',
            'description',
            'canonical_url',
            'is_active',
            'category',
            'customization',
            'base_price',
            'currency_code',
            'modalities',
            'target_segments',
            'related_industries',
            'related_functions',
            'related_skills',
            'descriptors',
            'tags',
            'included_products',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(),
            'modalities': forms.CheckboxSelectMultiple(),
            'target_segments': forms.CheckboxSelectMultiple(),
            'related_industries': forms.CheckboxSelectMultiple(),
            'related_functions': forms.CheckboxSelectMultiple(),
            'related_skills': forms.CheckboxSelectMultiple(),
            'descriptors': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
            'included_products': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_product_form_options()
        self.fields['category'].queryset = options['categories']
        self.fields['customization'].queryset = options['customizations']
        self.fields['modalities'].queryset = options['modalities']
        self.fields['target_segments'].queryset = options['target_segments']
        self.fields['related_industries'].queryset = options['industries']
        self.fields['related_functions'].queryset = options['functions']
        self.fields['related_skills'].queryset = options['skills']
        self.fields['descriptors'].queryset = options['descriptors']
        self.fields['tags'].queryset = options['tags']
        bundle_qs = options['products_for_bundle']
        if self.instance and self.instance.pk:
            bundle_qs = bundle_qs.exclude(pk=self.instance.pk)
        self.fields['included_products'].queryset = bundle_qs

        if self.instance and self.instance.pk and self.instance.duration:
            total_seconds = int(self.instance.duration.total_seconds())
            self.fields['duration_days'].initial = total_seconds // 86400

    def to_service_payload(self) -> dict:
        """Map validated form data to ``create_product`` / ``update_product`` input."""
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')

        cleaned = self.cleaned_data
        payload = {
            'name': cleaned['name'],
            'code': cleaned['code'],
            'description': cleaned.get('description', ''),
            'canonical_url': cleaned.get('canonical_url') or None,
            'is_active': cleaned.get('is_active', True),
            'base_price': cleaned.get('base_price'),
            'currency_code': cleaned.get('currency_code') or 'PEN',
            'duration_days': cleaned.get('duration_days'),
            'category_id': cleaned['category'].pk if cleaned.get('category') else None,
            'customization_id': (
                cleaned['customization'].pk if cleaned.get('customization') else None
            ),
            'modalities_ids': [m.pk for m in cleaned.get('modalities', [])],
            'target_segments_ids': [s.pk for s in cleaned.get('target_segments', [])],
            'related_industries_ids': [i.pk for i in cleaned.get('related_industries', [])],
            'related_functions_ids': [f.pk for f in cleaned.get('related_functions', [])],
            'related_skills_ids': [s.pk for s in cleaned.get('related_skills', [])],
            'descriptors_ids': [d.pk for d in cleaned.get('descriptors', [])],
            'tags_ids': [t.pk for t in cleaned.get('tags', [])],
            'included_products_ids': [p.pk for p in cleaned.get('included_products', [])],
        }
        return payload


def create_form_to_service_payload(form: ProductCreateForm) -> dict:
    """Map minimal create form to service input."""
    if not form.is_valid():
        raise ValueError('Form must be valid before building service payload')
    cleaned = form.cleaned_data
    return {
        'name': cleaned['name'],
        'code': cleaned['code'],
        'description': cleaned.get('description', ''),
        'is_active': cleaned.get('is_active', True),
    }
