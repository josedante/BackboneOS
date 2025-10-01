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
from connectors.protocols import TouchpointHint
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
    
    def save(self, *args, **kwargs):
        """Override save to automatically create channel for owned websites."""
        # Create channel if it doesn't exist
        if not self.channel:
            self.channel = self._get_or_create_website_channel()
        
        super().save(*args, **kwargs)
    
    def _get_or_create_website_channel(self):
        """Get or create a channel for this owned website."""
        from interactions.models import Channel
        from urllib.parse import urlparse
        
        # Extract domain from base_url for channel code
        parsed_url = urlparse(self.base_url)
        domain = parsed_url.netloc or parsed_url.path
        
        # Create a channel code from the domain
        # Remove www. prefix and convert to uppercase for consistency
        channel_code = domain.replace('www.', '').upper()
        
        # Create channel with website-specific parameters
        channel, created = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': f"{self.name} Website",
                'description': f"Owned website channel for {self.name}",
                'source_type': 'owned',
                'active': True
            }
        )
        
        return channel
    
    def get_channel_code(self):
        """Get the channel code for this website."""
        if self.channel:
            return self.channel.code
        return None
    
    def ensure_channel(self):
        """Ensure this website has a channel, creating one if needed."""
        if not self.channel:
            self.channel = self._get_or_create_website_channel()
            self.save(update_fields=['channel'])
        return self.channel

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
    
    @classmethod
    def process_page_read_event(cls, event_data: dict) -> list:
        """Process a page read event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for page read interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for page read
        action, _ = Action.objects.get_or_create(
            code='page_read',
            defaults={
                'name': 'Page Read',
                'description': 'User meaningfully engaged with page content',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction with proper Interaction creation order
        web_interaction = cls._create_web_interaction_with_interaction(
            event_data=event_data,
            agent=agent,
            action=action,
            interaction_payload={
                'interaction_type': 'page_read',
                'full_url': event_data.get('full_url', ''),
                'time_on_page': event_data.get('payload', {}).get('time_on_page'),
                'scroll_depth': event_data.get('payload', {}).get('scroll_depth'),
                'read_criteria_met': event_data.get('payload', {}).get('read_criteria_met'),
                'word_count': event_data.get('payload', {}).get('word_count'),
                'interactions_count': event_data.get('payload', {}).get('interactions_count')
            },
            website=website
        )
        
        return [web_interaction]
    
    @classmethod
    def process_click_event(cls, event_data: dict) -> list:
        """
        Process a click event using the simplified creation flow.
        
        Flow: Channel/Medium/TouchpointType → Touchpoint → Action → Interaction → WebInteraction
        """
        from interactions.models import Action
        from connectors.resolvers import DefaultTouchpointResolver
        from connectors.mapping_providers import DatabaseMappingProvider
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for click interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Step 1: Build TouchpointHint from event data
        hint = cls.build_touchpoint_hint_from_event_data(event_data, website)
        
        # Step 2: Resolve Touchpoint (creates Channel, Medium, TouchpointType if needed)
        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        touchpoint = resolver.resolve(
            hint,
            connector_type='web',
            source_identifier=website.base_url
        )
        
        # Step 3: Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Step 4: Get or create Action
        action, _ = Action.objects.get_or_create(
            code='click',
            defaults={
                'name': 'Click',
                'description': 'User clicked on an element',
                'action_type': None
            }
        )
        
        # Step 5: Create Interaction and WebInteraction with touchpoint
        web_interaction = cls._create_web_interaction_with_interaction(
            event_data=event_data,
            agent=agent,
            action=action,
            touchpoint=touchpoint,
            interaction_payload={
                'interaction_type': 'click',
                'full_url': event_data.get('full_url', ''),
                'clicked_element': event_data.get('payload', {}).get('clicked_element'),
                'element_id': event_data.get('payload', {}).get('element_id'),
                'element_class': event_data.get('payload', {}).get('element_class'),
                'click_position': event_data.get('payload', {}).get('click_position'),
                'target_url': event_data.get('payload', {}).get('target_url'),
                'text_content': event_data.get('payload', {}).get('text_content')
            },
            website=website
        )
        
        return [web_interaction]
    
    @classmethod
    def process_form_submit_event(cls, event_data: dict) -> list:
        """Process a form submission event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for form submission interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for form submission
        action, _ = Action.objects.get_or_create(
            code='form_submit',
            defaults={
                'name': 'Form Submit',
                'description': 'User submitted a form',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            payload={
                'interaction_type': 'form_submit',
                'full_url': event_data.get('full_url', ''),
                'form_id': event_data.get('payload', {}).get('form_id'),
                'form_type': event_data.get('payload', {}).get('form_type'),
                'fields_submitted': event_data.get('payload', {}).get('fields_submitted'),
                'form_data': event_data.get('payload', {}).get('form_data')
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return [web_interaction]
    
    @classmethod
    def process_download_event(cls, event_data: dict) -> list:
        """Process a download event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for download interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for download
        action, _ = Action.objects.get_or_create(
            code='download',
            defaults={
                'name': 'Download',
                'description': 'User downloaded a file',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            payload={
                'interaction_type': 'download',
                'full_url': event_data.get('full_url', ''),
                'file_name': event_data.get('payload', {}).get('file_name'),
                'file_type': event_data.get('payload', {}).get('file_type'),
                'file_size': event_data.get('payload', {}).get('file_size'),
                'download_url': event_data.get('payload', {}).get('download_url')
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return [web_interaction]
    
    @classmethod
    def process_video_play_event(cls, event_data: dict) -> list:
        """Process a video play event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for video play interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for video play
        action, _ = Action.objects.get_or_create(
            code='video_play',
            defaults={
                'name': 'Video Play',
                'description': 'User played a video',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            payload={
                'interaction_type': 'video_play',
                'full_url': event_data.get('full_url', ''),
                'video_id': event_data.get('payload', {}).get('video_id'),
                'video_title': event_data.get('payload', {}).get('video_title'),
                'video_duration': event_data.get('payload', {}).get('video_duration'),
                'video_source': event_data.get('payload', {}).get('video_source'),
                'play_position': event_data.get('payload', {}).get('play_position')
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return [web_interaction]
    
    @classmethod
    def process_search_event(cls, event_data: dict) -> list:
        """Process a search event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for search interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for search
        action, _ = Action.objects.get_or_create(
            code='search',
            defaults={
                'name': 'Search',
                'description': 'User performed a search',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            payload={
                'interaction_type': 'search',
                'full_url': event_data.get('full_url', ''),
                'search_query': event_data.get('payload', {}).get('search_query'),
                'search_results_count': event_data.get('payload', {}).get('search_results_count'),
                'search_category': event_data.get('payload', {}).get('search_category'),
                'filters_applied': event_data.get('payload', {}).get('filters_applied')
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return [web_interaction]
    
    @classmethod
    def process_newsletter_signup_event(cls, event_data: dict) -> list:
        """Process a newsletter signup event and create a single interaction."""
        from interactions.models import Interaction, Action
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for newsletter signup interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': cls._extract_domain(website_base),
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for newsletter signup
        action, _ = Action.objects.get_or_create(
            code='newsletter_signup',
            defaults={
                'name': 'Newsletter Signup',
                'description': 'User signed up for newsletter',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            payload={
                'interaction_type': 'newsletter_signup',
                'full_url': event_data.get('full_url', ''),
                'email': event_data.get('payload', {}).get('email'),
                'newsletter_type': event_data.get('payload', {}).get('newsletter_type'),
                'interests': event_data.get('payload', {}).get('interests'),
                'source_page': event_data.get('payload', {}).get('source_page')
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return [web_interaction]
    
    @classmethod
    def build_touchpoint_hint_from_event_data(cls, event_data: dict, website) -> 'TouchpointHint':
        """
        Build a TouchpointHint from raw event data without requiring a WebInteraction instance.
        
        This method extracts all the necessary touchpoint information from the event payload,
        allowing touchpoint resolution before creating the Interaction and WebInteraction.
        
        Args:
            event_data: Event data dictionary from client
            website: Website instance
            
        Returns:
            TouchpointHint: Hint for touchpoint resolution
        """
        from connectors.protocols import TouchpointHint
        
        # Determine channel code
        channel_code = website.channel.code if website.channel else cls._extract_domain(website.base_url)
        
        # Determine medium code from UTM or referrer
        medium_code = event_data.get('utm_medium')
        if not medium_code:
            referrer = event_data.get('referrer', '')
            medium_code = cls._analyze_referrer_medium(referrer)
        
        # Determine touchpoint type from event type
        event_type = event_data.get('event_type', 'page_view')
        touchpoint_type_map = {
            'page_view': 'web_page',
            'page_read': 'web_page',
            'form_submit': 'web_form',
            'click': 'web_button',
            'download': 'web_download',
            'video_play': 'web_video',
            'search': 'web_search',
            'newsletter_signup': 'web_signup',
        }
        touchpoint_type_code = touchpoint_type_map.get(event_type, 'web_page')
        
        return TouchpointHint(
            code=f"web.{event_type}",
            channel_code=channel_code,
            medium_code=medium_code,
            touchpoint_type_code=touchpoint_type_code,
            label=f"Web {event_type.replace('_', ' ').title()}",
            metadata={
                'website': website.base_url,
                'session_id': event_data.get('session_id', ''),
                'visitor_cookie': event_data.get('visitor_cookie', ''),
                'utm_source': event_data.get('utm_source', ''),
                'utm_medium': event_data.get('utm_medium', ''),
                'utm_campaign': event_data.get('utm_campaign', ''),
                'payload': event_data.get('payload', {}),
            }
        )
    
    @classmethod
    def _create_web_interaction_with_interaction(
        cls, 
        event_data: dict, 
        agent, 
        action, 
        interaction_payload: dict, 
        website, 
        touchpoint=None,
        **web_interaction_kwargs
    ) -> 'WebInteraction':
        """
        Helper method to create WebInteraction with proper creation order.
        
        This method follows the simplified flow:
        1. Touchpoint (with Channel, Medium, TouchpointType) - created before calling this method
        2. Interaction - created with touchpoint already assigned
        3. WebInteraction - created with interaction as primary key
        
        Args:
            event_data: Event data dictionary
            agent: Agent instance
            action: Action instance
            interaction_payload: Payload for the Interaction
            website: Website instance
            touchpoint: Optional pre-resolved Touchpoint instance
            **web_interaction_kwargs: Additional kwargs for WebInteraction
            
        Returns:
            WebInteraction: The created web interaction
        """
        from interactions.models import Interaction
        
        # Create core Interaction with touchpoint (if provided)
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            touchpoint=touchpoint,  # Touchpoint resolved before creation
            payload=interaction_payload,
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create WebInteraction with the interaction as primary key
        web_interaction = cls.objects.create(
            interaction=interaction,  # This is the primary key
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload=event_data.get('payload', {}),
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            **web_interaction_kwargs
        )
        
        return web_interaction
    
    # Helper methods for touchpoint inference
    def _get_channel_code(self) -> str:
        """Get channel code from website's channel or fallback to URL."""
        # Use the website's channel if available
        if self.website.channel:
            return self.website.channel.code
        
        # Fallback to extracting from URL (for backward compatibility)
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
    
    @classmethod
    def _extract_domain(cls, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or 'unknown'
    
    @classmethod
    def _create_page_view_interaction(cls, event_data: dict) -> 'WebInteraction':
        """Create page view interaction from event data."""
        from interactions.models import Interaction, Action
        from interactions.models import Agent
        from urllib.parse import urlparse
        import uuid
        
        # Get or create Website
        website_base = event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required for page view interaction")
        
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': urlparse(website_base).netloc or website_base,
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent from user agent
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action
        action, _ = Action.objects.get_or_create(
            code='no_action',
            defaults={
                'name': 'No Action',
                'description': 'Inferred event with no specific action',
                'action_type': None  # System action
            }
        )
        
        # Create WebInteraction with proper Interaction creation order
        # Note: touchpoint resolution is handled by the multi-interaction approach
        web_interaction = cls._create_web_interaction_with_interaction(
            event_data=event_data,
            agent=agent,
            action=action,
            interaction_payload={
                'interaction_type': 'page_view',
                'full_url': event_data.get('full_url', ''),
                'referrer': event_data.get('referrer', ''),
                'page_title': event_data.get('payload', {}).get('page_title', ''),
                'page_category': event_data.get('payload', {}).get('page_category', ''),
                'load_time': event_data.get('payload', {}).get('load_time'),
                'is_landing_page': event_data.get('payload', {}).get('is_landing_page', False),
                'page_depth': event_data.get('payload', {}).get('page_depth', 1)
            },
            website=website,
            resolve_touchpoint=False  # Handled by multi-interaction approach
        )
        
        return web_interaction
    
    @classmethod
    def _create_referrer_click_interaction(cls, event_data: dict, touchpoint) -> 'WebInteraction':
        """Create referrer click interaction from event data."""
        from interactions.models import Interaction, Action
        from urllib.parse import urlparse
        
        # Get or create Website (same as page view)
        website_base = event_data.get('website_base')
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': urlparse(website_base).netloc or website_base,
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent (same as page view)
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for external click
        action, _ = Action.objects.get_or_create(
            code='external_click',
            defaults={
                'name': 'External Click',
                'description': 'Click from external referrer',
                'action_type': 'digital'
            }
        )
        
        # Create WebInteraction for referrer click
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload={
                **event_data.get('payload', {}),
                'referrer_url': event_data.get('referrer', ''),
                'referrer_domain': cls._extract_domain(event_data.get('referrer', '')),
                'interaction_type': 'referrer_click'
            },
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            touchpoint=touchpoint,
            payload={
                'interaction_type': 'referrer_click',
                'referrer_url': event_data.get('referrer', ''),
                'referrer_domain': cls._extract_domain(event_data.get('referrer', '')),
                'referrer_title': event_data.get('payload', {}).get('referrer_title', ''),
                'referrer_description': event_data.get('payload', {}).get('referrer_description', ''),
                'click_source': 'external'
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return web_interaction
    
    @classmethod
    def _create_session_start_interaction(cls, event_data: dict, touchpoint) -> 'WebInteraction':
        """Create session start interaction from event data."""
        from interactions.models import Interaction, Action
        from urllib.parse import urlparse
        
        # Get or create Website (same as page view)
        website_base = event_data.get('website_base')
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': urlparse(website_base).netloc or website_base,
                'division': cls._get_default_division(),
                'active': True
            }
        )
        
        # Get or create Agent (same as page view)
        agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
        
        # Get or create Action for session start
        action, _ = Action.objects.get_or_create(
            code='session_start',
            defaults={
                'name': 'Session Start',
                'description': 'Beginning of a new session',
                'action_type': None  # System action
            }
        )
        
        # Create WebInteraction for session start
        web_interaction = cls.objects.create(
            website=website,
            session_id=event_data.get('session_id', ''),
            visitor_cookie=event_data.get('visitor_cookie', ''),
            user_agent=event_data.get('user_agent', ''),
            ip=event_data.get('ip_address'),
            utm_source=event_data.get('utm_source', ''),
            utm_medium=event_data.get('utm_medium', ''),
            utm_campaign=event_data.get('utm_campaign', ''),
            utm_content=event_data.get('utm_content', ''),
            utm_term=event_data.get('utm_term', ''),
            element=event_data.get('element', ''),
            payload={
                **event_data.get('payload', {}),
                'session_start': True,
                'landing_page': event_data.get('full_url', ''),
                'interaction_type': 'session_start'
            },
            is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
            occurred_at=event_data.get('occurred_at')
        )
        
        # Create core Interaction
        interaction = Interaction.objects.create(
            agent=agent,
            action=action,
            touchpoint=touchpoint,
            payload={
                'interaction_type': 'session_start',
                'session_id': event_data.get('session_id', ''),
                'visitor_cookie': event_data.get('visitor_cookie', ''),
                'landing_page': event_data.get('full_url', ''),
                'referrer': event_data.get('referrer', ''),
                'utm_source': event_data.get('utm_source', ''),
                'utm_medium': event_data.get('utm_medium', ''),
                'utm_campaign': event_data.get('utm_campaign', ''),
                'session_start': True
            },
            occurred_at=web_interaction.occurred_at
        )
        
        # Link the interactions
        web_interaction.interaction = interaction
        web_interaction.save()
        
        return web_interaction
    
    @classmethod
    def _get_default_division(cls):
        """Get or create a default division for websites."""
        from our_institution.models import Division
        
        division, _ = Division.objects.get_or_create(
            name="Default Division",
            defaults={
                'description': 'Default division for website interactions',
                'active': True
            }
        )
        return division
    
    @classmethod
    def _get_or_create_agent(cls, user_agent: str):
        """Get or create Agent from user agent string."""
        from interactions.models import Agent
        import uuid
        
        if not user_agent:
            # Create anonymous agent
            agent, _ = Agent.objects.get_or_create(
                identifier=f"anonymous_{uuid.uuid4().hex[:8]}",
                defaults={
                    'agent_type': 'browser',
                    'name': 'Anonymous Browser',
                    'metadata': {
                        'user_agent': user_agent,
                        'browser': {'family': 'Unknown'},
                        'os': {'family': 'Unknown'},
                        'device': {'family': 'Unknown'}
                    }
                }
            )
            return agent
        
        # Parse user agent to extract browser/OS info
        browser_info = cls._parse_user_agent(user_agent)
        
        # Create unique identifier from user agent
        agent_identifier = f"web_{hash(user_agent) % 1000000:06d}"
        
        agent, _ = Agent.objects.get_or_create(
            identifier=agent_identifier,
            defaults={
                'agent_type': 'browser',
                'name': f"{browser_info.get('browser', {}).get('family', 'Unknown')} on {browser_info.get('os', {}).get('family', 'Unknown')}",
                'metadata': {
                    'user_agent': user_agent,
                    **browser_info
                }
            }
        )
        
        return agent
    
    @classmethod
    def _parse_user_agent(cls, user_agent: str) -> dict:
        """Parse user agent string using ua-parser library."""
        try:
            from ua_parser import user_agent_parser
            
            # Parse user agent using ua-parser library
            parsed_ua = user_agent_parser.Parse(user_agent)
            
            return {
                'browser': {
                    'family': parsed_ua.browser.family or 'Unknown',
                    'version': f"{parsed_ua.browser.major}.{parsed_ua.browser.minor}.{parsed_ua.browser.patch}" if parsed_ua.browser.major else 'Unknown'
                },
                'os': {
                    'family': parsed_ua.os.family or 'Unknown',
                    'version': f"{parsed_ua.os.major}.{parsed_ua.os.minor}.{parsed_ua.os.patch}" if parsed_ua.os.major else 'Unknown'
                },
                'device': {
                    'family': parsed_ua.device.family or 'Other',
                    'brand': parsed_ua.device.brand or 'Unknown',
                    'model': parsed_ua.device.model or 'Unknown'
                }
            }
        except ImportError:
            # Fallback to simple parsing if ua-parser is not available
            return cls._parse_user_agent_fallback(user_agent)
        except Exception:
            # Fallback to simple parsing if parsing fails
            return cls._parse_user_agent_fallback(user_agent)
    
    @classmethod
    def _parse_user_agent_fallback(cls, user_agent: str) -> dict:
        """Fallback user agent parsing when ua-parser is not available."""
        user_agent_lower = user_agent.lower()
        
        # Browser detection
        browser_family = 'Unknown'
        if 'chrome' in user_agent_lower:
            browser_family = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser_family = 'Firefox'
        elif 'safari' in user_agent_lower:
            browser_family = 'Safari'
        elif 'edge' in user_agent_lower:
            browser_family = 'Edge'
        elif 'opera' in user_agent_lower:
            browser_family = 'Opera'
        
        # OS detection
        os_family = 'Unknown'
        if 'windows' in user_agent_lower:
            os_family = 'Windows'
        elif 'mac' in user_agent_lower:
            os_family = 'macOS'
        elif 'linux' in user_agent_lower:
            os_family = 'Linux'
        elif 'android' in user_agent_lower:
            os_family = 'Android'
        elif 'ios' in user_agent_lower:
            os_family = 'iOS'
        
        # Device detection
        device_family = 'Other'
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            device_family = 'Mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            device_family = 'Tablet'
        
        return {
            'browser': {
                'family': browser_family,
                'version': 'Unknown'
            },
            'os': {
                'family': os_family,
                'version': 'Unknown'
            },
            'device': {
                'family': device_family,
                'brand': 'Unknown',
                'model': 'Unknown'
            }
        }
    
    @classmethod
    def _is_bot_user_agent(cls, user_agent: str) -> bool:
        """Check if user agent indicates a bot/crawler using ua-parser."""
        if not user_agent:
            return False
        
        try:
            from ua_parser import user_agent_parser
            
            # Parse user agent using ua-parser library
            parsed_ua = user_agent_parser.Parse(user_agent)
            
            # Check if browser family indicates a bot
            browser_family = parsed_ua.browser.family or ''
            if browser_family.lower() in ['bot', 'crawler', 'spider', 'scraper']:
                return True
            
            # Check device family for bot indicators
            device_family = parsed_ua.device.family or ''
            if device_family.lower() in ['bot', 'crawler', 'spider', 'scraper']:
                return True
            
            # Fallback to string matching for known bot patterns
            user_agent_lower = user_agent.lower()
            bot_indicators = [
                'bot', 'crawler', 'spider', 'scraper', 'crawling',
                'googlebot', 'bingbot', 'slurp', 'duckduckbot',
                'baiduspider', 'yandexbot', 'facebookexternalhit',
                'twitterbot', 'linkedinbot', 'whatsapp', 'telegram',
                'applebot', 'crawler', 'spider'
            ]
            
            return any(indicator in user_agent_lower for indicator in bot_indicators)
            
        except ImportError:
            # Fallback to simple string matching if ua-parser is not available
            return cls._is_bot_user_agent_fallback(user_agent)
        except Exception:
            # Fallback to simple string matching if parsing fails
            return cls._is_bot_user_agent_fallback(user_agent)
    
    @classmethod
    def _is_bot_user_agent_fallback(cls, user_agent: str) -> bool:
        """Fallback bot detection when ua-parser is not available."""
        if not user_agent:
            return False
        
        user_agent_lower = user_agent.lower()
        bot_indicators = [
            'bot', 'crawler', 'spider', 'scraper', 'crawling',
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'baiduspider', 'yandexbot', 'facebookexternalhit',
            'twitterbot', 'linkedinbot', 'whatsapp', 'telegram',
            'applebot', 'crawler', 'spider'
        ]
        
        return any(indicator in user_agent_lower for indicator in bot_indicators)


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
    
    def determine_agent_type_from_ua(self) -> str:
        """Determine agent type from user agent using ua-parser."""
        if not self.metadata:
            return 'other'
        
        user_agent = self.metadata.get('user_agent', '')
        if not user_agent:
            return 'other'
        
        try:
            from ua_parser import user_agent_parser
            
            # Parse user agent using ua-parser library
            parsed_ua = user_agent_parser.Parse(user_agent)
            
            # Check if it's a bot based on browser/device family
            browser_family = (parsed_ua.browser.family or '').lower()
            device_family = (parsed_ua.device.family or '').lower()
            
            if any(bot_indicator in browser_family for bot_indicator in ['bot', 'crawler', 'spider', 'scraper']):
                return 'bot'
            elif any(bot_indicator in device_family for bot_indicator in ['bot', 'crawler', 'spider', 'scraper']):
                return 'bot'
            
            # Check if it's a mobile device
            if device_family in ['mobile', 'smartphone', 'tablet']:
                return 'device'
            
            # Check if it's a webview (mobile app)
            if 'webview' in browser_family or 'webview' in device_family:
                return 'device'
            
            # Default to browser for regular web browsers
            return 'browser'
            
        except (ImportError, Exception):
            # Fallback to simple detection
            user_agent_lower = user_agent.lower()
            
            # Check for bot indicators
            bot_indicators = ['bot', 'crawler', 'spider', 'scraper']
            if any(indicator in user_agent_lower for indicator in bot_indicators):
                return 'bot'
            
            # Check for mobile indicators
            mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
            if any(indicator in user_agent_lower for indicator in mobile_indicators):
                return 'device'
            
            # Default to browser
            return 'browser'
    
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
