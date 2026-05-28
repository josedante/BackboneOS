"""
Django forms for entities HTML views.

``to_service_payload()`` maps cleaned data to the dict expected by ``services``.
"""

from __future__ import annotations

from django import forms

from .models import Organization, Person
from .selectors import get_entities_form_options


class PersonCreateForm(forms.ModelForm):
    """Minimal fields for new people (parity with Next.js list dialog)."""

    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'second_last_name',
            'is_active',
        ]
        widgets = {
            'is_active': forms.CheckboxInput(),
        }


class PersonUpdateForm(forms.ModelForm):
    """Full person edit on detail page."""

    class Meta:
        model = Person
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'second_last_name',
            'gender',
            'birthday',
            'marital_status',
            'country_of_nationality',
            'id_type',
            'id_number',
            'is_active',
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_entities_form_options()
        self.fields['gender'].queryset = options['genders']
        self.fields['marital_status'].queryset = options['marital_statuses']
        self.fields['country_of_nationality'].queryset = options['countries']
        self.fields['id_type'].queryset = options['personal_id_types']

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        return dict(self.cleaned_data)


class OrganizationCreateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'legal_name', 'main_address', 'is_active']
        widgets = {
            'main_address': forms.Textarea(attrs={'rows': 2}),
            'is_active': forms.CheckboxInput(),
        }


class OrganizationUpdateForm(forms.ModelForm):
    """Organization detail with FK selects (improvement over Next.js text inputs)."""

    class Meta:
        model = Organization
        fields = [
            'name',
            'legal_name',
            'org_type',
            'industry',
            'id_type',
            'id_number',
            'main_address',
            'country',
            'is_active',
        ]
        widgets = {
            'main_address': forms.Textarea(attrs={'rows': 2}),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_entities_form_options()
        self.fields['org_type'].queryset = options['organization_types']
        self.fields['industry'].queryset = options['industries']
        self.fields['country'].queryset = options['countries']
        self.fields['id_type'].queryset = options['organizational_id_types']

    def to_service_payload(self) -> dict:
        if not self.is_valid():
            raise ValueError('Form must be valid before building service payload')
        return dict(self.cleaned_data)


def person_create_to_service_payload(form: PersonCreateForm) -> dict:
    if not form.is_valid():
        raise ValueError('Form must be valid before building service payload')
    return dict(form.cleaned_data)


def organization_create_to_service_payload(form: OrganizationCreateForm) -> dict:
    if not form.is_valid():
        raise ValueError('Form must be valid before building service payload')
    return dict(form.cleaned_data)
