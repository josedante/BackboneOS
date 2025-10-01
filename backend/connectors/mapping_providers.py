"""
Mapping providers for touchpoint resolution.

This module provides implementations of the MappingProviderProtocol that can
look up mapping rules from various sources (database, cache, files, etc.).
The providers implement the priority-based rule resolution system.
"""

from typing import Optional, TYPE_CHECKING
from django.core.cache import cache

from .protocols import TouchpointHint, MappingProviderProtocol

if TYPE_CHECKING:
    from .models import TouchpointMappingRule


class DatabaseMappingProvider:
    """
    Database-backed mapping provider for configurable touchpoint rules.
    
    This provider implements the priority-based rule resolution system:
    1. Specific source + event code (highest priority)
    2. Generic connector type + event code
    3. Generic event code only (lowest priority)
    
    The provider supports caching for improved performance and can be extended
    with additional lookup strategies.
    """
    
    def __init__(self, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the database mapping provider.
        
        Args:
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        self.cache_timeout = cache_timeout
        self.use_cache = use_cache
    
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up mapping rule using explicit parameters.
        
        This method implements the priority-based resolution system:
        1. Try specific source + event code
        2. Try generic connector type + event code
        3. Try generic event code only
        
        Args:
            connector_type: Type of connector (e.g., 'web', 'email', 'whatsapp')
            source_identifier: Source identifier (e.g., website URL, email domain)
            hint: The touchpoint hint containing event code
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule, if any
        """
        if not hint.code:
            return None
        
        # Try specific source first (highest priority)
        if source_identifier:
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
    
    def _lookup_rule(
        self, 
        connector_type: str, 
        source_identifier: str, 
        event_code: str
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up a specific mapping rule from the database.
        
        Args:
            connector_type: The connector type to match
            source_identifier: The source identifier to match
            event_code: The event code to match
            
        Returns:
            TouchpointMappingRule or None: The matching rule, if any
        """
        # Check cache first if enabled
        if self.use_cache:
            cache_key = f"touchpoint_mapping:{connector_type}:{source_identifier}:{event_code}"
            cached_rule = cache.get(cache_key)
            if cached_rule is not None:
                return cached_rule
        
        # Import here to avoid circular imports
        from .models import TouchpointMappingRule
        
        # Query the database
        rule = TouchpointMappingRule.objects.filter(
            connector_type=connector_type,
            source_identifier=source_identifier,
            event_code=event_code,
            is_active=True
        ).order_by('-priority').first()
        
        # Cache the result if enabled
        if self.use_cache and rule:
            cache.set(cache_key, rule, self.cache_timeout)
        
        return rule
    


class CachedMappingProvider(DatabaseMappingProvider):
    """
    Enhanced mapping provider with advanced caching capabilities.
    
    This provider extends the database provider with additional caching features
    including cache invalidation and bulk cache warming.
    """
    
    def __init__(self, cache_timeout: int = 3600, use_cache: bool = True):
        """
        Initialize the cached mapping provider.
        
        Args:
            cache_timeout: Cache timeout in seconds (default: 1 hour)
            use_cache: Whether to use caching (default: True)
        """
        super().__init__(cache_timeout, use_cache)
        self._local_cache = {}
    
    def invalidate_cache(self, connector_type: str = None, source_identifier: str = None):
        """
        Invalidate cached mapping rules.
        
        Args:
            connector_type: Specific connector type to invalidate (optional)
            source_identifier: Specific source identifier to invalidate (optional)
        """
        if connector_type and source_identifier:
            # Invalidate specific rule
            cache_key = f"touchpoint_mapping:{connector_type}:{source_identifier}:*"
            cache.delete_many(cache.keys(cache_key))
        elif connector_type:
            # Invalidate all rules for connector type
            cache_key = f"touchpoint_mapping:{connector_type}:*"
            cache.delete_many(cache.keys(cache_key))
        else:
            # Invalidate all mapping rules
            cache.delete_many(cache.keys("touchpoint_mapping:*"))
        
        # Clear local cache
        self._local_cache.clear()
    
    def warm_cache(self, connector_type: str = None):
        """
        Warm the cache with mapping rules.
        
        Args:
            connector_type: Specific connector type to warm (optional)
        """
        from .models import TouchpointMappingRule
        
        # Build query
        queryset = TouchpointMappingRule.objects.filter(is_active=True)
        if connector_type:
            queryset = queryset.filter(connector_type=connector_type)
        
        # Cache all matching rules
        for rule in queryset:
            cache_key = f"touchpoint_mapping:{rule.connector_type}:{rule.source_identifier}:{rule.event_code}"
            cache.set(cache_key, rule, self.cache_timeout)


class FileMappingProvider:
    """
    File-based mapping provider for static mapping rules.
    
    This provider reads mapping rules from configuration files (JSON, YAML, etc.)
    and can be used for deployment-specific or environment-specific rules.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the file mapping provider.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self._rules = {}
        self._load_rules()
    
    def _load_rules(self):
        """Load mapping rules from the configuration file."""
        if not self.config_file:
            return
        
        import json
        import os
        
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self._rules = data.get('mapping_rules', {})
        except (json.JSONDecodeError, IOError) as e:
            # Log error in production
            pass
    
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional['TouchpointMappingRule']:
        """
        Look up mapping rule from file configuration.
        
        Args:
            connector_type: Type of connector (e.g., 'web', 'email', 'whatsapp')
            source_identifier: Source identifier (e.g., website URL, email domain)
            hint: The touchpoint hint containing event code
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule, if any
        """
        if not hint.code:
            return None
        
        # Try specific source first
        if source_identifier:
            rule_key = f"{connector_type}:{source_identifier}:{hint.code}"
            if rule_key in self._rules:
                return self._create_rule_from_config(rule_key, self._rules[rule_key])
        
        # Try generic connector type
        rule_key = f"{connector_type}::{hint.code}"
        if rule_key in self._rules:
            return self._create_rule_from_config(rule_key, self._rules[rule_key])
        
        # Try generic event code
        rule_key = f"::{hint.code}"
        if rule_key in self._rules:
            return self._create_rule_from_config(rule_key, self._rules[rule_key])
        
        return None
    
    def _create_rule_from_config(self, rule_key: str, config: dict):
        """Create a TouchpointMappingRule from configuration data."""
        # This would create a mock rule object or use a different approach
        # depending on the specific implementation needs
        pass
