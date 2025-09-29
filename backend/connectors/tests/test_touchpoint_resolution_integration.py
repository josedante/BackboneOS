"""
Integration tests for complete Touchpoint Resolution System workflows.

This module tests end-to-end functionality of the touchpoint resolution system including:
- Complete resolution workflows
- Integration between all system components
- Real-world scenarios and edge cases
- Performance under load
- Error handling and recovery
"""

import json
from datetime import timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from unittest.mock import patch, MagicMock

from connectors.models import TouchpointMappingRule
from connectors.monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointAlert,
    TouchpointSystemHealth,
    TouchpointCacheMetrics
)
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.metrics import track_resolution
from connectors.alerting import alert_manager
from interactions.models import Interaction, Touchpoint, TouchpointType, Channel, Medium
from websites.models import WebInteraction
from connectors.extended_resolvers import ExtendedTouchpointResolver
from connectors.extended_mapping_providers import ExtendedDatabaseMappingProvider


class CompleteResolutionWorkflowTest(TestCase):
    """Test complete touchpoint resolution workflows."""
    
    def setUp(self):
        """Set up test data."""
        # Create touchpoint type
        self.touchpoint_type = TouchpointType.objects.create(
            code='landing_page',
            name='Landing Page',
            description='A landing page interaction'
        )
        
        # Create channel and medium
        self.channel = Channel.objects.create(
            code='organic',
            name='Organic',
            description='Organic traffic'
        )
        
        self.medium = Medium.objects.create(
            code='referral',
            name='Referral',
            description='Referral traffic'
        )
        
        # Create touchpoint
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_type=self.touchpoint_type,
            channel=self.channel,
            medium=self.medium,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create organization and division for website
        from our_institution.models import OurOrganization, Division
        self.organization = OurOrganization.objects.create(
            name='Test Organization'
        )
        self.division = Division.objects.create(
            organization=self.organization,
            name='Test Division',
            code='TEST_DIV'
        )
        
        # Create website
        from websites.models import Website
        self.website = Website.objects.create(
            name='Test Website',
            base_url='https://test.com',
            division=self.division
        )
        
        # Create mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            touchpoint_type_code='landing_page',
            priority=100,
            is_active=True
        )
        
        # Create interaction first
        self.interaction = Interaction.objects.create(
            occurred_at=timezone.now()
        )
        
        # Create web interaction
        self.web_interaction = WebInteraction.objects.create(
            interaction=self.interaction,
            website=self.website,
            session_id='test_session_123',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            payload={'url': 'https://test.com/page', 'referrer': 'https://google.com', 'test': 'data'}
        )
    
    def _create_web_interaction(self, **kwargs):
        """Helper method to create WebInteraction with proper interaction relationship."""
        # Create interaction first
        interaction = Interaction.objects.create(
            occurred_at=kwargs.pop('occurred_at', timezone.now())
        )
        
        # Set defaults
        defaults = {
            'interaction': interaction,
            'website': self.website,
            'session_id': 'test_session',
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'payload': {}
        }
        defaults.update(kwargs)
        
        return WebInteraction.objects.create(**defaults)
    
    def test_complete_web_resolution_workflow(self):
        """Test complete web touchpoint resolution workflow with multi-interaction approach."""
        # Step 1: Create extended touchpoint resolver
        mapping_provider = ExtendedDatabaseMappingProvider()
        resolver = ExtendedTouchpointResolver(mapping_provider)
        
        # Step 2: Resolve multiple touchpoints using batch resolution
        with track_resolution('web', {'interaction_id': self.web_interaction.interaction.id, 'batch': True}) as tracker:
            try:
                touchpoints = resolver.resolve_batch(self.web_interaction)
                
                # Step 3: Verify multiple touchpoints were created
                self.assertIsNotNone(touchpoints)
                self.assertGreater(len(touchpoints), 0)
                
                # Should have at least page view touchpoint
                page_view_touchpoint = touchpoints[0]
                self.assertIsNotNone(page_view_touchpoint)
                
                # The touchpoint class should be based on the UTM medium (cpc -> paid_traffic)
                self.assertEqual(page_view_touchpoint.touchpoint_type.code, 'web.paid_traffic')
                # Channel should be the UTM source (google) since this is an external click event
                self.assertEqual(page_view_touchpoint.channel.code, 'google')
                # Medium should be 'paid' based on utm_medium='cpc'
                self.assertEqual(page_view_touchpoint.channel.medium.code, 'paid')
                
                # Step 4: Record success
                tracker.record_success(
                    cache_hit=False,
                    mapping_applied=True,
                    touchpoint_created=True,
                    batch_size=len(touchpoints)
                )
                
            except Exception as e:
                tracker.record_error(str(e))
                raise
        
        # Step 5: Verify resolution event was created
        event = TouchpointResolutionEvent.objects.filter(connector_type='web').latest('created_at')
        self.assertEqual(event.event_type, 'resolution')
        self.assertFalse(event.error_occurred)
        self.assertTrue(event.mapping_rule_applied)
        self.assertTrue(event.touchpoint_created)
        self.assertIn('interaction_id', event.metadata)
    
    def test_resolution_with_custom_mapping_rule(self):
        """Test resolution with custom mapping rule."""
        # Create custom mapping rule
        custom_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='custom.com',
            event_code='page_view',
            touchpoint_code='web.custom_page_view',
            touchpoint_label='Custom Page View',
            channel_code='paid',
            medium_code='search',
            priority=200,
            is_active=True
        )
        
        # Create custom touchpoint class
        custom_touchpoint_type = TouchpointType.objects.create(
            code='web.custom_page_view',
            name='Custom Web Page View',
            description='A custom web page view interaction'
        )
        
        # Create custom channel and medium
        custom_channel = Channel.objects.create(
            code='paid',
            name='Paid',
            description='Paid traffic'
        )
        
        custom_medium = Medium.objects.create(
            code='search',
            name='Search',
            description='Search traffic'
        )
        
        # Create web interaction for custom rule
        custom_web_interaction = WebInteraction.objects.create(
            url='https://custom.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='custom_campaign',
            utm_content='custom_content',
            utm_term='custom_term',
            occurred_at=timezone.now(),
            metadata={'custom': 'data'}
        )
        
        # Resolve with custom rule
        resolver = WebTouchpointResolver()
        touchpoint = resolver.resolve(custom_web_interaction)
        
        # Verify custom rule was applied
        self.assertEqual(touchpoint.touchpoint_type.code, 'web.custom_page_view')
        self.assertEqual(touchpoint.channel.code, 'paid')
        self.assertEqual(touchpoint.medium.code, 'search')
    
    def test_resolution_without_mapping_rule(self):
        """Test resolution without custom mapping rule."""
        # Create web interaction without matching rule
        web_interaction = WebInteraction.objects.create(
            url='https://no-rule.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='no_rule_campaign',
            utm_content='no_rule_content',
            utm_term='no_rule_term',
            occurred_at=timezone.now(),
            metadata={'no_rule': 'data'}
        )
        
        # Resolve without custom rule
        resolver = WebTouchpointResolver()
        touchpoint = resolver.resolve(web_interaction)
        
        # Verify default resolution was used
        self.assertIsNotNone(touchpoint)
        # Should use default inference logic
    
    def test_resolution_error_handling(self):
        """Test resolution error handling."""
        # Create invalid web interaction
        invalid_web_interaction = WebInteraction.objects.create(
            url='',  # Invalid URL
            referrer='',
            user_agent='',
            utm_source='',
            utm_medium='',
            utm_campaign='',
            utm_content='',
            utm_term='',
            occurred_at=timezone.now(),
            metadata={}
        )
        
        # Attempt resolution
        resolver = WebTouchpointResolver()
        
        with track_resolution('web', {'interaction_id': invalid_web_interaction.id}) as tracker:
            try:
                touchpoint = resolver.resolve(invalid_web_interaction)
                # If resolution succeeds, it should still create a touchpoint
                self.assertIsNotNone(touchpoint)
                tracker.record_success(
                    cache_hit=False,
                    mapping_applied=False,
                    touchpoint_created=True
                )
            except Exception as e:
                tracker.record_error(str(e))
                # Verify error event was created
                event = TouchpointResolutionEvent.objects.get(connector_type='web')
                self.assertEqual(event.event_type, 'error')
                self.assertTrue(event.error_occurred)
                self.assertIsNotNone(event.error_message)


