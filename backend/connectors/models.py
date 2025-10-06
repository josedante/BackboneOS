from django.db import models
from backend.models import BaseUUIDModelWithActiveStatus


class AbstractConnectorInteraction(models.Model):
    """
    Abstract layer shared by all connector-specific interaction addons.
    Each record is a 1:1 extension of an Interaction row.
    
    This base class provides:
    - Consistent relationship with interactions.Interaction
    - Common helper properties for accessing related data
    - Standard UUID and active status fields
    """
    interaction = models.OneToOneField(
        "interactions.Interaction",
        on_delete=models.CASCADE,
        related_name="%(class)s",  # Dynamic related_name based on subclass
        primary_key=True,
    )
    
    # Active status field (since we're not inheriting from BaseUUIDModelWithActiveStatus)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    # ---- common helpers (available to all connectors) ----
    @property
    def action_code(self) -> str:
        """Get the action code from the related interaction"""
        return getattr(self.interaction.action, "code", "")

    @property
    def touchpoint(self):
        """Get the touchpoint from the related interaction"""
        return getattr(self.interaction, "touchpoint", None)

    @property
    def person(self):
        """Get the person from the related interaction"""
        return getattr(self.interaction, "person", None)

    @property
    def organization(self):
        """Get the organization from the related interaction"""
        return getattr(self.interaction, "organization", None)

    @property
    def agent(self):
        """Get the agent from the related interaction"""
        return getattr(self.interaction, "agent", None)

    @property
    def channel(self):
        """Get the channel from the related interaction's touchpoint"""
        return getattr(self.interaction.touchpoint, "channel", None) if self.interaction.touchpoint else None

    @property
    def occurred_at(self):
        """Get the occurred_at timestamp from the related interaction"""
        return getattr(self.interaction, "occurred_at", None)

    def __str__(self):
        return f"{self.__class__.__name__} for {self.interaction}"


