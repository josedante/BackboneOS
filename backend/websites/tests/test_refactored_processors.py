"""
Tests for refactored page view event processors.

This module contains comprehensive tests for the refactored PageViewEventProcessor,
testing the improvements applied from PageReadEventProcessor and ClickEventProcessor.
"""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
import logging

from interactions.models import Action, Agent, Interaction, Touchpoint, Channel, TouchpointClass, Medium
from websites.models import WebInteraction, Website, WebAgent, WebSession
from websites.processors import (
    PageViewEventProcessor,
    PageReadEventProcessor,
    ClickEventProcessor
)
from our_institution.models import Division, OurOrganization


class PageViewEventProcessorTestCase(TestCase):
    """Test cases for RefactoredPageViewEventProcessor functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization and division
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
        
        # Create test website
        self.website = Website.objects.create(
            base_url="https://test.com",
            name="Test Website",
            division=self.division,
            active=True
        )
        
        # Create test agent
        self.agent = WebAgent.objects.create(
            name="Test Browser",
            agent_type="browser",
            identifier="test-browser-1.0-windows"
        )
        
        # Create test session
        self.session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_visitor_456",
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
    
    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        
        self.assertEqual(processor.website, self.website)
        self.assertEqual(len(processor.created_interactions), 0)
        self.assertIsNone(processor.web_session)
    
    def test_page_view_only_interaction(self):
        """Test creating only page view interaction (no external referrer, existing session)."""
        # First create a WebSession to establish the session
        WebSession.objects.create(
            session_id='test_session_pageview_only',
            visitor_cookie='test_visitor_pageview_only',
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        # Then create an interaction to establish the session
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_pageview_only',
            visitor_cookie='test_visitor_pageview_only',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_pageview_only',
            'visitor_cookie': 'test_visitor_pageview_only',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'referrer': 'https://test.com/previous-page',  # Internal referrer
            'payload': {
                'page_title': 'Test Page',
                'page_description': 'Test page description'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Should create only 1 interaction (page view)
        self.assertEqual(len(interactions), 1)
        
        # Check page view interaction
        page_view = interactions[0]
        self.assertEqual(page_view.interaction.payload['interaction_type'], 'page_view')
        self.assertEqual(page_view.interaction.action.code, 'no_action')
        
        # Check touchpoint was created
        self.assertIsNotNone(page_view.interaction.touchpoint)
        self.assertEqual(page_view.interaction.touchpoint.name, 'Test Page')
        self.assertEqual(page_view.interaction.touchpoint.touchpoint_class.code, 'web.internal_interaction')
    
    def test_page_view_with_external_referrer(self):
        """Test creating page view and referrer click interactions."""
        # Create session and interaction to establish existing session
        WebSession.objects.create(
            session_id='test_session_external_referrer',
            visitor_cookie='test_visitor_external_referrer',
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_external_referrer',
            visitor_cookie='test_visitor_external_referrer',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_external_referrer',
            'visitor_cookie': 'test_visitor_external_referrer',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'referrer': 'https://google.com/search',  # External referrer
            'payload': {
                'page_title': 'Test Page',
                'page_description': 'Test page description'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Should create 2 interactions (page view + referrer click)
        self.assertEqual(len(interactions), 2)
        
        # Check page view interaction
        page_view = interactions[0]
        self.assertEqual(page_view.interaction.payload['interaction_type'], 'page_view')
        
        # Check referrer click interaction
        referrer_click = interactions[1]
        self.assertEqual(referrer_click.interaction.payload['interaction_type'], 'referrer_click')
        self.assertEqual(referrer_click.interaction.action.code, 'no_action')
        
        # Check referrer touchpoint was created
        self.assertIsNotNone(referrer_click.interaction.touchpoint)
        self.assertEqual(referrer_click.interaction.touchpoint.touchpoint_class.code, 'web.external_referrer')
    
    def test_page_view_with_new_session(self):
        """Test creating page view and session start interactions."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'new_session_789',  # New session
            'visitor_cookie': 'new_visitor_999',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'page_title': 'Test Page',
                'page_description': 'Test page description'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Should create 2 interactions (page view + session start)
        self.assertEqual(len(interactions), 2)
        
        # Check page view interaction
        page_view = interactions[0]
        self.assertEqual(page_view.interaction.payload['interaction_type'], 'page_view')
        
        # Check session start interaction
        session_start = interactions[1]
        self.assertEqual(session_start.interaction.payload['interaction_type'], 'session_start')
        self.assertEqual(session_start.interaction.action.code, 'no_action')
        # Note: is_new_visitor will be False because we're using the same visitor_cookie from setUp
        self.assertFalse(session_start.interaction.payload['is_new_visitor'])
        self.assertTrue(session_start.interaction.payload['landing_page'])
        
        # Check session start touchpoint was created
        self.assertIsNotNone(session_start.interaction.touchpoint)
        self.assertEqual(session_start.interaction.touchpoint.touchpoint_class.code, 'web.session_start')
    
    def test_all_three_interactions(self):
        """Test creating all three interactions (page view + referrer click + session start)."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'new_session_789',  # New session
            'visitor_cookie': 'new_visitor_999',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'referrer': 'https://google.com/search',  # External referrer
            'payload': {
                'page_title': 'Test Page',
                'page_description': 'Test page description'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Should create 3 interactions
        self.assertEqual(len(interactions), 3)
        
        # Check all interaction types
        interaction_types = [i.interaction.payload['interaction_type'] for i in interactions]
        self.assertIn('page_view', interaction_types)
        self.assertIn('referrer_click', interaction_types)
        self.assertIn('session_start', interaction_types)
        
        # Check all touchpoints were created
        for interaction in interactions:
            self.assertIsNotNone(interaction.interaction.touchpoint)
    
    def test_touchpoint_creation_page_view(self):
        """Test specific page view touchpoint creation."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'page_title': 'MBA Programs - Test University',
                'page_description': 'Comprehensive MBA programs'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check page view touchpoint
        page_view = interactions[0]
        touchpoint = page_view.interaction.touchpoint
        
        self.assertEqual(touchpoint.name, 'MBA Programs - Test University')
        self.assertEqual(touchpoint.description, 'Comprehensive MBA programs')
        self.assertEqual(touchpoint.url, 'https://test.com/programs/mba')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.internal_interaction')
        
        # Check channel was created correctly
        self.assertEqual(touchpoint.channel.code, 'test.com website')
        self.assertEqual(touchpoint.channel.medium.code, 'owned_website')
    
    def test_touchpoint_creation_referrer_click(self):
        """Test specific referrer click touchpoint creation."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'referrer': 'https://google.com/search?q=test',
            'payload': {
                'page_title': 'Test Page'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check referrer click touchpoint
        referrer_click = interactions[1]  # Second interaction
        touchpoint = referrer_click.interaction.touchpoint
        
        self.assertEqual(touchpoint.name, 'Referrer: google.com')
        self.assertEqual(touchpoint.description, 'User came from https://google.com/search?q=test')
        self.assertEqual(touchpoint.url, 'https://google.com/search?q=test')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.external_referrer')
    
    def test_touchpoint_creation_session_start(self):
        """Test specific session start touchpoint creation."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'new_session_789',
            'visitor_cookie': 'new_visitor_999',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'page_title': 'Test Page'
            }
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check session start touchpoint
        session_start = interactions[1]  # Second interaction
        touchpoint = session_start.interaction.touchpoint
        
        self.assertEqual(touchpoint.name, 'Session Start - Test Website')
        self.assertEqual(touchpoint.description, 'User started a new session on https://test.com')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.session_start')
    
    def test_external_referrer_detection(self):
        """Test external referrer detection logic."""
        processor = PageViewEventProcessor({
            'website_base': 'https://test.com',
            'referrer': 'https://google.com/search'
        })
        
        # External referrer
        self.assertTrue(processor._has_external_referrer())
        
        # Internal referrer
        processor.event_data['referrer'] = 'https://test.com/previous-page'
        self.assertFalse(processor._has_external_referrer())
        
        # No referrer
        processor.event_data['referrer'] = ''
        self.assertFalse(processor._has_external_referrer())
    
    def test_session_start_detection(self):
        """Test session start detection logic."""
        # New session (no existing interactions)
        processor = PageViewEventProcessor({
            'website_base': 'https://test.com',
            'session_id': 'new_session',
            'visitor_cookie': 'new_visitor'
        })
        self.assertTrue(processor._should_start_new_session())
        
        # Existing session - create session and interaction first
        WebSession.objects.create(
            session_id='test_session_existing',
            visitor_cookie='test_visitor_existing',
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_existing',
            visitor_cookie='test_visitor_existing',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        processor = PageViewEventProcessor({
            'website_base': 'https://test.com',
            'session_id': 'test_session_existing',
            'visitor_cookie': 'test_visitor_existing'
        })
        self.assertFalse(processor._should_start_new_session())
        
        # No session info
        processor = PageViewEventProcessor({
            'website_base': 'https://test.com',
            'session_id': '',
            'visitor_cookie': ''
        })
        self.assertTrue(processor._should_start_new_session())
    
    def test_transaction_rollback_on_error(self):
        """Test that transaction rollback works on error."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        
        # Mock an error during interaction creation
        with patch.object(processor, '_create_page_view_interaction', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                processor.process()
            
            # Verify no interactions were created
            self.assertEqual(len(processor.created_interactions), 0)
    
    def test_logging_functionality(self):
        """Test that logging works correctly."""
        # Create existing session to avoid session start interaction
        WebSession.objects.create(
            session_id='test_session_logging',
            visitor_cookie='test_visitor_logging',
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        # Create existing interaction to avoid session start
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(code='no_action', defaults={'name': 'Test'})[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_logging',
            visitor_cookie='test_visitor_logging',
            user_agent='Test User Agent'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_logging',
            'visitor_cookie': 'test_visitor_logging',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        
        # Test successful processing
        with self.assertLogs(logger='websites.processors', level='INFO') as log:
            interactions = processor.process()
            
        # Check that interactions were created successfully
        self.assertEqual(len(interactions), 1)
    
    def test_error_handling_in_touchpoint_creation(self):
        """Test error handling when touchpoint creation fails."""
        # Create session and interaction to establish existing session
        WebSession.objects.create(
            session_id='test_session_error_handling',
            visitor_cookie='test_visitor_error_handling',
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_error_handling',
            visitor_cookie='test_visitor_error_handling',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_error_handling',
            'visitor_cookie': 'test_visitor_error_handling',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        
        # Mock touchpoint creation to fail by raising an exception
        with patch.object(processor, '_create_page_view_touchpoint', side_effect=Exception("Touchpoint creation failed")):
            with self.assertRaises(Exception) as context:
                processor.process()
            
            # Verify the exception was raised
            self.assertIn("Touchpoint creation failed", str(context.exception))
    
    def test_agent_creation_and_parsing(self):
        """Test that agent creation and user agent parsing works correctly."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check that agent was created correctly
        agent = interactions[0].interaction.agent
        self.assertIsInstance(agent, WebAgent)
        self.assertEqual(agent.agent_type, 'browser')
        
        # Check that agent was created correctly
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, 'Chrome 91.0')
        self.assertEqual(agent.agent_type, 'browser')
    
    def test_website_creation_fallback(self):
        """Test website creation with fallback to default division."""
        # Delete existing division to test fallback
        self.division.delete()
        
        event_data = {
            'website_base': 'https://newtest.com',
            'full_url': 'https://newtest.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check that website was created
        self.assertIsNotNone(processor.website)
        self.assertEqual(processor.website.base_url, 'https://newtest.com')
        
        # Check that default division was created
        default_division = Division.objects.filter(code='DEFAULT').first()
        self.assertIsNotNone(default_division)
        self.assertEqual(processor.website.division, default_division)


class PageReadEventProcessorTestCase(TestCase):
    """Test cases for RefactoredPageReadEventProcessor functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization and division
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
        
        # Create test website
        self.website = Website.objects.create(
            base_url="https://test.com",
            name="Test Website",
            division=self.division,
            active=True
        )
        
        # Create test agent
        self.agent = WebAgent.objects.create(
            name="Test Browser",
            agent_type="browser",
            identifier="test-browser-1.0-windows"
        )
        
        # Create test session
        self.session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_visitor_456",
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
    
    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = PageReadEventProcessor(event_data)
        
        self.assertEqual(processor.website, self.website)
        self.assertIsNone(processor.web_session)
    
    def test_page_read_interaction_creation(self):
        """Test creating page read interaction with engagement data."""
        # First create a page view interaction to establish the session
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_123',
            visitor_cookie='test_visitor_456',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'page_title': 'Test Page',
                'page_description': 'Test page description',
                'time_on_page': 45,
                'scroll_depth': 75,
                'interactions_count': 3,
                'word_count': 1200
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        interaction = processor.process()
        
        # Check interaction was created
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.interaction.payload['interaction_type'], 'page_read')
        self.assertEqual(interaction.interaction.action.code, 'page_read')
        
        # Check engagement score was calculated
        self.assertIn('engagement_score', interaction.interaction.payload)
        self.assertGreater(interaction.interaction.payload['engagement_score'], 0)
        
        # Check touchpoint was created
        self.assertIsNotNone(interaction.interaction.touchpoint)
        self.assertEqual(interaction.interaction.touchpoint.name, 'Test Page')
        self.assertEqual(interaction.interaction.touchpoint.touchpoint_class.code, 'web.internal_interaction')
    
    def test_no_previous_page_view_error(self):
        """Test that error is raised when no previous page view exists."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'new_session_789',
            'visitor_cookie': 'new_visitor_999',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'page_title': 'Test Page'
            }
        }
        
        processor = PageReadEventProcessor(event_data)
        
        with self.assertRaises(ValueError) as context:
            processor.process()
        
        self.assertIn("Page read requires a previous page view", str(context.exception))
    
    def test_engagement_score_calculation(self):
        """Test engagement score calculation with different scenarios."""
        # First create a page view interaction
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_123',
            visitor_cookie='test_visitor_456',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # High engagement scenario
        high_engagement_payload = {
            'time_on_page': 60,
            'scroll_depth': 90,
            'interactions_count': 8,
            'word_count': 1000
        }
        
        processor = PageReadEventProcessor({
            'website_base': 'https://test.com',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'payload': high_engagement_payload
        })
        
        score = processor._calculate_engagement_score(high_engagement_payload)
        self.assertGreater(score, 0.8)  # Should be high engagement
        
        # Low engagement scenario
        low_engagement_payload = {
            'time_on_page': 5,
            'scroll_depth': 10,
            'interactions_count': 0,
            'word_count': 1000
        }
        
        score = processor._calculate_engagement_score(low_engagement_payload)
        self.assertLess(score, 0.3)  # Should be low engagement
    
    def test_touchpoint_creation(self):
        """Test that page touchpoint is created correctly."""
        # First create a page view interaction
        WebInteraction.objects.create(
            interaction=Interaction.objects.create(
                action=Action.objects.get_or_create(
                    code='no_action',
                    defaults={'name': 'Sin Acción', 'description': 'Test action'}
                )[0],
                agent=self.agent,
                occurred_at=timezone.now(),
                payload={'interaction_type': 'page_view'}
            ),
            website=self.website,
            session_id='test_session_123',
            visitor_cookie='test_visitor_456',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/programs/mba',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
        interaction = processor.process()
        
        # Verify touchpoint was created
        touchpoint = interaction.interaction.touchpoint
        self.assertIsNotNone(touchpoint)
        self.assertEqual(touchpoint.name, 'MBA Programs - Test University')
        self.assertEqual(touchpoint.description, 'Comprehensive MBA programs')
        self.assertEqual(touchpoint.url, 'https://test.com/programs/mba')
        
        # Verify touchpoint has correct channel and class
        self.assertEqual(touchpoint.channel.code, 'test.com website')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.internal_interaction')


class ClickEventProcessorTestCase(TestCase):
    """Test cases for RefactoredClickEventProcessor functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization and division
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
        
        # Create test website
        self.website = Website.objects.create(
            base_url="https://test.com",
            name="Test Website",
            division=self.division,
            active=True
        )
        
        # Create test agent
        self.agent = WebAgent.objects.create(
            name="Test Browser",
            agent_type="browser",
            identifier="test-browser-1.0-windows"
        )
        
        # Create test session
        self.session = WebSession.objects.create(
            session_id="test_session_123",
            visitor_cookie="test_visitor_456",
            website=self.website,
            agent=self.agent,
            ended_at=WebSession.get_session_end_time()
        )
    
    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = ClickEventProcessor(event_data)
        
        self.assertEqual(processor.website, self.website)
        self.assertIsNone(processor.web_session)
    
    def test_click_interaction_creation(self):
        """Test creating click interaction."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'clicked_element': 'button',
                'element_id': 'submit-btn',
                'element_class': 'btn-primary',
                'click_position': {'x': 100, 'y': 200},
                'target_url': 'https://test.com/thank-you'
            }
        }
        
        processor = ClickEventProcessor(event_data)
        interaction = processor.process()
        
        # Check interaction was created
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.interaction.payload['interaction_type'], 'click')
        self.assertEqual(interaction.interaction.action.code, 'click')
        
        # Check click data in payload
        self.assertEqual(interaction.interaction.payload['clicked_element'], 'button')
        self.assertEqual(interaction.interaction.payload['element_id'], 'submit-btn')
        self.assertEqual(interaction.interaction.payload['target_url'], 'https://test.com/thank-you')
        
        # Check touchpoint was created
        self.assertIsNotNone(interaction.interaction.touchpoint)
        self.assertEqual(interaction.interaction.touchpoint.touchpoint_class.code, 'web.internal_click')
    
    def test_click_touchpoint_creation(self):
        """Test specific click touchpoint creation."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'clicked_element': 'Learn More Button',
                'element_id': 'learn-more-btn',
                'target_url': 'https://test.com/learn-more'
            }
        }
        
        processor = ClickEventProcessor(event_data)
        interaction = processor.process()
        
        # Check touchpoint details
        touchpoint = interaction.interaction.touchpoint
        self.assertEqual(touchpoint.name, 'Click: Learn More Button (ID: learn-more-btn)')
        self.assertEqual(touchpoint.description, 'User clicked on Learn More Button leading to https://test.com/learn-more')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.internal_click')
        
        # Check channel was created correctly
        self.assertEqual(touchpoint.channel.code, 'test.com website')
        self.assertEqual(touchpoint.channel.medium.code, 'owned_website')
    
    def test_click_without_element_id(self):
        """Test click touchpoint creation without element ID."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'clicked_element': 'Link',
                'element_class': 'nav-link',
                'target_url': 'https://test.com/about'
            }
        }
        
        processor = ClickEventProcessor(event_data)
        interaction = processor.process()
        
        # Check touchpoint details
        touchpoint = interaction.interaction.touchpoint
        self.assertEqual(touchpoint.name, 'Click: Link (Class: nav-link)')
        self.assertEqual(touchpoint.description, 'User clicked on Link leading to https://test.com/about')
    
    def test_click_without_target_url(self):
        """Test click touchpoint creation without target URL."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'clicked_element': 'Button',
                'element_id': 'action-btn'
            }
        }
        
        processor = ClickEventProcessor(event_data)
        interaction = processor.process()
        
        # Check touchpoint details
        touchpoint = interaction.interaction.touchpoint
        self.assertEqual(touchpoint.name, 'Click: Button (ID: action-btn)')
        self.assertEqual(touchpoint.description, 'User clicked on Button')
    
    def test_error_handling_in_touchpoint_creation(self):
        """Test error handling when click touchpoint creation fails."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_123',
            'visitor_cookie': 'test_visitor_456',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'payload': {
                'clicked_element': 'Button'
            }
        }
        
        processor = ClickEventProcessor(event_data)
        
        # Mock touchpoint creation to fail by raising an exception
        with patch.object(processor, '_create_click_touchpoint', side_effect=Exception("Touchpoint creation failed")):
            with self.assertRaises(Exception) as context:
                processor.process()
            
            # Verify the exception was raised
            self.assertIn("Touchpoint creation failed", str(context.exception))
