"""
Web-specific touchpoint resolution.

This module provides web-specific touchpoint resolvers that understand
UTM parameters, referrer analysis, and web-specific touchpoint logic.
"""

from urllib.parse import urlparse
from typing import Optional
import re

from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from interactions.models import Touchpoint, TouchpointClass, Channel


class WebTouchpointResolver(DefaultTouchpointResolver):
    """
    Web-specific touchpoint resolver with UTM analysis and web-specific defaults.
    
    This resolver extends the generic DefaultTouchpointResolver with web-specific
    logic for analyzing UTM parameters, referrer URLs, and providing appropriate
    defaults for web interactions.
    """
    
    def _ensure_required_fields(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> TouchpointHint:
        """
        Ensure web-specific required fields with website-specific channels.
        
        This method provides web-specific defaults and analyzes UTM parameters
        to determine the appropriate channel and medium codes. It creates
        website-specific channels for better tracking across multiple websites.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            hint: The touchpoint hint from the connector's inference
            
        Returns:
            TouchpointHint: The hint with website-specific required fields ensured
        """
        # Get source channel code (where event originated)
        source_channel = self._get_source_channel_code(subject)
        
        # Ensure source channel if not specified
        if not hint.channel_code:
            hint = TouchpointHint(
                code=hint.code,
                channel_code=source_channel,
                medium_code=hint.medium_code or 'unknown',
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Analyze UTM parameters if available (highest priority)
        if hasattr(subject, 'utm_medium') and subject.utm_medium:
            medium = self._analyze_utm_medium(subject.utm_medium)
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code=medium,
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Analyze user agent for native app detection (second priority)
        elif hasattr(subject, 'user_agent') and subject.user_agent and (not hint.medium_code or hint.medium_code == 'unknown'):
            app_medium = self._analyze_user_agent(subject.user_agent)
            if app_medium:
                hint = TouchpointHint(
                    code=hint.code,
                    channel_code=hint.channel_code,
                    medium_code=app_medium,
                    label=hint.label,
                    metadata=hint.metadata
                )
        
        # Analyze referrer if available and no UTM medium or app detection (third priority)
        elif hasattr(subject, 'referrer_url') and subject.referrer_url and (not hint.medium_code or hint.medium_code == 'unknown'):
            medium = self._analyze_referrer(subject.referrer_url)
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code=medium,
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Set default medium if still not specified
        if not hint.medium_code or hint.medium_code == 'unknown':
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code='direct',
                label=hint.label,
                metadata=hint.metadata
            )
        
        return hint
    
    def _get_source_channel_code(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Get source channel code based on event type.
        
        For external click events: Source Channel = External source (Substack, Facebook, etc.)
        For internal website events: Source Channel = Capture Channel (website itself)
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            str: The source channel code
        """
        # Determine if this is an external click event or internal website event
        is_external_click = self._is_external_click_event(subject)
        
        if is_external_click:
            # External click event: Source Channel = External source
            return self._get_external_source_channel(subject)
        else:
            # Internal website event: Source Channel = Capture Channel (website)
            return self._get_website_channel_code(subject)
    
    def _is_external_click_event(self, subject: TouchpointInferenceProtocol) -> bool:
        """
        Determine if this is an external click event or internal website event.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            bool: True if external click event, False if internal website event
        """
        # Check if this is a page view/landing event (external click)
        if hasattr(subject, 'payload') and subject.payload:
            event_type = subject.payload.get('event_type', '')
            if event_type in ['page_view', 'landing', 'external_click']:
                return True
        
        # Check if this is a page view/landing event (metadata)
        if hasattr(subject, 'metadata') and subject.metadata:
            event_type = subject.metadata.get('event_type', '')
            if event_type in ['page_view', 'landing', 'external_click']:
                return True
        
        # Check if this is a page view/landing event (hint code)
        if hasattr(subject, 'infer_touchpoint_hint'):
            try:
                hint = subject.infer_touchpoint_hint()
                if hint.code in ['web.page_view', 'web.landing', 'web.external_click']:
                    return True
            except:
                pass
        
        # Check for external referrer (indicates external click)
        if hasattr(subject, 'referrer_url') and subject.referrer_url:
            if self._is_external_referrer(subject.referrer_url, subject):
                return True
        
        # Check for UTM parameters (indicates external click)
        if hasattr(subject, 'utm_source') and subject.utm_source:
            return True
        
        # Check for native app user agent (indicates external click)
        if hasattr(subject, 'user_agent') and subject.user_agent:
            if self._extract_app_channel_from_user_agent(subject.user_agent):
                return True
        
        # Default: Internal website event
        return False
    
    def _is_external_referrer(self, referrer_url: str, subject: TouchpointInferenceProtocol) -> bool:
        """
        Check if referrer is external to the website.
        
        Args:
            referrer_url: The referrer URL
            subject: The web interaction
            
        Returns:
            bool: True if external referrer, False if internal
        """
        if not referrer_url:
            return False
        
        try:
            from urllib.parse import urlparse
            parsed_referrer = urlparse(referrer_url)
            referrer_domain = parsed_referrer.netloc.lower()
            
            # Get website domain
            website_domain = None
            if hasattr(subject, 'website') and subject.website:
                parsed_website = urlparse(subject.website.base_url)
                website_domain = parsed_website.netloc.lower()
            
            # Remove www. prefix for comparison
            if referrer_domain.startswith('www.'):
                referrer_domain = referrer_domain[4:]
            if website_domain and website_domain.startswith('www.'):
                website_domain = website_domain[4:]
            
            # Check if referrer is external
            return referrer_domain != website_domain
            
        except Exception:
            return True  # Assume external if we can't parse
    
    def _get_external_source_channel(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Get external source channel code (where the external click originated).
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            str: The external source channel code
        """
        # Priority 1: UTM source (if available)
        if hasattr(subject, 'utm_source') and subject.utm_source:
            return self._normalize_utm_source(subject.utm_source)
        
        # Priority 2: Referrer analysis
        if hasattr(subject, 'referrer_url') and subject.referrer_url:
            return self._extract_source_channel_from_referrer(subject.referrer_url)
        
        # Priority 3: User agent analysis for native apps
        if hasattr(subject, 'user_agent') and subject.user_agent:
            app_channel = self._extract_app_channel_from_user_agent(subject.user_agent)
            if app_channel:
                return app_channel
        
        # Fallback: Direct traffic
        return 'direct'
    
    def _get_website_channel_code(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Get website-specific channel code from the subject.
        
        This method extracts the domain from the website URL and uses it as the
        channel code, enabling website-specific tracking for organizations with
        multiple websites.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            str: The website-specific channel code (domain)
        """
        # Try to get website URL from the subject
        if hasattr(subject, 'website') and subject.website:
            return self._extract_domain_from_url(subject.website.base_url)
        
        # Try to get URL from payload or metadata
        if hasattr(subject, 'payload') and subject.payload:
            url = subject.payload.get('url') or subject.payload.get('page_url')
            if url:
                return self._extract_domain_from_url(url)
        
        # Try to get URL from metadata
        if hasattr(subject, 'metadata') and subject.metadata:
            url = subject.metadata.get('url') or subject.metadata.get('page_url')
            if url:
                return self._extract_domain_from_url(url)
        
        # Try to get current URL from session or other fields
        if hasattr(subject, 'current_url') and subject.current_url:
            return self._extract_domain_from_url(subject.current_url)
        
        # Fallback to generic web channel
        return 'web'
    
    def _normalize_utm_source(self, utm_source: str) -> str:
        """
        Normalize UTM source to channel code.
        
        Args:
            utm_source: The UTM source parameter value
            
        Returns:
            str: The normalized channel code
        """
        utm_source = utm_source.lower().strip()
        
        # Common UTM source mappings
        source_mappings = {
            'google': 'google',
            'facebook': 'facebook',
            'twitter': 'twitter',
            'linkedin': 'linkedin',
            'instagram': 'instagram',
            'youtube': 'youtube',
            'substack': 'substack',
            'email': 'email',
            'newsletter': 'email',
            'direct': 'direct'
        }
        
        return source_mappings.get(utm_source, utm_source)
    
    def _extract_source_channel_from_referrer(self, referrer_url: str) -> str:
        """
        Extract source channel from referrer URL.
        
        Args:
            referrer_url: The referrer URL
            
        Returns:
            str: The source channel code
        """
        if not referrer_url:
            return 'direct'
        
        try:
            parsed = urlparse(referrer_url)
            hostname = parsed.netloc.lower() if parsed.netloc else ''
            
            # Remove www. prefix
            if hostname.startswith('www.'):
                hostname = hostname[4:]
            
            # Map common referrers to channel codes
            referrer_mappings = {
                'google.com': 'google',
                'bing.com': 'bing',
                'yahoo.com': 'yahoo',
                'duckduckgo.com': 'duckduckgo',
                'facebook.com': 'facebook',
                'fb.com': 'facebook',
                'twitter.com': 'twitter',
                'x.com': 'twitter',
                't.co': 'twitter',
                'linkedin.com': 'linkedin',
                'instagram.com': 'instagram',
                'youtube.com': 'youtube',
                'substack.com': 'substack',
                'gmail.com': 'email',
                'outlook.com': 'email',
                'mail.yahoo.com': 'email'
            }
            
            return referrer_mappings.get(hostname, hostname)
            
        except Exception:
            return 'direct'
    
    def _extract_app_channel_from_user_agent(self, user_agent: str) -> str:
        """
        Extract app channel from user agent.
        
        Args:
            user_agent: The user agent string
            
        Returns:
            str: The app channel code or None
        """
        if not user_agent:
            return None
            
        user_agent = user_agent.lower()
        
        # App-specific user agent patterns
        app_patterns = {
            r'substackapp': 'substack',
            r'esanapp': 'esan_app',
            r'myapp': 'generic_app',
            r'mobileapp': 'generic_app',
            r'app/\d+\.\d+': 'generic_app'
        }
        
        for pattern, channel in app_patterns.items():
            if re.search(pattern, user_agent):
                return channel
        
        return None
    
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL for channel naming.
        
        This method normalizes URLs to create consistent channel codes:
        - Removes protocol (http://, https://)
        - Removes www. prefix for cleaner channel names
        - Converts to lowercase
        - Handles edge cases gracefully
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            str: The normalized domain for use as channel code
        """
        if not url:
            return 'web'
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for cleaner channel names
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Handle localhost and IP addresses
            if domain in ['localhost', '127.0.0.1'] or domain.startswith('192.168.') or domain.startswith('10.'):
                return 'web'
            
            # Return the cleaned domain
            return domain if domain else 'web'
            
        except Exception:
            return 'web'
    
    def _get_channel_display_name(self, channel_code: str) -> str:
        """
        Get human-friendly display name for channel code.
        
        This method converts source channel codes into human-friendly
        display names for better readability in the admin interface and reports.
        
        Args:
            channel_code: The source channel code
            
        Returns:
            str: Human-friendly channel name
        """
        # Source channel display names
        source_channel_names = {
            # Search engines
            'google': 'Google',
            'bing': 'Bing',
            'yahoo': 'Yahoo',
            'duckduckgo': 'DuckDuckGo',
            
            # Social media
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'linkedin': 'LinkedIn',
            'instagram': 'Instagram',
            'youtube': 'YouTube',
            
            # Email/newsletter
            'email': 'Email',
            'substack': 'Substack',
            
            # Apps
            'esan_app': 'ESAN App',
            'generic_app': 'Mobile App',
            
            # Direct
            'direct': 'Direct',
            
            # Legacy website channels (for backward compatibility)
            'esan.edu.pe': 'ESAN University',
            'ue.edu.pe': 'ESAN UE',
            'esanuniversity.pe': 'ESAN University (International)',
            'web': 'Web Channel',
            'localhost': 'Local Development',
            '127.0.0.1': 'Local Development',
        }
        
        # Check for exact matches first
        if channel_code in source_channel_names:
            return source_channel_names[channel_code]
        
        # Handle legacy domain patterns (for backward compatibility)
        if channel_code.endswith('.edu.pe'):
            # Peruvian educational institutions
            domain_part = channel_code.replace('.edu.pe', '')
            return f"{domain_part.upper()} University"
        elif channel_code.endswith('.edu'):
            # International educational institutions
            domain_part = channel_code.replace('.edu', '')
            return f"{domain_part.title()} University"
        elif channel_code.endswith('.com'):
            # Commercial websites
            domain_part = channel_code.replace('.com', '')
            return f"{domain_part.title()} Website"
        elif channel_code.endswith('.org'):
            # Organization websites
            domain_part = channel_code.replace('.org', '')
            return f"{domain_part.title()} Organization"
        elif channel_code.endswith('.gov'):
            # Government websites
            domain_part = channel_code.replace('.gov', '')
            return f"{domain_part.title()} Government"
        else:
            # Generic fallback - capitalize
            return f"{channel_code.title()}"
    
    def _analyze_user_agent(self, user_agent: str) -> Optional[str]:
        """
        Analyze user agent to detect native app traffic.
        
        This method analyzes the user agent string to identify native mobile apps
        and WebView traffic, providing better detection of app-based interactions
        when UTM parameters are not available.
        
        Args:
            user_agent: The user agent string from the web interaction
            
        Returns:
            Optional[str]: The detected medium ('mobile' for apps, None for web)
        """
        if not user_agent:
            return None
            
        user_agent = user_agent.lower()
        
        # Check for custom app user agents
        app_patterns = [
            r'esanapp',           # ESAN custom app
            r'myapp',             # Generic app pattern
            r'mobileapp',         # Generic mobile app
            r'app/\d+\.\d+',      # App version pattern (e.g., "App/1.0")
        ]
        
        for pattern in app_patterns:
            if re.search(pattern, user_agent):
                return 'mobile'
        
        # Check for WebView patterns
        webview_patterns = [
            r'wv\)',              # WebView indicator
            r'webview',           # WebView in user agent
            r'mobile safari.*wv', # iOS WebView
            r'chrome.*mobile.*wv' # Android WebView
        ]
        
        for pattern in webview_patterns:
            if re.search(pattern, user_agent):
                return 'mobile'
        
        return None
    
    def _analyze_utm_medium(self, utm_medium: str) -> str:
        """
        Analyze UTM medium to determine proper medium code.
        
        Args:
            utm_medium: The UTM medium parameter value
            
        Returns:
            str: The standardized medium code
        """
        if not utm_medium:
            return 'direct'
        
        utm_medium = utm_medium.lower().strip()
        
        # Paid advertising
        if utm_medium in ['cpc', 'ppc', 'paid', 'paidsearch', 'paid_search']:
            return 'paid'
        
        # Email marketing
        elif utm_medium in ['email', 'newsletter', 'mail', 'mailing']:
            return 'email'
        
        # Social media
        elif utm_medium in ['social', 'facebook', 'twitter', 'linkedin', 'instagram', 'tiktok', 'youtube']:
            return 'social'
        
        # Referral traffic
        elif utm_medium in ['referral', 'referrer', 'refer']:
            return 'referral'
        
        # Organic search
        elif utm_medium in ['organic', 'seo', 'search', 'natural']:
            return 'organic'
        
        # Display advertising
        elif utm_medium in ['display', 'banner', 'cpm']:
            return 'display'
        
        # Video advertising
        elif utm_medium in ['video', 'youtube_ads', 'video_ads']:
            return 'video'
        
        # Mobile app
        elif utm_medium in ['mobile', 'app', 'mobile_app']:
            return 'mobile'
        
        # Affiliate marketing
        elif utm_medium in ['affiliate', 'partner', 'aff']:
            return 'affiliate'
        
        # Content marketing
        elif utm_medium in ['content', 'blog', 'article']:
            return 'content'
        
        # Return the original value if no match found
        else:
            return utm_medium
    
    def _analyze_referrer(self, referrer_url: str) -> str:
        """
        Analyze referrer URL to determine medium.
        
        Args:
            referrer_url: The referrer URL
            
        Returns:
            str: The determined medium code
        """
        if not referrer_url:
            return 'direct'
        
        try:
            parsed = urlparse(referrer_url)
            hostname = parsed.hostname.lower() if parsed.hostname else ''
            
            # Social media domains
            social_domains = [
                'facebook.com', 'fb.com', 'twitter.com', 'x.com', 't.co',
                'linkedin.com', 'instagram.com', 'tiktok.com', 'youtube.com',
                'pinterest.com', 'reddit.com', 'snapchat.com', 'whatsapp.com'
            ]
            
            for domain in social_domains:
                if domain in hostname:
                    return 'social'
            
            # Search engines
            search_domains = [
                'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
                'baidu.com', 'yandex.com', 'ask.com', 'aol.com'
            ]
            
            for domain in search_domains:
                if domain in hostname:
                    return 'organic'
            
            # Email providers (for email links)
            email_domains = [
                'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
                'mail.yahoo.com', 'mail.google.com'
            ]
            
            for domain in email_domains:
                if domain in hostname:
                    return 'email'
            
            # If it's an external referrer, it's referral
            if hostname and not hostname.startswith('localhost') and not hostname.startswith('127.0.0.1'):
                return 'referral'
            
            return 'direct'
            
        except Exception:
            return 'unknown'
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """
        Create or get touchpoint with web-specific logic.
        
        This method extends the base implementation with web-specific
        touchpoint class creation and channel handling.
        
        Args:
            hint: The touchpoint hint containing all necessary information
            
        Returns:
            Touchpoint: The created or existing touchpoint
        """
        # Get or create website-specific channel
        channel = None
        if hint.channel_code:
            channel_name = self._get_channel_display_name(hint.channel_code)
            channel, _ = Channel.objects.get_or_create(
                code=hint.channel_code,
                defaults={'name': channel_name}
            )
        
        # Get or create touchpoint class with web-specific logic
        touchpoint_class = None
        if hint.code:
            # Extract class code from touchpoint code (e.g., "web" from "web.page_read")
            class_code = hint.code.split('.')[0] if '.' in hint.code else hint.code
            
            # Web-specific touchpoint class names
            class_names = {
                'web': 'Web Touchpoint',
                'page': 'Page View',
                'form': 'Form Submission',
                'click': 'Click Event',
                'download': 'Download',
                'video': 'Video Play',
                'generic': 'Generic Web Interaction'
            }
            
            class_name = class_names.get(class_code, f"{class_code.title()} Touchpoint")
            
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code=class_code,
                defaults={
                    'name': class_name,
                    'description': f"Web touchpoint class for {class_code} interactions"
                }
            )
        
        # Create or get touchpoint
        touchpoint_code = hint.code or f"web.generic"
        touchpoint_name = hint.label or hint.code or 'Web Interaction'
        
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': touchpoint_name,
                'touchpoint_class': touchpoint_class,
                'description': f"Web touchpoint for {touchpoint_code}",
                'is_active': True
            }
        )
        
        return touchpoint


