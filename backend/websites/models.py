# apps/websites/models.py
from __future__ import annotations
import uuid, re
from django.db import models, transaction
from backend.models import BaseUUIDModelWithActiveStatus
from django.utils import timezone

# Core relations
from interactions.models import TouchpointClass, Touchpoint, Channel
from products.models import Product  # optional
from connectors.base import AbstractConnectorInteraction
from connectors.protocols import TouchpointInferenceProtocol, TouchpointHint
# from offers.models import ProductOffering  # optional

# --------------------------
# Website (ownership flexible)
# --------------------------
class Website(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=150)
    base_url = models.URLField(unique=True)
    # If you prefer a simple FK: 
    division = models.ForeignKey("our_institution.Division", on_delete=models.CASCADE)
    # Here we keep it flexible: 1 site ↔ many divisions if needed
    # divisions = models.ManyToManyField('our_institution.Division', through='WebsiteOwnership', blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return f"{self.name} ({self.base_url})"


# --------------------------
# TouchpointClass scaffolding
# --------------------------
def get_or_create_www_channel() -> Channel:
    # Ensure a "WWW" (website) channel exists
    return Channel.objects.get_or_create(code="WWW", defaults={"name": "World Wide Web"})[0]

def get_or_create_tpc(code: str, name: str, channel: Channel) -> TouchpointClass:
    return TouchpointClass.objects.get_or_create(
        code=code,
        defaults={"name": name, "channel": channel}
    )[0]

# def seed_touchpoint_classes(apps, schema_editor):
#     Channel = apps.get_model("interactions", "Channel")
#     TouchpointClass = apps.get_model("interactions", "TouchpointClass")

#     www = Channel.objects.get_or_create(code="WWW", defaults={"name": "World Wide Web"})[0]
#     get_or_create = lambda code, name: TouchpointClass.objects.get_or_create(code=code, defaults={"name": name, "channel": www})[0]

#     get_or_create("WWW_PAGE", "Website Page")
#     get_or_create("WWW_FORM", "Website Form")
#     get_or_create("WWW_THANKYOU", "Website Thank You")



