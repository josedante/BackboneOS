"""
Protocols and interfaces for the Touchpoint Resolution System.

This module defines the core protocols that all connector types must implement
to participate in the touchpoint resolution framework. The protocols ensure
consistent behavior across all connector implementations while allowing
specialized logic for each connector type.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from interactions.models import Touchpoint
    from .models import TouchpointMappingRule


@dataclass(frozen=True)
class TouchpointHint:
    """
    Standardized hint structure for touchpoint inference.
    
    This dataclass represents the information that a connector can provide
    about what kind of touchpoint should be created for an interaction.
    It serves as the bridge between connector-specific logic and the
    generic touchpoint resolution framework.
    
    Attributes:
        code: Touchpoint code (e.g., "web.page_read", "email.open")
        channel_code: Channel identifier (e.g., "web", "email", "chat")
        medium_code: Medium classification (e.g., "organic", "paid", "referral")
        label: Human-friendly name for the touchpoint
        metadata: Additional context data as a dictionary
    """
    code: Optional[str] = None              # e.g. "web.page_read", "email.open"
    channel_code: Optional[str] = None      # e.g. "web", "email", "chat"
    medium_code: Optional[str] = None       # e.g. "organic", "paid", "referral"
    label: Optional[str] = None             # Human-friendly name
    metadata: dict = None                   # Additional context
    
    def __post_init__(self):
        """Ensure metadata is always a dictionary."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


class TouchpointInferenceProtocol(Protocol):
    """
    Protocol that connector models must implement.
    
    Any model that wants to participate in touchpoint resolution must
    implement this protocol. The protocol defines a single method that
    returns a TouchpointHint with the connector's best guess about
    what touchpoint should be created.
    
    This protocol allows the generic resolution framework to work with
    any connector type without knowing the specific implementation details.
    """
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        """
        Infer a touchpoint hint from the connector's data.
        
        This method should analyze the connector's specific data (UTM parameters,
        event types, etc.) and return a TouchpointHint that represents the
        connector's best understanding of what touchpoint should be created.
        
        Returns:
            TouchpointHint: The inferred touchpoint information
        """
        ...


class TouchpointResolverProtocol(Protocol):
    """
    Protocol for touchpoint resolution strategies.
    
    This protocol defines the interface for touchpoint resolvers. A resolver
    takes a subject that implements TouchpointInferenceProtocol and returns
    a Touchpoint object.
    
    The protocol allows for different resolution strategies (default, cached,
    specialized, etc.) while maintaining a consistent interface.
    """
    
    def resolve(self, subject: TouchpointInferenceProtocol) -> Touchpoint:
        """
        Resolve a touchpoint for the given subject.
        
        Args:
            subject: A connector interaction that implements TouchpointInferenceProtocol
            
        Returns:
            Touchpoint: The resolved touchpoint object
        """
        ...


class MappingProviderProtocol(Protocol):
    """
    Protocol for mapping rule providers.
    
    This protocol defines the interface for providers that can look up
    mapping rules. Mapping rules allow administrators to override the
    default touchpoint creation logic without code changes.
    
    The protocol supports different providers (database, cache, file-based, etc.)
    while maintaining a consistent interface.
    """
    
    def lookup_mapping(
        self, 
        subject: TouchpointInferenceProtocol, 
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        """
        Look up a mapping rule for the given subject and hint.
        
        Args:
            subject: The connector interaction requesting touchpoint resolution
            hint: The touchpoint hint from the connector's inference
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule, if any
        """
        ...
