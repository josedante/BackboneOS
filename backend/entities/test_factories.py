"""Minimal factories for entities HTML tests."""

from world.models import Country, PersonalIDType


def create_test_country(**kwargs):
    defaults = {
        'iso3_code': 'PER',
        'iso2_code': 'PE',
        'name': 'Perú',
        'official_name': 'República del Perú',
    }
    defaults.update(kwargs)
    return Country.objects.create(**defaults)


def create_test_person_id_type(country=None, **kwargs):
    if country is None:
        country = create_test_country()
    defaults = {'name': 'DNI', 'code': 'DNI', 'country': country}
    defaults.update(kwargs)
    return PersonalIDType.objects.create(**defaults)
