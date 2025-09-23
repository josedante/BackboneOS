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
        
        # Check for session timeout using WebSession.ended_at
        try:
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active:
                return True  # Session expired = new session
        except WebSession.DoesNotExist:
            return True  # No session exists = new session
        
        return False  # Existing active session
    
    def _get_or_create_session(self, should_start_new: bool) -> WebSession:
        """Get or create WebSession for this event."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if should_start_new or not session_id or not visitor_cookie:
            # Create new session
            return self._create_new_session()
        else:
            # Get existing session and extend it
            try:
                session = WebSession.objects.get(session_id=session_id)
                if session.is_session_active:
                    # Extend the session for new activity
                    session.extend_session()
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
        
        # Create session with automatic ended_at
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
            ip_address=self.event_data.get('ip'),
            ended_at=WebSession.get_session_end_time()
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
        
        # Check for session timeout using WebSession.ended_at
        try:
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active:
                return 'session_timeout'
        except WebSession.DoesNotExist:
            return 'session_timeout'  # No session exists = timeout
        
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


class PageReadEventProcessor:
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
        self.event_data = event_data
        self.website = self._get_website()
        self.web_session = None
        
    def process(self) -> WebInteraction:
        """
        Process the page read event and create engagement interaction.
        
        Returns:
            WebInteraction: Created WebInteraction instance
        """
        # Validate previous page view exists
        if not self._has_previous_page_view():
            raise ValueError("Page read requires a previous page view")
        
        # Get existing session (don't create new one)
        self.web_session = self._get_or_create_session()
        
        # Create page read interaction
        page_read_interaction = self._create_page_read_interaction()
        
        # Update session activity
        self.web_session.update_activity()
        
        return page_read_interaction
    
    def _get_website(self) -> Website:
        """Get or create the website from event data."""
        website_base = self.event_data.get('website_base')
        if not website_base:
            raise ValueError("website_base is required")
        
        # Extract domain name for website creation
        domain_name = self._extract_domain_name(website_base)
        
        # Get or create division
        from our_institution.models import Division, OurOrganization
        org = OurOrganization.objects.first()
        if not org:
            org = OurOrganization.objects.create(
                name="Default Organization",
                legal_name="Default Organization Legal Name"
            )
        
        division = Division.objects.first()
        if not division:
            division = Division.objects.create(
                name="Default Division",
                code="DEFAULT",
                description="Default division",
                organization=org
            )
        
        # Get or create website
        website, _ = Website.objects.get_or_create(
            base_url=website_base,
            defaults={
                'name': f"{domain_name} Website",
                'division': division,
                'active': True
            }
        )
        
        return website
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            # Capitalize first letter
            return domain.capitalize()
        except:
            return "Unknown"
    
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
    
    def _get_or_create_session(self) -> WebSession:
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
    
    def _get_or_create_agent(self) -> WebAgent:
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
    
    def _build_version_string(self, component: dict) -> str:
        """Build version string from component parts."""
        parts = []
        if component.get('major'):
            parts.append(component['major'])
        if component.get('minor'):
            parts.append(component['minor'])
        if component.get('patch'):
            parts.append(component['patch'])
        return '.'.join(parts) if parts else 'Unknown'
    
    def _determine_agent_type(self, parsed_ua: dict) -> str:
        """Determine agent type based on parsed user agent."""
        browser_family = parsed_ua.get('browser', {}).get('family', '').lower()
        device_family = parsed_ua.get('device', {}).get('family', '').lower()
        
        # Check for bots
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'googlebot', 'bingbot']
        if any(indicator in browser_family for indicator in bot_indicators):
            return 'bot'
        
        # Check for mobile devices
        mobile_indicators = ['mobile', 'smartphone', 'tablet', 'iphone', 'ipad', 'android']
        if any(indicator in device_family for indicator in mobile_indicators):
            return 'device'
        
        # Default to browser
        return 'browser'
    
    def _create_agent_name(self, parsed_ua: dict, agent_type: str) -> str:
        """Create agent name from parsed user agent."""
        if agent_type == 'bot':
            return f"Bot: {parsed_ua.get('browser', {}).get('family', 'Unknown')}"
        elif agent_type == 'device':
            device = parsed_ua.get('device', {}).get('family', 'Unknown')
            browser = parsed_ua.get('browser', {}).get('family', 'Unknown')
            return f"{device} ({browser})"
        else:  # browser
            browser = parsed_ua.get('browser', {}).get('family', 'Unknown')
            os = parsed_ua.get('os', {}).get('family', 'Unknown')
            return f"{browser} on {os}"
    
    def _create_agent_identifier(self, parsed_ua: dict, agent_type: str) -> str:
        """Create agent identifier from parsed user agent."""
        browser = parsed_ua.get('browser', {}).get('family', 'unknown').lower()
        version = parsed_ua.get('browser', {}).get('version', 'unknown').replace('.', '')
        os = parsed_ua.get('os', {}).get('family', 'unknown').lower()
        
        if agent_type == 'bot':
            return f"bot-{browser}-{version}"
        elif agent_type == 'device':
            device = parsed_ua.get('device', {}).get('family', 'unknown').lower()
            return f"device-{device}-{browser}-{version}"
        else:  # browser
            return f"{browser}-{version}-{os}"
    
    def _create_page_read_interaction(self) -> WebInteraction:
        """Create page read interaction with engagement data."""
        # Get or create action
        action = Action.objects.get_or_create(
            code='page_read',
            defaults={'name': 'Leyó página', 'description': 'El usuario leyó una página de manera significativa'}
        )[0]
        
        # Get page data for touchpoint creation
        payload = self.event_data.get('payload', {})
        page_title = payload.get('page_title', '')
        page_description = payload.get('page_description', '')
        full_url = self.event_data.get('full_url', '')
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(payload)
        payload['engagement_score'] = engagement_score
        payload['interaction_type'] = 'page_read'
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=self._get_or_create_agent(),
            occurred_at=timezone.now(),
            payload=payload
        )
        
        # Create or get page touchpoint
        page_touchpoint = self._get_or_create_page_touchpoint(
            page_title, page_description, full_url
        )
        
        # Link touchpoint to interaction
        interaction.touchpoint = page_touchpoint
        interaction.save(update_fields=['touchpoint'])
        
        # Create WebInteraction (no UTM fields)
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            element=self.event_data.get('element', 'body'),
            payload=payload
        )
        
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
    
    def _get_or_create_page_touchpoint(self, title: str, description: str, url: str) -> 'Touchpoint':
        """Create or get touchpoint for the page being read."""
        from interactions.models import Touchpoint, Channel, TouchpointClass
        
        # Get or create medium
        from interactions.models import Medium
        medium, _ = Medium.objects.get_or_create(
            code='owned_website',
            defaults={'name': 'Owned Website'}
        )
        
        # Get or create channel
        domain_name = self._extract_domain_name(self.website.base_url)
        # Use consistent channel code (always truncate to 30 chars)
        channel_code = domain_name.lower()[:30]
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


class ClickEventProcessor:
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
        self.event_data = event_data
        self.website = self._get_website()
        self.web_session = None
        
    def process(self) -> WebInteraction:
        """
        Process the click event and create click interaction.
        
        Returns:
            WebInteraction: Created WebInteraction instance
        """
        # Get or create session
        self.web_session = self._get_or_create_session()
        
        # Create click interaction
        click_interaction = self._create_click_interaction()
        
        # Update session activity
        self.web_session.update_activity()
        
        return click_interaction
    
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
    
    def _get_or_create_session(self) -> WebSession:
        """Get or create WebSession for this event."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            # Create new session
            return self._create_new_session()
        else:
            # Get existing session and extend it
            try:
                session = WebSession.objects.get(session_id=session_id)
                if session.is_session_active:
                    # Extend the session for new activity
                    session.extend_session()
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
        
        # Create session with automatic ended_at
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
            ip_address=self.event_data.get('ip'),
            ended_at=WebSession.get_session_end_time()
        )
        
        return session
    
    def _get_or_create_agent(self) -> WebAgent:
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
    
    def _create_click_interaction(self) -> WebInteraction:
        """Create the click interaction."""
        # Get or create action
        action = Action.objects.get_or_create(
            code='click',
            defaults={'name': 'Click', 'description': 'User clicked on an element'}
        )[0]
        
        # Get or create agent
        agent = self._get_or_create_agent()
        
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
        
        # Create interaction
        interaction = Interaction.objects.create(
            action=action,
            agent=agent,
            occurred_at=timezone.now(),
            payload=interaction_payload
        )
        
        # Create click touchpoint first
        click_touchpoint = self._create_click_touchpoint()
        
        # Set the touchpoint on the interaction before creating WebInteraction
        interaction.touchpoint = click_touchpoint
        interaction.save(update_fields=['touchpoint'])
        
        # Create WebInteraction (touchpoint already set, so no automatic resolution)
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        return web_interaction
    
    def _create_click_touchpoint(self):
        """Create click-specific touchpoint."""
        try:
            # Get click data from event
            payload = self.event_data.get('payload', {})
            clicked_element = payload.get('clicked_element', 'Unknown Element')
            element_id = payload.get('element_id', '')
            element_class = payload.get('element_class', '')
            target_url = payload.get('target_url', '')
            
            # Create click touchpoint
            click_touchpoint = self._get_or_create_click_touchpoint(
                clicked_element, element_id, element_class, target_url
            )
            
            return click_touchpoint
        except Exception as e:
            # Log error but don't fail the entire process
            print(f"Error creating click touchpoint: {e}")
            return None
    
    def _get_or_create_click_touchpoint(self, element: str, element_id: str, element_class: str, target_url: str) -> 'Touchpoint':
        """Create or get touchpoint for the clicked element."""
        from interactions.models import Touchpoint, Channel, TouchpointClass
        
        # Get or create medium
        from interactions.models import Medium
        medium, created_medium = Medium.objects.get_or_create(
            code='owned_website',
            defaults={'name': 'Owned Website'}
        )
        # Get or create channel
        domain_name = self._extract_domain_name(self.website.base_url)
        # Use consistent channel code (always truncate to 30 chars)
        channel_code = domain_name.lower()[:30]
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
        
        # Get or create touchpoint class
        touchpoint_class, _ = TouchpointClass.objects.get_or_create(
            code='web.internal_click',
            defaults={'name': 'Internal Click'}
        )
        
        # Create touchpoint code based on element
        element_name = element.lower().replace(' ', '_').replace('-', '_')
        touchpoint_code = f"web.click.{element_name}"
        
        # Create touchpoint name
        touchpoint_name = f"Click: {element}"
        if element_id:
            touchpoint_name += f" (ID: {element_id})"
        elif element_class:
            touchpoint_name += f" (Class: {element_class})"
        
        # Create touchpoint description
        description = f"User clicked on {element}"
        if target_url:
            description += f" leading to {target_url}"
        
        # Get or create touchpoint
        touchpoint, _ = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': touchpoint_name,
                'description': description,
                'channel': channel,
                'touchpoint_class': touchpoint_class
            }
        )
        
        return touchpoint
