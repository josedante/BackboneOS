"""
Enhanced Django admin interface for Touchpoint Resolution System.

This module provides comprehensive admin interfaces for managing
touchpoint mapping rules, monitoring data, and system configuration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import TouchpointMappingRule, FailedEvent
from .monitoring_models import (
    TouchpointResolutionMetrics,
    TouchpointResolutionEvent,
    TouchpointCacheMetrics,
    TouchpointSystemHealth,
    TouchpointAlert
)
from .alerting import alert_manager
from .metrics import get_metrics_summary, get_current_metrics
from .admin_views import (
    monitoring_dashboard,
    mapping_rules_analytics,
    performance_report,
    ajax_metrics,
    system_health_check
)


@admin.register(TouchpointMappingRule)
class TouchpointMappingRuleAdmin(admin.ModelAdmin):
    """Enhanced admin interface for touchpoint mapping rules."""
    
    list_display = [
        'connector_type', 'source_identifier', 'event_code', 
        'touchpoint_code', 'channel_code', 'medium_code', 'touchpoint_type_code',
        'priority', 'is_active', 'created_at'
    ]
    list_filter = [
        'connector_type', 'is_active', 'channel_code', 'medium_code',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'event_code', 'touchpoint_code', 'source_identifier',
        'touchpoint_label', 'channel_code', 'medium_code', 'touchpoint_type_code'
    ]
    ordering = ['-priority', 'connector_type', 'event_code']
    
    fieldsets = (
        ('Scope Configuration', {
            'fields': ('connector_type', 'source_identifier', 'event_code'),
            'description': 'Define which connector and events this rule applies to.'
        }),
        ('Touchpoint Configuration', {
            'fields': ('touchpoint_code', 'touchpoint_label', 'channel_code', 'medium_code', 'touchpoint_type_code'),
            'description': 'Configure the resulting touchpoint properties.'
        }),
        ('Rule Priority', {
            'fields': ('priority',),
            'description': 'Higher priority rules take precedence. Default is 100.'
        }),
        ('Advanced Configuration', {
            'fields': ('metadata', 'is_active'),
            'classes': ('collapse',),
            'description': 'Additional metadata and activation status.'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and annotations."""
        return super().get_queryset(request).select_related()
    
    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(monitoring_dashboard), name='touchpoint_dashboard'),
            path('analytics/', self.admin_site.admin_view(mapping_rules_analytics), name='mapping_rules_analytics'),
            path('performance/', self.admin_site.admin_view(performance_report), name='performance_report'),
            path('ajax/metrics/', self.admin_site.admin_view(ajax_metrics), name='ajax_metrics'),
            path('health-check/', self.admin_site.admin_view(system_health_check), name='system_health_check'),
        ]
        return custom_urls + urls
    
    def save_model(self, request, obj, form, change):
        """Custom save logic with validation."""
        super().save_model(request, obj, form, change)
        
        # Clear cache when rules are modified
        from django.core.cache import cache
        cache.delete_many(cache.keys('touchpoint_mapping:*'))
        
        messages.success(request, f"Mapping rule {'updated' if change else 'created'} successfully!")
    
    # Custom admin actions
    actions = ['activate_rules', 'deactivate_rules', 'duplicate_rules', 'clear_cache']
    
    def activate_rules(self, request, queryset):
        """Activate selected mapping rules."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} mapping rule(s) activated successfully.')
    activate_rules.short_description = "Activate selected rules"
    
    def deactivate_rules(self, request, queryset):
        """Deactivate selected mapping rules."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} mapping rule(s) deactivated successfully.')
    deactivate_rules.short_description = "Deactivate selected rules"
    
    def duplicate_rules(self, request, queryset):
        """Duplicate selected mapping rules with modified identifiers."""
        duplicated_count = 0
        for rule in queryset:
            try:
                # Create a copy with modified identifier and event code to avoid unique constraint
                new_rule = TouchpointMappingRule.objects.create(
                    connector_type=rule.connector_type,
                    source_identifier=f"{rule.source_identifier}_copy",
                    event_code=f"{rule.event_code}_copy",  # Also modify event code to avoid unique constraint
                    touchpoint_code=rule.touchpoint_code,
                    touchpoint_label=f"{rule.touchpoint_label} (Copy)",
                    channel_code=rule.channel_code,
                    medium_code=rule.medium_code,
                    touchpoint_type_code=rule.touchpoint_type_code,
                    priority=rule.priority,
                    metadata=rule.metadata,
                    is_active=False  # Start as inactive
                )
                duplicated_count += 1
            except Exception as e:
                # If duplication fails, continue with next rule
                self.message_user(request, f'Failed to duplicate rule {rule.id}: {str(e)}', level='WARNING')
                continue
        
        self.message_user(request, f'{duplicated_count} mapping rule(s) duplicated successfully.')
    duplicate_rules.short_description = "Duplicate selected rules"
    
    def clear_cache(self, request, queryset):
        """Clear cache for selected mapping rules."""
        from django.core.cache import cache
        
        # Clear general cache
        cache.delete_many(cache.keys('touchpoint_mapping:*'))
        
        # Clear specific rule caches
        for rule in queryset:
            cache_key = f'touchpoint_mapping:{rule.connector_type}:{rule.source_identifier}'
            cache.delete(cache_key)
        
        self.message_user(request, f'Cache cleared for {queryset.count()} mapping rule(s).')
    clear_cache.short_description = "Clear cache for selected rules"


