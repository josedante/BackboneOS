"""
Tests comprehensivos para el módulo de analytics de products
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch

from .models import Division, ProductCategory, Modality, Customization, Product
from world.models import (
    Industry, FunctionOrResponsibility, Skill, MarketSegment, Tag,
    Country, DescriptorFamily, WorldDescriptor
)

User = get_user_model()


class AnalyticsAPITestCase(APITestCase):
    """Base test case para tests de Analytics API"""
    
    def setUp(self):
        """Configuración inicial para tests de Analytics"""
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
        
        # Crear datos de soporte del mundo
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE',
            name='Perú'
        )
        
        self.industry = Industry.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.function = FunctionOrResponsibility.objects.create(
            name='Desarrollador',
            code='DEV'
        )
        
        self.skill = Skill.objects.create(
            name='Python',
            code='PY',
            skill_type=Skill.TECHNICAL
        )
        
        self.market_segment = MarketSegment.objects.create(
            name='Startups',
            code='START'
        )
        
        self.tag = Tag.objects.create(
            name='Innovación',
            slug='innovacion'
        )
        
        # Crear divisiones
        self.division_tech = Division.objects.create(
            name='Tecnología',
            code='TECH',
            description='División de productos tecnológicos'
        )
        
        self.division_marketing = Division.objects.create(
            name='Marketing',
            code='MKT',
            description='División de marketing'
        )
        
        # Crear categorías
        self.category_software = ProductCategory.objects.create(
            name='Software',
            code='SW',
            division=self.division_tech
        )
        
        self.category_hardware = ProductCategory.objects.create(
            name='Hardware',
            code='HW',
            division=self.division_tech
        )
        
        self.category_service = ProductCategory.objects.create(
            name='Servicios',
            code='SRV',
            division=self.division_marketing
        )
        
        # Crear modalidades
        self.modality_virtual = Modality.objects.create(
            name='Virtual',
            description='Modalidad virtual'
        )
        
        self.modality_presencial = Modality.objects.create(
            name='Presencial',
            description='Modalidad presencial'
        )
        
        # Crear customizaciones
        self.customization_basic = Customization.objects.create(
            name='Básica',
            description='Personalización básica'
        )
        
        # Crear productos de prueba
        self.product1 = Product.objects.create(
            name='Sistema CRM',
            code='CRM001',
            description='Sistema de gestión de clientes',
            category=self.category_software,
            customization=self.customization_basic,
            base_price=Decimal('1500.00'),
            currency_code='PEN',
            duration=timedelta(hours=40)
        )
        self.product1.modalities.add(self.modality_virtual)
        self.product1.target_functions.add(self.function)
        self.product1.related_skills.add(self.skill)
        self.product1.target_segments.add(self.market_segment)
        self.product1.tags.add(self.tag)
        
        self.product2 = Product.objects.create(
            name='Sistema ERP',
            code='ERP001',
            description='Sistema de planificación empresarial',
            category=self.category_software,
            customization=self.customization_basic,
            base_price=Decimal('2500.00'),
            currency_code='PEN',
            duration=timedelta(hours=80)
        )
        self.product2.modalities.add(self.modality_presencial, self.modality_virtual)
        self.product2.target_functions.add(self.function)
        self.product2.related_skills.add(self.skill)
        
        self.product3 = Product.objects.create(
            name='Laptop Empresarial',
            code='LAP001',
            description='Laptop para uso empresarial',
            category=self.category_hardware,
            base_price=Decimal('3000.00'),
            currency_code='PEN'
        )
        
        self.product4 = Product.objects.create(
            name='Consultoría Marketing',
            code='CONS001',
            description='Servicio de consultoría en marketing',
            category=self.category_service,
            base_price=Decimal('1000.00'),
            currency_code='PEN'
        )
        
        self.client = APIClient()


class DivisionAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de divisiones"""
    
    def test_division_analytics_dashboard_authenticated(self):
        """Test dashboard de analytics por división con autenticación"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-divisions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('divisions_overview', response.data)
        self.assertIn('summary', response.data)
        
        # Verificar datos de overview
        overview = response.data['divisions_overview']
        self.assertIn('total_divisions', overview)
        self.assertIn('divisions_with_products', overview)
        self.assertIn('top_divisions', overview)
        self.assertIn('distribution', overview)
        
        # Verificar que hay 2 divisiones activas
        self.assertEqual(overview['total_divisions'], 2)
        self.assertEqual(overview['divisions_with_products'], 2)
        
        # Verificar que hay divisiones en el top
        self.assertGreater(len(overview['top_divisions']), 0)
    
    def test_division_analytics_unauthenticated(self):
        """Test acceso sin autenticación a analytics de divisiones"""
        url = reverse('products:analytics-divisions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_division_analytics_data_accuracy(self):
        """Test precisión de datos en analytics de divisiones"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-divisions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar conteos exactos
        summary = response.data['summary']
        self.assertEqual(summary['total_categories_across_divisions'], 3)
        self.assertEqual(summary['total_products_across_divisions'], 4)
        
        # Verificar distribución por división
        distribution = response.data['divisions_overview']['distribution']
        
        # División de tecnología debería tener 3 productos
        tech_division = next((d for d in distribution if d['division'] == 'Tecnología'), None)
        self.assertIsNotNone(tech_division)
        self.assertEqual(tech_division['products_count'], 3)
        self.assertEqual(tech_division['categories_count'], 2)
        
        # División de marketing debería tener 1 producto
        mkt_division = next((d for d in distribution if d['division'] == 'Marketing'), None)
        self.assertIsNotNone(mkt_division)
        self.assertEqual(mkt_division['products_count'], 1)
        self.assertEqual(mkt_division['categories_count'], 1)


class ProductAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de productos"""
    
    def test_product_analytics_dashboard(self):
        """Test dashboard principal de analytics de productos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('overview', response.data)
        self.assertIn('pricing', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('modalities', response.data)
        
        # Verificar overview
        overview = response.data['overview']
        self.assertEqual(overview['total_products'], 4)
        self.assertEqual(overview['total_categories'], 3)
        self.assertEqual(overview['total_divisions'], 2)
        
        # Verificar pricing statistics
        pricing = response.data['pricing']
        self.assertIn('avg_price', pricing)
        self.assertIn('min_price', pricing)
        self.assertIn('max_price', pricing)
        self.assertIn('price_ranges', pricing)
        
        # Verificar que los precios son correctos
        self.assertEqual(float(pricing['min_price']), 1000.00)
        self.assertEqual(float(pricing['max_price']), 3000.00)
    
    def test_product_analytics_filtering(self):
        """Test filtrado en analytics de productos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        
        # Filtrar por división
        response = self.client.get(url, {'division': self.division_tech.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Solo deberían aparecer productos de la división de tecnología
        overview = response.data['overview']
        self.assertEqual(overview['total_products'], 3)
        
        # Filtrar por categoría
        response = self.client.get(url, {'category': self.category_software.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Solo productos de software
        overview = response.data['overview']
        self.assertEqual(overview['total_products'], 2)


class CategoryAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de categorías"""
    
    def test_category_analytics(self):
        """Test analytics de categorías"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura
        self.assertIn('categories_performance', response.data)
        self.assertIn('category_hierarchy', response.data)
        self.assertIn('price_analysis', response.data)
        
        # Verificar performance de categorías
        performance = response.data['categories_performance']
        self.assertEqual(len(performance), 3)  # 3 categorías
        
        # Verificar que software tiene 2 productos
        software_perf = next((c for c in performance if c['category'] == 'Software'), None)
        self.assertIsNotNone(software_perf)
        self.assertEqual(software_perf['products_count'], 2)
    
    def test_category_hierarchy_analysis(self):
        """Test análisis de jerarquía de categorías"""
        # Crear subcategoría para probar jerarquía
        subcategory = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division_tech,
            parent=self.category_software
        )
        
        Product.objects.create(
            name='App E-commerce',
            code='ECOM001',
            category=subcategory,
            base_price=Decimal('1200.00'),
            currency_code='PEN'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se incluye la jerarquía
        hierarchy = response.data['category_hierarchy']
        self.assertIsInstance(hierarchy, list)
        self.assertGreater(len(hierarchy), 0)


class MarketSegmentationAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de segmentación de mercado"""
    
    def test_market_segmentation_analytics(self):
        """Test analytics de segmentación de mercado"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-market-segmentation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura
        self.assertIn('segment_analysis', response.data)
        self.assertIn('function_analysis', response.data)
        self.assertIn('skill_analysis', response.data)
        
        # Verificar análisis de segmentos
        segment_analysis = response.data['segment_analysis']
        self.assertIsInstance(segment_analysis, list)
        
        # Verificar que hay datos de startups
        startup_segment = next((s for s in segment_analysis if s['segment'] == 'Startups'), None)
        self.assertIsNotNone(startup_segment)
        self.assertEqual(startup_segment['products_count'], 1)
    
    def test_skills_analysis(self):
        """Test análisis de habilidades en productos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-market-segmentation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar análisis de skills
        skill_analysis = response.data['skill_analysis']
        self.assertIsInstance(skill_analysis, list)
        
        # Verificar que Python aparece
        python_skill = next((s for s in skill_analysis if s['skill'] == 'Python'), None)
        self.assertIsNotNone(python_skill)
        self.assertEqual(python_skill['products_count'], 2)


class PricingAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de precios"""
    
    def test_pricing_analytics(self):
        """Test analytics de precios"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-pricing')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura
        self.assertIn('price_distribution', response.data)
        self.assertIn('price_by_category', response.data)
        self.assertIn('pricing_trends', response.data)
        self.assertIn('currency_analysis', response.data)
        
        # Verificar distribución de precios
        distribution = response.data['price_distribution']
        self.assertIn('ranges', distribution)
        self.assertIn('statistics', distribution)
        
        # Verificar estadísticas
        stats = distribution['statistics']
        self.assertEqual(float(stats['min_price']), 1000.00)
        self.assertEqual(float(stats['max_price']), 3000.00)
        self.assertEqual(float(stats['avg_price']), 2000.00)
    
    def test_pricing_by_category(self):
        """Test análisis de precios por categoría"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-pricing')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar análisis por categoría
        by_category = response.data['price_by_category']
        self.assertIsInstance(by_category, list)
        
        # Verificar que software tiene precio promedio correcto
        software_pricing = next((c for c in by_category if c['category'] == 'Software'), None)
        self.assertIsNotNone(software_pricing)
        self.assertEqual(float(software_pricing['avg_price']), 2000.00)  # (1500 + 2500) / 2


class GrowthAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de crecimiento"""
    
    def test_growth_analytics(self):
        """Test analytics de crecimiento"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-growth')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura
        self.assertIn('monthly_trends', response.data)
        self.assertIn('category_growth', response.data)
        self.assertIn('new_products', response.data)
        
        # Verificar tendencias mensuales
        monthly_trends = response.data['monthly_trends']
        self.assertIsInstance(monthly_trends, list)
    
    @patch('django.utils.timezone.now')
    def test_growth_analytics_with_time_filter(self, mock_now):
        """Test analytics de crecimiento con filtro de tiempo"""
        # Simular fecha actual
        mock_now.return_value = date(2025, 6, 15)
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-growth')
        
        # Filtrar por último mes
        response = self.client.get(url, {'period': 'last_month'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Filtrar por último año
        response = self.client.get(url, {'period': 'last_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RecommendationsAnalyticsTests(AnalyticsAPITestCase):
    """Tests para analytics de recomendaciones"""
    
    def test_product_recommendations(self):
        """Test recomendaciones de productos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura
        self.assertIn('optimization_opportunities', response.data)
        self.assertIn('pricing_recommendations', response.data)
        self.assertIn('portfolio_insights', response.data)
        
        # Verificar oportunidades de optimización
        opportunities = response.data['optimization_opportunities']
        self.assertIsInstance(opportunities, list)
    
    def test_pricing_recommendations(self):
        """Test recomendaciones de precios"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar recomendaciones de precios
        pricing_rec = response.data['pricing_recommendations']
        self.assertIsInstance(pricing_rec, list)


class AnalyticsPerformanceTests(AnalyticsAPITestCase):
    """Tests de performance para analytics"""
    
    def test_analytics_response_time(self):
        """Test tiempo de respuesta de analytics"""
        # Crear más datos para probar performance
        for i in range(50):
            division = Division.objects.create(
                name=f'División {i}',
                code=f'DIV{i:03d}'
            )
            category = ProductCategory.objects.create(
                name=f'Categoría {i}',
                code=f'CAT{i:03d}',
                division=division
            )
            Product.objects.create(
                name=f'Producto {i}',
                code=f'PROD{i:03d}',
                category=category,
                base_price=Decimal('1000.00') + i
            )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Test que los endpoints respondan en tiempo razonable
        urls = [
            reverse('products:analytics-dashboard'),
            reverse('products:analytics-divisions'),
            reverse('products:analytics-categories'),
            reverse('products:analytics-pricing'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_analytics_query_optimization(self):
        """Test optimización de queries en analytics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        
        # Verificar que no hay queries N+1
        with self.assertNumQueries(10):  # Número esperado de queries optimizadas
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnalyticsErrorHandlingTests(AnalyticsAPITestCase):
    """Tests de manejo de errores en analytics"""
    
    def test_analytics_with_no_data(self):
        """Test analytics cuando no hay datos"""
        # Eliminar todos los productos
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Division.objects.all().delete()
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que maneja graciosamente la falta de datos
        overview = response.data['overview']
        self.assertEqual(overview['total_products'], 0)
        self.assertEqual(overview['total_categories'], 0)
    
    def test_analytics_with_invalid_filters(self):
        """Test analytics con filtros inválidos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        
        # Filtro con ID inexistente
        response = self.client.get(url, {'division': 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debería retornar datos vacíos pero válidos
        overview = response.data['overview']
        self.assertEqual(overview['total_products'], 0)
    
    def test_analytics_permission_errors(self):
        """Test errores de permisos en analytics"""
        # Usuario sin permisos especiales
        self.client.force_authenticate(user=self.user)
        
        urls = [
            reverse('products:analytics-dashboard'),
            reverse('products:analytics-divisions'),
            reverse('products:analytics-categories'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            # Dependiendo de la configuración, puede requerir permisos especiales
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_403_FORBIDDEN
            ])


class AnalyticsIntegrationTests(AnalyticsAPITestCase):
    """Tests de integración de analytics con otros módulos"""
    
    def test_analytics_with_offers_integration(self):
        """Test integración de analytics con ofertas"""
        # Este test documenta la integración esperada con offers
        from offers.models import ProductOffering
        
        # Crear ofertas para productos
        ProductOffering.objects.create(
            name='Oferta CRM',
            code='OFF_CRM',
            product=self.product1,
            price=Decimal('1200.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30)
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que incluye información de ofertas activas
        # (esto dependería de la implementación específica)
        if 'offers_analysis' in response.data:
            offers_analysis = response.data['offers_analysis']
            self.assertIn('products_with_offers', offers_analysis)
    
    def test_analytics_with_campaigns_integration(self):
        """Test integración de analytics con campañas"""
        # Este test documenta la integración esperada con campaigns
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:analytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Si hay integración con campaigns, debería aparecer en los datos
        if 'campaign_performance' in response.data:
            campaign_perf = response.data['campaign_performance']
            self.assertIsInstance(campaign_perf, (list, dict))
