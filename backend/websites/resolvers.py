"""
Web-specific touchpoint resolution.

This module provides web-specific touchpoint resolvers that understand
UTM parameters, referrer analysis, and web-specific touchpoint logic.
"""

from urllib.parse import urlparse
from typing import Optional

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
        Ensure web-specific required fields.
        
        This method provides web-specific defaults and analyzes UTM parameters
        to determine the appropriate channel and medium codes.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            hint: The touchpoint hint from the connector's inference
            
        Returns:
            TouchpointHint: The hint with web-specific required fields ensured
        """
        # Ensure web channel if not specified
        if not hint.channel_code:
            hint = TouchpointHint(
                code=hint.code,
                channel_code='web',
                medium_code=hint.medium_code or 'unknown',
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Analyze UTM parameters if available
        if hasattr(subject, 'utm_medium') and subject.utm_medium:
            medium = self._analyze_utm_medium(subject.utm_medium)
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code=medium,
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Analyze referrer if available and no UTM medium
        elif hasattr(subject, 'referrer_url') and subject.referrer_url and not hint.medium_code:
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
        # Get or create web channel
        channel = None
        if hint.channel_code:
            channel, _ = Channel.objects.get_or_create(
                code=hint.channel_code,
                defaults={'name': 'Web Channel'}
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
