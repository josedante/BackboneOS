"""
Tests for the interactions section HTML views (substrate stance).

Interactions are read-only here; only touchpoint config is editable. The
per-entity interaction timeline is asserted via the entities detail page.
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Touchpoint
from .test_factories import create_interaction_graph

User = get_user_model()


class InteractionsTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        graph = create_interaction_graph()
        self.user = graph['user']
        self.interaction = graph['interaction']
        self.touchpoint = graph['touchpoint']
        self.person = graph['person']

    def test_anonymous_list_redirects_to_login(self):
        response = self.client.get(reverse('interactions_html:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_list_renders_interaction(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.get(reverse('interactions_html:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Interacciones')
        self.assertContains(response, 'John')

    def test_touchpoints_tab(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.get(reverse('interactions_html:list'), {'tab': 'touchpoints'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homepage')

    def test_interaction_detail_is_read_only(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.get(
            reverse('interactions_html:interaction_detail', kwargs={'pk': self.interaction.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'solo lectura')
        # No interaction edit fields are rendered (read-only surface).
        self.assertNotContains(response, 'name="session_id"')
        self.assertNotContains(response, 'name="duration_seconds"')

    def test_interaction_create_route_removed(self):
        """Hand-entry route no longer exists under the interactions namespace."""
        from django.urls import NoReverseMatch

        with self.assertRaises(NoReverseMatch):
            reverse('interactions_html:interaction_create')

    def test_touchpoint_create_post(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.post(
            reverse('interactions_html:touchpoint_create'),
            {
                'name': 'Landing Page',
                'code': 'LANDING',
                'channel': self.touchpoint.channel_id,
                'medium': self.touchpoint.medium_id,
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Touchpoint.objects.filter(code='LANDING').exists())

    def test_touchpoint_detail_update(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.post(
            reverse('interactions_html:touchpoint_detail', kwargs={'pk': self.touchpoint.pk}),
            {
                'name': 'Homepage v2',
                'code': 'HOMEPAGE',
                'channel': self.touchpoint.channel_id,
                'medium': self.touchpoint.medium_id,
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.touchpoint.refresh_from_db()
        self.assertEqual(self.touchpoint.name, 'Homepage v2')

    def test_touchpoint_delete(self):
        self.client.login(username='interactionshtml', password='testpass123')
        pk = self.touchpoint.pk
        response = self.client.post(
            reverse('interactions_html:touchpoint_delete', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Touchpoint.objects.filter(pk=pk).exists())

    def test_interaction_detail_404(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.get(
            reverse('interactions_html:interaction_detail', kwargs={'pk': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)


class EntityInteractionTimelineTests(TestCase):
    """The high-value cross-cutting read: customer interaction timeline."""

    def setUp(self):
        self.client = Client()
        graph = create_interaction_graph()
        self.user = graph['user']
        self.person = graph['person']
        self.touchpoint = graph['touchpoint']

    def test_person_detail_shows_interaction_timeline(self):
        self.client.login(username='interactionshtml', password='testpass123')
        response = self.client.get(
            reverse('entities_html:person_detail', kwargs={'pk': self.person.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Interacciones')
        self.assertContains(response, self.touchpoint.name)