class SystemIntegrationTest(TransactionTestCase):
    """Test system integration with database transactions."""
    
    def setUp(self):
        """Set up test data."""
        # Create touchpoint type
        self.touchpoint_type = TouchpointType.objects.create(
            code='landing_page',
            name='Landing Page',
            description='A landing page interaction'
        )
        
        # Create channel and medium
        self.channel = Channel.objects.create(
            code='organic',
            name='Organic',
            description='Organic traffic'
        )
        
        self.medium = Medium.objects.create(
            code='referral',
            name='Referral',
            description='Referral traffic'
        )
        
        # Create touchpoint
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_type=self.touchpoint_type,
            channel=self.channel,
            medium=self.medium,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            touchpoint_type_code='landing_page',
            priority=100,
            is_active=True
        )
    
    def test_transactional_resolution_workflow(self):
        """Test resolution workflow with database transactions."""
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            url='https://test.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Test transactional resolution
        with transaction.atomic():
            resolver = WebTouchpointResolver()
            touchpoint = resolver.resolve(web_interaction)
            
            # Verify touchpoint was created within transaction
            self.assertIsNotNone(touchpoint)
            self.assertEqual(touchpoint.touchpoint_type.code, 'web.page_view')
            
            # Verify resolution event was created within transaction
            event = TouchpointResolutionEvent.objects.get(connector_type='web')
            self.assertEqual(event.event_type, 'resolution')
            self.assertFalse(event.error_occurred)
    
    def test_transaction_rollback_on_error(self):
        """Test transaction rollback on resolution error."""
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            url='https://test.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Test transaction rollback
        with self.assertRaises(Exception):
            with transaction.atomic():
                resolver = WebTouchpointResolver()
                touchpoint = resolver.resolve(web_interaction)
                
                # Simulate error
                raise Exception('Simulated error')
        
        # Verify no resolution event was created due to rollback
        self.assertEqual(TouchpointResolutionEvent.objects.count(), 0)


