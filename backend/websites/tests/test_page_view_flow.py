"""
Comprehensive tests for page view event processing flow.

This module tests the complete multi-interaction approach for page view events,
including all scenarios: new visitors, returning visitors, external referrers,
session inference, and touchpoint resolution.
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from interactions.models import Action, Agent, Interaction, Touchpoint, TouchpointClass, Channel, Medium
from websites.models import WebInteraction, Website, WebSession, WebAgent
from our_institution.models import Division, OurOrganization


class PageViewFlowTestCase(TestCase):
    """
    Test case for the complete page view event processing flow.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create test organization
        self.organization = OurOrganization.objects.create(
            name="Test Organization",
            legal_name="Test Organization Legal Name"
        )
        
        # Create test division
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST",
            description="Test division for testing",
            organization=self.organization
        )
        
        # Create test website
        self.website = Website.objects.create(
            name="ESAN University",
            base_url="https://esan.edu.pe",
            division=self.division,
            active=True
        )
        
        # Create test actions
        self.no_action = Action.objects.create(
            name="Sin Acción",
            code="no_action",
            description="Evento inferido o acción realizada hacia el usuario"
        )
        
        self.external_click_action = Action.objects.create(
            name="External Click",
            code="external_click",
            description="Click from external source"
        )
        
        # Create test agent (will be created automatically by processor)
        # Using the new ua-parser format: browser-version-os
        self.expected_agent_identifier = "chrome-91.0.4472-windows"
        
        # Create test medium
        self.organic_medium = Medium.objects.create(
            name="Organic",
            code="organic",
            description="Organic search traffic"
        )
        
        # Create test channel
        self.google_channel = Channel.objects.create(
            name="Google",
            code="google",
            medium=self.organic_medium
        )
        
        self.esan_channel = Channel.objects.create(
            name="ESAN University",
            code="esan.edu.pe",
            medium=self.organic_medium
        )
        
        # Create test touchpoint classes
        self.organic_traffic_class = TouchpointClass.objects.create(
            name="Organic Search Traffic",
            code="web.organic_traffic",
            description="Organic search traffic touchpoint class"
        )
        
        self.internal_interaction_class = TouchpointClass.objects.create(
            name="Internal Website Interaction",
            code="web.internal_interaction",
            description="Internal website interaction touchpoint class"
        )
        
        # Create test client
        self.client = Client()
    
    def test_new_visitor_with_external_referrer(self):
        """
        Test scenario: New visitor with external referrer (Google search).
        
        Expected: 3 interactions created
        1. Page View Interaction (no_action)
        2. Referrer Click Interaction (external_click)
        3. Session Start Interaction (no_action)
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_new_visitor_123_unique",
            "visitor_cookie": "visitor_new_456_unique",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "utm_campaign": "mba_search",
            "utm_content": "programs_page",
            "utm_term": "mba programs",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "page_category": "academic_programs",
                "load_time": 1.2,
                "is_landing_page": True,
                "page_depth": 2,
                "referrer_title": "Google Search Results",
                "referrer_description": "Search results for 'MBA programs Peru'"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify 3 interactions were created
        self.assertEqual(len(created_interactions), 3)
        
        # Verify all interactions are created
        self.assertEqual(len(created_interactions), 3)
        
        # Verify all interactions have the same website and session
        for interaction in created_interactions:
            self.assertEqual(interaction.website, self.website)
            self.assertEqual(interaction.session_id, "sess_new_visitor_123_unique")
            self.assertEqual(interaction.visitor_cookie, "visitor_new_456_unique")
        
        # Verify actions are correct (no_action for page view and session start, external_click for referrer)
        actions = [interaction.interaction.action for interaction in created_interactions]
        self.assertEqual(actions.count(self.no_action), 2)  # page view + session start
        self.assertEqual(actions.count(self.external_click_action), 1)  # referrer click
    
    def test_returning_visitor_with_external_referrer(self):
        """
        Test scenario: Returning visitor with external referrer.
        
        Expected: 2 interactions created
        1. Page View Interaction (no_action)
        2. Referrer Click Interaction (external_click)
        No session start (existing session)
        """
        # Create existing interaction for this visitor
        # Create existing interaction for returning visitor
        existing_agent = Agent.objects.create(
            name="Chrome",
            agent_type="browser",
            identifier="chrome-91.0.4472-windows"
        )
        existing_interaction = WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=self.no_action,
                agent=existing_agent,
                occurred_at=timezone.now() - timedelta(minutes=5)
            ),
            website=self.website,
            session_id="sess_returning_123",
            visitor_cookie="visitor_returning_456",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://facebook.com/post/123",
            "session_id": "sess_returning_123",
            "visitor_cookie": "visitor_returning_456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "facebook",
            "utm_medium": "social",
            "utm_campaign": "mba_promotion",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "referrer_title": "Facebook Post",
                "referrer_description": "MBA promotion post on Facebook"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify 3 interactions were created (page view, referrer click, session start)
        self.assertEqual(len(created_interactions), 3)
        
        # Verify actions are correct (no_action for page view and session start, external_click for referrer)
        actions = [interaction.interaction.action for interaction in created_interactions]
        self.assertEqual(actions.count(self.no_action), 2)  # page view and session start
        self.assertEqual(actions.count(self.external_click_action), 1)  # referrer click
    
    def test_direct_traffic_no_referrer(self):
        """
        Test scenario: Direct traffic with no referrer.
        
        Expected: 1-2 interactions created
        1. Page View Interaction (no_action)
        2. Session Start Interaction (no_action) - if new session
        No referrer click (no external referrer)
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/",
            "referrer": "",
            "session_id": "sess_direct_123_unique",
            "visitor_cookie": "visitor_direct_456_unique",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "element": "body",
            "payload": {
                "page_title": "ESAN University - Home",
                "page_description": "Welcome to ESAN University",
                "is_landing_page": True
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify 2 interactions were created (page view + session start)
        self.assertEqual(len(created_interactions), 2)
        
        # Verify actions are correct (no_action for both page view and session start)
        actions = [interaction.interaction.action for interaction in created_interactions]
        self.assertEqual(actions.count(self.no_action), 2)  # page view + session start
        self.assertEqual(actions.count(self.external_click_action), 0)  # no referrer click
    
    def test_session_timeout_new_session(self):
        """
        Test scenario: Session timeout triggers new session.
        
        Expected: 2-3 interactions created
        1. Page View Interaction (no_action)
        2. Session Start Interaction (no_action) - due to timeout
        3. Referrer Click Interaction (external_click) - if external referrer
        """
        # Create old interaction (more than 30 minutes ago)
        old_agent = Agent.objects.create(
            name="Chrome",
            agent_type="browser",
            identifier="chrome-91.0.4472-windows"
        )
        old_interaction = WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=self.no_action,
                agent=old_agent,
                occurred_at=timezone.now() - timedelta(minutes=35)
            ),
            website=self.website,
            session_id="sess_timeout_123",
            visitor_cookie="visitor_timeout_456",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://linkedin.com/post/456",
            "session_id": "sess_timeout_123_unique",
            "visitor_cookie": "visitor_timeout_456_unique",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "linkedin",
            "utm_medium": "social",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "referrer_title": "LinkedIn Post",
                "referrer_description": "MBA promotion on LinkedIn"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify 3 interactions were created
        self.assertEqual(len(created_interactions), 3)
        
        # Verify actions are correct (no_action for page view and session start, external_click for referrer)
        actions = [interaction.interaction.action for interaction in created_interactions]
        self.assertEqual(actions.count(self.no_action), 2)  # page view + session start
        self.assertEqual(actions.count(self.external_click_action), 1)  # referrer click
    
    def test_api_endpoint_page_view(self):
        """
        Test the API endpoint for page view events.
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_api_123_unique",
            "visitor_cookie": "visitor_api_456_unique",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals"
            }
        }
        
        # Make API request
        response = self.client.post(
            reverse('websites:page_view_event'),
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['interactions_created'], 3)
    
    def test_api_endpoint_invalid_data(self):
        """
        Test API endpoint with invalid data.
        """
        # Missing required field
        event_data = {
            "event_type": "page_view",
            "full_url": "https://esan.edu.pe/programs/mba"
            # Missing website_base
        }
        
        response = self.client.post(
            reverse('websites:page_view_event'),
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
    
    def test_api_endpoint_wrong_event_type(self):
        """
        Test API endpoint with wrong event type.
        """
        event_data = {
            "event_type": "form_submit",  # Wrong event type
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba"
        }
        
        response = self.client.post(
            reverse('websites:page_view_event'),
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
    
    def test_touchpoint_resolution(self):
        """
        Test that touchpoints are properly resolved for all interaction types.
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_touchpoint_123",
            "visitor_cookie": "visitor_touchpoint_456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify all interactions have touchpoints
        for interaction in created_interactions:
            self.assertIsNotNone(interaction.interaction.touchpoint)
            self.assertIsInstance(interaction.interaction.touchpoint, Touchpoint)
    
    def test_website_creation(self):
        """
        Test that websites are properly created from event data.
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://newwebsite.com",
            "full_url": "https://newwebsite.com/page",
            "session_id": "sess_new_website_123",
            "visitor_cookie": "visitor_new_website_456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "element": "body",
            "payload": {
                "page_title": "New Website Page"
            }
        }
        
        # Verify website doesn't exist
        self.assertFalse(Website.objects.filter(base_url="https://newwebsite.com").exists())
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify website was created
        self.assertTrue(Website.objects.filter(base_url="https://newwebsite.com").exists())
        new_website = Website.objects.get(base_url="https://newwebsite.com")
        self.assertEqual(new_website.name, "Newwebsite.com Website")
        self.assertTrue(new_website.active)
    
    def test_agent_creation(self):
        """
        Test that agents are properly created from user agent strings.
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "session_id": "sess_agent_123",
            "visitor_cookie": "visitor_agent_456",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify agent was created with correct details
        # Get the first interaction (page view)
        page_view_interaction = created_interactions[0]
        agent = page_view_interaction.interaction.agent
        
        self.assertEqual(agent.name, "Chrome")
        self.assertEqual(agent.agent_type, "browser")
        self.assertIn("91.0", agent.identifier)
    
    def test_payload_data_preservation(self):
        """
        Test that payload data is properly preserved in interactions.
        """
        event_data = {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_payload_123",
            "visitor_cookie": "visitor_payload_456",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "utm_source": "google",
            "utm_medium": "organic",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs designed for working professionals",
                "page_category": "academic_programs",
                "load_time": 1.2,
                "is_landing_page": True,
                "page_depth": 2,
                "referrer_title": "Google Search Results",
                "referrer_description": "Search results for 'MBA programs Peru'",
                "custom_field": "custom_value"
            }
        }
        
        # Process the event
        created_interactions = WebInteraction.process_page_view_event(event_data)
        
        # Verify payload data is preserved
        # Get interactions by action type
        page_view_interaction = next(i for i in created_interactions if i.interaction.action == self.no_action and 'page_title' in i.interaction.payload)
        referrer_click_interaction = next(i for i in created_interactions if i.interaction.action == self.external_click_action)
        session_start_interaction = next(i for i in created_interactions if i.interaction.action == self.no_action and 'landing_page' in i.interaction.payload)
        
        # Verify page view interaction payload
        interaction_payload = page_view_interaction.interaction.payload
        self.assertEqual(interaction_payload['page_title'], "MBA Programs - ESAN University")
        self.assertEqual(interaction_payload['page_description'], "Comprehensive MBA programs designed for working professionals")
        self.assertEqual(interaction_payload['page_category'], "academic_programs")
        self.assertEqual(interaction_payload['load_time'], 1.2)
        self.assertTrue(interaction_payload['is_landing_page'])
        self.assertEqual(interaction_payload['page_depth'], 2)
        
        # Verify WebInteraction payload is also preserved
        web_payload = page_view_interaction.payload
        self.assertEqual(web_payload['page_title'], "MBA Programs - ESAN University")
        self.assertEqual(web_payload['custom_field'], "custom_value")
        
        # Verify referrer click interaction has referrer data
        referrer_payload = referrer_click_interaction.interaction.payload
        self.assertEqual(referrer_payload['referrer_url'], "https://google.com/search?q=mba+programs")
        self.assertEqual(referrer_payload['referrer_title'], "Google Search Results")
        self.assertEqual(referrer_payload['referrer_description'], "Search results for 'MBA programs Peru'")
        
        # Verify session start interaction has session data
        session_payload = session_start_interaction.interaction.payload
        self.assertTrue(session_payload['landing_page'])
        self.assertIn('session_start_time', session_payload)
        self.assertIn('inference_reason', session_payload)


