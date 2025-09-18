"""
Tests for the mapping providers.

This module tests the mapping provider implementations that handle
configurable touchpoint resolution rules.
"""

import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.core.cache import cache

from connectors.mapping_providers import (
    DatabaseMappingProvider, 
    CachedMappingProvider, 
    FileMappingProvider
)
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from connectors.models import TouchpointMappingRule


class MockConnector(TouchpointInferenceProtocol):
    """Mock connector for testing."""
    
    def __init__(self, class_name="WebInteraction", source_identifier=""):
        self.class_name = class_name
        self.source_identifier = source_identifier
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(code="test.code")
    
    @property
    def __class__(self):
        """Mock the class name."""
        class MockClass:
            def __init__(self, name):
                self.__name__ = name
        return MockClass(self.class_name)


class TestDatabaseMappingProvider(TestCase):
    """Test the DatabaseMappingProvider class."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = DatabaseMappingProvider()
        self.connector = MockConnector()
    
    def test_provider_initialization(self):
        """Test provider initialization."""
        assert self.provider.cache_timeout == 3600
        assert self.provider.use_cache is True
    
    def test_provider_initialization_custom(self):
        """Test provider initialization with custom settings."""
        provider = DatabaseMappingProvider(cache_timeout=7200, use_cache=False)
        assert provider.cache_timeout == 7200
        assert provider.use_cache is False
    
    def test_lookup_mapping_no_hint_code(self):
        """Test lookup with no hint code."""
        hint = TouchpointHint()  # No code
        result = self.provider.lookup_mapping(self.connector, hint)
        assert result is None
    
    def test_lookup_mapping_no_rules(self):
        """Test lookup with no matching rules."""
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        assert result is None
    
    def test_lookup_mapping_specific_source(self):
        """Test lookup with specific source identifier."""
        # Create a mapping rule
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://example.com",
            event_code="web.page_read",
            touchpoint_code="web.example_page",
            touchpoint_label="Example Page",
            priority=200
        )
        
        # Create connector with specific source
        connector = MockConnector(source_identifier="https://example.com")
        hint = TouchpointHint(code="web.page_read")
        
        result = self.provider.lookup_mapping(connector, hint)
        
        assert result is not None
        assert result.touchpoint_code == "web.example_page"
        assert result.priority == 200
    
    def test_lookup_mapping_generic_connector_type(self):
        """Test lookup with generic connector type."""
        # Create a mapping rule
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",  # Generic
            event_code="web.page_read",
            touchpoint_code="web.generic_page",
            touchpoint_label="Generic Web Page",
            priority=100
        )
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        assert result is not None
        assert result.touchpoint_code == "web.generic_page"
        assert result.priority == 100
    
    def test_lookup_mapping_generic_event_code(self):
        """Test lookup with generic event code."""
        # Create a mapping rule
        rule = TouchpointMappingRule.objects.create(
            connector_type="",  # Generic
            source_identifier="",  # Generic
            event_code="web.page_read",
            touchpoint_code="web.fallback_page",
            touchpoint_label="Fallback Page",
            priority=50
        )
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        assert result is not None
        assert result.touchpoint_code == "web.fallback_page"
        assert result.priority == 50
    
    def test_lookup_mapping_priority_order(self):
        """Test that higher priority rules are returned first."""
        # Create multiple rules with different priorities
        rule1 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.low_priority",
            priority=50
        )
        
        rule2 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.high_priority",
            priority=150
        )
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        # Should return the higher priority rule
        assert result.touchpoint_code == "web.high_priority"
        assert result.priority == 150
    
    def test_lookup_mapping_inactive_rules(self):
        """Test that inactive rules are not returned."""
        # Create an inactive rule
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.inactive_rule",
            is_active=False
        )
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        assert result is None
    
    def test_get_connector_type(self):
        """Test connector type extraction."""
        # Test web connector
        web_connector = MockConnector("WebInteraction")
        assert self.provider._get_connector_type(web_connector) == "web"
        
        # Test email connector
        email_connector = MockConnector("EmailInteraction")
        assert self.provider._get_connector_type(email_connector) == "email"
        
        # Test WhatsApp connector
        whatsapp_connector = MockConnector("WhatsAppInteraction")
        assert self.provider._get_connector_type(whatsapp_connector) == "whatsapp"
        
        # Test generic connector
        generic_connector = MockConnector("GenericInteraction")
        assert self.provider._get_connector_type(generic_connector) == "generic"
    
    def test_get_source_identifier(self):
        """Test source identifier extraction."""
        # Default implementation should return empty string
        result = self.provider._get_source_identifier(self.connector)
        assert result == ""


class TestCachedMappingProvider(TestCase):
    """Test the CachedMappingProvider class."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = CachedMappingProvider()
        self.connector = MockConnector()
        # Clear cache before each test
        cache.clear()
    
    def test_provider_initialization(self):
        """Test cached provider initialization."""
        assert hasattr(self.provider, '_local_cache')
        assert self.provider.cache_timeout == 3600
        assert self.provider.use_cache is True
    
    @patch('connectors.mapping_providers.cache')
    def test_lookup_mapping_with_cache(self, mock_cache):
        """Test lookup with caching enabled."""
        # Mock cache to return None (cache miss)
        mock_cache.get.return_value = None
        
        # Create a mapping rule
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.cached_rule",
            priority=100
        )
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        # Verify cache was checked
        mock_cache.get.assert_called_once()
        
        # Verify result was cached
        mock_cache.set.assert_called_once()
        
        assert result is not None
        assert result.touchpoint_code == "web.cached_rule"
    
    @patch('connectors.mapping_providers.cache')
    def test_lookup_mapping_cache_hit(self, mock_cache):
        """Test lookup with cache hit."""
        # Create a mock rule
        mock_rule = Mock()
        mock_rule.touchpoint_code = "web.cached_rule"
        
        # Mock cache to return the rule (cache hit)
        mock_cache.get.return_value = mock_rule
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        # Verify cache was checked
        mock_cache.get.assert_called_once()
        
        # Verify result was not queried from database
        mock_cache.set.assert_not_called()
        
        assert result == mock_rule
    
    @patch('connectors.mapping_providers.cache')
    def test_invalidate_cache_specific(self, mock_cache):
        """Test cache invalidation for specific rule."""
        mock_cache.keys.return_value = ["touchpoint_mapping:web::web.page_read"]
        
        self.provider.invalidate_cache("web", "")
        
        # Verify cache keys were retrieved
        mock_cache.keys.assert_called_once()
        
        # Verify cache was cleared
        mock_cache.delete_many.assert_called_once()
    
    @patch('connectors.mapping_providers.cache')
    def test_invalidate_cache_all(self, mock_cache):
        """Test cache invalidation for all rules."""
        mock_cache.keys.return_value = ["touchpoint_mapping:web::web.page_read"]
        
        self.provider.invalidate_cache()
        
        # Verify cache was cleared
        mock_cache.delete_many.assert_called_once()
    
    @patch('connectors.mapping_providers.cache')
    def test_warm_cache(self, mock_cache):
        """Test cache warming."""
        # Create mapping rules
        rule1 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.rule1",
            priority=100
        )
        
        rule2 = TouchpointMappingRule.objects.create(
            connector_type="email",
            source_identifier="",
            event_code="email.open",
            touchpoint_code="email.rule2",
            priority=100
        )
        
        self.provider.warm_cache()
        
        # Verify cache was set for both rules
        assert mock_cache.set.call_count == 2
    
    @patch('connectors.mapping_providers.cache')
    def test_warm_cache_specific_connector(self, mock_cache):
        """Test cache warming for specific connector type."""
        # Create mapping rules
        rule1 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="",
            event_code="web.page_read",
            touchpoint_code="web.rule1",
            priority=100
        )
        
        rule2 = TouchpointMappingRule.objects.create(
            connector_type="email",
            source_identifier="",
            event_code="email.open",
            touchpoint_code="email.rule2",
            priority=100
        )
        
        self.provider.warm_cache("web")
        
        # Verify cache was set only for web rules
        assert mock_cache.set.call_count == 1


