"""
Event processors for website interactions.

This module contains refactored processors for handling different types of website events:
- PageViewEventProcessor: Multi-interaction approach for page views
- PageReadEventProcessor: Engagement-focused interactions for page reads  
- ClickEventProcessor: Click-specific interactions

All processors inherit from BaseWebEventProcessor to eliminate code duplication
and provide consistent functionality across all event types.
"""

from django.db import transaction
from django.utils import timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging
import ua_parser.user_agent_parser

from interactions.models import Action, Agent, Interaction, Touchpoint, Channel, TouchpointClass, Medium
from .models import WebInteraction, Website, WebAgent, WebSession
from our_institution.models import Division, OurOrganization

logger = logging.getLogger(__name__)


class BaseWebEventProcessor:
    """
    Base class for all web event processors.
    
    This class provides common functionality for all web event processors,
    eliminating code duplication and ensuring consistent behavior.
    """
    
    def __init__(self, event_data: Dict[str, Any]):
        """
        Initialize the processor with event data.
        
        Args:
            event_data: Dictionary containing the event data
        """
        self.event_data = event_data
        self.website = self._get_website()
        self.web_session = None
        
    def _get_website(self) -> Website:
        """Get or create website from event data."""
        website_base = self.event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required in event data")
        
        try:
            website = Website.objects.get(base_url=website_base)
            return website
        except Website.DoesNotExist:
            return self._create_website(website_base)
    
    def _create_website(self, base_url: str) -> Website:
        """Create a new website with fallback to default division."""
        try:
            # Try to get the first available division
            division = Division.objects.first()
            if not division:
                # Create default division if none exists
                org = OurOrganization.objects.first()
                if not org:
                    org = OurOrganization.objects.create(
                        name="Default Organization",
                        legal_name="Default Organization Legal Name"
                    )
                division = Division.objects.create(
                    name="Default Division",
                    code="DEFAULT",
                    description="Default division for websites",
                    organization=org
                )
            
            website = Website.objects.create(
                base_url=base_url,
                name=f"{self._extract_domain_name(base_url)} Website",
                division=division,
                active=True
            )
            
            logger.info(f"Created new website: {website.base_url}")
            return website
            
        except Exception as e:
            logger.error(f"Error creating website {base_url}: {e}")
            raise
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return 'unknown'
    
    def _parse_user_agent(self, user_agent_string: str) -> Dict[str, str]:
        """Parse user agent string to extract browser information."""
        try:
            parsed_ua = ua_parser.user_agent_parser.Parse(user_agent_string)
            
            # Extract browser information
            browser_family = parsed_ua.get('user_agent', {}).get('family', 'Unknown')
            browser_major = parsed_ua.get('user_agent', {}).get('major', '')
            browser_minor = parsed_ua.get('user_agent', {}).get('minor', '')
            
            # Extract OS information
            os_family = parsed_ua.get('os', {}).get('family', 'Unknown')
            os_major = parsed_ua.get('os', {}).get('major', '')
            os_minor = parsed_ua.get('os', {}).get('minor', '')
            
            # Build browser name
            browser_name = browser_family
            if browser_major:
                browser_name += f" {browser_major}"
                if browser_minor:
                    browser_name += f".{browser_minor}"
            
            # Build OS name
            os_name = os_family
            if os_major:
                os_name += f" {os_major}"
                if os_minor:
                    os_name += f".{os_minor}"
            
            # Determine agent type
            agent_type = 'browser'
            if 'bot' in browser_family.lower() or 'crawler' in browser_family.lower():
                agent_type = 'bot'
            elif 'mobile' in os_family.lower() or 'android' in os_family.lower() or 'ios' in os_family.lower():
                agent_type = 'mobile'
            
            # Create identifier
            identifier = f"{browser_name} on {os_name}".lower().replace(' ', '-')
            
            return {
                'name': browser_name,
                'agent_type': agent_type,
                'identifier': identifier,
                'os_name': os_name,
                'browser_family': browser_family,
                'browser_version': f"{browser_major}.{browser_minor}" if browser_major and browser_minor else browser_major or 'Unknown'
            }
            
        except Exception as e:
            logger.warning(f"Error parsing user agent '{user_agent_string}': {e}")
            return {
                'name': 'Unknown Browser',
                'agent_type': 'unknown',
                'identifier': 'unknown-browser',
                'os_name': 'Unknown OS',
                'browser_family': 'Unknown',
                'browser_version': 'Unknown'
            }
    
    def _get_or_create_agent(self) -> WebAgent:
        """Get or create WebAgent from user agent string."""
        user_agent_string = self.event_data.get('user_agent', '')
        if not user_agent_string:
            # Create default agent
            agent, _ = WebAgent.objects.get_or_create(
                name='Unknown Browser',
                defaults={
                    'agent_type': 'unknown',
                    'identifier': 'unknown-browser'
                }
            )
            return agent
        
        # Parse user agent
        ua_info = self._parse_user_agent(user_agent_string)
        
        # Get or create agent
        agent, _ = WebAgent.objects.get_or_create(
            name=ua_info['name'],
            defaults={
                'agent_type': ua_info['agent_type'],
                'identifier': ua_info['identifier']
            }
        )
        
        return agent
    
    def _get_or_create_website_channel_and_medium(self):
        """Get or create channel and medium for touchpoint creation."""
        # Get or create medium
        medium, _ = Medium.objects.get_or_create(
            code='owned_website',
            defaults={'name': 'Owned Website'}
        )
        
        # Get or create channel
        domain_name = self._extract_domain_name(self.website.base_url)
        # Use consistent channel code (always truncate to 30 chars)
        channel_code = f"{domain_name} website"[:30]
        channel, created = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': f'{domain_name} Website'
            }
        )
        
        # Always set the medium
        if channel.medium != medium:
            channel.medium = medium
            channel.save(update_fields=['medium'])
        
        return channel, medium
    
    def _get_or_create_session(self, should_start_new: bool = True) -> WebSession:
        """Get or create WebSession for the event."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            if should_start_new:
                return self._create_new_session()
            else:
                raise ValueError("session_id and visitor_cookie are required")
        
        try:
            # Try to get existing session
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active and should_start_new:
                return self._create_new_session()
            return session
        except WebSession.DoesNotExist:
            if should_start_new:
                return self._create_new_session()
            else:
                raise ValueError("Session not found")
    
    def _create_new_session(self) -> WebSession:
        """Create a new WebSession."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id:
            session_id = f"session_{timezone.now().timestamp()}"
        if not visitor_cookie:
            visitor_cookie = f"visitor_{timezone.now().timestamp()}"
        
        agent = self._get_or_create_agent()
        
        session = WebSession.objects.create(
            session_id=session_id,
            visitor_cookie=visitor_cookie,
            website=self.website,
            agent=agent,
            ended_at=WebSession.get_session_end_time()
        )
        
        logger.info(f"Created new session: {session_id}")
        return session
    
    def _create_base_web_interaction(self, action_code: str, action_name: str, 
                                   action_description: str, interaction_type: str, 
                                   payload: Dict[str, Any]) -> WebInteraction:
        """Create a base WebInteraction with common fields."""
        # Get or create action
        action, _ = Action.objects.get_or_create(
            code=action_code,
            defaults={
                'name': action_name,
                'description': action_description
            }
        )
        
        # Get or create agent
        agent = self._get_or_create_agent()
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=agent,
            occurred_at=timezone.now(),
            payload=payload
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', '')
        )
        
        return web_interaction


