from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import date, timedelta
from decimal import Decimal

from .models import Campaign, CampaignTouchpoint
from our_institution.models import OurOrganization, Division, Team
from interactions.models import Medium, Channel, TouchpointType, Touchpoint
from world.models import Industry, FunctionOrResponsibility, MarketSegment, Tag
from products.models import Product, ProductCategory
from offers.models import ProductOffering


class CampaignModelTests(TestCase):
    """Tests para el modelo Campaign"""

    def setUp(self):
        # Crear organización, división y equipo de prueba
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.team = Team.objects.create(
            name="Test Team",
            code="TEST_TEAM",
            division=self.division
        )

    def test_campaign_creation(self):
        """Test de creación básica de campaña"""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            code="TEST_CAMP_001",
            description="Test campaign description",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            division=self.division,
            team=self.team
        )
        
        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.code, "TEST_CAMP_001")
        self.assertTrue(campaign.is_active)
        self.assertEqual(str(campaign), "Test Campaign")

    def test_campaign_is_active_now_property(self):
        """Test de la propiedad is_active_now"""
        # Campaña activa actual
        active_campaign = Campaign.objects.create(
            name="Active Campaign",
            code="ACTIVE_001",
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=25),
            division=self.division
        )
        
        # Campaña futura
        future_campaign = Campaign.objects.create(
            name="Future Campaign",
            code="FUTURE_001",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=40),
            division=self.division
        )
        
        # Campaña pasada
        past_campaign = Campaign.objects.create(
            name="Past Campaign",
            code="PAST_001",
            start_date=date.today() - timedelta(days=40),
            end_date=date.today() - timedelta(days=10),
            division=self.division
        )
        
        self.assertTrue(active_campaign.is_active_now)
        self.assertFalse(future_campaign.is_active_now)
        self.assertFalse(past_campaign.is_active_now)

    def test_campaign_subcampaigns_relationship(self):
        """Test de la relación jerárquica de campañas"""
        parent_campaign = Campaign.objects.create(
            name="Parent Campaign",
            code="PARENT_001",
            start_date=date.today(),
            division=self.division
        )
        
        subcampaign = Campaign.objects.create(
            name="Sub Campaign",
            code="SUB_001",
            start_date=date.today(),
            parent=parent_campaign,
            division=self.division
        )
        
        self.assertEqual(subcampaign.parent, parent_campaign)
        self.assertIn(subcampaign, parent_campaign.subcampaigns.all())

    def test_campaign_unique_code_constraint(self):
        """Test de la restricción de código único"""
        Campaign.objects.create(
            name="First Campaign",
            code="UNIQUE_001",
            start_date=date.today(),
            division=self.division
        )
        
        with self.assertRaises(Exception):
            Campaign.objects.create(
                name="Second Campaign",
                code="UNIQUE_001",  # Código duplicado
                start_date=date.today(),
                division=self.division
            )

    def test_campaign_content_type_field(self):
        """Test del campo content_type"""
        # Test con content_type válido
        campaign = Campaign.objects.create(
            name="Product Campaign",
            code="PROD_CAMP_001",
            start_date=date.today(),
            content_type="product",
            division=self.division
        )
        
        self.assertEqual(campaign.content_type, "product")
        
        # Test con content_type None (opcional)
        campaign_none = Campaign.objects.create(
            name="Generic Campaign",
            code="GEN_CAMP_001",
            start_date=date.today(),
            division=self.division
        )
        
        self.assertIsNone(campaign_none.content_type)
        
        # Test con todos los valores de choice
        choices = ["affinity", "category", "product", "brand"]
        for i, choice in enumerate(choices):
            Campaign.objects.create(
                name=f"Test {choice.title()} Campaign",
                code=f"TEST_{choice.upper()}_{i:03d}",
                start_date=date.today(),
                content_type=choice,
                division=self.division
            )
        
        # Verificar que se crearon correctamente
        self.assertEqual(Campaign.objects.filter(content_type="affinity").count(), 1)
        self.assertEqual(Campaign.objects.filter(content_type="category").count(), 1)
        self.assertEqual(Campaign.objects.filter(content_type="product").count(), 2)  # Incluye la primera
        self.assertEqual(Campaign.objects.filter(content_type="brand").count(), 1)