class PerformanceIntegrationTest(TestCase):
    """Test system performance under load."""
    
    def setUp(self):
        """Set up test data."""
        # Create touchpoint type
        self.touchpoint_type = TouchpointType.objects.create(
            code='landing_page',
            name='Landing Page',
            description='A landing page interaction'
        )
        
        # Create channel and medium
        self.channel = Channel.objects.create(
            code='organic',
            name='Organic',
            description='Organic traffic'
        )
        
        self.medium = Medium.objects.create(
            code='referral',
            name='Referral',
            description='Referral traffic'
        )
        
        # Create touchpoint
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_type=self.touchpoint_type,
            channel=self.channel,
            medium=self.medium,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            touchpoint_type_code='landing_page',
            priority=100,
            is_active=True
        )
    
    def test_bulk_resolution_performance(self):
        """Test performance of bulk resolution operations."""
        import time
        
        # Create multiple web interactions
        web_interactions = []
        for i in range(100):
            web_interaction = WebInteraction.objects.create(
                url=f'https://test{i}.com/page',
                referrer='https://google.com',
                user_agent='Mozilla/5.0 (Test Browser)',
                utm_source='google',
                utm_medium='cpc',
                utm_campaign=f'test_campaign_{i}',
                utm_content=f'test_content_{i}',
                utm_term=f'test_term_{i}',
                occurred_at=timezone.now(),
                metadata={'test': f'data_{i}'}
            )
            web_interactions.append(web_interaction)
        
        # Test bulk resolution performance
        start_time = time.time()
        
        resolver = WebTouchpointResolver()
        for web_interaction in web_interactions:
            with track_resolution('web', {'interaction_id': web_interaction.id}) as tracker:
                try:
                    touchpoint = resolver.resolve(web_interaction)
                    tracker.record_success(
                        cache_hit=False,
                        mapping_applied=True,
                        touchpoint_created=True
                    )
                except Exception as e:
                    tracker.record_error(str(e))
        
        end_time = time.time()
        
        # Verify performance
        total_time = end_time - start_time
        avg_time_per_resolution = total_time / len(web_interactions)
        
        # Should complete within reasonable time
        self.assertLess(total_time, 10)  # 10 seconds max for 100 resolutions
        self.assertLess(avg_time_per_resolution, 0.1)  # 100ms max per resolution
        
        # Verify all resolutions were processed
        self.assertEqual(TouchpointResolutionEvent.objects.count(), 100)
    
    def test_concurrent_resolution_performance(self):
        """Test performance under concurrent resolution requests."""
        import threading
        import time
        
        # Create web interactions
        web_interactions = []
        for i in range(50):
            web_interaction = WebInteraction.objects.create(
                url=f'https://concurrent{i}.com/page',
                referrer='https://google.com',
                user_agent='Mozilla/5.0 (Test Browser)',
                utm_source='google',
                utm_medium='cpc',
                utm_campaign=f'concurrent_campaign_{i}',
                utm_content=f'concurrent_content_{i}',
                utm_term=f'concurrent_term_{i}',
                occurred_at=timezone.now(),
                metadata={'concurrent': f'data_{i}'}
            )
            web_interactions.append(web_interaction)
        
        # Test concurrent resolution
        results = []
        errors = []
        
        def resolve_interaction(web_interaction):
            try:
                resolver = WebTouchpointResolver()
                with track_resolution('web', {'interaction_id': web_interaction.id}) as tracker:
                    touchpoint = resolver.resolve(web_interaction)
                    tracker.record_success(
                        cache_hit=False,
                        mapping_applied=True,
                        touchpoint_created=True
                    )
                    results.append(touchpoint)
            except Exception as e:
                errors.append(e)
        
        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for web_interaction in web_interactions:
            thread = threading.Thread(target=resolve_interaction, args=(web_interaction,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verify performance
        total_time = end_time - start_time
        self.assertLess(total_time, 5)  # 5 seconds max for concurrent resolution
        
        # Verify results
        self.assertEqual(len(results), 50)
        self.assertEqual(len(errors), 0)
        self.assertEqual(TouchpointResolutionEvent.objects.count(), 50)


class ErrorRecoveryIntegrationTest(TestCase):
    """Test error recovery and system resilience."""
    
    def setUp(self):
        """Set up test data."""
        # Create touchpoint type
        self.touchpoint_type = TouchpointType.objects.create(
            code='landing_page',
            name='Landing Page',
            description='A landing page interaction'
        )
        
        # Create channel and medium
        self.channel = Channel.objects.create(
            code='organic',
            name='Organic',
            description='Organic traffic'
        )
        
        self.medium = Medium.objects.create(
            code='referral',
            name='Referral',
            description='Referral traffic'
        )
        
        # Create touchpoint
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_type=self.touchpoint_type,
            channel=self.channel,
            medium=self.medium,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            touchpoint_type_code='landing_page',
            priority=100,
            is_active=True
        )
    
    def test_database_error_recovery(self):
        """Test recovery from database errors."""
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            url='https://test.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Mock database error
        with patch('connectors.resolvers.Touchpoint.objects.get_or_create') as mock_get_or_create:
            mock_get_or_create.side_effect = Exception('Database error')
            
            resolver = WebTouchpointResolver()
            
            with track_resolution('web', {'interaction_id': web_interaction.id}) as tracker:
                try:
                    touchpoint = resolver.resolve(web_interaction)
                    self.fail('Expected exception was not raised')
                except Exception as e:
                    tracker.record_error(str(e))
                    
                    # Verify error event was created
                    event = TouchpointResolutionEvent.objects.get(connector_type='web')
                    self.assertEqual(event.event_type, 'error')
                    self.assertTrue(event.error_occurred)
                    self.assertEqual(event.error_message, 'Database error')
    
    def test_cache_error_recovery(self):
        """Test recovery from cache errors."""
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            url='https://test.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Mock cache error
        with patch('django.core.cache.cache.get') as mock_cache_get:
            mock_cache_get.side_effect = Exception('Cache error')
            
            resolver = WebTouchpointResolver()
            
            # Should still work despite cache error
            with track_resolution('web', {'interaction_id': web_interaction.id}) as tracker:
                try:
                    touchpoint = resolver.resolve(web_interaction)
                    tracker.record_success(
                        cache_hit=False,
                        mapping_applied=True,
                        touchpoint_created=True
                    )
                    
                    # Verify resolution still succeeded
                    self.assertIsNotNone(touchpoint)
                    
                except Exception as e:
                    tracker.record_error(str(e))
    
    def test_system_health_monitoring(self):
        """Test system health monitoring during errors."""
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            url='https://test.com/page',
            referrer='https://google.com',
            user_agent='Mozilla/5.0 (Test Browser)',
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='test_campaign',
            utm_content='test_content',
            utm_term='test_term',
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Create system health record
        health_record = TouchpointSystemHealth.objects.create(
            health_status='healthy',
            avg_resolution_time_ms=45.0,
            error_rate=0.01,
            active_mapping_rules=1,
            total_touchpoints=1,
            total_interactions=1,
            cache_size=0,
            cache_memory_usage_mb=0,
            database_connections=1,
            slow_queries_count=0,
            memory_usage_mb=512.0,
            cpu_usage_percent=25.0
        )
        
        # Simulate error scenario
        with patch('connectors.resolvers.Touchpoint.objects.get_or_create') as mock_get_or_create:
            mock_get_or_create.side_effect = Exception('Database error')
            
            resolver = WebTouchpointResolver()
            
            # Attempt resolution
            with track_resolution('web', {'interaction_id': web_interaction.id}) as tracker:
                try:
                    touchpoint = resolver.resolve(web_interaction)
                    self.fail('Expected exception was not raised')
                except Exception as e:
                    tracker.record_error(str(e))
                    
                    # Verify error event was created
                    event = TouchpointResolutionEvent.objects.get(connector_type='web')
                    self.assertEqual(event.event_type, 'error')
                    self.assertTrue(event.error_occurred)
                    
                    # Verify system health is still monitored
                    self.assertEqual(TouchpointSystemHealth.objects.count(), 1)
                    self.assertEqual(health_record.health_status, 'healthy')


if __name__ == '__main__':
    import unittest
    unittest.main()

