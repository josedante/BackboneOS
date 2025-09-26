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


class GoogleSearchScenarioTestCase(TestCase):
    """Test case for the Google search scenario from the examples."""
    
    def setUp(self):
        """Set up test data for Google search scenario."""
        # Create test organization and division
        self.organization = OurOrganization.objects.create(
            name="ESAN University"
        )
        self.division = Division.objects.create(
            name="Academic Division",
            code="ACADEMIC",
            organization=self.organization
        )
        
        # Create test website
        self.website = Website.objects.create(
            name="ESAN University Website",
            base_url="https://esan.edu.pe",
            division=self.division
        )
        
        # Create test product
        self.product = Product.objects.create(
            name="MBA Program",
            code="MBA_PROGRAM"
        )
        
        # Create test agent and action
        self.agent = Agent.objects.create(
            agent_type="browser",
            name="Test User",
            identifier="test_user_123"
        )
        self.action = Action.objects.create(
            code="no_action",
            name="Sin Acción",
            description="Evento inferido o acción realizada hacia el usuario"
        )
        self.interaction = Interaction.objects.create(
            action=self.action,
            agent=self.agent
        )
        
        # Create mapping provider and resolver
        self.mapping_provider = WebMappingProvider()
        self.resolver = WebTouchpointResolver(self.mapping_provider)
    
    def test_google_search_page_view_scenario(self):
        """Test the Google search page view scenario from the examples."""
        
        # Create WebInteraction for the scenario
        # Note: For organic Google search, UTM parameters would typically be empty
        web_interaction = WebInteraction.objects.create(
            interaction=self.interaction,
            website=self.website,
            session_id="sess_abc123",
            visitor_cookie="visitor_xyz789",
            user_agent="Mozilla/5.0...",
            utm_source="",  # Empty for organic search
            utm_medium="",  # Empty for organic search
            utm_campaign="",  # Empty for organic search
            payload={
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "page_category": "academic_programs"
            }
        )
        
        # Test Page View Interaction
        print("\n=== Testing Page View Interaction ===")
        
        # Create hint for page view
        page_view_hint = TouchpointHint(
            code="web_page.mba_programs_esan_university",
            metadata={
                "website_url": "https://esan.edu.pe/programs/mba",
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "event_type": "page_view"
            }
        )
        
        # Test channel determination
        channel_code = self.resolver._determine_channel_from_subject(page_view_hint)
        print(f"Page View Channel: {channel_code}")
        self.assertEqual(channel_code, "esan.edu.pe")
        
        # Test medium determination
        medium_code = self.resolver._determine_medium_from_subject(page_view_hint)
        print(f"Page View Medium: {medium_code}")
        self.assertEqual(medium_code, "owned_website")
        
        # Test touchpoint type determination
        touchpoint_type_code = self.resolver._get_enhanced_touchpoint_class_code(page_view_hint)
        print(f"Page View TouchpointType: {touchpoint_type_code}")
        self.assertEqual(touchpoint_type_code, "web_page")
        
        # Test referrer click interaction
        print("\n=== Testing Referrer Click Interaction ===")
        
        referrer_hint = TouchpointHint(
            code="web.referrer_page.google_search",
            metadata={
                "referrer_url": "https://google.com/search?q=mba+programs+peru",
                "event_type": "referrer_click"
            }
        )
        
        # Test channel determination for referrer
        referrer_channel = self.resolver._determine_channel_from_subject(referrer_hint)
        print(f"Referrer Channel: {referrer_channel}")
        self.assertEqual(referrer_channel, "google.com")
        
        # Test medium determination for referrer
        referrer_medium = self.resolver._determine_medium_from_subject(referrer_hint)
        print(f"Referrer Medium: {referrer_medium}")
        self.assertEqual(referrer_medium, "organic_search")
        
        # Test touchpoint type for referrer
        referrer_touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(referrer_hint)
        print(f"Referrer TouchpointType: {referrer_touchpoint_type}")
        self.assertEqual(referrer_touchpoint_type, "search_results")
        
        print("\n=== Expected Results ===")
        print("1. Page View Interaction:")
        print("   - Channel: esan.edu.pe")
        print("   - Medium: owned_website")
        print("   - TouchpointType: web_page")
        print("2. Referrer Click Interaction:")
        print("   - Channel: google")
        print("   - Medium: organic_search")
        print("   - TouchpointType: search_results")
        print("3. Session Start Interaction:")
        print("   - Channel: esan.edu.pe")
        print("   - Medium: owned_website")
        print("   - TouchpointType: web_page")
    
    def test_utm_precedence_scenario(self):
        """Test that UTM parameters take precedence over referrer analysis."""
        
        # Create WebInteraction with UTM parameters (paid campaign scenario)
        web_interaction = WebInteraction.objects.create(
            interaction=self.interaction,
            website=self.website,
            session_id="sess_utm123",
            visitor_cookie="visitor_utm789",
            user_agent="Mozilla/5.0...",
            utm_source="google",  # UTM parameters present
            utm_medium="cpc",     # Cost per click (paid)
            utm_campaign="mba_paid_search",
            payload={
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "page_category": "academic_programs"
            }
        )
        
        # Test Page View Interaction with UTM precedence
        print("\n=== Testing UTM Precedence Scenario ===")
        
        # Create hint for page view with UTM parameters
        page_view_hint = TouchpointHint(
            code="web_page.mba_programs_esan_university",
            metadata={
                "website_url": "https://esan.edu.pe/programs/mba",
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "event_type": "page_view",
                "utm_source": "google",  # UTM source should take precedence for channel
                "utm_medium": "cpc"      # UTM medium should take precedence for medium
            }
        )
        
        # Test channel determination (should use UTM source, not website URL)
        channel_code = self.resolver._determine_channel_from_subject(page_view_hint)
        print(f"Page View Channel (with UTM): {channel_code}")
        self.assertEqual(channel_code, "google")  # UTM source for paid traffic
        
        # Test medium determination (should use UTM, not owned_website)
        medium_code = self.resolver._determine_medium_from_subject(page_view_hint)
        print(f"Page View Medium (with UTM): {medium_code}")
        self.assertEqual(medium_code, "cpc")  # UTM should take precedence
        
        # Test referrer click with UTM precedence
        print("\n=== Testing Referrer Click with UTM Precedence ===")
        
        referrer_hint = TouchpointHint(
            code="web.referrer_page.google_search",
            metadata={
                "referrer_url": "https://google.com/search?q=mba+programs+peru",
                "event_type": "referrer_click",
                "utm_source": "google",  # UTM source should take precedence for channel
                "utm_medium": "cpc"      # UTM medium should take precedence for medium
            }
        )
        
        # Test channel determination for referrer (should use UTM source, not referrer URL)
        referrer_channel = self.resolver._determine_channel_from_subject(referrer_hint)
        print(f"Referrer Channel (with UTM): {referrer_channel}")
        self.assertEqual(referrer_channel, "google")  # UTM source for paid traffic
        
        # Test medium determination for referrer (should use UTM)
        referrer_medium = self.resolver._determine_medium_from_subject(referrer_hint)
        print(f"Referrer Medium (with UTM): {referrer_medium}")
        self.assertEqual(referrer_medium, "cpc")  # UTM should take precedence
        
        print("\n=== Expected Results (UTM Precedence) ===")
        print("1. Page View Interaction:")
        print("   - Channel: google (UTM source for paid traffic)")
        print("   - Medium: cpc (UTM medium takes precedence)")
        print("   - TouchpointType: web_page")
        print("2. Referrer Click Interaction:")
        print("   - Channel: google (UTM source for paid traffic)")
        print("   - Medium: cpc (UTM medium takes precedence)")
        print("   - TouchpointType: search_results")
