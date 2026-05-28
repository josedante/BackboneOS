import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class DashboardHomeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashboarduser',
            email='dash@example.com',
            password='testpass123',
        )

    def test_anonymous_home_redirects_to_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_home_renders_dashboard(self):
        self.client.login(username='dashboarduser', password='testpass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to BackboneOS')
        self.assertContains(response, 'Quick Actions')
        self.assertContains(response, 'Recent Activity')

    def test_api_root_returns_json_catalog(self):
        response = self.client.get(reverse('api-catalog'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'BackboneOS API')
        self.assertIn('products', data['endpoints']['api'])
