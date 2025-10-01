"""
Tests for the touchpoint resolution protocols.

This module tests the core protocols and interfaces that define the contract
for the touchpoint resolution system.
"""

import pytest
from dataclasses import dataclass
from typing import Optional

from connectors.protocols import TouchpointHint, TouchpointResolverProtocol, MappingProviderProtocol
from interactions.models import Touchpoint


class TestTouchpointHint:
    """Test the TouchpointHint dataclass."""
    
    def test_touchpoint_hint_creation(self):
        """Test basic TouchpointHint creation."""
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View",
            metadata={"url": "/test", "session_id": "abc123"}
        )
        
        assert hint.code == "web.page_read"
        assert hint.channel_code == "web"
        assert hint.medium_code == "organic"
        assert hint.touchpoint_type_code == "landing_page"
        assert hint.label == "Web Page View"
        assert hint.metadata == {"url": "/test", "session_id": "abc123"}
    
    def test_touchpoint_hint_defaults(self):
        """Test TouchpointHint with default values."""
        hint = TouchpointHint()
        
        assert hint.code is None
        assert hint.channel_code is None
        assert hint.medium_code is None
        assert hint.touchpoint_type_code is None
        assert hint.label is None
        assert hint.metadata == {}  # Should be empty dict, not None
    
    def test_touchpoint_hint_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        hint = TouchpointHint(code="test.code")
        assert hint.metadata == {}
    
    def test_touchpoint_hint_immutability(self):
        """Test that TouchpointHint is immutable."""
        hint = TouchpointHint(code="test.code")
        
        with pytest.raises(AttributeError):
            hint.code = "new.code"
        
        with pytest.raises(AttributeError):
            hint.metadata = {"new": "value"}


class TestTouchpointResolverProtocol:
    """Test the TouchpointResolverProtocol interface."""
    
    def test_protocol_implementation(self):
        """Test that a class can implement the resolver protocol."""
        
        class MockResolver:
            def resolve(self, hint: TouchpointHint, *, connector_type: str, source_identifier: str = '') -> Touchpoint:
                # This would normally create a real Touchpoint
                # For testing, we'll just return a mock
                return None  # In real tests, this would be a Touchpoint instance
        
        # This should not raise any errors
        resolver = MockResolver()
        hint = TouchpointHint(code="test.code")
        result = resolver.resolve(hint, connector_type='web', source_identifier='test.com')
        
        # In a real test, we'd assert the result is a Touchpoint
        assert result is None  # Mock implementation


class TestMappingProviderProtocol:
    """Test the MappingProviderProtocol interface."""
    
    def test_protocol_implementation(self):
        """Test that a class can implement the mapping provider protocol."""
        
        class MockMappingProvider:
            def lookup_mapping(self, *, connector_type: str, source_identifier: str, hint: TouchpointHint):
                return None  # Mock implementation
        
        # This should not raise any errors
        provider = MockMappingProvider()
        hint = TouchpointHint(code="test.code")
        result = provider.lookup_mapping(
            connector_type='web',
            source_identifier='test.com',
            hint=hint
        )
        
        assert result is None  # Mock implementation


class TestProtocolIntegration:
    """Test integration between different protocols."""
    
    def test_full_workflow_simulation(self):
        """Test a simulated full workflow using all protocols."""
        
        # Create a hint directly (no connector needed)
        hint = TouchpointHint(
            code="web.form_submit",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="web_form",
            label="Web Form Submit",
            metadata={"form_id": "contact_form"}
        )
        
        class MockMappingProvider:
            def lookup_mapping(self, *, connector_type: str, source_identifier: str, hint: TouchpointHint):
                # Simulate finding a mapping rule
                if hint.code == "web.form_submit":
                    return MockMappingRule()
                return None
        
        class MockMappingRule:
            def __init__(self):
                self.touchpoint_code = "web.lead_form"
                self.touchpoint_label = "Lead Form"
                self.channel_code = "web"
                self.medium_code = "organic"
                self.touchpoint_type_code = "web_form"
                self.metadata = {"form_type": "lead"}
        
        class MockResolver:
            def __init__(self, mapping_provider: MappingProviderProtocol):
                self.mapping_provider = mapping_provider
            
            def resolve(self, hint: TouchpointHint, *, connector_type: str, source_identifier: str = '') -> Touchpoint:
                mapping_rule = self.mapping_provider.lookup_mapping(
                    connector_type=connector_type,
                    source_identifier=source_identifier,
                    hint=hint
                )
                
                # Simulate applying mapping rule
                if mapping_rule:
                    final_code = mapping_rule.touchpoint_code
                    final_label = mapping_rule.touchpoint_label
                else:
                    final_code = hint.code
                    final_label = hint.label
                
                # In a real implementation, this would create a Touchpoint
                return None  # Mock implementation
        
        # Test the full workflow
        mapping_provider = MockMappingProvider()
        resolver = MockResolver(mapping_provider)
        
        # Verify hint
        assert hint.code == "web.form_submit"
        
        # Look up mapping rule
        mapping_rule = mapping_provider.lookup_mapping(
            connector_type='web',
            source_identifier='test.com',
            hint=hint
        )
        assert mapping_rule is not None
        assert mapping_rule.touchpoint_code == "web.lead_form"
        
        # Resolve touchpoint
        touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='test.com')
        # In a real test, we'd assert the touchpoint properties
        assert touchpoint is None  # Mock implementation