# --------------------------
# Abstract web surface
# --------------------------
class WebSurface(BaseUUIDModelWithActiveStatus):
    """
    One URL-addressable surface on the website (a page or a form).
    Owns a Touchpoint to integrate with the core interactions model.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="surfaces")

    # URL addressing
    path = models.CharField(max_length=512, help_text="Path starting with '/', e.g. /products/crm")
    exact_match = models.BooleanField(default=True, help_text="If False, acts as a prefix")
    # Optional regex alternative (if you want), but keep it off for performance by default
    regex = models.CharField(max_length=512, blank=True, default="", help_text="Optional regex to match paths")

    # Business semantics
    title = models.CharField(max_length=200, blank=True, default="")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    # offering = models.ForeignKey(ProductOffering, null=True, blank=True, on_delete=models.SET_NULL)

    # TouchpointClass linking
    touchpoint_class = models.ForeignKey(TouchpointClass, on_delete=models.PROTECT, related_name="web_surfaces")
    touchpoint = models.OneToOneField(
        Touchpoint,
        on_delete=models.CASCADE,
        related_name="web_surface",
        null=True, blank=True,
    )

    # Flags
    is_thankyou = models.BooleanField(default=False)
    is_form = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("website", "path", "is_form", "is_thankyou")]
        indexes = [
            models.Index(fields=["website", "path"]),
            models.Index(fields=["touchpoint_class"]),
            models.Index(fields=["is_form", "is_thankyou"]),
        ]
        ordering = ["website__name", "path"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(path__startswith="/"),
                name="websurface_path_starts_with_slash",
            ),
        ]
    
    @property
    def canonical_url(self) -> str:
        return f"{self.website.base_url.rstrip('/')}{self.path}"

    def __str__(self): return f"{self.website.name}:{self.path}"

    def matches(self, path: str) -> bool:
        if self.regex:
            return bool(re.match(self.regex, path))
        if self.exact_match:
            return path == self.path
        return path.startswith(self.path.rstrip("/"))

    def ensure_tpi(self):
        """
        Create or update the Touchpoint this surface owns.
        """
        if self.touchpoint_id:
            return self.touchpoint

        # Create a minimal TPI capturing the canonical URL
        # (Assumes TPI has fields like url/title/metadata; if not, store in metadata.)
        tpi = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            title=self.title or self.path,
            # If your TPI model has no URL field, put it into metadata JSON:
            # metadata={"url_path": self.path, "is_form": self.is_form, "is_thankyou": self.is_thankyou}
        )
        self.touchpoint = tpi
        self.save(update_fields=["touchpoint"])
        return tpi


# --------------------------
# Specializations (optional concrete classes)
# --------------------------
class WebPage(WebSurface):
    class Meta:
        proxy = True
    # no extra db table; purely ergonomic

class WebForm(WebSurface):
    class Meta:
        proxy = True
    # no extra db table; purely ergonomic


# --------------------------
# Router rules (fast mapping URL -> WebSurface)
# --------------------------
class UrlRoutingRule(BaseUUIDModelWithActiveStatus):
    PREFIX = "prefix"
    REGEX = "regex"
    EXACT = "exact"
    KIND_CHOICES = [(EXACT, "Exact"), (PREFIX, "Prefix"), (REGEX, "Regex")]

    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="routing_rules")
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=EXACT)
    pattern = models.CharField(max_length=512)
    surface = models.ForeignKey(WebSurface, on_delete=models.CASCADE, related_name="routing_rules")
    priority = models.PositiveIntegerField(default=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "id"]
        unique_together = [("website", "pattern", "surface")]

    def __str__(self): return f"{self.website}:{self.kind}:{self.pattern} -> {self.surface_id}"


# --------------------------
# Resolver API (service-like helpers)
# --------------------------
class SurfaceResolver:
    @staticmethod
    def resolve(website: Website, path: str) -> WebSurface | None:
        # 1) Fast path: direct surface match
        for s in WebSurface.objects.filter(website=website, is_form=False).only("id", "path", "exact_match", "regex"):
            if s.matches(path):
                return s
        # 2) Rules
        rules = UrlRoutingRule.objects.filter(website=website, active=True).select_related("surface")
        for r in rules:
            if r.kind == UrlRoutingRule.EXACT and path == r.pattern:
                return r.surface
            if r.kind == UrlRoutingRule.PREFIX and path.startswith(r.pattern.rstrip("/")):
                return r.surface
            if r.kind == UrlRoutingRule.REGEX and re.match(r.pattern, path):
                return r.surface
        return None


# class Website(models.Model):
#     name = models.CharField(max_length=150)
#     base_url = models.URLField(unique=True)
#     # Option A: flexible ownership
#     divisions = models.ManyToManyField("our_institution.Division", through="WebsiteOwnership", blank=True)
#     active = models.BooleanField(default=True)

# class WebsiteOwnership(models.Model):
#     website = models.ForeignKey(Website, on_delete=models.CASCADE)
#     division = models.ForeignKey("our_institution.Division", on_delete=models.CASCADE)
#     role = models.CharField(max_length=20, default="PRIMARY")  # or choices

class WebInteraction(AbstractConnectorInteraction):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="events")

    # Browser identity
    session_id = models.CharField(max_length=64, db_index=True, blank=True, default="")
    visitor_cookie = models.CharField(max_length=64, db_index=True, blank=True, default="")
    user_agent = models.TextField(blank=True, default="")
    client_hints = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    # Attribution (denorm; normalize in workers if you have dims)
    utm_source = models.CharField(max_length=100, blank=True, default="")
    utm_medium = models.CharField(max_length=100, blank=True, default="")
    utm_campaign = models.CharField(max_length=150, blank=True, default="")
    utm_content = models.CharField(max_length=150, blank=True, default="")
    utm_term = models.CharField(max_length=100, blank=True, default="")

    # Event extras
    element = models.CharField(max_length=200, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)


    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["visitor_cookie"]),
            models.Index(fields=["utm_source", "utm_medium", "utm_campaign"]),
        ]
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        """
        Implement TouchpointInferenceProtocol.
        
        Delegates to specialized web adapter for touchpoint inference.
        
        Returns:
            TouchpointHint: The inferred touchpoint information
        """
        from .adapters import infer_web_touchpoint_hint
        return infer_web_touchpoint_hint(self)
    
    def _ensure_touchpoint(self):
        """
        Ensure this web interaction has a proper touchpoint.
        
        Uses the new touchpoint resolution system to automatically
        create or update the touchpoint for this web interaction.
        """
        if not self.interaction.touchpoint_id:
            from .resolvers import WebTouchpointResolver
            from .mapping_providers import WebMappingProvider
            
            resolver = WebTouchpointResolver(WebMappingProvider())
            touchpoint = resolver.resolve(self)
            
            self.interaction.touchpoint = touchpoint
            self.interaction.save(update_fields=['touchpoint'])
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure touchpoint resolution.
        
        Automatically resolves and assigns a touchpoint when the
        web interaction is saved.
        """
        super().save(*args, **kwargs)
        self._ensure_touchpoint()
    
    @classmethod
    def process_page_view_event(cls, event_data: dict) -> list:
        """
        Process a page view event and create up to 3 interactions.
        
        This method implements the multi-interaction approach where a single
        page view event can create multiple WebInteraction instances:
        1. Page View Interaction (always created)
        2. Referrer Click Interaction (if external referrer exists)
        3. Session Start Interaction (if new session criteria met)
        
        Args:
            event_data: Dictionary containing the page view event data
            
        Returns:
            list: List of created WebInteraction instances
        """
        from django.db import transaction
        from interactions.models import Action, Agent
        from .processors import PageViewEventProcessor
        
        with transaction.atomic():
            processor = PageViewEventProcessor(event_data)
            return processor.process()