class CachedWebTouchpointResolver(WebTouchpointResolver):
    """
    Cached version of the web touchpoint resolver for improved performance.
    
    This resolver adds caching to the web-specific touchpoint resolution process
    to avoid repeated database queries for the same touchpoint codes and UTM analysis.
    """
    
    def __init__(self, mapping_provider, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached web resolver.
        
        Args:
            mapping_provider: Provider for looking up mapping rules
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        super().__init__(mapping_provider)
        self.cache_timeout = cache_timeout
        self.use_cache = use_cache
        self._utm_analysis_cache = {}
        self._referrer_analysis_cache = {}
        self._domain_extraction_cache = {}
        self._channel_display_name_cache = {}
        self._user_agent_analysis_cache = {}
        self._source_channel_cache = {}
        self._utm_source_cache = {}
        self._referrer_channel_cache = {}
        self._app_channel_cache = {}
        self._external_click_cache = {}
        self._external_referrer_cache = {}
        self._website_channel_cache = {}
    
    def _analyze_utm_medium(self, utm_medium: str) -> str:
        """
        Analyze UTM medium with caching.
        
        Args:
            utm_medium: The UTM medium parameter value
            
        Returns:
            str: The standardized medium code
        """
        if not self.use_cache:
            return super()._analyze_utm_medium(utm_medium)
        
        if utm_medium in self._utm_analysis_cache:
            return self._utm_analysis_cache[utm_medium]
        
        result = super()._analyze_utm_medium(utm_medium)
        self._utm_analysis_cache[utm_medium] = result
        
        return result
    
    def _analyze_referrer(self, referrer_url: str) -> str:
        """
        Analyze referrer URL with caching.
        
        Args:
            referrer_url: The referrer URL
            
        Returns:
            str: The determined medium code
        """
        if not self.use_cache:
            return super()._analyze_referrer(referrer_url)
        
        if referrer_url in self._referrer_analysis_cache:
            return self._referrer_analysis_cache[referrer_url]
        
        result = super()._analyze_referrer(referrer_url)
        self._referrer_analysis_cache[referrer_url] = result
        
        return result
    
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL with caching.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            str: The normalized domain for use as channel code
        """
        if not self.use_cache:
            return super()._extract_domain_from_url(url)
        
        if url in self._domain_extraction_cache:
            return self._domain_extraction_cache[url]
        
        result = super()._extract_domain_from_url(url)
        self._domain_extraction_cache[url] = result
        
        return result
    
    def _get_channel_display_name(self, channel_code: str) -> str:
        """
        Get human-friendly display name for channel code with caching.
        
        Args:
            channel_code: The channel code (domain)
            
        Returns:
            str: Human-friendly channel name
        """
        if not self.use_cache:
            return super()._get_channel_display_name(channel_code)
        
        if channel_code in self._channel_display_name_cache:
            return self._channel_display_name_cache[channel_code]
        
        result = super()._get_channel_display_name(channel_code)
        self._channel_display_name_cache[channel_code] = result
        
        return result
    
    def _analyze_user_agent(self, user_agent: str) -> Optional[str]:
        """
        Analyze user agent with caching.
        
        Args:
            user_agent: The user agent string from the web interaction
            
        Returns:
            Optional[str]: The detected medium ('mobile' for apps, None for web)
        """
        if not self.use_cache:
            return super()._analyze_user_agent(user_agent)
        
        if user_agent in self._user_agent_analysis_cache:
            return self._user_agent_analysis_cache[user_agent]
        
        result = super()._analyze_user_agent(user_agent)
        self._user_agent_analysis_cache[user_agent] = result
        
        return result
    
    def _normalize_utm_source(self, utm_source: str) -> str:
        """
        Normalize UTM source with caching.
        
        Args:
            utm_source: The UTM source parameter value
            
        Returns:
            str: The normalized channel code
        """
        if not self.use_cache:
            return super()._normalize_utm_source(utm_source)
        
        if utm_source in self._utm_source_cache:
            return self._utm_source_cache[utm_source]
        
        result = super()._normalize_utm_source(utm_source)
        self._utm_source_cache[utm_source] = result
        
        return result
    
    def _extract_source_channel_from_referrer(self, referrer_url: str) -> str:
        """
        Extract source channel from referrer URL with caching.
        
        Args:
            referrer_url: The referrer URL
            
        Returns:
            str: The source channel code
        """
        if not self.use_cache:
            return super()._extract_source_channel_from_referrer(referrer_url)
        
        if referrer_url in self._referrer_channel_cache:
            return self._referrer_channel_cache[referrer_url]
        
        result = super()._extract_source_channel_from_referrer(referrer_url)
        self._referrer_channel_cache[referrer_url] = result
        
        return result
    
    def _extract_app_channel_from_user_agent(self, user_agent: str) -> str:
        """
        Extract app channel from user agent with caching.
        
        Args:
            user_agent: The user agent string
            
        Returns:
            str: The app channel code or None
        """
        if not self.use_cache:
            return super()._extract_app_channel_from_user_agent(user_agent)
        
        if user_agent in self._app_channel_cache:
            return self._app_channel_cache[user_agent]
        
        result = super()._extract_app_channel_from_user_agent(user_agent)
        self._app_channel_cache[user_agent] = result
        
        return result
    
    def _is_external_click_event(self, subject: TouchpointInferenceProtocol) -> bool:
        """
        Determine if this is an external click event with caching.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            bool: True if external click event, False if internal website event
        """
        if not self.use_cache:
            return super()._is_external_click_event(subject)
        
        # Create a cache key based on subject attributes
        cache_key = self._create_subject_cache_key(subject)
        
        if cache_key in self._external_click_cache:
            return self._external_click_cache[cache_key]
        
        result = super()._is_external_click_event(subject)
        self._external_click_cache[cache_key] = result
        
        return result
    
    def _is_external_referrer(self, referrer_url: str, subject: TouchpointInferenceProtocol) -> bool:
        """
        Check if referrer is external with caching.
        
        Args:
            referrer_url: The referrer URL
            subject: The web interaction
            
        Returns:
            bool: True if external referrer, False if internal
        """
        if not self.use_cache:
            return super()._is_external_referrer(referrer_url, subject)
        
        # Create a cache key based on referrer and website
        website_url = getattr(subject.website, 'base_url', '') if hasattr(subject, 'website') and subject.website else ''
        cache_key = f"{referrer_url}|{website_url}"
        
        if cache_key in self._external_referrer_cache:
            return self._external_referrer_cache[cache_key]
        
        result = super()._is_external_referrer(referrer_url, subject)
        self._external_referrer_cache[cache_key] = result
        
        return result
    
    def _get_website_channel_code(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Get website-specific channel code with caching.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            str: The website-specific channel code (domain)
        """
        if not self.use_cache:
            return super()._get_website_channel_code(subject)
        
        # Create a cache key based on subject attributes
        cache_key = self._create_subject_cache_key(subject)
        
        if cache_key in self._website_channel_cache:
            return self._website_channel_cache[cache_key]
        
        result = super()._get_website_channel_code(subject)
        self._website_channel_cache[cache_key] = result
        
        return result
    
    def _create_subject_cache_key(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Create a cache key for subject-based caching.
        
        Args:
            subject: The web interaction
            
        Returns:
            str: A cache key string
        """
        key_parts = []
        
        # Add website URL
        if hasattr(subject, 'website') and subject.website:
            key_parts.append(f"website:{subject.website.base_url}")
        
        # Add payload URL
        if hasattr(subject, 'payload') and subject.payload:
            url = subject.payload.get('url') or subject.payload.get('page_url')
            if url:
                key_parts.append(f"payload_url:{url}")
        
        # Add metadata URL
        if hasattr(subject, 'metadata') and subject.metadata:
            url = subject.metadata.get('url') or subject.metadata.get('page_url')
            if url:
                key_parts.append(f"metadata_url:{url}")
        
        # Add current URL
        if hasattr(subject, 'current_url') and subject.current_url:
            key_parts.append(f"current_url:{subject.current_url}")
        
        # Add event type
        if hasattr(subject, 'payload') and subject.payload:
            event_type = subject.payload.get('event_type', '')
            if event_type:
                key_parts.append(f"event_type:{event_type}")
        
        if hasattr(subject, 'metadata') and subject.metadata:
            event_type = subject.metadata.get('event_type', '')
            if event_type:
                key_parts.append(f"metadata_event_type:{event_type}")
        
        return "|".join(key_parts) if key_parts else "default"
