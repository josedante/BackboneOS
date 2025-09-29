# apps/websites/models.py
from __future__ import annotations
import uuid, re
from django.db import models, transaction
from django.conf import settings
from backend.models import BaseUUIDModelWithActiveStatus
from django.utils import timezone
from datetime import timedelta

# Core relations
from interactions.models import TouchpointType, Touchpoint, Channel, Agent
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
    
    # Channel for owned website traffic analysis
    channel = models.ForeignKey("interactions.Channel", on_delete=models.CASCADE, null=True, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return f"{self.name} ({self.base_url})"


# --------------------------
# TouchpointType scaffolding
# --------------------------
def get_or_create_www_channel() -> Channel:
    # Ensure a "WWW" (website) channel exists
    return Channel.objects.get_or_create(code="WWW", defaults={"name": "World Wide Web"})[0]

def get_or_create_tpc(code: str, name: str, channel: Channel) -> TouchpointType:
    return TouchpointType.objects.get_or_create(
        code=code,
        defaults={"name": name}
    )[0]

# def seed_touchpoint_types(apps, schema_editor):
#     Channel = apps.get_model("interactions", "Channel")
#     TouchpointType = apps.get_model("interactions", "TouchpointType")

#     www = Channel.objects.get_or_create(code="WWW", defaults={"name": "World Wide Web"})[0]
#     get_or_create = lambda code, name: TouchpointType.objects.get_or_create(code=code, defaults={"name": name})[0]

#     get_or_create("WWW_PAGE", "Website Page")
#     get_or_create("WWW_FORM", "Website Form")
#     get_or_create("WWW_THANKYOU", "Website Thank You")



# --------------------------
# Removed WebSurface, UrlRoutingRule, and SurfaceResolver models
# These were over-engineered and not actually used in practice.
# Touchpoint resolution works directly with URLs without these abstractions.
# --------------------------


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

class WebSession(BaseUUIDModelWithActiveStatus):
    """
    Represents a web session - a continuous period of user activity.
    
    Sessions are created when:
    - New visitor arrives (first interaction)
    - Session timeout (30+ minutes gap)
    - Cross-domain referrer
    - UTM parameter changes
    """
    
    # Session identity
    session_id = models.CharField(max_length=64, db_index=True, unique=True)
    visitor_cookie = models.CharField(max_length=64, db_index=True)
    
    # Session context
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="sessions")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="web_sessions")
    
    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    # Session attribution (first interaction's UTM data)
    utm_source = models.CharField(max_length=100, blank=True, default="")
    utm_medium = models.CharField(max_length=100, blank=True, default="")
    utm_campaign = models.CharField(max_length=150, blank=True, default="")
    utm_content = models.CharField(max_length=150, blank=True, default="")
    utm_term = models.CharField(max_length=100, blank=True, default="")
    
    # Session metadata
    referrer_url = models.URLField(blank=True, default="")
    landing_page_url = models.URLField(blank=True, default="")
    user_agent = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Session analytics (computed fields)
    page_count = models.PositiveIntegerField(default=0)
    is_bounce = models.BooleanField(default=True)  # Single page session
    conversion_events = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['visitor_cookie', 'started_at']),
            models.Index(fields=['website', 'started_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['utm_source', 'utm_medium']),
        ]
    
    @property
    def duration(self):
        """Get session duration."""
        if self.ended_at:
            return self.ended_at - self.started_at
        return timezone.now() - self.started_at
    
    @property
    def is_session_active(self):
        """Check if session is still active based on ended_at timestamp."""
        if not self.ended_at:
            return True
        return timezone.now() < self.ended_at
    
    def get_interactions(self):
        """Get all interactions in this session."""
        return WebInteraction.objects.filter(session_id=self.session_id)
    
    def get_page_views(self):
        """Get page view interactions in this session."""
        return self.get_interactions().filter(
            interaction__action__code='no_action',
            interaction__payload__interaction_type='page_view'
        )
    
    def get_conversion_events(self):
        """Get conversion events in this session."""
        return self.get_interactions().filter(
            interaction__action__code__in=['form_submit', 'purchase', 'download']
        )
    
    def end_session(self):
        """Mark session as ended."""
        self.ended_at = timezone.now()
        self.save(update_fields=['ended_at'])
    
    def update_activity(self):
        """Update last activity timestamp and extend session."""
        now = timezone.now()
        self.last_activity_at = now
        
        # Extend session if it's still active
        if not self.ended_at or self.ended_at > now:
            self.ended_at = now + timedelta(seconds=settings.WEB_SESSION_DURATION_SECONDS)
            self.save(update_fields=['last_activity_at', 'ended_at'])
        else:
            self.save(update_fields=['last_activity_at'])
    
    def extend_session(self):
        """Extend session duration from now."""
        now = timezone.now()
        self.ended_at = now + timedelta(seconds=settings.WEB_SESSION_DURATION_SECONDS)
        self.last_activity_at = now
        self.save(update_fields=['ended_at', 'last_activity_at'])
    
    @classmethod
    def get_session_end_time(cls):
        """Get the default session end time from now."""
        return timezone.now() + timedelta(seconds=settings.WEB_SESSION_DURATION_SECONDS)
    
    def __str__(self):
        return f"Session {self.session_id[:8]}... ({self.website.name})"


class WebInteraction(AbstractConnectorInteraction):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="events")
    # Note: session relationship will be added in a future migration

    # Browser identity (keep for backward compatibility)
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
        
        TODO: Implement touchpoint inference logic.
        Currently returns a basic hint based on the interaction data.
        
        Returns:
            TouchpointHint: The inferred touchpoint information
        """
        # TODO: Implement proper touchpoint inference
        # For now, return a basic hint
        return TouchpointHint(
            channel_code=self.website.base_url,
            medium_code="web",
            touchpoint_type_code="web_page"
        )
    
    def _ensure_touchpoint(self):
        """
        Ensure this web interaction has a proper touchpoint.
        
        TODO: Implement touchpoint resolution system.
        Currently does nothing - touchpoint resolution needs to be implemented.
        """
        # TODO: Implement touchpoint resolution
        # This method should create or update the touchpoint for this interaction
        pass
    
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
        
        TODO: Implement page view event processing.
        This method should implement the multi-interaction approach where a single
        page view event can create multiple WebInteraction instances:
        1. Page View Interaction (always created)
        2. Referrer Click Interaction (if external referrer exists)
        3. Session Start Interaction (if new session criteria met)
        
        Args:
            event_data: Dictionary containing the page view event data
            
        Returns:
            list: List of created WebInteraction instances
        """
        # TODO: Implement page view event processing
        # For now, return empty list
        return []


