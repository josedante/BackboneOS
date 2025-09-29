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
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
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
        """Test creation of page view interaction."""
        # Create page view interaction
        web_interaction = WebInteraction._create_page_view_interaction(self.sample_event_data)
        
        # Verify WebInteraction was created
        self.assertIsInstance(web_interaction, WebInteraction)
        self.assertEqual(web_interaction.website, self.website)
        self.assertEqual(web_interaction.session_id, "sess_test123")
        self.assertEqual(web_interaction.visitor_cookie, "visitor_test456")
        self.assertEqual(web_interaction.utm_source, "google")
        self.assertEqual(web_interaction.utm_medium, "organic")
        
        # Verify core Interaction was created
        self.assertIsNotNone(web_interaction.interaction)
        self.assertEqual(web_interaction.interaction.action.code, "no_action")
        self.assertIn("page_view", web_interaction.interaction.payload["interaction_type"])
    
    def test_create_referrer_click_interaction(self):
        """Test creation of referrer click interaction."""
        # Create a mock touchpoint
        mock_touchpoint = MagicMock()
        mock_touchpoint.code = "web.referrer_click.google_search"
        
        # Create referrer click interaction
        web_interaction = WebInteraction._create_referrer_click_interaction(
            self.sample_event_data, 
            mock_touchpoint
        )
        
        # Verify WebInteraction was created
        self.assertIsInstance(web_interaction, WebInteraction)
        self.assertEqual(web_interaction.website, self.website)
        self.assertEqual(web_interaction.session_id, "sess_test123")
        self.assertIn("referrer_click", web_interaction.payload["interaction_type"])
        
        # Verify core Interaction was created
        self.assertIsNotNone(web_interaction.interaction)
        self.assertEqual(web_interaction.interaction.action.code, "external_click")
        self.assertEqual(web_interaction.interaction.touchpoint, mock_touchpoint)
        self.assertIn("referrer_click", web_interaction.interaction.payload["interaction_type"])
    
    def test_create_session_start_interaction(self):
        """Test creation of session start interaction."""
        # Create a mock touchpoint
        mock_touchpoint = MagicMock()
        mock_touchpoint.code = "web.session_start"
        
        # Create session start interaction
        web_interaction = WebInteraction._create_session_start_interaction(
            self.sample_event_data, 
            mock_touchpoint
        )
        
        # Verify WebInteraction was created
        self.assertIsInstance(web_interaction, WebInteraction)
        self.assertEqual(web_interaction.website, self.website)
        self.assertEqual(web_interaction.session_id, "sess_test123")
        self.assertTrue(web_interaction.payload["session_start"])
        self.assertIn("session_start", web_interaction.payload["interaction_type"])
        
        # Verify core Interaction was created
        self.assertIsNotNone(web_interaction.interaction)
        self.assertEqual(web_interaction.interaction.action.code, "session_start")
        self.assertEqual(web_interaction.interaction.touchpoint, mock_touchpoint)
        self.assertTrue(web_interaction.interaction.payload["session_start"])
    
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
        
        # Test mobile device
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        browser_info = WebInteraction._parse_user_agent(mobile_ua)
        
        self.assertEqual(browser_info["browser"]["family"], "Safari")
        self.assertEqual(browser_info["os"]["family"], "iOS")
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
        self.assertTrue(division.active)
        
        # Test that subsequent calls return the same division
        division2 = WebInteraction._get_default_division()
        self.assertEqual(division, division2)


class PageViewEventProcessingTestCase(TestCase):
    """Test cases for the complete page view event processing."""
    
    def setUp(self):
        """Set up test data."""
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
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
    
    @patch('websites.models.ExtendedTouchpointResolver')
    @patch('websites.models.ExtendedDatabaseMappingProvider')
    def test_process_page_view_event(self, mock_mapping_provider, mock_resolver):
        """Test the complete page view event processing."""
        # Mock the resolver and mapping provider
        mock_resolver_instance = MagicMock()
        mock_resolver.return_value = mock_resolver_instance
        
        # Mock touchpoints returned by resolver
        mock_touchpoints = [MagicMock(), MagicMock(), MagicMock()]
        mock_resolver_instance.resolve_batch.return_value = mock_touchpoints
        
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
        """Test page view event processing without external referrer."""
        # Remove referrer from event data
        event_data = self.sample_event_data.copy()
        event_data["referrer"] = ""
        
        # Mock the resolver to return only one touchpoint (page view)
        with patch('websites.models.ExtendedTouchpointResolver') as mock_resolver_class:
            with patch('websites.models.ExtendedDatabaseMappingProvider'):
                mock_resolver = MagicMock()
                mock_resolver_class.return_value = mock_resolver
                mock_resolver.resolve_batch.return_value = [MagicMock()]
                
                # Process the event
                interactions = WebInteraction.process_page_view_event(event_data)
                
                # Should create only page view interaction
                self.assertEqual(len(interactions), 1)
                self.assertIsInstance(interactions[0], WebInteraction)
    
    def test_process_page_view_event_with_external_referrer(self):
        """Test page view event processing with external referrer."""
        # Mock the resolver to return multiple touchpoints
        with patch('websites.models.ExtendedTouchpointResolver') as mock_resolver_class:
            with patch('websites.models.ExtendedDatabaseMappingProvider'):
                mock_resolver = MagicMock()
                mock_resolver_class.return_value = mock_resolver
                mock_resolver.resolve_batch.return_value = [MagicMock(), MagicMock()]
                
                # Process the event
                interactions = WebInteraction.process_page_view_event(self.sample_event_data)
                
                # Should create page view and referrer click interactions
                self.assertEqual(len(interactions), 2)
                for interaction in interactions:
                    self.assertIsInstance(interaction, WebInteraction)
    
    def test_process_page_view_event_with_new_session(self):
        """Test page view event processing with new session."""
        # Mock the resolver to return all three touchpoints
        with patch('websites.models.ExtendedTouchpointResolver') as mock_resolver_class:
            with patch('websites.models.ExtendedDatabaseMappingProvider'):
                mock_resolver = MagicMock()
                mock_resolver_class.return_value = mock_resolver
                mock_resolver.resolve_batch.return_value = [MagicMock(), MagicMock(), MagicMock()]
                
                # Process the event
                interactions = WebInteraction.process_page_view_event(self.sample_event_data)
                
                # Should create all three interactions
                self.assertEqual(len(interactions), 3)
                for interaction in interactions:
                    self.assertIsInstance(interaction, WebInteraction)


class WebSessionTestCase(TestCase):
    """Test cases for WebSession model."""
    
    def setUp(self):
        """Set up test data."""
        # Create test division and website
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
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
        self.assertEqual(duration.total_seconds(), 30 * 60)  # 30 minutes
    
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
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            description="Test division for website interactions",
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
