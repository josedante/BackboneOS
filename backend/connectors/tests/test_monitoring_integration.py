"""
Integration tests for Touchpoint Resolution System monitoring and metrics.

This module tests end-to-end functionality of the monitoring system including:
- Metrics collection and storage
- Alert generation and management
- Performance monitoring
- System health tracking
- Data retention and cleanup
"""

import json
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from connectors.models import TouchpointMappingRule
from connectors.monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointAlert,
    TouchpointSystemHealth,
    TouchpointCacheMetrics
)
from connectors.metrics import track_resolution, ResolutionTracker
from connectors.alerting import alert_manager
from connectors.retention_policies import TouchpointRetentionPolicies
from interactions.models import Interaction, Touchpoint, TouchpointType, Channel, Medium


class MetricsCollectionIntegrationTest(TestCase):
    """Test metrics collection integration with the system."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
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
    
    def test_track_resolution_context_manager(self):
        """Test the track_resolution context manager."""
        # Test successful resolution tracking
        with track_resolution('web', {'test': 'data'}) as tracker:
            tracker.record_success(
                cache_hit=False,
                mapping_applied=True,
                touchpoint_created=True
            )
        
        # Verify event was created
        event = TouchpointResolutionEvent.objects.get(connector_type='web')
        self.assertEqual(event.event_type, 'resolution')
        self.assertFalse(event.error_occurred)
        self.assertTrue(event.mapping_rule_applied)
        self.assertTrue(event.touchpoint_created)
        self.assertIn('test', event.metadata)
    
    def test_track_resolution_error_handling(self):
        """Test error handling in track_resolution context manager."""
        # Test error tracking
        with self.assertRaises(ValueError):
            with track_resolution('web', {'test': 'data'}) as tracker:
                tracker.record_error('Test error', 'ValueError')
                raise ValueError('Test error')
        
        # Verify error event was created
        event = TouchpointResolutionEvent.objects.get(connector_type='web')
        self.assertEqual(event.event_type, 'error')
        self.assertTrue(event.error_occurred)
        self.assertEqual(event.error_message, 'Test error')
        self.assertEqual(event.error_type, 'ValueError')
    
    def test_resolution_tracker_methods(self):
        """Test ResolutionTracker methods."""
        tracker = ResolutionTracker({'connector_type': 'web'})
        
        # Test success recording
        tracker.record_success(
            cache_hit=True,
            mapping_applied=False,
            touchpoint_created=True
        )
        
        self.assertEqual(tracker.event_data['event_type'], 'resolution')
        self.assertTrue(tracker.event_data['cache_hit'])
        self.assertFalse(tracker.event_data['mapping_rule_applied'])
        self.assertTrue(tracker.event_data['touchpoint_created'])
        self.assertFalse(tracker.event_data['error_occurred'])
        
        # Test error recording
        tracker.record_error('Test error', 'TestError')
        
        self.assertEqual(tracker.event_data['event_type'], 'error')
        self.assertTrue(tracker.event_data['error_occurred'])
        self.assertEqual(tracker.event_data['error_message'], 'Test error')
        self.assertEqual(tracker.event_data['error_type'], 'TestError')
    
    def test_metrics_aggregation(self):
        """Test metrics aggregation from events."""
        # Create multiple resolution events
        now = timezone.now()
        for i in range(10):
            TouchpointResolutionEvent.objects.create(
                connector_type='web',
                event_type='resolution',
                touchpoint_code='web.page_view',
                resolution_time_ms=45.0 + i,
                cache_hit=i % 2 == 0,
                mapping_rule_applied=True,
                touchpoint_created=True,
                error_occurred=False,
                occurred_at=now - timedelta(minutes=i)
            )
        
        # Create some error events
        for i in range(2):
            TouchpointResolutionEvent.objects.create(
                connector_type='web',
                event_type='error',
                touchpoint_code='web.page_view',
                resolution_time_ms=0,
                cache_hit=False,
                mapping_rule_applied=False,
                touchpoint_created=False,
                error_occurred=True,
                error_message='Test error',
                error_type='TestError',
                occurred_at=now - timedelta(minutes=i)
            )
        
        # Test metrics calculation
        events = TouchpointResolutionEvent.objects.filter(connector_type='web')
        total_events = events.count()
        successful_events = events.filter(error_occurred=False).count()
        failed_events = events.filter(error_occurred=True).count()
        
        self.assertEqual(total_events, 12)
        self.assertEqual(successful_events, 10)
        self.assertEqual(failed_events, 2)
        
        # Test success rate calculation
        success_rate = (successful_events / total_events) * 100
        self.assertEqual(success_rate, 83.33)  # 10/12 * 100


class AlertingSystemIntegrationTest(TestCase):
    """Test alerting system integration."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_alert_creation(self):
        """Test alert creation and management."""
        # Create an alert
        alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='High Resolution Time',
            message='Average resolution time exceeded threshold',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
        
        self.assertEqual(alert.alert_type, 'performance')
        self.assertEqual(alert.severity, 'warning')
        self.assertEqual(alert.status, 'active')
        self.assertIsNotNone(alert.triggered_at)
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment workflow."""
        alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='Test Alert',
            message='This is a test alert',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
        
        # Acknowledge the alert
        alert.acknowledge()
        
        self.assertEqual(alert.status, 'acknowledged')
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_alert_resolution(self):
        """Test alert resolution workflow."""
        alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='Test Alert',
            message='This is a test alert',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
        
        # Resolve the alert
        alert.resolve()
        
        self.assertEqual(alert.status, 'resolved')
        self.assertIsNotNone(alert.resolved_at)
    
    def test_alert_dismissal(self):
        """Test alert dismissal workflow."""
        alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='Test Alert',
            message='This is a test alert',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
        
        # Dismiss the alert
        alert.dismiss()
        
        self.assertEqual(alert.status, 'dismissed')
        self.assertIsNotNone(alert.dismissed_at)
    
    def test_alert_manager_integration(self):
        """Test alert manager integration."""
        # Test getting active alerts
        active_alerts = alert_manager.get_active_alerts()
        self.assertEqual(len(active_alerts), 0)
        
        # Create an active alert
        alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='Test Alert',
            message='This is a test alert',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
        
        # Test getting active alerts
        active_alerts = alert_manager.get_active_alerts()
        self.assertEqual(len(active_alerts), 1)
        self.assertEqual(active_alerts[0].id, alert.id)
        
        # Test getting alert summary
        summary = alert_manager.get_alert_summary()
        self.assertIn('active', summary)
        self.assertEqual(summary['active'], 1)


class SystemHealthIntegrationTest(TestCase):
    """Test system health monitoring integration."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_system_health_record_creation(self):
        """Test system health record creation."""
        health_record = TouchpointSystemHealth.objects.create(
            health_status='healthy',
            avg_resolution_time_ms=45.0,
            error_rate=0.02,
            active_mapping_rules=5,
            total_touchpoints=100,
            total_interactions=1000,
            cache_size=50,
            cache_memory_usage_mb=10.5,
            database_connections=5,
            slow_queries_count=0,
            memory_usage_mb=512.0,
            cpu_usage_percent=25.0
        )
        
        self.assertEqual(health_record.health_status, 'healthy')
        self.assertEqual(health_record.avg_resolution_time_ms, 45.0)
        self.assertEqual(health_record.error_rate, 0.02)
        self.assertIsNotNone(health_record.recorded_at)
    
    def test_health_status_calculation(self):
        """Test health status calculation based on metrics."""
        # Create health record with good metrics
        good_health = TouchpointSystemHealth.objects.create(
            health_status='healthy',
            avg_resolution_time_ms=45.0,
            error_rate=0.01,
            active_mapping_rules=5,
            total_touchpoints=100,
            total_interactions=1000,
            cache_size=50,
            cache_memory_usage_mb=10.5,
            database_connections=5,
            slow_queries_count=0,
            memory_usage_mb=512.0,
            cpu_usage_percent=25.0
        )
        
        self.assertEqual(good_health.health_status, 'healthy')
        
        # Create health record with poor metrics
        poor_health = TouchpointSystemHealth.objects.create(
            health_status='unhealthy',
            avg_resolution_time_ms=500.0,
            error_rate=0.15,
            active_mapping_rules=5,
            total_touchpoints=100,
            total_interactions=1000,
            cache_size=50,
            cache_memory_usage_mb=10.5,
            database_connections=5,
            slow_queries_count=5,
            memory_usage_mb=1024.0,
            cpu_usage_percent=90.0
        )
        
        self.assertEqual(poor_health.health_status, 'unhealthy')


