from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import OurOrganization, Division, Seat, Unit, Position, Team
from world.models import Country, Industry, OrganizationType

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
