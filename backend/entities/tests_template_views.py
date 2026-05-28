"""Tests for entities HTML template views."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import IndividualProfile, Organization, Person
from .test_factories import create_test_country, create_test_person_id_type

User = get_user_model()


class EntitiesTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='entitieshtml',
            email='entitieshtml@example.com',
            password='testpass123',
        )
        self.country = create_test_country()
        self.id_type = create_test_person_id_type(country=self.country)
        self.person = Person.objects.create(
            first_name='Ana',
            last_name='García',
            country_of_nationality=self.country,
            id_type=self.id_type,
            id_number='12345678',
        )
        self.organization = Organization.objects.create(
            name='Acme Corp',
            legal_name='Acme S.A.C.',
        )

    def test_anonymous_list_redirects_to_login(self):
        response = self.client.get(reverse('entities_html:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_list_renders_person(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.get(reverse('entities_html:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana')
        self.assertContains(response, 'Gestión de Entidades')

    def test_organizations_tab(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.get(reverse('entities_html:list'), {'tab': 'organizations'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acme Corp')

    def test_search_filters_people(self):
        self.client.login(username='entitieshtml', password='testpass123')
        Person.objects.create(first_name='Otro', last_name='Usuario')
        response = self.client.get(reverse('entities_html:list'), {'q': 'Ana'})
        self.assertContains(response, 'García')
        self.assertNotContains(response, 'Otro Usuario')

    def test_person_create_and_detail(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.post(
            reverse('entities_html:person_create'),
            {
                'first_name': 'Luis',
                'last_name': 'Torres',
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(first_name='Luis')
        self.assertRedirects(
            response,
            reverse('entities_html:person_detail', kwargs={'pk': person.pk}),
        )

    def test_person_detail_update(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.post(
            reverse('entities_html:person_detail', kwargs={'pk': self.person.pk}),
            {
                'first_name': 'Ana',
                'middle_name': '',
                'last_name': 'López',
                'second_last_name': '',
                'gender': '',
                'birthday': '',
                'marital_status': '',
                'country_of_nationality': str(self.country.pk),
                'id_type': str(self.id_type.pk),
                'id_number': '12345678',
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.person.refresh_from_db()
        self.assertEqual(self.person.last_name, 'López')

    def test_person_delete(self):
        self.client.login(username='entitieshtml', password='testpass123')
        pk = self.person.pk
        response = self.client.post(reverse('entities_html:person_delete', kwargs={'pk': pk}))
        self.assertRedirects(response, reverse('entities_html:list'))
        self.assertFalse(Person.objects.filter(pk=pk).exists())

    def test_organization_create_and_detail(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.post(
            reverse('entities_html:org_create'),
            {
                'name': 'Beta LLC',
                'legal_name': 'Beta LLC',
                'main_address': '',
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        org = Organization.objects.get(name='Beta LLC')
        self.assertRedirects(
            response,
            reverse('entities_html:org_detail', kwargs={'pk': org.pk}),
        )

    def test_organization_delete(self):
        self.client.login(username='entitieshtml', password='testpass123')
        pk = self.organization.pk
        response = self.client.post(reverse('entities_html:org_delete', kwargs={'pk': pk}))
        self.assertRedirects(response, reverse('entities_html:list'))
        self.assertFalse(Organization.objects.filter(pk=pk).exists())

    def test_person_create_profile(self):
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.post(
            reverse('entities_html:person_create_profile', kwargs={'pk': self.person.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(IndividualProfile.objects.filter(person=self.person).exists())

    def test_person_create_profile_when_exists_shows_error(self):
        IndividualProfile.objects.create(person=self.person)
        self.client.login(username='entitieshtml', password='testpass123')
        response = self.client.post(
            reverse('entities_html:person_create_profile', kwargs={'pk': self.person.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IndividualProfile.objects.filter(person=self.person).count(), 1)

    def test_detail_404(self):
        self.client.login(username='entitieshtml', password='testpass123')
        import uuid

        response = self.client.get(
            reverse('entities_html:person_detail', kwargs={'pk': uuid.uuid4()}),
        )
        self.assertEqual(response.status_code, 404)
