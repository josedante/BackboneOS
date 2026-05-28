"""
Tests for offers HTML views (operator CRUD).

Product offerings are editable in the dashboard; capture and substrate flows
remain in interactions / contextual apps.
"""

import uuid
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import ProductOffering
from .test_factories import create_offering_graph

User = get_user_model()


class OffersTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        graph = create_offering_graph()
        self.user = graph['user']
        self.offering = graph['offering']
        self.product = graph['product']

    def test_anonymous_list_redirects_to_login(self):
        response = self.client.get(reverse('offers_html:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_list_renders_offering(self):
        self.client.login(username='offershtml', password='testpass123')
        response = self.client.get(reverse('offers_html:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRM Launch Offer')

    def test_list_filter_active(self):
        self.client.login(username='offershtml', password='testpass123')
        ProductOffering.objects.create(
            name='Inactive Offer',
            code='INACTIVE_OFF',
            product=self.product,
            price='500.00',
            is_active=False,
        )
        response = self.client.get(reverse('offers_html:list'), {'is_active': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRM Launch Offer')
        self.assertNotContains(response, 'Inactive Offer')

    def test_offering_create(self):
        self.client.login(username='offershtml', password='testpass123')
        response = self.client.post(
            reverse('offers_html:create'),
            {
                'name': 'Winter Promo',
                'code': 'WINTER_2026',
                'description': 'Seasonal promo',
                'product': str(self.product.pk),
                'price': '750.00',
                'currency_code': 'USD',
                'valid_from': str(date.today()),
                'valid_until': str(date.today() + timedelta(days=14)),
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        created = ProductOffering.objects.get(code='WINTER_2026')
        self.assertEqual(created.name, 'Winter Promo')

    def test_offering_detail_update(self):
        self.client.login(username='offershtml', password='testpass123')
        response = self.client.post(
            reverse('offers_html:detail', kwargs={'pk': self.offering.pk}),
            {
                'name': 'CRM Launch Offer Updated',
                'code': self.offering.code,
                'description': self.offering.description,
                'product': str(self.product.pk),
                'price': '800.00',
                'currency_code': 'USD',
                'valid_from': str(self.offering.valid_from),
                'valid_until': str(self.offering.valid_until),
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.offering.refresh_from_db()
        self.assertEqual(self.offering.name, 'CRM Launch Offer Updated')

    def test_offering_delete(self):
        self.client.login(username='offershtml', password='testpass123')
        pk = self.offering.pk
        response = self.client.post(reverse('offers_html:delete', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProductOffering.objects.filter(pk=pk).exists())

    def test_offering_detail_404(self):
        self.client.login(username='offershtml', password='testpass123')
        response = self.client.get(
            reverse('offers_html:detail', kwargs={'pk': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)
