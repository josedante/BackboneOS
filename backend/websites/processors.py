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
from .models import WebInteraction, Website
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
        
    def process(self) -> List[WebInteraction]:
        """
        Process the page view event and create all applicable interactions.
        
        Returns:
            List[WebInteraction]: List of created WebInteraction instances
        """
        # Check session start criteria BEFORE creating any interactions
        should_start_session = self._should_start_new_session()
        has_external_referrer = self._has_external_referrer()
        
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
        """Get or create agent from user agent string."""
        user_agent = self.event_data.get('user_agent', '')
        if not user_agent:
            user_agent = 'Unknown Browser'
        
        # Extract browser name from user agent
        browser_name = self._extract_browser_name(user_agent)
        
        agent, created = Agent.objects.get_or_create(
            name=browser_name,
            defaults={
                'agent_type': 'browser',
                'identifier': f"{browser_name.lower()}-{self._extract_browser_version(user_agent)}"
            }
        )
        return agent
    
    def _extract_browser_name(self, user_agent: str) -> str:
        """Extract browser name from user agent string."""
        user_agent = user_agent.lower()
        
        if 'chrome' in user_agent:
            return 'Chrome'
        elif 'firefox' in user_agent:
            return 'Firefox'
        elif 'safari' in user_agent:
            return 'Safari'
        elif 'edge' in user_agent:
            return 'Edge'
        elif 'opera' in user_agent:
            return 'Opera'
        else:
            return 'Unknown Browser'
    
    def _extract_browser_version(self, user_agent: str) -> str:
        """Extract browser version from user agent string."""
        import re
        
        # Try to extract version number
        version_match = re.search(r'version/(\d+\.\d+)', user_agent.lower())
        if version_match:
            return version_match.group(1)
        
        # Try Chrome version
        chrome_match = re.search(r'chrome/(\d+\.\d+)', user_agent.lower())
        if chrome_match:
            return chrome_match.group(1)
        
        return 'Unknown'
    
    def _extract_platform(self, user_agent: str) -> str:
        """Extract platform from user agent string."""
        user_agent = user_agent.lower()
        
        if 'windows' in user_agent:
            return 'Windows'
        elif 'mac' in user_agent or 'macos' in user_agent:
            return 'macOS'
        elif 'linux' in user_agent:
            return 'Linux'
        elif 'android' in user_agent:
            return 'Android'
        elif 'ios' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent:
            return 'iOS'
        else:
            return 'Unknown'
    
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
