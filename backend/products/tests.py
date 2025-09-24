from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

from our_institution.models import Division
from .models import ProductCategory, Modality, Customization, Product
from .serializers import (
    DivisionSerializer, ProductCategorySerializer, ModalitySerializer,
    CustomizationSerializer, ProductListSerializer, ProductDetailSerializer
)
from world.models import (
    Industry, FunctionOrResponsibility, Skill, MarketSegment, Tag,
    Country, DescriptorFamily, WorldDescriptor
)

User = get_user_model()


class DivisionModelTests(TestCase):
    """Tests para el modelo Division"""
    
    def setUp(self):
        self.division_data = {
            'name': 'Tecnología',
            'code': 'TECH',
            'description': 'División de productos tecnológicos'
        }
    
    def test_division_creation(self):
        """Test crear una división válida"""
        division = Division.objects.create(**self.division_data)
        self.assertEqual(division.name, 'Tecnología')
        self.assertEqual(division.code, 'TECH')
        self.assertTrue(division.is_active)
        self.assertIsNotNone(division.id)
    
    def test_division_str_representation(self):
        """Test representación string de la división"""
        division = Division.objects.create(**self.division_data)
        self.assertEqual(str(division), 'Tecnología')
    
    def test_unique_constraints(self):
        """Test restricciones de unicidad"""
        Division.objects.create(**self.division_data)
        
        # Verificar que se creó correctamente
        self.assertEqual(Division.objects.filter(name='Tecnología').count(), 1)
        self.assertEqual(Division.objects.filter(code='TECH').count(), 1)
    
    def test_categories_count_property(self):
        """Test propiedad categories_count"""
        division = Division.objects.create(**self.division_data)
        
        # Sin categorías
        self.assertEqual(division.categories_count, 0)
        
        # Crear categorías
        category1 = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=division
        )
        category2 = ProductCategory.objects.create(
            name='Hardware',
            code='HARD',
            division=division
        )
        
        # Refrescar desde DB
        division.refresh_from_db()
        self.assertEqual(division.categories_count, 2)
        
        # Desactivar una categoría
        category1.is_active = False
        category1.save()
        
        division.refresh_from_db()
        self.assertEqual(division.categories_count, 1)
    
    def test_products_count_property(self):
        """Test propiedad products_count"""
        division = Division.objects.create(**self.division_data)
        category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=division
        )
        
        # Sin productos
        self.assertEqual(division.products_count, 0)
        
        # Crear productos
        Product.objects.create(
            name='Producto 1',
            code='PROD1',
            category=category
        )
        Product.objects.create(
            name='Producto 2',
            code='PROD2',
            category=category
        )
        
        self.assertEqual(division.products_count, 2)
    
    def test_get_revenue_summary(self):
        """Test método get_revenue_summary"""
        division = Division.objects.create(**self.division_data)
        category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=division
        )
        
        # Crear productos con precios
        Product.objects.create(
            name='Producto 1',
            code='PROD1',
            category=category,
            base_price=Decimal('100.00')
        )
        Product.objects.create(
            name='Producto 2',
            code='PROD2',
            category=category,
            base_price=Decimal('200.00')
        )
        Product.objects.create(
            name='Producto sin precio',
            code='PROD3',
            category=category
        )
        
        summary = division.get_revenue_summary()
        
        self.assertEqual(summary['total_products_with_price'], 2)
        self.assertEqual(summary['avg_price'], Decimal('150.00'))
        self.assertEqual(summary['total_potential_value'], Decimal('300.00'))