@admin.register(TouchpointResolutionEvent)
class TouchpointResolutionEventAdmin(admin.ModelAdmin):
    """Admin interface for touchpoint resolution events."""
    
    list_display = [
        'connector_type', 'event_type', 'touchpoint_code',
        'resolution_time_ms', 'cache_hit', 'error_occurred',
        'occurred_at'
    ]
    list_filter = [
        'connector_type', 'event_type', 'error_occurred', 'cache_hit',
        'mapping_rule_applied', 'touchpoint_created', 'occurred_at'
    ]
    search_fields = [
        'touchpoint_code', 'channel_code', 'medium_code',
        'error_message', 'error_type'
    ]
    ordering = ['-occurred_at']
    
    readonly_fields = ['occurred_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('connector_type', 'event_type', 'occurred_at')
        }),
        ('Performance Data', {
            'fields': ('resolution_time_ms', 'cache_hit', 'mapping_rule_applied', 'touchpoint_created')
        }),
        ('Touchpoint Details', {
            'fields': ('touchpoint_code', 'channel_code', 'medium_code')
        }),
        ('Error Information', {
            'fields': ('error_occurred', 'error_message', 'error_type'),
            'classes': ('collapse',)
        }),
        ('Additional Context', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Limit to recent events by default."""
        qs = super().get_queryset(request)
        if not request.GET.get('occurred_at__gte'):
            # Default to last 7 days
            default_date = timezone.now() - timedelta(days=7)
            qs = qs.filter(occurred_at__gte=default_date)
        return qs
    
    def has_add_permission(self, request):
        """Events are created automatically, not manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Events are read-only."""
        return False


@admin.register(TouchpointAlert)
class TouchpointAlertAdmin(admin.ModelAdmin):
    """Admin interface for system alerts."""
    
    list_display = [
        'alert_type', 'severity', 'title', 'status',
        'triggered_at', 'connector_type'
    ]
    list_filter = [
        'alert_type', 'severity', 'status', 'connector_type',
        'triggered_at', 'acknowledged_at', 'resolved_at'
    ]
    search_fields = ['title', 'message', 'alert_type']
    ordering = ['-triggered_at']
    
    readonly_fields = [
        'triggered_at', 'acknowledged_at', 'resolved_at',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'severity', 'title', 'message')
        }),
        ('Context', {
            'fields': ('connector_type', 'threshold_value', 'actual_value')
        }),
        ('Status', {
            'fields': ('status', 'triggered_at', 'acknowledged_at', 'resolved_at')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['acknowledge_alerts', 'resolve_alerts', 'dismiss_alerts']
    
    def acknowledge_alerts(self, request, queryset):
        """Bulk acknowledge alerts."""
        count = 0
        for alert in queryset.filter(status='active'):
            alert.acknowledge()
            count += 1
        messages.success(request, f"{count} alerts acknowledged.")
    acknowledge_alerts.short_description = "Acknowledge selected alerts"
    
    def resolve_alerts(self, request, queryset):
        """Bulk resolve alerts."""
        count = 0
        for alert in queryset.filter(status__in=['active', 'acknowledged']):
            alert.resolve()
            count += 1
        messages.success(request, f"{count} alerts resolved.")
    resolve_alerts.short_description = "Resolve selected alerts"
    
    def dismiss_alerts(self, request, queryset):
        """Bulk dismiss alerts."""
        count = 0
        for alert in queryset.filter(status__in=['active', 'acknowledged']):
            alert.dismiss()
            count += 1
        messages.success(request, f"{count} alerts dismissed.")
    dismiss_alerts.short_description = "Dismiss selected alerts"


@admin.register(TouchpointResolutionMetrics)
class TouchpointResolutionMetricsAdmin(admin.ModelAdmin):
    """Admin interface for aggregated resolution metrics."""
    
    list_display = [
        'period_type', 'period_start', 'period_end',
        'total_resolutions', 'success_rate', 'avg_resolution_time_ms',
        'cache_hit_rate', 'error_rate'
    ]
    list_filter = [
        'period_type', 'period_start', 'period_end'
    ]
    search_fields = ['period_type']
    ordering = ['-period_start']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_type', 'period_start', 'period_end')
        }),
        ('Resolution Metrics', {
            'fields': ('total_resolutions', 'successful_resolutions', 'failed_resolutions')
        }),
        ('Performance Metrics', {
            'fields': (
                'avg_resolution_time_ms', 'min_resolution_time_ms', 'max_resolution_time_ms',
                'p95_resolution_time_ms', 'p99_resolution_time_ms'
            )
        }),
        ('Cache Metrics', {
            'fields': ('cache_hit_rate', 'cache_miss_rate')
        }),
        ('Mapping Rule Metrics', {
            'fields': ('mapping_rules_applied', 'mapping_rules_created')
        }),
        ('Connector Breakdown', {
            'fields': ('connector_breakdown',),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate(self, obj):
        """Calculate success rate percentage."""
        if obj.total_resolutions == 0:
            return "0%"
        rate = (obj.successful_resolutions / obj.total_resolutions) * 100
        return f"{rate:.1f}%"
    success_rate.short_description = 'Success Rate'
    
    def error_rate(self, obj):
        """Calculate error rate percentage."""
        if obj.total_resolutions == 0:
            return "0%"
        rate = (obj.failed_resolutions / obj.total_resolutions) * 100
        return f"{rate:.1f}%"
    error_rate.short_description = 'Error Rate'
    
    def has_add_permission(self, request):
        """Metrics are created automatically."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Metrics are read-only."""
        return False


@admin.register(TouchpointSystemHealth)
class TouchpointSystemHealthAdmin(admin.ModelAdmin):
    """Admin interface for system health records."""
    
    list_display = [
        'recorded_at', 'health_status', 'error_rate',
        'avg_resolution_time_ms', 'active_mapping_rules',
        'cache_size'
    ]
    list_filter = [
        'health_status', 'recorded_at'
    ]
    search_fields = ['health_status']
    ordering = ['-recorded_at']
    
    readonly_fields = ['recorded_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Health Status', {
            'fields': ('health_status', 'recorded_at')
        }),
        ('Performance Metrics', {
            'fields': ('avg_resolution_time_ms', 'error_rate')
        }),
        ('System Metrics', {
            'fields': ('active_mapping_rules', 'total_touchpoints', 'total_interactions')
        }),
        ('Cache Metrics', {
            'fields': ('cache_size', 'cache_memory_usage_mb')
        }),
        ('Database Metrics', {
            'fields': ('database_connections', 'slow_queries_count')
        }),
        ('Resource Usage', {
            'fields': ('memory_usage_mb', 'cpu_usage_percent')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Health records are created automatically."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Health records are read-only."""
        return False


@admin.register(TouchpointCacheMetrics)
class TouchpointCacheMetricsAdmin(admin.ModelAdmin):
    """Admin interface for cache performance metrics."""
    
    list_display = [
        'period_start', 'period_end', 'total_operations',
        'hit_rate', 'avg_operation_time_ms', 'cache_size_at_end'
    ]
    list_filter = [
        'period_start', 'period_end'
    ]
    search_fields = ['period_start']
    ordering = ['-period_start']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('Operation Metrics', {
            'fields': (
                'total_operations', 'get_operations', 'set_operations', 'delete_operations'
            )
        }),
        ('Hit/Miss Metrics', {
            'fields': ('cache_hits', 'cache_misses')
        }),
        ('Performance Metrics', {
            'fields': ('avg_operation_time_ms', 'max_operation_time_ms')
        }),
        ('Cache Size Metrics', {
            'fields': ('cache_size_at_start', 'cache_size_at_end', 'max_cache_size')
        }),
        ('Key Pattern Breakdown', {
            'fields': ('key_pattern_breakdown',),
            'classes': ('collapse',)
        }),
    )
    
    def hit_rate(self, obj):
        """Calculate cache hit rate percentage."""
        if obj.get_operations == 0:
            return "0%"
        rate = (obj.cache_hits / obj.get_operations) * 100
        return f"{rate:.1f}%"
    hit_rate.short_description = 'Hit Rate'
    
    def has_add_permission(self, request):
        """Cache metrics are created automatically."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Cache metrics are read-only."""
        return False


@admin.register(FailedEvent)
class FailedEventAdmin(admin.ModelAdmin):
    """Admin interface for managing failed connector events."""
    
    list_display = [
        'id', 'connector_type', 'event_type', 'status',
        'retry_count', 'get_max_retries_display',
        'first_failed_at', 'next_retry_at', 'source_identifier_short'
    ]
    list_filter = [
        'connector_type', 'event_type', 'status',
        'first_failed_at', 'next_retry_at'
    ]
    search_fields = [
        'id', 'source_identifier', 'error_message',
        'interaction_ids'
    ]
    ordering = ['-first_failed_at']
    
    readonly_fields = [
        'id', 'first_failed_at', 'last_retry_at', 'processed_at',
        'retry_count', 'interaction_ids', 'get_max_retries_display',
        'formatted_error_trace', 'formatted_raw_payload'
    ]
    
    fieldsets = (
        ('Event Information', {
            'fields': ('id', 'connector_type', 'event_type', 'source_identifier', 'status')
        }),
        ('Retry Configuration', {
            'fields': ('retry_count', 'get_max_retries_display', 'next_retry_at')
        }),
        ('Timeline', {
            'fields': ('first_failed_at', 'last_retry_at', 'processed_at')
        }),
        ('Error Details', {
            'fields': ('error_message', 'formatted_error_trace'),
            'classes': ('collapse',)
        }),
        ('Event Payload', {
            'fields': ('formatted_raw_payload',),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('interaction_ids',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['retry_selected_events', 'abandon_selected_events', 'reset_retry_count']
    
    def get_max_retries_display(self, obj):
        """Display max retries for this connector type."""
        return obj.get_max_retries()
    get_max_retries_display.short_description = 'Max Retries'
    
    def source_identifier_short(self, obj):
        """Display truncated source identifier."""
        if len(obj.source_identifier) > 40:
            return f"{obj.source_identifier[:37]}..."
        return obj.source_identifier
    source_identifier_short.short_description = 'Source'
    
    def formatted_error_trace(self, obj):
        """Display formatted error trace."""
        if not obj.error_trace:
            return "No trace available"
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.error_trace[:2000])
    formatted_error_trace.short_description = 'Error Trace'
    
    def formatted_raw_payload(self, obj):
        """Display formatted JSON payload."""
        if not obj.raw_payload:
            return "No payload available"
        try:
            formatted = json.dumps(obj.raw_payload, indent=2, ensure_ascii=False)
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted[:2000])
        except:
            return format_html('<pre>{}</pre>', str(obj.raw_payload)[:2000])
    formatted_raw_payload.short_description = 'Raw Payload'
    
    def retry_selected_events(self, request, queryset):
        """Manually trigger retry for selected events."""
        from .fallback import retry_failed_event
        
        # Only retry events that are retryable
        retryable = queryset.filter(status__in=['pending', 'retrying'])
        
        if not retryable.exists():
            messages.warning(request, "No retryable events selected (must be 'pending' or 'retrying' status)")
            return
        
        success_count = 0
        failed_count = 0
        
        for event in retryable:
            try:
                if retry_failed_event(event):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                messages.error(request, f"Error retrying event {event.id}: {str(e)}")
        
        # Show results
        if success_count > 0:
            messages.success(request, f"{success_count} event(s) retried successfully")
        if failed_count > 0:
            messages.warning(request, f"{failed_count} event(s) failed to retry")
    
    retry_selected_events.short_description = "Retry selected events"
    
    def abandon_selected_events(self, request, queryset):
        """Mark selected events as abandoned (won't retry)."""
        # Only abandon events that haven't been processed
        abandonable = queryset.filter(status__in=['pending', 'retrying', 'failed'])
        
        updated = abandonable.update(status='abandoned')
        
        if updated > 0:
            messages.success(request, f"{updated} event(s) marked as abandoned")
        else:
            messages.warning(request, "No abandonable events selected")
    
    abandon_selected_events.short_description = "Abandon selected events"
    
    def reset_retry_count(self, request, queryset):
        """Reset retry count for selected events (useful for giving them another chance)."""
        # Only reset for failed events
        resettable = queryset.filter(status='failed')
        
        updated_count = 0
        for event in resettable:
            event.retry_count = 0
            event.status = 'pending'
            event.next_retry_at = timezone.now()
            event.save(update_fields=['retry_count', 'status', 'next_retry_at'])
            updated_count += 1
        
        if updated_count > 0:
            messages.success(request, f"{updated_count} event(s) reset for retry")
        else:
            messages.warning(request, "No failed events selected to reset")
    
    reset_retry_count.short_description = "Reset retry count (give another chance)"
    
    def has_add_permission(self, request):
        """Events are created automatically via store_failed_event()."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset and default to recent events."""
        qs = super().get_queryset(request)
        
        # Default to last 30 days if no date filter specified
        if not request.GET.get('first_failed_at__gte'):
            default_date = timezone.now() - timedelta(days=30)
            qs = qs.filter(first_failed_at__gte=default_date)
        
        return qs
