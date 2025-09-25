"""
Tests for the websites app models.

This module tests the core models of the websites app:
- Website
- WebSurface
- WebInteraction
- WebSession
- UrlRoutingRule
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from interactions.models import Channel, Medium, TouchpointType, Touchpoint, Agent, Action
from our_institution.models import Division, OurOrganization
from products.models import Product
from websites.models import Website, WebSurface, WebInteraction, WebSession, UrlRoutingRule


class WebsiteModelTestCase(TestCase):
    """Test cases for the Website model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.channel = Channel.objects.create(
            name="Test Channel",
            code="test_channel"
        )
    
    def test_website_creation(self):
        """Test basic website creation."""
        website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division,
            channel=self.channel
        )
        
        self.assertEqual(website.name, "Test Website")
        self.assertEqual(website.base_url, "https://test.com")
        self.assertEqual(website.division, self.division)
        self.assertEqual(website.channel, self.channel)
        self.assertTrue(website.active)
        self.assertTrue(website.is_active)
    
    def test_website_str_representation(self):
        """Test website string representation."""
        website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        
        expected_str = "Test Website (https://test.com)"
        self.assertEqual(str(website), expected_str)
    
    def test_website_unique_base_url(self):
        """Test that base_url must be unique."""
        Website.objects.create(
            name="Test Website 1",
            base_url="https://test.com",
            division=self.division
        )
        
        with self.assertRaises(IntegrityError):
            Website.objects.create(
                name="Test Website 2",
                base_url="https://test.com",
                division=self.division
            )
    
    def test_website_ordering(self):
        """Test website ordering."""
        website1 = Website.objects.create(
            name="Alpha Website",
            base_url="https://alpha.com",
            division=self.division
        )
        website2 = Website.objects.create(
            name="Beta Website",
            base_url="https://beta.com",
            division=self.division
        )
        
        websites = list(Website.objects.all())
        self.assertEqual(websites[0], website1)
        self.assertEqual(websites[1], website2)