class PageViewEventProcessor(BaseWebEventProcessor):
    """
    Processor for page view events that creates multiple interactions.
    
    This processor implements the multi-interaction approach where a single
    page view event can create up to 3 separate WebInteraction instances:
    1. Page View Interaction (always created)
    2. Referrer Click Interaction (if external referrer exists)
    3. Session Start Interaction (if new session criteria met)
    """
    
    def __init__(self, event_data: Dict[str, Any]):
        """
        Initialize the processor with event data.
        
        Args:
            event_data: Dictionary containing the page view event data
        """
        super().__init__(event_data)
        self.created_interactions = []
        
    @transaction.atomic
    def process(self) -> List[WebInteraction]:
        """
        Process the page view event and create all applicable interactions.
        
        Returns:
            List[WebInteraction]: List of created WebInteraction instances
        """
        try:
            # Check session start criteria BEFORE creating any interactions
            should_start_session = self._should_start_new_session()
            has_external_referrer = self._has_external_referrer()
            
            # Get or create WebSession
            self.web_session = self._get_or_create_session(should_start_session)
            
            # 1. Always create Page View Interaction
            page_view_interaction = self._create_page_view_interaction()
            self.created_interactions.append(page_view_interaction)
            
            # 2. Create Referrer Click Interaction (if external referrer exists)
            if has_external_referrer:
                referrer_click_interaction = self._create_referrer_click_interaction()
                self.created_interactions.append(referrer_click_interaction)
            
            # 3. Create Session Start Interaction (if new session criteria met)
            if should_start_session:
                session_start_interaction = self._create_session_start_interaction()
                self.created_interactions.append(session_start_interaction)
            
            # Update session activity
            self.web_session.update_activity()
            
            logger.info(f"Successfully created {len(self.created_interactions)} interactions for page view event")
            return self.created_interactions
            
        except Exception as e:
            logger.error(f"Error processing page view event: {e}")
            raise
    
    def _has_external_referrer(self) -> bool:
        """Check if there's an external referrer."""
        referrer = self.event_data.get('referrer')
        if not referrer:
            return False
        
        try:
            parsed_referrer = urlparse(referrer)
            referrer_domain = parsed_referrer.netloc.lower()
            
            parsed_website = urlparse(self.website.base_url)
            website_domain = parsed_website.netloc.lower()
            
            # Remove www. prefix for comparison
            if referrer_domain.startswith('www.'):
                referrer_domain = referrer_domain[4:]
            if website_domain.startswith('www.'):
                website_domain = website_domain[4:]
            
            return referrer_domain != website_domain
        except Exception as e:
            logger.warning(f"Error parsing referrer URL {referrer}: {e}")
            return True  # Assume external if we can't parse
    
    def _should_start_new_session(self) -> bool:
        """
        Determine if this should start a new session.
        
        This implements the server-side session inference logic.
        """
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            return True  # No session info = new session
        
        # Check if this is the first interaction for this session
        existing_interactions = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).exists()
        
        if not existing_interactions:
            return True  # First interaction = new session
        
        # Check for session timeout using WebSession.ended_at
        try:
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active:
                return True  # Session expired = new session
        except WebSession.DoesNotExist:
            return True  # No session exists = new session
        
        return False  # Existing active session
    
    def _create_page_view_interaction(self) -> WebInteraction:
        """Create page view interaction with page touchpoint."""
        # Get page data for touchpoint creation
        payload = self.event_data.get('payload', {})
        page_title = payload.get('page_title', '')
        page_description = payload.get('page_description', '')
        full_url = self.event_data.get('full_url', '')
        
        # Create interaction payload
        interaction_payload = {
            'interaction_type': 'page_view',
            'full_url': full_url,
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': self.event_data.get('visitor_cookie'),
            'referrer': self.event_data.get('referrer'),
            'page_title': page_title,
            'page_description': page_description
        }
        
        # Add all payload data from event
        interaction_payload.update(payload)
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='no_action',
            action_name='Sin Acción',
            action_description='Acción sin clasificar específica',
            interaction_type='page_view',
            payload=interaction_payload
        )
        
        # Create page view touchpoint
        page_touchpoint = self._create_page_view_touchpoint(
            page_title, page_description, full_url
        )
        
        # Link touchpoint to interaction
        if page_touchpoint:
            web_interaction.interaction.touchpoint = page_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_referrer_click_interaction(self) -> WebInteraction:
        """Create referrer click interaction."""
        referrer = self.event_data.get('referrer', '')
        
        # Create interaction payload
        interaction_payload = {
            'interaction_type': 'referrer_click',
            'referrer': referrer,
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': self.event_data.get('visitor_cookie'),
            'full_url': self.event_data.get('full_url')
        }
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='no_action',
            action_name='Sin Acción',
            action_description='Acción sin clasificar específica',
            interaction_type='referrer_click',
            payload=interaction_payload
        )
        
        # Create referrer click touchpoint
        referrer_touchpoint = self._create_referrer_click_touchpoint(referrer)
        
        # Link touchpoint to interaction
        if referrer_touchpoint:
            web_interaction.interaction.touchpoint = referrer_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_session_start_interaction(self) -> WebInteraction:
        """Create session start interaction."""
        # Check if this is a new visitor
        visitor_cookie = self.event_data.get('visitor_cookie')
        is_new_visitor = not WebInteraction.objects.filter(
            visitor_cookie=visitor_cookie
        ).exists() if visitor_cookie else True
        
        # Create interaction payload
        interaction_payload = {
            'interaction_type': 'session_start',
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': visitor_cookie,
            'is_new_visitor': is_new_visitor,
            'landing_page': True,
            'full_url': self.event_data.get('full_url'),
            'referrer': self.event_data.get('referrer')
        }
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='no_action',
            action_name='Sin Acción',
            action_description='Acción sin clasificar específica',
            interaction_type='session_start',
            payload=interaction_payload
        )
        
        # Create session start touchpoint
        session_touchpoint = self._create_session_start_touchpoint()
        
        # Link touchpoint to interaction
        if session_touchpoint:
            web_interaction.interaction.touchpoint = session_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_page_view_touchpoint(self, title: str, description: str, url: str) -> Optional[Touchpoint]:
        """Create page view specific touchpoint."""
        try:
            # Get channel and medium
            channel, medium = self._get_or_create_website_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.internal_interaction',
                defaults={'name': 'Internal Web Interaction'}
            )
            
            # Create touchpoint code
            touchpoint_code = f"web.page_view.{title.lower().replace(' ', '_').replace('-', '_')}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': title,
                    'description': description,
                    'url': url,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating page view touchpoint: {e}")
            return None
    
    def _create_referrer_click_touchpoint(self, referrer: str) -> Optional[Touchpoint]:
        """Create referrer click specific touchpoint."""
        try:
            # Get channel and medium
            channel, medium = self._get_or_create_referrerchannel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.external_referrer',
                defaults={'name': 'External Referrer'}
            )
            
            # Create touchpoint code
            parsed_referrer = urlparse(referrer)
            domain = parsed_referrer.netloc.lower()
            touchpoint_code = f"web.referrer.{domain.replace('.', '_')}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': f"Referrer: {domain}",
                    'description': f"User came from {referrer}",
                    'url': referrer,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating referrer click touchpoint: {e}")
            return None
    
    def _create_session_start_touchpoint(self) -> Optional[Touchpoint]:
        """Create session start specific touchpoint."""
        try:
            # Get channel and medium
            channel, medium = self._get_or_create_website_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.session_start',
                defaults={'name': 'Session Start'}
            )
            
            # Create touchpoint code
            touchpoint_code = f"web.session_start.{self.website.base_url}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': f"Session Start - {self.website.name}",
                    'description': f"User started a new session on {self.website.base_url}",
                    'url': self.website.base_url,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating session start touchpoint: {e}")
            return None


