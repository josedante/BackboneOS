"""
Database models for storing touchpoint resolution metrics and monitoring data.

These models provide persistent storage for performance metrics,
allowing for historical analysis and reporting.
"""

from django.db import models
from django.utils import timezone
from interactions.models import BaseUUIDModelWithActiveStatus


class TouchpointResolutionMetrics(BaseUUIDModelWithActiveStatus):
    """
    Store aggregated touchpoint resolution metrics for historical analysis.
    """
    
    # Time period
    period_start = models.DateTimeField(help_text="Start of the metrics period")
    period_end = models.DateTimeField(help_text="End of the metrics period")
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='hourly',
        help_text="Type of aggregation period"
    )
    
    # Resolution metrics
    total_resolutions = models.PositiveIntegerField(default=0)
    successful_resolutions = models.PositiveIntegerField(default=0)
    failed_resolutions = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_resolution_time_ms = models.FloatField(default=0.0)
    min_resolution_time_ms = models.FloatField(default=0.0)
    max_resolution_time_ms = models.FloatField(default=0.0)
    p95_resolution_time_ms = models.FloatField(default=0.0)
    p99_resolution_time_ms = models.FloatField(default=0.0)
    
    # Cache metrics
    cache_hit_rate = models.FloatField(default=0.0)
    cache_miss_rate = models.FloatField(default=0.0)
    
    # Mapping rule metrics
    mapping_rules_applied = models.PositiveIntegerField(default=0)
    mapping_rules_created = models.PositiveIntegerField(default=0)
    
    # Connector breakdown (JSON field)
    connector_breakdown = models.JSONField(default=dict, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [
            ('period_start', 'period_end', 'period_type'),
        ]
    
    def __str__(self):
        return f"Metrics {self.period_type} {self.period_start} - {self.period_end}"
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_resolutions == 0:
            return 0.0
        return (self.failed_resolutions / self.total_resolutions) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_resolutions == 0:
            return 0.0
        return (self.successful_resolutions / self.total_resolutions) * 100


class TouchpointResolutionEvent(BaseUUIDModelWithActiveStatus):
    """
    Store individual touchpoint resolution events for detailed analysis.
    """
    
    # Event identification
    connector_type = models.CharField(max_length=50, help_text="Type of connector (web, email, etc.)")
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('resolution', 'Resolution'),
            ('cache_hit', 'Cache Hit'),
            ('cache_miss', 'Cache Miss'),
            ('mapping_applied', 'Mapping Applied'),
            ('error', 'Error'),
        ],
        default='resolution'
    )
    
    # Performance data
    resolution_time_ms = models.FloatField(help_text="Resolution time in milliseconds")
    
    # Context data
    touchpoint_code = models.CharField(max_length=100, blank=True)
    channel_code = models.CharField(max_length=50, blank=True)
    medium_code = models.CharField(max_length=50, blank=True)
    
    # Flags
    cache_hit = models.BooleanField(default=False)
    mapping_rule_applied = models.BooleanField(default=False)
    touchpoint_created = models.BooleanField(default=False)
    error_occurred = models.BooleanField(default=False)
    
    # Error details
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    occurred_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['connector_type', 'occurred_at']),
            models.Index(fields=['event_type', 'occurred_at']),
            models.Index(fields=['error_occurred', 'occurred_at']),
            models.Index(fields=['occurred_at']),
        ]
    
    def __str__(self):
        return f"{self.connector_type} {self.event_type} at {self.occurred_at}"


class TouchpointCacheMetrics(BaseUUIDModelWithActiveStatus):
    """
    Store cache performance metrics.
    """
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Cache operation metrics
    total_operations = models.PositiveIntegerField(default=0)
    get_operations = models.PositiveIntegerField(default=0)
    set_operations = models.PositiveIntegerField(default=0)
    delete_operations = models.PositiveIntegerField(default=0)
    
    # Hit/miss metrics
    cache_hits = models.PositiveIntegerField(default=0)
    cache_misses = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_operation_time_ms = models.FloatField(default=0.0)
    max_operation_time_ms = models.FloatField(default=0.0)
    
    # Cache size metrics
    cache_size_at_start = models.PositiveIntegerField(default=0)
    cache_size_at_end = models.PositiveIntegerField(default=0)
    max_cache_size = models.PositiveIntegerField(default=0)
    
    # Key pattern breakdown
    key_pattern_breakdown = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Cache metrics {self.period_start} - {self.period_end}"
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total_gets = self.get_operations
        if total_gets == 0:
            return 0.0
        return (self.cache_hits / total_gets) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage."""
        total_gets = self.get_operations
        if total_gets == 0:
            return 0.0
        return (self.cache_misses / total_gets) * 100


class TouchpointSystemHealth(BaseUUIDModelWithActiveStatus):
    """
    Store system health metrics for monitoring.
    """
    
    # Timestamp
    recorded_at = models.DateTimeField(default=timezone.now)
    
    # System metrics
    active_mapping_rules = models.PositiveIntegerField(default=0)
    total_touchpoints = models.PositiveIntegerField(default=0)
    total_interactions = models.PositiveIntegerField(default=0)
    
    # Cache metrics
    cache_size = models.PositiveIntegerField(default=0)
    cache_memory_usage_mb = models.FloatField(default=0.0)
    
    # Database metrics
    database_connections = models.PositiveIntegerField(default=0)
    slow_queries_count = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_resolution_time_ms = models.FloatField(default=0.0)
    error_rate = models.FloatField(default=0.0)
    
    # Resource usage
    memory_usage_mb = models.FloatField(default=0.0)
    cpu_usage_percent = models.FloatField(default=0.0)
    
    # Health status
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Additional metrics
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['recorded_at']),
            models.Index(fields=['health_status', 'recorded_at']),
        ]
    
    def __str__(self):
        return f"System health {self.health_status} at {self.recorded_at}"


class TouchpointAlert(BaseUUIDModelWithActiveStatus):
    """
    Store alerts and notifications for system monitoring.
    """
    
    # Alert identification
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('high_error_rate', 'High Error Rate'),
            ('slow_resolution', 'Slow Resolution'),
            ('cache_miss_rate', 'High Cache Miss Rate'),
            ('system_health', 'System Health'),
            ('mapping_rule_issue', 'Mapping Rule Issue'),
        ]
    )
    
    # Alert details
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Context
    connector_type = models.CharField(max_length=50, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('acknowledged', 'Acknowledged'),
            ('resolved', 'Resolved'),
            ('dismissed', 'Dismissed'),
        ],
        default='active'
    )
    
    # Timestamps
    triggered_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_type}: {self.title}"
    
    def acknowledge(self):
        """Mark alert as acknowledged."""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self):
        """Mark alert as resolved."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def dismiss(self):
        """Mark alert as dismissed."""
        self.status = 'dismissed'
        self.save()