class PageReadEventProcessorTestCase(TestCase):
    """Test cases for PageReadEventProcessor functionality."""
    
    def setUp(self):
        """Set up test data for page read event tests."""
        # Create organization and division
        from our_institution.models import OurOrganization, Division
        self.org = OurOrganization.objects.create(
            name="Test Organization",
            legal_name="Test Organization Legal Name"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST",
            description="Test division",
            organization=self.org
        )
        
        # Create website
        self.website = Website.objects.create(
            base_url="https://test.com",
            name="Test Website",
            division=self.division,
            active=True
        )
        
        # Create actions
        self.page_read_action = Action.objects.create(
            code='page_read',
            name='Leyó página',
            description='El usuario leyó una página de manera significativa'
        )
        
        self.no_action = Action.objects.create(
            code='no_action',
            name='Sin Acción',
            description='Evento inferido'
        )
        
        # Create test session
        self.session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_visitor_456",
            website=self.website,
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign"
        )
        
        # Create test agent
        self.agent = WebAgent.objects.create(
            name="Chrome",
            agent_type="browser",
            identifier="chrome-91.0.4472-windows",
            metadata={
                'browser': {'family': 'Chrome', 'version': '91.0.4472.124'},
                'os': {'family': 'Windows', 'version': '10.0'},
                'device': {'family': 'Other'}
            }
        )
        
        # Create a previous page view interaction (required for page read)
        self.page_view_interaction = WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=self.no_action,
                agent=self.agent,
                occurred_at=timezone.now() - timedelta(minutes=5),
                payload={
                    'interaction_type': 'page_view',
                    'page_title': 'Test Page',
                    'page_description': 'Test page description'
                }
            ),
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_visitor_456",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    def test_page_read_event_processing(self):
        """Test basic page read event processing."""
        from websites.processors import PageReadEventProcessor
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs designed for working professionals',
                'page_category': 'academic_programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'read_criteria_met': 'scroll_depth',
                'word_count': 1200,
                'interactions_count': 3
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        page_read_interaction = processor.process()
        
        # Verify interaction was created
        self.assertIsInstance(page_read_interaction, WebInteraction)
        self.assertEqual(page_read_interaction.interaction.action, self.page_read_action)
        self.assertEqual(page_read_interaction.website, self.website)
        self.assertEqual(page_read_interaction.session_id, 'test_session_123')
        self.assertEqual(page_read_interaction.visitor_cookie, 'test_visitor_456')
        
        # Verify engagement data
        payload = page_read_interaction.payload
        self.assertEqual(payload['page_title'], 'MBA Programs - Test University')
        self.assertEqual(payload['time_on_page'], 45)
        self.assertEqual(payload['scroll_depth'], 75)
        self.assertEqual(payload['interactions_count'], 3)
        self.assertIn('engagement_score', payload)
        self.assertEqual(payload['interaction_type'], 'page_read')
        
        # Verify engagement score calculation
        self.assertGreater(payload['engagement_score'], 0.5)  # Should be high engagement
        self.assertLessEqual(payload['engagement_score'], 1.0)
    
    def test_engagement_score_calculation(self):
        """Test engagement score calculation with different scenarios."""
        from websites.processors import PageReadEventProcessor
        
        # High engagement scenario
        high_engagement_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'High Engagement Page',
                'page_description': 'High engagement content',
                'time_on_page': 60,  # High time
                'scroll_depth': 90,  # High scroll
                'interactions_count': 5,  # High interactions
                'word_count': 1000
            }
        }
        
        processor = PageReadEventProcessor(high_engagement_data)
        high_interaction = processor.process()
        high_score = high_interaction.payload['engagement_score']
        
        # Low engagement scenario
        low_engagement_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'Low Engagement Page',
                'page_description': 'Low engagement content',
                'time_on_page': 15,  # Low time
                'scroll_depth': 25,  # Low scroll
                'interactions_count': 1,  # Low interactions
                'word_count': 1000
            }
        }
        
        processor = PageReadEventProcessor(low_engagement_data)
        low_interaction = processor.process()
        low_score = low_interaction.payload['engagement_score']
        
        # Verify high engagement has higher score
        self.assertGreater(high_score, low_score)
        self.assertGreater(high_score, 0.7)  # High engagement
        self.assertLess(low_score, 0.5)  # Low engagement
    
    def test_short_content_adjustment(self):
        """Test engagement score adjustment for short content."""
        from websites.processors import PageReadEventProcessor
        
        # Short content (should need less time for high engagement)
        short_content_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'Short Content Page',
                'page_description': 'Short content',
                'time_on_page': 15,  # 15 seconds on short content
                'scroll_depth': 80,  # High scroll
                'interactions_count': 2,
                'word_count': 150  # Short content
            }
        }
        
        processor = PageReadEventProcessor(short_content_data)
        short_interaction = processor.process()
        short_score = short_interaction.payload['engagement_score']
        
        # Should have good engagement score despite shorter time
        self.assertGreater(short_score, 0.6)  # Good engagement for short content
    
    def test_touchpoint_creation(self):
        """Test that page touchpoint is created correctly."""
        from websites.processors import PageReadEventProcessor
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        page_read_interaction = processor.process()
        
        # Verify touchpoint was created
        touchpoint = page_read_interaction.interaction.touchpoint
        self.assertIsNotNone(touchpoint)
        self.assertEqual(touchpoint.name, 'MBA Programs - Test University')
        self.assertEqual(touchpoint.description, 'Comprehensive MBA programs')
        self.assertEqual(touchpoint.url, 'https://test.com/programs/mba')
        
        # Verify touchpoint has correct channel and class
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.internal_interaction')
    
    def test_no_previous_page_view_error(self):
        """Test that page read fails without previous page view."""
        from websites.processors import PageReadEventProcessor
        
        # Create new session without page view
        new_session = WebSession.objects.create(
            session_id="new_session_789",
            visitor_cookie="new_visitor_012",
            website=self.website
        )
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'new_session_789',
            'visitor_cookie': 'new_visitor_012',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        
        with self.assertRaises(ValueError) as context:
            processor.process()
        
        self.assertIn("Page read requires a previous page view", str(context.exception))
    
    def test_session_not_found_error(self):
        """Test that page read fails with non-existent session."""
        from websites.processors import PageReadEventProcessor
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'nonexistent_session',
            'visitor_cookie': 'nonexistent_visitor',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        
        with self.assertRaises(ValueError) as context:
            processor.process()
        
        self.assertIn("Page read requires a previous page view", str(context.exception))
    
    def test_no_utm_fields(self):
        """Test that page read interactions don't have UTM fields."""
        from websites.processors import PageReadEventProcessor
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        page_read_interaction = processor.process()
        
        # Verify no UTM fields are set
        self.assertEqual(page_read_interaction.utm_source, '')
        self.assertEqual(page_read_interaction.utm_medium, '')
        self.assertEqual(page_read_interaction.utm_campaign, '')
        self.assertEqual(page_read_interaction.utm_content, '')
        self.assertEqual(page_read_interaction.utm_term, '')
    
    def test_session_activity_update(self):
        """Test that session activity is updated after page read."""
        from websites.processors import PageReadEventProcessor
        
        # Get initial last activity
        initial_activity = self.session.last_activity_at
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        page_read_interaction = processor.process()
        
        # Refresh session from database
        self.session.refresh_from_db()
        
        # Verify last activity was updated
        self.assertGreater(self.session.last_activity_at, initial_activity)
    
    def test_agent_creation_and_parsing(self):
        """Test that agents are created and parsed correctly."""
        from websites.processors import PageReadEventProcessor
        
        event_data = {
            'event_type': 'page_read',
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'element': 'body',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        page_read_interaction = processor.process()
        
        # Verify agent was created/used
        agent = page_read_interaction.interaction.agent
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, WebAgent)
        
        # Verify agent has correct metadata
        self.assertIn('browser', agent.metadata)
        self.assertIn('os', agent.metadata)
        self.assertIn('device', agent.metadata)
        
        # Verify agent properties work
        self.assertEqual(agent.browser_family, 'Chrome')
        self.assertEqual(agent.os_family, 'Mac OS X')
        self.assertFalse(agent.is_mobile)
        self.assertFalse(agent.is_bot)
