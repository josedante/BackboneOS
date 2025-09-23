"""
Page view event processors for multi-interaction approach.

This module contains the logic for processing page view events and creating
multiple interactions (page view, referrer click, session start) from a single event.
"""

from django.db import transaction
from django.utils import timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from interactions.models import Action, Agent, Interaction
from .models import WebInteraction, Website, WebAgent, WebSession
from .resolvers import WebTouchpointResolver
from .mapping_providers import WebMappingProvider


class PageViewEventProcessor:
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
        self.event_data = event_data
        self.website = self._get_website()
        self.created_interactions = []
        self.web_session = None
        
    def process(self) -> List[WebInteraction]:
        """
        Process the page view event and create all applicable interactions.
        
        Returns:
            List[WebInteraction]: List of created WebInteraction instances
        """
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
        
        return self.created_interactions
    
    def _get_website(self) -> Website:
        """Get or create the website from event data."""
        website_base = self.event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required in event data")
        
        # Try to find an existing division, or create a default one
        from our_institution.models import Division
        try:
            default_division = Division.objects.first()
            if not default_division:
                # Create a default division if none exists
                from our_institution.models import OurOrganization
                default_org = OurOrganization.objects.first()
                if not default_org:
                    default_org = OurOrganization.objects.create(
                        name="Default Organization",
                        legal_name="Default Organization Legal Name"
                    )
                default_division = Division.objects.create(
                    name="Default Division",
                    code="DEFAULT",
                    description="Default division for websites",
                    organization=default_org
                )
        except:
            default_division = None
        
        website, created = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': self._extract_domain_name(website_base),
                'division': default_division,
                'active': True
            }
        )
        return website
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract a friendly domain name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            # Capitalize first letter of the domain, but keep the rest as is
            return f"{domain.capitalize()} Website"
        except:
            return "Unknown Website"
    
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
        except:
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
        
        # Check for session timeout (30 minutes)
        last_interaction = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).order_by('-created_at').first()
        
        if last_interaction:
            time_diff = timezone.now() - last_interaction.created_at
            if time_diff.total_seconds() > 1800:  # 30 minutes
                return True  # Session timeout = new session
        
        return False  # Existing active session
    
    def _get_or_create_session(self, should_start_new: bool) -> WebSession:
        """Get or create WebSession for this event."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if should_start_new or not session_id or not visitor_cookie:
            # Create new session
            return self._create_new_session()
        else:
            # Get existing session
            try:
                session = WebSession.objects.get(session_id=session_id)
                return session
            except WebSession.DoesNotExist:
                # Session doesn't exist, create new one
                return self._create_new_session()
    
    def _create_new_session(self) -> WebSession:
        """Create a new WebSession."""
        session_id = self.event_data.get('session_id', '')
        visitor_cookie = self.event_data.get('visitor_cookie', '')
        
        # Get agent for this session
        agent = self._get_or_create_agent()
        
        # Create session
        session = WebSession.objects.create(
            session_id=session_id,
            visitor_cookie=visitor_cookie,
            website=self.website,
            agent=agent,
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            referrer_url=self.event_data.get('referrer', ''),
            landing_page_url=self.event_data.get('full_url', ''),
            user_agent=self.event_data.get('user_agent', ''),
            ip_address=self.event_data.get('ip')
        )
        
        return session
    
    def _create_page_view_interaction(self) -> WebInteraction:
        """Create the page view interaction."""
        # Get or create action
        action = Action.objects.get_or_create(
            code='no_action',
            defaults={'name': 'Sin Acción', 'description': 'Evento inferido o acción realizada hacia el usuario'}
        )[0]
        
        # Get or create agent
        agent = self._get_or_create_agent()
        
        # Create interaction payload with all event data
        interaction_payload = {
            'interaction_type': 'page_view',
            'full_url': self.event_data.get('full_url'),
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': self.event_data.get('visitor_cookie')
        }
        
        # Add all payload data from event
        event_payload = self.event_data.get('payload', {})
        interaction_payload.update(event_payload)
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=agent,
            occurred_at=timezone.now(),
            payload=interaction_payload
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        # Resolve touchpoint
        self._resolve_touchpoint(web_interaction)
        
        return web_interaction
    
    def _create_referrer_click_interaction(self) -> WebInteraction:
        """Create the referrer click interaction."""
        # Get or create action
        action = Action.objects.get_or_create(
            code='external_click',
            defaults={'name': 'External Click', 'description': 'Click from external source'}
        )[0]
        
        # Get or create agent
        agent = self._get_or_create_agent()
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=agent,
            occurred_at=timezone.now(),
            payload={
                'interaction_type': 'referrer_click',
                'referrer_url': self.event_data.get('referrer'),
                'referrer_title': self.event_data.get('payload', {}).get('referrer_title'),
                'referrer_description': self.event_data.get('payload', {}).get('referrer_description'),
                'session_id': self.event_data.get('session_id'),
                'visitor_cookie': self.event_data.get('visitor_cookie')
            }
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        # Resolve touchpoint
        self._resolve_touchpoint(web_interaction)
        
        return web_interaction
    
    def _create_session_start_interaction(self) -> WebInteraction:
        """Create the session start interaction."""
        # Get or create action
        action = Action.objects.get_or_create(
            code='no_action',
            defaults={'name': 'Sin Acción', 'description': 'Evento inferido o acción realizada hacia el usuario'}
        )[0]
        
        # Get or create agent
        agent = self._get_or_create_agent()
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=agent,
            occurred_at=timezone.now(),
            payload={
                'interaction_type': 'session_start',
                'session_start_time': timezone.now().isoformat(),
                'is_new_visitor': not self._has_existing_visitor(),
                'landing_page': True,
                'inference_reason': self._get_session_start_reason(),
                'page_title': self.event_data.get('payload', {}).get('page_title'),
                'full_url': self.event_data.get('full_url'),
                'session_id': self.event_data.get('session_id'),
                'visitor_cookie': self.event_data.get('visitor_cookie')
            }
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        # Resolve touchpoint
        self._resolve_touchpoint(web_interaction)
        
        return web_interaction
    
    def _get_or_create_agent(self) -> Agent:
        """Get or create agent from user agent string using ua-parser."""
        user_agent = self.event_data.get('user_agent', '')
        if not user_agent:
            user_agent = 'Unknown Browser'
        
        # Parse user agent using ua-parser
        parsed_ua = self._parse_user_agent(user_agent)
        
        # Determine agent type based on parsing results
        agent_type = self._determine_agent_type(parsed_ua)
        
        # Create agent name and identifier
        agent_name = self._create_agent_name(parsed_ua, agent_type)
        agent_identifier = self._create_agent_identifier(parsed_ua, agent_type)
        
        agent, created = WebAgent.objects.get_or_create(
            name=agent_name,
            defaults={
                'agent_type': agent_type,
                'identifier': agent_identifier,
                'metadata': parsed_ua
            }
        )
        return agent
    
    def _parse_user_agent(self, user_agent: str) -> dict:
        """Parse user agent string using ua-parser library."""
        try:
            import ua_parser.user_agent_parser as ua_parser
            parsed = ua_parser.Parse(user_agent)
            
            # Convert to a more usable format
            return {
                'browser': {
                    'family': parsed.get('user_agent', {}).get('family', 'Other'),
                    'major': parsed.get('user_agent', {}).get('major'),
                    'minor': parsed.get('user_agent', {}).get('minor'),
                    'patch': parsed.get('user_agent', {}).get('patch'),
                    'version': self._build_version_string(parsed.get('user_agent', {}))
                },
                'os': {
                    'family': parsed.get('os', {}).get('family', 'Other'),
                    'major': parsed.get('os', {}).get('major'),
                    'minor': parsed.get('os', {}).get('minor'),
                    'patch': parsed.get('os', {}).get('patch'),
                    'version': self._build_version_string(parsed.get('os', {}))
                },
                'device': {
                    'family': parsed.get('device', {}).get('family', 'Other'),
                    'brand': parsed.get('device', {}).get('brand'),
                    'model': parsed.get('device', {}).get('model')
                },
                'raw_user_agent': user_agent
            }
        except Exception as e:
            # Fallback to basic parsing if ua-parser fails
            return {
                'browser': {'family': 'Other', 'version': 'Unknown'},
                'os': {'family': 'Other', 'version': 'Unknown'},
                'device': {'family': 'Other'},
                'raw_user_agent': user_agent,
                'parse_error': str(e)
            }
    
    def _build_version_string(self, version_dict: dict) -> str:
        """Build version string from version components."""
        if not version_dict:
            return 'Unknown'
        
        major = version_dict.get('major')
        minor = version_dict.get('minor')
        patch = version_dict.get('patch')
        
        if major is None:
            return 'Unknown'
        
        version_parts = [str(major)]
        if minor is not None:
            version_parts.append(str(minor))
        if patch is not None:
            version_parts.append(str(patch))
        
        return '.'.join(version_parts)
    
    def _determine_agent_type(self, parsed_ua: dict) -> str:
        """Determine agent type based on parsed user agent data."""
        browser_family = parsed_ua.get('browser', {}).get('family', '').lower()
        device_family = parsed_ua.get('device', {}).get('family', '').lower()
        
        # Check for bots/crawlers
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'crawling', 'headless']
        if any(indicator in browser_family.lower() for indicator in bot_indicators):
            return 'bot'
        
        # Check for mobile apps (WebView)
        if 'webview' in browser_family.lower() or 'mobile' in device_family.lower():
            return 'device'
        
        # Default to browser for web traffic
        return 'browser'
    
    def _create_agent_name(self, parsed_ua: dict, agent_type: str) -> str:
        """Create agent name based on parsed data and agent type."""
        if agent_type == 'bot':
            browser_family = parsed_ua.get('browser', {}).get('family', 'Unknown Bot')
            return f"Bot: {browser_family}"
        elif agent_type == 'device':
            device_family = parsed_ua.get('device', {}).get('family', 'Unknown Device')
            browser_family = parsed_ua.get('browser', {}).get('family', 'Unknown')
            return f"{device_family} ({browser_family})"
        else:  # browser
            browser_family = parsed_ua.get('browser', {}).get('family', 'Unknown Browser')
            return browser_family
    
    def _create_agent_identifier(self, parsed_ua: dict, agent_type: str) -> str:
        """Create agent identifier based on parsed data and agent type."""
        browser_family = parsed_ua.get('browser', {}).get('family', 'unknown').lower()
        browser_version = parsed_ua.get('browser', {}).get('version', 'unknown')
        os_family = parsed_ua.get('os', {}).get('family', 'unknown').lower()
        device_family = parsed_ua.get('device', {}).get('family', 'unknown').lower()
        
        if agent_type == 'bot':
            return f"bot-{browser_family}-{browser_version}"
        elif agent_type == 'device':
            return f"device-{device_family}-{browser_family}-{browser_version}"
        else:  # browser
            return f"{browser_family}-{browser_version}-{os_family}"
    
    
    def _has_existing_visitor(self) -> bool:
        """Check if visitor has existing interactions."""
        visitor_cookie = self.event_data.get('visitor_cookie')
        if not visitor_cookie:
            return False
        
        return WebInteraction.objects.filter(
            visitor_cookie=visitor_cookie
        ).exists()
    
    def _get_session_start_reason(self) -> str:
        """Get the reason for session start inference."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            return 'no_session_info'
        
        # Check if this is the first interaction for this session
        existing_interactions = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).exists()
        
        if not existing_interactions:
            return 'first_interaction'
        
        # Check for session timeout
        last_interaction = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).order_by('-created_at').first()
        
        if last_interaction:
            time_diff = timezone.now() - last_interaction.created_at
            if time_diff.total_seconds() > 1800:  # 30 minutes
                return 'session_timeout'
        
        return 'unknown'
    
    def _resolve_touchpoint(self, web_interaction: WebInteraction):
        """Resolve and assign touchpoint for the web interaction."""
        try:
            resolver = WebTouchpointResolver(WebMappingProvider())
            touchpoint = resolver.resolve(web_interaction)
            
            web_interaction.interaction.touchpoint = touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        except Exception as e:
            # Log error but don't fail the entire process
            print(f"Error resolving touchpoint for {web_interaction.id}: {e}")
