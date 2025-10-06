"""
Generic touchpoint resolution framework.

This module provides the core touchpoint resolution logic that works with any
connector type. It uses a subject-agnostic approach where touchpoint hints
are provided directly, without requiring a connector interaction object.
"""

from django.db import transaction
from typing import Optional, TYPE_CHECKING

from interactions.models import Touchpoint, TouchpointType, Channel, Medium
from .protocols import TouchpointHint
from .metrics import track_resolution

if TYPE_CHECKING:
    from .models import TouchpointMappingRule


class DefaultTouchpointResolver:
    """
    Generic touchpoint resolver using subject-agnostic approach.
    
    This resolver implements the core touchpoint resolution strategy:
    1. Accept a TouchpointHint with explicit parameters
    2. Apply configurable mapping overrides
    3. Create or get touchpoint with proper three-dimensional classification
    
    The resolver works directly with hints and explicit parameters,
    eliminating the need for connector interaction objects.
    """
    
    def __init__(self, mapping_provider: 'MappingProviderProtocol'):
        """
        Initialize the resolver with a mapping provider.
        
        Args:
            mapping_provider: Provider for looking up mapping rules
        """
        self.mapping_provider = mapping_provider
    
    @transaction.atomic
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        """
        Resolve touchpoint from a hint with explicit parameters.
        
        This method implements the core resolution strategy:
        1. Accept TouchpointHint and explicit parameters
        2. Apply configurable mapping overrides
        3. Create or get touchpoint with three-dimensional classification
        
        Args:
            hint: TouchpointHint containing touchpoint information
            connector_type: Type of connector (e.g., 'web', 'email', 'whatsapp')
            source_identifier: Source identifier (e.g., website URL, email domain)
            
        Returns:
            Touchpoint: The resolved touchpoint object
        """
        # Track resolution with metrics
        with track_resolution(connector_type, {'hint_code': hint.code}) as tracker:
            try:
                # Step 1: Apply mapping overrides
                mapping_rule = self.mapping_provider.lookup_mapping(
                    connector_type=connector_type,
                    source_identifier=source_identifier,
                    hint=hint
                )
                mapping_applied = mapping_rule is not None
                if mapping_rule:
                    hint = self._apply_mapping_rule(hint, mapping_rule)
                
                # Step 2: Create or get touchpoint with taxonomy
                touchpoint = self._get_or_create_touchpoint(hint)
                
                # Record successful resolution
                tracker.record_success(
                    cache_hit=False,  # TODO: Implement cache hit detection
                    mapping_applied=mapping_applied,
                    touchpoint_created=True
                )
                
                return touchpoint
                
            except Exception as e:
                # Record error
                tracker.record_error(str(e))
                raise
    
    def _apply_mapping_rule(self, hint: TouchpointHint, rule: 'TouchpointMappingRule') -> TouchpointHint:
        """
        Apply mapping rule overrides to hint.
        
        Args:
            hint: The original touchpoint hint
            rule: The mapping rule to apply
            
        Returns:
            TouchpointHint: The modified hint with rule overrides applied
        """
        return TouchpointHint(
            code=rule.touchpoint_code or hint.code,
            channel_code=rule.channel_code or hint.channel_code,
            medium_code=rule.medium_code or hint.medium_code,
            touchpoint_type_code=rule.touchpoint_type_code or hint.touchpoint_type_code,
            label=rule.touchpoint_label or hint.label,
            metadata={**hint.metadata, **rule.metadata}
        )
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """
        Create or get touchpoint from hint with three-dimensional classification.
        
        This method handles the creation of Touchpoint, Channel, Medium, and TouchpointType
        objects based on the provided hint.
        
        Args:
            hint: The touchpoint hint containing all necessary information
            
        Returns:
            Touchpoint: The created or existing touchpoint
        """
        # Get or create channel
        channel = None
        if hint.channel_code:
            channel, _ = Channel.objects.get_or_create(
                code=hint.channel_code,
                defaults={
                    'name': self._format_code_as_name(hint.channel_code),
                    'description': f"Auto-generated channel for {hint.channel_code}",
                    'source_type': 'external'
                }
            )
        
        # Get or create medium
        medium = None
        if hint.medium_code:
            medium, _ = Medium.objects.get_or_create(
                code=hint.medium_code,
                defaults={
                    'name': self._format_code_as_name(hint.medium_code),
                    'description': f"Auto-generated medium for {hint.medium_code}",
                    'communication_type': 'asynchronous'
                }
            )
        
        # Get or create touchpoint type
        touchpoint_type = None
        if hint.touchpoint_type_code:
            touchpoint_type, _ = TouchpointType.objects.get_or_create(
                code=hint.touchpoint_type_code,
                defaults={
                    'name': self._format_code_as_name(hint.touchpoint_type_code),
                    'description': f"Auto-generated touchpoint type for {hint.touchpoint_type_code}"
                }
            )
        
        # Handle hierarchical touchpoints: create parent if specified
        parent_touchpoint = None
        if hint.parent_code:
            # Create parent touchpoint (same taxonomy, but without parent)
            parent_name = f"{self._format_code_as_name(hint.channel_code or '')} - {self._format_code_as_name(hint.medium_code or '')}"
            parent_touchpoint, _ = Touchpoint.objects.get_or_create(
                code=hint.parent_code,
                defaults={
                    'name': parent_name,
                    'channel': channel,
                    'medium': medium,
                    'touchpoint_type': touchpoint_type,
                    'parent': None,  # Parent has no parent
                    'description': f"Parent touchpoint for rollup analytics: {hint.parent_code}",
                    'is_active': True
                }
            )
        
        # Create or get child touchpoint (or standalone if no parent)
        touchpoint_code = hint.code or f"generic.{hint.channel_code or 'unknown'}"
        touchpoint_name = hint.label or hint.code or 'Generic Touchpoint'
        
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            url=hint.url or '',
            defaults={
                'name': touchpoint_name,
                'channel': channel,
                'medium': medium,
                'touchpoint_type': touchpoint_type,
                'parent': parent_touchpoint,  # Link to parent if exists
                'description': f"Auto-generated touchpoint for {touchpoint_code}",
                'is_active': True
            }
        )
        
        return touchpoint
    
    def _format_code_as_name(self, code: str) -> str:
        """
        Format a code string into a human-readable name.
        
        Handles various code formats:
        - snake_case: 'organic_search' → 'Organic Search'
        - SCREAMING_SNAKE: 'GOOGLE_COM' → 'Google Com'
        - kebab-case: 'paid-search' → 'Paid Search'
        
        Args:
            code: The code string to format
            
        Returns:
            str: Formatted human-readable name
        """
        if not code:
            return ''
        
        # Replace underscores and hyphens with spaces
        formatted = code.replace('_', ' ').replace('-', ' ')
        
        # Title case each word
        formatted = ' '.join(word.capitalize() for word in formatted.split())
        
        return formatted