class CampaignTouchpointModelTests(TestCase):
    """Tests para el modelo CampaignTouchpoint"""

    def setUp(self):
        # Crear datos de prueba
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            code="TEST_CAMP",
            start_date=date.today(),
            division=self.division
        )
        
        # Crear medium, channel y touchpoint
        self.medium = Medium.objects.create(
            name="Digital",
            code="DIGITAL"
        )
        self.channel = Channel.objects.create(
            name="Website",
            code="WEB"
        )
        self.touchpoint_type = TouchpointType.objects.create(
            name="Landing Page",
            code="LANDING"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Homepage",
            code="HOMEPAGE",
            touchpoint_type=self.touchpoint_type
        )

    def test_campaign_touchpoint_creation(self):
        """Test de creación de relación campaña-touchpoint"""
        ct = CampaignTouchpoint.objects.create(
            campaign=self.campaign,
            touchpoint=self.touchpoint,
            weight=0.5,
            priority=1,
            expected_conversions=100,
            budget_allocated=Decimal('5000.00')
        )
        
        self.assertEqual(ct.campaign, self.campaign)
        self.assertEqual(ct.touchpoint, self.touchpoint)
        self.assertEqual(ct.weight, 0.5)
        self.assertEqual(ct.priority, 1)
        self.assertEqual(str(ct), f"{self.campaign.name} -> {self.touchpoint.name}")

    def test_campaign_touchpoint_unique_constraint(self):
        """Test de la restricción de unicidad campaña-touchpoint"""
        CampaignTouchpoint.objects.create(
            campaign=self.campaign,
            touchpoint=self.touchpoint,
            weight=0.5
        )
        
        with self.assertRaises(Exception):
            CampaignTouchpoint.objects.create(
                campaign=self.campaign,
                touchpoint=self.touchpoint,  # Misma combinación
                weight=0.8
            )

    def test_campaign_touchpoint_properties(self):
        """Test de las propiedades calculadas"""
        ct = CampaignTouchpoint.objects.create(
            campaign=self.campaign,
            touchpoint=self.touchpoint
        )
        
        # Test is_product_targeted (requiere producto en touchpoint y campaign)
        self.assertFalse(ct.is_product_targeted)
        
        # Test is_cross_product (requiere productos diferentes)
        self.assertFalse(ct.is_cross_product)


