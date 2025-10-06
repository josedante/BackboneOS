"""
Tests for the websites app models.

This module tests the multi-interaction approach for page view events,
including the creation of page view, referrer click, and session start interactions.
"""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json

from websites.models import WebInteraction, Website, WebSession, WebAgent
from interactions.models import Interaction, Action, Agent, Touchpoint
from our_institution.models import Division, OurOrganization


class WebInteractionTestCase(TestCase):
    """Test cases for WebInteraction model and multi-interaction approach."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization first
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            is_active=True
        )
        
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
            organization=self.organization,
            is_active=True
        )
        
        # Create test website
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.example.com",
            division=self.division,
            is_active=True
        )
        
        # Sample event data
        self.sample_event_data = {
            "event_type": "page_view",
            "website_base": "https://test.example.com",
            "full_url": "https://test.example.com/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_test123",
            "visitor_cookie": "visitor_test456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "utm_campaign": "mba_search",
            "utm_content": "programs_page",
            "utm_term": "mba programs",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - Test University",
                "page_description": "Comprehensive MBA programs...",
                "page_category": "academic_programs",
                "load_time": 1.2,
                "is_landing_page": False,
                "page_depth": 2,
                "referrer_title": "Google Search Results",
                "referrer_description": "Search results for 'MBA programs'"
            }
        }
    
    def test_create_page_view_interaction(self):
        """Test that page view interaction is created via process_page_view_event."""
        # In v2.0, we test the multi-interaction approach
        # A basic page view (no external referrer, not landing page) should create 1 interaction
        event_data = self.sample_event_data.copy()
        event_data['referrer'] = event_data['website_base']  # Same domain = no external referrer
        event_data['payload'] = {'is_landing_page': False}
        
        # Process the event
        interactions = WebInteraction.process_page_view_event(event_data)
        
        # Should create only the page view interaction
        self.assertEqual(len(interactions), 1)
        page_view = interactions[0]
        
        # Verify it's a WebInteraction
        self.assertIsInstance(page_view, WebInteraction)
        self.assertEqual(page_view.website, self.website)
        self.assertEqual(page_view.session_id, "sess_test123")
        self.assertEqual(page_view.visitor_cookie, "visitor_test456")
        self.assertEqual(page_view.utm_source, "google")
        self.assertEqual(page_view.utm_medium, "organic")
        
        # Verify the core Interaction was created with page_view action
        self.assertIsNotNone(page_view.interaction)
        self.assertEqual(page_view.interaction.action.code, "page_view")
    
    def test_create_referrer_click_interaction(self):
        """Test that referrer click interaction is created when there's an external referrer."""
        # In v2.0, referrer click is created automatically when external referrer exists
        event_data = self.sample_event_data.copy()
        event_data['referrer'] = "https://google.com/search?q=mba+programs"  # External referrer
        event_data['payload'] = {'is_landing_page': False}
        
        # Process the event
        interactions = WebInteraction.process_page_view_event(event_data)
        
        # Should create 2 interactions: page view + referrer click
        self.assertEqual(len(interactions), 2)
        
        # Find the referrer click interaction (it's created second)
        referrer_click = interactions[1]
        
        # Verify it's a WebInteraction with referrer click action
        self.assertIsInstance(referrer_click, WebInteraction)
        self.assertEqual(referrer_click.website, self.website)
        self.assertEqual(referrer_click.session_id, "sess_test123")
        
        # Verify the core Interaction has referrer_click action
        self.assertIsNotNone(referrer_click.interaction)
        self.assertEqual(referrer_click.interaction.action.code, "referrer_click")
        
        # Verify the touchpoint reflects the external source
        self.assertIsNotNone(referrer_click.interaction.touchpoint)
        # Touchpoint should be related to Google organic search
        touchpoint_code = referrer_click.interaction.touchpoint.code
        self.assertIn("google", touchpoint_code.lower())
    
    def test_create_session_start_interaction(self):
        """Test that session start interaction is created for landing pages."""
        # In v2.0, session start is created automatically when it's a landing page
        event_data = self.sample_event_data.copy()
        event_data['referrer'] = "https://google.com/search?q=mba+programs"  # External referrer
        event_data['payload'] = {'is_landing_page': True}  # Mark as landing page
        
        # Process the event
        interactions = WebInteraction.process_page_view_event(event_data)
        
        # Should create 3 interactions: page view + referrer click + session start
        self.assertEqual(len(interactions), 3)
        
        # Find the session start interaction (it's created third)
        session_start = interactions[2]
        
        # Verify it's a WebInteraction with session_start action
        self.assertIsInstance(session_start, WebInteraction)
        self.assertEqual(session_start.website, self.website)
        self.assertEqual(session_start.session_id, "sess_test123")
        
        # Verify the core Interaction has session_start action
        self.assertIsNotNone(session_start.interaction)
        self.assertEqual(session_start.interaction.action.code, "session_start")
        
        # Verify the touchpoint reflects the session entry point
        self.assertIsNotNone(session_start.interaction.touchpoint)
    
    def test_get_or_create_agent(self):
        """Test agent creation from user agent string."""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Create agent
        agent = WebInteraction._get_or_create_agent(user_agent)
        
        # Verify agent was created
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.agent_type, "browser")
        self.assertIn("Chrome", agent.name)
        self.assertIn("Windows", agent.name)
        self.assertEqual(agent.metadata["user_agent"], user_agent)
    
    def test_parse_user_agent(self):
        """Test user agent parsing."""
        # Test Chrome on Windows
        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        browser_info = WebInteraction._parse_user_agent(chrome_ua)
        
        self.assertEqual(browser_info["browser"]["family"], "Chrome")
        self.assertEqual(browser_info["os"]["family"], "Windows")
        self.assertEqual(browser_info["device"]["family"], "Other")
        
        # Test Firefox on macOS
        firefox_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
        browser_info = WebInteraction._parse_user_agent(firefox_ua)
        
        self.assertEqual(browser_info["browser"]["family"], "Firefox")
        self.assertEqual(browser_info["os"]["family"], "macOS")
        
        # Test mobile device (iPhone)
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        browser_info = WebInteraction._parse_user_agent(mobile_ua)
        
        self.assertEqual(browser_info["browser"]["family"], "Safari")
        # Note: ua-parser may return "Mac OS X" or "iOS" depending on version
        # The key is that it detects the device as iPhone
        self.assertIn(browser_info["os"]["family"], ["iOS", "Mac OS X", "macOS"])
        self.assertEqual(browser_info["device"]["family"], "Mobile")
    
    def test_is_bot_user_agent(self):
        """Test bot detection from user agent."""
        # Test bot user agents
        bot_uas = [
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "facebookexternalhit/1.1",
            "Twitterbot/1.0",
            "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com/robots)"
        ]
        
        for ua in bot_uas:
            self.assertTrue(WebInteraction._is_bot_user_agent(ua), f"Should detect bot: {ua}")
        
        # Test regular user agents
        regular_uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        for ua in regular_uas:
            self.assertFalse(WebInteraction._is_bot_user_agent(ua), f"Should not detect bot: {ua}")
    
    def test_extract_domain(self):
        """Test domain extraction from URL."""
        # Test various URLs
        test_cases = [
            ("https://google.com/search?q=test", "google.com"),
            ("https://www.example.com/path", "www.example.com"),
            ("http://subdomain.example.org", "subdomain.example.org"),
            ("invalid-url", "unknown"),
            ("", "unknown")
        ]
        
        for url, expected_domain in test_cases:
            result = WebInteraction._extract_domain(url)
            self.assertEqual(result, expected_domain, f"Failed for URL: {url}")
    
    def test_get_default_division(self):
        """Test default division creation."""
        # Create default division
        division = WebInteraction._get_default_division()
        
        # Verify division was created
        self.assertIsInstance(division, Division)
        self.assertEqual(division.name, "Default Division")
        self.assertTrue(division.is_active)
        
        # Test that subsequent calls return the same division
        division2 = WebInteraction._get_default_division()
        self.assertEqual(division, division2)


