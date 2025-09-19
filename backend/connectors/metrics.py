"""
Performance metrics collection for Touchpoint Resolution System.

This module provides comprehensive metrics collection for monitoring
touchpoint resolution performance, cache efficiency, and system health.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ResolutionMetrics:
    """Metrics for a single touchpoint resolution operation."""
    connector_type: str
    resolution_time_ms: float
    cache_hit: bool
    mapping_rule_applied: bool
    touchpoint_created: bool
    error_occurred: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=timezone.now)


@dataclass
class CacheMetrics:
    """Metrics for cache operations."""
    operation: str  # 'get', 'set', 'delete', 'warm'
    key_pattern: str
    success: bool
    duration_ms: float
    hit_rate: Optional[float] = None
    timestamp: datetime = field(default_factory=timezone.now)


@dataclass
class SystemMetrics:
    """System-level metrics."""
    active_mapping_rules: int
    cache_size: int
    database_connections: int
    memory_usage_mb: Optional[float] = None
    timestamp: datetime = field(default_factory=timezone.now)


class TouchpointMetricsCollector:
    """
    Central metrics collector for touchpoint resolution system.
    
    Collects and aggregates metrics for:
    - Resolution performance
    - Cache efficiency
    - System health
    - Error rates
    """
    
    def __init__(self):
        self.metrics_buffer: List[ResolutionMetrics] = []
        self.cache_metrics_buffer: List[CacheMetrics] = []
        self.buffer_size = getattr(settings, 'TOUCHPOINT_METRICS_BUFFER_SIZE', 100)
        self.flush_interval = getattr(settings, 'TOUCHPOINT_METRICS_FLUSH_INTERVAL', 60)  # seconds
        self.last_flush = timezone.now()
    
    def record_resolution(self, metrics: ResolutionMetrics):
        """Record touchpoint resolution metrics."""
        self.metrics_buffer.append(metrics)
        
        # Auto-flush if buffer is full
        if len(self.metrics_buffer) >= self.buffer_size:
            self.flush_metrics()
        
        # Log high-latency resolutions
        if metrics.resolution_time_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow touchpoint resolution: {metrics.resolution_time_ms:.2f}ms "
                f"for {metrics.connector_type}"
            )
        
        # Log errors
        if metrics.error_occurred:
            logger.error(
                f"Touchpoint resolution error for {metrics.connector_type}: "
                f"{metrics.error_message}"
            )
    
    def record_cache_operation(self, metrics: CacheMetrics):
        """Record cache operation metrics."""
        self.cache_metrics_buffer.append(metrics)
        
        # Auto-flush if buffer is full
        if len(self.cache_metrics_buffer) >= self.buffer_size:
            self.flush_cache_metrics()
    
    def flush_metrics(self):
        """Flush resolution metrics to storage."""
        if not self.metrics_buffer:
            return
        
        try:
            # Store metrics in cache for real-time access
            cache_key = f"touchpoint_metrics_{timezone.now().strftime('%Y%m%d_%H%M')}"
            cache.set(cache_key, self.metrics_buffer, 3600)  # 1 hour
            
            # Store aggregated metrics
            self._store_aggregated_metrics()
            
            # Clear buffer
            self.metrics_buffer.clear()
            self.last_flush = timezone.now()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
    
    def flush_cache_metrics(self):
        """Flush cache metrics to storage."""
        if not self.cache_metrics_buffer:
            return
        
        try:
            # Store cache metrics
            cache_key = f"cache_metrics_{timezone.now().strftime('%Y%m%d_%H%M')}"
            cache.set(cache_key, self.cache_metrics_buffer, 3600)
            
            # Clear buffer
            self.cache_metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush cache metrics: {e}")
    
    def _store_aggregated_metrics(self):
        """Store aggregated metrics for reporting."""
        if not self.metrics_buffer:
            return
        
        # Calculate aggregations
        total_resolutions = len(self.metrics_buffer)
        successful_resolutions = sum(1 for m in self.metrics_buffer if not m.error_occurred)
        error_rate = (total_resolutions - successful_resolutions) / total_resolutions * 100
        
        avg_resolution_time = sum(m.resolution_time_ms for m in self.metrics_buffer) / total_resolutions
        max_resolution_time = max(m.resolution_time_ms for m in self.metrics_buffer)
        
        cache_hit_rate = sum(1 for m in self.metrics_buffer if m.cache_hit) / total_resolutions * 100
        
        # Group by connector type
        connector_stats = {}
        for metrics in self.metrics_buffer:
            if metrics.connector_type not in connector_stats:
                connector_stats[metrics.connector_type] = {
                    'count': 0,
                    'total_time': 0,
                    'errors': 0,
                    'cache_hits': 0
                }
            
            stats = connector_stats[metrics.connector_type]
            stats['count'] += 1
            stats['total_time'] += metrics.resolution_time_ms
            if metrics.error_occurred:
                stats['errors'] += 1
            if metrics.cache_hit:
                stats['cache_hits'] += 1
        
        # Store aggregated data
        aggregated_data = {
            'timestamp': timezone.now().isoformat(),
            'total_resolutions': total_resolutions,
            'successful_resolutions': successful_resolutions,
            'error_rate': error_rate,
            'avg_resolution_time_ms': avg_resolution_time,
            'max_resolution_time_ms': max_resolution_time,
            'cache_hit_rate': cache_hit_rate,
            'connector_stats': connector_stats
        }
        
        cache_key = f"aggregated_metrics_{timezone.now().strftime('%Y%m%d_%H')}"
        cache.set(cache_key, aggregated_data, 86400)  # 24 hours
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Get recent aggregated metrics
            current_hour = timezone.now().strftime('%Y%m%d_%H')
            cache_key = f"aggregated_metrics_{current_hour}"
            aggregated = cache.get(cache_key, {})
            
            # Get system metrics
            system_metrics = self._get_system_metrics()
            
            return {
                'aggregated': aggregated,
                'system': system_metrics,
                'buffer_size': len(self.metrics_buffer),
                'last_flush': self.last_flush.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Count active mapping rules
            from .models import TouchpointMappingRule
            active_rules = TouchpointMappingRule.objects.filter(is_active=True).count()
            
            # Get cache size
            cache_keys = cache.keys('touchpoint_*')
            cache_size = len(cache_keys)
            
            # Get database connections
            db_connections = len(connection.queries) if settings.DEBUG else 0
            
            return {
                'active_mapping_rules': active_rules,
                'cache_size': cache_size,
                'database_connections': db_connections,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""
        try:
            summary = {
                'total_resolutions': 0,
                'successful_resolutions': 0,
                'error_rate': 0,
                'avg_resolution_time_ms': 0,
                'max_resolution_time_ms': 0,
                'cache_hit_rate': 0,
                'connector_breakdown': {},
                'hourly_breakdown': []
            }
            
            # Collect data from last N hours
            for i in range(hours):
                hour_key = (timezone.now() - timedelta(hours=i)).strftime('%Y%m%d_%H')
                cache_key = f"aggregated_metrics_{hour_key}"
                data = cache.get(cache_key)
                
                if data:
                    summary['total_resolutions'] += data.get('total_resolutions', 0)
                    summary['successful_resolutions'] += data.get('successful_resolutions', 0)
                    summary['max_resolution_time_ms'] = max(
                        summary['max_resolution_time_ms'],
                        data.get('max_resolution_time_ms', 0)
                    )
                    
                    # Add to hourly breakdown
                    summary['hourly_breakdown'].append({
                        'hour': hour_key,
                        'resolutions': data.get('total_resolutions', 0),
                        'error_rate': data.get('error_rate', 0),
                        'avg_time_ms': data.get('avg_resolution_time_ms', 0)
                    })
                    
                    # Aggregate connector stats
                    connector_stats = data.get('connector_stats', {})
                    for connector, stats in connector_stats.items():
                        if connector not in summary['connector_breakdown']:
                            summary['connector_breakdown'][connector] = {
                                'count': 0,
                                'total_time': 0,
                                'errors': 0
                            }
                        
                        summary['connector_breakdown'][connector]['count'] += stats['count']
                        summary['connector_breakdown'][connector]['total_time'] += stats['total_time']
                        summary['connector_breakdown'][connector]['errors'] += stats['errors']
            
            # Calculate final metrics
            if summary['total_resolutions'] > 0:
                summary['error_rate'] = (
                    (summary['total_resolutions'] - summary['successful_resolutions']) /
                    summary['total_resolutions'] * 100
                )
                
                total_time = sum(
                    stats['total_time'] for stats in summary['connector_breakdown'].values()
                )
                summary['avg_resolution_time_ms'] = total_time / summary['total_resolutions']
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}


# Global metrics collector instance
metrics_collector = TouchpointMetricsCollector()


@contextmanager
def track_resolution(connector_type: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Context manager to track touchpoint resolution performance.
    
    Usage:
        with track_resolution('web', {'url': '/products'}) as tracker:
            touchpoint = resolver.resolve(web_interaction)
            tracker.record_success(cache_hit=True, mapping_applied=True)
    """
    start_time = time.time()
    metrics = ResolutionMetrics(
        connector_type=connector_type,
        resolution_time_ms=0,
        cache_hit=False,
        mapping_rule_applied=False,
        touchpoint_created=False,
        error_occurred=False,
        metadata=metadata or {}
    )
    
    class Tracker:
        def record_success(self, cache_hit: bool = False, mapping_applied: bool = False, 
                          touchpoint_created: bool = True):
            metrics.cache_hit = cache_hit
            metrics.mapping_rule_applied = mapping_applied
            metrics.touchpoint_created = touchpoint_created
            metrics.resolution_time_ms = (time.time() - start_time) * 1000
            metrics_collector.record_resolution(metrics)
        
        def record_error(self, error_message: str):
            metrics.error_occurred = True
            metrics.error_message = error_message
            metrics.resolution_time_ms = (time.time() - start_time) * 1000
            metrics_collector.record_resolution(metrics)
    
    tracker = Tracker()
    
    try:
        yield tracker
    except Exception as e:
        tracker.record_error(str(e))
        raise


