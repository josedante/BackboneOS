"""
Extended resolvers for multi-interaction touchpoint resolution.

This module provides extended touchpoint resolution capabilities to support
the websites app's multi-interaction approach, session-aware resolution,
and batch processing requirements.
"""

from django.db import transaction
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from interactions.models import Touchpoint, TouchpointType, Channel, Medium
from .protocols import TouchpointHint
from .extended_protocols import (
    MultiTouchpointInferenceProtocol, 
    BatchTouchpointHint, 
    MultiTouchpointHint,
    SessionAwareTouchpointResolverProtocol,
    BatchMappingProviderProtocol
)
from .metrics import track_resolution

if TYPE_CHECKING:
    from .models import TouchpointMappingRule


class ExtendedTouchpointResolver:
    """
    Extended touchpoint resolver supporting multi-interaction approach.
    
    This resolver extends the base DefaultTouchpointResolver to support
    the websites app's multi-interaction approach, session-aware resolution,
    and batch processing capabilities.
    """
    
    def __init__(self, mapping_provider: 'BatchMappingProviderProtocol'):
        """
        Initialize the extended resolver with a batch mapping provider.
        
        Args:
            mapping_provider: Provider for looking up batch mapping rules
        """
        self.mapping_provider = mapping_provider
    
    @transaction.atomic
    def resolve_batch(self, subject: MultiTouchpointInferenceProtocol) -> List[Touchpoint]:
        """
        Resolve multiple touchpoints for a batch of interactions.
        
        This method implements the multi-interaction resolution strategy:
        1. Get batch hint from connector-specific inference
        2. Apply batch mapping overrides
        3. Resolve each interaction with session context
        4. Create or get touchpoints with proper relationships
        
        Args:
            subject: A connector interaction that implements MultiTouchpointInferenceProtocol
            
        Returns:
            List[Touchpoint]: Multiple resolved touchpoint objects
        """
        # Get connector type for metrics
        connector_type = self._get_connector_type(subject)
        
        # Track batch resolution with metrics
        with track_resolution(connector_type, {'subject_class': subject.__class__.__name__, 'batch': True}) as tracker:
            try:
                # Step 1: Get batch hint from connector-specific inference
                batch_hint = subject.infer_multi_touchpoint_hints()
                
                # Step 2: Apply batch mapping overrides
                batch_mapping_rule = self.mapping_provider.lookup_batch_mapping(subject, batch_hint)
                mapping_applied = batch_mapping_rule is not None
                if batch_mapping_rule:
                    batch_hint = self._apply_batch_mapping_rule(batch_hint, batch_mapping_rule)
                
                # Step 3: Resolve each interaction with session context
                touchpoints = []
                for multi_hint in batch_hint.hints:
                    touchpoint = self._resolve_single_with_session_context(
                        multi_hint, 
                        batch_hint.session_id,
                        batch_hint.coordination_metadata
                    )
                    touchpoints.append(touchpoint)
                
                # Record successful batch resolution
                tracker.record_success(
                    cache_hit=False,  # TODO: Implement cache hit detection
                    mapping_applied=mapping_applied,
                    touchpoint_created=True,
                    batch_size=len(touchpoints)
                )
                
                return touchpoints
                
            except Exception as e:
                # Record error
                tracker.record_error(str(e))
                raise
    
    def resolve_with_session_context(
        self, 
        subject: MultiTouchpointInferenceProtocol,
        session_context: Dict[str, Any]
    ) -> List[Touchpoint]:
        """
        Resolve touchpoints with session context.
        
        This method allows for session-aware touchpoint resolution,
        where the session context influences the resolution of individual interactions.
        
        Args:
            subject: A connector interaction that implements MultiTouchpointInferenceProtocol
            session_context: Session-level context for coordinated resolution
            
        Returns:
            List[Touchpoint]: Multiple resolved touchpoint objects with session context
        """
        # Get connector type for metrics
        connector_type = self._get_connector_type(subject)
        
        # Track session-aware resolution with metrics
        with track_resolution(connector_type, {'subject_class': subject.__class__.__name__, 'session_aware': True}) as tracker:
            try:
                # Step 1: Get batch hint from connector-specific inference
                batch_hint = subject.infer_multi_touchpoint_hints()
                
                # Step 2: Apply session-aware mapping overrides
                session_mapping_rule = self.mapping_provider.lookup_session_mapping(subject, session_context)
                mapping_applied = session_mapping_rule is not None
                if session_mapping_rule:
                    batch_hint = self._apply_session_mapping_rule(batch_hint, session_mapping_rule, session_context)
                
                # Step 3: Resolve each interaction with enhanced session context
                touchpoints = []
                for multi_hint in batch_hint.hints:
                    # Merge session context with interaction-specific context
                    enhanced_context = {**session_context, **multi_hint.session_context}
                    touchpoint = self._resolve_single_with_session_context(
                        multi_hint,
                        batch_hint.session_id,
                        enhanced_context
                    )
                    touchpoints.append(touchpoint)
                
                # Record successful session-aware resolution
                tracker.record_success(
                    cache_hit=False,  # TODO: Implement cache hit detection
                    mapping_applied=mapping_applied,
                    touchpoint_created=True,
                    session_aware=True,
                    batch_size=len(touchpoints)
                )
                
                return touchpoints
                
            except Exception as e:
                # Record error
                tracker.record_error(str(e))
                raise
    
    def _apply_batch_mapping_rule(
        self, 
        batch_hint: BatchTouchpointHint, 
        rule: 'TouchpointMappingRule'
    ) -> BatchTouchpointHint:
        """
        Apply batch mapping rule overrides to batch hint.
        
        Args:
            batch_hint: The original batch touchpoint hint
            rule: The batch mapping rule to apply
            
        Returns:
            BatchTouchpointHint: The modified batch hint with rule overrides applied
        """
        # Apply rule overrides to each interaction hint
        modified_hints = []
        for multi_hint in batch_hint.hints:
            modified_hint = MultiTouchpointHint(
                interaction_type=multi_hint.interaction_type,
                hint=TouchpointHint(
                    code=rule.touchpoint_code or multi_hint.hint.code,
                    channel_code=rule.channel_code or multi_hint.hint.channel_code,
                    medium_code=rule.medium_code or multi_hint.hint.medium_code,
                    touchpoint_type_code=rule.touchpoint_type_code or multi_hint.hint.touchpoint_type_code,
                    label=rule.touchpoint_label or multi_hint.hint.label,
                    metadata={**multi_hint.hint.metadata, **rule.metadata}
                ),
                session_context=multi_hint.session_context,
                metadata={**multi_hint.metadata, **rule.metadata}
            )
            modified_hints.append(modified_hint)
        
        return BatchTouchpointHint(
            hints=modified_hints,
            session_id=batch_hint.session_id,
            event_data=batch_hint.event_data,
            coordination_metadata={**batch_hint.coordination_metadata, **rule.metadata}
        )
    
    def _apply_session_mapping_rule(
        self, 
        batch_hint: BatchTouchpointHint, 
        rule: 'TouchpointMappingRule',
        session_context: Dict[str, Any]
    ) -> BatchTouchpointHint:
        """
        Apply session-aware mapping rule overrides to batch hint.
        
        Args:
            batch_hint: The original batch touchpoint hint
            rule: The session mapping rule to apply
            session_context: Session-level context for rule application
            
        Returns:
            BatchTouchpointHint: The modified batch hint with session rule overrides applied
        """
        # Apply session-aware rule overrides to each interaction hint
        modified_hints = []
        for multi_hint in batch_hint.hints:
            # Merge session context with rule metadata
            enhanced_metadata = {**multi_hint.hint.metadata, **rule.metadata, **session_context}
            
            modified_hint = MultiTouchpointHint(
                interaction_type=multi_hint.interaction_type,
                hint=TouchpointHint(
                    code=rule.touchpoint_code or multi_hint.hint.code,
                    channel_code=rule.channel_code or multi_hint.hint.channel_code,
                    medium_code=rule.medium_code or multi_hint.hint.medium_code,
                    touchpoint_type_code=rule.touchpoint_type_code or multi_hint.hint.touchpoint_type_code,
                    label=rule.touchpoint_label or multi_hint.hint.label,
                    metadata=enhanced_metadata
                ),
                session_context={**multi_hint.session_context, **session_context},
                metadata={**multi_hint.metadata, **rule.metadata}
            )
            modified_hints.append(modified_hint)
        
        return BatchTouchpointHint(
            hints=modified_hints,
            session_id=batch_hint.session_id,
            event_data=batch_hint.event_data,
            coordination_metadata={**batch_hint.coordination_metadata, **rule.metadata, **session_context}
        )
    
    def _resolve_single_with_session_context(
        self, 
        multi_hint: MultiTouchpointHint,
        session_id: Optional[str],
        coordination_metadata: Dict[str, Any]
    ) -> Touchpoint:
        """
        Resolve a single touchpoint with session context.
        
        Args:
            multi_hint: The multi-touchpoint hint for this interaction
            session_id: Session identifier for coordination
            coordination_metadata: Metadata for coordinating between interactions
            
        Returns:
            Touchpoint: The resolved touchpoint object
        """
        # Get or create channel with session context
        channel = self._get_or_create_channel_with_context(
            multi_hint.hint.channel_code, 
            coordination_metadata
        )
        
        # Get or create medium with session context
        medium = self._get_or_create_medium_with_context(
            multi_hint.hint.medium_code,
            coordination_metadata
        )
        
        # Get or create touchpoint type with session context
        touchpoint_type = self._get_or_create_touchpoint_type_with_context(
            multi_hint.hint.touchpoint_type_code,
            coordination_metadata
        )
        
        # Create or get touchpoint with session context
        touchpoint_code = multi_hint.hint.code or f"web.{multi_hint.interaction_type}"
        touchpoint_name = multi_hint.hint.label or f"Web {multi_hint.interaction_type.title()}"
        
        # Include session context in touchpoint metadata
        enhanced_metadata = {
            **multi_hint.hint.metadata,
            **multi_hint.session_context,
            'session_id': session_id,
            'interaction_type': multi_hint.interaction_type
        }
        
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': touchpoint_name,
                'channel': channel,
                'medium': medium,
                'touchpoint_type': touchpoint_type,
                'description': f"Auto-generated touchpoint for {touchpoint_code}",
                'is_active': True,
                'metadata': enhanced_metadata
            }
        )
        
        return touchpoint
    
    def _get_or_create_channel_with_context(
        self, 
        channel_code: Optional[str], 
        context: Dict[str, Any]
    ) -> Optional[Channel]:
        """Get or create channel with session context."""
        if not channel_code:
            return None
        
        # Include session context in channel metadata
        enhanced_metadata = {
            'session_context': context,
            'auto_generated': True
        }
        
        channel, _ = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': channel_code.title(),
                'description': f"Auto-generated channel for {channel_code}",
                'source_type': 'external',
                'metadata': enhanced_metadata
            }
        )
        
        return channel
    
    def _get_or_create_medium_with_context(
        self, 
        medium_code: Optional[str], 
        context: Dict[str, Any]
    ) -> Optional[Medium]:
        """Get or create medium with session context."""
        if not medium_code:
            return None
        
        # Include session context in medium metadata
        enhanced_metadata = {
            'session_context': context,
            'auto_generated': True
        }
        
        medium, _ = Medium.objects.get_or_create(
            code=medium_code,
            defaults={
                'name': medium_code.title(),
                'description': f"Auto-generated medium for {medium_code}",
                'communication_type': 'asynchronous',
                'metadata': enhanced_metadata
            }
        )
        
        return medium
    
    def _get_or_create_touchpoint_type_with_context(
        self, 
        touchpoint_type_code: Optional[str], 
        context: Dict[str, Any]
    ) -> Optional[TouchpointType]:
        """Get or create touchpoint type with session context."""
        if not touchpoint_type_code:
            return None
        
        # Include session context in touchpoint type metadata
        enhanced_metadata = {
            'session_context': context,
            'auto_generated': True
        }
        
        touchpoint_type, _ = TouchpointType.objects.get_or_create(
            code=touchpoint_type_code,
            defaults={
                'name': touchpoint_type_code.title(),
                'description': f"Auto-generated touchpoint type for {touchpoint_type_code}",
                'metadata': enhanced_metadata
            }
        )
        
        return touchpoint_type
    
    def _get_connector_type(self, subject: MultiTouchpointInferenceProtocol) -> str:
        """Extract connector type from subject class name."""
        class_name = subject.__class__.__name__.lower()
        if class_name.startswith('web'):
            return 'web'
        elif class_name.startswith('email'):
            return 'email'
        elif class_name.startswith('whatsapp'):
            return 'whatsapp'
        return 'generic'


