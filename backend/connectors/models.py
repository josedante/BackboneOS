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
        """Get the channel from the related interaction"""
        return getattr(self.interaction, "channel", None)

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
            self.metadata
        ]):
            raise ValidationError(
                "At least one override field (touchpoint_code, touchpoint_label, "
                "channel_code, medium_code, or metadata) must be provided."
            )
