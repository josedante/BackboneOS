"""
Tests for the websites app resolvers.

This module tests the WebTouchpointResolver and its three-dimensional
classification logic.
"""

from django.test import TestCase
from unittest.mock import Mock, patch

from interactions.models import Channel, Medium, TouchpointType, Touchpoint
from our_institution.models import Division, OurOrganization
from products.models import Product
from websites.models import Website, WebInteraction
from websites.resolvers import WebTouchpointResolver, CachedWebTouchpointResolver
from connectors.protocols import TouchpointHint


class WebTouchpointResolverTestCase(TestCase):
    """Test cases for the WebTouchpointResolver."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.resolver = WebTouchpointResolver()
    
    def test_connector_type(self):
        """Test connector type identification."""
        subject = Mock()
        connector_type = self.resolver._get_connector_type(subject)
        self.assertEqual(connector_type, 'web')
    
    def test_channel_display_name_mapping(self):
        """Test channel display name mapping."""
        # Test known channels
        self.assertEqual(
            self.resolver._get_channel_display_name('google'),
            'Google'
        )
        self.assertEqual(
            self.resolver._get_channel_display_name('facebook'),
            'Facebook'
        )
        self.assertEqual(
            self.resolver._get_channel_display_name('twitter'),
            'Twitter'
        )
        self.assertEqual(
            self.resolver._get_channel_display_name('linkedin'),
            'LinkedIn'
        )
        self.assertEqual(
            self.resolver._get_channel_display_name('email'),
            'Email'
        )
    
    def test_channel_display_name_domain_patterns(self):
        """Test channel display name for domain patterns."""
        # Test .com domains
        self.assertEqual(
            self.resolver._get_channel_display_name('alpha.com'),
            'Alpha.com Website'
        )
        
        # Test .edu.pe domains
        self.assertEqual(
            self.resolver._get_channel_display_name('esan.edu.pe'),
            'ESAN University'
        )
        
        # Test .edu domains
        self.assertEqual(
            self.resolver._get_channel_display_name('harvard.edu'),
            'Harvard University'
        )
    
    def test_channel_display_name_fallback(self):
        """Test channel display name fallback."""
        # Test unknown channel
        self.assertEqual(
            self.resolver._get_channel_display_name('unknown_channel'),
            'Unknown Channel'
        )
    
    def test_determine_channel_from_website_url(self):
        """Test channel determination from website URL."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'website_url': 'https://esan.edu.pe/contact',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'esan.edu.pe')
    
    def test_determine_channel_from_current_url(self):
        """Test channel determination from current URL."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'current_url': 'https://alpha.com/products',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'alpha.com')
    
    def test_determine_channel_from_page_url(self):
        """Test channel determination from page URL."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'page_url': 'https://test.com/about',
                'event_type': 'page_view'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'test.com')
    
    def test_determine_channel_default(self):
        """Test channel determination default fallback."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'web')
    
    def test_determine_medium_from_utm(self):
        """Test medium determination from UTM parameters."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'utm_medium': 'social',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'social')
    
    def test_determine_medium_from_google_referrer(self):
        """Test medium determination from Google referrer."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://www.google.com/search?q=test',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'organic')
    
    def test_determine_medium_from_facebook_referrer(self):
        """Test medium determination from Facebook referrer."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://www.facebook.com/some-post',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'social')
    
    def test_determine_medium_from_email_referrer(self):
        """Test medium determination from email referrer."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://mail.google.com/mail/u/0/',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'email')
    
    def test_determine_medium_from_other_referrer(self):
        """Test medium determination from other referrer."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'referrer_url': 'https://example.com/some-page',
                'event_type': 'page_view'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'referral')
    
    def test_determine_medium_default(self):
        """Test medium determination default fallback."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'direct')
    
    def test_touchpoint_type_page_view(self):
        """Test touchpoint type for page view."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'page_view'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_page')
    
    def test_touchpoint_type_form_submit(self):
        """Test touchpoint type for form submit."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'form_submit'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_form')
    
    def test_touchpoint_type_link_click(self):
        """Test touchpoint type for link click."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'a.cta-link'
            }
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'link')
    
    def test_touchpoint_type_button_click(self):
        """Test touchpoint type for button click."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'event_type': 'click',
                'selector': 'button.submit-btn'
            }
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'button')
    
    def test_touchpoint_type_click_default(self):
        """Test touchpoint type for click without selector."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'click'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'link')
    
    def test_touchpoint_type_download(self):
        """Test touchpoint type for download."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'download'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_download')
    
    def test_touchpoint_type_purchase(self):
        """Test touchpoint type for purchase."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'purchase'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_purchase')
    
    def test_touchpoint_type_default(self):
        """Test touchpoint type default fallback."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={'event_type': 'unknown_event'}
        )
        
        touchpoint_type = self.resolver._get_enhanced_touchpoint_class_code(hint)
        self.assertEqual(touchpoint_type, 'web_page')
    
    def test_complete_touchpoint_creation(self):
        """Test complete touchpoint creation with three dimensions."""
        hint = TouchpointHint(
            code="test_interaction",
            channel_code="esan.edu.pe",
            medium_code="organic",
            metadata={
                'event_type': 'page_view',
                'website_url': 'https://esan.edu.pe/contact'
            }
        )
        
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify three dimensions
        self.assertEqual(touchpoint.channel.code, 'esan.edu.pe')
        self.assertEqual(touchpoint.medium.code, 'organic')
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
    
    def test_medium_priority_logic(self):
        """Test medium determination priority logic."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'utm_medium': 'paid',
                'referrer_url': 'https://www.google.com/search'
            }
        )
        
        medium_code = self.resolver._determine_medium_from_subject(hint)
        self.assertEqual(medium_code, 'paid')  # UTM should win
    
    def test_channel_priority_logic(self):
        """Test channel determination priority logic."""
        hint = TouchpointHint(
            code="test_interaction",
            metadata={
                'website_url': 'https://esan.edu.pe/contact',
                'current_url': 'https://alpha.com/products'
            }
        )
        
        channel_code = self.resolver._determine_channel_from_subject(hint)
        self.assertEqual(channel_code, 'esan.edu.pe')  # website_url should win