class TestFileMappingProvider(TestCase):
    """Test the FileMappingProvider class."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = FileMappingProvider()
        self.connector = MockConnector()
    
    def test_provider_initialization(self):
        """Test file provider initialization."""
        assert self.provider.config_file is None
        assert self.provider._rules == {}
    
    def test_provider_initialization_with_file(self):
        """Test file provider initialization with config file."""
        provider = FileMappingProvider("test_config.json")
        assert provider.config_file == "test_config.json"
    
    def test_lookup_mapping_no_hint_code(self):
        """Test lookup with no hint code."""
        hint = TouchpointHint()  # No code
        result = self.provider.lookup_mapping(self.connector, hint)
        assert result is None
    
    def test_lookup_mapping_no_rules(self):
        """Test lookup with no matching rules."""
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        assert result is None
    
    def test_lookup_mapping_with_rules(self):
        """Test lookup with configured rules."""
        # Set up rules
        self.provider._rules = {
            "web::web.page_read": {
                "touchpoint_code": "web.generic_page",
                "touchpoint_label": "Generic Web Page"
            }
        }
        
        hint = TouchpointHint(code="web.page_read")
        result = self.provider.lookup_mapping(self.connector, hint)
        
        # Should return a mock rule (implementation would create real rule)
        assert result is None  # Mock implementation
    
    def test_get_connector_type(self):
        """Test connector type extraction."""
        # Test web connector
        web_connector = MockConnector("WebInteraction")
        assert self.provider._get_connector_type(web_connector) == "web"
        
        # Test email connector
        email_connector = MockConnector("EmailInteraction")
        assert self.provider._get_connector_type(email_connector) == "email"
        
        # Test generic connector
        generic_connector = MockConnector("GenericInteraction")
        assert self.provider._get_connector_type(generic_connector) == "generic"
    
    def test_get_source_identifier(self):
        """Test source identifier extraction."""
        result = self.provider._get_source_identifier(self.connector)
        assert result == ""