class PageViewEventProcessingTestCase(TestCase):
    """Test cases for the complete page view event processing."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization first
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            is_active=True
        )
        
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
            organization=self.organization,
            is_active=True
        )
        
        # Sample event data
        self.sample_event_data = {
            "event_type": "page_view",
            "website_base": "https://test.example.com",
            "full_url": "https://test.example.com/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_test123",
            "visitor_cookie": "visitor_test456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "utm_campaign": "mba_search",
            "payload": {
                "page_title": "MBA Programs - Test University",
                "page_category": "academic_programs"
            }
        }
    
    def test_process_page_view_event(self):
        """Test the complete page view event processing (integration test)."""
        # Note: This is now an integration test that uses actual database
        # rather than mocking, since v2.0 uses DefaultTouchpointResolver from connectors
        
        # Process the page view event
        interactions = WebInteraction.process_page_view_event(self.sample_event_data)
        
        # Verify interactions were created
        self.assertIsInstance(interactions, list)
        self.assertGreater(len(interactions), 0)
        
        # Verify all interactions are WebInteraction instances
        for interaction in interactions:
            self.assertIsInstance(interaction, WebInteraction)
            self.assertEqual(interaction.website.base_url, "https://test.example.com")
            self.assertEqual(interaction.session_id, "sess_test123")
    
    def test_process_page_view_event_without_referrer(self):
        """Test page view event processing without external referrer (integration test)."""
        # Remove referrer from event data
        event_data = self.sample_event_data.copy()
        event_data["referrer"] = ""
        
        # Process the event
        interactions = WebInteraction.process_page_view_event(event_data)
        
        # Should create only page view interaction (no referrer click)
        self.assertEqual(len(interactions), 1)
        self.assertIsInstance(interactions[0], WebInteraction)
    
    def test_process_page_view_event_with_external_referrer(self):
        """Test page view event processing with external referrer (integration test)."""
        # Process the event (has external referrer in sample_event_data)
        interactions = WebInteraction.process_page_view_event(self.sample_event_data)
        
        # Should create page view and referrer click interactions
        self.assertEqual(len(interactions), 2)
        for interaction in interactions:
            self.assertIsInstance(interaction, WebInteraction)
    
    def test_process_page_view_event_with_new_session(self):
        """Test page view event processing with new session (integration test)."""
        # Mark as landing page to trigger session start
        event_data = self.sample_event_data.copy()
        event_data["payload"] = event_data.get("payload", {}).copy()
        event_data["payload"]["is_landing_page"] = True
        
        # Process the event
        interactions = WebInteraction.process_page_view_event(event_data)
        
        # Should create all three interactions (page view, referrer click, session start)
        self.assertEqual(len(interactions), 3)
        for interaction in interactions:
            self.assertIsInstance(interaction, WebInteraction)


class WebSessionTestCase(TestCase):
    """Test cases for WebSession model."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization first
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            is_active=True
        )
        
        # Create test division and website
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
            organization=self.organization,
            is_active=True
        )
        
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.example.com",
            division=self.division,
            is_active=True
        )
    
    def test_web_session_creation(self):
        """Test WebSession creation."""
        session = WebSession.objects.create(
            session_id="sess_test123",
            visitor_cookie="visitor_test456",
            website=self.website,
            started_at=timezone.now()
        )
        
        # Verify session was created
        self.assertIsInstance(session, WebSession)
        self.assertEqual(session.session_id, "sess_test123")
        self.assertEqual(session.visitor_cookie, "visitor_test456")
        self.assertEqual(session.website, self.website)
        self.assertTrue(session.is_session_active)
    
    def test_web_session_duration(self):
        """Test WebSession duration calculation."""
        now = timezone.now()
        session = WebSession.objects.create(
            session_id="sess_test123",
            visitor_cookie="visitor_test456",
            website=self.website,
            started_at=now
        )
        
        # Test active session duration
        duration = session.duration
        self.assertIsNotNone(duration)
        self.assertGreater(duration.total_seconds(), 0)
        
        # Test ended session duration
        session.ended_at = now + timezone.timedelta(minutes=30)
        session.save()
        
        duration = session.duration
        # Use assertAlmostEqual for floating point comparison
        self.assertAlmostEqual(duration.total_seconds(), 30 * 60, delta=1)  # 30 minutes +/- 1 second
    
    def test_web_session_activity_update(self):
        """Test WebSession activity update."""
        session = WebSession.objects.create(
            session_id="sess_test123",
            visitor_cookie="visitor_test456",
            website=self.website,
            started_at=timezone.now()
        )
        
        # Update activity
        session.update_activity()
        
        # Verify last activity was updated
        self.assertIsNotNone(session.last_activity_at)
        self.assertTrue(session.is_session_active)