class CachedWebTouchpointResolverTestCase(TestCase):
    """Test cases for the CachedWebTouchpointResolver."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = OurOrganization.objects.create(
            name="Test Organization"
        )
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST_DIV",
            organization=self.organization
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.resolver = CachedWebTouchpointResolver(use_cache=True)
    
    def test_cached_resolver_creation(self):
        """Test cached resolver creation."""
        self.assertTrue(self.resolver.use_cache)
        self.assertIsNotNone(self.resolver._external_click_cache)
        self.assertIsNotNone(self.resolver._external_referrer_cache)
        self.assertIsNotNone(self.resolver._website_channel_cache)
    
    def test_cache_functionality(self):
        """Test cache functionality."""
        # Test that cache is used when enabled
        subject = Mock()
        subject.website = self.website
        
        # First call should populate cache
        result1 = self.resolver._get_website_channel_code(subject)
        
        # Second call should use cache
        result2 = self.resolver._get_website_channel_code(subject)
        
        self.assertEqual(result1, result2)
        self.assertIn('test.com', result1)
    
    def test_cache_disabled(self):
        """Test cache functionality when disabled."""
        resolver = CachedWebTouchpointResolver(use_cache=False)
        self.assertFalse(resolver.use_cache)
        
        # Should not use cache
        subject = Mock()
        subject.website = self.website
        
        result = resolver._get_website_channel_code(subject)
        self.assertIn('test.com', result)
    
    def test_cache_key_creation(self):
        """Test cache key creation."""
        subject = Mock()
        subject.website = self.website
        subject.session_id = "test_session"
        subject.visitor_cookie = "test_cookie"
        
        cache_key = self.resolver._create_subject_cache_key(subject)
        self.assertIsInstance(cache_key, str)
        self.assertIn('test.com', cache_key)
        self.assertIn('test_session', cache_key)
        self.assertIn('test_cookie', cache_key)
