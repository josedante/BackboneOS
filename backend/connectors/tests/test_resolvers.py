"""
Tests for the touchpoint resolution framework.

This module tests the generic touchpoint resolvers that work with any
connector type.
"""

import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.db import transaction

from connectors.resolvers import DefaultTouchpointResolver, CachedTouchpointResolver
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from interactions.models import Touchpoint, TouchpointType, Channel, Medium


class MockConnector(TouchpointInferenceProtocol):
    """Mock connector for testing."""
    
    def __init__(self, hint: TouchpointHint):
        self.hint = hint
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return self.hint


class MockMappingProvider:
    """Mock mapping provider for testing."""
    
    def __init__(self, mapping_rule=None):
        self.mapping_rule = mapping_rule
    
    def lookup_mapping(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint):
        return self.mapping_rule


class MockMappingRule:
    """Mock mapping rule for testing."""
    
    def __init__(self, **kwargs):
        self.touchpoint_code = kwargs.get('touchpoint_code')
        self.touchpoint_label = kwargs.get('touchpoint_label')
        self.channel_code = kwargs.get('channel_code')
        self.medium_code = kwargs.get('medium_code')
        self.touchpoint_type_code = kwargs.get('touchpoint_type_code')
        self.metadata = kwargs.get('metadata', {})


class TestDefaultTouchpointResolver(TestCase):
    """Test the DefaultTouchpointResolver class."""
    
    def setUp(self):
        """Set up test data."""
        self.mapping_provider = MockMappingProvider()
        self.resolver = DefaultTouchpointResolver(self.mapping_provider)
    
    def test_resolver_initialization(self):
        """Test resolver initialization."""
        assert self.resolver.mapping_provider == self.mapping_provider
    
    def test_resolve_without_mapping_rule(self):
        """Test touchpoint resolution without mapping rule."""
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View"
        )
        connector = MockConnector(hint)
        
        with transaction.atomic():
            touchpoint = self.resolver.resolve(connector)
        
        # Verify touchpoint was created
        assert isinstance(touchpoint, Touchpoint)
        assert touchpoint.code == "web.page_read"
        assert touchpoint.name == "Web Page View"
        assert touchpoint.is_active is True
        
        # Verify three-dimensional classification was created
        assert touchpoint.channel is not None
        assert touchpoint.channel.code == "web"
        assert touchpoint.medium is not None
        assert touchpoint.medium.code == "organic"
        assert touchpoint.touchpoint_type is not None
        assert touchpoint.touchpoint_type.code == "landing_page"
    
    def test_resolve_with_mapping_rule(self):
        """Test touchpoint resolution with mapping rule."""
        hint = TouchpointHint(
            code="web.form_submit",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="form",
            label="Web Form Submit"
        )
        
        mapping_rule = MockMappingRule(
            touchpoint_code="web.lead_form",
            touchpoint_label="Lead Form",
            channel_code="web",
            medium_code="paid",
            touchpoint_type_code="lead_form"
        )
        
        self.mapping_provider.mapping_rule = mapping_rule
        connector = MockConnector(hint)
        
        with transaction.atomic():
            touchpoint = self.resolver.resolve(connector)
        
        # Verify mapping rule was applied
        assert touchpoint.code == "web.lead_form"
        assert touchpoint.name == "Lead Form"
    
    def test_resolve_reuses_existing_touchpoint(self):
        """Test that resolver reuses existing touchpoints."""
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View"
        )
        connector = MockConnector(hint)
        
        with transaction.atomic():
            touchpoint1 = self.resolver.resolve(connector)
            touchpoint2 = self.resolver.resolve(connector)
        
        # Should return the same touchpoint
        assert touchpoint1.id == touchpoint2.id
    
    def test_resolve_without_code(self):
        """Test touchpoint resolution without touchpoint code."""
        hint = TouchpointHint(
            channel_code="web",
            medium_code="organic",
            label="Generic Web Interaction"
        )
        connector = MockConnector(hint)
        
        with transaction.atomic():
            touchpoint = self.resolver.resolve(connector)
        
        # Should create a generic touchpoint code
        assert touchpoint.code == "generic.web"
        assert touchpoint.name == "Generic Web Interaction"
    
    def test_resolve_without_channel_code(self):
        """Test touchpoint resolution without channel code."""
        hint = TouchpointHint(
            code="generic.interaction",
            medium_code="organic",
            touchpoint_type_code="generic",
            label="Generic Interaction"
        )
        connector = MockConnector(hint)
        
        with transaction.atomic():
            touchpoint = self.resolver.resolve(connector)
        
        # Should create touchpoint without channel
        assert touchpoint.code == "generic.interaction"
        assert touchpoint.touchpoint_type is not None
        assert touchpoint.touchpoint_type.code == "generic"
    
    def test_apply_mapping_rule(self):
        """Test mapping rule application."""
        hint = TouchpointHint(
            code="web.form_submit",
            channel_code="web",
            medium_code="organic",
            label="Web Form Submit",
            metadata={"form_id": "contact"}
        )
        
        mapping_rule = MockMappingRule(
            touchpoint_code="web.lead_form",
            touchpoint_label="Lead Form",
            channel_code="web",
            medium_code="paid",
            metadata={"form_type": "lead"}
        )
        
        result_hint = self.resolver._apply_mapping_rule(hint, mapping_rule)
        
        # Verify mapping rule was applied
        assert result_hint.code == "web.lead_form"
        assert result_hint.label == "Lead Form"
        assert result_hint.channel_code == "web"
        assert result_hint.medium_code == "paid"
        
        # Verify metadata was merged
        assert result_hint.metadata["form_id"] == "contact"
        assert result_hint.metadata["form_type"] == "lead"
    
    def test_apply_mapping_rule_partial_override(self):
        """Test mapping rule with partial overrides."""
        hint = TouchpointHint(
            code="web.form_submit",
            channel_code="web",
            medium_code="organic",
            label="Web Form Submit"
        )
        
        mapping_rule = MockMappingRule(
            touchpoint_code="web.lead_form",
            # Only override code, leave other fields as-is
        )
        
        result_hint = self.resolver._apply_mapping_rule(hint, mapping_rule)
        
        # Verify only code was overridden
        assert result_hint.code == "web.lead_form"
        assert result_hint.channel_code == "web"  # Original value
        assert result_hint.medium_code == "organic"  # Original value
        assert result_hint.label == "Web Form Submit"  # Original value
    
    def test_ensure_required_fields(self):
        """Test the ensure_required_fields method."""
        hint = TouchpointHint(code="test.code")
        connector = MockConnector(hint)
        
        result_hint = self.resolver._ensure_required_fields(connector, hint)
        
        # Default implementation should return the hint unchanged
        assert result_hint == hint
    
    def test_get_or_create_touchpoint(self):
        """Test touchpoint creation logic."""
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View"
        )
        
        with transaction.atomic():
            touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify touchpoint was created
        assert isinstance(touchpoint, Touchpoint)
        assert touchpoint.code == "web.page_read"
        assert touchpoint.name == "Web Page View"
        assert touchpoint.is_active is True
        
        # Verify three-dimensional classification was created
        assert touchpoint.channel is not None
        assert touchpoint.channel.code == "web"
        assert touchpoint.medium is not None
        assert touchpoint.medium.code == "organic"
        assert touchpoint.touchpoint_type is not None
        assert touchpoint.touchpoint_type.code == "landing_page"
    
    def test_get_or_create_touchpoint_with_existing_type(self):
        """Test touchpoint creation with existing touchpoint type."""
        # Create a touchpoint type first
        touchpoint_type = TouchpointType.objects.create(
            code="landing_page",
            name="Landing Page",
            description="Landing page touchpoints"
        )
        
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View"
        )
        
        with transaction.atomic():
            touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify touchpoint was created with existing type
        assert touchpoint.touchpoint_type == touchpoint_type


