"""
Tests for the three-dimensional classification system in the websites app.

This module tests the new three-dimensional classification system:
- Channel (WHERE): Where the interaction happened
- Medium (HOW): How it communicates  
- TouchpointType (WHAT): What type of touchpoint
"""

from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch

from interactions.models import Channel, Medium, TouchpointType, Touchpoint, Agent, Action, Interaction
from our_institution.models import Division, OurOrganization
from products.models import Product
from websites.models import Website, WebInteraction, WebSurface
from websites.resolvers import WebTouchpointResolver
from websites.mapping_providers import WebMappingProvider
from websites.adapters import infer_web_touchpoint_hint
from connectors.protocols import TouchpointHint


class ThreeDimensionalClassificationTestCase(TestCase):
    """Test case for the three-dimensional classification system."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization and division
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        
        # Create test website
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        
        # Create test product
        self.product = Product.objects.create(
            name="Test Product",
            code="TEST_PRODUCT"
        )
        
        # Create test agent
        self.agent = Agent.objects.create(
            agent_type="browser",
            name="Test Browser",
            identifier="test_browser_123"
        )
        
        # Create test action
        self.action = Action.objects.create(
            name="Page View",
            code="page_view"
        )
        
        # Create test interaction (required for WebInteraction)
        self.interaction = Interaction.objects.create(
            action=self.action,
            agent=self.agent
        )
        
        # Create test channels
        self.web_channel = Channel.objects.create(
            name="Web",
            code="web"
        )
        self.esan_channel = Channel.objects.create(
            name="ESAN University",
            code="esan.edu.pe"
        )
        
        # Create test mediums
        self.organic_medium = Medium.objects.create(
            name="Organic Search",
            code="organic"
        )
        self.social_medium = Medium.objects.create(
            name="Social Media",
            code="social"
        )
        self.email_medium = Medium.objects.create(
            name="Email",
            code="email"
        )
        
        # Create test touchpoint types
        self.web_page_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        self.web_form_type = TouchpointType.objects.create(
            name="Web Form",
            code="web_form"
        )
        self.link_type = TouchpointType.objects.create(
            name="Link",
            code="link"
        )
        self.button_type = TouchpointType.objects.create(
            name="Button",
            code="button"
        )
        
        # Create test web surface
        self.web_surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            title="Test Page",
            touchpoint_class=self.web_page_type
        )
        
        # Create resolver with mapping provider
        self.mapping_provider = WebMappingProvider()
        self.resolver = WebTouchpointResolver(self.mapping_provider)


class ChannelClassificationTestCase(ThreeDimensionalClassificationTestCase):
    """Test cases for Channel (WHERE) classification."""
    
    def test_channel_from_website_url(self):
        """Test channel determination from website URL."""
        
        # Test with website URL in metadata
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'website_url': 'https://esan.edu.pe/contact',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'esan.edu.pe')
    
    def test_channel_from_current_url(self):
        """Test channel determination from current URL."""
        resolver = WebTouchpointResolver()
        
        # Test with current URL in metadata
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'current_url': 'https://alpha.com/products',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'alpha.com')
    
    def test_channel_from_page_url(self):
        """Test channel determination from page URL."""
        resolver = WebTouchpointResolver()
        
        # Test with page URL in metadata
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'page_url': 'https://test.com/about',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'test.com')
    
    def test_channel_default_fallback(self):
        """Test channel default fallback."""
        resolver = WebTouchpointResolver()
        
        # Test with no URL information
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'web')
    
    def test_channel_domain_normalization(self):
        """Test channel domain normalization."""
        resolver = WebTouchpointResolver()
        
        # Test with www prefix
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'website_url': 'https://www.esan.edu.pe/contact',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'esan.edu.pe')


class MediumClassificationTestCase(ThreeDimensionalClassificationTestCase):
    """Test cases for Medium (HOW) classification."""
    
    def test_medium_from_utm_medium(self):
        """Test medium determination from UTM medium."""
        resolver = WebTouchpointResolver()
        
        # Test with UTM medium
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'utm_medium': 'social',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'social')
    
    def test_medium_from_google_referrer(self):
        """Test medium determination from Google referrer."""
        resolver = WebTouchpointResolver()
        
        # Test with Google referrer
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://www.google.com/search?q=test',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'organic')
    
    def test_medium_from_facebook_referrer(self):
        """Test medium determination from Facebook referrer."""
        resolver = WebTouchpointResolver()
        
        # Test with Facebook referrer
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://www.facebook.com/some-post',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'social')
    
    def test_medium_from_email_referrer(self):
        """Test medium determination from email referrer."""
        resolver = WebTouchpointResolver()
        
        # Test with email referrer
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://mail.google.com/mail/u/0/',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'email')
    
    def test_medium_from_other_referrer(self):
        """Test medium determination from other referrer."""
        resolver = WebTouchpointResolver()
        
        # Test with other referrer
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://example.com/some-page',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'referral')
    
    def test_medium_default_fallback(self):
        """Test medium default fallback."""
        resolver = WebTouchpointResolver()
        
        # Test with no referrer or UTM information
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'direct')


class TouchpointTypeClassificationTestCase(ThreeDimensionalClassificationTestCase):
    """Test cases for TouchpointType (WHAT) classification."""
    
    def test_touchpoint_type_page_view(self):
        """Test touchpoint type for page view."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_page')
    
    def test_touchpoint_type_form_submit(self):
        """Test touchpoint type for form submit."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'form_submit'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_form')
    
    def test_touchpoint_type_link_click(self):
        """Test touchpoint type for link click."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'a.cta-link'
            }
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'link')
    
    def test_touchpoint_type_button_click(self):
        """Test touchpoint type for button click."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'button.submit-btn'
            }
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'button')
    
    def test_touchpoint_type_click_default(self):
        """Test touchpoint type for click without selector."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'click'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'link')
    
    def test_touchpoint_type_download(self):
        """Test touchpoint type for download."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'download'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_download')
    
    def test_touchpoint_type_purchase(self):
        """Test touchpoint type for purchase."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'purchase'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_purchase')
    
    def test_touchpoint_type_default_fallback(self):
        """Test touchpoint type default fallback."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'unknown_event'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_page')


class ThreeDimensionalIntegrationTestCase(ThreeDimensionalClassificationTestCase):
    """Test cases for three-dimensional integration."""
    
    def test_complete_touchpoint_creation(self):
        """Test complete touchpoint creation with three dimensions."""
        resolver = WebTouchpointResolver()
        
        hint = TouchpointHint(
            code="test_interaction",
            channel_code="esan.edu.pe",
            medium_code="organic",
            metadata={
                'event_type': 'page_view',
                'website_url': 'https://esan.edu.pe/contact'
            }
        )
        
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify three dimensions
        self.assertEqual(touchpoint.channel.code, 'esan.edu.pe')
        self.assertEqual(touchpoint.medium.code, 'organic')
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
    
    def test_web_interaction_touchpoint_resolution(self):
        """Test touchpoint resolution from WebInteraction."""
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=self.interaction,
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            user_agent="Mozilla/5.0 (Test Browser)",
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        # Test touchpoint hint inference
        hint = infer_web_touchpoint_hint(web_interaction)
        
        # Verify hint properties
        self.assertEqual(hint.medium_code, 'organic')
        self.assertIsNotNone(hint.metadata)
        self.assertIn('event_type', hint.metadata)
    
    def test_three_dimensional_analytics(self):
        """Test three-dimensional analytics capabilities."""
        # Create multiple touchpoints with different dimensions
        touchpoint1 = Touchpoint.objects.create(
            name="ESAN Page View",
            channel=self.esan_channel,
            medium=self.organic_medium,
            touchpoint_type=self.web_page_type
        )
        
        touchpoint2 = Touchpoint.objects.create(
            name="ESAN Form Submit",
            channel=self.esan_channel,
            medium=self.social_medium,
            touchpoint_type=self.web_form_type
        )
        
        touchpoint3 = Touchpoint.objects.create(
            name="ESAN Link Click",
            channel=self.esan_channel,
            medium=self.email_medium,
            touchpoint_type=self.link_type
        )
        
        # Test filtering by channel
        esan_touchpoints = Touchpoint.objects.filter(channel=self.esan_channel)
        self.assertEqual(esan_touchpoints.count(), 3)
        
        # Test filtering by medium
        organic_touchpoints = Touchpoint.objects.filter(medium=self.organic_medium)
        self.assertEqual(organic_touchpoints.count(), 1)
        
        # Test filtering by touchpoint type
        web_page_touchpoints = Touchpoint.objects.filter(touchpoint_type=self.web_page_type)
        self.assertEqual(web_page_touchpoints.count(), 1)
        
        # Test filtering by combination
        esan_organic_touchpoints = Touchpoint.objects.filter(
            channel=self.esan_channel,
            medium=self.organic_medium
        )
        self.assertEqual(esan_organic_touchpoints.count(), 1)
    
    def test_no_overlap_with_action_field(self):
        """Test that TouchpointType doesn't overlap with Action field."""
        # Create touchpoint with web-specific type
        touchpoint = Touchpoint.objects.create(
            name="Test Touchpoint",
            channel=self.web_channel,
            medium=self.organic_medium,
            touchpoint_type=self.web_page_type
        )
        
        # Verify touchpoint type is web-specific
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
        
        # Verify it doesn't conflict with action codes
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'page_view')
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'form_submit')
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'click')
    
    def test_smart_click_classification(self):
        """Test smart click classification (link vs button)."""
        resolver = WebTouchpointResolver()
        
        # Test link click
        link_hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'a.cta-link'
            }
        )
        
        link_type = resolver._get_enhanced_touchpoint_class_code(link_hint)
        self.assertEqual(link_type, 'link')
        
        # Test button click
        button_hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'button.submit-btn'
            }
        )
        
        button_type = resolver._get_enhanced_touchpoint_class_code(button_hint)
        self.assertEqual(button_type, 'button')
    
    def test_medium_priority_logic(self):
        """Test medium determination priority logic."""
        resolver = WebTouchpointResolver()
        
        # Test UTM medium has priority over referrer
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'utm_medium': 'paid',
                'referrer_url': 'https://www.google.com/search'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'paid')  # UTM should win
    
    def test_channel_priority_logic(self):
        """Test channel determination priority logic."""
        resolver = WebTouchpointResolver()
        
        # Test website_url has priority over current_url
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'website_url': 'https://esan.edu.pe/contact',
                'current_url': 'https://alpha.com/products'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'esan.edu.pe')  # website_url should win
