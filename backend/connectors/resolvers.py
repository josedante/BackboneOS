"""
Generic touchpoint resolution framework.

This module provides the core touchpoint resolution logic that works with any
connector type. It implements the strategy pattern where specialized logic
is delegated to connector-specific adapters while maintaining a consistent
interface for all connector types.
"""

from django.db import transaction
from typing import Optional, TYPE_CHECKING

from interactions.models import Touchpoint, TouchpointType, Channel, Medium
from .protocols import TouchpointInferenceProtocol, TouchpointResolverProtocol, TouchpointHint
from .metrics import track_resolution

if TYPE_CHECKING:
    from .models import TouchpointMappingRule


class DefaultTouchpointResolver:
    """
    Generic touchpoint resolver that works with any connector type.
    
    This resolver implements the core touchpoint resolution strategy:
    1. Get hint from connector-specific inference
    2. Apply configurable mapping overrides
    3. Fallback to connector-specific defaults
    4. Create or get touchpoint with proper relationships
    
    The resolver delegates specialized logic to connector-specific adapters
    while providing a consistent interface for all connector types.
    """
    
    def __init__(self, mapping_provider: 'MappingProviderProtocol'):
        """
        Initialize the resolver with a mapping provider.
        
        Args:
            mapping_provider: Provider for looking up mapping rules
        """
        self.mapping_provider = mapping_provider
    
    @transaction.atomic
    def resolve(self, subject: TouchpointInferenceProtocol) -> Touchpoint:
        """
        Resolve touchpoint for any connector type.
        
        This method implements the core resolution strategy:
        1. Get hint from connector-specific inference
        2. Apply configurable mapping overrides
        3. Fallback to connector-specific defaults
        4. Create or get touchpoint
        
        Args:
            subject: A connector interaction that implements TouchpointInferenceProtocol
            
        Returns:
            Touchpoint: The resolved touchpoint object
        """
        # Get connector type for metrics
        connector_type = self._get_connector_type(subject)
        
        # Track resolution with metrics
        with track_resolution(connector_type, {'subject_class': subject.__class__.__name__}) as tracker:
            try:
                # Step 1: Get hint from connector-specific inference
                hint = subject.infer_touchpoint_hint()
                
                # Step 2: Apply mapping overrides
                mapping_rule = self.mapping_provider.lookup_mapping(subject, hint)
                mapping_applied = mapping_rule is not None
                if mapping_rule:
                    hint = self._apply_mapping_rule(hint, mapping_rule)
                
                # Step 3: Ensure we have required fields
                final_hint = self._ensure_required_fields(subject, hint)
                
                # Step 4: Create or get touchpoint
                touchpoint = self._get_or_create_touchpoint(final_hint)
                
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
    
    def _ensure_required_fields(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> TouchpointHint:
        """
        Ensure hint has required fields, using connector-specific defaults.
        
        This method can be overridden by connector-specific resolvers to provide
        specialized defaults for their connector type.
        
        Args:
            subject: The connector interaction
            hint: The touchpoint hint to validate
            
        Returns:
            TouchpointHint: The hint with required fields ensured
        """
        # Default implementation - connector-specific resolvers should override
        return hint
    
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
                    'name': hint.channel_code.title(),
                    'description': f"Auto-generated channel for {hint.channel_code}",
                    'source_type': 'external'  # Default source type
                }
            )
        
        # Get or create medium
        medium = None
        if hint.medium_code:
            medium, _ = Medium.objects.get_or_create(
                code=hint.medium_code,
                defaults={
                    'name': hint.medium_code.title(),
                    'description': f"Auto-generated medium for {hint.medium_code}",
                    'communication_type': 'asynchronous'  # Default communication type
                }
            )
        
        # Get or create touchpoint type
        touchpoint_type = None
        if hint.touchpoint_type_code:
            touchpoint_type, _ = TouchpointType.objects.get_or_create(
                code=hint.touchpoint_type_code,
                defaults={
                    'name': hint.touchpoint_type_code.title(),
                    'description': f"Auto-generated touchpoint type for {hint.touchpoint_type_code}"
                }
            )
        
        # Create or get touchpoint
        touchpoint_code = hint.code or f"generic.{hint.channel_code or 'unknown'}"
        touchpoint_name = hint.label or hint.code or 'Generic Touchpoint'
        
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': touchpoint_name,
                'channel': channel,
                'medium': medium,
                'touchpoint_type': touchpoint_type,
                'description': f"Auto-generated touchpoint for {touchpoint_code}",
                'is_active': True
            }
        )
        
        return touchpoint
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """Extract connector type from subject class name."""
        class_name = subject.__class__.__name__.lower()
        if class_name.startswith('web'):
            return 'web'
        elif class_name.startswith('email'):
            return 'email'
        elif class_name.startswith('whatsapp'):
            return 'whatsapp'
        return 'generic'


class CachedTouchpointResolver(DefaultTouchpointResolver):
    """
    Cached version of the touchpoint resolver for improved performance.
    
    This resolver adds caching to the touchpoint resolution process to avoid
    repeated database queries for the same touchpoint codes.
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
        self._channel_cache = {}
        self._medium_cache = {}
        self._touchpoint_type_cache = {}
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """
        Create or get touchpoint with caching.
        
        Args:
            hint: The touchpoint hint containing all necessary information
            
        Returns:
            Touchpoint: The created or existing touchpoint
        """
        # Check cache first
        touchpoint_code = hint.code or f"generic.{hint.channel_code or 'unknown'}"
        if touchpoint_code in self._touchpoint_cache:
            return self._touchpoint_cache[touchpoint_code]
        
        # Create/get touchpoint using parent implementation
        touchpoint = super()._get_or_create_touchpoint(hint)
        
        # Cache the result
        self._touchpoint_cache[touchpoint_code] = touchpoint
        
        return touchpoint