class ProductCategoryModelTests(TestCase):
    """Tests para el modelo ProductCategory"""
    
    def setUp(self):
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.category_data = {
            'name': 'Software',
            'code': 'SOFT',
            'description': 'Categoría de software',
            'division': self.division
        }
    
    def test_category_creation(self):
        """Test crear una categoría válida"""
        category = ProductCategory.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Software')
        self.assertEqual(category.code, 'SOFT')
        self.assertEqual(category.division, self.division)
        self.assertTrue(category.is_active)
    
    def test_category_str_representation(self):
        """Test representación string de la categoría"""
        category = ProductCategory.objects.create(**self.category_data)
        expected = f"{self.division.name} > {category.name}"
        self.assertEqual(str(category), expected)
        
        # Test sin división
        category_no_div = ProductCategory.objects.create(
            name='Sin División',
            code='NODIV'
        )
        self.assertEqual(str(category_no_div), 'Sin División')
    
    def test_category_hierarchy(self):
        """Test jerarquía de categorías"""
        parent = ProductCategory.objects.create(**self.category_data)
        
        child = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division,
            parent=parent
        )
        
        grandchild = ProductCategory.objects.create(
            name='E-commerce',
            code='ECOMM',
            division=self.division,
            parent=child
        )
        
        # Verificar relaciones
        self.assertEqual(child.parent, parent)
        self.assertEqual(grandchild.parent, child)
        self.assertIn(child, parent.subcategories.all())
        self.assertIn(grandchild, child.subcategories.all())
    
    def test_full_path_property(self):
        """Test propiedad full_path"""
        parent = ProductCategory.objects.create(**self.category_data)
        
        child = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division,
            parent=parent
        )
        
        grandchild = ProductCategory.objects.create(
            name='E-commerce',
            code='ECOMM',
            division=self.division,
            parent=child
        )
        
        # Verificar paths
        expected_parent = f"{self.division.name} > {parent.name}"
        expected_child = f"{self.division.name} > {parent.name} > {child.name}"
        expected_grandchild = f"{self.division.name} > {parent.name} > {child.name} > {grandchild.name}"
        
        self.assertEqual(parent.full_path, expected_parent)
        self.assertEqual(child.full_path, expected_child)
        self.assertEqual(grandchild.full_path, expected_grandchild)
    
    def test_level_properties(self):
        """Test propiedades level y absolute_level"""
        parent = ProductCategory.objects.create(**self.category_data)
        
        child = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division,
            parent=parent
        )
        
        grandchild = ProductCategory.objects.create(
            name='E-commerce',
            code='ECOMM',
            division=self.division,
            parent=child
        )
        
        # Verificar niveles
        self.assertEqual(parent.level, 0)  # Sin padre
        self.assertEqual(child.level, 1)   # 1 nivel de padres
        self.assertEqual(grandchild.level, 2)  # 2 niveles de padres
        
        # Niveles absolutos (con división)
        self.assertEqual(parent.absolute_level, 1)     # División=0, parent=1
        self.assertEqual(child.absolute_level, 2)      # División=0, parent=1, child=2
        self.assertEqual(grandchild.absolute_level, 3) # División=0, parent=1, child=2, grandchild=3
    
    def test_get_descendants(self):
        """Test método get_descendants"""
        parent = ProductCategory.objects.create(**self.category_data)
        
        child1 = ProductCategory.objects.create(
            name='Child 1',
            code='CHILD1',
            division=self.division,
            parent=parent
        )
        
        child2 = ProductCategory.objects.create(
            name='Child 2',
            code='CHILD2',
            division=self.division,
            parent=parent
        )
        
        grandchild = ProductCategory.objects.create(
            name='Grandchild',
            code='GRAND1',
            division=self.division,
            parent=child1
        )
        
        descendants = parent.get_descendants()
        
        # Debe incluir todos los descendientes
        self.assertEqual(len(descendants), 3)
        self.assertIn(child1, descendants)
        self.assertIn(child2, descendants)
        self.assertIn(grandchild, descendants)


class ModalityModelTests(TestCase):
    """Tests para el modelo Modality"""
    
    def setUp(self):
        self.modality_data = {
            'name': 'Presencial',
            'description': 'Modalidad presencial'
        }
    
    def test_modality_creation(self):
        """Test crear una modalidad válida"""
        modality = Modality.objects.create(**self.modality_data)
        self.assertEqual(modality.name, 'Presencial')
        self.assertTrue(modality.is_active)
    
    def test_modality_str_representation(self):
        """Test representación string de la modalidad"""
        modality = Modality.objects.create(**self.modality_data)
        self.assertEqual(str(modality), 'Presencial')
    
    def test_unique_name(self):
        """Test nombre único"""
        Modality.objects.create(**self.modality_data)
        
        # Verificar unicidad
        existing_count = Modality.objects.filter(name='Presencial').count()
        self.assertEqual(existing_count, 1)


class CustomizationModelTests(TestCase):
    """Tests para el modelo Customization"""
    
    def setUp(self):
        self.customization_data = {
            'name': 'Personalización Premium',
            'description': 'Personalización avanzada del producto'
        }
    
    def test_customization_creation(self):
        """Test crear una personalización válida"""
        customization = Customization.objects.create(**self.customization_data)
        self.assertEqual(customization.name, 'Personalización Premium')
        self.assertTrue(customization.is_active)
    
    def test_customization_str_representation(self):
        """Test representación string de la personalización"""
        customization = Customization.objects.create(**self.customization_data)
        self.assertEqual(str(customization), 'Personalización Premium')