class CampaignAPITests(APITestCase):
    """Tests para la API de campañas"""

    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.team = Team.objects.create(
            name="Test Team",
            code="TEST_TEAM",
            division=self.division
        )
        
        # Crear industry y segment para relaciones semánticas
        self.industry = Industry.objects.create(
            name="Technology",
            code="TECH"
        )
        self.function = FunctionOrResponsibility.objects.create(
            name="Sales",
            code="SALES"
        )
        self.segment = MarketSegment.objects.create(
            name="Enterprise",
            code="ENT"
        )
        
        # Autenticar usuario
        self.client.force_authenticate(user=self.user)

    def test_create_campaign_api(self):
        """Test de creación de campaña via API"""
        url = reverse('campaigns:campaign-list')
        data = {
            'name': 'API Test Campaign',
            'code': 'API_TEST_001',
            'description': 'Campaign created via API',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30)),
            'budget': '15000.00',
            'division': str(self.division.id),
            'team': str(self.team.id),
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 1)
        
        campaign = Campaign.objects.first()
        self.assertEqual(campaign.name, 'API Test Campaign')
        self.assertEqual(campaign.code, 'API_TEST_001')

    def test_list_campaigns_api(self):
        """Test de listado de campañas via API"""
        # Crear campañas de prueba
        Campaign.objects.create(
            name="Campaign 1",
            code="CAMP_001",
            start_date=date.today(),
            division=self.division
        )
        Campaign.objects.create(
            name="Campaign 2",
            code="CAMP_002",
            start_date=date.today(),
            division=self.division
        )
        
        url = reverse('campaigns:campaign-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_campaign_filtering(self):
        """Test de filtros en la API de campañas"""
        # Crear campañas con diferentes estados
        active_campaign = Campaign.objects.create(
            name="Active Campaign",
            code="ACTIVE_001",
            start_date=date.today(),
            division=self.division,
            is_active=True
        )
        inactive_campaign = Campaign.objects.create(
            name="Inactive Campaign", 
            code="INACTIVE_001",
            start_date=date.today(),
            division=self.division,
            is_active=False
        )
        
        url = reverse('campaigns:campaign-list')
        
        # Test filtro por is_active
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'ACTIVE_001')

    def test_campaign_content_type_filtering(self):
        """Test de filtros por content_type en la API"""
        # Crear campañas con diferentes content_type
        Campaign.objects.create(
            name="Product Campaign",
            code="PRODUCT_001",
            start_date=date.today(),
            content_type="product",
            division=self.division
        )
        Campaign.objects.create(
            name="Brand Campaign",
            code="BRAND_001",
            start_date=date.today(),
            content_type="brand",
            division=self.division
        )
        Campaign.objects.create(
            name="Generic Campaign",
            code="GENERIC_001",
            start_date=date.today(),
            # content_type=None (sin tipo)
            division=self.division
        )
        
        url = reverse('campaigns:campaign-list')
        
        # Test filtro por content_type=product
        response = self.client.get(url, {'content_type': 'product'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'PRODUCT_001')
        
        # Test filtro por content_type=brand
        response = self.client.get(url, {'content_type': 'brand'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'BRAND_001')

    def test_campaign_search(self):
        """Test de búsqueda en campañas"""
        Campaign.objects.create(
            name="Digital Marketing Campaign",
            code="DIGITAL_001",
            start_date=date.today(),
            division=self.division
        )
        Campaign.objects.create(
            name="Email Campaign",
            code="EMAIL_001",
            start_date=date.today(), 
            division=self.division
        )
        
        url = reverse('campaigns:campaign-list')
        response = self.client.get(url, {'search': 'Digital'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Digital Marketing Campaign')

    def test_campaign_analytics_endpoint(self):
        """Test del endpoint de analytics"""
        # Crear campañas de prueba
        Campaign.objects.create(
            name="Campaign 1",
            code="CAMP_001",
            start_date=date.today(),
            division=self.division,
            budget=Decimal('10000')
        )
        Campaign.objects.create(
            name="Campaign 2", 
            code="CAMP_002",
            start_date=date.today(),
            division=self.division,
            budget=Decimal('20000')
        )
        
        url = reverse('campaigns:campaign-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_campaigns', response.data)
        self.assertIn('active_campaigns', response.data)
        self.assertIn('budget_statistics', response.data)
        self.assertEqual(response.data['total_campaigns'], 2)

    def test_duplicate_campaign_endpoint(self):
        """Test del endpoint de duplicación de campañas"""
        original_campaign = Campaign.objects.create(
            name="Original Campaign",
            code="ORIGINAL_001",
            description="Original description",
            start_date=date.today(),
            division=self.division,
            budget=Decimal('15000')
        )
        
        url = reverse('campaigns:campaign-duplicate', kwargs={'pk': original_campaign.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 2)
        
        duplicated = Campaign.objects.exclude(pk=original_campaign.pk).first()
        self.assertTrue(duplicated.name.startswith("Original Campaign (Copia)"))
        self.assertNotEqual(duplicated.code, original_campaign.code)


class CampaignTouchpointAPITests(APITestCase):
    """Tests para la API de relaciones campaña-touchpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            code="TEST_CAMP",
            start_date=date.today(),
            division=self.division
        )
        
        self.medium = Medium.objects.create(
            name="Digital",
            code="DIGITAL"
        )
        self.channel = Channel.objects.create(
            name="Website",
            code="WEB"
        )
        self.touchpoint_type = TouchpointType.objects.create(
            name="Landing Page",
            code="LANDING"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Homepage",
            code="HOMEPAGE",
            touchpoint_type=self.touchpoint_type
        )
        
        self.client.force_authenticate(user=self.user)

    def test_create_campaign_touchpoint_api(self):
        """Test de creación de relación campaña-touchpoint via API"""
        url = reverse('campaigns:campaigntouchpoint-list')
        data = {
            'campaign': str(self.campaign.id),
            'touchpoint': str(self.touchpoint.id),
            'weight': 0.7,
            'priority': 1,
            'expected_conversions': 150,
            'budget_allocated': '8000.00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CampaignTouchpoint.objects.count(), 1)

    def test_list_campaign_touchpoints_api(self):
        """Test de listado de relaciones campaña-touchpoint"""
        CampaignTouchpoint.objects.create(
            campaign=self.campaign,
            touchpoint=self.touchpoint,
            weight=0.5
        )
        
        url = reverse('campaigns:campaigntouchpoint-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CampaignSerializerTests(TestCase):
    """Tests para los serializers de campañas"""

    def setUp(self):
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )

    def test_campaign_list_serializer(self):
        """Test del serializer de listado de campañas"""
        from .serializers import CampaignListSerializer
        
        campaign = Campaign.objects.create(
            name="Test Campaign",
            code="TEST_001",
            start_date=date.today(),
            division=self.division,
            budget=Decimal('10000')
        )
        
        serializer = CampaignListSerializer(campaign)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Campaign')
        self.assertEqual(data['code'], 'TEST_001')
        self.assertIn('budget_display', data)
        self.assertEqual(data['budget_display'], '$10,000.00')

    def test_campaign_choice_serializer(self):
        """Test del serializer de choices"""
        from .serializers import CampaignChoiceSerializer
        
        campaign = Campaign.objects.create(
            name="Test Campaign",
            code="TEST_001",
            start_date=date.today(),
            division=self.division
        )
        
        serializer = CampaignChoiceSerializer(campaign)
        data = serializer.data
        
        self.assertIn('display_name', data)
        self.assertIn(campaign.name, data['display_name'])
        self.assertIn(campaign.code, data['display_name'])


class CampaignProductIntegrationTests(TestCase):
    """Tests para Product Integration Enhancements en Campaigns"""

    def setUp(self):
        # Crear organización y división
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        
        # Crear categoría de producto
        self.product_category = ProductCategory.objects.create(
            name="Software",
            code="SW",
            division=self.division
        )
        
        # Crear productos
        self.product1 = Product.objects.create(
            name="CRM System",
            code="CRM001",
            description="Customer Relationship Management",
            category=self.product_category,
            base_price=Decimal('1000.00'),
            currency_code="USD"
        )
        
        self.product2 = Product.objects.create(
            name="ERP System", 
            code="ERP001",
            description="Enterprise Resource Planning",
            category=self.product_category,
            base_price=Decimal('2000.00'),
            currency_code="USD"
        )
        
        # Crear ofertas
        self.offering1 = ProductOffering.objects.create(
            name="CRM Premium",
            code="CRM_PREM",
            description="Premium CRM offering",
            product=self.product1,
            price=Decimal('850.00'),
            currency_code="USD"
        )
        
        self.offering2 = ProductOffering.objects.create(
            name="ERP Standard",
            code="ERP_STD",
            description="Standard ERP offering", 
            product=self.product2,
            price=Decimal('1800.00'),
            currency_code="USD"
        )
        
        # Crear campaña
        self.campaign = Campaign.objects.create(
            name="Product Integration Test Campaign",
            code="PROD_INT_TEST",
            description="Test campaign for product integration",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('50000.00'),
            content_type="product",
            funnel_stage="think",
            division=self.division
        )

    def test_campaign_target_products_relationship(self):
        """Test relación ManyToMany con productos"""
        # Agregar productos a la campaña
        self.campaign.target_products.add(self.product1, self.product2)
        
        # Verificar que los productos están asociados
        self.assertEqual(self.campaign.target_products.count(), 2)
        self.assertIn(self.product1, self.campaign.target_products.all())
        self.assertIn(self.product2, self.campaign.target_products.all())
        
        # Verificar relación inversa
        campaigns_with_product1 = Campaign.objects.filter(target_products=self.product1)
        self.assertIn(self.campaign, campaigns_with_product1)

    def test_campaign_target_offers_relationship(self):
        """Test relación ManyToMany con ofertas"""
        # Agregar ofertas a la campaña
        self.campaign.target_offers.add(self.offering1, self.offering2)
        
        # Verificar que las ofertas están asociadas
        self.assertEqual(self.campaign.target_offers.count(), 2)
        self.assertIn(self.offering1, self.campaign.target_offers.all())
        self.assertIn(self.offering2, self.campaign.target_offers.all())
        
        # Verificar relación inversa
        campaigns_with_offering1 = Campaign.objects.filter(target_offers=self.offering1)
        self.assertIn(self.campaign, campaigns_with_offering1)

    def test_campaign_target_categories_relationship(self):
        """Test relación ManyToMany con categorías"""
        # Agregar categoría a la campaña
        self.campaign.target_categories.add(self.product_category)
        
        # Verificar que la categoría está asociada
        self.assertEqual(self.campaign.target_categories.count(), 1)
        self.assertIn(self.product_category, self.campaign.target_categories.all())
        
        # Verificar relación inversa
        campaigns_with_category = Campaign.objects.filter(target_categories=self.product_category)
        self.assertIn(self.campaign, campaigns_with_category)

    def test_get_product_performance_analytics(self):
        """Test método get_product_performance_analytics"""
        # Configurar datos de prueba
        self.campaign.target_products.add(self.product1, self.product2)
        self.campaign.target_categories.add(self.product_category)
        self.campaign.target_offers.add(self.offering1, self.offering2)
        
        # Ejecutar analytics
        analytics = self.campaign.get_product_performance_analytics()
        
        # Verificar estructura de respuesta
        self.assertIn('by_product', analytics)
        self.assertIn('by_category', analytics)
        self.assertIn('by_offer', analytics)
        self.assertIn('summary', analytics)
        
        # Verificar summary
        summary = analytics['summary']
        self.assertEqual(summary['total_products'], 2)
        self.assertEqual(summary['total_categories'], 1)
        self.assertEqual(summary['total_offerings'], 2)
        self.assertEqual(summary['total_potential_revenue'], 2650.00)  # 850 + 1800

    def test_get_bundle_analytics(self):
        """Test método get_bundle_analytics"""
        # Crear producto bundle
        bundle_product = Product.objects.create(
            name="Software Bundle",
            code="BUNDLE001",
            description="Bundle of software products",
            category=self.product_category,
            base_price=Decimal('3000.00'),
            currency_code="USD"
        )
        
        # Agregar productos incluidos al bundle
        bundle_product.included_products.add(self.product1, self.product2)
        
        # Agregar bundle a la campaña
        self.campaign.target_products.add(bundle_product)
        
        # Ejecutar analytics de bundle
        bundle_analytics = self.campaign.get_bundle_analytics()
        
        # Verificar estructura
        self.assertIn('bundle_products', bundle_analytics)
        self.assertIn('total_bundles', bundle_analytics)
        self.assertIn('avg_bundle_size', bundle_analytics)
        
        # Verificar datos
        self.assertEqual(bundle_analytics['total_bundles'], 1)
        self.assertEqual(bundle_analytics['avg_bundle_size'], 2.0)  # 2 productos incluidos

    def test_get_target_summary(self):
        """Test método get_target_summary"""
        # Configurar datos
        self.campaign.target_products.add(self.product1, self.product2)
        self.campaign.target_categories.add(self.product_category)
        self.campaign.target_offers.add(self.offering1, self.offering2)
        
        # Ejecutar summary
        summary = self.campaign.get_target_summary()
        
        # Verificar estructura
        self.assertIn('products', summary)
        self.assertIn('categories', summary)
        self.assertIn('offers', summary)
        
        # Verificar datos de productos
        products_data = summary['products']
        self.assertEqual(products_data['total'], 2)
        self.assertEqual(products_data['bundles'], 0)  # No bundles en este test
        self.assertEqual(products_data['individual'], 2)
        
        # Verificar datos de categorías
        categories_data = summary['categories']
        self.assertEqual(categories_data['total'], 1)
        self.assertEqual(categories_data['with_products'], 1)
        
        # Verificar datos de ofertas
        offers_data = summary['offers']
        self.assertEqual(offers_data['total'], 2)
        self.assertEqual(offers_data['active'], 2)  # Ambas ofertas están activas por defecto
        self.assertEqual(offers_data['total_revenue'], 2650.00)

    def test_campaign_with_mixed_targeting(self):
        """Test campaña con targeting mixto (productos, categorías y ofertas)"""
        # Configurar targeting mixto
        self.campaign.target_products.add(self.product1)  # Solo producto 1
        self.campaign.target_categories.add(self.product_category)  # Toda la categoría
        self.campaign.target_offers.add(self.offering2)  # Solo oferta 2
        
        # Verificar que todos los tipos de targeting funcionan
        self.assertEqual(self.campaign.target_products.count(), 1)
        self.assertEqual(self.campaign.target_categories.count(), 1)
        self.assertEqual(self.campaign.target_offers.count(), 1)
        
        # Verificar que se pueden combinar
        all_targeted_products = set()
        all_targeted_products.update(self.campaign.target_products.all())
        
        # Productos de la categoría objetivo
        category_products = Product.objects.filter(category__in=self.campaign.target_categories.all())
        all_targeted_products.update(category_products)
        
        # Productos de las ofertas objetivo
        offer_products = Product.objects.filter(offerings__in=self.campaign.target_offers.all())
        all_targeted_products.update(offer_products)
        
        # Debería incluir producto1 (directo), producto2 (categoría), y producto2 (oferta)
        self.assertIn(self.product1, all_targeted_products)
        self.assertIn(self.product2, all_targeted_products)

    def test_campaign_content_type_offer(self):
        """Test content_type 'offer' para campañas de ofertas"""
        offer_campaign = Campaign.objects.create(
            name="Offer Campaign",
            code="OFFER_CAMP",
            start_date=date.today(),
            content_type="offer",
            division=self.division
        )
        
        # Agregar ofertas
        offer_campaign.target_offers.add(self.offering1, self.offering2)
        
        # Verificar que funciona correctamente
        self.assertEqual(offer_campaign.content_type, "offer")
        self.assertEqual(offer_campaign.target_offers.count(), 2)
        
        # Verificar que se puede filtrar por content_type
        offer_campaigns = Campaign.objects.filter(content_type="offer")
        self.assertIn(offer_campaign, offer_campaigns)

    def test_campaign_analytics_with_empty_targeting(self):
        """Test analytics con campaña sin targeting"""
        empty_campaign = Campaign.objects.create(
            name="Empty Campaign",
            code="EMPTY_CAMP",
            start_date=date.today(),
            division=self.division
        )
        
        # Analytics deberían funcionar sin errores
        analytics = empty_campaign.get_product_performance_analytics()
        self.assertEqual(analytics['summary']['total_products'], 0)
        self.assertEqual(analytics['summary']['total_categories'], 0)
        self.assertEqual(analytics['summary']['total_offerings'], 0)
        
        bundle_analytics = empty_campaign.get_bundle_analytics()
        self.assertEqual(bundle_analytics['total_bundles'], 0)
        
        summary = empty_campaign.get_target_summary()
        self.assertEqual(summary['products']['total'], 0)
        self.assertEqual(summary['categories']['total'], 0)
        self.assertEqual(summary['offers']['total'], 0)


class CampaignProductIntegrationAPITests(APITestCase):
    """Tests de API para Product Integration Enhancements"""

    def setUp(self):
        # Crear usuario
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.organization = OurOrganization.objects.create(name="Test Org")
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        
        self.product_category = ProductCategory.objects.create(
            name="Software",
            code="SW",
            division=self.division
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            code="TEST_PROD",
            category=self.product_category,
            base_price=Decimal('1000.00'),
            currency_code="USD"
        )
        
        self.offering = ProductOffering.objects.create(
            name="Test Offering",
            code="TEST_OFFER",
            product=self.product,
            price=Decimal('850.00'),
            currency_code="USD"
        )
        
        self.campaign = Campaign.objects.create(
            name="API Test Campaign",
            code="API_TEST",
            start_date=date.today(),
            division=self.division
        )
        
        self.client.force_authenticate(user=self.user)

    def test_campaign_product_analytics_endpoint(self):
        """Test endpoint de analytics de productos"""
        # Configurar datos
        self.campaign.target_products.add(self.product)
        self.campaign.target_offers.add(self.offering)
        
        url = reverse('campaigns:campaign-product-analytics', kwargs={'pk': self.campaign.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('by_product', response.data)
        self.assertIn('by_category', response.data)
        self.assertIn('by_offer', response.data)
        self.assertIn('summary', response.data)

    def test_campaign_bundle_analytics_endpoint(self):
        """Test endpoint de analytics de bundles"""
        url = reverse('campaigns:campaign-bundle-analytics', kwargs={'pk': self.campaign.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('bundle_products', response.data)
        self.assertIn('total_bundles', response.data)
        self.assertIn('avg_bundle_size', response.data)

    def test_campaign_target_summary_endpoint(self):
        """Test endpoint de resumen de targeting"""
        url = reverse('campaigns:campaign-target-summary', kwargs={'pk': self.campaign.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('offers', response.data)

    def test_campaign_compatible_offerings_endpoint(self):
        """Test endpoint de ofertas compatibles"""
        # Configurar datos
        self.campaign.target_products.add(self.product)
        
        url = reverse('campaigns:campaign-compatible-offerings', kwargs={'pk': self.campaign.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería incluir la oferta compatible
        self.assertGreater(len(response.data), 0)

    def test_campaign_creation_with_product_integration(self):
        """Test creación de campaña con Product Integration"""
        url = reverse('campaigns:campaign-list')
        data = {
            'name': 'Product Integration Campaign',
            'code': 'PROD_INT_API',
            'start_date': str(date.today()),
            'content_type': 'product',
            'target_products': [str(self.product.pk)],
            'target_offers': [str(self.offering.pk)],
            'target_categories': [str(self.product_category.pk)],
            'division': str(self.division.pk)
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó la campaña
        campaign = Campaign.objects.get(code='PROD_INT_API')
        self.assertEqual(campaign.target_products.count(), 1)
        self.assertEqual(campaign.target_offers.count(), 1)
        self.assertEqual(campaign.target_categories.count(), 1)

    def test_campaign_filtering_by_product_integration(self):
        """Test filtrado por campos de Product Integration"""
        # Crear campaña con targeting específico
        self.campaign.target_products.add(self.product)
        self.campaign.target_offers.add(self.offering)
        self.campaign.target_categories.add(self.product_category)
        
        url = reverse('campaigns:campaign-list')
        
        # Filtrar por producto
        response = self.client.get(url, {'target_products': self.product.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por oferta
        response = self.client.get(url, {'target_offers': self.offering.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por categoría
        response = self.client.get(url, {'target_categories': self.product_category.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
