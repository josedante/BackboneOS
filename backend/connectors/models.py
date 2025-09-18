from django.db import models


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
