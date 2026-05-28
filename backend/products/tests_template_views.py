"""Tests for products HTML template views."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Product, ProductCategory
from .test_factories import create_test_division

User = get_user_model()


class ProductsTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='productshtml',
            email='html@example.com',
            password='testpass123',
        )
        self.division = create_test_division()
        self.category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=self.division,
        )
        self.product = Product.objects.create(
            name='Sistema Web',
            code='SYS001',
            description='Sistema web avanzado',
            category=self.category,
            base_price=Decimal('1500.00'),
        )

    def test_anonymous_list_redirects_to_login(self):
        response = self.client.get(reverse('products_html:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_anonymous_detail_redirects_to_login(self):
        response = self.client.get(
            reverse('products_html:detail', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_list_renders_product(self):
        self.client.login(username='productshtml', password='testpass123')
        response = self.client.get(reverse('products_html:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sistema Web')
        self.assertContains(response, 'Gestión de Productos')

    def test_search_filters_products(self):
        self.client.login(username='productshtml', password='testpass123')
        Product.objects.create(
            name='Otro Producto',
            code='OTRO001',
            category=self.category,
        )
        response = self.client.get(reverse('products_html:list'), {'q': 'Sistema'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sistema Web')
        self.assertNotContains(response, 'Otro Producto')

    def test_category_filter(self):
        self.client.login(username='productshtml', password='testpass123')
        other_category = ProductCategory.objects.create(
            name='Hardware',
            code='HW',
            division=self.division,
        )
        Product.objects.create(name='Servidor', code='SRV001', category=other_category)
        response = self.client.get(
            reverse('products_html:list'),
            {'category': str(self.category.id)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sistema Web')
        self.assertNotContains(response, 'Servidor')

    def test_create_product_redirects_to_detail(self):
        self.client.login(username='productshtml', password='testpass123')
        response = self.client.post(
            reverse('products_html:create'),
            {
                'name': 'Nuevo Curso',
                'code': 'NEW001',
                'description': 'Descripción',
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Product.objects.get(code='NEW001')
        self.assertEqual(response.url, reverse('products_html:detail', kwargs={'pk': created.pk}))

    def test_update_product(self):
        self.client.login(username='productshtml', password='testpass123')
        response = self.client.post(
            reverse('products_html:detail', kwargs={'pk': self.product.pk}),
            {
                'name': 'Sistema Actualizado',
                'code': 'SYS001',
                'description': self.product.description,
                'is_active': 'on',
                'currency_code': 'PEN',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Sistema Actualizado')

    def test_delete_product(self):
        self.client.login(username='productshtml', password='testpass123')
        pk = self.product.pk
        response = self.client.post(reverse('products_html:delete', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('products_html:list'))
        self.assertFalse(Product.objects.filter(pk=pk).exists())

    def test_invalid_product_returns_404(self):
        self.client.login(username='productshtml', password='testpass123')
        response = self.client.get(
            reverse(
                'products_html:detail',
                kwargs={'pk': '00000000-0000-0000-0000-000000000099'},
            )
        )
        self.assertEqual(response.status_code, 404)
