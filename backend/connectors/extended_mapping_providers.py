"""
Extended mapping providers for multi-interaction touchpoint resolution.

This module provides extended mapping providers to support the websites app's
multi-interaction approach, session-aware resolution, and batch processing.
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from django.core.cache import cache

from .protocols import TouchpointInferenceProtocol, TouchpointHint
from .extended_protocols import (
    MultiTouchpointInferenceProtocol, 
    BatchTouchpointHint,
    BatchMappingProviderProtocol
)

if TYPE_CHECKING:
    from .models import TouchpointMappingRule


class ExtendedDatabaseMappingProvider:
    """
    Extended database-backed mapping provider for multi-interaction resolution.
    
    This provider extends the base DatabaseMappingProvider to support
    batch processing, session-aware resolution, and multi-interaction
    mapping rule lookup.
    """
    
    def __init__(self, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the extended database mapping provider.
        
        Args:
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        self.cache_timeout = cache_timeout
        self.use_cache = use_cache
    
    def lookup_batch_mapping(
        self, 
        subject: MultiTouchpointInferenceProtocol, 
        batch_hint: BatchTouchpointHint
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up mapping rules for batch processing.
        
        This method implements batch mapping rule lookup with priority-based resolution:
        1. Session-specific batch rules (highest priority)
        2. Connector-specific batch rules (medium priority)
        3. Generic batch rules (lowest priority)
        
        Args:
            subject: The connector interaction requesting batch touchpoint resolution
            batch_hint: The batch touchpoint hint containing multiple interaction hints
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule for the batch
        """
        if not batch_hint.hints:
            return None
        
        # Get connector type and session context
        connector_type = self._get_connector_type(subject)
        session_id = batch_hint.session_id
        
        # Try session-specific batch rules first (highest priority)
        if session_id:
            rule = self._lookup_session_batch_rule(
                connector_type=connector_type,
                session_id=session_id,
                event_codes=[hint.hint.code for hint in batch_hint.hints if hint.hint.code]
            )
            if rule:
                return rule
        
        # Try connector-specific batch rules (medium priority)
        rule = self._lookup_connector_batch_rule(
            connector_type=connector_type,
            event_codes=[hint.hint.code for hint in batch_hint.hints if hint.hint.code]
        )
        if rule:
            return rule
        
        # Try generic batch rules (lowest priority)
        rule = self._lookup_generic_batch_rule(
            event_codes=[hint.hint.code for hint in batch_hint.hints if hint.hint.code]
        )
        
        return rule
    
    def lookup_session_mapping(
        self,
        subject: MultiTouchpointInferenceProtocol,
        session_context: Dict[str, Any]
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up session-aware mapping rules.
        
        This method supports session-level mapping rule lookup,
        allowing for session-specific touchpoint resolution overrides.
        
        Args:
            subject: The connector interaction requesting session-aware resolution
            session_context: Session-level context for rule lookup
            
        Returns:
            TouchpointMappingRule or None: The applicable session-level mapping rule
        """
        if not session_context:
            return None
        
        # Get connector type and session identifier
        connector_type = self._get_connector_type(subject)
        session_id = session_context.get('session_id')
        
        if not session_id:
            return None
        
        # Try session-specific rules
        rule = self._lookup_session_rule(
            connector_type=connector_type,
            session_id=session_id,
            session_context=session_context
        )
        
        return rule
    
    def _lookup_session_batch_rule(
        self, 
        connector_type: str, 
        session_id: str, 
        event_codes: List[str]
    ) -> Optional['TouchpointMappingRule']:
        """Look up session-specific batch mapping rules."""
        if not event_codes:
            return None
        
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"session_batch_mapping:{connector_type}:{session_id}:{':'.join(event_codes)}"
            cached_rule = cache.get(cache_key)
            if cached_rule is not None:
                return cached_rule
        
        # Import here to avoid circular imports
        from .models import TouchpointMappingRule
        
        # Query for session-specific batch rules
        rule = TouchpointMappingRule.objects.filter(
            connector_type=connector_type,
            source_identifier=f"session:{session_id}",
            event_code__in=event_codes,
            is_active=True
        ).order_by('-priority').first()
        
        # Cache the result if enabled
        if self.use_cache and rule:
            cache.set(cache_key, rule, self.cache_timeout)
        
        return rule
    
    def _lookup_connector_batch_rule(
        self, 
        connector_type: str, 
        event_codes: List[str]
    ) -> Optional['TouchpointMappingRule']:
        """Look up connector-specific batch mapping rules."""
        if not event_codes:
            return None
        
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"connector_batch_mapping:{connector_type}:{':'.join(event_codes)}"
            cached_rule = cache.get(cache_key)
            if cached_rule is not None:
                return cached_rule
        
        # Import here to avoid circular imports
        from .models import TouchpointMappingRule
        
        # Query for connector-specific batch rules
        rule = TouchpointMappingRule.objects.filter(
            connector_type=connector_type,
            source_identifier="",  # Generic connector rule
            event_code__in=event_codes,
            is_active=True
        ).order_by('-priority').first()
        
        # Cache the result if enabled
        if self.use_cache and rule:
            cache.set(cache_key, rule, self.cache_timeout)
        
        return rule
    
    def _lookup_generic_batch_rule(
        self, 
        event_codes: List[str]
    ) -> Optional['TouchpointMappingRule']:
        """Look up generic batch mapping rules."""
        if not event_codes:
            return None
        
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"generic_batch_mapping:{':'.join(event_codes)}"
            cached_rule = cache.get(cache_key)
            if cached_rule is not None:
                return cached_rule
        
        # Import here to avoid circular imports
        from .models import TouchpointMappingRule
        
        # Query for generic batch rules
        rule = TouchpointMappingRule.objects.filter(
            connector_type="",  # Generic rule
            source_identifier="",  # Generic rule
            event_code__in=event_codes,
            is_active=True
        ).order_by('-priority').first()
        
        # Cache the result if enabled
        if self.use_cache and rule:
            cache.set(cache_key, rule, self.cache_timeout)
        
        return rule
    
    def _lookup_session_rule(
        self, 
        connector_type: str, 
        session_id: str, 
        session_context: Dict[str, Any]
    ) -> Optional['TouchpointMappingRule']:
        """Look up session-specific mapping rules."""
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"session_mapping:{connector_type}:{session_id}"
            cached_rule = cache.get(cache_key)
            if cached_rule is not None:
                return cached_rule
        
        # Import here to avoid circular imports
        from .models import TouchpointMappingRule
        
        # Query for session-specific rules
        rule = TouchpointMappingRule.objects.filter(
            connector_type=connector_type,
            source_identifier=f"session:{session_id}",
            is_active=True
        ).order_by('-priority').first()
        
        # Cache the result if enabled
        if self.use_cache and rule:
            cache.set(cache_key, rule, self.cache_timeout)
        
        return rule
    
    def _get_connector_type(self, subject: MultiTouchpointInferenceProtocol) -> str:
        """Extract connector type from subject class name."""
        class_name = subject.__class__.__name__.lower()
        
        if class_name.startswith('web'):
            return 'web'
        elif class_name.startswith('email'):
            return 'email'
        elif class_name.startswith('whatsapp'):
            return 'whatsapp'
        elif class_name.startswith('chat'):
            return 'chat'
        elif class_name.startswith('social'):
            return 'social'
        else:
            return 'generic'


class CachedExtendedMappingProvider(ExtendedDatabaseMappingProvider):
    """
    Enhanced extended mapping provider with advanced caching capabilities.
    
    This provider extends the extended database provider with additional
    caching features including session-aware cache invalidation and
    batch cache warming.
    """
    
    def __init__(self, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached extended mapping provider.
        
        Args:
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        super().__init__(cache_timeout, use_cache)
        self._local_cache = {}
        self._session_cache = {}
    
    def invalidate_session_cache(self, session_id: str = None, connector_type: str = None):
        """
        Invalidate cached mapping rules for specific sessions.
        
        Args:
            session_id: Specific session to invalidate (optional)
            connector_type: Specific connector type to invalidate (optional)
        """
        if session_id and connector_type:
            # Invalidate specific session rule
            cache_key = f"session_mapping:{connector_type}:{session_id}"
            cache.delete(cache_key)
        elif session_id:
            # Invalidate all rules for session
            cache.delete_many(cache.keys(f"session_mapping:*:{session_id}"))
        elif connector_type:
            # Invalidate all session rules for connector type
            cache.delete_many(cache.keys(f"session_mapping:{connector_type}:*"))
        else:
            # Invalidate all session rules
            cache.delete_many(cache.keys("session_mapping:*"))
        
        # Clear local caches
        self._local_cache.clear()
        self._session_cache.clear()
    
    def invalidate_batch_cache(self, connector_type: str = None):
        """
        Invalidate cached batch mapping rules.
        
        Args:
            connector_type: Specific connector type to invalidate (optional)
        """
        if connector_type:
            # Invalidate connector-specific batch rules
            cache.delete_many(cache.keys(f"connector_batch_mapping:{connector_type}:*"))
            cache.delete_many(cache.keys(f"session_batch_mapping:{connector_type}:*"))
        else:
            # Invalidate all batch rules
            cache.delete_many(cache.keys("connector_batch_mapping:*"))
            cache.delete_many(cache.keys("session_batch_mapping:*"))
            cache.delete_many(cache.keys("generic_batch_mapping:*"))
        
        # Clear local caches
        self._local_cache.clear()
        self._session_cache.clear()
    
    def warm_session_cache(self, session_id: str, connector_type: str = None):
        """
        Warm the cache with session-specific mapping rules.
        
        Args:
            session_id: Session identifier to warm cache for
            connector_type: Specific connector type to warm (optional)
        """
        from .models import TouchpointMappingRule
        
        # Build query for session-specific rules
        queryset = TouchpointMappingRule.objects.filter(
            source_identifier=f"session:{session_id}",
            is_active=True
        )
        if connector_type:
            queryset = queryset.filter(connector_type=connector_type)
        
        # Cache all matching rules
        for rule in queryset:
            cache_key = f"session_mapping:{rule.connector_type}:{session_id}"
            cache.set(cache_key, rule, self.cache_timeout)
    
    def warm_batch_cache(self, connector_type: str = None):
        """
        Warm the cache with batch mapping rules.
        
        Args:
            connector_type: Specific connector type to warm (optional)
        """
        from .models import TouchpointMappingRule
        
        # Build query for batch rules
        queryset = TouchpointMappingRule.objects.filter(
            is_active=True
        )
        if connector_type:
            queryset = queryset.filter(connector_type=connector_type)
        
        # Cache all matching rules
        for rule in queryset:
            if rule.source_identifier.startswith("session:"):
                # Session-specific batch rule
                session_id = rule.source_identifier.replace("session:", "")
                cache_key = f"session_batch_mapping:{rule.connector_type}:{session_id}:{rule.event_code}"
            elif rule.connector_type and not rule.source_identifier:
                # Connector-specific batch rule
                cache_key = f"connector_batch_mapping:{rule.connector_type}:{rule.event_code}"
            else:
                # Generic batch rule
                cache_key = f"generic_batch_mapping:{rule.event_code}"
            
            cache.set(cache_key, rule, self.cache_timeout)
