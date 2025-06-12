from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from world.models import Country, PersonalIDType, OrganizationType, Industry
from .models import Person, ContactDetail, IndividualProfile, Organization, PhysicalAddress


class PersonModelTest(TestCase):
    """Tests para el modelo Person"""
    
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE', 
            name='Perú',
            official_name='República del Perú'
        )
        self.id_type = PersonalIDType.objects.create(
            name='DNI',
            code='DNI',
            country=self.country
        )
    
    def test_person_creation(self):
        """Test de creación básica de persona"""
        person = Person.objects.create(
            first_name='Juan',
            fathers_name='Pérez',
            country_of_nationality=self.country,
            id_type=self.id_type,
            id_number='12345678'
        )
        
        self.assertEqual(person.first_name, 'Juan')
        self.assertEqual(person.fathers_name, 'Pérez')
        self.assertEqual(str(person), 'Juan Pérez')
    
    def test_full_name_property(self):
        """Test de la propiedad full_name"""
        person = Person.objects.create(
            first_name='Juan',
            middle_name='Carlos',
            fathers_name='Pérez',
            mothers_name='García'
        )
        
        self.assertEqual(person.full_name, 'Juan Carlos Pérez García')
    
    def test_primary_contact(self):
        """Test de contacto principal"""
        person = Person.objects.create(
            first_name='Juan',
            fathers_name='Pérez'
        )
        
        contact = ContactDetail.objects.create(
            person=person,
            email='juan@example.com',
            is_primary=True
        )
        
        self.assertEqual(person.primary_contact, contact)
        self.assertEqual(person.primary_email, 'juan@example.com')


class OrganizationModelTest(TestCase):
    """Tests para el modelo Organization"""
    
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE',
            name='Perú',
            official_name='República del Perú'
        )
        self.org_type = OrganizationType.objects.create(
            name='Empresa',
            code='EMP'
        )
        self.industry = Industry.objects.create(
            name='Tecnología',
            code='TECH'
        )
    
    def test_organization_creation(self):
        """Test de creación básica de organización"""
        org = Organization.objects.create(
            name='Tech Corp',
            legal_name='Tech Corporation S.A.C.',
            org_type=self.org_type,
            industry=self.industry,
            country=self.country,
            id_number='20123456789'
        )
        
        self.assertEqual(org.name, 'Tech Corp')
        self.assertEqual(org.display_name, 'Tech Corporation S.A.C.')
        self.assertEqual(str(org), 'Tech Corp')
    
    def test_has_complete_info(self):
        """Test de validación de información completa"""
        org = Organization.objects.create(
            name='Tech Corp',
            org_type=self.org_type,
            industry=self.industry,
            country=self.country,
            id_number='20123456789'
        )
        
        # Sin id_type, no está completa
        self.assertFalse(org.has_complete_profile())


class PersonAPITest(APITestCase):
    """Tests para la API de personas"""
    
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE',
            name='Perú',
            official_name='República del Perú'
        )
        self.person = Person.objects.create(
            first_name='Juan',
            fathers_name='Pérez',
            country_of_nationality=self.country
        )
        self.list_url = reverse('entities:person-list')
        self.detail_url = reverse('entities:person-detail', kwargs={'pk': self.person.pk})
    
    def test_get_person_list(self):
        """Test de listado de personas"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Juan Pérez')
    
    def test_get_person_detail(self):
        """Test de detalle de persona"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Juan')
        self.assertEqual(response.data['fathers_name'], 'Pérez')
    
    def test_choices_endpoint(self):
        """Test del endpoint de choices"""
        url = reverse('entities:entities-choices-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('gender_choices', response.data)
        self.assertIn('marital_status_choices', response.data)


class OrganizationAPITest(APITestCase):
    """Tests para la API de organizaciones"""
    
    def setUp(self):
        self.country = Country.objects.create(
            iso3_code='PER',
            iso2_code='PE',
            name='Perú',
            official_name='República del Perú'
        )
        self.org_type = OrganizationType.objects.create(
            name='Empresa',
            code='EMP'
        )
        self.industry = Industry.objects.create(
            name='Tecnología',
            code='TECH'
        )
        self.organization = Organization.objects.create(
            name='Tech Corp',
            org_type=self.org_type,
            industry=self.industry,
            country=self.country,
            id_number='20123456789'
        )
        self.list_url = reverse('entities:organization-list')
        self.detail_url = reverse('entities:organization-detail', kwargs={'pk': self.organization.pk})
    
    def test_get_organization_list(self):
        """Test de listado de organizaciones"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tech Corp')
    
    def test_get_organization_detail(self):
        """Test de detalle de organización"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tech Corp')
        self.assertEqual(response.data['id_number'], '20123456789')
