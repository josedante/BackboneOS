from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import OurOrganization, Division, Seat, Unit, Position, Team
from world.models import Country, Industry, OrganizationType
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class OurOrganizationModelTest(TestCase):
    def setUp(self):
        # Crear datos de prueba del world
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.industry = Industry.objects.create(name='Tecnología')
        self.org_type = OrganizationType.objects.create(name='SAC')

    def test_unique_active_constraint(self):
        """Prueba que solo puede haber una organización activa"""
        org1 = OurOrganization.objects.create(
            name='Org 1', 
            is_active=True,
            country=self.country
        )
        
        # Crear segunda organización activa debe fallar
        org2 = OurOrganization(
            name='Org 2', 
            is_active=True,
            country=self.country
        )
        
        with self.assertRaises(ValidationError):
            org2.full_clean()

    def test_organization_creation(self):
        """Prueba creación exitosa de organización"""
        org = OurOrganization.objects.create(
            name='BackboneOS',
            legal_name='Backbone Operating Systems SAC',
            tax_id='20500000000',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        
        self.assertEqual(org.name, 'BackboneOS')
        self.assertEqual(str(org), 'Backbone Operating Systems SAC')
        self.assertTrue(org.is_active)

class DivisionModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='Org Test', 
            is_active=True,
            country=self.country
        )

    def test_division_creation(self):
        """Prueba creación de división"""
        division = Division.objects.create(
            name='Tecnología',
            code='TECH',
            description='División de desarrollo tecnológico',
            organization=self.org
        )
        
        self.assertEqual(division.name, 'Tecnología')
        self.assertEqual(division.code, 'TECH')
        self.assertEqual(division.organization, self.org)
        self.assertEqual(str(division), f'Tecnología ({self.org.name})')

    def test_division_unique_constraints(self):
        """Prueba que name y code son únicos por organización"""
        Division.objects.create(
            name='Tech', 
            code='TECH',
            organization=self.org
        )
        
        # Nombre duplicado en misma organización debe fallar
        with self.assertRaises(Exception):
            Division.objects.create(
                name='Tech', 
                code='TECH2',
                organization=self.org
            )
        
        # Código duplicado en misma organización debe fallar
        with self.assertRaises(Exception):
            Division.objects.create(
                name='Technology', 
                code='TECH',
                organization=self.org
            )

class SeatModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='Org X', 
            is_active=True,
            country=self.country
        )

    def test_seat_creation(self):
        """Prueba creación de sede"""
        seat = Seat.objects.create(
            name='Sede Central',
            code='HQT1',
            category='HQT',
            organization=self.org
        )
        
        self.assertEqual(seat.organization, self.org)
        self.assertEqual(seat.category, 'HQT')
        self.assertEqual(str(seat), 'Sede Central')

class UnitModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='Org Test', 
            is_active=True,
            country=self.country
        )
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH',
            organization=self.org
        )

    def test_unit_hierarchy(self):
        """Prueba jerarquía de unidades"""
        parent = Unit.objects.create(
            name='Gerencia General',
            code='GG001',
            division=self.division
        )
        child = Unit.objects.create(
            name='Gerencia de Marketing', 
            code='GM001',
            parent=parent,
            division=self.division
        )
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_unit_without_parent(self):
        """Prueba unidad sin padre (nivel raíz)"""
        unit = Unit.objects.create(
            name='Dirección Ejecutiva',
            code='DE001',
            division=self.division
        )
        
        self.assertIsNone(unit.parent)
        self.assertEqual(str(unit), 'Dirección Ejecutiva (Tecnología)')

    def test_unit_full_path(self):
        """Prueba generación de ruta completa"""
        parent = Unit.objects.create(
            name='Gerencia',
            code='GER001',
            division=self.division
        )
        child = Unit.objects.create(
            name='Subgerencia', 
            code='SUB001',
            parent=parent,
            division=self.division
        )
        
        expected_path = f"{self.division.name} > {parent.name} > {child.name}"
        self.assertEqual(child.full_path, expected_path)
        
    def test_unit_unique_constraint(self):
        """Prueba que code es único por división"""
        Unit.objects.create(
            name='Desarrollo',
            code='DEV001',
            division=self.division
        )
        
        # Código duplicado en misma división debe fallar
        with self.assertRaises(Exception):
            Unit.objects.create(
                name='Desarrollo Alternativo',
                code='DEV001',
                division=self.division
            )

class PositionModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='Org Test', 
            is_active=True,
            country=self.country
        )
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH',
            organization=self.org
        )
        self.unit = Unit.objects.create(
            name='Desarrollo', 
            code='DEV',
            division=self.division
        )

    def test_position_link_to_unit(self):
        """Prueba vinculación de cargo a unidad"""
        position = Position.objects.create(
            name='Desarrollador Senior',
            code='DEV001',
            description='Desarrollo de aplicaciones web',
            unit=self.unit
        )
        
        self.assertEqual(position.unit, self.unit)
        self.assertEqual(str(position), 'Desarrollador Senior - Desarrollo')
        
    def test_position_unique_constraint(self):
        """Prueba que code es único por unidad"""
        Position.objects.create(
            name='Desarrollador Senior',
            code='DEV001',
            unit=self.unit
        )
        
        # Código duplicado en misma unidad debe fallar
        with self.assertRaises(Exception):
            Position.objects.create(
                name='Desarrollador Junior',
                code='DEV001',
                unit=self.unit
            )

class TeamModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='Org Test', 
            is_active=True,
            country=self.country
        )
        self.division = Division.objects.create(
            name='Tecnología',
            code='TECH',
            organization=self.org
        )

    def test_team_creation(self):
        """Prueba creación de equipo"""
        team = Team.objects.create(
            name='Equipo de Innovación',
            code='INNOV',
            division=self.division
        )
        
        self.assertTrue(team.is_active)
        self.assertEqual(str(team), f'Equipo de Innovación ({self.division.name})')

    def test_team_unique_constraints(self):
        """Prueba que name y code son únicos por división"""
        Team.objects.create(
            name='Innovation', 
            code='INNOV',
            division=self.division
        )
        
        # Nombre duplicado en misma división debe fallar
        with self.assertRaises(Exception):
            Team.objects.create(
                name='Innovation', 
                code='INNOV2',
                division=self.division
            )

class IntegrationTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.org = OurOrganization.objects.create(
            name='BackboneOS',
            is_active=True,
            country=self.country
        )

    def test_complete_organizational_structure(self):
        """Prueba estructura organizacional completa"""
        # Crear división
        division = Division.objects.create(
            name='Tecnología',
            code='TECH',
            organization=self.org
        )
        
        # Crear sede
        seat = Seat.objects.create(
            name='Oficina Principal',
            code='MAIN',
            organization=self.org
        )
        
        # Crear unidad
        unit = Unit.objects.create(
            name='Desarrollo de Software',
            code='DEV001',
            division=division
        )
        
        # Crear cargo
        position = Position.objects.create(
            name='Tech Lead',
            code='TL001',
            unit=unit
        )
        
        # Crear equipo
        team = Team.objects.create(
            name='Squad Backend',
            code='BACK',
            division=division
        )
        
        # Verificar que todo esté conectado
        self.assertEqual(seat.organization, self.org)
        self.assertEqual(division.organization, self.org)
        self.assertEqual(unit.division, division)
        self.assertEqual(position.unit, unit)
        self.assertEqual(team.division, division)
        self.assertTrue(all([
            division.is_active,
            seat.is_active,
            unit.is_active,
            position.is_active,
            team.is_active
        ]))
        
        # Verificar propiedades calculadas
        self.assertEqual(division.units_count, 1)
        self.assertEqual(division.teams_count, 1)
        self.assertEqual(unit.positions_count, 1)

# ============================
# TESTS DE API ENDPOINTS
# ============================