class WebSurfaceModelTestCase(TestCase):
    """Test cases for the WebSurface model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.product = Product.objects.create(
            name="Test Product",
            code="TEST_PRODUCT"
        )
        self.touchpoint_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Test Touchpoint",
            touchpoint_type=self.touchpoint_type
        )
    
    def test_web_surface_creation(self):
        """Test basic web surface creation."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            title="Test Page",
            touchpoint_class=self.touchpoint_type,
            touchpoint=self.touchpoint
        )
        
        self.assertEqual(surface.website, self.website)
        self.assertEqual(surface.path, "/test-page")
        self.assertEqual(surface.title, "Test Page")
        self.assertEqual(surface.touchpoint_class, self.touchpoint_type)
        self.assertEqual(surface.touchpoint, self.touchpoint)
        self.assertTrue(surface.exact_match)
        self.assertFalse(surface.is_form)
        self.assertFalse(surface.is_thankyou)
    
    def test_web_surface_canonical_url(self):
        """Test canonical URL property."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type
        )
        
        expected_url = "https://test.com/test-page"
        self.assertEqual(surface.canonical_url, expected_url)
    
    def test_web_surface_matches_exact(self):
        """Test exact path matching."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type,
            exact_match=True
        )
        
        self.assertTrue(surface.matches("/test-page"))
        self.assertFalse(surface.matches("/test-page/extra"))
        self.assertFalse(surface.matches("/other-page"))
    
    def test_web_surface_matches_prefix(self):
        """Test prefix path matching."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test",
            touchpoint_class=self.touchpoint_type,
            exact_match=False
        )
        
        self.assertTrue(surface.matches("/test"))
        self.assertTrue(surface.matches("/test/page"))
        self.assertTrue(surface.matches("/test/extra/path"))
        self.assertFalse(surface.matches("/other"))
    
    def test_web_surface_matches_regex(self):
        """Test regex path matching."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test",
            touchpoint_class=self.touchpoint_type,
            regex=r"^/test-\d+$"
        )
        
        self.assertTrue(surface.matches("/test-123"))
        self.assertTrue(surface.matches("/test-456"))
        self.assertFalse(surface.matches("/test-abc"))
        self.assertFalse(surface.matches("/test"))
    
    def test_web_surface_str_representation(self):
        """Test web surface string representation."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type
        )
        
        expected_str = "Test Website:/test-page"
        self.assertEqual(str(surface), expected_str)
    
    def test_web_surface_unique_constraint(self):
        """Test web surface unique constraint."""
        WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type,
            is_form=False,
            is_thankyou=False
        )
        
        with self.assertRaises(IntegrityError):
            WebSurface.objects.create(
                website=self.website,
                path="/test-page",
                touchpoint_class=self.touchpoint_type,
                is_form=False,
                is_thankyou=False
            )
    
    def test_web_surface_path_constraint(self):
        """Test web surface path constraint."""
        surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type
        )
        
        # This should not raise an error
        self.assertEqual(surface.path, "/test-page")
        
        # Test invalid path (should be caught by constraint)
        with self.assertRaises(ValidationError):
            surface.path = "invalid-path"  # Should start with /
            surface.full_clean()


class WebInteractionModelTestCase(TestCase):
    """Test cases for the WebInteraction model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.agent = Agent.objects.create(
            agent_type="browser",
            name="Test Browser",
            identifier="test_browser_123"
        )
        self.action = Action.objects.create(
            name="Page View",
            code="page_view"
        )
        self.touchpoint_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        self.touchpoint = Touchpoint.objects.create(
            name="Test Touchpoint",
            touchpoint_type=self.touchpoint_type
        )
    
    def test_web_interaction_creation(self):
        """Test basic web interaction creation."""
        interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            user_agent="Mozilla/5.0 (Test Browser)",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            element="button.submit",
            payload={"event_type": "click"},
            is_bot=False
        )
        
        self.assertEqual(interaction.website, self.website)
        self.assertEqual(interaction.session_id, "test_session_123")
        self.assertEqual(interaction.visitor_cookie, "test_cookie_456")
        self.assertEqual(interaction.user_agent, "Mozilla/5.0 (Test Browser)")
        self.assertEqual(interaction.utm_source, "google")
        self.assertEqual(interaction.utm_medium, "organic")
        self.assertEqual(interaction.utm_campaign, "test_campaign")
        self.assertEqual(interaction.element, "button.submit")
        self.assertEqual(interaction.payload, {"event_type": "click"})
        self.assertFalse(interaction.is_bot)
    
    def test_web_interaction_indexes(self):
        """Test web interaction indexes."""
        # Create multiple interactions to test indexes
        for i in range(5):
            WebInteraction.objects.create(
                website=self.website,
                session_id=f"session_{i}",
                visitor_cookie=f"cookie_{i}",
                utm_source=f"source_{i}",
                utm_medium=f"medium_{i}",
                utm_campaign=f"campaign_{i}"
            )
        
        # Test that we can query by indexed fields efficiently
        interactions = WebInteraction.objects.filter(website=self.website)
        self.assertEqual(interactions.count(), 5)
        
        interactions = WebInteraction.objects.filter(session_id="session_0")
        self.assertEqual(interactions.count(), 1)
        
        interactions = WebInteraction.objects.filter(visitor_cookie="cookie_0")
        self.assertEqual(interactions.count(), 1)
    
    def test_web_interaction_utm_attribution(self):
        """Test UTM attribution fields."""
        interaction = WebInteraction.objects.create(
            website=self.website,
            utm_source="facebook",
            utm_medium="social",
            utm_campaign="summer_sale",
            utm_content="banner_ad",
            utm_term="shoes"
        )
        
        self.assertEqual(interaction.utm_source, "facebook")
        self.assertEqual(interaction.utm_medium, "social")
        self.assertEqual(interaction.utm_campaign, "summer_sale")
        self.assertEqual(interaction.utm_content, "banner_ad")
        self.assertEqual(interaction.utm_term, "shoes")


