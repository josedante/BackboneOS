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
from websites.models import WebInteraction, Website
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
        
        # Create test agent
        self.agent = Agent.objects.create(
            name="Chrome",
            agent_type="browser",
            identifier="chrome-91.0"
        )
        
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
        existing_interaction = WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=self.no_action,
                agent=self.agent,
                occurred_at=timezone.now() - timedelta(minutes=5)
            ),
            website=self.website,
            session_id="sess_returning_123",
            visitor_cookie="visitor_returning_456",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
        
        # Verify 2 interactions were created
        self.assertEqual(len(created_interactions), 2)
        
        # Verify actions are correct (no_action for page view, external_click for referrer)
        actions = [interaction.interaction.action for interaction in created_interactions]
        self.assertEqual(actions.count(self.no_action), 1)  # page view only
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
        old_interaction = WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=self.no_action,
                agent=self.agent,
                occurred_at=timezone.now() - timedelta(minutes=35)
            ),
            website=self.website,
            session_id="sess_timeout_123",
            visitor_cookie="visitor_timeout_456",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