@contextmanager
def track_cache_operation(operation: str, key_pattern: str):
    """
    Context manager to track cache operations.
    
    Usage:
        with track_cache_operation('get', 'touchpoint_mapping:*') as tracker:
            result = cache.get(key)
            tracker.record_success(hit=result is not None)
    """
    start_time = time.time()
    metrics = CacheMetrics(
        operation=operation,
        key_pattern=key_pattern,
        success=False,
        duration_ms=0
    )
    
    class Tracker:
        def record_success(self, hit: bool = True):
            metrics.success = True
            metrics.duration_ms = (time.time() - start_time) * 1000
            metrics.hit_rate = 1.0 if hit else 0.0
            metrics_collector.record_cache_operation(metrics)
        
        def record_failure(self):
            metrics.success = False
            metrics.duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_cache_operation(metrics)
    
    tracker = Tracker()
    
    try:
        yield tracker
    except Exception as e:
        tracker.record_failure()
        raise


def get_metrics_summary(hours: int = 24) -> Dict[str, Any]:
    """Get metrics summary for the last N hours."""
    return metrics_collector.get_performance_summary(hours)


def get_current_metrics() -> Dict[str, Any]:
    """Get current system metrics."""
    return metrics_collector.get_current_metrics()


def flush_metrics():
    """Manually flush metrics buffers."""
    metrics_collector.flush_metrics()
    metrics_collector.flush_cache_metrics()
