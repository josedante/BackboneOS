"""
Tests for the connector models.

This module tests the TouchpointMappingRule model and its validation logic.
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from connectors.models import TouchpointMappingRule


class TestTouchpointMappingRule(TestCase):
    """Test the TouchpointMappingRule model."""
    
    def test_model_creation(self):
        """Test basic model creation."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://example.com",
            event_code="web.page_read",
            touchpoint_code="web.example_page",
            touchpoint_label="Example Page",
            channel_code="web",
            medium_code="organic",
            priority=200
        )
        
        assert rule.connector_type == "web"
        assert rule.source_identifier == "https://example.com"
        assert rule.event_code == "web.page_read"
        assert rule.touchpoint_code == "web.example_page"
        assert rule.touchpoint_label == "Example Page"
        assert rule.channel_code == "web"
        assert rule.medium_code == "organic"
        assert rule.priority == 200
        assert rule.is_active is True
        assert rule.metadata == {}
    
    def test_model_creation_minimal(self):
        """Test model creation with minimal fields."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.minimal_rule"
        )
        
        assert rule.connector_type == "web"
        assert rule.source_identifier == ""
        assert rule.event_code == "web.page_read"
        assert rule.touchpoint_code == "web.minimal_rule"
        assert rule.touchpoint_label == ""
        assert rule.channel_code == ""
        assert rule.medium_code == ""
        assert rule.priority == 100  # Default value
        assert rule.is_active is True
        assert rule.metadata == {}
    
    def test_model_str_representation(self):
        """Test string representation of the model."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://example.com",
            event_code="web.page_read",
            touchpoint_code="web.example_page"
        )
        
        expected = "web:https://example.com:web.page_read -> web.example_page"
        assert str(rule) == expected
    
    def test_model_str_representation_no_source(self):
        """Test string representation without source identifier."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.generic_page"
        )
        
        expected = "web::web.page_read -> web.generic_page"
        assert str(rule) == expected
    
    def test_model_ordering(self):
        """Test model ordering by priority, connector_type, and event_code."""
        # Create rules with different priorities
        rule1 = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.low_priority",
            priority=50
        )
        
        rule2 = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.high_priority",
            priority=150
        )
        
        rule3 = TouchpointMappingRule.objects.create(
            connector_type="email",
            event_code="email.open",
            touchpoint_code="email.medium_priority",
            priority=100
        )
        
        # Get all rules ordered
        rules = list(TouchpointMappingRule.objects.all())
        
        # Should be ordered by priority (desc), then connector_type, then event_code
        assert rules[0] == rule2  # Highest priority
        assert rules[1] == rule3  # Medium priority
        assert rules[2] == rule1  # Lowest priority
    
    def test_model_unique_constraint(self):
        """Test unique constraint on connector_type, source_identifier, and event_code."""
        # Create first rule
        TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://example.com",
            event_code="web.page_read",
            touchpoint_code="web.first_rule"
        )
        
        # Try to create duplicate rule
        with pytest.raises(IntegrityError):
            TouchpointMappingRule.objects.create(
                connector_type="web",
                source_identifier="https://example.com",
                event_code="web.page_read",
                touchpoint_code="web.second_rule"
            )
    
    def test_model_unique_constraint_different_source(self):
        """Test that different source identifiers are allowed."""
        # Create first rule
        rule1 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://example.com",
            event_code="web.page_read",
            touchpoint_code="web.first_rule"
        )
        
        # Create second rule with different source
        rule2 = TouchpointMappingRule.objects.create(
            connector_type="web",
            source_identifier="https://other.com",
            event_code="web.page_read",
            touchpoint_code="web.second_rule"
        )
        
        # Both rules should exist
        assert TouchpointMappingRule.objects.count() == 2
        assert rule1.touchpoint_code == "web.first_rule"
        assert rule2.touchpoint_code == "web.second_rule"
    
    def test_model_clean_validation_success(self):
        """Test clean validation with valid data."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.valid_rule"
        )
        
        # Should not raise any exceptions
        rule.clean()
    
    def test_model_clean_validation_with_label(self):
        """Test clean validation with touchpoint_label."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_label="Valid Rule"
        )
        
        # Should not raise any exceptions
        rule.clean()
    
    def test_model_clean_validation_with_channel_code(self):
        """Test clean validation with channel_code."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read",
            channel_code="web"
        )
        
        # Should not raise any exceptions
        rule.clean()
    
    def test_model_clean_validation_with_medium_code(self):
        """Test clean validation with medium_code."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read",
            medium_code="organic"
        )
        
        # Should not raise any exceptions
        rule.clean()
    
    def test_model_clean_validation_with_metadata(self):
        """Test clean validation with metadata."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read",
            metadata={"custom": "value"}
        )
        
        # Should not raise any exceptions
        rule.clean()
    
    def test_model_clean_validation_failure(self):
        """Test clean validation failure with no override fields."""
        rule = TouchpointMappingRule(
            connector_type="web",
            event_code="web.page_read"
            # No override fields provided
        )
        
        with pytest.raises(ValidationError) as exc_info:
            rule.clean()
        
        assert "At least one override field" in str(exc_info.value)
    
    def test_model_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.metadata_test"
        )
        
        assert rule.metadata == {}
        assert isinstance(rule.metadata, dict)
    
    def test_model_metadata_custom(self):
        """Test custom metadata."""
        custom_metadata = {
            "form_type": "lead",
            "campaign_id": "summer2024",
            "custom_field": "value"
        }
        
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.form_submit",
            touchpoint_code="web.lead_form",
            metadata=custom_metadata
        )
        
        assert rule.metadata == custom_metadata
        assert rule.metadata["form_type"] == "lead"
        assert rule.metadata["campaign_id"] == "summer2024"
        assert rule.metadata["custom_field"] == "value"
    
    def test_model_priority_default(self):
        """Test that priority defaults to 100."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.priority_test"
        )
        
        assert rule.priority == 100
    
    def test_model_priority_custom(self):
        """Test custom priority values."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.priority_test",
            priority=500
        )
        
        assert rule.priority == 500
    
    def test_model_is_active_default(self):
        """Test that is_active defaults to True."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.active_test"
        )
        
        assert rule.is_active is True
    
    def test_model_is_active_custom(self):
        """Test custom is_active value."""
        rule = TouchpointMappingRule.objects.create(
            connector_type="web",
            event_code="web.page_read",
            touchpoint_code="web.inactive_test",
            is_active=False
        )
        
        assert rule.is_active is False
    
    def test_model_indexes(self):
        """Test that the model has the expected indexes."""
        # This test verifies that the indexes are defined in the Meta class
        # The actual index creation is tested by Django's migration system
        
        meta = TouchpointMappingRule._meta
        index_fields = [index.fields for index in meta.indexes]
        
        expected_indexes = [
            ['connector_type', 'event_code'],
            ['source_identifier', 'event_code'],
            ['priority'],
            ['is_active']
        ]
        
        for expected_index in expected_indexes:
            assert expected_index in index_fields
    
    def test_model_verbose_names(self):
        """Test verbose names for the model."""
        meta = TouchpointMappingRule._meta
        
        assert meta.verbose_name == "Touchpoint Mapping Rule"
        assert meta.verbose_name_plural == "Touchpoint Mapping Rules"