class PageReadEventProcessor(BaseWebEventProcessor):
    """
    Processor for page read events that creates engagement-focused interactions.
    
    This processor:
    1. Validates previous page view exists
    2. Creates single WebInteraction with engagement data
    3. Calculates engagement score
    4. Creates page touchpoint if needed
    5. Updates session activity
    """
    
    def __init__(self, event_data: Dict[str, Any]):
        """
        Initialize the processor with event data.
        
        Args:
            event_data: Dictionary containing the page read event data
        """
        super().__init__(event_data)
        
    @transaction.atomic
    def process(self) -> WebInteraction:
        """
        Process the page read event and create engagement interaction.
        
        Returns:
            WebInteraction: Created WebInteraction instance
        """
        try:
            # Validate previous page view exists
            if not self._has_previous_page_view():
                raise ValueError("Page read requires a previous page view")
            
            # Get existing session (don't create new one)
            self.web_session = self._get_or_create_session(should_start_new=False)
            
            # Create page read interaction
            page_read_interaction = self._create_page_read_interaction()
            
            # Update session activity
            self.web_session.update_activity()
            
            logger.info(f"Successfully created page read interaction")
            return page_read_interaction
            
        except Exception as e:
            logger.error(f"Error processing page read event: {e}")
            raise
    
    def _has_previous_page_view(self) -> bool:
        """Check if there's a previous page view for this session/page."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            return False
        
        return WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie,
            interaction__action__code='no_action',
            interaction__payload__interaction_type='page_view'
        ).exists()
    
    def _get_or_create_session(self, should_start_new: bool = True) -> WebSession:
        """Get existing session for this page read event."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            raise ValueError("session_id and visitor_cookie are required for page read events")
        
        try:
            session = WebSession.objects.get(session_id=session_id)
            return session
        except WebSession.DoesNotExist:
            raise ValueError("Session not found - page read requires an existing session")
    
    def _create_page_read_interaction(self) -> WebInteraction:
        """Create page read interaction with engagement data."""
        # Get page data for touchpoint creation
        payload = self.event_data.get('payload', {})
        page_title = payload.get('page_title', '')
        page_description = payload.get('page_description', '')
        full_url = self.event_data.get('full_url', '')
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(payload)
        payload['engagement_score'] = engagement_score
        payload['interaction_type'] = 'page_read'
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='page_read',
            action_name='Leyó página',
            action_description='El usuario leyó una página de manera significativa',
            interaction_type='page_read',
            payload=payload
        )
        
        # Create or get page touchpoint
        page_touchpoint = self._get_or_create_page_touchpoint(
            page_title, page_description, full_url
        )
        
        # Link touchpoint to interaction
        if page_touchpoint:
            web_interaction.interaction.touchpoint = page_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _calculate_engagement_score(self, payload: dict) -> float:
        """
        Calculate engagement score based on multiple factors.
        Returns score between 0.0 and 1.0
        """
        time_on_page = payload.get('time_on_page', 0)
        scroll_depth = payload.get('scroll_depth', 0)
        interactions_count = payload.get('interactions_count', 0)
        word_count = payload.get('word_count', 1000)
        
        # Time factor (adjusted for content length)
        if word_count < 200:
            time_threshold = 10  # Short pages
        elif word_count < 500:
            time_threshold = 20  # Medium pages
        else:
            time_threshold = 30  # Long pages
        
        time_factor = min(time_on_page / time_threshold, 1.0)
        
        # Scroll depth (0-100% to 0-1)
        scroll_score = scroll_depth / 100
        
        # Interaction score (max at 5 interactions)
        interaction_score = min(interactions_count / 5, 1.0)
        
        # Weighted composite score
        engagement_score = (
            time_factor * 0.3 +      # 30% - Time factor (adjusted for content length)
            scroll_score * 0.4 +     # 40% - Scroll depth (most important)
            interaction_score * 0.3  # 30% - User interactions
        )
        
        return round(engagement_score, 2)
    
    def _get_or_create_page_touchpoint(self, title: str, description: str, url: str) -> Optional[Touchpoint]:
        """Create or get touchpoint for the page being read."""
        try:
            # Get channel and medium
            channel, medium = self._get_or_create_website_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.internal_interaction',
                defaults={'name': 'Internal Web Interaction'}
            )
            
            # Create touchpoint code
            touchpoint_code = f"web.page_read.{title.lower().replace(' ', '_').replace('-', '_')}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': title,
                    'description': description,
                    'url': url,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating page read touchpoint: {e}")
            return None