class WebAgentTestCase(TestCase):
    """Test cases for WebAgent proxy model."""
    
    def setUp(self):
        """Set up test data."""
        # Create test agent
        self.agent = Agent.objects.create(
            identifier="test_agent_123",
            agent_type="browser",
            name="Test Browser",
            metadata={
                "browser": {"family": "Chrome", "version": "91.0"},
                "os": {"family": "Windows", "version": "10"},
                "device": {"family": "Desktop", "brand": "Unknown", "model": "Unknown"}
            }
        )
    
    def test_web_agent_properties(self):
        """Test WebAgent proxy model properties."""
        web_agent = WebAgent.objects.get(pk=self.agent.pk)
        
        # Test browser properties
        self.assertEqual(web_agent.browser_family, "Chrome")
        self.assertEqual(web_agent.browser_version, "91.0")
        
        # Test OS properties
        self.assertEqual(web_agent.os_family, "Windows")
        self.assertEqual(web_agent.os_version, "10")
        
        # Test device properties
        self.assertEqual(web_agent.device_family, "Desktop")
        self.assertEqual(web_agent.device_brand, "Unknown")
        self.assertEqual(web_agent.device_model, "Unknown")
        
        # Test boolean properties
        self.assertFalse(web_agent.is_mobile)
        self.assertFalse(web_agent.is_bot)
        self.assertFalse(web_agent.is_webview)
    
    def test_web_agent_display_name(self):
        """Test WebAgent display name generation."""
        web_agent = WebAgent.objects.get(pk=self.agent.pk)
        
        # Test display name
        display_name = web_agent.display_name
        self.assertIn("Chrome", display_name)
        self.assertIn("Windows", display_name)
        
        # Test technical summary
        technical_summary = web_agent.technical_summary
        self.assertIn("Chrome", technical_summary)
        self.assertIn("Windows", technical_summary)


class WebsiteTestCase(TestCase):
    """Test cases for Website model."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization first
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            is_active=True
        )
        
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
            organization=self.organization,
            is_active=True
        )
    
    def test_website_creation(self):
        """Test Website creation."""
        website = Website.objects.create(
            name="Test Website",
            base_url="https://test.example.com",
            division=self.division,
            is_active=True
        )
        
        # Verify website was created
        self.assertIsInstance(website, Website)
        self.assertEqual(website.name, "Test Website")
        self.assertEqual(website.base_url, "https://test.example.com")
        self.assertEqual(website.division, self.division)
        self.assertTrue(website.active)
    
    def test_website_string_representation(self):
        """Test Website string representation."""
        website = Website.objects.create(
            name="Test Website",
            base_url="https://test.example.com",
            division=self.division,
            is_active=True
        )
        
        # Test string representation
        str_repr = str(website)
        self.assertIn("Test Website", str_repr)
        self.assertIn("test.example.com", str_repr)
