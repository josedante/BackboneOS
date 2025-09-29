"""
Extended protocols for multi-interaction touchpoint resolution.

This module extends the base connectors framework to support the websites app's
multi-interaction approach, session-aware resolution, and batch processing.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from interactions.models import Touchpoint
    from .models import TouchpointMappingRule
    from .protocols import TouchpointHint


@dataclass(frozen=True)
class MultiTouchpointHint:
    """
    Extended hint structure for multi-interaction touchpoint resolution.
    
    This dataclass supports the websites app's multi-interaction approach where
    a single event can create multiple interactions with different touchpoints.
    
    Attributes:
        interaction_type: Type of interaction (e.g., "page_view", "referrer_click", "session_start")
        hint: The base TouchpointHint for this interaction
        session_context: Session-level context for coordinated resolution
        metadata: Additional context data
    """
    interaction_type: str                    # e.g. "page_view", "referrer_click", "session_start"
    hint: 'TouchpointHint'                  # The base touchpoint hint
    session_context: Optional[Dict[str, Any]] = None  # Session-level context
    metadata: Dict[str, Any] = None          # Additional context
    
    def __post_init__(self):
        """Ensure metadata is always a dictionary."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.session_context is None:
            object.__setattr__(self, 'session_context', {})


@dataclass(frozen=True)
class BatchTouchpointHint:
    """
    Batch hint structure for processing multiple interactions together.
    
    This dataclass supports the websites app's requirement to process
    multiple related interactions (page view, referrer click, session start)
    with coordinated touchpoint resolution.
    
    Attributes:
        hints: List of MultiTouchpointHint for each interaction
        session_id: Session identifier for coordinated resolution
        event_data: Original event data for context
        coordination_metadata: Metadata for coordinating between interactions
    """
    hints: List[MultiTouchpointHint]
    session_id: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    coordination_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Ensure coordination_metadata is always a dictionary."""
        if self.coordination_metadata is None:
            object.__setattr__(self, 'coordination_metadata', {})


class MultiTouchpointInferenceProtocol(Protocol):
    """
    Extended protocol for multi-interaction touchpoint inference.
    
    This protocol extends the base TouchpointInferenceProtocol to support
    the websites app's multi-interaction approach and session-aware resolution.
    """
    
    def infer_multi_touchpoint_hints(self) -> BatchTouchpointHint:
        """
        Infer multiple touchpoint hints for coordinated resolution.
        
        This method should analyze the connector's data and return a
        BatchTouchpointHint containing multiple interaction hints that
        need to be resolved together.
        
        Returns:
            BatchTouchpointHint: Multiple touchpoint hints for coordinated resolution
        """
        ...
    
    def infer_touchpoint_hint(self) -> 'TouchpointHint':
        """
        Infer a single touchpoint hint (backward compatibility).
        
        This method maintains backward compatibility with the base protocol
        while supporting the extended multi-interaction approach.
        
        Returns:
            TouchpointHint: The inferred touchpoint information
        """
        ...


class SessionAwareTouchpointResolverProtocol(Protocol):
    """
    Protocol for session-aware touchpoint resolution.
    
    This protocol extends the base TouchpointResolverProtocol to support
    session-aware resolution and batch processing of multiple interactions.
    """
    
    def resolve_batch(self, subject: MultiTouchpointInferenceProtocol) -> List['Touchpoint']:
        """
        Resolve multiple touchpoints for a batch of interactions.
        
        This method processes multiple related interactions together,
        allowing for coordinated touchpoint resolution and session awareness.
        
        Args:
            subject: A connector interaction that implements MultiTouchpointInferenceProtocol
            
        Returns:
            List[Touchpoint]: Multiple resolved touchpoint objects
        """
        ...
    
    def resolve_with_session_context(
        self, 
        subject: MultiTouchpointInferenceProtocol,
        session_context: Dict[str, Any]
    ) -> List['Touchpoint']:
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
        ...


class BatchMappingProviderProtocol(Protocol):
    """
    Extended protocol for batch mapping rule providers.
    
    This protocol extends the base MappingProviderProtocol to support
    batch processing and session-aware mapping rule lookup.
    """
    
    def lookup_batch_mapping(
        self, 
        subject: MultiTouchpointInferenceProtocol, 
        batch_hint: BatchTouchpointHint
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up mapping rules for batch processing.
        
        This method supports batch mapping rule lookup for multiple
        related interactions with session context.
        
        Args:
            subject: The connector interaction requesting batch touchpoint resolution
            batch_hint: The batch touchpoint hint containing multiple interaction hints
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule for the batch
        """
        ...
    
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
        ...
