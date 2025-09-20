"""
Resolver tests for the websites app.

This module tests the WebTouchpointResolver and CachedWebTouchpointResolver classes.
"""

from django.test import TestCase
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model

from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage
from websites.resolvers import WebTouchpointResolver, CachedWebTouchpointResolver
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider

User = get_user_model()


class WebTouchpointResolverTest(TestCase):
    """Test cases for the WebTouchpointResolver."""
    
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
        
        # Create mapping provider
        self.mapping_provider = WebMappingProvider()
        self.resolver = WebTouchpointResolver(self.mapping_provider)
    
    def test_ensure_required_fields_utm_priority(self):
        """Test that UTM parameters take priority in medium detection."""
        # Create mock interaction with UTM parameters
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = 'email'
        mock_interaction.utm_source = 'newsletter'
        mock_interaction.utm_campaign = 'welcome'
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        mock_interaction.referrer_url = 'https://www.google.com'
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = self.resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'email')
        self.assertEqual(enhanced_hint.channel_code, 'email')
    
    def test_ensure_required_fields_referrer_analysis(self):
        """Test referrer analysis when no UTM parameters."""
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
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = self.resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'social')
        self.assertEqual(enhanced_hint.channel_code, 'facebook')
    
    def test_ensure_required_fields_user_agent_analysis(self):
        """Test user agent analysis for native app detection."""
        # Create mock interaction with app user agent
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.user_agent = 'SubstackApp/1.0 (iPhone; iOS 15.0)'
        mock_interaction.referrer_url = None
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = self.resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'mobile')
        self.assertEqual(enhanced_hint.channel_code, 'substack')
    
    def test_ensure_required_fields_direct_fallback(self):
        """Test direct traffic fallback when no other indicators."""
        # Create mock interaction with no external indicators
        mock_interaction = Mock()
        mock_interaction.website = self.website
        mock_interaction.utm_medium = ''
        mock_interaction.utm_source = ''
        mock_interaction.utm_campaign = ''
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        mock_interaction.referrer_url = None
        mock_interaction.session_id = 'test-session'
        mock_interaction.payload = {}
        mock_interaction.metadata = {}
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        enhanced_hint = self.resolver._ensure_required_fields(mock_interaction, hint)
        
        self.assertEqual(enhanced_hint.medium_code, 'direct')
        self.assertEqual(enhanced_hint.channel_code, 'example.com')
    
    def test_get_website_channel_code(self):
        """Test website channel code extraction."""
        mock_interaction = Mock()
        mock_interaction.website = self.website
        
        channel_code = self.resolver._get_website_channel_code(mock_interaction)
        self.assertEqual(channel_code, 'example.com')
    
    def test_extract_domain_from_url(self):
        """Test domain extraction from URL."""
        # Test normal URL
        domain = self.resolver._extract_domain_from_url('https://www.example.com/path')
        self.assertEqual(domain, 'example.com')
        
        # Test URL with www
        domain = self.resolver._extract_domain_from_url('https://www.test.com')
        self.assertEqual(domain, 'test.com')
        
        # Test localhost
        domain = self.resolver._extract_domain_from_url('http://localhost:8000')
        self.assertEqual(domain, 'localhost:8000')
        
        # Test invalid URL
        domain = self.resolver._extract_domain_from_url('invalid-url')
        self.assertEqual(domain, 'web')
    
    def test_get_channel_display_name(self):
        """Test channel display name generation."""
        # Test website domain
        name = self.resolver._get_channel_display_name('example.com')
        self.assertEqual(name, 'Example Website')
        
        # Test known source
        name = self.resolver._get_channel_display_name('google')
        self.assertEqual(name, 'Google')
        
        # Test unknown source
        name = self.resolver._get_channel_display_name('unknown-source')
        self.assertEqual(name, 'Unknown-Source')
    
    def test_analyze_user_agent(self):
        """Test user agent analysis for native app detection."""
        # Test native app user agent
        app_channel = self.resolver._extract_app_channel_from_user_agent('SubstackApp/1.0 (iPhone; iOS 15.0)')
        self.assertEqual(app_channel, 'substack')
        
        # Test regular browser user agent
        app_channel = self.resolver._extract_app_channel_from_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        self.assertIsNone(app_channel)
        
        # Test WebView user agent
        app_channel = self.resolver._extract_app_channel_from_user_agent('Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148')
        self.assertIsNone(app_channel)  # Should not detect as app
    
    def test_is_external_click_event(self):
        """Test external click event detection."""
        # Test internal click event
        mock_interaction = Mock()
        mock_interaction.payload = {'event_type': 'internal_click'}
        mock_interaction.metadata = {}
        mock_interaction.referrer_url = None
        mock_interaction.utm_source = ''
        mock_interaction.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        
        is_external = self.resolver._is_external_click_event(mock_interaction)
        self.assertFalse(is_external)
        
        # Test external page_view with referrer
        mock_interaction.payload = {'event_type': 'page_view'}
        mock_interaction.referrer_url = 'https://www.google.com'
        
        with patch.object(self.resolver, '_is_external_referrer', return_value=True):
            is_external = self.resolver._is_external_click_event(mock_interaction)
            self.assertTrue(is_external)
    
    def test_get_enhanced_touchpoint_class_code(self):
        """Test enhanced touchpoint class code generation."""
        # Test click event (should be traffic)
        hint = TouchpointHint(
            code='web.internal_click',
            label='Internal Click',
            medium_code='direct'
        )
        touchpoint_class = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_class, 'web.internal_traffic')
        
        # Test non-click event (should be interaction)
        hint = TouchpointHint(
            code='web.form_submit',
            label='Form Submit',
            medium_code='direct'
        )
        with patch.object(self.resolver, '_is_internal_website_interaction', return_value=True):
            touchpoint_class = self.resolver._get_enhanced_touchpoint_class_code(hint)
            self.assertEqual(touchpoint_class, 'web.internal_interaction')
        
        # Test external traffic
        hint = TouchpointHint(
            code='web.page_view',
            label='Page View',
            medium_code='social'
        )
        touchpoint_class = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_class, 'web.social_traffic')
    
    def test_get_enhanced_touchpoint_class_name(self):
        """Test enhanced touchpoint class name generation."""
        name = self.resolver._get_enhanced_touchpoint_class_name('web.internal_traffic')
        self.assertEqual(name, 'Internal Website Traffic')
        
        name = self.resolver._get_enhanced_touchpoint_class_name('web.social_traffic')
        self.assertEqual(name, 'Social Media Traffic')
        
        name = self.resolver._get_enhanced_touchpoint_class_name('web.unknown_traffic')
        self.assertEqual(name, 'Unknown Traffic Source')