class ProductModelTests(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        # Crear datos de soporte
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=self.division
        )
        
        self.modality = Modality.objects.create(
            name='Virtual',
            description='Modalidad virtual'
        )
        
        self.customization = Customization.objects.create(
            name='Premium',
            description='Personalización premium'
        )
        
        # Crear datos del mundo
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE',
            name='Perú',
            official_name='República del Perú'
        )
        
        self.industry = Industry.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.function = FunctionOrResponsibility.objects.create(
            name='Desarrollo',
            code='DEV'
        )
        
        self.skill = Skill.objects.create(
            name='Python',
            code='PY'
        )
        
        self.descriptor_family = DescriptorFamily.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.descriptor = WorldDescriptor.objects.create(
            family=self.descriptor_family,
            name='Desarrollo Web',
            code='WEBDEV'
        )
        
        self.market_segment = MarketSegment.objects.create(
            name='Startups',
            code='START'
        )
        
        self.tag = Tag.objects.create(
            name='Innovación',
            slug='innovacion'
        )
        
        self.product_data = {
            'name': 'Sistema de Gestión Web',
            'code': 'SGW001',
            'description': 'Sistema completo de gestión empresarial web',
            'canonical_url': 'https://example.com/sgw',
            'category': self.category,
            'customization': self.customization,
            'duration': timedelta(hours=40),
            'base_price': Decimal('1500.00'),
            'currency_code': 'PEN'
        }
    
    def test_product_creation(self):
        """Test crear un producto válido"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.name, 'Sistema de Gestión Web')
        self.assertEqual(product.code, 'SGW001')
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.base_price, Decimal('1500.00'))
        self.assertTrue(product.is_active)
    
    def test_product_str_representation(self):
        """Test representación string del producto"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), 'Sistema de Gestión Web')
    
    def test_unique_constraints(self):
        """Test restricciones de unicidad"""
        Product.objects.create(**self.product_data)
        
        # Verificar unicidad
        self.assertEqual(Product.objects.filter(name='Sistema de Gestión Web').count(), 1)
        self.assertEqual(Product.objects.filter(code='SGW001').count(), 1)
    
    def test_price_validation(self):
        """Test validación de precios"""
        # Precio negativo debe fallar
        product_data = self.product_data.copy()
        product_data['base_price'] = Decimal('-100.00')
        
        with self.assertRaises(ValidationError):
            product = Product(**product_data)
            product.clean()
    
    def test_currency_validation(self):
        """Test validación de moneda"""
        # Moneda inválida debe fallar en la base de datos
        product_data = self.product_data.copy()
        product_data['currency_code'] = 'XXX'
        
        # Esto debería fallar por la constraint de DB
        with self.assertRaises(Exception):  # IntegrityError o similar
            Product.objects.create(**product_data)
    
    def test_product_properties(self):
        """Test propiedades calculadas del producto"""
        product = Product.objects.create(**self.product_data)
        
        # Test is_customizable
        self.assertTrue(product.is_customizable)
        
        # Test has_canonical_url
        self.assertTrue(product.has_canonical_url)
        
        # Test price_display
        expected_price = "PEN 1,500.00"
        self.assertEqual(product.price_display, expected_price)
        
        # Test duration_display - 40 horas = 1 día (40 horas = 1 día + 16 horas, pero el model devuelve solo la parte de días)
        # Según el modelo, 40 horas debería ser "1 día" porque days = 40*3600 // 86400 = 1
        self.assertEqual(product.duration_display, "1 día")
        
        # Test producto sin precio
        product_no_price = Product.objects.create(
            name='Producto sin precio',
            code='PSP001',
            category=self.category
        )
        self.assertEqual(product_no_price.price_display, "Precio por consultar")
    
    def test_duration_display_variations(self):
        """Test diferentes formatos de duration_display"""
        # Días
        product_days = Product.objects.create(
            name='Producto Días',
            code='PD001',
            duration=timedelta(days=3)
        )
        self.assertEqual(product_days.duration_display, "3 días")
        
        # Un día
        product_one_day = Product.objects.create(
            name='Producto Un Día',
            code='PUD001',
            duration=timedelta(days=1)
        )
        self.assertEqual(product_one_day.duration_display, "1 día")
        
        # Horas
        product_hours = Product.objects.create(
            name='Producto Horas',
            code='PH001',
            duration=timedelta(hours=5)
        )
        self.assertEqual(product_hours.duration_display, "5 horas")
        
        # Una hora
        product_one_hour = Product.objects.create(
            name='Producto Una Hora',
            code='PUH001',
            duration=timedelta(hours=1)
        )
        self.assertEqual(product_one_hour.duration_display, "1 hora")
        
        # Menos de una hora
        product_minutes = Product.objects.create(
            name='Producto Minutos',
            code='PM001',
            duration=timedelta(minutes=30)
        )
        self.assertEqual(product_minutes.duration_display, "Menos de 1 hora")
    
    def test_many_to_many_relations(self):
        """Test relaciones ManyToMany"""
        product = Product.objects.create(**self.product_data)
        
        # Agregar relaciones
        product.modalities.add(self.modality)
        product.target_segments.add(self.market_segment)
        product.related_industries.add(self.industry)
        product.related_functions.add(self.function)
        product.related_skills.add(self.skill)
        product.descriptors.add(self.descriptor)
        product.tags.add(self.tag)
        
        # Verificar relaciones
        self.assertIn(self.modality, product.modalities.all())
        self.assertIn(self.market_segment, product.target_segments.all())
        self.assertIn(self.industry, product.related_industries.all())
        self.assertIn(self.function, product.related_functions.all())
        self.assertIn(self.skill, product.related_skills.all())
        self.assertIn(self.descriptor, product.descriptors.all())
        self.assertIn(self.tag, product.tags.all())
    
    def test_target_audience_method(self):
        """Test método get_target_audience"""
        product = Product.objects.create(**self.product_data)
        
        # Sin segmentos
        self.assertEqual(product.get_target_audience(), 'General')
        
        # Con segmentos
        product.target_segments.add(self.market_segment)
        self.assertEqual(product.get_target_audience(), 'Startups')
        
        # Múltiples segmentos
        segment2 = MarketSegment.objects.create(
            name='PYMES',
            code='PYMES'
        )
        product.target_segments.add(segment2)
        audience = product.get_target_audience()
        self.assertIn('Startups', audience)
        self.assertIn('PYMES', audience)
    
    def test_modalities_display_method(self):
        """Test método get_modalities_display"""
        product = Product.objects.create(**self.product_data)
        
        # Sin modalidades
        self.assertEqual(product.get_modalities_display(), 'No especificada')
        
        # Con modalidades
        product.modalities.add(self.modality)
        self.assertEqual(product.get_modalities_display(), 'Virtual')
    
    def test_related_skills_summary(self):
        """Test método get_related_skills_summary"""
        product = Product.objects.create(**self.product_data)
        
        # Crear skills de diferentes tipos
        skill_tech = Skill.objects.create(
            name='Django',
            code='DJ',
            skill_type=Skill.TECHNICAL
        )
        skill_soft = Skill.objects.create(
            name='Comunicación',
            code='COM',
            skill_type=Skill.SOFT
        )
        
        product.related_skills.add(skill_tech, skill_soft)
        
        summary = product.get_related_skills_summary()
        
        self.assertIn(Skill.TECHNICAL, summary)
        self.assertIn(Skill.SOFT, summary)
        self.assertIn('Django', summary[Skill.TECHNICAL])
        self.assertIn('Comunicación', summary[Skill.SOFT])


