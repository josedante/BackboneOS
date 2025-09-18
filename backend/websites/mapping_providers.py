"""
Web-specific mapping providers for touchpoint resolution.

This module provides web-specific mapping providers that understand
website URLs, UTM parameters, and web-specific source identification.
"""

from urllib.parse import urlparse
from typing import Optional

from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointInferenceProtocol


class WebMappingProvider(DatabaseMappingProvider):
    """
    Web-specific mapping provider that understands website URLs and UTM parameters.
    
    This provider extends the generic DatabaseMappingProvider with web-specific
    logic for extracting source identifiers from web interactions and understanding
    website-specific mapping rules.
    """
    
    def _get_source_identifier(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Extract website URL as source identifier.
        
        This method looks for website-related information in the subject
        to determine the source identifier for mapping rule lookup.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            
        Returns:
            str: The source identifier (website URL or domain)
        """
        # Try to get website URL from the subject
        if hasattr(subject, 'website') and subject.website:
            return subject.website.base_url
        
        # Try to get URL from payload or metadata
        if hasattr(subject, 'payload') and subject.payload:
            url = subject.payload.get('url') or subject.payload.get('page_url')
            if url:
                return url
        
        # Try to get URL from metadata
        if hasattr(subject, 'metadata') and subject.metadata:
            url = subject.metadata.get('url') or subject.metadata.get('page_url')
            if url:
                return url
        
        # Try to get referrer URL as source identifier
        if hasattr(subject, 'referrer_url') and subject.referrer_url:
            return subject.referrer_url
        
        # Try to get current URL from session or other fields
        if hasattr(subject, 'current_url') and subject.current_url:
            return subject.current_url
        
        return ''
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Extract connector type from subject class name.
        
        Args:
            subject: The web interaction
            
        Returns:
            str: The connector type identifier
        """
        class_name = subject.__class__.__name__.lower()
        
        # Map class names to connector types
        if class_name.startswith('web'):
            return 'web'
        elif class_name.startswith('page'):
            return 'web'
        elif class_name.startswith('form'):
            return 'web'
        elif class_name.startswith('click'):
            return 'web'
        else:
            return 'web'  # Default to web for web interactions
    
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL for more flexible matching.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            str: The domain part of the URL
        """
        if not url:
            return ''
        
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ''
    
    def _normalize_source_identifier(self, source_identifier: str) -> str:
        """
        Normalize source identifier for consistent matching.
        
        This method normalizes URLs and domains to ensure consistent
        matching in mapping rules.
        
        Args:
            source_identifier: The source identifier to normalize
            
        Returns:
            str: The normalized source identifier
        """
        if not source_identifier:
            return ''
        
        # If it's a URL, extract the domain
        if source_identifier.startswith(('http://', 'https://')):
            domain = self._extract_domain_from_url(source_identifier)
            if domain:
                return domain
        
        # If it's already a domain, normalize it
        if '.' in source_identifier and not source_identifier.startswith('/'):
            return source_identifier.lower().strip()
        
        # Return as-is for other cases
        return source_identifier.lower().strip()
    
    def lookup_mapping(self, subject: TouchpointInferenceProtocol, hint) -> Optional:
        """
        Look up mapping rule with web-specific source identifier normalization.
        
        This method extends the base lookup with web-specific source identifier
        normalization and domain extraction.
        
        Args:
            subject: The web interaction requesting touchpoint resolution
            hint: The touchpoint hint from the connector's inference
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule, if any
        """
        if not hint.code:
            return None
        
        # Get connector type and source identifier
        connector_type = self._get_connector_type(subject)
        source_identifier = self._get_source_identifier(subject)
        
        # Normalize source identifier
        normalized_source = self._normalize_source_identifier(source_identifier)
        
        # Try specific source first (highest priority)
        if normalized_source:
            rule = self._lookup_rule(
                connector_type=connector_type,
                source_identifier=normalized_source,
                event_code=hint.code
            )
            if rule:
                return rule
        
        # Try original source identifier if different from normalized
        if source_identifier and source_identifier != normalized_source:
            rule = self._lookup_rule(
                connector_type=connector_type,
                source_identifier=source_identifier,
                event_code=hint.code
            )
            if rule:
                return rule
        
        # Try generic connector type (medium priority)
        rule = self._lookup_rule(
            connector_type=connector_type,
            source_identifier='',
            event_code=hint.code
        )
        if rule:
            return rule
        
        # Try generic event code (lowest priority)
        rule = self._lookup_rule(
            connector_type='',
            source_identifier='',
            event_code=hint.code
        )
        
        return rule


class CachedWebMappingProvider(WebMappingProvider):
    """
    Cached version of the web mapping provider for improved performance.
    
    This provider extends the WebMappingProvider with additional caching
    for source identifier normalization and domain extraction.
    """
    
    def __init__(self, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached web mapping provider.
        
        Args:
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        super().__init__(cache_timeout, use_cache)
        self._source_normalization_cache = {}
        self._domain_extraction_cache = {}
    
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL with caching.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            str: The domain part of the URL
        """
        if not self.use_cache:
            return super()._extract_domain_from_url(url)
        
        if url in self._domain_extraction_cache:
            return self._domain_extraction_cache[url]
        
        result = super()._extract_domain_from_url(url)
        self._domain_extraction_cache[url] = result
        
        return result
    
    def _normalize_source_identifier(self, source_identifier: str) -> str:
        """
        Normalize source identifier with caching.
        
        Args:
            source_identifier: The source identifier to normalize
            
        Returns:
            str: The normalized source identifier
        """
        if not self.use_cache:
            return super()._normalize_source_identifier(source_identifier)
        
        if source_identifier in self._source_normalization_cache:
            return self._source_normalization_cache[source_identifier]
        
        result = super()._normalize_source_identifier(source_identifier)
        self._source_normalization_cache[source_identifier] = result
        
        return result
    
    def invalidate_cache(self, connector_type: str = None, source_identifier: str = None):
        """
        Invalidate cached mapping rules and web-specific caches.
        
        Args:
            connector_type: Specific connector type to invalidate (optional)
            source_identifier: Specific source identifier to invalidate (optional)
        """
        # Invalidate parent caches
        super().invalidate_cache(connector_type, source_identifier)
        
        # Invalidate web-specific caches
        if source_identifier:
            # Invalidate specific source normalization cache
            if source_identifier in self._source_normalization_cache:
                del self._source_normalization_cache[source_identifier]
            
            # Invalidate domain extraction cache
            if source_identifier in self._domain_extraction_cache:
                del self._domain_extraction_cache[source_identifier]
        else:
            # Clear all web-specific caches
            self._source_normalization_cache.clear()
            self._domain_extraction_cache.clear()