class CachedTouchpointResolver(DefaultTouchpointResolver):
    """
    Cached version of the touchpoint resolver for improved performance.
    
    This resolver adds in-memory caching to the touchpoint resolution process
    to avoid repeated database queries for the same touchpoint codes.
    """
    
    def __init__(self, mapping_provider: 'MappingProviderProtocol', cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached resolver.
        
        Args:
            mapping_provider: Provider for looking up mapping rules
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        super().__init__(mapping_provider)
        self.cache_timeout = cache_timeout
        self.use_cache = use_cache
        self._touchpoint_cache = {}
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """
        Create or get touchpoint with in-memory caching.
        
        Args:
            hint: The touchpoint hint containing all necessary information
            
        Returns:
            Touchpoint: The created or existing touchpoint
        """
        if not self.use_cache:
            return super()._get_or_create_touchpoint(hint)
        
        # Check cache first
        touchpoint_code = hint.code or f"generic.{hint.channel_code or 'unknown'}"
        if touchpoint_code in self._touchpoint_cache:
            return self._touchpoint_cache[touchpoint_code]
        
        # Create/get touchpoint using parent implementation
        touchpoint = super()._get_or_create_touchpoint(hint)
        
        # Cache the result
        self._touchpoint_cache[touchpoint_code] = touchpoint
        
        return touchpoint
