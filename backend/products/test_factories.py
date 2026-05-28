"""Shared test data factories for the products app."""

from our_institution.models import Division, OurOrganization


def create_test_organization(**kwargs) -> OurOrganization:
    defaults = {
        'name': 'Test Organization',
        'legal_name': 'Test Organization Legal',
        'email': 'test@example.com',
    }
    defaults.update(kwargs)
    return OurOrganization.objects.create(**defaults)


def create_test_division(organization: OurOrganization | None = None, **kwargs) -> Division:
    org = organization or create_test_organization()
    defaults = {
        'organization': org,
        'name': 'Tecnología',
        'code': 'TECH',
        'description': 'División de productos tecnológicos',
    }
    defaults.update(kwargs)
    return Division.objects.create(**defaults)