class ClickEventProcessor(BaseWebEventProcessor):
    """
    Processor for click events that creates single interactions.
    
    This processor handles click events (button clicks, link clicks, etc.)
    and creates a single WebInteraction with click action and internal_click touchpoint class.
    """
    
    def __init__(self, event_data: Dict[str, Any]):
        """
        Initialize the processor with event data.
        
        Args:
            event_data: Dictionary containing the click event data
        """
        super().__init__(event_data)
        
    @transaction.atomic
    def process(self) -> WebInteraction:
        """
        Process the click event and create click interaction.
        
        Returns:
            WebInteraction: Created WebInteraction instance
        """
        try:
            # Get or create session
            self.web_session = self._get_or_create_session()
            
            # Create click interaction
            click_interaction = self._create_click_interaction()
            
            # Update session activity
            self.web_session.update_activity()
            
            logger.info(f"Successfully created click interaction")
            return click_interaction
            
        except Exception as e:
            logger.error(f"Error processing click event: {e}")
            raise
    
    def _create_click_interaction(self) -> WebInteraction:
        """Create the click interaction."""
        # Create interaction payload with all event data
        interaction_payload = {
            'interaction_type': 'click',
            'full_url': self.event_data.get('full_url'),
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': self.event_data.get('visitor_cookie'),
            'clicked_element': self.event_data.get('payload', {}).get('clicked_element'),
            'element_id': self.event_data.get('payload', {}).get('element_id'),
            'element_class': self.event_data.get('payload', {}).get('element_class'),
            'click_position': self.event_data.get('payload', {}).get('click_position'),
            'target_url': self.event_data.get('payload', {}).get('target_url')
        }
        
        # Add all payload data from event
        event_payload = self.event_data.get('payload', {})
        interaction_payload.update(event_payload)
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='click',
            action_name='Click',
            action_description='User clicked on an element',
            interaction_type='click',
            payload=interaction_payload
        )
        
        # Create click touchpoint
        click_touchpoint = self._create_click_touchpoint()
        if click_touchpoint:
            web_interaction.interaction.touchpoint = click_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_click_touchpoint(self) -> Optional[Touchpoint]:
        """Create click-specific touchpoint."""
        try:
            # Get click data from event
            payload = self.event_data.get('payload', {})
            clicked_element = payload.get('clicked_element', 'Unknown Element')
            element_id = payload.get('element_id', '')
            element_class = payload.get('element_class', '')
            target_url = payload.get('target_url', '')
            
            # Get channel and medium
            channel, medium = self._get_or_create_website_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.internal_click',
                defaults={'name': 'Internal Click'}
            )
            
            # Create touchpoint code based on element
            element_name = clicked_element.lower().replace(' ', '_').replace('-', '_')
            touchpoint_code = f"web.click.{element_name}"
            
            # Create touchpoint name
            touchpoint_name = f"Click: {clicked_element}"
            if element_id:
                touchpoint_name += f" (ID: {element_id})"
            elif element_class:
                touchpoint_name += f" (Class: {element_class})"
            
            # Create touchpoint description
            description = f"User clicked on {clicked_element}"
            if target_url:
                description += f" leading to {target_url}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': touchpoint_name,
                    'description': description,
                    'url': self.event_data.get('full_url', ''),
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating click touchpoint: {e}")
            return None