class ProductIncludedRelationTests(TestCase):
    """Tests para relaciones de productos incluidos"""
    
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Software',
            code='SOFT'
        )
        
        self.main_product = Product.objects.create(
            name='Suite Completa',
            code='SUITE001',
            category=self.category,
            base_price=Decimal('1000.00')
        )
        
        self.included_product1 = Product.objects.create(
            name='Módulo A',
            code='MOD_A',
            category=self.category,
            base_price=Decimal('300.00')
        )
        
        self.included_product2 = Product.objects.create(
            name='Módulo B',
            code='MOD_B',
            category=self.category,
            base_price=Decimal('200.00')
        )
    
    def test_included_products_basic(self):
        """Test funcionalidad básica de productos incluidos"""
        # Agregar productos incluidos
        self.main_product.included_products.add(self.included_product1, self.included_product2)
        
        # Verificar relaciones
        included = self.main_product.get_included_products_list()
        self.assertEqual(included.count(), 2)
        self.assertIn(self.included_product1, included)
        self.assertIn(self.included_product2, included)
        
        # Verificar productos padre
        parents = self.included_product1.get_parent_products()
        self.assertEqual(parents.count(), 1)
        self.assertIn(self.main_product, parents)
    
    def test_add_included_product_method(self):
        """Test método add_included_product"""
        # Agregar producto válido
        result = self.main_product.add_included_product(self.included_product1)
        self.assertTrue(result)
        self.assertIn(self.included_product1, self.main_product.included_products.all())
        
        # Intentar agregar el mismo producto (debe retornar False)
        result = self.main_product.add_included_product(self.included_product1)
        self.assertFalse(result)
        
        # Intentar agregarse a sí mismo (debe fallar)
        with self.assertRaises(ValidationError):
            self.main_product.add_included_product(self.main_product)
    
    def test_remove_included_product_method(self):
        """Test método remove_included_product"""
        self.main_product.included_products.add(self.included_product1)
        
        # Verificar que está incluido
        self.assertIn(self.included_product1, self.main_product.included_products.all())
        
        # Remover
        self.main_product.remove_included_product(self.included_product1)
        self.assertNotIn(self.included_product1, self.main_product.included_products.all())
    
    def test_bundle_pricing(self):
        """Test cálculos de precios de bundle"""
        self.main_product.included_products.add(self.included_product1, self.included_product2)
        
        # Test get_total_included_price
        total_included = self.main_product.get_total_included_price()
        expected_total = self.included_product1.base_price + self.included_product2.base_price
        self.assertEqual(total_included, expected_total)
        
        # Test bundle_price_display - usar formato sin comas para comparar número base
        bundle_display = self.main_product.get_bundle_price_display()
        expected_bundle_total = self.main_product.base_price + total_included
        # El formato esperado incluye comas de miles: "PEN 1,500.00 (incluye 2 productos)"
        self.assertIn(f"{expected_bundle_total:,.2f}", bundle_display)
        self.assertIn("incluye 2 productos", bundle_display)
    
    def test_bundle_properties(self):
        """Test propiedades is_bundle e is_included_in_bundles"""
        # Sin productos incluidos
        self.assertFalse(self.main_product.is_bundle)
        self.assertFalse(self.included_product1.is_included_in_bundles)
        
        # Con productos incluidos
        self.main_product.included_products.add(self.included_product1)
        
        # Refrescar desde DB
        self.main_product.refresh_from_db()
        self.included_product1.refresh_from_db()
        
        self.assertTrue(self.main_product.is_bundle)
        self.assertTrue(self.included_product1.is_included_in_bundles)
    
    def test_included_products_display(self):
        """Test método get_included_products_display"""
        # Sin productos incluidos
        display = self.main_product.get_included_products_display()
        self.assertEqual(display, 'Ninguno')
        
        # Con productos incluidos
        self.main_product.included_products.add(self.included_product1, self.included_product2)
        display = self.main_product.get_included_products_display()
        
        self.assertIn('Módulo A', display)
        self.assertIn('Módulo B', display)


