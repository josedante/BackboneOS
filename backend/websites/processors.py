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

from interactions.models import Action, Agent, Interaction, Touchpoint, Channel, TouchpointType, Medium
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
            
            # Create the owned_website medium and channel
            medium, _ = Medium.objects.get_or_create(
                code='owned_website',
                defaults={'name': 'Owned Website'}
            )
            
            domain_name = self._extract_domain_name(base_url)
            # Truncate domain name if too long for channel code (30 char limit)
            channel_code = domain_name[:30] if len(domain_name) > 30 else domain_name
            channel_name = self._get_channel_display_name(domain_name)
            channel, _ = Channel.objects.get_or_create(
                code=channel_code,
                defaults={
                    'name': channel_name,
                    'medium': medium
                }
            )
            
            website = Website.objects.create(
                base_url=base_url,
                name=f"{self._extract_domain_name(base_url)} Website",
                division=division,
                channel=channel,
                active=True
            )
            
            logger.info(f"Created new website: {website.base_url} with channel: {channel.code}")
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
        channel_code = f"{domain_name}"[:30]
        channel, created = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': f'{domain_name}'
            }
        )
        
        # Always set the medium
        if channel.medium != medium:
            channel.medium = medium
            channel.save(update_fields=['medium'])
        
        return channel, medium
    
    def _get_or_create_traffic_channel_and_medium(self):
        """
        Get or create channel and medium for traffic source analysis.
        
        This method analyzes the event data to determine the traffic source
        and creates appropriate channel and medium objects based on:
        1. UTM parameters (highest priority)
        2. Referrer analysis (second priority) 
        3. User agent analysis (third priority)
        4. Direct traffic fallback (lowest priority)
        
        Returns:
            tuple: (channel, medium) objects
        """
        # Extract traffic source information
        utm_medium = self.event_data.get('utm_medium', '')
        utm_source = self.event_data.get('utm_source', '')
        utm_campaign = self.event_data.get('utm_campaign', '')
        referrer_url = self.event_data.get('referrer', '')
        user_agent = self.event_data.get('user_agent', '')
        
        # Priority 1: UTM parameters analysis
        if utm_medium:
            medium_code, channel_code = self._analyze_utm_traffic(utm_medium, utm_source)
        # Priority 2: Referrer analysis
        elif referrer_url:
            medium_code, channel_code = self._analyze_referrer_traffic(referrer_url)
        # Priority 3: User agent analysis for native apps
        elif user_agent:
            medium_code, channel_code = self._analyze_user_agent_traffic(user_agent)
        # Priority 4: Direct traffic fallback
        else:
            medium_code, channel_code = self._get_direct_traffic()
        
        # Get or create medium
        medium, _ = Medium.objects.get_or_create(
            code=medium_code,
            defaults={'name': self._get_medium_display_name(medium_code)}
        )
        
        # Get or create channel
        channel_name = self._get_channel_display_name(channel_code)
        channel, _ = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': channel_name,
                'medium': medium
            }
        )
        
        # Ensure medium is set on channel
        if channel.medium != medium:
            channel.medium = medium
            channel.save(update_fields=['medium'])
        
        return channel, medium
    
    def _analyze_utm_traffic(self, utm_medium: str, utm_source: str) -> tuple:
        """
        Analyze UTM parameters to determine medium and channel.
        
        Args:
            utm_medium: UTM medium parameter
            utm_source: UTM source parameter
            
        Returns:
            tuple: (medium_code, channel_code)
        """
        # Normalize UTM medium
        utm_medium = utm_medium.lower().strip()
        
        # Map UTM medium to standardized medium codes
        medium_mappings = {
            'cpc': 'paid',
            'ppc': 'paid', 
            'paid': 'paid',
            'paidsearch': 'paid',
            'paid_search': 'paid',
            'email': 'email',
            'newsletter': 'email',
            'mail': 'email',
            'mailing': 'email',
            'social': 'social',
            'facebook': 'social',
            'twitter': 'social',
            'linkedin': 'social',
            'instagram': 'social',
            'tiktok': 'social',
            'youtube': 'social',
            'referral': 'referral',
            'referrer': 'referral',
            'refer': 'referral',
            'organic': 'organic',
            'seo': 'organic',
            'search': 'organic',
            'natural': 'organic',
            'display': 'display',
            'banner': 'display',
            'cpm': 'display',
            'video': 'video',
            'youtube_ads': 'video',
            'video_ads': 'video',
            'mobile': 'mobile',
            'app': 'mobile',
            'mobile_app': 'mobile',
            'affiliate': 'affiliate',
            'partner': 'affiliate',
            'aff': 'affiliate',
            'content': 'content',
            'blog': 'content',
            'article': 'content'
        }
        
        medium_code = medium_mappings.get(utm_medium, utm_medium)
        
        # Normalize UTM source to channel code
        if utm_source:
            utm_source = utm_source.lower().strip()
            channel_mappings = {
                'google': 'google',
                'facebook': 'facebook',
                'twitter': 'twitter',
                'linkedin': 'linkedin',
                'instagram': 'instagram',
                'youtube': 'youtube',
                'substack': 'substack',
                'email': 'email',
                'newsletter': 'email',
                'web_direct': 'web_direct'
            }
            channel_code = channel_mappings.get(utm_source, utm_source)
        else:
            channel_code = 'web_direct'
        
        return medium_code, channel_code
    
    def _analyze_referrer_traffic(self, referrer_url: str) -> tuple:
        """
        Analyze referrer URL to determine medium and channel.
        
        Args:
            referrer_url: The referrer URL
            
        Returns:
            tuple: (medium_code, channel_code)
        """
        if not referrer_url:
            return 'web_direct', 'web_direct'
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(referrer_url)
            hostname = parsed.hostname.lower() if parsed.hostname else ''
            
            # Remove www. prefix
            if hostname.startswith('www.'):
                hostname = hostname[4:]
            
            # Check if referrer is internal to the current website
            current_website_domain = self._extract_domain_name(self.website.base_url)
            if hostname == current_website_domain:
                # Internal referrer - channel should be the internal website
                return 'owned_website', current_website_domain
            
            # Check if referrer is from a different owned website (same organization)
            if self._is_owned_website(hostname):
                # Different owned website - medium is owned_website, channel is the referrer domain
                domain_parts = hostname.split('.')
                if len(domain_parts) >= 2:
                    domain_name = domain_parts[0]  # Get the main domain part
                    return 'owned_website', domain_name
                return 'owned_website', hostname
            
            # Social media domains
            social_domains = {
                'facebook.com': 'facebook',
                'fb.com': 'facebook', 
                'twitter.com': 'twitter',
                'x.com': 'twitter',
                't.co': 'twitter',
                'linkedin.com': 'linkedin',
                'instagram.com': 'instagram',
                'tiktok.com': 'tiktok',
                'youtube.com': 'youtube',
                'pinterest.com': 'pinterest',
                'reddit.com': 'reddit',
                'snapchat.com': 'snapchat',
                'whatsapp.com': 'whatsapp'
            }
            
            # Check for social media
            for domain, channel in social_domains.items():
                if domain in hostname:
                    return 'social', channel
            
            # Search engines
            search_domains = {
                'google.com': 'google',
                'bing.com': 'bing',
                'yahoo.com': 'yahoo',
                'duckduckgo.com': 'duckduckgo',
                'baidu.com': 'baidu',
                'yandex.com': 'yandex',
                'ask.com': 'ask',
                'aol.com': 'aol',
                'kagi.com': 'kagi'
            }
            
            # Check for search engines
            for domain, channel in search_domains.items():
                if domain in hostname:
                    return 'organic_search', channel
            
            # Email providers
            email_domains = {
                'gmail.com': 'gmail',
                'outlook.com': 'outlook',
                'yahoo.com': 'yahoo',
                'hotmail.com': 'hotmail',
                'mail.yahoo.com': 'yahoo',
                'mail.google.com': 'gmail'
            }
            
            # Check for email providers
            for domain, channel in email_domains.items():
                if domain in hostname:
                    return 'email', channel
            
            # If it's an external referrer, it's referral
            if hostname and not hostname.startswith('localhost') and not hostname.startswith('127.0.0.1'):
                # Extract domain name without TLD for generic external referrers
                domain_parts = hostname.split('.')
                if len(domain_parts) >= 2:
                    domain_name = domain_parts[0]  # Get the main domain part
                    return 'referrer', domain_name
                return 'referrer', hostname
            
            return 'owned_website', 'web.owned_referrer'
            
        except Exception:
            return 'owned_website', 'web.owned_referrer'
    
    def _analyze_user_agent_traffic(self, user_agent: str) -> tuple:
        """
        Analyze user agent to detect native app traffic.
        
        Args:
            user_agent: The user agent string
            
        Returns:
            tuple: (medium_code, channel_code)
        """
        if not user_agent:
            return 'web_direct', 'web_direct'
        
        user_agent = user_agent.lower()
        
        # App-specific user agent patterns
        app_patterns = {
            r'substackapp': ('mobile', 'substack'),
            r'esanapp': ('mobile', 'esan_app'),
            r'myapp': ('mobile', 'generic_app'),
            r'mobileapp': ('mobile', 'generic_app'),
            r'app/\d+\.\d+': ('mobile', 'generic_app')
        }
        
        import re
        for pattern, (medium, channel) in app_patterns.items():
            if re.search(pattern, user_agent):
                return medium, channel
        
        # Check for WebView patterns
        webview_patterns = [
            r'wv\)',              # WebView indicator
            r'webview',           # WebView in user agent
            r'mobile safari.*wv', # iOS WebView
            r'chrome.*mobile.*wv' # Android WebView
        ]
        
        for pattern in webview_patterns:
            if re.search(pattern, user_agent):
                return 'mobile', 'webview'
        
        # If no app patterns found, fall back to direct traffic
        return self._get_direct_traffic()
    
    def _get_direct_traffic(self) -> tuple:
        """
        Get direct traffic classification.
        
        Returns:
            tuple: (medium_code, channel_code)
        """
        # Extract domain from website base URL for channel
        domain_name = self._extract_domain_name(self.website.base_url)
        return 'web_direct', domain_name
    
    def _get_medium_display_name(self, medium_code: str) -> str:
        """
        Get human-friendly display name for medium code.
        
        Args:
            medium_code: The medium code
            
        Returns:
            str: Human-friendly medium name
        """
        medium_names = {
            'paid': 'Paid Advertising',
            'email': 'Email Marketing',
            'social': 'Social Media',
            'referral': 'Referral Traffic',
            'organic': 'Organic Search',
            'organic_search': 'Organic Search',
            'display': 'Display Advertising',
            'video': 'Video Advertising',
            'mobile': 'Mobile App',
            'affiliate': 'Affiliate Marketing',
            'content': 'Content Marketing',
            'web_direct': 'Direct Traffic',
            'owned_website': 'Owned Website'
        }
        
        return medium_names.get(medium_code, medium_code.title())
    
    def _get_channel_display_name(self, channel_code: str) -> str:
        """
        Get human-friendly display name for channel code.
        
        Args:
            channel_code: The channel code
            
        Returns:
            str: Human-friendly channel name
        """
        channel_names = {
            # Search engines
            'google': 'Google',
            'bing': 'Bing',
            'yahoo': 'Yahoo',
            'duckduckgo': 'DuckDuckGo',
            'baidu': 'Baidu',
            'yandex': 'Yandex',
            'ask': 'Ask',
            'aol': 'AOL',
            
            # Social media
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'linkedin': 'LinkedIn',
            'instagram': 'Instagram',
            'youtube': 'YouTube',
            'tiktok': 'TikTok',
            'pinterest': 'Pinterest',
            'reddit': 'Reddit',
            'snapchat': 'Snapchat',
            'whatsapp': 'WhatsApp',
            
            # Email providers
            'gmail': 'Gmail',
            'outlook': 'Outlook',
            'hotmail': 'Hotmail',
            
            # Apps
            'substack': 'Substack',
            'esan_app': 'ESAN App',
            'generic_app': 'Mobile App',
            'webview': 'WebView',
            
            # Direct
            'web_direct': 'Direct Traffic'
        }
        
        # Check for exact matches first
        if channel_code in channel_names:
            return channel_names[channel_code]
        
        # Handle domain patterns
        if channel_code.endswith('.com'):
            domain_part = channel_code.replace('.com', '')
            return f"{domain_part.title()}.com Website"
        elif channel_code.endswith('.edu.pe'):
            domain_part = channel_code.replace('.edu.pe', '')
            return f"{domain_part.upper()} University"
        elif channel_code.endswith('.edu'):
            domain_part = channel_code.replace('.edu', '')
            return f"{domain_part.title()} University"
        else:
            # Generic fallback - capitalize
            return f"{channel_code.title()}"
    
    def _get_traffic_touchpoint_class_code(self, medium_code: str) -> str:
        """
        Get touchpoint class code based on medium for traffic classification.
        
        Args:
            medium_code: The medium code from traffic analysis
            
        Returns:
            str: The touchpoint class code
        """
        touchpoint_class_mappings = {
            'paid': 'web.paid_traffic',
            'email': 'web.email_traffic',
            'social': 'web.social_traffic',
            'referral': 'web.referral_traffic',
            'organic': 'web.organic_traffic',
            'organic_search': 'web.organic_traffic',
            'display': 'web.display_traffic',
            'video': 'web.video_traffic',
            'mobile': 'web.mobile_traffic',
            'affiliate': 'web.affiliate_traffic',
            'content': 'web.content_traffic',
            'web_direct': 'web.direct_traffic',
            'owned_website': 'web.referral_traffic'  # Changed to referral_traffic for owned websites
        }
        
        return touchpoint_class_mappings.get(medium_code, 'web.unknown_traffic')
    
    def _get_traffic_touchpoint_class_name(self, touchpoint_class_code: str) -> str:
        """
        Get human-friendly touchpoint class name.
        
        Args:
            touchpoint_class_code: The touchpoint class code
            
        Returns:
            str: Human-friendly touchpoint class name
        """
        touchpoint_class_names = {
            'web.paid_traffic': 'Paid Advertising Traffic',
            'web.email_traffic': 'Email Marketing Traffic',
            'web.social_traffic': 'Social Media Traffic',
            'web.referral_traffic': 'Referral Traffic',
            'web.organic_traffic': 'Organic Search Traffic',
            'web.display_traffic': 'Display Advertising Traffic',
            'web.video_traffic': 'Video Advertising Traffic',
            'web.mobile_traffic': 'Mobile App Traffic',
            'web.affiliate_traffic': 'Affiliate Marketing Traffic',
            'web.content_traffic': 'Content Marketing Traffic',
            'web.direct_traffic': 'Direct Traffic',
            'web.internal_traffic': 'Internal Website Traffic',
            'web.unknown_traffic': 'Unknown Traffic Source'
        }
        
        return touchpoint_class_names.get(touchpoint_class_code, 'Unknown Traffic Source')
    
    def _is_owned_website(self, hostname: str) -> bool:
        """
        Check if a hostname belongs to an owned website (same organization).
        
        This method checks if the referrer domain is from the same organization
        as the current website. This would typically involve checking against
        a list of owned domains or using some organizational domain pattern.
        
        Args:
            hostname: The hostname to check
            
        Returns:
            bool: True if the hostname is an owned website
        """
        try:
            # Get all websites in the same division as current website
            owned_websites = Website.objects.filter(
                division=self.website.division,
                active=True
            ).exclude(id=self.website.id)  # Exclude current website
            
            # Check if referrer domain matches any owned website domain
            for website in owned_websites:
                owned_domain = self._extract_domain_name(website.base_url)
                if hostname == owned_domain:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking owned website for {hostname}: {e}")
            return False
    
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
            touchpoint_class, _ = TouchpointType.objects.get_or_create(
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
            # Get channel and medium using traffic analysis
            channel, medium = self._get_or_create_traffic_channel_and_medium()
            
            # Determine touchpoint class based on medium
            touchpoint_class_code = self._get_traffic_touchpoint_class_code(medium.code)
            touchpoint_class_name = self._get_traffic_touchpoint_class_name(touchpoint_class_code)
            
            touchpoint_class, _ = TouchpointType.objects.get_or_create(
                code=touchpoint_class_code,
                defaults={'name': touchpoint_class_name}
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
            touchpoint_class, _ = TouchpointType.objects.get_or_create(
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
            touchpoint_class, _ = TouchpointType.objects.get_or_create(
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
            touchpoint_class, _ = TouchpointType.objects.get_or_create(
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