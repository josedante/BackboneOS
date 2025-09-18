from django.db import models
from backend.models import BaseUUIDModelWithActiveStatus

class AbstractConnectorInteraction(BaseUUIDModelWithActiveStatus):
    """
    Abstract layer shared by all connector-specific interaction addons.
    Each record is a 1:1 extension of an Interaction row.
    """
    interaction = models.OneToOneField(
        "interactions.Interaction",
        on_delete=models.CASCADE,
        related_name="%(class)s",   # or "connector", overridden in concrete classes
        primary_key=True,
    )

    class Meta:
        abstract = True

    # ---- common helpers (available to all connectors) ----
    @property
    def action_code(self) -> str:
        return getattr(self.interaction.action, "code", "")

    @property
    def tp(self):
        return getattr(self.interaction, "touchpoint_instance", None)

    @property
    def person(self):
        return getattr(self.interaction, "actor_person", None)

    @property
    def organization(self):
        return getattr(self.interaction, "actor_org", None)
