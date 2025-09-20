"""
Adapter tests for the websites app.

This module tests the WebTouchpointAdapter functionality.
"""

from django.test import TestCase
from unittest.mock import Mock
from django.contrib.auth import get_user_model

from our_institution.models import OurOrganization, Division
from connectors.protocols import TouchpointHint
from websites.models import Website
from websites.adapters import infer_web_touchpoint_hint

User = get_user_model()


class WebTouchpointAdapterTest(TestCase):
    """Test cases for the WebTouchpointAdapter."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.our_organization = OurOrganization.objects.create(
            name='Test Organization',
            legal_name='Test Organization Legal',
            is_active=True
        )
        self.division = Division.objects.create(
            organization=self.our_organization,
            name='Test Division',
            code='TEST',
            description='Test division for testing'
        )
        self.website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com'
        )
    
    def test_infer_touchpoint_hint_page_view(self):
        """Test touchpoint hint inference for page view."""
        mock_interaction = Mock()
        mock_interaction.payload = {'event_type': 'page_view', 'page': '/test'}
        mock_interaction.metadata = {'ip_address': '192.168.1.1'}
        mock_interaction.website = self.website
        mock_interaction.session_id = 'test-session'
        mock_interaction.visitor_cookie = 'test-cookie'
        mock_interaction.is_bot = False
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.utm_content = ''
        mock_interaction.utm_term = ''
        mock_interaction.element = ''
        mock_interaction.user_agent = ''
        mock_interaction.ip = None
        mock_interaction.client_hints = {}
        
        hint = infer_web_touchpoint_hint(mock_interaction)
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.code, 'web.page_read')
        self.assertEqual(hint.label, 'Web Page View - Test Website')
        self.assertIsNotNone(hint.metadata)
    
    def test_infer_touchpoint_hint_form_submit(self):
        """Test touchpoint hint inference for form submit."""
        mock_interaction = Mock()
        mock_interaction.payload = {'event_type': 'form_submit', 'form_id': 'contact'}
        mock_interaction.metadata = {'ip_address': '192.168.1.1'}
        mock_interaction.website = self.website
        mock_interaction.session_id = 'test-session'
        mock_interaction.visitor_cookie = 'test-cookie'
        mock_interaction.is_bot = False
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.utm_content = ''
        mock_interaction.utm_term = ''
        mock_interaction.element = ''
        mock_interaction.user_agent = ''
        mock_interaction.ip = None
        mock_interaction.client_hints = {}
        
        hint = infer_web_touchpoint_hint(mock_interaction)
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.code, 'web.form_submit')
        self.assertEqual(hint.label, 'Web Form Submit - Test Website')
        self.assertIsNotNone(hint.metadata)
    
    def test_infer_touchpoint_hint_default(self):
        """Test touchpoint hint inference with default fallback."""
        mock_interaction = Mock()
        mock_interaction.payload = {'event_type': 'unknown_event'}
        mock_interaction.metadata = {'ip_address': '192.168.1.1'}
        mock_interaction.website = self.website
        mock_interaction.session_id = 'test-session'
        mock_interaction.visitor_cookie = 'test-cookie'
        mock_interaction.is_bot = False
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.utm_content = ''
        mock_interaction.utm_term = ''
        mock_interaction.element = ''
        mock_interaction.user_agent = ''
        mock_interaction.ip = None
        mock_interaction.client_hints = {}
        
        hint = infer_web_touchpoint_hint(mock_interaction)
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.code, 'web.unknown_event')
        self.assertEqual(hint.label, 'Web Unknown_Event - Test Website')
