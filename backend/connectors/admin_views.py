"""
Custom admin views for the Touchpoint Resolution System.

This module provides custom admin views for dashboards, reports,
and specialized management interfaces.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import json

from .models import TouchpointMappingRule
from .monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointAlert,
    TouchpointSystemHealth
)


@staff_member_required
def monitoring_dashboard(request):
    """
    Custom dashboard view for touchpoint resolution monitoring.
    """
    # Get recent metrics (last 24 hours)
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    # Basic statistics
    total_rules = TouchpointMappingRule.objects.filter(is_active=True).count()
    total_events = TouchpointResolutionEvent.objects.filter(occurred_at__gte=last_24h).count()
    successful_events = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=last_24h,
        error_occurred=False
    ).count()
    
    success_rate = (successful_events / total_events * 100) if total_events > 0 else 0
    
    # Average resolution time
    avg_resolution_time = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=last_24h,
        error_occurred=False
    ).aggregate(avg_time=Avg('resolution_time_ms'))['avg_time'] or 0
    
    # Cache hit rate
    cache_hits = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=last_24h,
        cache_hit=True
    ).count()
    cache_hit_rate = (cache_hits / total_events * 100) if total_events > 0 else 0
    
    # Active alerts
    active_alerts = TouchpointAlert.objects.filter(status='active').count()
    
    # Connector breakdown
    connector_stats = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=last_24h
    ).values('connector_type').annotate(
        count=Count('id'),
        avg_time=Avg('resolution_time_ms')
    ).order_by('-count')
    
    # Recent events for the activity feed
    recent_events = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=last_24h
    ).order_by('-occurred_at')[:10]
    
    # System health
    latest_health = TouchpointSystemHealth.objects.order_by('-recorded_at').first()
    
    context = {
        'title': 'Touchpoint Resolution Dashboard',
        'total_rules': total_rules,
        'total_events': total_events,
        'success_rate': round(success_rate, 1),
        'avg_resolution_time': round(avg_resolution_time, 1),
        'cache_hit_rate': round(cache_hit_rate, 1),
        'active_alerts': active_alerts,
        'connector_stats': connector_stats,
        'recent_events': recent_events,
        'latest_health': latest_health,
        'time_range': '24 hours',
    }
    
    return render(request, 'admin/connectors/monitoring_dashboard.html', context)


@staff_member_required
def mapping_rules_analytics(request):
    """
    Analytics view for mapping rules usage and performance.
    """
    # Get rule usage statistics
    rule_stats = []
    for rule in TouchpointMappingRule.objects.filter(is_active=True):
        # Count how many times this rule was applied
        applied_count = TouchpointResolutionEvent.objects.filter(
            mapping_rule_applied=True,
            touchpoint_code=rule.touchpoint_code,
            connector_type=rule.connector_type
        ).count()
        
        rule_stats.append({
            'rule': rule,
            'applied_count': applied_count,
            'success_rate': 95.0,  # TODO: Calculate actual success rate
        })
    
    # Sort by usage
    rule_stats.sort(key=lambda x: x['applied_count'], reverse=True)
    
    context = {
        'title': 'Mapping Rules Analytics',
        'rule_stats': rule_stats,
        'total_rules': len(rule_stats),
    }
    
    return render(request, 'admin/connectors/mapping_rules_analytics.html', context)


@staff_member_required
def performance_report(request):
    """
    Performance report view with detailed metrics and trends.
    """
    # Get time range from request
    hours = int(request.GET.get('hours', 24))
    now = timezone.now()
    start_time = now - timedelta(hours=hours)
    
    # Get performance metrics
    events = TouchpointResolutionEvent.objects.filter(occurred_at__gte=start_time)
    
    # Calculate metrics
    total_events = events.count()
    successful_events = events.filter(error_occurred=False).count()
    failed_events = events.filter(error_occurred=True).count()
    
    # Performance statistics
    perf_stats = events.filter(error_occurred=False).aggregate(
        avg_time=Avg('resolution_time_ms'),
        min_time=Min('resolution_time_ms'),
        max_time=Max('resolution_time_ms')
    )
    
    # Cache performance
    cache_hits = events.filter(cache_hit=True).count()
    cache_misses = events.filter(cache_hit=False).count()
    
    # Error breakdown
    error_breakdown = events.filter(error_occurred=True).values(
        'error_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Hourly breakdown
    hourly_stats = []
    for i in range(hours):
        hour_start = start_time + timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        
        hour_events = events.filter(occurred_at__gte=hour_start, occurred_at__lt=hour_end)
        hour_successful = hour_events.filter(error_occurred=False).count()
        hour_total = hour_events.count()
        
        hourly_stats.append({
            'hour': hour_start.strftime('%H:00'),
            'total': hour_total,
            'successful': hour_successful,
            'success_rate': (hour_successful / hour_total * 100) if hour_total > 0 else 0,
        })
    
    context = {
        'title': f'Performance Report - Last {hours} Hours',
        'time_range': hours,
        'total_events': total_events,
        'successful_events': successful_events,
        'failed_events': failed_events,
        'success_rate': (successful_events / total_events * 100) if total_events > 0 else 0,
        'perf_stats': perf_stats,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'cache_hit_rate': (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0,
        'error_breakdown': error_breakdown,
        'hourly_stats': hourly_stats,
    }
    
    return render(request, 'admin/connectors/performance_report.html', context)


@staff_member_required
def ajax_metrics(request):
    """
    AJAX endpoint for real-time metrics updates.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get recent metrics
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    events = TouchpointResolutionEvent.objects.filter(occurred_at__gte=last_hour)
    
    metrics = {
        'total_events': events.count(),
        'successful_events': events.filter(error_occurred=False).count(),
        'avg_resolution_time': events.filter(error_occurred=False).aggregate(
            avg_time=Avg('resolution_time_ms')
        )['avg_time'] or 0,
        'cache_hit_rate': (events.filter(cache_hit=True).count() / events.count() * 100) if events.count() > 0 else 0,
        'active_alerts': TouchpointAlert.objects.filter(status='active').count(),
        'timestamp': now.isoformat(),
    }
    
    return JsonResponse(metrics)


@staff_member_required
def system_health_check(request):
    """
    System health check endpoint.
    """
    health_status = {
        'status': 'healthy',
        'checks': {},
        'timestamp': timezone.now().isoformat(),
    }
    
    # Check database connectivity
    try:
        TouchpointMappingRule.objects.count()
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check cache connectivity
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy: cache not working'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check recent error rate
    last_hour = timezone.now() - timedelta(hours=1)
    recent_events = TouchpointResolutionEvent.objects.filter(occurred_at__gte=last_hour)
    if recent_events.count() > 0:
        error_rate = recent_events.filter(error_occurred=True).count() / recent_events.count()
        if error_rate > 0.05:  # 5% error rate threshold
            health_status['checks']['error_rate'] = f'unhealthy: {error_rate:.1%} error rate'
            health_status['status'] = 'unhealthy'
        else:
            health_status['checks']['error_rate'] = f'healthy: {error_rate:.1%} error rate'
    else:
        health_status['checks']['error_rate'] = 'healthy: no recent events'
    
    return JsonResponse(health_status)
