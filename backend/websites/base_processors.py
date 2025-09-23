"""
Base web event processors with common functionality.

This module contains base classes and utilities for processing web events,
extracting common functionality from individual event processors.
"""

from django.db import transaction
from django.utils import timezone
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import logging

from interactions.models import Action, Agent, Interaction
from .models import WebInteraction, Website, WebAgent, WebSession

logger = logging.getLogger(__name__)


class BaseWebEventProcessor:
    """
    Base class for web event processors with common functionality.
    
    This class provides shared methods for:
    - Website creation and management
    - User agent parsing and agent creation
    - Session management
    - Common utility functions
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
        except Exception as e:
            logger.warning(f"Error creating default division: {e}")
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
        except Exception as e:
            logger.warning(f"Error parsing domain from URL {url}: {e}")
            return "Unknown Website"
    
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
            logger.warning(f"Error parsing user agent '{user_agent}': {e}")
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
    
    def _get_or_create_session(self, should_start_new: bool = False) -> WebSession:
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
    
    def _create_base_web_interaction(self, action_code: str, action_name: str, action_description: str, 
                                   interaction_type: str, payload: dict) -> WebInteraction:
        """Create a base WebInteraction with common fields."""
        # Get or create action
        action = Action.objects.get_or_create(
            code=action_code,
            defaults={'name': action_name, 'description': action_description}
        )[0]
        
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
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        return web_interaction
    
    def _get_or_create_channel_and_medium(self):
        """Get or create channel and medium for touchpoint creation."""
        from interactions.models import Channel, Medium
        
        # Get or create medium
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
        
        return channel, medium
