"""
Mapping provider tests for the websites app.

This module tests the WebMappingProvider and CachedWebMappingProvider classes.
"""

from django.test import TestCase
from unittest.mock import Mock
from connectors.protocols import TouchpointHint
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider


class WebMappingProviderTest(TestCase):
    """Test cases for the WebMappingProvider."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = WebMappingProvider()
    
    def test_lookup_mapping(self):
        """Test mapping rule lookup."""
        # Create a mock subject and hint
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        
        # Test lookup (should return None since no rules exist)
        rule = self.provider.lookup_mapping(mock_subject, hint)
        self.assertIsNone(rule)  # No rules in test database
    
    def test_get_connector_type(self):
        """Test connector type extraction."""
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        connector_type = self.provider._get_connector_type(mock_subject)
        self.assertEqual(connector_type, 'web')
    
    def test_get_source_identifier(self):
        """Test source identifier extraction."""
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        source_id = self.provider._get_source_identifier(mock_subject)
        self.assertEqual(source_id, 'https://www.example.com')


class CachedWebMappingProviderTest(TestCase):
    """Test cases for the CachedWebMappingProvider."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = CachedWebMappingProvider()
    
    def test_caching_functionality(self):
        """Test that caching works correctly."""
        # Create a mock subject and hint
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        
        # First lookup should populate cache
        rule1 = self.provider.lookup_mapping(mock_subject, hint)
        
        # Second lookup should use cache
        rule2 = self.provider.lookup_mapping(mock_subject, hint)
        
        # Both should return the same result
        self.assertEqual(rule1, rule2)
        self.assertIsNone(rule1)  # No rules in test database
    
    def test_cache_invalidation(self):
        """Test cache invalidation functionality."""
        # Create a mock subject and hint
        mock_subject = Mock()
        mock_subject.website = Mock()
        mock_subject.website.base_url = 'https://www.example.com'
        
        hint = TouchpointHint(code='web.page_view', label='Page View')
        
        # Populate cache
        self.provider.lookup_mapping(mock_subject, hint)
        
        # Clear cache
        self.provider.clear_cache()
        
        # Cache should be empty
        self.assertEqual(len(self.provider._source_normalization_cache), 0)
        self.assertEqual(len(self.provider._domain_extraction_cache), 0)