class OurInstitutionAPITestCase(APITestCase):
    """Tests base para APIs de our_institution"""
    
    def setUp(self):
        """Configuración común para todos los tests de API"""
        self.client = APIClient()
        
        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
        
        # Crear datos base necesarios
        self.country = Country.objects.create(
            iso3_code='TST',
            iso2_code='TS',
            name='Test Country',
            official_name='Republic of Test Country'
        )
        
        self.industry = Industry.objects.create(
            name='Technology',
            code='TECH'
        )
        
        self.org_type = OrganizationType.objects.create(
            name='Private Company',
            code='PVT'
        )

class OurOrganizationAPITests(OurInstitutionAPITestCase):
    """Tests para la API de OurOrganization"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            legal_name='Test Organization Inc.',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.list_url = reverse('ourorganization-list')
        self.detail_url = reverse('ourorganization-detail', kwargs={'pk': self.organization.pk})
    
    def test_list_organizations(self):
        """Test listar organizaciones"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Organization')
    
    def test_get_organization_detail(self):
        """Test obtener detalle de organización"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Organization')
        self.assertEqual(response.data['legal_name'], 'Test Organization Inc.')
        
        # Verificar campos calculados
        self.assertIn('divisions_count', response.data)
        self.assertIn('seats_count', response.data)
        self.assertIn('units_count', response.data)
        self.assertIn('teams_count', response.data)
        self.assertIn('positions_count', response.data)
    
    def test_create_organization(self):
        """Test crear organización"""
        data = {
            'name': 'New Organization',
            'legal_name': 'New Organization LLC',
            'country': self.country.iso3_code,
            'industry': self.industry.id,
            'org_type': self.org_type.id,
            'is_active': True
        }
        
        # Primero desactivar la organización actual para evitar constraint
        self.organization.is_active = False
        self.organization.save()
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Organization')
    
    def test_organization_filtering(self):
        """Test filtrado de organizaciones"""
        # Filtrar por país
        response = self.client.get(self.list_url, {'country': self.country.iso3_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por industria
        response = self.client.get(self.list_url, {'industry': self.industry.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_organization_search(self):
        """Test búsqueda en organizaciones"""
        response = self.client.get(self.list_url, {'search': 'Test Organization'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class DivisionAPITests(OurInstitutionAPITestCase):
    """Tests para la API de Division"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.division = Division.objects.create(
            name='Technology Division',
            code='TECH',
            description='Technology and innovation division',
            organization=self.organization
        )
        self.list_url = reverse('division-list')
        self.detail_url = reverse('division-detail', kwargs={'pk': self.division.pk})
    
    def test_list_divisions(self):
        """Test listar divisiones"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Technology Division')
    
    def test_get_division_detail(self):
        """Test obtener detalle de división"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology Division')
        self.assertEqual(response.data['code'], 'TECH')
        self.assertEqual(response.data['organization_name'], 'Test Organization')
        
        # Verificar campos calculados
        self.assertIn('units_count', response.data)
        self.assertIn('teams_count', response.data)
        self.assertIn('positions_count', response.data)
    
    def test_create_division(self):
        """Test crear división"""
        data = {
            'name': 'Sales Division',
            'code': 'SALES',
            'description': 'Sales and marketing division',
            'organization': self.organization.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sales Division')
        self.assertEqual(response.data['code'], 'SALES')
    
    def test_division_filtering(self):
        """Test filtrado de divisiones"""
        # Filtrar por organización
        response = self.client.get(self.list_url, {'organization': self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por estado activo
        response = self.client.get(self.list_url, {'is_active': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_division_search(self):
        """Test búsqueda en divisiones"""
        response = self.client.get(self.list_url, {'search': 'Technology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class SeatAPITests(OurInstitutionAPITestCase):
    """Tests para la API de Seat"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.seat = Seat.objects.create(
            name='Main Office',
            code='MAIN',
            category='HQT',
            organization=self.organization
        )
        self.list_url = reverse('seat-list')
        self.detail_url = reverse('seat-detail', kwargs={'pk': self.seat.pk})
    
    def test_list_seats(self):
        """Test listar sedes"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Main Office')
    
    def test_get_seat_detail(self):
        """Test obtener detalle de sede"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Main Office')
        self.assertEqual(response.data['code'], 'MAIN')
        self.assertEqual(response.data['category'], 'HQT')
    
    def test_create_seat(self):
        """Test crear sede"""
        data = {
            'name': 'Branch Office',
            'code': 'BRANCH',
            'category': 'SUB',  # Usar 'SUB' que es una opción válida (Sucursal)
            'organization': self.organization.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Branch Office')
        self.assertEqual(response.data['category'], 'SUB')
    
    def test_seat_filtering(self):
        """Test filtrado de sedes"""
        # Filtrar por categoría
        response = self.client.get(self.list_url, {'category': 'HQT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por organización
        response = self.client.get(self.list_url, {'organization': self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class UnitAPITests(OurInstitutionAPITestCase):
    """Tests para la API de Unit"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.division = Division.objects.create(
            name='Technology Division',
            code='TECH',
            organization=self.organization
        )
        self.unit = Unit.objects.create(
            name='Software Development',
            code='SOFT',
            description='Software development unit',
            division=self.division
        )
        self.list_url = reverse('unit-list')
        self.detail_url = reverse('unit-detail', kwargs={'pk': self.unit.pk})
    
    def test_list_units(self):
        """Test listar unidades"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Software Development')
    
    def test_get_unit_detail(self):
        """Test obtener detalle de unidad"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Software Development')
        self.assertEqual(response.data['code'], 'SOFT')
        self.assertEqual(response.data['division_name'], 'Technology Division')
        
        # Verificar campos calculados
        self.assertIn('positions_count', response.data)
        self.assertIn('full_path', response.data)
    
    def test_create_unit(self):
        """Test crear unidad"""
        data = {
            'name': 'Quality Assurance',
            'code': 'QA',
            'description': 'Quality assurance unit',
            'division': self.division.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Quality Assurance')
        self.assertEqual(response.data['code'], 'QA')
    
    def test_unit_hierarchy(self):
        """Test jerarquía de unidades"""
        # Crear unidad padre
        parent_unit = Unit.objects.create(
            name='Engineering',
            code='ENG',
            division=self.division
        )
        
        # Crear unidad hija
        data = {
            'name': 'Backend Development',
            'code': 'BACKEND',
            'division': self.division.id,
            'parent': parent_unit.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['parent']), str(parent_unit.id))
    
    def test_unit_filtering(self):
        """Test filtrado de unidades"""
        # Filtrar por división
        response = self.client.get(self.list_url, {'division': self.division.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por organización (a través de división)
        response = self.client.get(self.list_url, {'division__organization': self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PositionAPITests(OurInstitutionAPITestCase):
    """Tests para la API de Position"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.division = Division.objects.create(
            name='Technology Division',
            code='TECH',
            organization=self.organization
        )
        self.unit = Unit.objects.create(
            name='Software Development',
            code='SOFT',
            division=self.division
        )
        self.position = Position.objects.create(
            name='Senior Developer',
            code='SDEV',
            description='Senior software developer position',
            unit=self.unit
        )
        self.list_url = reverse('position-list')
        self.detail_url = reverse('position-detail', kwargs={'pk': self.position.pk})
    
    def test_list_positions(self):
        """Test listar posiciones"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Senior Developer')
    
    def test_get_position_detail(self):
        """Test obtener detalle de posición"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Senior Developer')
        self.assertEqual(response.data['code'], 'SDEV')
        self.assertEqual(response.data['unit_name'], 'Software Development')
        self.assertEqual(response.data['division_name'], 'Technology Division')
    
    def test_create_position(self):
        """Test crear posición"""
        data = {
            'name': 'Junior Developer',
            'code': 'JDEV',
            'description': 'Junior software developer position',
            'unit': self.unit.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Junior Developer')
        self.assertEqual(response.data['code'], 'JDEV')
    
    def test_position_filtering(self):
        """Test filtrado de posiciones"""
        # Filtrar por unidad
        response = self.client.get(self.list_url, {'unit': self.unit.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por división (a través de unidad)
        response = self.client.get(self.list_url, {'unit__division': self.division.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por organización (a través de unidad->división)
        response = self.client.get(self.list_url, {'unit__division__organization': self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class TeamAPITests(OurInstitutionAPITestCase):
    """Tests para la API de Team"""
    
    def setUp(self):
        super().setUp()
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        self.division = Division.objects.create(
            name='Technology Division',
            code='TECH',
            organization=self.organization
        )
        self.team = Team.objects.create(
            name='Agile Squad',
            code='AGILE',
            description='Agile development team',
            division=self.division
        )
        self.list_url = reverse('team-list')
        self.detail_url = reverse('team-detail', kwargs={'pk': self.team.pk})
    
    def test_list_teams(self):
        """Test listar equipos"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Agile Squad')
    
    def test_get_team_detail(self):
        """Test obtener detalle de equipo"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Agile Squad')
        self.assertEqual(response.data['code'], 'AGILE')
        self.assertEqual(response.data['division_name'], 'Technology Division')
    
    def test_create_team(self):
        """Test crear equipo"""
        data = {
            'name': 'DevOps Team',
            'code': 'DEVOPS',
            'description': 'DevOps and infrastructure team',
            'division': self.division.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'DevOps Team')
        self.assertEqual(response.data['code'], 'DEVOPS')
    
    def test_team_filtering(self):
        """Test filtrado de equipos"""
        # Filtrar por división
        response = self.client.get(self.list_url, {'division': self.division.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por organización (a través de división)
        response = self.client.get(self.list_url, {'division__organization': self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


# ============================
# TESTS DE INTEGRACIÓN API
# ============================

class OurInstitutionIntegrationTests(OurInstitutionAPITestCase):
    """Tests de integración entre diferentes endpoints"""
    
    def test_complete_organization_flow(self):
        """Test flujo completo de creación de estructura organizacional"""
        # 1. Crear organización
        org_data = {
            'name': 'Tech Corp',
            'legal_name': 'Tech Corporation Inc.',
            'country': self.country.iso3_code,
            'industry': self.industry.id,
            'org_type': self.org_type.id,
            'is_active': True
        }
        org_response = self.client.post(
            reverse('ourorganization-list'),
            org_data,
            format='json'
        )
        self.assertEqual(org_response.status_code, status.HTTP_201_CREATED)
        org_id = org_response.data['id']
        
        # 2. Crear división
        division_data = {
            'name': 'Technology',
            'code': 'TECH',
            'description': 'Technology division',
            'organization': org_id
        }
        division_response = self.client.post(
            reverse('division-list'),
            division_data,
            format='json'
        )
        self.assertEqual(division_response.status_code, status.HTTP_201_CREATED)
        division_id = division_response.data['id']
        
        # 3. Crear sede
        seat_data = {
            'name': 'Headquarters',
            'code': 'HQ',
            'category': 'HQT',
            'organization': org_id
        }
        seat_response = self.client.post(
            reverse('seat-list'),
            seat_data,
            format='json'
        )
        self.assertEqual(seat_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Crear unidad
        unit_data = {
            'name': 'Development',
            'code': 'DEV',
            'description': 'Software development unit',
            'division': division_id
        }
        unit_response = self.client.post(
            reverse('unit-list'),
            unit_data,
            format='json'
        )
        self.assertEqual(unit_response.status_code, status.HTTP_201_CREATED)
        unit_id = unit_response.data['id']
        
        # 5. Crear posición
        position_data = {
            'name': 'Software Engineer',
            'code': 'SE',
            'description': 'Software engineer position',
            'unit': unit_id
        }
        position_response = self.client.post(
            reverse('position-list'),
            position_data,
            format='json'
        )
        self.assertEqual(position_response.status_code, status.HTTP_201_CREATED)
        
        # 6. Crear equipo
        team_data = {
            'name': 'Backend Squad',
            'code': 'BACKEND',
            'description': 'Backend development team',
            'division': division_id
        }
        team_response = self.client.post(
            reverse('team-list'),
            team_data,
            format='json'
        )
        self.assertEqual(team_response.status_code, status.HTTP_201_CREATED)
        
        # 7. Verificar que la organización tiene las métricas actualizadas
        org_detail_response = self.client.get(
            reverse('ourorganization-detail', kwargs={'pk': org_id})
        )
        self.assertEqual(org_detail_response.status_code, status.HTTP_200_OK)
        
        # Verificar conteos
        org_data = org_detail_response.data
        self.assertEqual(org_data['divisions_count'], 1)
        self.assertEqual(org_data['seats_count'], 1)
        self.assertEqual(org_data['units_count'], 1)
        self.assertEqual(org_data['teams_count'], 1)
        self.assertEqual(org_data['positions_count'], 1)
    
    def test_hierarchical_filtering(self):
        """Test filtrado jerárquico entre endpoints"""
        # Crear estructura básica
        organization = OurOrganization.objects.create(
            name='Filter Test Corp',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        division = Division.objects.create(
            name='Sales',
            code='SALES',
            organization=organization
        )
        unit = Unit.objects.create(
            name='Inside Sales',
            code='INSIDE',
            division=division
        )
        
        # Test filtrar divisiones por organización
        response = self.client.get(
            reverse('division-list'),
            {'organization': organization.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtrar unidades por división
        response = self.client.get(
            reverse('unit-list'),
            {'division': division.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtrar posiciones por organización (a través de jerarquía)
        position = Position.objects.create(
            name='Sales Rep',
            code='SREP',
            unit=unit
        )
        
        response = self.client.get(
            reverse('position-list'),
            {'unit__division__organization': organization.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


# ============================
# TESTS DE VALIDACIÓN API
# ============================

class OurInstitutionValidationTests(OurInstitutionAPITestCase):
    """Tests de validación para APIs de our_institution"""
    
    def test_unique_constraints_validation(self):
        """Test validación de constraints únicos"""
        # Crear organización y división
        organization = OurOrganization.objects.create(
            name='Validation Test Corp',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        division = Division.objects.create(
            name='Engineering',
            code='ENG',
            organization=organization
        )
        
        # Test constraint único en Division (code por organización)
        duplicate_division_data = {
            'name': 'Engineering 2',
            'code': 'ENG',  # Código duplicado
            'organization': organization.id
        }
        response = self.client.post(
            reverse('division-list'),
            duplicate_division_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test constraint único en Unit (code por división)
        unit = Unit.objects.create(
            name='Backend',
            code='BACK',
            division=division
        )
        
        duplicate_unit_data = {
            'name': 'Backend 2',
            'code': 'BACK',  # Código duplicado
            'division': division.id
        }
        response = self.client.post(
            reverse('unit-list'),
            duplicate_unit_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_required_fields_validation(self):
        """Test validación de campos requeridos"""
        # Test división sin organización
        division_data = {
            'name': 'Marketing',
            'code': 'MKT'
            # Falta 'organization'
        }
        response = self.client.post(
            reverse('division-list'),
            division_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test unidad sin división
        unit_data = {
            'name': 'Sales Team',
            'code': 'SALES'
            # Falta 'division'
        }
        response = self.client.post(
            reverse('unit-list'),
            unit_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_functionality(self):
        """Test funcionalidad de búsqueda"""
        # Crear datos para búsqueda
        organization = OurOrganization.objects.create(
            name='Search Test Corporation',
            country=self.country,
            industry=self.industry,
            org_type=self.org_type,
            is_active=True
        )
        division = Division.objects.create(
            name='Research and Development',
            code='RND',
            description='Innovation and research division',
            organization=organization
        )
        
        # Test búsqueda por nombre
        response = self.client.get(
            reverse('division-list'),
            {'search': 'Research'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test búsqueda por código
        response = self.client.get(
            reverse('division-list'),
            {'search': 'RND'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test búsqueda por descripción
        response = self.client.get(
            reverse('division-list'),
            {'search': 'Innovation'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
