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
from interactions.models import Medium, Channel, TouchpointClass, Touchpoint
from world.models import Industry, FunctionOrResponsibility, MarketSegment, Tag


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
            code="WEB",
            medium=self.medium
        )
        self.touchpoint_class = TouchpointClass.objects.create(
            name="Landing Page",
            code="LANDING"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Homepage",
            code="HOMEPAGE",
            touchpoint_class=self.touchpoint_class
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
            code="WEB",
            medium=self.medium
        )
        self.touchpoint_class = TouchpointClass.objects.create(
            name="Landing Page",
            code="LANDING"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Homepage",
            code="HOMEPAGE",
            touchpoint_class=self.touchpoint_class
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
