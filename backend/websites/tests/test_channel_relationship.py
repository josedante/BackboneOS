"""
Channel Relationship Tests for Websites App

This module contains comprehensive tests to verify the channel relationship functionality
in the websites app after the migration from direct interaction access to mediated
touchpoint access.

The tests verify that:
1. Channel access works correctly through the touchpoint relationship
2. Automatic touchpoint resolution creates touchpoints with proper channels
3. Website-specific channel code generation works correctly
4. UTM, referrer, and user agent analysis determine channels correctly
5. The AbstractConnectorInteraction.channel property works as expected
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone

from entities.models import Organization
from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction, Action, Channel, Medium
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage
from websites.resolvers import WebTouchpointResolver, CachedWebTouchpointResolver
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider
from websites.adapters import infer_web_touchpoint_hint

User = get_user_model()


class ChannelRelationshipTest(TestCase):
    """Test cases for channel relationship functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create organization
        self.our_organization = OurOrganization.objects.create(
            name='Test Organization',
            legal_name='Test Organization Legal',
            is_active=True
        )
        
        # Create division
        self.division = Division.objects.create(
            organization=self.our_organization,
            name='Test Division',
            code='TEST',
            description='Test division for testing'
        )
        
        # Create website
        self.website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com',
        )
        
        # Create medium and channel
        self.medium = Medium.objects.create(
            name='Digital',
            code='DIGITAL',
            description='Digital medium'
        )
        
        self.channel = Channel.objects.create(
            name='Example Website',
            code='example.com',
            description='Test website channel',
            medium=self.medium
        )
        
        # Create touchpoint class
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page',
            name='Web Page',
            description='A web page touchpoint'
        )
        
        # Create touchpoint with channel
        self.touchpoint = Touchpoint.objects.create(
            code='web.test',
            name='Test Touchpoint',
            touchpoint_class=self.touchpoint_class,
            channel=self.channel  # Channel is now on touchpoint, not interaction
        )
        
        # Create action
        self.action = Action.objects.create(
            code='web.page_view',
            name='Page View',
            description='Page view action'
        )
    
    def test_channel_access_through_touchpoint(self):
        """Test that channel is accessed through touchpoint relationship."""
        # Create interaction with touchpoint
        interaction = Interaction.objects.create(
            action=self.action,
            touchpoint=self.touchpoint,
            person=None
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        # Test channel access through touchpoint
        self.assertEqual(web_interaction.touchpoint, self.touchpoint)
        self.assertEqual(web_interaction.touchpoint.channel, self.channel)
        self.assertEqual(web_interaction.touchpoint.channel.code, 'example.com')
        self.assertEqual(web_interaction.touchpoint.channel.name, 'Example Website')
        
        # Test AbstractConnectorInteraction.channel property
        channel_via_property = web_interaction.channel
        self.assertEqual(channel_via_property, self.channel)
    
    def test_website_channel_code_generation(self):
        """Test website-specific channel code generation."""
        # Create resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Test website channel code extraction
        mock_interaction = Mock()
        mock_interaction.website = self.website
        
        channel_code = resolver._get_website_channel_code(mock_interaction)
        self.assertEqual(channel_code, 'example.com')
    
    def test_channel_display_name_generation(self):
        """Test channel display name generation."""
        # Create resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Test various channel display names
        test_cases = [
            ('example.com', 'Example Website'),
            ('google.com', 'Google Website'),
            ('facebook.com', 'Facebook Website'),
            ('unknown-source', 'Unknown-Source'),
        ]
        
        for channel_code, expected_name in test_cases:
            name = resolver._get_channel_display_name(channel_code)
            self.assertEqual(name, expected_name)
    
    def test_utm_analysis_for_channel(self):
        """Test UTM parameter analysis for channel determination."""
        # Create resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Create mock interaction with UTM parameters
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = 'email'
        mock_interaction.utm_source = 'newsletter'
        mock_interaction.utm_campaign = 'test-campaign'
        mock_interaction.utm_content = 'header'
        mock_interaction.utm_term = 'test'
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        mock_interaction.referrer_url = ''
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        # Test hint enhancement
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'email')
        self.assertEqual(enhanced_hint.channel_code, 'email')
    
    def test_referrer_analysis_for_channel(self):
        """Test referrer analysis for channel determination."""
        # Create resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Create mock interaction with referrer but no UTM
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        mock_interaction.referrer_url = 'https://www.facebook.com/some-post'
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        # Test hint enhancement
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'social')
        self.assertEqual(enhanced_hint.channel_code, 'facebook')
    
    def test_user_agent_analysis_for_app_channel(self):
        """Test user agent analysis for native app channel detection."""
        # Create resolver
        mapping_provider = WebMappingProvider()
        resolver = WebTouchpointResolver(mapping_provider)
        
        # Test native app user agent
        app_user_agent = 'SubstackApp/1.0 (iPhone; iOS 15.0)'
        app_channel = resolver._extract_app_channel_from_user_agent(app_user_agent)
        self.assertEqual(app_channel, 'substack')
        
        # Test regular browser user agent
        browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        app_channel = resolver._extract_app_channel_from_user_agent(browser_user_agent)
        self.assertIsNone(app_channel)
    
    def test_automatic_touchpoint_resolution(self):
        """Test automatic touchpoint resolution with channel assignment."""
        # Create interaction without touchpoint initially
        interaction = Interaction.objects.create(
            action=self.action,
            touchpoint=None,  # No touchpoint initially
            person=None
        )
        
        # Create WebInteraction without touchpoint
        web_interaction = WebInteraction(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        # Mock the resolver to avoid complex setup
        with patch('websites.resolvers.WebTouchpointResolver') as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            
            # Mock the touchpoint creation - use existing touchpoint
            mock_resolver.resolve.return_value = self.touchpoint
            
            # Save the interaction (this should trigger touchpoint resolution)
            web_interaction.save()
            
            # Verify resolver was called
            mock_resolver.resolve.assert_called_once()
            
            # Verify touchpoint was assigned
            interaction.refresh_from_db()
            self.assertEqual(interaction.touchpoint, self.touchpoint)
            
            # Verify channel is accessible through touchpoint
            self.assertEqual(interaction.touchpoint.channel, self.channel)
    
    def test_complete_integration_flow(self):
        """Test complete integration flow from WebInteraction to touchpoint with channel."""
        # Create interaction
        interaction = Interaction.objects.create(
            action=self.action,
            touchpoint=self.touchpoint,
            person=None
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            utm_medium='organic',
            utm_source='google',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        # Test touchpoint hint inference
        hint = web_interaction.infer_touchpoint_hint()
        self.assertEqual(hint.code, 'web.page_read')
        
        # Test channel access through various methods
        self.assertEqual(web_interaction.touchpoint.channel, self.channel)
        self.assertEqual(web_interaction.channel, self.channel)
        self.assertEqual(web_interaction.channel.code, 'example.com')
        self.assertEqual(web_interaction.channel.name, 'Example Website')
    
    def test_cached_resolver_functionality(self):
        """Test cached resolver functionality."""
        # Create cached resolver
        mapping_provider = CachedWebMappingProvider()
        cached_resolver = CachedWebTouchpointResolver(mapping_provider)
        
        # Create mock interaction
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        mock_interaction.referrer_url = ''
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        # Test hint enhancement with cached resolver
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = cached_resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'direct')
        self.assertEqual(enhanced_hint.channel_code, 'example.com')  # Website-specific channel
    
    def test_channel_property_backward_compatibility(self):
        """Test that the channel property maintains backward compatibility."""
        # Create interaction with touchpoint
        interaction = Interaction.objects.create(
            action=self.action,
            touchpoint=self.touchpoint,
            person=None
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        # Test that both access methods work
        direct_channel = web_interaction.touchpoint.channel
        property_channel = web_interaction.channel
        
        self.assertEqual(direct_channel, property_channel)
        self.assertEqual(direct_channel.code, 'example.com')
        self.assertEqual(property_channel.code, 'example.com')
    
    def test_channel_none_handling(self):
        """Test handling when touchpoint has no channel."""
        # Create touchpoint without channel
        touchpoint_no_channel = Touchpoint.objects.create(
            code='web.no_channel',
            name='No Channel Touchpoint',
            touchpoint_class=self.touchpoint_class,
            channel=None  # No channel
        )
        
        # Create interaction with touchpoint without channel
        interaction = Interaction.objects.create(
            action=self.action,
            touchpoint=touchpoint_no_channel,
            person=None
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        # Test that channel property returns None gracefully
        self.assertIsNone(web_interaction.channel)
        self.assertIsNone(web_interaction.touchpoint.channel)
