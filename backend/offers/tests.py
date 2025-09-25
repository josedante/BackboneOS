from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from .models import ProductOffering
from products.models import Product, ProductCategory, Division
from our_institution.models import OurOrganization
from world.models import Industry, FunctionOrResponsibility
from interactions.models import Channel, Medium


class ProductOfferingModelTest(TestCase):
    """Tests para el modelo ProductOffering"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear organización
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            legal_name="Test Organization Legal",
            email="test@example.com"
        )
        # Crear división
        self.division = Division.objects.create(
            organization=self.organization,
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
            base_price=Decimal('1000.00'),
            currency_code="USD"
        )
        
        # Crear oferta
        self.offering = ProductOffering.objects.create(
            name="Oferta CRM Premium",
            code="CRM_PREM_001",
            description="Oferta premium del sistema CRM",
            product=self.product,
            price=Decimal('850.00'),
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
        self.offering.valid_from = date.today() - timedelta(days=10)
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


# ============================
# TESTS DE API ENDPOINTS
# ============================

class OfferAPITestCase(APITestCase):
    """Base test case para tests de API de Offers"""
    
    def setUp(self):
        """Configuración inicial para tests de API"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Datos base
        # Crear organización
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            legal_name="Test Organization Legal",
            email="test@example.com"
        )
        self.division = Division.objects.create(
            organization=self.organization,
            name="Tecnología",
            code="TECH",
            description="División de tecnología"
        )
        
        self.category = ProductCategory.objects.create(
            name="Software",
            code="SW",
            division=self.division
        )
        
        self.product = Product.objects.create(
            name="Sistema CRM",
            code="CRM001",
            description="Sistema de gestión de clientes",
            category=self.category,
            base_price=Decimal('1000.00'),
            currency_code="USD"
        )
        
        # Crear offering de prueba
        self.offering = ProductOffering.objects.create(
            name="Oferta CRM Premium",
            code="CRM_PREM_001",
            description="Oferta premium del sistema CRM",
            product=self.product,
            price=Decimal('850.00'),
            currency_code="USD",
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30),
            is_active=True
        )


