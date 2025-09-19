"""
Alerting system for Touchpoint Resolution System.

This module provides comprehensive alerting capabilities for monitoring
system health, performance issues, and error conditions.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from .monitoring_models import TouchpointAlert, TouchpointResolutionMetrics, TouchpointSystemHealth
from .metrics import get_metrics_summary

logger = logging.getLogger(__name__)


class TouchpointAlertManager:
    """
    Manages alerts for the touchpoint resolution system.
    
    Monitors various metrics and triggers alerts when thresholds are exceeded.
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'error_rate': 5.0,  # 5% error rate
            'avg_resolution_time_ms': 1000.0,  # 1 second
            'max_resolution_time_ms': 5000.0,  # 5 seconds
            'cache_miss_rate': 20.0,  # 20% cache miss rate
            'system_health': 'warning',  # System health threshold
        }
        
        self.alert_cooldowns = {
            'high_error_rate': 300,  # 5 minutes
            'slow_resolution': 600,  # 10 minutes
            'cache_miss_rate': 300,  # 5 minutes
            'system_health': 1800,  # 30 minutes
        }
    
    def check_all_alerts(self) -> List[TouchpointAlert]:
        """
        Check all alert conditions and create new alerts if needed.
        
        Returns:
            List of newly created alerts
        """
        new_alerts = []
        
        try:
            # Check error rate
            error_alert = self._check_error_rate()
            if error_alert:
                new_alerts.append(error_alert)
            
            # Check resolution performance
            performance_alert = self._check_resolution_performance()
            if performance_alert:
                new_alerts.append(performance_alert)
            
            # Check cache performance
            cache_alert = self._check_cache_performance()
            if cache_alert:
                new_alerts.append(cache_alert)
            
            # Check system health
            health_alert = self._check_system_health()
            if health_alert:
                new_alerts.append(health_alert)
            
            # Send notifications for critical alerts
            for alert in new_alerts:
                if alert.severity == 'critical':
                    self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
        
        return new_alerts
    
    def _check_error_rate(self) -> Optional[TouchpointAlert]:
        """Check if error rate exceeds threshold."""
        try:
            # Get recent metrics
            metrics = get_metrics_summary(hours=1)  # Last hour
            
            error_rate = metrics.get('error_rate', 0)
            threshold = self.alert_thresholds['error_rate']
            
            if error_rate > threshold:
                # Check if we already have a recent alert for this
                if self._has_recent_alert('high_error_rate', minutes=5):
                    return None
                
                alert = TouchpointAlert.objects.create(
                    alert_type='high_error_rate',
                    severity='high' if error_rate > threshold * 2 else 'medium',
                    title=f"High Error Rate Detected",
                    message=f"Touchpoint resolution error rate is {error_rate:.1f}%, exceeding threshold of {threshold}%",
                    threshold_value=threshold,
                    actual_value=error_rate,
                    metadata={
                        'total_resolutions': metrics.get('total_resolutions', 0),
                        'failed_resolutions': metrics.get('total_resolutions', 0) - metrics.get('successful_resolutions', 0)
                    }
                )
                
                logger.warning(f"High error rate alert created: {error_rate:.1f}%")
                return alert
        
        except Exception as e:
            logger.error(f"Error checking error rate: {e}")
        
        return None
    
    def _check_resolution_performance(self) -> Optional[TouchpointAlert]:
        """Check if resolution performance is degraded."""
        try:
            metrics = get_metrics_summary(hours=1)
            
            avg_time = metrics.get('avg_resolution_time_ms', 0)
            max_time = metrics.get('max_resolution_time_ms', 0)
            
            threshold_avg = self.alert_thresholds['avg_resolution_time_ms']
            threshold_max = self.alert_thresholds['max_resolution_time_ms']
            
            if avg_time > threshold_avg or max_time > threshold_max:
                # Check if we already have a recent alert
                if self._has_recent_alert('slow_resolution', minutes=10):
                    return None
                
                severity = 'critical' if max_time > threshold_max * 2 else 'high'
                
                alert = TouchpointAlert.objects.create(
                    alert_type='slow_resolution',
                    severity=severity,
                    title=f"Slow Resolution Performance",
                    message=f"Average resolution time: {avg_time:.1f}ms, Max: {max_time:.1f}ms (thresholds: {threshold_avg}ms avg, {threshold_max}ms max)",
                    threshold_value=threshold_avg,
                    actual_value=avg_time,
                    metadata={
                        'avg_resolution_time_ms': avg_time,
                        'max_resolution_time_ms': max_time,
                        'total_resolutions': metrics.get('total_resolutions', 0)
                    }
                )
                
                logger.warning(f"Slow resolution alert created: avg={avg_time:.1f}ms, max={max_time:.1f}ms")
                return alert
        
        except Exception as e:
            logger.error(f"Error checking resolution performance: {e}")
        
        return None
    
    def _check_cache_performance(self) -> Optional[TouchpointAlert]:
        """Check if cache performance is degraded."""
        try:
            # Get cache metrics from the last hour
            recent_metrics = TouchpointResolutionMetrics.objects.filter(
                period_start__gte=timezone.now() - timedelta(hours=1),
                period_type='hourly'
            ).order_by('-period_start').first()
            
            if not recent_metrics:
                return None
            
            cache_miss_rate = recent_metrics.cache_miss_rate
            threshold = self.alert_thresholds['cache_miss_rate']
            
            if cache_miss_rate > threshold:
                # Check if we already have a recent alert
                if self._has_recent_alert('cache_miss_rate', minutes=5):
                    return None
                
                alert = TouchpointAlert.objects.create(
                    alert_type='cache_miss_rate',
                    severity='medium',
                    title=f"High Cache Miss Rate",
                    message=f"Cache miss rate is {cache_miss_rate:.1f}%, exceeding threshold of {threshold}%",
                    threshold_value=threshold,
                    actual_value=cache_miss_rate,
                    metadata={
                        'cache_hit_rate': recent_metrics.cache_hit_rate,
                        'total_operations': recent_metrics.total_resolutions
                    }
                )
                
                logger.warning(f"High cache miss rate alert created: {cache_miss_rate:.1f}%")
                return alert
        
        except Exception as e:
            logger.error(f"Error checking cache performance: {e}")
        
        return None
    
    def _check_system_health(self) -> Optional[TouchpointAlert]:
        """Check overall system health."""
        try:
            # Get latest system health record
            latest_health = TouchpointSystemHealth.objects.order_by('-recorded_at').first()
            
            if not latest_health:
                return None
            
            if latest_health.health_status in ['warning', 'critical']:
                # Check if we already have a recent alert
                if self._has_recent_alert('system_health', minutes=30):
                    return None
                
                severity = 'critical' if latest_health.health_status == 'critical' else 'high'
                
                alert = TouchpointAlert.objects.create(
                    alert_type='system_health',
                    severity=severity,
                    title=f"System Health {latest_health.health_status.title()}",
                    message=f"System health status is {latest_health.health_status}. Error rate: {latest_health.error_rate:.1f}%, Avg resolution time: {latest_health.avg_resolution_time_ms:.1f}ms",
                    actual_value=latest_health.error_rate,
                    metadata={
                        'health_status': latest_health.health_status,
                        'error_rate': latest_health.error_rate,
                        'avg_resolution_time_ms': latest_health.avg_resolution_time_ms,
                        'active_mapping_rules': latest_health.active_mapping_rules,
                        'cache_size': latest_health.cache_size
                    }
                )
                
                logger.warning(f"System health alert created: {latest_health.health_status}")
                return alert
        
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
        
        return None
    
    def _has_recent_alert(self, alert_type: str, minutes: int = 5) -> bool:
        """Check if there's a recent alert of the given type."""
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        return TouchpointAlert.objects.filter(
            alert_type=alert_type,
            status__in=['active', 'acknowledged'],
            triggered_at__gte=cutoff_time
        ).exists()
    
    def _send_alert_notification(self, alert: TouchpointAlert):
        """Send alert notification via email."""
        try:
            if not hasattr(settings, 'TOUCHPOINT_ALERT_EMAILS'):
                return
            
            email_addresses = settings.TOUCHPOINT_ALERT_EMAILS
            if not email_addresses:
                return
            
            subject = f"[{alert.severity.upper()}] Touchpoint Alert: {alert.title}"
            
            message = f"""
Touchpoint Resolution System Alert

Alert Type: {alert.alert_type}
Severity: {alert.severity}
Title: {alert.title}

Message:
{alert.message}

Threshold: {alert.threshold_value}
Actual Value: {alert.actual_value}

Triggered At: {alert.triggered_at}
Alert ID: {alert.id}

Please check the system and take appropriate action.

---
Touchpoint Resolution System
            """.strip()
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=email_addresses,
                fail_silently=True
            )
            
            logger.info(f"Alert notification sent for {alert.alert_type}")
        
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    def get_active_alerts(self) -> List[TouchpointAlert]:
        """Get all active alerts."""
        return TouchpointAlert.objects.filter(
            status='active'
        ).order_by('-triggered_at')
    
    def get_alerts_by_severity(self, severity: str) -> List[TouchpointAlert]:
        """Get alerts by severity level."""
        return TouchpointAlert.objects.filter(
            severity=severity,
            status='active'
        ).order_by('-triggered_at')
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        try:
            alert = TouchpointAlert.objects.get(id=alert_id)
            alert.acknowledge()
            return True
        except TouchpointAlert.DoesNotExist:
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            alert = TouchpointAlert.objects.get(id=alert_id)
            alert.resolve()
            return True
        except TouchpointAlert.DoesNotExist:
            return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts."""
        active_alerts = self.get_active_alerts()
        
        summary = {
            'total_active': active_alerts.count(),
            'by_severity': {
                'critical': active_alerts.filter(severity='critical').count(),
                'high': active_alerts.filter(severity='high').count(),
                'medium': active_alerts.filter(severity='medium').count(),
                'low': active_alerts.filter(severity='low').count(),
            },
            'by_type': {},
            'recent_alerts': []
        }
        
        # Group by alert type
        for alert in active_alerts:
            alert_type = alert.alert_type
            if alert_type not in summary['by_type']:
                summary['by_type'][alert_type] = 0
            summary['by_type'][alert_type] += 1
        
        # Get recent alerts (last 10)
        summary['recent_alerts'] = [
            {
                'id': str(alert.id),
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'triggered_at': alert.triggered_at.isoformat()
            }
            for alert in active_alerts[:10]
        ]
        
        return summary


# Global alert manager instance
alert_manager = TouchpointAlertManager()