class CachedExtendedTouchpointResolver(ExtendedTouchpointResolver):
    """
    Cached version of the extended touchpoint resolver for improved performance.
    
    This resolver adds caching to the extended touchpoint resolution process
    to avoid repeated database queries for the same touchpoint codes and
    session contexts.
    """
    
    def __init__(self, mapping_provider: 'BatchMappingProviderProtocol', cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached extended resolver.
        
        Args:
            mapping_provider: Provider for looking up batch mapping rules
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
        self._session_cache = {}
    
    def resolve_batch(self, subject: MultiTouchpointInferenceProtocol) -> List[Touchpoint]:
        """
        Resolve multiple touchpoints with caching.
        
        Args:
            subject: A connector interaction that implements MultiTouchpointInferenceProtocol
            
        Returns:
            List[Touchpoint]: Multiple resolved touchpoint objects
        """
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"batch_resolution:{subject.__class__.__name__}:{id(subject)}"
            cached_touchpoints = self._session_cache.get(cache_key)
            if cached_touchpoints is not None:
                return cached_touchpoints
        
        # Resolve using parent implementation
        touchpoints = super().resolve_batch(subject)
        
        # Cache the result if enabled
        if self.use_cache:
            self._session_cache[cache_key] = touchpoints
        
        return touchpoints
    
    def resolve_with_session_context(
        self, 
        subject: MultiTouchpointInferenceProtocol,
        session_context: Dict[str, Any]
    ) -> List[Touchpoint]:
        """
        Resolve touchpoints with session context and caching.
        
        Args:
            subject: A connector interaction that implements MultiTouchpointInferenceProtocol
            session_context: Session-level context for coordinated resolution
            
        Returns:
            List[Touchpoint]: Multiple resolved touchpoint objects with session context
        """
        # Check cache first if enabled
        if self.use_cache:
            session_key = f"session:{session_context.get('session_id', 'unknown')}"
            cache_key = f"session_resolution:{subject.__class__.__name__}:{session_key}"
            cached_touchpoints = self._session_cache.get(cache_key)
            if cached_touchpoints is not None:
                return cached_touchpoints
        
        # Resolve using parent implementation
        touchpoints = super().resolve_with_session_context(subject, session_context)
        
        # Cache the result if enabled
        if self.use_cache:
            session_key = f"session:{session_context.get('session_id', 'unknown')}"
            cache_key = f"session_resolution:{subject.__class__.__name__}:{session_key}"
            self._session_cache[cache_key] = touchpoints
        
        return touchpoints