class CacheMetricsIntegrationTest(TestCase):
    """Test cache metrics integration."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_cache_metrics_record_creation(self):
        """Test cache metrics record creation."""
        cache_metrics = TouchpointCacheMetrics.objects.create(
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now(),
            total_operations=1000,
            get_operations=800,
            set_operations=150,
            delete_operations=50,
            cache_hits=720,
            cache_misses=80,
            avg_operation_time_ms=2.5,
            max_operation_time_ms=15.0,
            cache_size_at_start=100,
            cache_size_at_end=120,
            max_cache_size=150,
            key_pattern_breakdown={'touchpoint_mapping:*': 500, 'resolution:*': 300}
        )
        
        self.assertEqual(cache_metrics.total_operations, 1000)
        self.assertEqual(cache_metrics.get_operations, 800)
        self.assertEqual(cache_metrics.cache_hits, 720)
        self.assertEqual(cache_metrics.cache_misses, 80)
        
        # Test hit rate calculation
        hit_rate = (cache_metrics.cache_hits / cache_metrics.get_operations) * 100
        self.assertEqual(hit_rate, 90.0)  # 720/800 * 100
    
    def test_cache_performance_monitoring(self):
        """Test cache performance monitoring."""
        # Create cache metrics with good performance
        good_cache = TouchpointCacheMetrics.objects.create(
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now(),
            total_operations=1000,
            get_operations=800,
            set_operations=150,
            delete_operations=50,
            cache_hits=720,
            cache_misses=80,
            avg_operation_time_ms=2.5,
            max_operation_time_ms=15.0,
            cache_size_at_start=100,
            cache_size_at_end=120,
            max_cache_size=150
        )
        
        # Test hit rate
        hit_rate = (good_cache.cache_hits / good_cache.get_operations) * 100
        self.assertGreater(hit_rate, 80)  # Good hit rate
        
        # Test operation time
        self.assertLess(good_cache.avg_operation_time_ms, 10)  # Good performance


class DataRetentionIntegrationTest(TestCase):
    """Test data retention policies and cleanup integration."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
        )
    
    def test_retention_policies_configuration(self):
        """Test retention policies configuration."""
        # Test default retention policies
        default_policies = TouchpointRetentionPolicies.get_all_policies()
        
        self.assertIn('detailed_events', default_policies)
        self.assertIn('aggregated_metrics', default_policies)
        self.assertIn('resolved_alerts', default_policies)
        
        self.assertEqual(default_policies['detailed_events'], 90)
        self.assertEqual(default_policies['aggregated_metrics'], 365)
        self.assertEqual(default_policies['resolved_alerts'], 180)
    
    def test_retention_policy_environment_specific(self):
        """Test environment-specific retention policies."""
        # Test development environment policies
        dev_policies = TouchpointRetentionPolicies.DEVELOPMENT
        
        self.assertEqual(dev_policies['detailed_events'], 7)
        self.assertEqual(dev_policies['aggregated_metrics'], 30)
        self.assertEqual(dev_policies['resolved_alerts'], 30)
        
        # Test production environment policies
        prod_policies = TouchpointRetentionPolicies.PRODUCTION
        
        self.assertEqual(prod_policies['detailed_events'], 90)
        self.assertEqual(prod_policies['aggregated_metrics'], 365)
        self.assertEqual(prod_policies['resolved_alerts'], 180)
    
    def test_data_cleanup_integration(self):
        """Test data cleanup integration with retention policies."""
        # Create old events that should be cleaned up
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
        
        # Create recent events that should be kept
        recent_event = TouchpointResolutionEvent.objects.create(
            connector_type='web',
            event_type='resolution',
            touchpoint_code='web.page_view',
            resolution_time_ms=45.0,
            cache_hit=False,
            mapping_rule_applied=True,
            touchpoint_created=True,
            error_occurred=False,
            occurred_at=timezone.now() - timedelta(days=30)
        )
        
        # Test cleanup logic
        cutoff_date = timezone.now() - timedelta(days=90)
        old_events = TouchpointResolutionEvent.objects.filter(occurred_at__lt=cutoff_date)
        recent_events = TouchpointResolutionEvent.objects.filter(occurred_at__gte=cutoff_date)
        
        self.assertEqual(old_events.count(), 1)
        self.assertEqual(recent_events.count(), 1)
        
        # Verify the old event would be cleaned up
        self.assertEqual(old_events.first().id, old_event.id)
        
        # Verify the recent event would be kept
        self.assertEqual(recent_events.first().id, recent_event.id)


