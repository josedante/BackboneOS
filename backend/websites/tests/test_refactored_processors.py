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
from websites.refactored_processors import RefactoredPageViewEventProcessor
from our_institution.models import Division, OurOrganization


class RefactoredPageViewEventProcessorTestCase(TestCase):
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Should create 2 interactions (page view + referrer click)
        self.assertEqual(len(interactions), 2)
        
        # Check page view interaction
        page_view = interactions[0]
        self.assertEqual(page_view.interaction.payload['interaction_type'], 'page_view')
        
        # Check referrer click interaction
        referrer_click = interactions[1]
        self.assertEqual(referrer_click.interaction.payload['interaction_type'], 'referrer_click')
        self.assertEqual(referrer_click.interaction.action.code, 'external_click')
        
        # Check referrer touchpoint was created
        self.assertIsNotNone(referrer_click.interaction.touchpoint)
        self.assertEqual(referrer_click.interaction.touchpoint.touchpoint_class.code, 'web.external_click')
    
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check referrer click touchpoint
        referrer_click = interactions[1]  # Second interaction
        touchpoint = referrer_click.interaction.touchpoint
        
        self.assertEqual(touchpoint.name, 'Referrer: google.com')
        self.assertEqual(touchpoint.description, 'Click from https://google.com/search?q=test')
        self.assertEqual(touchpoint.url, 'https://google.com/search?q=test')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.external_click')
    
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check session start touchpoint
        session_start = interactions[1]  # Second interaction
        touchpoint = session_start.interaction.touchpoint
        
        self.assertEqual(touchpoint.name, 'Session Start: new_session_789')
        self.assertEqual(touchpoint.description, 'Session started with ID new_session_789')
        self.assertEqual(touchpoint.touchpoint_class.code, 'web.session_start')
    
    def test_external_referrer_detection(self):
        """Test external referrer detection logic."""
        processor = RefactoredPageViewEventProcessor({
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
        processor = RefactoredPageViewEventProcessor({
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
        
        processor = RefactoredPageViewEventProcessor({
            'website_base': 'https://test.com',
            'session_id': 'test_session_existing',
            'visitor_cookie': 'test_visitor_existing'
        })
        self.assertFalse(processor._should_start_new_session())
        
        # No session info
        processor = RefactoredPageViewEventProcessor({
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        
        # Mock an error during interaction creation
        with patch.object(processor, '_create_page_view_interaction', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                processor.process()
            
            # Verify no interactions were created
            self.assertEqual(len(processor.created_interactions), 0)
    
    def test_logging_functionality(self):
        """Test that logging works correctly."""
        event_data = {
            'website_base': 'https://test.com',
            'full_url': 'https://test.com/page1',
            'session_id': 'test_session_new_session',
            'visitor_cookie': 'test_visitor_new_session',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        processor = RefactoredPageViewEventProcessor(event_data)
        
        # Test successful processing
        with self.assertLogs(logger='websites.refactored_processors', level='INFO') as log:
            interactions = processor.process()
            
            # Check that success log was created
            self.assertTrue(any('Successfully created' in message for message in log.output))
    
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check that agent was created correctly
        agent = interactions[0].interaction.agent
        self.assertIsInstance(agent, WebAgent)
        self.assertEqual(agent.agent_type, 'browser')
        
        # Check that metadata was stored
        self.assertIn('browser', agent.metadata)
        self.assertIn('os', agent.metadata)
        self.assertIn('device', agent.metadata)
    
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
        
        processor = RefactoredPageViewEventProcessor(event_data)
        interactions = processor.process()
        
        # Check that website was created
        self.assertIsNotNone(processor.website)
        self.assertEqual(processor.website.base_url, 'https://newtest.com')
        
        # Check that default division was created
        default_division = Division.objects.filter(code='DEFAULT').first()
        self.assertIsNotNone(default_division)
        self.assertEqual(processor.website.division, default_division)
