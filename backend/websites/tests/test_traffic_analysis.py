"""
Tests for traffic analysis functionality in PageViewEventProcessor.

This module tests the _get_or_create_traffic_channel_and_medium method
to ensure it correctly differentiates traffic sources as expected by the tests.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch

from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage
from websites.processors import PageViewEventProcessor
from websites.mapping_providers import WebMappingProvider, CachedWebMappingProvider

User = get_user_model()


class TrafficAnalysisTestCase(TestCase):
    """Test cases for traffic analysis in PageViewEventProcessor."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.our_organization = OurOrganization.objects.create(
            name='Test Organization',
            legal_name='Test Organization Legal',
            is_active=True
        )
        self.division = Division.objects.create(
            organization=self.our_organization,
            name='Test Division',
            code='TEST',
            description='Test division for testing'
        )
        self.website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com',
        )
    
    def test_utm_priority_analysis(self):
        """Test that UTM parameters take priority in medium detection."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': 'email',
            'utm_source': 'newsletter',
            'utm_campaign': 'welcome',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.google.com',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'email')
        self.assertEqual(channel.code, 'email')
        self.assertEqual(medium.name, 'Email Marketing')
        self.assertEqual(channel.name, 'Email')
    
    def test_referrer_analysis(self):
        """Test referrer analysis when no UTM parameters."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.facebook.com/some-post',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'social')
        self.assertEqual(channel.code, 'facebook')
        self.assertEqual(medium.name, 'Social Media')
        self.assertEqual(channel.name, 'Facebook')
    
    def test_user_agent_analysis(self):
        """Test user agent analysis for native app detection."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'SubstackApp/1.0 (iPhone; iOS 15.0)',
            'referrer': None,
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'mobile')
        self.assertEqual(channel.code, 'substack')
        self.assertEqual(medium.name, 'Mobile App')
        self.assertEqual(channel.name, 'Substack')
    
    def test_direct_fallback(self):
        """Test direct traffic fallback when no other indicators."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': None,
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'web_direct')
        self.assertEqual(channel.code, 'example.com')
        self.assertEqual(medium.name, 'Direct Traffic')
        self.assertEqual(channel.name, 'Example.com Website')
    
    def test_google_search_referrer(self):
        """Test Google search referrer analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.google.com/search?q=test',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'organic')
        self.assertEqual(channel.code, 'google')
        self.assertEqual(medium.name, 'Organic Search')
        self.assertEqual(channel.name, 'Google')
    
    def test_twitter_referrer(self):
        """Test Twitter referrer analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://twitter.com/some-post',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'social')
        self.assertEqual(channel.code, 'twitter')
        self.assertEqual(medium.name, 'Social Media')
        self.assertEqual(channel.name, 'Twitter')
    
    def test_linkedin_referrer(self):
        """Test LinkedIn referrer analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.linkedin.com/feed/',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'social')
        self.assertEqual(channel.code, 'linkedin')
        self.assertEqual(medium.name, 'Social Media')
        self.assertEqual(channel.name, 'LinkedIn')
    
    def test_paid_utm_medium(self):
        """Test paid UTM medium analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': 'cpc',
            'utm_source': 'google',
            'utm_campaign': 'brand_campaign',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.google.com',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'paid')
        self.assertEqual(channel.code, 'google')
        self.assertEqual(medium.name, 'Paid Advertising')
        self.assertEqual(channel.name, 'Google')
    
    def test_organic_utm_medium(self):
        """Test organic UTM medium analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': 'organic',
            'utm_source': 'google',
            'utm_campaign': 'seo_campaign',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.google.com',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'organic')
        self.assertEqual(channel.code, 'google')
        self.assertEqual(medium.name, 'Organic Search')
        self.assertEqual(channel.name, 'Google')
    
    def test_social_utm_medium(self):
        """Test social UTM medium analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': 'social',
            'utm_source': 'facebook',
            'utm_campaign': 'social_campaign',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.facebook.com',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'social')
        self.assertEqual(channel.code, 'facebook')
        self.assertEqual(medium.name, 'Social Media')
        self.assertEqual(channel.name, 'Facebook')
    
    def test_mobile_app_user_agent(self):
        """Test mobile app user agent analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'ESANApp/2.0 (iPhone; iOS 16.0)',
            'referrer': None,
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'mobile')
        self.assertEqual(channel.code, 'esan_app')
        self.assertEqual(medium.name, 'Mobile App')
        self.assertEqual(channel.name, 'ESAN App')
    
    def test_webview_user_agent(self):
        """Test WebView user agent analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 wv)',
            'referrer': None,
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'mobile')
        self.assertEqual(channel.code, 'webview')
        self.assertEqual(medium.name, 'Mobile App')
        self.assertEqual(channel.name, 'WebView')
    
    def test_touchpoint_class_mapping(self):
        """Test touchpoint class mapping based on medium."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': 'social',
            'utm_source': 'facebook',
            'utm_campaign': 'social_campaign',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.facebook.com',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        # Test touchpoint class code mapping
        touchpoint_class_code = processor._get_traffic_touchpoint_class_code(medium.code)
        self.assertEqual(touchpoint_class_code, 'web.social_traffic')
        
        # Test touchpoint class name mapping
        touchpoint_class_name = processor._get_traffic_touchpoint_class_name(touchpoint_class_code)
        self.assertEqual(touchpoint_class_name, 'Social Media Traffic')
    
    def test_internal_referrer_analysis(self):
        """Test internal referrer analysis."""
        event_data = {
            'website_base': 'https://www.example.com',
            'utm_medium': '',
            'utm_source': '',
            'utm_campaign': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer': 'https://www.example.com/internal-page',
            'session_id': 'test-session',
            'payload': {},
            'metadata': {}
        }
        
        processor = PageViewEventProcessor(event_data)
        channel, medium = processor._get_or_create_traffic_channel_and_medium()
        
        self.assertEqual(medium.code, 'owned_website')
        self.assertEqual(channel.code, 'example.com')
        self.assertEqual(medium.name, 'Owned Website')
        self.assertEqual(channel.name, 'Example.com Website')
    
    def test_all_medium_mappings(self):
        """Test all medium code mappings."""
        medium_tests = [
            ('paid', 'web.paid_traffic', 'Paid Advertising Traffic'),
            ('email', 'web.email_traffic', 'Email Marketing Traffic'),
            ('social', 'web.social_traffic', 'Social Media Traffic'),
            ('referral', 'web.referral_traffic', 'Referral Traffic'),
            ('organic', 'web.organic_traffic', 'Organic Search Traffic'),
            ('display', 'web.display_traffic', 'Display Advertising Traffic'),
            ('video', 'web.video_traffic', 'Video Advertising Traffic'),
            ('mobile', 'web.mobile_traffic', 'Mobile App Traffic'),
            ('affiliate', 'web.affiliate_traffic', 'Affiliate Marketing Traffic'),
            ('content', 'web.content_traffic', 'Content Marketing Traffic'),
            ('web_direct', 'web.direct_traffic', 'Direct Traffic'),
        ]
        
        processor = PageViewEventProcessor({'website_base': 'https://www.example.com'})
        
        for medium_code, expected_class_code, expected_class_name in medium_tests:
            touchpoint_class_code = processor._get_traffic_touchpoint_class_code(medium_code)
            self.assertEqual(touchpoint_class_code, expected_class_code)
            
            touchpoint_class_name = processor._get_traffic_touchpoint_class_name(touchpoint_class_code)
            self.assertEqual(touchpoint_class_name, expected_class_name)