class TestCachedTouchpointResolver(TestCase):
    """Test the CachedTouchpointResolver class."""
    
    def setUp(self):
        """Set up test data."""
        self.mapping_provider = MockMappingProvider()
        self.resolver = CachedTouchpointResolver(self.mapping_provider)
    
    def test_resolver_initialization(self):
        """Test cached resolver initialization."""
        assert self.resolver.mapping_provider == self.mapping_provider
        assert self.resolver.cache_timeout == 3600
        assert hasattr(self.resolver, '_touchpoint_cache')
        assert hasattr(self.resolver, '_channel_cache')
        assert hasattr(self.resolver, '_touchpoint_type_cache')
    
    def test_resolve_with_caching(self):
        """Test touchpoint resolution with caching."""
        hint = TouchpointHint(
            code="web.page_read",
            channel_code="web",
            medium_code="organic",
            touchpoint_type_code="landing_page",
            label="Web Page View"
        )
        connector = MockConnector(hint)
        
        with transaction.atomic():
            # First resolution should create and cache
            touchpoint1 = self.resolver.resolve(connector)
            
            # Second resolution should use cache
            touchpoint2 = self.resolver.resolve(connector)
        
        # Should return the same touchpoint
        assert touchpoint1.id == touchpoint2.id
        
        # Verify cache was populated
        assert "web.page_read" in self.resolver._touchpoint_cache
    
    def test_custom_cache_timeout(self):
        """Test resolver with custom cache timeout."""
        resolver = CachedTouchpointResolver(self.mapping_provider, cache_timeout=7200)
        assert resolver.cache_timeout == 7200
    
    def test_disable_caching(self):
        """Test resolver with caching disabled."""
        resolver = CachedTouchpointResolver(self.mapping_provider, use_cache=False)
        assert resolver.use_cache is False