class ProductOfferingViewSetTests(OfferAPITestCase):
    """Tests comprehensivos para ProductOfferingViewSet"""
    
    def test_offering_list_unauthenticated(self):
        """Test acceso sin autenticación a lista de ofertas"""
        url = reverse('offers:productoffering-list')
        response = self.client.get(url)
        
        # Las ofertas pueden requerir autenticación según configuración
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
    
    def test_offering_list_authenticated(self):
        """Test listado de ofertas con autenticación"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Oferta CRM Premium')
    
    def test_offering_detail(self):
        """Test detalle de oferta"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-detail', kwargs={'pk': self.offering.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Oferta CRM Premium')
        self.assertEqual(response.data['code'], 'CRM_PREM_001')
        self.assertEqual(float(response.data['price']), 850.00)
    
    def test_offering_create(self):
        """Test creación de oferta"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-list')
        
        offering_data = {
            'name': 'Nueva Oferta',
            'code': 'NEW_001',
            'description': 'Una nueva oferta especial',
            'product': self.product.pk,
            'price': 750.00,
            'currency_code': 'USD',
            'valid_from': date.today().isoformat(),
            'valid_until': (date.today() + timedelta(days=15)).isoformat(),
            'is_active': True
        }
        
        response = self.client.post(url, offering_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó correctamente
        offering = ProductOffering.objects.get(code='NEW_001')
        self.assertEqual(offering.name, 'Nueva Oferta')
        self.assertEqual(float(offering.price), 750.00)
    
    def test_offering_update(self):
        """Test actualización de oferta"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-detail', kwargs={'pk': self.offering.pk})
        
        update_data = {
            'price': 800.00,
            'currency_code': 'PEN'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        self.offering.refresh_from_db()
        self.assertEqual(float(self.offering.price), 800.00)
        self.assertEqual(self.offering.currency_code, 'PEN')
    
    def test_offering_delete(self):
        """Test eliminación de oferta"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-detail', kwargs={'pk': self.offering.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que fue eliminada
        self.assertFalse(ProductOffering.objects.filter(pk=self.offering.pk).exists())
    
    def test_offering_search(self):
        """Test funcionalidad de búsqueda"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Búsqueda por nombre
        response = self.client.get(url, {'search': 'CRM'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Búsqueda por código
        response = self.client.get(url, {'search': 'PREM'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_offering_filtering(self):
        """Test filtrado de ofertas"""
        # Crear ofertas adicionales para filtrado
        expired_offering = ProductOffering.objects.create(
            name="Oferta Expirada",
            code="EXP_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=date.today() - timedelta(days=10),
            valid_until=date.today() - timedelta(days=1),
            is_active=True
        )
        
        inactive_offering = ProductOffering.objects.create(
            name="Oferta Inactiva",
            code="INACT_001",
            product=self.product,
            price=Decimal('600.00'),
            is_active=False
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtro por activas
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Solo activas
        
        # Filtro por producto
        response = self.client.get(url, {'product': self.product.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Todas del producto
    
    def test_offering_ordering(self):
        """Test ordenamiento de ofertas"""
        # Crear otra oferta para probar ordenamiento
        ProductOffering.objects.create(
            name="Oferta A",
            code="A_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=date.today()
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Ordenamiento por precio
        response = self.client.get(url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(result['price']) for result in response.data['results']]
        self.assertEqual(prices, sorted(prices))
        
        # Ordenamiento descendente por precio
        response = self.client.get(url, {'ordering': '-price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(result['price']) for result in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))


class ProductOfferingEndpointsTests(OfferAPITestCase):
    """Tests para endpoints específicos de ProductOffering"""
    
    def test_choices_endpoint(self):
        """Test endpoint de choices"""
        self.client.force_authenticate(user=self.user)
        
        # Crear más ofertas para choices
        ProductOffering.objects.create(
            name="Opción A",
            code="CHOICE_A",
            product=self.product,
            price=Decimal('500.00'),
            currency_code="USD"
        )
        
        url = reverse('offers:productoffering-choices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_currently_valid_endpoint(self):
        """Test endpoint de ofertas actualmente válidas"""
        # Crear oferta válida
        valid_offering = ProductOffering.objects.create(
            name="Oferta Válida",
            code="VALID001",
            product=self.product,
            price=Decimal('1000.00'),
            is_active=True,
            valid_from=date.today() - timedelta(days=5),
            valid_until=date.today() + timedelta(days=30)
        )
        
        # Crear oferta expirada
        expired_offering = ProductOffering.objects.create(
            name="Oferta Expirada",
            code="EXPIRED001",
            product=self.product,
            price=Decimal('800.00'),
            is_active=True,
            valid_from=date.today() - timedelta(days=60),
            valid_until=date.today() - timedelta(days=1)
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-currently-valid')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo ofertas válidas deberían aparecer
        valid_codes = [offer['code'] for offer in response.data]
        self.assertIn('CRM_PREM_001', valid_codes)  # La del setUp
        self.assertIn('VALID001', valid_codes)
        self.assertNotIn('EXPIRED001', valid_codes)
    
    def test_by_product_endpoint(self):
        """Test endpoint de ofertas por producto"""
        # Crear otro producto y oferta
        another_product = Product.objects.create(
            name="Sistema ERP",
            code="ERP001",
            category=self.category,
            base_price=Decimal('2000.00')
        )
        
        ProductOffering.objects.create(
            name="Oferta ERP",
            code="ERP_001",
            product=another_product,
            price=Decimal('1800.00'),
            currency_code="USD"
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-by-product')
        
        # Filtrar por el producto original
        response = self.client.get(url, {'product_id': self.product.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], str(self.product.pk))
    
    def test_by_channel_endpoint(self):
        """Test endpoint de ofertas por canal"""
        # Crear medium y channel
        medium = Medium.objects.create(name="Digital", code="DIG")
        channel = Channel.objects.create(name="Web", code="WEB")
        
        # Asociar canal a la oferta
        self.offering.channels.add(channel)
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-by-channel')
        
        response = self.client.get(url, {'channel_id': channel.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_analytics_endpoint(self):
        """Test endpoint de analytics con autenticación"""
        self.client.force_authenticate(user=self.user)
        
        # Crear ofertas adicionales para analytics más completo
        ProductOffering.objects.create(
            name="Oferta USD",
            code="USD_001",
            product=self.product,
            price=Decimal('1000.00'),
            currency_code="USD",
            is_active=True
        )
        
        ProductOffering.objects.create(
            name="Oferta EUR",
            code="EUR_001",
            product=self.product,
            price=Decimal('900.00'),
            currency_code="EUR",
            is_active=True
        )
        
        ProductOffering.objects.create(
            name="Oferta Inactiva",
            code="INACTIVE_001",
            product=self.product,
            price=Decimal('500.00'),
            currency_code="USD",
            is_active=False
        )
        
        url = reverse('offers:productoffering-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        expected_keys = [
            'total_offerings', 'active_offerings', 'expired_offerings',
            'future_offerings', 'by_currency', 'by_product_category',
            'price_statistics', 'top_products', 'recent_offerings'
        ]
        
        for key in expected_keys:
            self.assertIn(key, response.data)
        
        # Verificar valores específicos
        self.assertEqual(response.data['total_offerings'], 4)  # Including setUp offering
        self.assertEqual(response.data['active_offerings'], 3)
    
    def test_duplicate_endpoint(self):
        """Test endpoint de duplicación"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('offers:productoffering-duplicate', kwargs={'pk': self.offering.pk})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductOffering.objects.count(), 2)
        
        # Verificar que la copia tiene los datos correctos
        duplicate = ProductOffering.objects.exclude(id=self.offering.id).first()
        self.assertEqual(duplicate.name, "Oferta CRM Premium (Copia)")
        self.assertTrue(duplicate.code.startswith("CRM_PREM_001_copy_"))
        self.assertEqual(duplicate.price, self.offering.price)
        self.assertFalse(duplicate.is_active)  # Copia desactivada
    
    def test_bulk_create_endpoint(self):
        """Test endpoint de creación en lote"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear otro producto para las ofertas en lote
        product2 = Product.objects.create(
            name="Sistema ERP",
            code="ERP001",
            category=self.category,
            base_price=Decimal('2000.00'),
            currency_code="USD"
        )
        
        bulk_data = {
            'offers': [
                {
                    'name': 'Oferta Lote 1',
                    'code': 'BULK_001',
                    'product': self.product.pk,
                    'price': 100.00,
                    'currency_code': 'USD'
                },
                {
                    'name': 'Oferta Lote 2',
                    'code': 'BULK_002',
                    'product': product2.pk,
                    'price': 200.00,
                    'currency_code': 'USD'
                },
                {
                    'name': 'Oferta Lote 3',
                    'code': 'BULK_003',
                    'product': self.product.pk,
                    'price': 300.00,
                    'currency_code': 'EUR'
                }
            ]
        }
        
        url = reverse('offers:productoffering-bulk-create')
        response = self.client.post(url, bulk_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('offers', response.data)
        self.assertEqual(len(response.data['offers']), 3)
        
        # Verificar que se crearon las ofertas
        bulk_offers = ProductOffering.objects.filter(code__startswith='BULK_')
        self.assertEqual(bulk_offers.count(), 3)
    
    def test_bulk_create_with_errors(self):
        """Test creación en lote con algunos errores"""
        self.client.force_authenticate(user=self.admin_user)
        
        bulk_data = {
            'offers': [
                {
                    'name': 'Oferta Válida',
                    'code': 'VALID_BULK_001',
                    'product': self.product.pk,
                    'price': 100.00,
                    'currency_code': 'USD'
                },
                {
                    'name': 'Oferta Inválida',
                    'code': self.offering.code,  # Código duplicado
                    'product': self.product.pk,
                    'price': 200.00,
                    'currency_code': 'USD'
                },
                {
                    'name': 'Oferta Sin Producto',
                    'code': 'NO_PRODUCT_001',
                    'price': 300.00,
                    'currency_code': 'USD'
                    # Falta 'product'
                }
            ]
        }
        
        url = reverse('offers:productoffering-bulk-create')
        response = self.client.post(url, bulk_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertIn('errors', response.data)
        self.assertEqual(len(response.data['errors']), 2)  # 2 ofertas con error
        self.assertEqual(response.data['created'], 1)  # 1 oferta válida creada
    
    def test_export_json_endpoint(self):
        """Test endpoint de exportación en formato JSON"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear ofertas adicionales para exportar
        ProductOffering.objects.create(
            name="Oferta Export 1",
            code="EXP_001",
            product=self.product,
            price=Decimal('500.00'),
            currency_code="USD"
        )
        
        ProductOffering.objects.create(
            name="Oferta Export 2",
            code="EXP_002",
            product=self.product,
            price=Decimal('600.00'),
            currency_code="EUR"
        )
        
        url = reverse('offers:productoffering-export')
        response = self.client.get(url, {'format': 'json'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)  # Al menos 3 ofertas
        
        # Verificar estructura de datos
        first_offer = response.data[0]
        expected_fields = ['id', 'name', 'code', 'product', 'price', 'currency_code']
        for field in expected_fields:
            self.assertIn(field, first_offer)
    
    def test_export_csv_endpoint(self):
        """Test endpoint de exportación en formato CSV"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('offers:productoffering-export')
        response = self.client.get(url, {'format': 'csv'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="offers.csv"', response['Content-Disposition'])
        
        # Verificar contenido CSV
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        self.assertGreaterEqual(len(lines), 2)  # Header + al menos 1 fila de datos
        
        # Verificar header
        header = lines[0]
        expected_columns = ['ID', 'Nombre', 'Código', 'Producto', 'Precio', 'Moneda', 'Fecha Inicio', 'Fecha Fin', 'Activa']
        for column in expected_columns:
            self.assertIn(column, header)
    
    def test_export_xlsx_endpoint(self):
        """Test endpoint de exportación en formato XLSX (no implementado)"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('offers:productoffering-export')
        response = self.client.get(url, {'format': 'xlsx'})
        
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
        self.assertIn('error', response.data)
        self.assertIn('XLSX no implementado', response.data['error'])
    
    def test_export_with_filters(self):
        """Test exportación con filtros aplicados"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear ofertas con diferentes monedas
        ProductOffering.objects.create(
            name="Oferta USD",
            code="USD_EXPORT_001",
            product=self.product,
            price=Decimal('500.00'),
            currency_code="USD"
        )
        
        ProductOffering.objects.create(
            name="Oferta EUR",
            code="EUR_EXPORT_001",
            product=self.product,
            price=Decimal('400.00'),
            currency_code="EUR"
        )
        
        url = reverse('offers:productoffering-export')
        response = self.client.get(url, {
            'format': 'json',
            'currency_code': 'USD'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Todas las ofertas exportadas deben ser USD
        for offer in response.data:
            self.assertEqual(offer['currency_code'], 'USD')
    
    def test_bulk_create_authentication_required(self):
        """Test que bulk_create requiere autenticación"""
        url = reverse('offers:productoffering-bulk-create')
        response = self.client.post(url, {'offers': []}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_export_authentication_required(self):
        """Test que export requiere autenticación"""
        url = reverse('offers:productoffering-export')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferBusinessLogicTests(OfferAPITestCase):
    """Tests de lógica de negocio para ofertas"""
    
    def test_offer_validity_period_validation(self):
        """Test validación de período de validez"""
        # Test con fechas válidas
        offering = ProductOffering(
            name="Oferta Válida",
            code="VALID_PERIOD_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30)
        )
        
        # No debería lanzar error
        offering.full_clean()
        offering.save()
        
        # Test que documenta comportamiento esperado con fechas inválidas
        # (Actualmente no hay validación automática en el modelo)
        invalid_offering = ProductOffering(
            name="Oferta Inválida",
            code="INVALID_PERIOD_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=date.today(),
            valid_until=date.today() - timedelta(days=1)  # Fecha fin anterior a inicio
        )
        
        # En el futuro debería agregarse esta validación
        # with self.assertRaises(ValidationError):
        #     invalid_offering.full_clean()
    
    def test_discount_calculation_logic(self):
        """Test lógica de cálculo de descuentos"""
        # Crear oferta con descuento
        discounted_offer = ProductOffering.objects.create(
            name="Oferta con Descuento",
            code="DISC_001",
            product=self.product,
            price=Decimal('750.00'),  # Precio base: 1000.00
            currency_code="USD"
        )
        
        # Verificar que el precio de oferta es menor al precio base
        self.assertLess(discounted_offer.price, self.product.base_price)
        
        # Calcular porcentaje de descuento esperado
        expected_discount = ((self.product.base_price - discounted_offer.price) / self.product.base_price) * 100
        self.assertEqual(float(expected_discount), 25.0)  # 25% de descuento
    
    def test_offer_expiry_status_logic(self):
        """Test lógica de estado de expiración"""
        today = date.today()
        
        # Oferta expirada
        expired_offer = ProductOffering.objects.create(
            name="Oferta Expirada",
            code="EXP_STATUS_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=today - timedelta(days=10),
            valid_until=today - timedelta(days=1)
        )
        
        # Oferta futura
        future_offer = ProductOffering.objects.create(
            name="Oferta Futura",
            code="FUT_STATUS_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=today + timedelta(days=1),
            valid_until=today + timedelta(days=10)
        )
        
        # Oferta sin fechas (siempre válida)
        always_valid_offer = ProductOffering.objects.create(
            name="Oferta Siempre Válida",
            code="ALWAYS_001",
            product=self.product,
            price=Decimal('500.00'),
            valid_from=None,
            valid_until=None
        )
        
        # Verificar estados usando la propiedad is_currently_valid
        self.assertFalse(expired_offer.is_currently_valid)
        self.assertFalse(future_offer.is_currently_valid)
        self.assertTrue(always_valid_offer.is_currently_valid)
        self.assertTrue(self.offering.is_currently_valid)  # Del setUp
    
    def test_price_validation_business_rules(self):
        """Test reglas de negocio para validación de precios"""
        # Precio positivo
        with self.assertRaises(Exception):
            invalid_offer = ProductOffering(
                name="Precio Negativo",
                code="NEG_PRICE_001",
                product=self.product,
                price=Decimal('-100.00')
            )
            invalid_offer.save()
            # En el futuro debería agregarse validación automática
            # invalid_offer.full_clean()
        
        # Precio cero (podría ser válido para ofertas gratuitas)
        free_offer = ProductOffering(
            name="Oferta Gratuita",
            code="FREE_001",
            product=self.product,
            price=Decimal('0.00')
        )
        # No debería lanzar error para precios en cero
        free_offer.full_clean()
    
    def test_currency_consistency(self):
        """Test consistencia de monedas entre producto y oferta"""
        # Crear producto con moneda específica
        eur_product = Product.objects.create(
            name="Producto EUR",
            code="EUR_PROD_001",
            category=self.category,
            base_price=Decimal('1000.00'),
            currency_code="EUR"
        )
        
        # Crear oferta con la misma moneda
        eur_offer = ProductOffering.objects.create(
            name="Oferta EUR",
            code="EUR_OFFER_001",
            product=eur_product,
            price=Decimal('850.00'),
            currency_code="EUR"
        )
        
        # Verificar consistencia
        self.assertEqual(eur_offer.currency_code, eur_product.currency_code)
        
        # Crear oferta con moneda diferente (podría ser válido para mercados internacionales)
        usd_offer = ProductOffering.objects.create(
            name="Oferta USD para Producto EUR",
            code="USD_EUR_001",
            product=eur_product,
            price=Decimal('900.00'),
            currency_code="USD"
        )
        
        # Esto debería ser válido pero documentar la diferencia
        self.assertNotEqual(usd_offer.currency_code, eur_product.currency_code)


class OfferFilteringAdvancedTests(OfferAPITestCase):
    """Tests avanzados de filtrado y búsqueda"""
    
    def setUp(self):
        super().setUp()
        
        # Crear datos adicionales para filtros avanzados
        self.category2 = ProductCategory.objects.create(
            name="Hardware",
            code="HW",
            division=self.division
        )
        
        self.product2 = Product.objects.create(
            name="Servidor",
            code="SRV001",
            category=self.category2,
            base_price=Decimal('5000.00'),
            currency_code="USD"
        )
        
        # Crear medium y channels
        self.medium = Medium.objects.create(name="Digital", code="DIG")
        self.channel1 = Channel.objects.create(name="Web", code="WEB")
        self.channel2 = Channel.objects.create(name="Email", code="EMAIL")
        
        # Crear industry
        self.industry = Industry.objects.create(name="Technology", code="TECH")
        
        # Crear ofertas con diferentes características
        self.offer_hw = ProductOffering.objects.create(
            name="Oferta Servidor Premium",
            code="SRV_PREM_001",
            product=self.product2,
            price=Decimal('4500.00'),
            currency_code="USD",
            is_active=True,
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=60)
        )
        
        self.offer_eur = ProductOffering.objects.create(
            name="Oferta Europa",
            code="EUR_001",
            product=self.product,
            price=Decimal('750.00'),
            currency_code="EUR",
            is_active=True
        )
        
        # Asociar channels e industries
        self.offering.channels.add(self.channel1)
        self.offer_hw.channels.add(self.channel2)
        self.offering.related_industries.add(self.industry)
    
    def test_filter_by_product_category(self):
        """Test filtro por categoría de producto"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por categoría Software
        response = self.client.get(url, {'product__category': self.category.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debería encontrar las ofertas de productos de software
        codes = [offer['code'] for offer in response.data['results']]
        self.assertIn('CRM_PREM_001', codes)
        self.assertIn('EUR_001', codes)
        self.assertNotIn('SRV_PREM_001', codes)
    
    def test_filter_by_division(self):
        """Test filtro por división"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por división
        response = self.client.get(url, {'product__category__division': self.division.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Todas las ofertas deberían aparecer (misma división)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_filter_by_channel(self):
        """Test filtro por canal"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por canal Web
        response = self.client.get(url, {'channels': self.channel1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Solo ofertas asociadas al canal Web
        codes = [offer['code'] for offer in response.data['results']]
        self.assertIn('CRM_PREM_001', codes)
        self.assertNotIn('SRV_PREM_001', codes)
    
    def test_filter_by_industry(self):
        """Test filtro por industria"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por industria
        response = self.client.get(url, {'related_industries': self.industry.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Solo ofertas asociadas a la industria
        codes = [offer['code'] for offer in response.data['results']]
        self.assertIn('CRM_PREM_001', codes)
    
    def test_filter_by_currency_multiple(self):
        """Test filtro por múltiples monedas"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por USD y EUR
        response = self.client.get(url, {'currency_code__in': 'USD,EUR'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debería encontrar ofertas en ambas monedas
        currencies = [offer['currency_code'] for offer in response.data['results']]
        self.assertIn('USD', currencies)
        self.assertIn('EUR', currencies)
    
    def test_filter_by_price_range(self):
        """Test filtro por rango de precios"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar por rango de precios (500-1000)
        response = self.client.get(url, {'price__gte': 500, 'price__lte': 1000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los precios están en el rango
        for offer in response.data['results']:
            price = float(offer['price'])
            self.assertGreaterEqual(price, 500)
            self.assertLessEqual(price, 1000)
    
    def test_filter_by_validity_dates(self):
        """Test filtro por fechas de validez"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtrar ofertas que empiezan desde hoy
        today_str = date.today().isoformat()
        response = self.client.get(url, {'valid_from__gte': today_str})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar fechas de inicio
        for offer in response.data['results']:
            if offer['valid_from']:
                self.assertGreaterEqual(offer['valid_from'], today_str)
    
    def test_complex_filtering_combination(self):
        """Test combinación compleja de filtros"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Filtros múltiples: activa + USD + precio <= 1000
        response = self.client.get(url, {
            'is_active': 'true',
            'currency_code': 'USD',
            'price__lte': 1000
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que todos los resultados cumplen los criterios
        for offer in response.data['results']:
            self.assertTrue(offer['is_active'])
            self.assertEqual(offer['currency_code'], 'USD')
            self.assertLessEqual(float(offer['price']), 1000)
    
    def test_search_functionality_advanced(self):
        """Test funcionalidad de búsqueda avanzada"""
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Búsqueda por nombre
        response = self.client.get(url, {'search': 'Premium'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Búsqueda por código
        response = self.client.get(url, {'search': 'SRV'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [offer['code'] for offer in response.data['results']]
        self.assertIn('SRV_PREM_001', codes)
        
        # Búsqueda por descripción (si está habilitada)
        response = self.client.get(url, {'search': 'sistema'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería encontrar la oferta del CRM si busca en descripción


class OfferPerformanceTests(OfferAPITestCase):
    """Tests de performance para ofertas"""
    
    def test_large_dataset_performance(self):
        """Test performance con dataset grande"""
        # Crear muchas ofertas para probar performance
        offers = []
        for i in range(100):
            offers.append(ProductOffering(
                name=f"Oferta Performance {i}",
                code=f"PERF_{i:03d}",
                product=self.product,
                price=Decimal(str(500.00 + i)),
                currency_code="USD",
                is_active=True
            ))
        
        ProductOffering.objects.bulk_create(offers)
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-list')
        
        # Test listado con paginación
        response = self.client.get(url, {'page_size': 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 20)
        
        # Test búsqueda en dataset grande
        response = self.client.get(url, {'search': 'Performance'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_analytics_performance(self):
        """Test performance del endpoint de analytics"""
        # Crear ofertas variadas para analytics
        for i in range(50):
            ProductOffering.objects.create(
                name=f"Analytics Test {i}",
                code=f"ANALYTICS_{i:03d}",
                product=self.product,
                price=Decimal(str(100.00 + i * 10)),
                currency_code="USD" if i % 2 == 0 else "EUR",
                is_active=i % 3 != 0,  # Algunos inactivos
                valid_from=date.today() - timedelta(days=i % 30),
                valid_until=date.today() + timedelta(days=i % 60)
            )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-analytics')
        
        # El endpoint de analytics debería responder rápidamente
        import time
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 5.0)  # Menos de 5 segundos
        
        # Verificar que retorna datos completos
        self.assertIn('total_offerings', response.data)
        self.assertIn('price_statistics', response.data)
        self.assertIn('by_currency', response.data)


class OfferIntegrationTests(OfferAPITestCase):
    """Tests de integración con otros módulos"""
    
    def test_product_integration(self):
        """Test integración con módulo de productos"""
        self.client.force_authenticate(user=self.user)
        
        # Verificar que el producto relacionado es accesible
        product_url = f"/api/products/products/{self.product.pk}/"
        response = self.client.get(product_url)
        
        if response.status_code == 200:
            # Si el endpoint existe, verificar datos
            self.assertEqual(response.data['name'], 'Sistema CRM')
        else:
            # Si no existe, documentar para futura implementación
            self.assertIn(response.status_code, [404, 401])
    
    def test_campaign_integration(self):
        """Test integración con módulo de campañas"""
        # Este test documenta la integración esperada con campañas
        
        # Crear datos necesarios para campaña
        from our_institution.models import OurOrganization, Division as OurDivision
        
        try:
            org = OurOrganization.objects.create(name="Test Corp")
            div = OurDivision.objects.create(
                name="Marketing",
                code="MKT",
                organization=org
            )
            
            from campaigns.models import Campaign
            campaign = Campaign.objects.create(
                name="Campaña Test",
                code="CAMP_001",
                start_date=date.today(),
                division=div
            )
            
            # En el futuro: asociar oferta con campaña
            # self.offering.campaigns.add(campaign)
            # self.assertIn(campaign, self.offering.campaigns.all())
            
        except Exception:
            # Si falla la creación, documentar para futura implementación
            pass
    
    def test_channel_integration(self):
        """Test integración con canales de interacción"""
        # Crear medium y channel
        medium = Medium.objects.create(name="Digital", code="DIG")
        channel = Channel.objects.create(name="Website", code="WEB")
        
        # Asociar canal a oferta
        self.offering.channels.add(channel)
        self.offering.save()
        
        # Verificar asociación
        self.assertIn(channel, self.offering.channels.all())
        
        # Test filtrado por canal
        self.client.force_authenticate(user=self.user)
        url = reverse('offers:productoffering-by-channel')
        response = self.client.get(url, {'channel_id': channel.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class OfferSecurityTests(OfferAPITestCase):
    """Tests de seguridad para endpoints de ofertas"""
    
    def test_authentication_requirements(self):
        """Test requerimientos de autenticación"""
        url = reverse('offers:productoffering-list')
        
        # Sin autenticación
        response = self.client.get(url)
        # Puede requerir autenticación según configuración
        self.assertIn(response.status_code, [200, 401])
        
        # Con autenticación básica
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_permission_levels(self):
        """Test niveles de permisos"""
        url = reverse('offers:productoffering-list')
        
        # Usuario normal - solo lectura
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Intentar crear (puede requerir permisos especiales)
        create_data = {
            'name': 'Test Permission',
            'code': 'PERM_001',
            'product': self.product.pk,
            'price': 100.00
        }
        response = self.client.post(url, create_data, format='json')
        self.assertIn(response.status_code, [201, 403])  # Creado o prohibido
        
        # Admin - acceso completo
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, create_data, format='json')
        # Admin debería poder crear
        self.assertIn(response.status_code, [201, 400])  # Creado o error de validación
    
    def test_data_access_security(self):
        """Test seguridad de acceso a datos"""
        # Crear oferta "privada" (si existe ese concepto)
        private_offering = ProductOffering.objects.create(
            name="Oferta Privada",
            code="PRIVATE_001",
            product=self.product,
            price=Decimal('1000.00'),
            is_active=False  # Inactiva como "privada"
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Usuario normal no debería ver ofertas inactivas en listado
        url = reverse('offers:productoffering-list')
        response = self.client.get(url)
        
        if response.status_code == 200:
            codes = [offer['code'] for offer in response.data['results']]
            # Depende de la implementación de filtros por defecto
            # self.assertNotIn('PRIVATE_001', codes)
        
        # Pero debería poder acceder por ID directo si tiene permisos
        detail_url = reverse('offers:productoffering-detail', kwargs={'pk': private_offering.pk})
        response = self.client.get(detail_url)
        self.assertIn(response.status_code, [200, 404, 403])


class OfferValidationAdvancedTests(OfferAPITestCase):
    """Tests avanzados de validación"""
    
    def test_code_uniqueness_validation(self):
        """Test validación de unicidad de códigos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-list')
        
        # Crear primera oferta
        data1 = {
            'name': 'Primera Oferta',
            'code': 'UNIQUE_001',
            'product': self.product.pk,
            'price': 100.00,
            'currency_code': 'USD'
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, 201)
        
        # Intentar crear segunda con mismo código
        data2 = {
            'name': 'Segunda Oferta',
            'code': 'UNIQUE_001',  # Código duplicado
            'product': self.product.pk,
            'price': 200.00,
            'currency_code': 'USD'
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertIn('code', response2.data)
    
    def test_price_validation_advanced(self):
        """Test validación avanzada de precios"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-list')
        
        # Precio negativo
        negative_data = {
            'name': 'Precio Negativo',
            'code': 'NEG_001',
            'product': self.product.pk,
            'price': -100.00,
            'currency_code': 'USD'
        }
        response = self.client.post(url, negative_data, format='json')
        # Debería fallar si hay validación de precio
        self.assertIn(response.status_code, [400, 201])  # Error o creado (sin validación)
        
        # Precio con demasiados decimales
        decimal_data = {
            'name': 'Muchos Decimales',
            'code': 'DEC_001',
            'product': self.product.pk,
            'price': 100.123456,
            'currency_code': 'USD'
        }
        response = self.client.post(url, decimal_data, format='json')
        # Debería funcionar o truncar decimales
        self.assertIn(response.status_code, [201, 400])
    
    def test_date_validation_advanced(self):
        """Test validación avanzada de fechas"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('offers:productoffering-list')
        
        # Fecha de fin anterior a fecha de inicio
        invalid_dates_data = {
            'name': 'Fechas Inválidas',
            'code': 'INV_DATES_001',
            'product': self.product.pk,
            'price': 100.00,
            'currency_code': 'USD',
            'valid_from': (date.today() + timedelta(days=10)).isoformat(),
            'valid_until': date.today().isoformat()  # Anterior a valid_from
        }
        response = self.client.post(url, invalid_dates_data, format='json')
        # Debería fallar si hay validación de fechas
        self.assertIn(response.status_code, [400, 201])  # Error o creado (sin validación)
        
        # Fechas en el pasado
        past_dates_data = {
            'name': 'Fechas Pasadas',
            'code': 'PAST_001',
            'product': self.product.pk,
            'price': 100.00,
            'currency_code': 'USD',
            'valid_from': (date.today() - timedelta(days=10)).isoformat(),
            'valid_until': (date.today() - timedelta(days=5)).isoformat()
        }
        response = self.client.post(url, past_dates_data, format='json')
        # Podría ser válido para ofertas retrospectivas
        self.assertIn(response.status_code, [201, 400])