# --------------------------
# WebAgent Proxy Model
# --------------------------
class WebAgent(Agent):
    """
    Proxy model for Agent with website-specific functionality.
    
    This proxy model provides website-specific methods and properties
    for Agent instances without creating a separate database table.
    """
    
    class Meta:
        proxy = True
        verbose_name = "Web Agent"
        verbose_name_plural = "Web Agents"
    
    @property
    def browser_family(self) -> str:
        """Get the browser family from metadata."""
        return self.metadata.get('browser', {}).get('family', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def browser_version(self) -> str:
        """Get the browser version from metadata."""
        return self.metadata.get('browser', {}).get('version', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def os_family(self) -> str:
        """Get the operating system family from metadata."""
        return self.metadata.get('os', {}).get('family', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def os_version(self) -> str:
        """Get the operating system version from metadata."""
        return self.metadata.get('os', {}).get('version', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def device_family(self) -> str:
        """Get the device family from metadata."""
        return self.metadata.get('device', {}).get('family', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def device_brand(self) -> str:
        """Get the device brand from metadata."""
        return self.metadata.get('device', {}).get('brand', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def device_model(self) -> str:
        """Get the device model from metadata."""
        return self.metadata.get('device', {}).get('model', 'Unknown') if self.metadata else 'Unknown'
    
    @property
    def is_mobile(self) -> bool:
        """Check if this is a mobile device."""
        if not self.metadata:
            return False
        device_family = self.metadata.get('device', {}).get('family', '').lower()
        return device_family in ['mobile', 'smartphone', 'tablet', 'iphone', 'ipad', 'android']
    
    @property
    def is_bot(self) -> bool:
        """Check if this is a bot/crawler."""
        return self.agent_type == 'bot'
    
    @property
    def is_webview(self) -> bool:
        """Check if this is a WebView (mobile app)."""
        if not self.metadata:
            return False
        browser_family = self.metadata.get('browser', {}).get('family', '').lower()
        return 'webview' in browser_family or self.agent_type == 'device'
    
    @property
    def display_name(self) -> str:
        """Get a user-friendly display name for the agent."""
        if self.agent_type == 'bot':
            return f"Bot: {self.browser_family}"
        elif self.agent_type == 'device':
            return f"{self.device_family} ({self.browser_family})"
        else:  # browser
            return f"{self.browser_family} on {self.os_family}"
    
    @property
    def technical_summary(self) -> str:
        """Get a technical summary of the agent."""
        parts = [f"{self.browser_family} {self.browser_version}"]
        if self.os_family != 'Unknown':
            parts.append(f"on {self.os_family} {self.os_version}")
        if self.device_family != 'Other' and self.device_family != 'Unknown':
            parts.append(f"({self.device_family})")
        return " ".join(parts)
    
    def get_web_interactions(self):
        """Get all WebInteraction instances for this agent."""
        return WebInteraction.objects.filter(interaction__agent=self)
    
    def get_web_interactions_by_website(self, website):
        """Get WebInteraction instances for this agent on a specific website."""
        return WebInteraction.objects.filter(
            interaction__agent=self,
            website=website
        )
    
    def get_session_count(self):
        """Get the number of unique sessions for this agent."""
        return self.get_web_interactions().values('session_id').distinct().count()
    
    def get_website_count(self):
        """Get the number of unique websites this agent has visited."""
        return self.get_web_interactions().values('website').distinct().count()
    
    def get_last_activity(self):
        """Get the last activity timestamp for this agent."""
        last_interaction = self.get_web_interactions().order_by('-created_at').first()
        return last_interaction.created_at if last_interaction else None
    
    def get_activity_summary(self):
        """Get a summary of this agent's activity."""
        interactions = self.get_web_interactions()
        return {
            'total_interactions': interactions.count(),
            'unique_sessions': self.get_session_count(),
            'unique_websites': self.get_website_count(),
            'last_activity': self.get_last_activity(),
            'is_mobile': self.is_mobile,
            'is_bot': self.is_bot,
            'is_webview': self.is_webview
        }
    
    def __str__(self):
        """String representation of the WebAgent."""
        return f"{self.display_name} ({self.technical_summary})"
