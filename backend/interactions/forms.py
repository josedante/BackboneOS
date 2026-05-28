"""
Django forms for the interactions section.

Substrate stance: only Touchpoint config is editable here. Interaction capture
lives in contextual apps (sales/support/tracking) that call ``services.create_interaction``,
so there is intentionally no interaction hand-entry form.

``to_service_payload()`` maps cleaned data to the dict expected by ``services``.
"""

from __future__ import annotations

from django import forms

from .models import Touchpoint
from .selectors import get_touchpoint_form_options


class _TouchpointFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_touchpoint_form_options()
        self.fields['channel'].queryset = options['channels']
        self.fields['medium'].queryset = options['mediums']
        self.fields['touchpoint_type'].queryset = options['touchpoint_types']
        self.fields['product'].queryset = options['products']
        self.fields['assigned_staff'].queryset = options['staff_users']
        self.fields['parent'].queryset = options['parent_touchpoints']
        for fk in ('channel', 'medium', 'touchpoint_type', 'product', 'assigned_staff', 'parent'):
            self.fields[fk].required = False

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        return dict(self.cleaned_data)


class TouchpointCreateForm(_TouchpointFormMixin, forms.ModelForm):
    class Meta:
        model = Touchpoint
        fields = [
            'name',
            'code',
            'description',
            'url',
            'channel',
            'medium',
            'touchpoint_type',
            'content_type',
            'product',
            'assigned_staff',
            'parent',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(),
        }


class TouchpointUpdateForm(_TouchpointFormMixin, forms.ModelForm):
    class Meta:
        model = Touchpoint
        fields = TouchpointCreateForm.Meta.fields + ['external_id']
        widgets = TouchpointCreateForm.Meta.widgets


def touchpoint_create_to_service_payload(form: TouchpointCreateForm) -> dict:
    return form.to_service_payload()


def touchpoint_update_to_service_payload(form: TouchpointUpdateForm) -> dict:
    return form.to_service_payload()
