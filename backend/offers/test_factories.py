"""
Minimal test fixtures for offers HTML tests.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model

from our_institution.models import Division, OurOrganization
from products.models import Product, ProductCategory

from .models import ProductOffering

User = get_user_model()


def create_offering_graph(*, user=None):
    """
    Organization → division → category → product → product offering.

    Returns created objects for template view assertions.
    """
    user = user or User.objects.create_user(
        username='offershtml',
        email='offershtml@example.com',
        password='testpass123',
    )
    organization = OurOrganization.objects.create(name='Offers Test Org')
    division = Division.objects.create(
        name='Sales Division',
        code='SALES_DIV',
        organization=organization,
    )
    category = ProductCategory.objects.create(
        name='Software',
        code='SW_OFF',
        division=division,
    )
    product = Product.objects.create(
        name='CRM Suite',
        code='CRM_SUITE',
        description='Customer relationship management',
        category=category,
        base_price=Decimal('1000.00'),
        currency_code='USD',
    )
    offering = ProductOffering.objects.create(
        name='CRM Launch Offer',
        code='CRM_LAUNCH_2026',
        description='Introductory pricing',
        product=product,
        price=Decimal('850.00'),
        currency_code='USD',
        valid_from=date.today(),
        valid_until=date.today() + timedelta(days=30),
        is_active=True,
    )
    return {
        'user': user,
        'organization': organization,
        'division': division,
        'category': category,
        'product': product,
        'offering': offering,
    }
