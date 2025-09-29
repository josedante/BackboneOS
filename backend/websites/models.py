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
    def infer_session_for_interaction(cls, web_interaction: 'WebInteraction') -> 'WebSession':
        """
        Infer or create a WebSession for the given WebInteraction.
        
        Simple logic: session continues if within 30 minutes, otherwise create new session.
        
        Args:
            web_interaction: The WebInteraction to infer session for
            
        Returns:
            WebSession: The inferred or created session
        """
        visitor_cookie = web_interaction.visitor_cookie
        website = web_interaction.website
        occurred_at = web_interaction.occurred_at
        
        # Check for existing active session within 30-minute window
        timeout_threshold = occurred_at - timedelta(minutes=30)
        
        # Look for recent session with same visitor cookie
        recent_session = cls.objects.filter(
            visitor_cookie=visitor_cookie,
            website=website,
            last_activity_at__gte=timeout_threshold,
            ended_at__isnull=True
        ).order_by('-last_activity_at').first()
        
        if recent_session:
            # Continue existing session
            recent_session.last_activity_at = occurred_at
            recent_session.page_count += 1
            recent_session.is_bounce = False  # Multiple pages = not a bounce
            recent_session.save()
            return recent_session
        
        # Create new session
        return cls._create_new_session(web_interaction)
    
    @classmethod
    def _create_new_session(cls, web_interaction: 'WebInteraction') -> 'WebSession':
        """
        Create a new WebSession for the given interaction.
        
        Args:
            web_interaction: The WebInteraction to create session for
            
        Returns:
            WebSession: The newly created session
        """
        # Generate unique session ID
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        
        # Create session with interaction data
        session = cls.objects.create(
            session_id=session_id,
            visitor_cookie=web_interaction.visitor_cookie,
            website=web_interaction.website,
            agent=web_interaction.agent,
            started_at=web_interaction.occurred_at,
            last_activity_at=web_interaction.occurred_at,
            utm_source=web_interaction.utm_source,
            utm_medium=web_interaction.utm_medium,
            utm_campaign=web_interaction.utm_campaign,
            utm_content=web_interaction.utm_content,
            utm_term=web_interaction.utm_term,
            referrer_url=web_interaction.payload.get('referrer', ''),
            landing_page_url=web_interaction.payload.get('full_url', ''),
            user_agent=web_interaction.user_agent,
            ip_address=web_interaction.ip,
            page_count=1,
            is_bounce=True  # Will be updated if more pages are viewed
        )
        
        return session
    
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
        
        Provides basic touchpoint inference for backward compatibility.
        For multi-interaction processing, use infer_multi_touchpoint_hints().
        
        Returns:
            TouchpointHint: The inferred touchpoint information
        """
        # Basic touchpoint inference for single interaction
        channel_code = self._get_channel_code()
        medium_code = self._get_medium_code()
        touchpoint_type_code = self._get_touchpoint_type_code()
        
        return TouchpointHint(
            code=f"web.{self.event_type}",
            channel_code=channel_code,
            medium_code=medium_code,
            touchpoint_type_code=touchpoint_type_code,
            label=self._generate_touchpoint_label(),
            metadata=self._extract_metadata()
        )
    
    def infer_multi_touchpoint_hints(self):
        """
        Implement MultiTouchpointInferenceProtocol.
        
        Provides multi-interaction touchpoint inference for the websites app's
        multi-interaction approach (page view, referrer click, session start).
        
        Returns:
            BatchTouchpointHint: Multiple touchpoint hints for coordinated resolution
        """
        from connectors.extended_protocols import BatchTouchpointHint, MultiTouchpointHint
        
        hints = []
        
        # 1. Page View Interaction (always created)
        page_view_hint = self._create_page_view_hint()
        hints.append(page_view_hint)
        
        # 2. Referrer Click Interaction (if external referrer exists)
        if self._has_external_referrer():
            referrer_hint = self._create_referrer_click_hint()
            hints.append(referrer_hint)
        
        # 3. Session Start Interaction (if new session criteria met)
        if self._is_new_session():
            session_hint = self._create_session_start_hint()
            hints.append(session_hint)
        
        return BatchTouchpointHint(
            hints=hints,
            session_id=self.session_id,
            event_data=self._get_event_data(),
            coordination_metadata=self._get_coordination_metadata()
        )
    
    def _ensure_touchpoint(self):
        """
        Ensure this web interaction has a proper touchpoint.
        
        Uses the extended connectors framework for touchpoint resolution.
        """
        from connectors.extended_resolvers import ExtendedTouchpointResolver
        from connectors.extended_mapping_providers import ExtendedDatabaseMappingProvider
        
        # Use extended framework for touchpoint resolution
        resolver = ExtendedTouchpointResolver(ExtendedDatabaseMappingProvider())
        
        # For single interaction, use basic resolution
        if not hasattr(self, 'event_type') or self.event_type != 'page_view':
            # Use basic resolution for non-page-view events
            from connectors.resolvers import DefaultTouchpointResolver
            from connectors.mapping_providers import DatabaseMappingProvider
            
            basic_resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
            touchpoint = basic_resolver.resolve(self)
            self.interaction.touchpoint = touchpoint
            self.interaction.save()
        else:
            # Use batch resolution for page view events
            touchpoints = resolver.resolve_batch(self)
            if touchpoints:
                # Assign the first touchpoint (page view) to this interaction
                self.interaction.touchpoint = touchpoints[0]
                self.interaction.save()
    
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
        
        Implements the multi-interaction approach where a single page view event
        creates multiple WebInteraction instances with coordinated touchpoint resolution.
        
        Args:
            event_data: Dictionary containing the page view event data
            
        Returns:
            list: List of created WebInteraction instances
        """
        from connectors.extended_resolvers import ExtendedTouchpointResolver
        from connectors.extended_mapping_providers import ExtendedDatabaseMappingProvider
        
        # Create the primary page view interaction
        page_view_interaction = cls._create_page_view_interaction(event_data)
        
        # Use extended framework for batch resolution
        resolver = ExtendedTouchpointResolver(ExtendedDatabaseMappingProvider())
        touchpoints = resolver.resolve_batch(page_view_interaction)
        
        # Create additional interactions based on touchpoints
        interactions = [page_view_interaction]
        
        # Create referrer click interaction if needed
        if len(touchpoints) > 1:
            referrer_interaction = cls._create_referrer_click_interaction(event_data, touchpoints[1])
            interactions.append(referrer_interaction)
        
        # Create session start interaction if needed
        if len(touchpoints) > 2:
            session_interaction = cls._create_session_start_interaction(event_data, touchpoints[2])
            interactions.append(session_interaction)
        
        return interactions
    
    # Helper methods for touchpoint inference
    def _get_channel_code(self) -> str:
        """Get channel code from website URL."""
        from urllib.parse import urlparse
        parsed_url = urlparse(self.website.base_url)
        return parsed_url.netloc or self.website.base_url
    
    def _get_medium_code(self) -> str:
        """Get medium code from UTM parameters or referrer analysis."""
        # UTM parameters take precedence
        if self.utm_medium:
            return self.utm_medium
        
        # Analyze referrer if no UTM
        if self.payload.get('referrer'):
            return self._analyze_referrer_medium(self.payload['referrer'])
        
        return 'direct'
    
    def _get_touchpoint_type_code(self) -> str:
        """Get touchpoint type code based on event type."""
        event_type_map = {
            'page_view': 'web_page',
            'page_read': 'web_page',
            'form_submit': 'web_form',
            'click': 'web_button',
            'download': 'web_download',
            'video_play': 'web_video'
        }
        return event_type_map.get(self.event_type, 'web_page')
    
    def _generate_touchpoint_label(self) -> str:
        """Generate human-friendly touchpoint label."""
        event_type = getattr(self, 'event_type', 'interaction')
        return f"Web {event_type.replace('_', ' ').title()}"
    
    def _extract_metadata(self) -> dict:
        """Extract metadata for touchpoint hint."""
        return {
            'website': self.website.base_url,
            'session_id': self.session_id,
            'visitor_cookie': self.visitor_cookie,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'payload': self.payload
        }
    
    def _has_external_referrer(self) -> bool:
        """Check if there's an external referrer."""
        referrer = self.payload.get('referrer', '')
        if not referrer:
            return False
        
        from urllib.parse import urlparse
        referrer_domain = urlparse(referrer).netloc
        website_domain = urlparse(self.website.base_url).netloc
        
        return referrer_domain and referrer_domain != website_domain
    
    def _is_new_session(self) -> bool:
        """
        Check if this interaction represents a new session.
        
        Simple logic: new session if no existing session within 30 minutes.
        """
        # If we already have a session, check if it's new
        if self.session:
            # Check if this is the first interaction in the session
            return self.session.interactions.count() == 0
        
        # If no session yet, we need to infer one
        # This will be called during the inference process
        # For now, assume new session if no session_id
        return not self.session_id
    
    def _get_event_data(self) -> dict:
        """Get event data for batch processing."""
        return {
            'event_type': getattr(self, 'event_type', 'page_view'),
            'website_base': self.website.base_url,
            'session_id': self.session_id,
            'visitor_cookie': self.visitor_cookie,
            'payload': self.payload
        }
    
    def _get_coordination_metadata(self) -> dict:
        """Get coordination metadata for batch processing."""
        return {
            'session_id': self.session_id,
            'visitor_cookie': self.visitor_cookie,
            'website': self.website.base_url,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign
        }
    
    def _create_page_view_hint(self):
        """Create touchpoint hint for page view interaction."""
        from connectors.extended_protocols import MultiTouchpointHint
        
        return MultiTouchpointHint(
            interaction_type='page_view',
            hint=self.infer_touchpoint_hint(),
            session_context={'interaction_type': 'page_view'},
            metadata={'always_created': True}
        )
    
    def _create_referrer_click_hint(self):
        """Create touchpoint hint for referrer click interaction."""
        from connectors.extended_protocols import MultiTouchpointHint, TouchpointHint
        
        # Analyze referrer for channel and medium
        referrer = self.payload.get('referrer', '')
        referrer_domain = self._extract_domain(referrer)
        referrer_medium = self._analyze_referrer_medium(referrer)
        
        return MultiTouchpointHint(
            interaction_type='referrer_click',
            hint=TouchpointHint(
                code='web.referrer_click',
                channel_code=referrer_domain,
                medium_code=referrer_medium,
                touchpoint_type_code='web_referrer',
                label='Referrer Click',
                metadata={'referrer': referrer}
            ),
            session_context={'interaction_type': 'referrer_click'},
            metadata={'conditionally_created': True}
        )
    
    def _create_session_start_hint(self):
        """Create touchpoint hint for session start interaction."""
        from connectors.extended_protocols import MultiTouchpointHint, TouchpointHint
        
        return MultiTouchpointHint(
            interaction_type='session_start',
            hint=TouchpointHint(
                code='web.session_start',
                channel_code=self._get_channel_code(),
                medium_code=self._get_medium_code(),
                touchpoint_type_code='web_session',
                label='Session Start',
                metadata={'session_id': self.session_id}
            ),
            session_context={'interaction_type': 'session_start'},
            metadata={'conditionally_created': True}
        )
    
    def _analyze_referrer_medium(self, referrer: str) -> str:
        """Analyze referrer to determine medium."""
        if not referrer:
            return 'direct'
        
        referrer_lower = referrer.lower()
        
        # Search engines
        if any(engine in referrer_lower for engine in ['google.com', 'bing.com', 'yahoo.com']):
            return 'organic_search'
        
        # Social media
        if any(social in referrer_lower for social in ['facebook.com', 'twitter.com', 'linkedin.com']):
            return 'social_media'
        
        # Email
        if 'mail' in referrer_lower or 'email' in referrer_lower:
            return 'email'
        
        return 'referral'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or 'unknown'
    
    @classmethod
    def _create_page_view_interaction(cls, event_data: dict) -> 'WebInteraction':
        """Create page view interaction from event data."""
        # Implementation for creating page view interaction
        # This would create the actual WebInteraction instance
        pass
    
    @classmethod
    def _create_referrer_click_interaction(cls, event_data: dict, touchpoint) -> 'WebInteraction':
        """Create referrer click interaction from event data."""
        # Implementation for creating referrer click interaction
        pass
    
    @classmethod
    def _create_session_start_interaction(cls, event_data: dict, touchpoint) -> 'WebInteraction':
        """Create session start interaction from event data."""
        # Implementation for creating session start interaction
        pass


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
