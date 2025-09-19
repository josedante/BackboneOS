"""
Comprehensive test suite for the websites app.

This module tests all key components of the websites app including:
- Models (Website, WebSurface, WebInteraction)
- Resolvers (WebTouchpointResolver, CachedWebTouchpointResolver)
- Mapping Providers (WebMappingProvider, CachedWebMappingProvider)
- Adapters (WebTouchpointAdapter)
- Integration with the touchpoint resolution system
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone

from entities.models import Organization
from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage
from websites.resolvers import WebTouchpointResolver, CachedWebTouchpointResolver
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider
from websites.adapters import infer_web_touchpoint_hint


User = get_user_model()


class WebsiteModelTest(TestCase):
    """Test cases for the Website model."""
    
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
    
    def test_website_creation(self):
        """Test creating a website."""
        website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com'
        )
        
        self.assertEqual(website.name, 'Test Website')
        self.assertEqual(website.base_url, 'https://www.example.com')
        self.assertEqual(website.division, self.division)
        self.assertTrue(website.is_active)
    
    def test_website_str_representation(self):
        """Test string representation of website."""
        website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com'
        )
        
        self.assertEqual(str(website), 'Test Website (https://www.example.com)')
    
    def test_website_ordering(self):
        """Test website ordering by name."""
        website1 = Website.objects.create(
            division=self.division,
            name='Zebra Website',
            base_url='https://www.zebra.com'
        )
        website2 = Website.objects.create(
            division=self.division,
            name='Alpha Website',
            base_url='https://www.alpha.com'
        )
        
        websites = list(Website.objects.all())
        self.assertEqual(websites[0], website2)  # Alpha should come first
        self.assertEqual(websites[1], website1)  # Zebra should come second


class WebSurfaceModelTest(TestCase):
    """Test cases for the WebSurface model."""
    
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
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page',
            name='Web Page',
            description='A web page touchpoint'
        )
    
    def test_websurface_creation(self):
        """Test creating a web surface."""
        surface = WebSurface.objects.create(
            website=self.website,
            path='/test-page',
            title='Test Page',
            touchpoint_class=self.touchpoint_class
        )
        
        self.assertEqual(surface.website, self.website)
        self.assertEqual(surface.path, '/test-page')
        self.assertEqual(surface.title, 'Test Page')
        self.assertEqual(surface.touchpoint_class, self.touchpoint_class)
        self.assertFalse(surface.is_form)
        self.assertFalse(surface.is_thankyou)
    
    def test_websurface_path_validation(self):
        """Test path validation for web surface."""
        # Valid path
        surface = WebSurface.objects.create(
            website=self.website,
            path='/valid-path',
            title='Valid Page',
            touchpoint_class=self.touchpoint_class
        )
        self.assertEqual(surface.path, '/valid-path')
        
        # Invalid path (doesn't start with /)
        with self.assertRaises(ValidationError):
            surface = WebSurface(
                website=self.website,
                path='invalid-path',  # Missing leading slash
                title='Invalid Page',
                touchpoint_class=self.touchpoint_class
            )
            surface.full_clean()
    
    def test_websurface_proxy_models(self):
        """Test WebForm and WebPage proxy models."""
        # Create a form surface
        form_surface = WebSurface.objects.create(
            website=self.website,
            path='/contact-form',
            title='Contact Form',
            touchpoint_class=self.touchpoint_class,
            is_form=True
        )
        
        # Create a page surface
        page_surface = WebSurface.objects.create(
            website=self.website,
            path='/about',
            title='About Page',
            touchpoint_class=self.touchpoint_class
        )
        
        # Test WebForm proxy model
        web_form = WebForm.objects.get(id=form_surface.id)
        self.assertTrue(web_form.is_form)
        self.assertIsInstance(web_form, WebForm)
        
        # Test WebPage proxy model
        web_page = WebPage.objects.get(id=page_surface.id)
        self.assertFalse(web_page.is_form)
        self.assertIsInstance(web_page, WebPage)


class WebInteractionModelTest(TestCase):
    """Test cases for the WebInteraction model."""
    
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
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page',
            name='Web Page',
            description='A web page touchpoint'
        )
        self.touchpoint = Touchpoint.objects.create(
            code='web.test',
            name='Test Touchpoint',
            touchpoint_class=self.touchpoint_class
        )
    
    def test_webinteraction_creation(self):
        """Test creating a web interaction."""
        # Create the required Interaction first
        from interactions.models import Interaction, Action
        action = Action.objects.create(code='web.page_view', name='Page View')
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=self.touchpoint,
            person=None  # Optional
        )
        
        # Create the WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            utm_medium='organic',
            utm_source='google',
            utm_campaign='test-campaign',
            session_id='test-session-123',
            payload={'event_type': 'page_view', 'page': '/test'},
            ip='192.168.1.1'
        )
        
        self.assertEqual(web_interaction.website, self.website)
        self.assertEqual(web_interaction.user_agent, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        self.assertEqual(web_interaction.utm_medium, 'organic')
        self.assertEqual(web_interaction.utm_source, 'google')
        self.assertEqual(web_interaction.utm_campaign, 'test-campaign')
        self.assertEqual(web_interaction.session_id, 'test-session-123')
        self.assertEqual(web_interaction.payload, {'event_type': 'page_view', 'page': '/test'})
        self.assertEqual(web_interaction.ip, '192.168.1.1')
        self.assertEqual(web_interaction.touchpoint, self.touchpoint)
    
    def test_webinteraction_infer_touchpoint_hint(self):
        """Test touchpoint hint inference."""
        # Create the required Interaction first
        from interactions.models import Interaction, Action
        action = Action.objects.create(code='web.page_view', name='Page View')
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=self.touchpoint,
            person=None  # Optional
        )
        
        # Create the WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='test-session-123',
            payload={'event_type': 'page_view'}
        )
        
        hint = web_interaction.infer_touchpoint_hint()
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.code, 'web.page_read')
        self.assertEqual(hint.label, 'Web Page View - Test Website')
        self.assertIsNotNone(hint.metadata)
    
    def test_webinteraction_auto_touchpoint_creation(self):
        """Test automatic touchpoint creation on save."""
        # Create the required Interaction first
        from interactions.models import Interaction, Action
        action = Action.objects.create(code='web.page_view', name='Page View')
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=None,  # No touchpoint initially
            person=None  # Optional
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
            
            # Save the interaction
            web_interaction.save()
            
            # Verify resolver was called
            mock_resolver.resolve.assert_called_once()


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


class WebMappingProviderTest(TestCase):
    """Test cases for the WebMappingProvider."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = WebMappingProvider()
    
    def test_lookup_mapping(self):
        """Test mapping rule lookup."""
        # Create a mock subject and hint
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        
        # Test lookup (should return None since no rules exist)
        rule = self.provider.lookup_mapping(mock_subject, hint)
        self.assertIsNone(rule)  # No rules in test database
    
    def test_get_connector_type(self):
        """Test connector type extraction."""
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        connector_type = self.provider._get_connector_type(mock_subject)
        self.assertEqual(connector_type, 'web')
    
    def test_get_source_identifier(self):
        """Test source identifier extraction."""
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        source_id = self.provider._get_source_identifier(mock_subject)
        self.assertEqual(source_id, 'https://www.example.com')


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
        self.assertEqual(hint.code, 'web.page_read')
        
        # Test enhanced hint generation
        enhanced_hint = resolver._ensure_required_fields(web_interaction, hint)
        self.assertEqual(enhanced_hint.medium_code, 'direct')
        self.assertEqual(enhanced_hint.channel_code, 'web')
        
        # Test touchpoint class generation
        touchpoint_class_code = resolver._get_enhanced_touchpoint_class_code(enhanced_hint)
        self.assertEqual(touchpoint_class_code, 'web.direct_traffic')
        
        # Test touchpoint class name
        touchpoint_class_name = resolver._get_enhanced_touchpoint_class_name(touchpoint_class_code)
        self.assertEqual(touchpoint_class_name, 'Direct Traffic')
    
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
        
        self.assertEqual(enhanced_hint.medium_code, 'direct')
        self.assertEqual(enhanced_hint.channel_code, 'web')
        
        # Test touchpoint class for internal click
        touchpoint_class_code = cached_resolver._get_enhanced_touchpoint_class_code(enhanced_hint)
        self.assertEqual(touchpoint_class_code, 'web.internal_traffic')