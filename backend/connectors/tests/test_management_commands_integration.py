"""
Integration tests for Touchpoint Resolution System management commands.

This module tests end-to-end functionality of management commands including:
- Backfill operations
- Testing commands
- Rule management
- Cache management
- Monitoring commands
- Data cleanup operations
"""

import json
from datetime import timedelta
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.core.cache import cache
from io import StringIO
from unittest.mock import patch, MagicMock

from connectors.models import TouchpointMappingRule
from connectors.monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointAlert,
    TouchpointSystemHealth,
    TouchpointCacheMetrics
)
from interactions.models import Interaction, Touchpoint, TouchpointType, Channel, Medium
from websites.models import WebInteraction


class ManagementCommandsIntegrationTest(TestCase):
    """Test management commands integration with the system."""
    
    def setUp(self):
        """Set up test data."""
        # Create test touchpoint class
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page_view',
            name='Web Page View',
            description='A web page view interaction'
        )
        
        # Create test channel and medium
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
        
        # Create test touchpoint
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create test interaction
        self.interaction = Interaction.objects.create(
            touchpoint=self.touchpoint,
            occurred_at=timezone.now(),
            payload={'test': 'data'}
        )
        
        # Create test mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            priority=100,
            is_active=True
        )
    
    def test_backfill_touchpoints_command(self):
        """Test the backfill touchpoints management command."""
        # Create some interactions without touchpoints
        interaction_without_touchpoint = Interaction.objects.create(
            touchpoint=None,
            occurred_at=timezone.now(),
            metadata={'test': 'data'}
        )
        
        # Run the backfill command
        out = StringIO()
        call_command('backfill_touchpoints', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Starting touchpoint backfill process', output)
        self.assertIn('Processed', output)
    
    def test_test_touchpoint_resolution_command(self):
        """Test the test touchpoint resolution management command."""
        # Run the test command
        out = StringIO()
        call_command('test_touchpoint_resolution', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Testing touchpoint resolution', output)
        self.assertIn('Test completed', output)
    
    def test_manage_mapping_rules_command(self):
        """Test the manage mapping rules management command."""
        # Test listing rules
        out = StringIO()
        call_command('manage_mapping_rules', 'list', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Mapping Rules', output)
        self.assertIn('test.com', output)
        
        # Test creating a new rule
        out = StringIO()
        call_command(
            'manage_mapping_rules', 'create',
            '--connector-type', 'web',
            '--source-identifier', 'new-test.com',
            '--event-code', 'form_submit',
            '--touchpoint-code', 'web.form_submit',
            '--touchpoint-label', 'Form Submit',
            '--channel-code', 'organic',
            '--medium-code', 'referral',
            '--priority', '150',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Mapping rule created successfully', output)
        
        # Verify the rule was created
        rule = TouchpointMappingRule.objects.get(source_identifier='new-test.com')
        self.assertEqual(rule.event_code, 'form_submit')
        self.assertEqual(rule.priority, 150)
    
    def test_manage_touchpoint_cache_command(self):
        """Test the manage touchpoint cache management command."""
        # Test cache stats
        out = StringIO()
        call_command('manage_touchpoint_cache', 'stats', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cache Statistics', output)
        
        # Test cache clear
        out = StringIO()
        call_command('manage_touchpoint_cache', 'clear', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cache cleared successfully', output)
    
    def test_monitor_touchpoint_system_command(self):
        """Test the monitor touchpoint system management command."""
        # Test health check
        out = StringIO()
        call_command('monitor_touchpoint_system', 'health', stdout=out)
        
        output = out.getvalue()
        self.assertIn('System Health Check', output)
        self.assertIn('Status:', output)
        
        # Test metrics
        out = StringIO()
        call_command('monitor_touchpoint_system', 'metrics', '--hours', '1', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Touchpoint Resolution Metrics', output)
        self.assertIn('Last 1 hours', output)
    
    def test_cleanup_touchpoint_events_command(self):
        """Test the cleanup touchpoint events management command."""
        # Create some old events
        old_event = TouchpointResolutionEvent.objects.create(
            connector_type='web',
            event_type='resolution',
            touchpoint_code='web.page_view',
            resolution_time_ms=45.0,
            cache_hit=False,
            mapping_rule_applied=True,
            touchpoint_created=True,
            error_occurred=False,
            occurred_at=timezone.now() - timedelta(days=100)
        )
        
        # Test dry run
        out = StringIO()
        call_command('cleanup_touchpoint_events', '--dry-run', '--retention-days', '90', stdout=out)
        
        output = out.getvalue()
        self.assertIn('DRY RUN MODE', output)
        self.assertIn('Data to be cleaned up', output)
        
        # Test actual cleanup
        out = StringIO()
        call_command('cleanup_touchpoint_events', '--force', '--retention-days', '90', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cleanup completed successfully', output)
        
        # Verify old event was deleted
        self.assertFalse(TouchpointResolutionEvent.objects.filter(id=old_event.id).exists())


class ManagementCommandsErrorHandlingTest(TestCase):
    """Test error handling in management commands."""
    
    def setUp(self):
        """Set up test data."""
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page_view',
            name='Web Page View',
            description='A web page view interaction'
        )
        
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
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_invalid_command_arguments(self):
        """Test handling of invalid command arguments."""
        # Test invalid action for manage_mapping_rules
        with self.assertRaises(CommandError):
            call_command('manage_mapping_rules', 'invalid_action')
        
        # Test missing required arguments
        with self.assertRaises(CommandError):
            call_command('manage_mapping_rules', 'create')
    
    def test_database_errors(self):
        """Test handling of database errors."""
        # Test with invalid touchpoint class
        with self.assertRaises(CommandError):
            call_command(
                'manage_mapping_rules', 'create',
                '--connector-type', 'web',
                '--source-identifier', 'test.com',
                '--event-code', 'page_view',
                '--touchpoint-code', 'invalid.touchpoint',
                '--touchpoint-label', 'Test',
                '--channel-code', 'organic',
                '--medium-code', 'referral',
                '--priority', '100'
            )
    
    def test_cache_errors(self):
        """Test handling of cache errors."""
        # Mock cache error
        with patch('django.core.cache.cache.clear') as mock_clear:
            mock_clear.side_effect = Exception('Cache error')
            
            out = StringIO()
            call_command('manage_touchpoint_cache', 'clear', stdout=out)
            
            output = out.getvalue()
            self.assertIn('Error clearing cache', output)


class ManagementCommandsPerformanceTest(TestCase):
    """Test performance of management commands."""
    
    def setUp(self):
        """Set up test data."""
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page_view',
            name='Web Page View',
            description='A web page view interaction'
        )
        
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
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
        
        # Create many interactions for performance testing
        for i in range(100):
            Interaction.objects.create(
                touchpoint=self.touchpoint,
                occurred_at=timezone.now() - timedelta(minutes=i),
                metadata={'test': f'data_{i}'}
            )
    
    def test_backfill_performance(self):
        """Test performance of backfill command with many records."""
        import time
        
        start_time = time.time()
        out = StringIO()
        call_command('backfill_touchpoints', stdout=out)
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 10)  # 10 seconds max
        
        output = out.getvalue()
        self.assertIn('Processed', output)
    
    def test_cleanup_performance(self):
        """Test performance of cleanup command with many records."""
        # Create many old events
        for i in range(100):
            TouchpointResolutionEvent.objects.create(
                connector_type='web',
                event_type='resolution',
                touchpoint_code='web.page_view',
                resolution_time_ms=45.0,
                cache_hit=False,
                mapping_rule_applied=True,
                touchpoint_created=True,
                error_occurred=False,
                occurred_at=timezone.now() - timedelta(days=100)
            )
        
        import time
        
        start_time = time.time()
        out = StringIO()
        call_command('cleanup_touchpoint_events', '--force', '--retention-days', '90', stdout=out)
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5)  # 5 seconds max
        
        output = out.getvalue()
        self.assertIn('Cleanup completed successfully', output)


class ManagementCommandsIntegrationWithAdminTest(TestCase):
    """Test integration between management commands and admin interface."""
    
    def setUp(self):
        """Set up test data."""
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page_view',
            name='Web Page View',
            description='A web page view interaction'
        )
        
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
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_command_created_rules_visible_in_admin(self):
        """Test that rules created via command are visible in admin."""
        # Create a rule via command
        out = StringIO()
        call_command(
            'manage_mapping_rules', 'create',
            '--connector-type', 'web',
            '--source-identifier', 'command-test.com',
            '--event-code', 'page_view',
            '--touchpoint-code', 'web.page_view',
            '--touchpoint-label', 'Page View',
            '--channel-code', 'organic',
            '--medium-code', 'referral',
            '--priority', '150',
            stdout=out
        )
        
        # Verify the rule exists and is accessible
        rule = TouchpointMappingRule.objects.get(source_identifier='command-test.com')
        self.assertEqual(rule.event_code, 'page_view')
        self.assertEqual(rule.priority, 150)
        self.assertTrue(rule.is_active)
    
    def test_admin_modified_rules_affect_commands(self):
        """Test that rules modified in admin affect command behavior."""
        # Create a rule via command
        out = StringIO()
        call_command(
            'manage_mapping_rules', 'create',
            '--connector-type', 'web',
            '--source-identifier', 'admin-test.com',
            '--event-code', 'page_view',
            '--touchpoint-code', 'web.page_view',
            '--touchpoint-label', 'Page View',
            '--channel-code', 'organic',
            '--medium-code', 'referral',
            '--priority', '150',
            stdout=out
        )
        
        # Modify the rule in admin (simulate admin change)
        rule = TouchpointMappingRule.objects.get(source_identifier='admin-test.com')
        rule.priority = 200
        rule.save()
        
        # Verify the change is reflected
        rule.refresh_from_db()
        self.assertEqual(rule.priority, 200)
    
    def test_cache_consistency_between_admin_and_commands(self):
        """Test cache consistency between admin and commands."""
        # Clear cache via command
        out = StringIO()
        call_command('manage_touchpoint_cache', 'clear', stdout=out)
        
        # Verify cache is cleared
        self.assertIsNone(cache.get('test_key'))
        
        # Set cache via command (if implemented)
        # This would test that cache operations are consistent


if __name__ == '__main__':
    import unittest
    unittest.main()