class TouchpointMappingRule(BaseUUIDModelWithActiveStatus):
    """
    Configurable mapping rules for touchpoint resolution.
    
    This model allows administrators to override default touchpoint creation logic
    without code changes. Rules can be configured for specific connector types,
    source identifiers (like website URLs), and event codes.
    
    The mapping rules follow a priority-based resolution system:
    1. Specific source + event code (highest priority)
    2. Generic connector type + event code
    3. Generic event code only (lowest priority)
    """
    
    # Scope - which connector/source this applies to
    connector_type = models.CharField(
        max_length=50,
        help_text="Type of connector (e.g., 'web', 'email', 'whatsapp')"
    )
    source_identifier = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Specific source identifier (e.g., website URL, email domain)"
    )
    
    # Event matching
    event_code = models.CharField(
        max_length=100,
        help_text="Event code to match (e.g., 'web.page_read', 'email.open')"
    )
    
    # Resulting touchpoint configuration
    touchpoint_code = models.CharField(
        max_length=100,
        help_text="Touchpoint code to create (e.g., 'web.lead_form')"
    )
    touchpoint_label = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Human-friendly label for the touchpoint"
    )
    channel_code = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Channel code override (e.g., 'web', 'email')"
    )
    medium_code = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Medium code override (e.g., 'organic', 'paid', 'referral')"
    )
    touchpoint_type_code = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Touchpoint type code override (e.g., 'landing_page', 'form', 'chat')"
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional metadata to include in the touchpoint"
    )
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Rule priority (higher = more specific)"
    )
    
    class Meta:
        ordering = ['-priority', 'connector_type', 'event_code']
        indexes = [
            models.Index(fields=['connector_type', 'event_code']),
            models.Index(fields=['source_identifier', 'event_code']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_active']),
        ]
        unique_together = [
            ('connector_type', 'source_identifier', 'event_code'),
        ]
        verbose_name = "Touchpoint Mapping Rule"
        verbose_name_plural = "Touchpoint Mapping Rules"
    
    def __str__(self):
        source_part = f":{self.source_identifier}:" if self.source_identifier else "::"
        return f"{self.connector_type}{source_part}{self.event_code} -> {self.touchpoint_code}"
    
    def clean(self):
        """Validate the mapping rule."""
        from django.core.exceptions import ValidationError
        
        # Ensure at least one of the override fields is provided
        if not any([
            self.touchpoint_code,
            self.touchpoint_label,
            self.channel_code,
            self.medium_code,
            self.touchpoint_type_code,
            self.metadata
        ]):
            raise ValidationError(
                "At least one override field (touchpoint_code, touchpoint_label, "
                "channel_code, medium_code, touchpoint_type_code, or metadata) must be provided."
            )


class FailedEvent(BaseUUIDModelWithActiveStatus):
    """
    Fallback storage for events that failed to process.
    
    This model serves as a safety net to prevent data loss when event processing
    fails. Events stored here can be retried automatically via background workers
    or manually reprocessed through the admin interface.
    
    Status Flow:
    pending → processing → (success | failed | abandoned)
    """
    
    # Event identification
    connector_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Type of connector (e.g., 'web', 'email', 'whatsapp')"
    )
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Type of event (e.g., 'page_view', 'email_open', 'message_received')"
    )
    source_identifier = models.CharField(
        max_length=200,
        blank=True,
        help_text="Source identifier (e.g., website URL, email domain)"
    )
    
    # Raw event data (preserved exactly as received)
    raw_payload = models.JSONField(
        help_text="Complete raw event data as received"
    )
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending Retry'),
        ('processing', 'Currently Processing'),
        ('success', 'Successfully Processed'),
        ('failed', 'Failed (Will Retry)'),
        ('abandoned', 'Abandoned (Max Retries Exceeded)'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Latest error message"
    )
    error_trace = models.TextField(
        blank=True,
        help_text="Full stack trace of the error"
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of retry attempts"
    )
    
    # Timing
    first_failed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this event first failed"
    )
    last_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last retry attempt timestamp"
    )
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Scheduled next retry time (exponential backoff)"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When successfully processed"
    )
    
    # Result tracking (if successfully processed)
    interaction_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="IDs of interactions created when successfully processed"
    )
    
    class Meta:
        ordering = ['-first_failed_at']
        indexes = [
            models.Index(fields=['connector_type', 'status']),
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['is_active', 'status']),
        ]
        verbose_name = "Failed Event"
        verbose_name_plural = "Failed Events"
    
    def __str__(self):
        return f"{self.connector_type}.{self.event_type} - {self.status} (retries: {self.retry_count})"
    
    def get_max_retries(self) -> int:
        """
        Get maximum retry attempts for this event based on connector type.
        
        Uses FAILED_EVENT_RETRY_CONFIG from settings to determine max retries
        per connector type. Falls back to 'default' if connector type not configured.
        
        Returns:
            int: Maximum number of retry attempts
        """
        from django.conf import settings
        
        config = getattr(settings, 'FAILED_EVENT_RETRY_CONFIG', {'default': 5})
        return config.get(self.connector_type, config.get('default', 5))
    
    def calculate_next_retry(self):
        """
        Calculate next retry time using exponential backoff.
        
        Retry intervals:
        - 1st retry: 1 minute
        - 2nd retry: 5 minutes
        - 3rd retry: 15 minutes
        - 4th retry: 1 hour
        - 5th retry: 6 hours
        """
        from django.utils import timezone
        from datetime import timedelta
        
        backoff_intervals = [
            timedelta(minutes=1),   # 1 minute
            timedelta(minutes=5),   # 5 minutes
            timedelta(minutes=15),  # 15 minutes
            timedelta(hours=1),     # 1 hour
            timedelta(hours=6),     # 6 hours
        ]
        
        if self.retry_count < len(backoff_intervals):
            interval = backoff_intervals[self.retry_count]
        else:
            interval = timedelta(hours=24)  # Daily retries after max backoff
        
        return timezone.now() + interval
    
    def mark_processing(self):
        """Mark event as currently being processed."""
        self.status = 'processing'
        self.save(update_fields=['status'])
    
    def mark_success(self, interaction_ids: list):
        """Mark event as successfully processed."""
        from django.utils import timezone
        
        self.status = 'success'
        self.interaction_ids = interaction_ids
        self.processed_at = timezone.now()
        self.error_message = ''
        self.error_trace = ''
        self.save(update_fields=['status', 'interaction_ids', 'processed_at', 'error_message', 'error_trace'])
    
    def mark_failed(self, error_message: str, error_trace: str = ''):
        """Mark event as failed and schedule next retry."""
        from django.utils import timezone
        
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        self.error_message = error_message[:5000]  # Truncate if too long
        self.error_trace = error_trace[:10000]  # Truncate stack trace
        
        max_retries = self.get_max_retries()
        
        if self.retry_count >= max_retries:
            self.status = 'abandoned'
            self.next_retry_at = None
        else:
            self.status = 'failed'
            self.next_retry_at = self.calculate_next_retry()
        
        self.save(update_fields=['retry_count', 'last_retry_at', 'error_message', 'error_trace', 'status', 'next_retry_at'])


# Monitoring models are defined in monitoring_models.py
# They are imported separately to avoid circular imports

# Import monitoring models for Django to detect them
from .monitoring_models import (
    TouchpointResolutionMetrics,
    TouchpointResolutionEvent,
    TouchpointCacheMetrics,
    TouchpointSystemHealth,
    TouchpointAlert
)
