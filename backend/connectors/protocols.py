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
        touchpoint_type_code: Touchpoint type classification (e.g., "landing_page", "form", "chat")
        parent_code: Optional parent touchpoint code for hierarchical structure
        label: Human-friendly name for the touchpoint
        metadata: Additional context data as a dictionary
    """
    code: Optional[str] = None              # e.g. "web.page_read", "email.open"
    channel_code: Optional[str] = None      # e.g. "web", "email", "chat"
    medium_code: Optional[str] = None       # e.g. "organic", "paid", "referral"
    touchpoint_type_code: Optional[str] = None  # e.g. "landing_page", "form", "chat"
    parent_code: Optional[str] = None       # e.g. parent touchpoint code for hierarchy
    url: Optional[str] = None               # e.g. "https://www.thebackbonegroup.com/"
    label: Optional[str] = None             # Human-friendly name
    metadata: dict = None                   # Additional context
    
    def __post_init__(self):
        """Ensure metadata is always a dictionary."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


class TouchpointResolverProtocol(Protocol):
    """
    Protocol for touchpoint resolution strategies.
    
    This protocol defines the interface for touchpoint resolvers. A resolver
    takes a TouchpointHint with explicit parameters and returns a Touchpoint object.
    
    The protocol allows for different resolution strategies (default, cached,
    specialized, etc.) while maintaining a consistent interface.
    """
    
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        """
        Resolve a touchpoint from a hint with explicit parameters.
        
        Args:
            hint: TouchpointHint containing touchpoint information
            connector_type: Type of connector (e.g., 'web', 'email', 'whatsapp')
            source_identifier: Source identifier (e.g., website URL, email domain)
            
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
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        """
        Look up a mapping rule using explicit parameters.
        
        Args:
            connector_type: Type of connector (e.g., 'web', 'email', 'whatsapp')
            source_identifier: Source identifier (e.g., website URL, email domain)
            hint: The touchpoint hint containing event code
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule, if any
        """
        ...
