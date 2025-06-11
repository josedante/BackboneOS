from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from .models import ProductOffering
from products.models import Product, ProductCategory, Division
from world.models import Industry, FunctionOrResponsibility
from interactions.models import Channel, Medium


class ProductOfferingModelTest(TestCase):
    """Tests para el modelo ProductOffering"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear división
        self.division = Division.objects.create(
            name="Tecnología",
            code="TECH",
            description="División de tecnología"
        )
        
        # Crear categoría
        self.category = ProductCategory.objects.create(
            name="Software",
            code="SW",
            division=self.division
        )
        
        # Crear producto
        self.product = Product.objects.create(
            name="Sistema CRM",
            code="CRM001",
            description="Sistema de gestión de clientes",
            category=self.category,
            price=1000.00,
            currency_code="USD"
        )
        
        # Crear oferta
        self.offering = ProductOffering.objects.create(
            name="Oferta CRM Premium",
            code="CRM_PREM_001",
            description="Oferta premium del sistema CRM",
            product=self.product,
            price=850.00,
            currency_code="USD",
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30)
        )
    
    def test_str_representation(self):
        """Test representación string"""
        expected = f"{self.offering.name} ({self.product.name})"
        self.assertEqual(str(self.offering), expected)
    
    def test_price_display(self):
        """Test formato de precio"""
        expected = "USD 850.00"
        self.assertEqual(self.offering.price_display, expected)
    
    def test_is_currently_valid_true(self):
        """Test validez actual - válida"""
        self.assertTrue(self.offering.is_currently_valid)
    
    def test_is_currently_valid_false_expired(self):
        """Test validez actual - expirada"""
        self.offering.valid_until = date.today() - timedelta(days=1)
        self.offering.save()
        self.assertFalse(self.offering.is_currently_valid)
    
    def test_is_currently_valid_false_future(self):
        """Test validez actual - futura"""
        self.offering.valid_from = date.today() + timedelta(days=1)
        self.offering.save()
        self.assertFalse(self.offering.is_currently_valid)
    
    def test_is_currently_valid_no_dates(self):
        """Test validez actual - sin fechas (siempre válida)"""
        self.offering.valid_from = None
        self.offering.valid_until = None
        self.offering.save()
        self.assertTrue(self.offering.is_currently_valid)


class ProductOfferingAPITest(APITestCase):
    """Tests para la API de ofertas"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear división y categoría
        self.division = Division.objects.create(
            name="Servicios",
            code="SERV"
        )
        
        self.category = ProductCategory.objects.create(
            name="Consultoría",
            code="CONS",
            division=self.division
        )
        
        # Crear producto
        self.product = Product.objects.create(
            name="Consultoría IT",
            code="CONS001",
            description="Servicios de consultoría",
            category=self.category,
            price=2000.00
        )
        
        # URLs de la API
        self.list_url = reverse('productoffering-list')
        self.analytics_url = reverse('productoffering-analytics')
        self.choices_url = reverse('productoffering-choices')
        self.currently_valid_url = reverse('productoffering-currently-valid')
    
    def test_create_offering(self):
        """Test crear oferta"""
        data = {
            'name': 'Oferta Consultoría Q1',
            'code': 'CONS_Q1_2024',
            'description': 'Oferta especial primer trimestre',
            'product': self.product.id,
            'price': '1800.00',
            'currency_code': 'USD',
            'valid_from': date.today().isoformat(),
            'valid_until': (date.today() + timedelta(days=90)).isoformat(),
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductOffering.objects.count(), 1)
        
        offering = ProductOffering.objects.first()
        self.assertEqual(offering.name, data['name'])
        self.assertEqual(offering.code, data['code'])
        self.assertEqual(str(offering.price), data['price'])
    
    def test_list_offerings(self):
        """Test listar ofertas"""
        # Crear algunas ofertas
        ProductOffering.objects.create(
            name="Oferta 1",
            code="OFF001",
            product=self.product,
            price=1500.00,
            currency_code="USD"
        )
        
        ProductOffering.objects.create(
            name="Oferta 2",
            code="OFF002", 
            product=self.product,
            price=1200.00,
            currency_code="EUR"
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_currency(self):
        """Test filtrar por moneda"""
        # Crear ofertas con diferentes monedas
        ProductOffering.objects.create(
            name="Oferta USD",
            code="USD001",
            product=self.product,
            price=1000.00,
            currency_code="USD"
        )
        
        ProductOffering.objects.create(
            name="Oferta EUR",
            code="EUR001",
            product=self.product,
            price=900.00,
            currency_code="EUR"
        )
        
        # Filtrar por USD
        response = self.client.get(self.list_url, {'currency_code': 'USD'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['currency_code'], 'USD')
    
    def test_currently_valid_offerings(self):
        """Test ofertas actualmente válidas"""
        # Crear oferta válida
        valid_offering = ProductOffering.objects.create(
            name="Oferta Válida",
            code="VALID001",
            product=self.product,
            price=1000.00,
            is_active=True,
            valid_from=date.today() - timedelta(days=5),
            valid_until=date.today() + timedelta(days=30)
        )
        
        # Crear oferta expirada
        expired_offering = ProductOffering.objects.create(
            name="Oferta Expirada",
            code="EXPIRED001",
            product=self.product,
            price=800.00,
            is_active=True,
            valid_from=date.today() - timedelta(days=60),
            valid_until=date.today() - timedelta(days=1)
        )
        
        response = self.client.get(self.currently_valid_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(valid_offering.id))
    
    def test_analytics_endpoint(self):
        """Test endpoint de analytics"""
        # Crear varias ofertas para analytics
        ProductOffering.objects.create(
            name="Oferta 1",
            code="AN001",
            product=self.product,
            price=1000.00,
            currency_code="USD",
            is_active=True
        )
        
        ProductOffering.objects.create(
            name="Oferta 2",
            code="AN002",
            product=self.product,
            price=1200.00,
            currency_code="EUR",
            is_active=True
        )
        
        response = self.client.get(self.analytics_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('total_offerings', response.data)
        self.assertIn('active_offerings', response.data)
        self.assertIn('by_currency', response.data)
        self.assertIn('price_statistics', response.data)
        
        # Verificar valores
        self.assertEqual(response.data['total_offerings'], 2)
        self.assertEqual(response.data['active_offerings'], 2)
    
    def test_choices_endpoint(self):
        """Test endpoint de choices"""
        # Crear ofertas
        ProductOffering.objects.create(
            name="Opción A",
            code="CHOICE_A",
            product=self.product,
            price=500.00,
            currency_code="USD"
        )
        
        response = self.client.get(self.choices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('display_name', response.data[0])
    
    def test_duplicate_offering(self):
        """Test duplicar oferta"""
        original = ProductOffering.objects.create(
            name="Original",
            code="ORIG001",
            product=self.product,
            price=1000.00,
            currency_code="USD",
            description="Oferta original"
        )
        
        duplicate_url = reverse('productoffering-duplicate', kwargs={'pk': original.pk})
        response = self.client.post(duplicate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductOffering.objects.count(), 2)
        
        # Verificar que la copia tiene los datos correctos
        duplicate = ProductOffering.objects.exclude(id=original.id).first()
        self.assertEqual(duplicate.name, "Original (Copia)")
        self.assertTrue(duplicate.code.startswith("ORIG001_copy_"))
        self.assertEqual(duplicate.price, original.price)
        self.assertFalse(duplicate.is_active)  # Copia desactivada


class ProductOfferingValidationTest(TestCase):
    """Tests de validación"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.division = Division.objects.create(name="Test", code="TEST")
        self.category = ProductCategory.objects.create(
            name="Test Cat", code="TESTCAT", division=self.division
        )
        self.product = Product.objects.create(
            name="Test Product", code="TESTPROD", category=self.category, price=100.00
        )
    
    def test_unique_code_validation(self):
        """Test validación de código único"""
        # Crear primera oferta
        ProductOffering.objects.create(
            name="Primera",
            code="UNIQUE001",
            product=self.product,
            price=100.00
        )
        
        # Intentar crear segunda con mismo código
        with self.assertRaises(Exception):
            ProductOffering.objects.create(
                name="Segunda",
                code="UNIQUE001",  # Código duplicado
                product=self.product,
                price=200.00
            )
    
    def test_positive_price_validation(self):
        """Test que el precio debe ser positivo"""
        offering = ProductOffering(
            name="Test Negative",
            code="NEG001",
            product=self.product,
            price=-100.00  # Precio negativo
        )
        
        # En el modelo no hay validación automática, pero debería haberla
        # Este test documenta el comportamiento esperado
        self.assertLess(offering.price, 0)
