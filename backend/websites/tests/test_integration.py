"""
Integration tests for the websites app.

This module contains integration tests that verify the complete flow
from WebInteraction creation to touchpoint resolution.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from entities.models import Organization
from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction, Action, Channel, Medium
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage
from websites.resolvers import WebTouchpointResolver, CachedWebTouchpointResolver
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider
from websites.adapters import infer_web_touchpoint_hint

User = get_user_model()


class IntegrationTest(TestCase):
    """Integration tests for the complete touchpoint resolution flow."""
    
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
            base_url='https://www.example.com',
        )
    
    def test_complete_touchpoint_resolution_flow(self):
        """Test the complete flow from WebInteraction creation to touchpoint resolution."""
        # Create mapping provider and resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Create the required Interaction first
        from interactions.models import Interaction, Action
        action = Action.objects.create(code='web.page_view', name='Page View')
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=None,
            person=None,
            referrer_url='https://www.google.com/search?q=test',
            payload={'ip_address': '192.168.1.1'}
        )
        
        # Create a web interaction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view', 'page': '/test'},
            ip='192.168.1.1'
        )
        
        # Test touchpoint hint inference
        hint = web_interaction.infer_touchpoint_hint()
        self.assertEqual(hint.code, 'web.page_view')
        
        # Test enhanced hint generation
        enhanced_hint = resolver._ensure_required_fields(web_interaction, hint)
        self.assertEqual(enhanced_hint.medium_code, 'web_direct')
        self.assertEqual(enhanced_hint.channel_code, 'example.com')  # Website-specific channel
        
        # Test touchpoint class generation
        touchpoint_class_code = resolver._get_enhanced_touchpoint_class_code(enhanced_hint)
        self.assertEqual(touchpoint_class_code, 'web.internal_interaction')
        
        # Test touchpoint class name
        touchpoint_class_name = resolver._get_enhanced_touchpoint_class_name(touchpoint_class_code)
        self.assertEqual(touchpoint_class_name, 'Internal Website Interaction')
    
    def test_cached_resolver_integration(self):
        """Test integration with cached resolver."""
        # Create cached resolver
        mapping_provider = CachedWebMappingProvider()
        cached_resolver = CachedWebTouchpointResolver(mapping_provider)
        
        # Create the required Interaction first
        from interactions.models import Interaction, Action
        action = Action.objects.create(code='web.internal_click', name='Internal Click')
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=None,
            person=None
        )
        
        # Create a web interaction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'internal_click'}
        )
        
        # Test that cached resolver works the same as regular resolver
        hint = web_interaction.infer_touchpoint_hint()
        enhanced_hint = cached_resolver._ensure_required_fields(web_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'web_direct')
        self.assertEqual(enhanced_hint.channel_code, 'example.com')  # Website-specific channel
        
        # Test touchpoint class for internal click
        touchpoint_class_code = cached_resolver._get_enhanced_touchpoint_class_code(enhanced_hint)
        self.assertEqual(touchpoint_class_code, 'web.internal_traffic')