class WebSessionModelTestCase(TestCase):
    """Test cases for the WebSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.agent = Agent.objects.create(
            agent_type="browser",
            name="Test Browser",
            identifier="test_browser_123"
        )
    
    def test_web_session_creation(self):
        """Test basic web session creation."""
        session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            website=self.website,
            agent=self.agent,
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            referrer_url="https://google.com/search",
            landing_page_url="https://test.com/landing",
            user_agent="Mozilla/5.0 (Test Browser)",
            ip_address="192.168.1.1"
        )
        
        self.assertEqual(session.session_id, "test_session_123")
        self.assertEqual(session.visitor_cookie, "test_cookie_456")
        self.assertEqual(session.website, self.website)
        self.assertEqual(session.agent, self.agent)
        self.assertEqual(session.utm_source, "google")
        self.assertEqual(session.utm_medium, "organic")
        self.assertEqual(session.utm_campaign, "test_campaign")
        self.assertEqual(session.referrer_url, "https://google.com/search")
        self.assertEqual(session.landing_page_url, "https://test.com/landing")
        self.assertEqual(session.user_agent, "Mozilla/5.0 (Test Browser)")
        self.assertEqual(session.ip_address, "192.168.1.1")
        self.assertEqual(session.page_count, 0)
        self.assertTrue(session.is_bounce)
        self.assertEqual(session.conversion_events, [])
    
    def test_web_session_duration(self):
        """Test web session duration property."""
        session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            website=self.website
        )
        
        # Test active session
        self.assertIsNotNone(session.duration)
        
        # Test ended session
        session.end_session()
        self.assertIsNotNone(session.duration)
    
    def test_web_session_is_active(self):
        """Test web session is_active property."""
        session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            website=self.website
        )
        
        # Test active session
        self.assertTrue(session.is_session_active)
        
        # Test ended session
        session.end_session()
        self.assertFalse(session.is_session_active)
    
    def test_web_session_str_representation(self):
        """Test web session string representation."""
        session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            website=self.website
        )
        
        expected_str = "Session test_sess... (Test Website)"
        self.assertEqual(str(session), expected_str)
    
    def test_web_session_unique_session_id(self):
        """Test that session_id must be unique."""
        WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            website=self.website
        )
        
        with self.assertRaises(IntegrityError):
            WebSession.objects.create(
                session_id="test_session_123",
                visitor_cookie="test_cookie_789",
                website=self.website
            )


class UrlRoutingRuleModelTestCase(TestCase):
    """Test cases for the UrlRoutingRule model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.touchpoint_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        self.web_surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            touchpoint_class=self.touchpoint_type
        )
    
    def test_url_routing_rule_creation(self):
        """Test basic URL routing rule creation."""
        rule = UrlRoutingRule.objects.create(
            website=self.website,
            kind=UrlRoutingRule.EXACT,
            pattern="/exact-path",
            surface=self.web_surface,
            priority=100
        )
        
        self.assertEqual(rule.website, self.website)
        self.assertEqual(rule.kind, UrlRoutingRule.EXACT)
        self.assertEqual(rule.pattern, "/exact-path")
        self.assertEqual(rule.surface, self.web_surface)
        self.assertEqual(rule.priority, 100)
        self.assertTrue(rule.active)
    
    def test_url_routing_rule_kinds(self):
        """Test different URL routing rule kinds."""
        # Test EXACT kind
        exact_rule = UrlRoutingRule.objects.create(
            website=self.website,
            kind=UrlRoutingRule.EXACT,
            pattern="/exact",
            surface=self.web_surface
        )
        self.assertEqual(exact_rule.kind, UrlRoutingRule.EXACT)
        
        # Test PREFIX kind
        prefix_rule = UrlRoutingRule.objects.create(
            website=self.website,
            kind=UrlRoutingRule.PREFIX,
            pattern="/prefix",
            surface=self.web_surface
        )
        self.assertEqual(prefix_rule.kind, UrlRoutingRule.PREFIX)
        
        # Test REGEX kind
        regex_rule = UrlRoutingRule.objects.create(
            website=self.website,
            kind=UrlRoutingRule.REGEX,
            pattern=r"^/regex-\d+$",
            surface=self.web_surface
        )
        self.assertEqual(regex_rule.kind, UrlRoutingRule.REGEX)
    
    def test_url_routing_rule_str_representation(self):
        """Test URL routing rule string representation."""
        rule = UrlRoutingRule.objects.create(
            website=self.website,
            kind=UrlRoutingRule.EXACT,
            pattern="/test-pattern",
            surface=self.web_surface
        )
        
        expected_str = "Test Website:exact:/test-pattern -> 1"
        self.assertEqual(str(rule), expected_str)
    
    def test_url_routing_rule_ordering(self):
        """Test URL routing rule ordering."""
        rule1 = UrlRoutingRule.objects.create(
            website=self.website,
            pattern="/pattern1",
            surface=self.web_surface,
            priority=200
        )
        rule2 = UrlRoutingRule.objects.create(
            website=self.website,
            pattern="/pattern2",
            surface=self.web_surface,
            priority=100
        )
        
        rules = list(UrlRoutingRule.objects.all())
        self.assertEqual(rules[0], rule2)  # Lower priority first
        self.assertEqual(rules[1], rule1)
    
    def test_url_routing_rule_unique_constraint(self):
        """Test URL routing rule unique constraint."""
        UrlRoutingRule.objects.create(
            website=self.website,
            pattern="/test-pattern",
            surface=self.web_surface
        )
        
        with self.assertRaises(IntegrityError):
            UrlRoutingRule.objects.create(
                website=self.website,
                pattern="/test-pattern",
                surface=self.web_surface
            )
