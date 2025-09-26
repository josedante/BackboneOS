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
from interactions.models import Touchpoint, TouchpointType, Channel, Medium


class WebTouchpointResolver(DefaultTouchpointResolver):
    """
    Web-specific touchpoint resolver with UTM analysis and web-specific defaults.
    
    This resolver extends the generic DefaultTouchpointResolver with web-specific
    logic for analyzing UTM parameters, referrer URLs, and providing appropriate
    defaults for web interactions.
    """
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """Get connector type for web interactions."""
        return 'web'
    
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
        
        # If no UTM medium, try other methods
        if not hint.medium_code or hint.medium_code == 'unknown':
            # Analyze user agent for native app detection (second priority)
            if hasattr(subject, 'user_agent') and subject.user_agent:
                app_medium = self._analyze_user_agent(subject.user_agent)
                if app_medium:
                    hint = TouchpointHint(
                        code=hint.code,
                        channel_code=hint.channel_code,
                        medium_code=app_medium,
                        label=hint.label,
                        metadata=hint.metadata
                    )
            
            # Analyze referrer if available (third priority)
            if (not hint.medium_code or hint.medium_code == 'unknown') and hasattr(subject, 'referrer_url') and subject.referrer_url:
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
                    medium_code='web_direct',
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
        
        This method intelligently distinguishes between external landing events
        and internal website interactions based on context clues.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            bool: True if external click event, False if internal website event
        """
        # Get event type from various sources
        event_type = None
        if hasattr(subject, 'payload') and subject.payload:
            event_type = subject.payload.get('event_type', '')
        elif hasattr(subject, 'metadata') and subject.metadata:
            event_type = subject.metadata.get('event_type', '')
        elif hasattr(subject, 'infer_touchpoint_hint'):
            try:
                hint = subject.infer_touchpoint_hint()
                if 'page_view' in hint.code:
                    event_type = 'page_view'
                elif 'landing' in hint.code:
                    event_type = 'landing'
                elif 'external_click' in hint.code:
                    event_type = 'external_click'
            except:
                pass
        
        # Handle explicit external events
        if event_type in ['landing', 'external_click']:
            return True
        
        # Handle page_view events intelligently
        if event_type == 'page_view':
            # Check for external indicators
            has_external_referrer = (hasattr(subject, 'referrer_url') and 
                                   subject.referrer_url and 
                                   self._is_external_referrer(subject.referrer_url, subject))
            
            has_utm_parameters = (hasattr(subject, 'utm_source') and subject.utm_source)
            
            has_app_user_agent = (hasattr(subject, 'user_agent') and 
                                subject.user_agent and 
                                self._extract_app_channel_from_user_agent(subject.user_agent))
            
            # Only treat as external if there are external indicators
            if has_external_referrer or has_utm_parameters or has_app_user_agent:
                return True
            else:
                # No external indicators = internal page view
                return False
        
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
        return 'web_direct'
    
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
            'web_direct': 'web_direct'
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
            return 'web_direct'
        
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
            return 'web_direct'
    
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
            'web_direct': 'Web Direct',
            
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
            r'app',               # some custom app
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
            return 'web_direct'
        
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
            return 'web_direct'
        
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
            
            return 'web_direct'
            
        except Exception:
            return 'unknown'
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """
        Create or get touchpoint with enhanced web-specific logic.
        
        This method creates rich, feature-rich TouchpointClass categories
        for better ML analysis and predictive modeling.
        
        Args:
            hint: The touchpoint hint containing all necessary information
            
        Returns:
            Touchpoint: The created or existing touchpoint
        """
        # Get or create channel (WHERE the interaction happened)
        channel = None
        if hint.channel_code:
            channel_name = self._get_channel_display_name(hint.channel_code)
            channel, created = Channel.objects.get_or_create(
                code=hint.channel_code,
                defaults={
                    'name': channel_name
                }
            )
        else:
            # Determine channel from the subject if not provided
            channel_code = self._determine_channel_from_subject(hint)
            if channel_code:
                channel_name = self._get_channel_display_name(channel_code)
                channel, created = Channel.objects.get_or_create(
                    code=channel_code,
                    defaults={
                        'name': channel_name
                    }
                )
        
        # Get or create medium (HOW it communicates)
        medium = None
        if hint.medium_code:
            medium, _ = Medium.objects.get_or_create(
                code=hint.medium_code,
                defaults={'name': hint.medium_code.title()}
            )
        else:
            # Determine medium from the subject if not provided
            medium_code = self._determine_medium_from_subject(hint)
            if medium_code:
                medium, _ = Medium.objects.get_or_create(
                    code=medium_code,
                    defaults={'name': medium_code.title()}
                )
        
        # Get or create enhanced touchpoint class
        touchpoint_class_code = self._get_enhanced_touchpoint_class_code(hint)
        touchpoint_class_name = self._get_enhanced_touchpoint_class_name(touchpoint_class_code)
        
        touchpoint_class, _ = TouchpointType.objects.get_or_create(
            code=touchpoint_class_code,
            defaults={
                'name': touchpoint_class_name,
                'description': f"Enhanced web touchpoint class: {touchpoint_class_name}"
            }
        )
        
        # Create or get touchpoint
        touchpoint_code = hint.code or f"web.generic"
        touchpoint_name = hint.label or hint.code or 'Web Interaction'
        
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': touchpoint_name,
                'touchpoint_type': touchpoint_class,
                'channel': channel,
                'medium': medium,
                'description': f"Web touchpoint for {touchpoint_code}",
                'is_active': True
            }
        )
        
        return touchpoint
    
    def _determine_channel_from_subject(self, hint: TouchpointHint) -> str:
        """
        Determine the channel (WHERE the interaction happened) from the hint.
        
        Channel represents the location/context where the interaction occurred,
        not just the traffic source. For web interactions, this is typically
        the website domain where the interaction took place.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            str: The channel code
        """
        # Check UTM source first (highest precedence)
        if hint.metadata and 'utm_source' in hint.metadata:
            utm_source = hint.metadata['utm_source']
            if utm_source:
                return utm_source.lower()
        
        # Check if there's a website URL in metadata (where the interaction happened)
        if hint.metadata and 'website_url' in hint.metadata:
            website_url = hint.metadata['website_url']
            if website_url:
                # Extract domain from website URL
                from urllib.parse import urlparse
                parsed = urlparse(website_url)
                domain = parsed.netloc
                if domain:
                    # Normalize domain
                    return domain.replace('www.', '').lower()
        
        # Check if there's a current URL in metadata
        if hint.metadata and 'current_url' in hint.metadata:
            current_url = hint.metadata['current_url']
            if current_url:
                from urllib.parse import urlparse
                parsed = urlparse(current_url)
                domain = parsed.netloc
                if domain:
                    return domain.replace('www.', '').lower()
        
        # Check if there's a page URL in metadata
        if hint.metadata and 'page_url' in hint.metadata:
            page_url = hint.metadata['page_url']
            if page_url:
                from urllib.parse import urlparse
                parsed = urlparse(page_url)
                domain = parsed.netloc
                if domain:
                    return domain.replace('www.', '').lower()
        
        # Check if there's a referrer URL in metadata (for referrer click interactions)
        if hint.metadata and 'referrer_url' in hint.metadata:
            referrer_url = hint.metadata['referrer_url']
            if referrer_url:
                from urllib.parse import urlparse
                parsed = urlparse(referrer_url)
                domain = parsed.netloc
                if domain:
                    return domain.replace('www.', '').lower()
        
        # Default to web channel for web interactions
        return 'web'
    
    def _determine_medium_from_subject(self, hint: TouchpointHint) -> str:
        """
        Determine the medium (HOW it communicates) from the hint.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            str: The medium code
        """
        # Check UTM medium first
        if hint.metadata and 'utm_medium' in hint.metadata:
            utm_medium = hint.metadata['utm_medium']
            if utm_medium:
                return utm_medium.lower()
        
        # Check if this is a page view on our own website
        if hint.metadata and 'website_url' in hint.metadata:
            website_url = hint.metadata['website_url']
            if website_url:
                # This is a page view on our own website
                return 'owned_website'
        
        # Check referrer for medium inference
        if hint.metadata and 'referrer_url' in hint.metadata:
            referrer_url = hint.metadata['referrer_url']
            if referrer_url:
                from urllib.parse import urlparse
                parsed = urlparse(referrer_url)
                domain = parsed.netloc.lower()
                
                # Map common domains to mediums
                if 'google' in domain:
                    return 'organic_search'
                elif any(social in domain for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
                    return 'social_media'
                elif 'mail' in domain or 'email' in domain:
                    return 'email'
            else:
                    return 'referral'
        
        # Default to direct
        return 'direct'
    
    def _get_enhanced_touchpoint_class_code(self, hint: TouchpointHint) -> str:
        """
        Get touchpoint type code based on the functional type of interaction.
        
        In the new three-dimensional system:
        - Channel: WHERE the interaction happened (esan.edu.pe, alpha.com, mobile_app)
        - Medium: HOW it communicates (social, organic, paid, email)
        - TouchpointType: WHAT type of touchpoint (web_page, web_form, link, button)
        
        This method determines the functional type, not the traffic source.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            str: The touchpoint type code
        """
        # Determine the functional type of interaction (TouchpointType)
        # This is about WHAT type of touchpoint, not WHERE it came from or HOW
        
        # Check event type from hint
        event_type = hint.metadata.get('event_type', '') if hint.metadata else ''
        code = hint.code or ''
        
        # Check for referrer click interactions
        if 'referrer_click' in event_type.lower() or 'referrer_click' in code.lower():
            # Check if it's a Google search referrer
            if hint.metadata and 'referrer_url' in hint.metadata:
                referrer_url = hint.metadata['referrer_url']
                if 'google' in referrer_url.lower():
                    return 'search_results'
            return 'web_page'  # Default for referrer clicks
        
        # Map to web-specific touchpoint types (avoiding overlap with action field)
        if 'page_view' in event_type.lower() or 'page_view' in code.lower():
            return 'web_page'
        elif 'form_submit' in event_type.lower() or 'form_submit' in code.lower():
            return 'web_form'
        elif 'click' in event_type.lower() or 'click' in code.lower():
            # Determine if it's a link or button based on selector
            if hint.metadata and 'selector' in hint.metadata:
                selector = hint.metadata['selector']
                if 'a' in selector.lower() or 'link' in selector.lower():
                    return 'link'
                elif 'button' in selector.lower() or 'btn' in selector.lower():
                    return 'button'
            return 'link'  # Default to link for clicks
        elif 'download' in event_type.lower() or 'download' in code.lower():
            return 'web_download'
        elif 'purchase' in event_type.lower() or 'purchase' in code.lower():
            return 'web_purchase'
        elif 'signup' in event_type.lower() or 'signup' in code.lower():
            return 'web_signup'
        elif 'login' in event_type.lower() or 'login' in code.lower():
            return 'web_login'
        elif 'session_start' in event_type.lower() or 'session_start' in code.lower():
            return 'web_session_start'
        elif 'session_end' in event_type.lower() or 'session_end' in code.lower():
            return 'web_session_end'
        else:
            # Default to web_page for web interactions
            return 'web_page'
    
    def _is_internal_website_interaction(self, hint: TouchpointHint) -> bool:
        """
        Determine if this is an internal website interaction (non-click) vs internal click.
        
        This method distinguishes between:
        - Internal clicks → should be "traffic" (return False)
        - Internal non-click events → should be "interaction" (return True)
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            bool: True if internal website interaction (non-click), False if internal click
        """
        # Check if this is an internal click event (should be traffic, not interaction)
        if hint.code:
            if 'internal_click' in hint.code or 'click' in hint.code:
                return False  # Internal clicks are traffic, not interaction
        
        # Check metadata for click event indicators
        if hint.metadata:
            event_type = hint.metadata.get('event_type', '')
            if event_type in ['internal_click', 'click', 'navigation', 'menu_click', 'button_click']:
                return False  # All clicks are traffic, not interaction
            
            # Check for internal interaction indicators (non-click events)
            if hint.metadata.get('is_internal_interaction', False):
                return True
        
        # Check if channel code matches a website domain (internal interaction)
        if hint.channel_code:
            # If channel is a website domain, it's likely an internal interaction
            if '.' in hint.channel_code and not hint.channel_code in ['web_direct', 'unknown']:
                # This is a website domain, likely internal interaction
                return True
        
        # Default to false (true direct traffic)
        return False
    
    def _is_internal_click_event(self, hint: TouchpointHint) -> bool:
        """
        Determine if this is an internal click event (within same website) or external click.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            bool: True if internal click, False if external click
        """
        # Check if there's a target URL in the hint metadata
        if hint.metadata:
            target_url = hint.metadata.get('target_url')
            if target_url:
                # If target URL is provided, check if it's internal or external
                return self._is_internal_url(target_url, hint)
        
        # Check if there's a target URL in the hint payload
        if hasattr(hint, 'payload') and hint.payload:
            target_url = hint.payload.get('target_url')
            if target_url:
                return self._is_internal_url(target_url, hint)
        
        # If no target URL, assume it's an internal click (button, form, etc.)
        return True
    
    def _is_internal_url(self, target_url: str, hint: TouchpointHint) -> bool:
        """
        Check if target URL is internal to the website.
        
        Args:
            target_url: The target URL of the click
            hint: The touchpoint hint
            
        Returns:
            bool: True if internal URL, False if external
        """
        if not target_url:
            return True  # No target URL = internal action
        
        try:
            from urllib.parse import urlparse
            parsed_target = urlparse(target_url)
            target_domain = parsed_target.netloc.lower()
            
            # Get website domain from hint metadata
            website_domain = None
            if hint.metadata:
                website_url = hint.metadata.get('website_url') or hint.metadata.get('website_base')
                if website_url:
                    parsed_website = urlparse(website_url)
                    website_domain = parsed_website.netloc.lower()
            
            if not website_domain:
                return True  # No website domain = assume internal
            
            # Remove www. prefix for comparison
            if target_domain.startswith('www.'):
                target_domain = target_domain[4:]
            if website_domain.startswith('www.'):
                website_domain = website_domain[4:]
            
            # Check if target is internal
            return target_domain == website_domain
            
        except Exception:
            return True  # Assume internal if we can't parse
    
    def _is_click_event(self, hint: TouchpointHint) -> bool:
        """
        Check if this is a click event based on the hint metadata.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            bool: True if click event, False otherwise
        """
        # Check if there's a click indicator in the hint metadata
        if hint.metadata:
            event_type = hint.metadata.get('event_type', '')
            if 'click' in event_type.lower():
                return True
        
        # Check if there's a click indicator in the hint payload
        if hasattr(hint, 'payload') and hint.payload:
            interaction_type = hint.payload.get('interaction_type', '')
            if 'click' in interaction_type.lower():
                return True
        
        # Check if the hint code indicates a click event
        if hint.code and 'click' in hint.code.lower():
            return True
        
        return False
    
    
    def _get_enhanced_touchpoint_class_name(self, touchpoint_class_code: str) -> str:
        """
        Get human-friendly name for medium-based touchpoint class.
        
        Args:
            touchpoint_class_code: The touchpoint class code
            
        Returns:
            str: Human-friendly touchpoint class name
        """
        # Medium-based touchpoint class names
        medium_names = {
            'web.social_traffic': 'Social Media Traffic',
            'web.organic_traffic': 'Organic Search Traffic',
            'web.paid_traffic': 'Paid Advertising Traffic',
            'web.email_traffic': 'Email/Newsletter Traffic',
            'web.referral_traffic': 'Referral Traffic',
            'web.direct_traffic': 'Direct Traffic',
            'web.internal_traffic': 'Internal Website Traffic',
            'web.internal_interaction': 'Internal Website Interaction',
            'web.internal_click': 'Internal Click',
            'web.mobile_traffic': 'Mobile Traffic',
            'web.app_traffic': 'Mobile App Traffic',
            'web.display_traffic': 'Display Advertising Traffic',
            'web.video_traffic': 'Video Advertising Traffic',
            'web.affiliate_traffic': 'Affiliate Traffic',
            'web.content_traffic': 'Content Marketing Traffic',
            'web.unknown_traffic': 'Unknown Traffic Source'
        }
        
        return medium_names.get(touchpoint_class_code, f"Web Traffic - {touchpoint_class_code.split('.')[-1].title()}")


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
