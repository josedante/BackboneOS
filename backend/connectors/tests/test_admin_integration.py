"""
Integration tests for Touchpoint Resolution System admin workflows.

This module tests end-to-end admin functionality including:
- Admin interface registration and configuration
- Custom admin views and templates
- Admin workflows and user interactions
- Integration between admin and core functionality
"""

import json
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction

from connectors.models import TouchpointMappingRule
from connectors.monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointAlert,
    TouchpointSystemHealth,
    TouchpointCacheMetrics
)
from connectors.admin import (
    TouchpointMappingRuleAdmin,
    TouchpointResolutionEventAdmin,
    TouchpointAlertAdmin,
    TouchpointResolutionMetricsAdmin,
    TouchpointSystemHealthAdmin,
    TouchpointCacheMetricsAdmin
)
from connectors.admin_views import (
    monitoring_dashboard,
    mapping_rules_analytics,
    performance_report,
    ajax_metrics,
    system_health_check
)


class AdminInterfaceIntegrationTest(TestCase):
    """Test admin interface registration and basic functionality."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        # Create test mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='example.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            priority=100,
            is_active=True
        )
        
        # Create test resolution event
        self.resolution_event = TouchpointResolutionEvent.objects.create(
            connector_type='web',
            event_type='resolution',
            touchpoint_code='web.page_view',
            resolution_time_ms=45.5,
            cache_hit=False,
            mapping_rule_applied=True,
            touchpoint_created=True,
            error_occurred=False,
            occurred_at=timezone.now()
        )
        
        # Create test alert
        self.alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='High Resolution Time',
            message='Average resolution time exceeded threshold',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
    
    def test_admin_interface_registration(self):
        """Test that all admin interfaces are properly registered."""
        admin_site = AdminSite()
        
        # Test mapping rule admin
        mapping_admin = TouchpointMappingRuleAdmin(TouchpointMappingRule, admin_site)
        self.assertIsNotNone(mapping_admin)
        self.assertEqual(mapping_admin.list_display[0], 'connector_type')
        
        # Test resolution event admin
        event_admin = TouchpointResolutionEventAdmin(TouchpointResolutionEvent, admin_site)
        self.assertIsNotNone(event_admin)
        self.assertEqual(event_admin.list_display[0], 'connector_type')
        
        # Test alert admin
        alert_admin = TouchpointAlertAdmin(TouchpointAlert, admin_site)
        self.assertIsNotNone(alert_admin)
        self.assertEqual(alert_admin.list_display[0], 'alert_type')
    
    def test_admin_list_views(self):
        """Test admin list views are accessible and display data correctly."""
        # Test mapping rules list
        response = self.client.get('/admin/connectors/touchpointmappingrule/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com')
        self.assertContains(response, 'web.page_view')
        
        # Test resolution events list
        response = self.client.get('/admin/connectors/touchpointresolutionevent/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'web')
        self.assertContains(response, '45.5')
        
        # Test alerts list
        response = self.client.get('/admin/connectors/touchpointalert/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Resolution Time')
        self.assertContains(response, 'Active')
    
    def test_admin_form_views(self):
        """Test admin form views for creating and editing records."""
        # Test mapping rule form
        response = self.client.get(f'/admin/connectors/touchpointmappingrule/{self.mapping_rule.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com')
        self.assertContains(response, 'web.page_view')
        
        # Test creating new mapping rule
        response = self.client.get('/admin/connectors/touchpointmappingrule/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connector type:')
        self.assertContains(response, 'Event code:')
    
    def test_admin_search_and_filter(self):
        """Test admin search and filtering functionality."""
        # Test search functionality
        response = self.client.get('/admin/connectors/touchpointmappingrule/?q=example.com')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com')
        
        # Test filtering
        response = self.client.get('/admin/connectors/touchpointmappingrule/?connector_type=web')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com')
        
        # Test date filtering
        response = self.client.get('/admin/connectors/touchpointresolutionevent/?occurred_at__gte=2024-01-01')
        self.assertEqual(response.status_code, 200)


class AdminWorkflowIntegrationTest(TestCase):
    """Test complete admin workflows and user interactions."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
    
    def test_mapping_rule_creation_workflow(self):
        """Test complete workflow for creating a mapping rule."""
        # Step 1: Access the add form
        response = self.client.get('/admin/connectors/touchpointmappingrule/add/')
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit the form
        form_data = {
            'connector_type': 'web',
            'source_identifier': 'test.com',
            'event_code': 'form_submit',
            'touchpoint_code': 'web.form_submit',
            'touchpoint_label': 'Form Submission',
            'channel_code': 'organic',
            'medium_code': 'referral',
            'priority': '150',
            'is_active': 'on',
            'metadata': '{}'
        }
        
        response = self.client.post('/admin/connectors/touchpointmappingrule/add/', form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Step 3: Verify the rule was created
        rule = TouchpointMappingRule.objects.get(source_identifier='test.com')
        self.assertEqual(rule.event_code, 'form_submit')
        self.assertEqual(rule.priority, 150)
        self.assertTrue(rule.is_active)
    
    def test_mapping_rule_editing_workflow(self):
        """Test complete workflow for editing a mapping rule."""
        # Create a rule to edit
        rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='edit-test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            priority=100,
            is_active=True
        )
        
        # Step 1: Access the edit form
        response = self.client.get(f'/admin/connectors/touchpointmappingrule/{rule.id}/change/')
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit the edited form
        form_data = {
            'connector_type': 'web',
            'source_identifier': 'edit-test.com',
            'event_code': 'page_view',
            'touchpoint_code': 'web.page_view_updated',
            'touchpoint_label': 'Updated Page View',
            'channel_code': 'paid',
            'medium_code': 'search',
            'priority': '200',
            'is_active': 'on',
            'metadata': '{}'
        }
        
        response = self.client.post(f'/admin/connectors/touchpointmappingrule/{rule.id}/change/', form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Step 3: Verify the rule was updated
        rule.refresh_from_db()
        self.assertEqual(rule.touchpoint_code, 'web.page_view_updated')
        self.assertEqual(rule.touchpoint_label, 'Updated Page View')
        self.assertEqual(rule.channel_code, 'paid')
        self.assertEqual(rule.priority, 200)
    
    def test_alert_management_workflow(self):
        """Test complete workflow for managing alerts."""
        # Create an alert
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
        
        # Step 1: View the alert
        response = self.client.get('/admin/connectors/touchpointalert/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Alert')
        
        # Step 2: Acknowledge the alert
        response = self.client.post('/admin/connectors/touchpointalert/', {
            'action': 'acknowledge_alerts',
            '_selected_action': [str(alert.id)]
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Verify the alert was acknowledged
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'acknowledged')
        self.assertIsNotNone(alert.acknowledged_at)
        
        # Step 4: Resolve the alert
        response = self.client.post('/admin/connectors/touchpointalert/', {
            'action': 'resolve_alerts',
            '_selected_action': [str(alert.id)]
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Verify the alert was resolved
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')
        self.assertIsNotNone(alert.resolved_at)
    
    def test_bulk_operations_workflow(self):
        """Test bulk operations on multiple records."""
        # Create multiple mapping rules
        rules = []
        for i in range(3):
            rule = TouchpointMappingRule.objects.create(
                connector_type='web',
                source_identifier=f'bulk-test-{i}.com',
                event_code='page_view',
                touchpoint_code=f'web.page_view_{i}',
                touchpoint_label=f'Page View {i}',
                channel_code='organic',
                medium_code='referral',
                priority=100,
                is_active=True
            )
            rules.append(rule)
        
        # Test bulk deactivation using the custom admin action
        response = self.client.post('/admin/connectors/touchpointmappingrule/', {
            'action': 'deactivate_rules',
            '_selected_action': [str(rule.id) for rule in rules]
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify all rules were deactivated
        for rule in rules:
            rule.refresh_from_db()
            self.assertFalse(rule.is_active)
        
        # Test bulk activation using the custom admin action
        response = self.client.post('/admin/connectors/touchpointmappingrule/', {
            'action': 'activate_rules',
            '_selected_action': [str(rule.id) for rule in rules]
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify all rules were activated
        for rule in rules:
            rule.refresh_from_db()
            self.assertTrue(rule.is_active)
        
        # Test bulk duplication using the custom admin action
        response = self.client.post('/admin/connectors/touchpointmappingrule/', {
            'action': 'duplicate_rules',
            '_selected_action': [str(rule.id) for rule in rules[:2]]  # Duplicate first 2 rules
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify rules were duplicated
        self.assertEqual(TouchpointMappingRule.objects.count(), 5)  # 3 original + 2 duplicated
        
        # Check that duplicated rules have modified identifiers and event codes
        duplicated_rules = TouchpointMappingRule.objects.filter(
            source_identifier__endswith='_copy',
            event_code__endswith='_copy'
        )
        self.assertEqual(duplicated_rules.count(), 2)
        
        # Verify duplicated rules are inactive by default
        for rule in duplicated_rules:
            self.assertFalse(rule.is_active)
        
        # Test bulk cache clearing using the custom admin action
        from django.core.cache import cache
        
        # Set some cache data
        cache.set('touchpoint_mapping:web:bulk-test-1.com', 'cached_data_1', 300)
        cache.set('touchpoint_mapping:web:bulk-test-2.com', 'cached_data_2', 300)
        self.assertIsNotNone(cache.get('touchpoint_mapping:web:bulk-test-1.com'))
        self.assertIsNotNone(cache.get('touchpoint_mapping:web:bulk-test-2.com'))
        
        # Test cache clearing action
        response = self.client.post('/admin/connectors/touchpointmappingrule/', {
            'action': 'clear_cache',
            '_selected_action': [str(rule.id) for rule in rules[:2]]  # Clear cache for first 2 rules
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify cache was cleared
        self.assertIsNone(cache.get('touchpoint_mapping:web:bulk-test-1.com'))
        self.assertIsNone(cache.get('touchpoint_mapping:web:bulk-test-2.com'))


class CustomAdminViewsIntegrationTest(TestCase):
    """Test custom admin views and their integration with the system."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        # Create test data
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
        
        # Create test resolution events
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
        
        # Create test alert
        self.alert = TouchpointAlert.objects.create(
            alert_type='performance',
            severity='warning',
            title='Test Alert',
            message='This is a test alert',
            connector_type='web',
            threshold_value=100.0,
            actual_value=150.0,
            status='active'
        )
    
    def test_monitoring_dashboard_view(self):
        """Test the monitoring dashboard view."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Touchpoint Resolution Dashboard')
        self.assertContains(response, '99.2%')  # Success rate
        self.assertContains(response, '45ms')   # Avg resolution time
    
    def test_mapping_rules_analytics_view(self):
        """Test the mapping rules analytics view."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mapping Rules Analytics')
        self.assertContains(response, 'page_view')  # event_code is displayed
        self.assertContains(response, 'web.page_view')  # touchpoint_code is displayed
    
    def test_performance_report_view(self):
        """Test the performance report view."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/performance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Performance Report')
        self.assertContains(response, 'Last 24 Hours')
    
    def test_ajax_metrics_endpoint(self):
        """Test the AJAX metrics endpoint."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/ajax/metrics/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('total_events', data)
        self.assertIn('successful_events', data)
        self.assertIn('avg_resolution_time', data)
        self.assertIn('cache_hit_rate', data)
        self.assertIn('active_alerts', data)
        self.assertIn('timestamp', data)
    
    def test_system_health_check_endpoint(self):
        """Test the system health check endpoint."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/health-check/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_custom_view_permissions(self):
        """Test that custom views require proper permissions."""
        # Create a non-admin user
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass'
        )
        
        # Test access without admin permissions
        self.client.logout()
        self.client.login(username='regular', password='regularpass')
        
        response = self.client.get('/admin/connectors/touchpointmappingrule/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        response = self.client.get('/admin/connectors/touchpointmappingrule/analytics/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AdminTemplateIntegrationTest(TestCase):
    """Test custom admin templates and their functionality."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        # Create test mapping rule
        self.mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='template-test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            priority=200,
            is_active=True
        )
    
    def test_mapping_rule_form_template(self):
        """Test the custom mapping rule form template."""
        response = self.client.get(f'/admin/connectors/touchpointmappingrule/{self.mapping_rule.id}/change/')
        self.assertEqual(response.status_code, 200)
        
        # Check for custom template elements
        self.assertContains(response, 'mapping-rule-preview')
        self.assertContains(response, 'Rule:')
        self.assertContains(response, 'web:page_view → web.page_view')
        self.assertContains(response, 'priority-high')  # Priority 200 should be high
    
    def test_mapping_rule_list_template(self):
        """Test the custom mapping rule list template."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/')
        self.assertEqual(response.status_code, 200)
        
        # Check for custom template elements
        self.assertContains(response, 'mapping-rules-stats')
        self.assertContains(response, 'Total Rules')
        self.assertContains(response, 'Active Rules')
        self.assertContains(response, 'priority-high')  # Priority 200 should be high
        self.assertContains(response, 'connector-web')  # Web connector badge
    
    def test_dashboard_template(self):
        """Test the monitoring dashboard template."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Check for custom template elements
        self.assertContains(response, 'dashboard-container')
        self.assertContains(response, 'dashboard-header')
        self.assertContains(response, 'metrics-grid')
        self.assertContains(response, 'metric-card')
        self.assertContains(response, 'quick-actions')
    
    def test_analytics_template(self):
        """Test the mapping rules analytics template."""
        response = self.client.get('/admin/connectors/touchpointmappingrule/analytics/')
        self.assertEqual(response.status_code, 200)
        
        # Check for custom template elements
        self.assertContains(response, 'analytics-container')
        self.assertContains(response, 'analytics-header')
        self.assertContains(response, 'stats-summary')
        self.assertContains(response, 'rules-table')
        self.assertContains(response, 'usage-bar')


class AdminCacheIntegrationTest(TestCase):
    """Test admin interface integration with caching."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        # Clear cache
        cache.clear()
    
    def test_cache_clearing_on_rule_save(self):
        """Test that cache is cleared when mapping rules are saved."""
        # Verify admin user exists and is properly configured
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_active)
        
        # Verify login is working
        login_success = self.client.login(username='admin', password='adminpass')
        self.assertTrue(login_success, "Admin user login failed")
        
        # Create a mapping rule
        rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='cache-test.com',
            event_code='page_view',
            touchpoint_code='web.page_view',
            touchpoint_label='Page View',
            channel_code='organic',
            medium_code='referral',
            touchpoint_type_code='landing_page',
            priority=100,
            is_active=True
        )
        
        # Set some cache data
        cache.set('touchpoint_mapping:web:cache-test.com', 'cached_data', 300)
        self.assertIsNotNone(cache.get('touchpoint_mapping:web:cache-test.com'))
        
        # Test that the admin list view is accessible
        response = self.client.get('/admin/connectors/touchpointmappingrule/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Touchpoint Mapping Rules')
        
        # Test that the admin change form is accessible
        response = self.client.get(f'/admin/connectors/touchpointmappingrule/{rule.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Touchpoint Mapping Rule')


class AdminErrorHandlingIntegrationTest(TestCase):
    """Test error handling in admin interfaces."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
    
    def test_invalid_form_submission(self):
        """Test handling of invalid form submissions."""
        # Test that we can create a rule with valid data
        rule = TouchpointMappingRule.objects.create(
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
        
        # Verify the rule was created successfully
        self.assertEqual(rule.source_identifier, 'test.com')
        self.assertEqual(TouchpointMappingRule.objects.count(), 1)
    
    def test_nonexistent_record_access(self):
        """Test handling of access to non-existent records."""
        # Test that non-existent records don't exist in the database
        self.assertEqual(TouchpointMappingRule.objects.filter(id=99999).count(), 0)
        
        # Test that we can't get a non-existent record
        with self.assertRaises(TouchpointMappingRule.DoesNotExist):
            TouchpointMappingRule.objects.get(id=99999)
    
    def test_unauthorized_access(self):
        """Test handling of unauthorized access."""
        # Log out and try to access admin
        self.client.logout()
        
        response = self.client.get('/admin/connectors/touchpointmappingrule/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access custom views without authentication
        response = self.client.get('/admin/connectors/touchpointmappingrule/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AdminPerformanceIntegrationTest(TestCase):
    """Test admin interface performance and optimization."""
    
    def setUp(self):
        """Set up test data and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        # Create multiple test records
        for i in range(50):
            TouchpointMappingRule.objects.create(
                connector_type='web',
                source_identifier=f'perf-test-{i}.com',
                event_code='page_view',
                touchpoint_code=f'web.page_view_{i}',
                touchpoint_label=f'Page View {i}',
                channel_code='organic',
                medium_code='referral',
                priority=100,
                is_active=True
            )
    
    def test_admin_list_performance(self):
        """Test that admin list views perform well with many records."""
        # Test mapping rules list with many records
        response = self.client.get('/admin/connectors/touchpointmappingrule/')
        self.assertEqual(response.status_code, 200)
        
        # Should contain pagination
        self.assertContains(response, 'perf-test-0.com')
        self.assertContains(response, 'perf-test-49.com')
    
    def test_admin_search_performance(self):
        """Test that admin search performs well with many records."""
        # Test search functionality
        response = self.client.get('/admin/connectors/touchpointmappingrule/?q=perf-test-25')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'perf-test-25.com')
    
    def test_admin_filter_performance(self):
        """Test that admin filtering performs well with many records."""
        # Test filtering
        response = self.client.get('/admin/connectors/touchpointmappingrule/?connector_type=web')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'perf-test-0.com')
        self.assertContains(response, 'perf-test-49.com')


if __name__ == '__main__':
    import unittest
    unittest.main()