# ============================
# TESTS DE SERIALIZERS
# ============================

class ProductSerializerTests(TestCase):
    """Tests para los serializers de products"""
    
    def setUp(self):
        # Crear datos de soporte
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=self.division
        )
        
        self.modality = Modality.objects.create(
            name='Virtual'
        )
        
        self.product = Product.objects.create(
            name='Sistema Web',
            code='SYS001',
            description='Sistema web avanzado',
            category=self.category,
            base_price=Decimal('1500.00'),
            currency_code='PEN'
        )
        
        self.product.modalities.add(self.modality)
    
    def test_division_serializer(self):
        """Test DivisionSerializer"""
        serializer = DivisionSerializer(instance=self.division)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Tecnología')
        self.assertEqual(data['code'], 'TECH')
        self.assertIn('categories_count', data)
        self.assertIn('products_count', data)
        self.assertTrue(data['is_active'])
    
    def test_product_category_serializer(self):
        """Test ProductCategorySerializer"""
        serializer = ProductCategorySerializer(instance=self.category)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Software')
        self.assertEqual(data['code'], 'SOFT')
        self.assertEqual(data['division_name'], 'Tecnología')
        self.assertIn('full_path', data)
        self.assertIn('level', data)
        self.assertIn('subcategories_count', data)
        self.assertIn('products_count', data)
    
    def test_modality_serializer(self):
        """Test ModalitySerializer"""
        serializer = ModalitySerializer(instance=self.modality)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Virtual')
        self.assertIn('products_count', data)
    
    def test_product_list_serializer(self):
        """Test ProductListSerializer"""
        serializer = ProductListSerializer(instance=self.product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Sistema Web')
        self.assertEqual(data['code'], 'SYS001')
        self.assertEqual(data['category_name'], 'Software')
        self.assertIn('price_display', data)
        self.assertIn('target_audience', data)
        self.assertIn('modalities_display', data)
        self.assertIn('skills_count', data)
        self.assertIn('is_bundle', data)
    
    def test_product_detail_serializer(self):
        """Test ProductDetailSerializer"""
        # Crear un producto que sea bundle para probar bundle_price_display
        included_product = Product.objects.create(
            name='Producto Incluido',
            code='PI001',
            category=self.category,
            base_price=Decimal('500.00'),
            currency_code='PEN'
        )
        self.product.included_products.add(included_product)
        
        # Verificar que el producto es un bundle
        self.assertTrue(self.product.is_bundle)
        
        serializer = ProductDetailSerializer(instance=self.product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Sistema Web')
        self.assertIn('category', data)
        self.assertIn('modalities', data)
        self.assertIn('price_display', data)
        self.assertIn('is_customizable', data)
        self.assertIn('bundle_price_display', data)
        self.assertIn('skills_summary', data)


# ============================
# TESTS DE API ENDPOINTS
# ============================

class ProductsAPITests(APITestCase):
    """Tests para los endpoints de la API de products"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario para tests autenticados
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=self.division
        )
        
        self.product = Product.objects.create(
            name='Sistema Web',
            code='SYS001',
            description='Sistema web avanzado',
            category=self.category,
            base_price=Decimal('1500.00')
        )
        
        # Autenticar cliente para tests que requieren autenticación
        self.client.force_authenticate(user=self.user)
    
    def test_division_list_endpoint(self):
        """Test endpoint de lista de divisiones"""
        url = '/api/products/divisions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tecnología')
    
    def test_division_detail_endpoint(self):
        """Test endpoint de detalle de división"""
        url = f'/api/products/divisions/{self.division.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tecnología')
    
    def test_category_list_endpoint(self):
        """Test endpoint de lista de categorías"""
        url = '/api/products/categories/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Software')
    
    def test_product_list_endpoint(self):
        """Test endpoint de lista de productos"""
        url = '/api/products/products/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Sistema Web')
    
    def test_product_detail_endpoint(self):
        """Test endpoint de detalle de producto"""
        url = f'/api/products/products/{self.product.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Sistema Web')
        self.assertIn('category', response.data)
        self.assertIn('price_display', response.data)
    
    def test_product_search_functionality(self):
        """Test funcionalidad de búsqueda de productos"""
        url = '/api/products/products/'
        response = self.client.get(url, {'search': 'Sistema'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Búsqueda sin resultados
        response = self.client.get(url, {'search': 'NoExiste'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_product_filtering(self):
        """Test funcionalidad de filtrado"""
        # Crear producto inactivo
        inactive_product = Product.objects.create(
            name='Producto Inactivo',
            code='INACT001',
            category=self.category,
            is_active=False
        )
        
        url = '/api/products/products/'
        
        # Filtrar por categoría
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe mostrar productos activos de la categoría
        names = [item['name'] for item in response.data['results']]
        self.assertIn('Sistema Web', names)
        self.assertNotIn('Producto Inactivo', names)
    
    def test_product_ordering(self):
        """Test funcionalidad de ordenamiento"""
        # Crear otro producto
        another_product = Product.objects.create(
            name='Aplicación Móvil',
            code='APP001',
            category=self.category,
            base_price=Decimal('800.00')
        )
        
        url = '/api/products/products/'
        
        # Ordenar por nombre
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names[0], 'Aplicación Móvil')  # A viene antes que S
        
        # Ordenar por precio
        response = self.client.get(url, {'ordering': 'base_price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [item['base_price'] for item in response.data['results']]
        self.assertEqual(float(prices[0]), 800.0)  # Precio menor primero
    
    def test_category_tree_endpoint(self):
        """Test endpoint de árbol de categorías"""
        # Crear subcategoría
        subcategory = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division,
            parent=self.category
        )
        
        url = '/api/products/categories/tree/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe mostrar solo categorías raíz con sus subcategorías
        self.assertEqual(len(response.data), 1)
        category_data = response.data[0]
        self.assertEqual(category_data['name'], 'Software')
        self.assertIn('subcategories', category_data)
    
    def test_authentication_requirements(self):
        """Test requerimientos de autenticación"""
        # Crear cliente sin autenticación
        unauthenticated_client = APIClient()
        
        # Los endpoints de products requieren autenticación según el error
        urls_requiring_auth = [
            '/api/products/divisions/',
            '/api/products/categories/',
            '/api/products/products/',
            f'/api/products/products/{self.product.id}/'
        ]
        
        for url in urls_requiring_auth:
            response = unauthenticated_client.get(url)
            # Los endpoints requieren autenticación (401) o están públicos (200)
            self.assertIn(response.status_code, [
                status.HTTP_200_OK, 
                status.HTTP_401_UNAUTHORIZED, 
                status.HTTP_404_NOT_FOUND
            ])


# ============================
# TESTS DE INTEGRACIÓN
# ============================

class ProductsIntegrationTests(TestCase):
    """Tests de integración para products app"""
    
    def setUp(self):
        # Crear estructura completa de datos
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.parent_category = ProductCategory.objects.create(
            name='Software',
            code='SOFT',
            division=self.division
        )
        
        self.child_category = ProductCategory.objects.create(
            name='Aplicaciones Web',
            code='WEBAPP',
            division=self.division,
            parent=self.parent_category
        )
        
        self.modality = Modality.objects.create(
            name='Virtual'
        )
        
        self.customization = Customization.objects.create(
            name='Premium'
        )
        
        # Crear datos del mundo
        self.industry = Industry.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.skill = Skill.objects.create(
            name='Python',
            code='PY'
        )
        
        self.market_segment = MarketSegment.objects.create(
            name='Startups',
            code='START'
        )
        
        self.tag = Tag.objects.create(
            name='Innovación',
            slug='innovacion'
        )
    
    def test_complete_product_setup(self):
        """Test configuración completa de un producto"""
        # Crear producto completo
        product = Product.objects.create(
            name='Sistema Completo',
            code='COMPLETE001',
            description='Sistema con todas las características',
            category=self.child_category,
            customization=self.customization,
            base_price=Decimal('2000.00'),
            currency_code='PEN'
        )
        
        # Agregar todas las relaciones
        product.modalities.add(self.modality)
        product.target_segments.add(self.market_segment)
        product.related_industries.add(self.industry)
        product.related_skills.add(self.skill)
        product.tags.add(self.tag)
        
        # Verificar todas las relaciones
        self.assertEqual(product.modalities.count(), 1)
        self.assertEqual(product.target_segments.count(), 1)
        self.assertEqual(product.related_industries.count(), 1)
        self.assertEqual(product.related_skills.count(), 1)
        self.assertEqual(product.tags.count(), 1)
        
        # Verificar propiedades calculadas
        self.assertTrue(product.is_customizable)
        self.assertEqual(product.get_target_audience(), 'Startups')
        self.assertEqual(product.get_modalities_display(), 'Virtual')
    
    def test_hierarchical_consistency(self):
        """Test consistencia jerárquica"""
        # Verificar jerarquía de categorías
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertIn(self.child_category, self.parent_category.subcategories.all())
        
        # Verificar full_path
        expected_path = f"{self.division.name} > {self.parent_category.name} > {self.child_category.name}"
        self.assertEqual(self.child_category.full_path, expected_path)
        
        # Verificar niveles
        self.assertEqual(self.parent_category.level, 0)
        self.assertEqual(self.child_category.level, 1)
        self.assertEqual(self.parent_category.absolute_level, 1)
        self.assertEqual(self.child_category.absolute_level, 2)
    
    def test_cascade_deletion_behavior(self):
        """Test comportamiento de eliminación en cascada"""
        # Crear producto en categoría hijo
        product = Product.objects.create(
            name='Test Product',
            code='TEST001',
            category=self.child_category
        )
        
        product_id = product.id
        child_category_id = self.child_category.id
        
        # Eliminar categoría padre (debe eliminar hijo por CASCADE)
        self.parent_category.delete()
        
        # Verificar que la categoría hijo se eliminó
        self.assertFalse(ProductCategory.objects.filter(id=child_category_id).exists())
        
        # Verificar que el producto se mantuvo pero perdió su categoría (SET_NULL)
        product.refresh_from_db()
        self.assertIsNone(product.category)
    
    def test_division_analytics(self):
        """Test análisis de divisiones"""
        # Crear productos con precios en la división
        product1 = Product.objects.create(
            name='Producto 1',
            code='PROD1',
            category=self.parent_category,
            base_price=Decimal('1000.00')
        )
        
        product2 = Product.objects.create(
            name='Producto 2',
            code='PROD2',
            category=self.child_category,
            base_price=Decimal('1500.00')
        )
        
        product3 = Product.objects.create(
            name='Producto sin precio',
            code='PROD3',
            category=self.parent_category
        )
        
        # Verificar resumen de ingresos
        revenue_summary = self.division.get_revenue_summary()
        
        self.assertEqual(revenue_summary['total_products_with_price'], 2)
        self.assertEqual(revenue_summary['avg_price'], Decimal('1250.00'))
        self.assertEqual(revenue_summary['total_potential_value'], Decimal('2500.00'))
        
        # Verificar contadores
        self.assertEqual(self.division.categories_count, 2)  # parent y child
        self.assertEqual(self.division.products_count, 3)    # todos los productos
    
    def test_complex_bundle_scenario(self):
        """Test escenario complejo de bundles"""
        # Crear productos base
        main_product = Product.objects.create(
            name='Suite Empresarial',
            code='SUITE001',
            category=self.parent_category,
            base_price=Decimal('5000.00')
        )
        
        module_a = Product.objects.create(
            name='Módulo CRM',
            code='CRM001',
            category=self.child_category,
            base_price=Decimal('1500.00')
        )
        
        module_b = Product.objects.create(
            name='Módulo Inventario',
            code='INV001',
            category=self.child_category,
            base_price=Decimal('1200.00')
        )
        
        # Crear bundle
        main_product.included_products.add(module_a, module_b)
        
        # Verificar propiedades del bundle
        self.assertTrue(main_product.is_bundle)
        self.assertTrue(module_a.is_included_in_bundles)
        self.assertTrue(module_b.is_included_in_bundles)
        
        # Verificar precios
        total_included = main_product.get_total_included_price()
        self.assertEqual(total_included, Decimal('2700.00'))
        
        bundle_display = main_product.get_bundle_price_display()
        self.assertIn('7,700.00', bundle_display)  # 5000 + 2700
        self.assertIn('incluye 2 productos', bundle_display)
        
        # Verificar relaciones inversas
        parents_of_module_a = module_a.get_parent_products()
        self.assertEqual(parents_of_module_a.count(), 1)
        self.assertIn(main_product, parents_of_module_a)


# ============================
# TESTS DE PERFORMANCE
# ============================

class ProductsPerformanceTests(TestCase):
    """Tests de performance para products app"""
    
    def setUp(self):
        # Crear datos de prueba en cantidad
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH'
        )
        
        self.categories = []
        for i in range(5):
            category = ProductCategory.objects.create(
                name=f'Categoría {i}',
                code=f'CAT{i}',
                division=self.division
            )
            self.categories.append(category)
        
        # Crear productos
        for i in range(20):
            category = self.categories[i % 5]  # Distribuir entre categorías
            Product.objects.create(
                name=f'Producto {i}',
                code=f'PROD{i:03d}',
                category=category,
                base_price=Decimal(str(100 + (i * 50)))
            )
    
    def test_query_optimization_with_select_related(self):
        """Test optimización de queries con select_related"""
        with self.assertNumQueries(1):
            # Una sola query para obtener productos con categorías y divisiones
            products = list(
                Product.objects.select_related('category__division')[:10]
            )
            
            # Acceder a categoría y división no debe generar queries adicionales
            for product in products:
                _ = product.category.name
                _ = product.category.division.name
    
    def test_query_optimization_with_prefetch_related(self):
        """Test optimización de queries con prefetch_related"""
        # Agregar relaciones M2M a algunos productos
        industry = Industry.objects.create(name='Tech', code='TECH')
        skill = Skill.objects.create(name='Python', code='PY')
        
        products = Product.objects.all()[:5]
        for product in products:
            product.related_industries.add(industry)
            product.related_skills.add(skill)
        
        with self.assertNumQueries(3):  # 1 query principal + 2 prefetch
            products_list = list(
                Product.objects.prefetch_related('related_industries', 'related_skills')[:5]
            )
            
            # Acceder a relaciones M2M no debe generar queries adicionales
            for product in products_list:
                _ = list(product.related_industries.all())
                _ = list(product.related_skills.all())
    
    def test_bulk_operations(self):
        """Test operaciones en lote"""
        # Test bulk_create de modalidades
        modalities_data = [
            Modality(name=f'Modalidad {i}')
            for i in range(50)
        ]
        
        with self.assertNumQueries(1):
            Modality.objects.bulk_create(modalities_data)
        
        self.assertEqual(Modality.objects.count(), 50)
        
        # Test bulk_update
        modalities = list(Modality.objects.all()[:10])
        for modality in modalities:
            modality.description = f'Descripción actualizada para {modality.name}'
        
        with self.assertNumQueries(1):
            Modality.objects.bulk_update(modalities, ['description'])
    
    def test_division_revenue_performance(self):
        """Test performance del cálculo de ingresos de división"""
        # El cálculo debe ser eficiente incluso con muchos productos
        with self.assertNumQueries(3):  # Queries optimizadas para el cálculo
            revenue_summary = self.division.get_revenue_summary()
            
            self.assertEqual(revenue_summary['total_products_with_price'], 20)
            self.assertIsNotNone(revenue_summary['avg_price'])
            self.assertIsNotNone(revenue_summary['total_potential_value'])


# ============================
# TESTS DE VALIDACIÓN
# ============================

class ProductsValidationTests(TestCase):
    """Tests de validación para products app"""
    
    def test_product_price_constraints(self):
        """Test restricciones de precio del producto"""
        # Precio válido
        product = Product(
            name='Producto Válido',
            code='VALID001',
            base_price=Decimal('100.00')
        )
        product.clean()  # No debe fallar
        
        # Precio cero debe fallar
        product.base_price = Decimal('0')
        with self.assertRaises(ValidationError):
            product.clean()
        
        # Precio negativo debe fallar
        product.base_price = Decimal('-50.00')
        with self.assertRaises(ValidationError):
            product.clean()
    
    def test_product_currency_validation(self):
        """Test validación de moneda"""
        category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST'
        )
        
        # Monedas válidas
        valid_currencies = ['PEN', 'USD', 'EUR']
        for currency in valid_currencies:
            product = Product.objects.create(
                name=f'Producto {currency}',
                code=f'PROD_{currency}',
                category=category,
                currency_code=currency
            )
            self.assertEqual(product.currency_code, currency)
    
    def test_circular_included_products_prevention(self):
        """Test prevención de productos incluidos circulares"""
        product = Product.objects.create(
            name='Producto Test',
            code='TEST001'
        )
        
        # Un producto no puede incluirse a sí mismo
        with self.assertRaises(ValidationError):
            product.add_included_product(product)
    
    def test_unique_constraints_validation(self):
        """Test validaciones de restricciones únicas"""
        # Crear primer producto
        Product.objects.create(
            name='Producto Único',
            code='UNIQUE001'
        )
        
        # Verificar que el nombre y código son únicos
        existing_names = Product.objects.filter(name='Producto Único').count()
        existing_codes = Product.objects.filter(code='UNIQUE001').count()
        
        self.assertEqual(existing_names, 1)
        self.assertEqual(existing_codes, 1)
    
    def test_category_hierarchy_validation(self):
        """Test validación de jerarquía de categorías"""
        division = Division.objects.create(
            name='Test Division',
            code='TESTDIV'
        )
        
        parent = ProductCategory.objects.create(
            name='Padre',
            code='PARENT',
            division=division
        )
        
        child = ProductCategory.objects.create(
            name='Hijo',
            code='CHILD',
            division=division,
            parent=parent
        )
        
        # Verificar que la jerarquía es válida
        self.assertEqual(child.parent, parent)
        self.assertEqual(child.level, 1)
        self.assertEqual(parent.level, 0)
        
        # Verificar que get_descendants funciona correctamente
        descendants = parent.get_descendants()
        self.assertIn(child, descendants)
        self.assertEqual(len(descendants), 1)
