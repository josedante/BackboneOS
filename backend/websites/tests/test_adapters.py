"""
Tests for the websites app adapters.

This module tests the web touchpoint inference adapters and their
integration with the three-dimensional classification system.
"""

from django.test import TestCase
from unittest.mock import Mock, patch

from interactions.models import Channel, Medium, TouchpointType, Touchpoint, Agent, Action
from our_institution.models import Division, OurOrganization
from products.models import Product
from websites.models import Website, WebInteraction
from websites.adapters import (
    infer_web_touchpoint_hint,
    _determine_event_type,
    _map_event_type_to_code,
    _create_touchpoint_label,
    _analyze_utm_medium,
    _build_metadata
)
from connectors.protocols import TouchpointHint


class WebTouchpointAdapterTestCase(TestCase):
    """Test cases for the web touchpoint adapter."""
    
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
        self.agent = Agent.objects.create(
            agent_type="browser",
            name="Test Browser",
            identifier="test_browser_123"
        )
        self.action = Action.objects.create(
            name="Page View",
            code="page_view"
        )
    
    def test_infer_web_touchpoint_hint_page_view(self):
        """Test touchpoint hint inference for page view."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            user_agent="Mozilla/5.0 (Test Browser)",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.medium_code, 'organic')
        self.assertIsNotNone(hint.metadata)
        self.assertIn('event_type', hint.metadata)
        self.assertEqual(hint.metadata['event_type'], 'page_view')
    
    def test_infer_web_touchpoint_hint_form_submit(self):
        """Test touchpoint hint inference for form submit."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            utm_source="facebook",
            utm_medium="social",
            utm_campaign="test_campaign",
            payload={
                'event_type': 'form_submit',
                'form_id': 'contact_form'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        self.assertEqual(hint.medium_code, 'social')
        self.assertEqual(hint.metadata['event_type'], 'form_submit')
        self.assertIn('form_id', hint.metadata)
    
    def test_infer_web_touchpoint_hint_click(self):
        """Test touchpoint hint inference for click."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            element="button.submit-btn",
            payload={
                'event_type': 'click',
                'selector': 'button.submit-btn'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        self.assertEqual(hint.metadata['event_type'], 'click')
        self.assertIn('selector', hint.metadata)
        self.assertEqual(hint.metadata['selector'], 'button.submit-btn')
    
    def test_infer_web_touchpoint_hint_download(self):
        """Test touchpoint hint inference for download."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            payload={
                'event_type': 'download',
                'file_name': 'brochure.pdf'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        self.assertEqual(hint.metadata['event_type'], 'download')
        self.assertIn('file_name', hint.metadata)
        self.assertEqual(hint.metadata['file_name'], 'brochure.pdf')
    
    def test_infer_web_touchpoint_hint_purchase(self):
        """Test touchpoint hint inference for purchase."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            payload={
                'event_type': 'purchase',
                'order_id': 'ORD-123',
                'amount': 99.99
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        self.assertEqual(hint.metadata['event_type'], 'purchase')
        self.assertIn('order_id', hint.metadata)
        self.assertEqual(hint.metadata['order_id'], 'ORD-123')
        self.assertEqual(hint.metadata['amount'], 99.99)
    
    def test_determine_event_type_from_payload(self):
        """Test event type determination from payload."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={'event_type': 'page_view'}
        )
        
        event_type = _determine_event_type(web_interaction)
        self.assertEqual(event_type, 'page_view')
    
    def test_determine_event_type_from_element(self):
        """Test event type determination from element."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            element="button.submit-btn"
        )
        
        event_type = _determine_event_type(web_interaction)
        self.assertEqual(event_type, 'click')
    
    def test_determine_event_type_default(self):
        """Test event type determination default."""
        web_interaction = WebInteraction.objects.create(
            website=self.website
        )
        
        event_type = _determine_event_type(web_interaction)
        self.assertEqual(event_type, 'page_view')
    
    def test_map_event_type_to_code(self):
        """Test event type to code mapping."""
        # Test page view
        code = _map_event_type_to_code('page_view')
        self.assertEqual(code, 'page_view')
        
        # Test form submit
        code = _map_event_type_to_code('form_submit')
        self.assertEqual(code, 'form_submit')
        
        # Test click
        code = _map_event_type_to_code('click')
        self.assertEqual(code, 'click')
        
        # Test download
        code = _map_event_type_to_code('download')
        self.assertEqual(code, 'download')
        
        # Test purchase
        code = _map_event_type_to_code('purchase')
        self.assertEqual(code, 'purchase')
    
    def test_create_touchpoint_label_page_view(self):
        """Test touchpoint label creation for page view."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={'event_type': 'page_view'}
        )
        
        label = _create_touchpoint_label('page_view', web_interaction)
        self.assertIn('Page View', label)
    
    def test_create_touchpoint_label_form_submit(self):
        """Test touchpoint label creation for form submit."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'form_submit',
                'form_id': 'contact_form'
            }
        )
        
        label = _create_touchpoint_label('form_submit', web_interaction)
        self.assertIn('Form Submit', label)
        self.assertIn('contact_form', label)
    
    def test_create_touchpoint_label_click(self):
        """Test touchpoint label creation for click."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            element="button.submit-btn",
            payload={'event_type': 'click'}
        )
        
        label = _create_touchpoint_label('click', web_interaction)
        self.assertIn('Click', label)
        self.assertIn('button.submit-btn', label)
    
    def test_analyze_utm_medium_from_utm_medium(self):
        """Test UTM medium analysis from utm_medium field."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            utm_medium="social"
        )
        
        medium = _analyze_utm_medium(web_interaction)
        self.assertEqual(medium, 'social')
    
    def test_analyze_utm_medium_from_payload(self):
        """Test UTM medium analysis from payload."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={'utm_medium': 'organic'}
        )
        
        medium = _analyze_utm_medium(web_interaction)
        self.assertEqual(medium, 'organic')
    
    def test_analyze_utm_medium_from_referrer(self):
        """Test UTM medium analysis from referrer."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            referrer_url="https://www.google.com/search"
        )
        
        medium = _analyze_utm_medium(web_interaction)
        self.assertEqual(medium, 'organic')
    
    def test_analyze_utm_medium_from_facebook_referrer(self):
        """Test UTM medium analysis from Facebook referrer."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            referrer_url="https://www.facebook.com/some-post"
        )
        
        medium = _analyze_utm_medium(web_interaction)
        self.assertEqual(medium, 'social')
    
    def test_analyze_utm_medium_default(self):
        """Test UTM medium analysis default."""
        web_interaction = WebInteraction.objects.create(
            website=self.website
        )
        
        medium = _analyze_utm_medium(web_interaction)
        self.assertEqual(medium, 'direct')
    
    def test_build_metadata_basic(self):
        """Test basic metadata building."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            user_agent="Mozilla/5.0 (Test Browser)",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            payload={'event_type': 'page_view'}
        )
        
        metadata = _build_metadata(web_interaction, 'page_view')
        
        self.assertEqual(metadata['event_type'], 'page_view')
        self.assertEqual(metadata['session_id'], 'test_session_123')
        self.assertEqual(metadata['visitor_cookie'], 'test_cookie_456')
        self.assertEqual(metadata['user_agent'], 'Mozilla/5.0 (Test Browser)')
        self.assertEqual(metadata['utm_source'], 'google')
        self.assertEqual(metadata['utm_medium'], 'organic')
        self.assertEqual(metadata['utm_campaign'], 'test_campaign')
    
    def test_build_metadata_with_referrer(self):
        """Test metadata building with referrer."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            referrer_url="https://www.google.com/search",
            payload={'event_type': 'page_view'}
        )
        
        metadata = _build_metadata(web_interaction, 'page_view')
        
        self.assertEqual(metadata['referrer_url'], 'https://www.google.com/search')
    
    def test_build_metadata_with_element(self):
        """Test metadata building with element."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            element="button.submit-btn",
            payload={'event_type': 'click'}
        )
        
        metadata = _build_metadata(web_interaction, 'click')
        
        self.assertEqual(metadata['element'], 'button.submit-btn')
    
    def test_build_metadata_with_payload(self):
        """Test metadata building with payload data."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'form_submit',
                'form_id': 'contact_form',
                'custom_field': 'custom_value'
            }
        )
        
        metadata = _build_metadata(web_interaction, 'form_submit')
        
        self.assertEqual(metadata['event_type'], 'form_submit')
        self.assertEqual(metadata['form_id'], 'contact_form')
        self.assertEqual(metadata['custom_field'], 'custom_value')
    
    def test_build_metadata_with_website_url(self):
        """Test metadata building with website URL."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        metadata = _build_metadata(web_interaction, 'page_view')
        
        self.assertEqual(metadata['website_url'], 'https://test.com/contact')
        self.assertEqual(metadata['current_url'], 'https://test.com/contact')
        self.assertEqual(metadata['page_url'], 'https://test.com/contact')
    
    def test_infer_web_touchpoint_hint_complete_flow(self):
        """Test complete touchpoint hint inference flow."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            user_agent="Mozilla/5.0 (Test Browser)",
            utm_source="facebook",
            utm_medium="social",
            utm_campaign="summer_sale",
            utm_content="banner_ad",
            utm_term="shoes",
            referrer_url="https://www.facebook.com/some-post",
            element="button.cta-btn",
            payload={
                'event_type': 'click',
                'selector': 'button.cta-btn',
                'url': 'https://test.com/products'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        
        # Verify hint properties
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.medium_code, 'social')
        self.assertIsNone(hint.channel_code)  # Should be determined by resolver
        
        # Verify metadata
        self.assertEqual(hint.metadata['event_type'], 'click')
        self.assertEqual(hint.metadata['session_id'], 'test_session_123')
        self.assertEqual(hint.metadata['visitor_cookie'], 'test_cookie_456')
        self.assertEqual(hint.metadata['user_agent'], 'Mozilla/5.0 (Test Browser)')
        self.assertEqual(hint.metadata['utm_source'], 'facebook')
        self.assertEqual(hint.metadata['utm_medium'], 'social')
        self.assertEqual(hint.metadata['utm_campaign'], 'summer_sale')
        self.assertEqual(hint.metadata['utm_content'], 'banner_ad')
        self.assertEqual(hint.metadata['utm_term'], 'shoes')
        self.assertEqual(hint.metadata['referrer_url'], 'https://www.facebook.com/some-post')
        self.assertEqual(hint.metadata['element'], 'button.cta-btn')
        self.assertEqual(hint.metadata['selector'], 'button.cta-btn')
        self.assertEqual(hint.metadata['website_url'], 'https://test.com/products')
        self.assertEqual(hint.metadata['current_url'], 'https://test.com/products')
        self.assertEqual(hint.metadata['page_url'], 'https://test.com/products')