class MonitoringSystemEndToEndTest(TestCase):
    """Test end-to-end monitoring system functionality."""
    
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
            channel=self.channel,
            name='Test Touchpoint',
            code='test_touchpoint',
            description='Test touchpoint for integration tests'
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
    
    def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow from resolution to alerting."""
        # Step 1: Track a resolution
        with track_resolution('web', {'test': 'data'}) as tracker:
            tracker.record_success(
                cache_hit=False,
                mapping_applied=True,
                touchpoint_created=True
            )
        
        # Step 2: Verify event was created
        event = TouchpointResolutionEvent.objects.get(connector_type='web')
        self.assertEqual(event.event_type, 'resolution')
        self.assertFalse(event.error_occurred)
        
        # Step 3: Create system health record
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
        
        # Step 4: Verify health record
        self.assertEqual(health_record.health_status, 'healthy')
        
        # Step 5: Create cache metrics
        cache_metrics = TouchpointCacheMetrics.objects.create(
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now(),
            total_operations=100,
            get_operations=80,
            set_operations=15,
            delete_operations=5,
            cache_hits=70,
            cache_misses=10,
            avg_operation_time_ms=2.5,
            max_operation_time_ms=15.0,
            cache_size_at_start=0,
            cache_size_at_end=10,
            max_cache_size=15
        )
        
        # Step 6: Verify cache metrics
        self.assertEqual(cache_metrics.total_operations, 100)
        self.assertEqual(cache_metrics.cache_hits, 70)
        
        # Step 7: Create an alert if needed
        if health_record.error_rate > 0.05:  # 5% threshold
            alert = TouchpointAlert.objects.create(
                alert_type='performance',
                severity='warning',
                title='High Error Rate',
                message='Error rate exceeded threshold',
                connector_type='web',
                threshold_value=0.05,
                actual_value=health_record.error_rate,
                status='active'
            )
            
            self.assertEqual(alert.alert_type, 'performance')
            self.assertEqual(alert.status, 'active')
        
        # Step 8: Verify complete monitoring data
        self.assertEqual(TouchpointResolutionEvent.objects.count(), 1)
        self.assertEqual(TouchpointSystemHealth.objects.count(), 1)
        self.assertEqual(TouchpointCacheMetrics.objects.count(), 1)
        
        # Step 9: Test data retention
        retention_policies = TouchpointRetentionPolicies.get_all_policies()
        self.assertIn('detailed_events', retention_policies)
        self.assertEqual(retention_policies['detailed_events'], 90)


if __name__ == '__main__':
    import unittest
    unittest.main()

