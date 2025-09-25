"""
Integration tests for the websites app.

This module tests the complete integration flow of the websites app
with the three-dimensional classification system.
"""

from django.test import TestCase
from django.db import transaction
from unittest.mock import Mock, patch

from interactions.models import Channel, Medium, TouchpointType, Touchpoint, Agent, Action, Interaction
from our_institution.models import Division, OurOrganization
from products.models import Product
from websites.models import Website, WebInteraction, WebSurface
from websites.resolvers import WebTouchpointResolver
from websites.adapters import infer_web_touchpoint_hint


class WebsitesIntegrationTestCase(TestCase):
    """Integration test cases for the websites app."""
    
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
        self.resolver = WebTouchpointResolver()
    
    def test_complete_web_interaction_flow(self):
        """Test complete web interaction flow with three-dimensional classification."""
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            user_agent="Mozilla/5.0 (Test Browser)",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="test_campaign",
            referrer_url="https://www.google.com/search?q=test",
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        # Test touchpoint hint inference
        hint = infer_web_touchpoint_hint(web_interaction)
        
        # Verify hint properties
        self.assertEqual(hint.medium_code, 'organic')
        self.assertIsNotNone(hint.metadata)
        self.assertEqual(hint.metadata['event_type'], 'page_view')
        self.assertEqual(hint.metadata['website_url'], 'https://test.com/contact')
        
        # Test touchpoint creation
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify three-dimensional classification
        self.assertEqual(touchpoint.channel.code, 'test.com')  # WHERE
        self.assertEqual(touchpoint.medium.code, 'organic')     # HOW
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')  # WHAT
        
        # Test that touchpoint is properly linked
        self.assertIsNotNone(touchpoint.channel)
        self.assertIsNotNone(touchpoint.medium)
        self.assertIsNotNone(touchpoint.touchpoint_type)
    
    def test_form_submit_flow(self):
        """Test form submit interaction flow."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            utm_source="facebook",
            utm_medium="social",
            utm_campaign="summer_sale",
            payload={
                'event_type': 'form_submit',
                'form_id': 'contact_form',
                'url': 'https://test.com/contact'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify classification
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.medium.code, 'social')
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_form')
    
    def test_click_interaction_flow(self):
        """Test click interaction flow with smart classification."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            element="button.submit-btn",
            payload={
                'event_type': 'click',
                'selector': 'button.submit-btn',
                'url': 'https://test.com/contact'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify classification
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.medium.code, 'direct')  # No UTM or referrer
        self.assertEqual(touchpoint.touchpoint_type.code, 'button')  # Smart classification
    
    def test_link_click_interaction_flow(self):
        """Test link click interaction flow."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            element="a.cta-link",
            payload={
                'event_type': 'click',
                'selector': 'a.cta-link',
                'url': 'https://test.com/contact'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify classification
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.medium.code, 'direct')
        self.assertEqual(touchpoint.touchpoint_type.code, 'link')  # Smart classification
    
    def test_download_interaction_flow(self):
        """Test download interaction flow."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            utm_source="email",
            utm_medium="email",
            utm_campaign="newsletter",
            payload={
                'event_type': 'download',
                'file_name': 'brochure.pdf',
                'url': 'https://test.com/downloads'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify classification
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.medium.code, 'email')
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_download')
    
    def test_purchase_interaction_flow(self):
        """Test purchase interaction flow."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            session_id="test_session_123",
            visitor_cookie="test_cookie_456",
            utm_source="google",
            utm_medium="paid",
            utm_campaign="product_launch",
            payload={
                'event_type': 'purchase',
                'order_id': 'ORD-123',
                'amount': 99.99,
                'url': 'https://test.com/checkout'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify classification
        self.assertEqual(touchpoint.channel.code, 'test.com')
        self.assertEqual(touchpoint.medium.code, 'paid')
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_purchase')
    
    def test_utm_priority_logic(self):
        """Test UTM parameter priority logic."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            utm_medium="paid",
            referrer_url="https://www.google.com/search",
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # UTM medium should have priority over referrer analysis
        self.assertEqual(touchpoint.medium.code, 'paid')
    
    def test_channel_priority_logic(self):
        """Test channel determination priority logic."""
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact',
                'website_url': 'https://test.com/contact',
                'current_url': 'https://alpha.com/products'
            }
        )
        
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # website_url should have priority over current_url
        self.assertEqual(touchpoint.channel.code, 'test.com')
    
    def test_multiple_interactions_same_session(self):
        """Test multiple interactions in the same session."""
        session_id = "test_session_123"
        visitor_cookie = "test_cookie_456"
        
        # Create multiple interactions
        interactions = []
        for i in range(3):
            interaction = WebInteraction.objects.create(
                website=self.website,
                session_id=session_id,
                visitor_cookie=visitor_cookie,
                payload={
                    'event_type': 'page_view',
                    'url': f'https://test.com/page{i}'
                }
            )
            interactions.append(interaction)
        
        # Test that all interactions get proper classification
        for interaction in interactions:
            hint = infer_web_touchpoint_hint(interaction)
            touchpoint = self.resolver._get_or_create_touchpoint(hint)
            
            self.assertEqual(touchpoint.channel.code, 'test.com')
            self.assertEqual(touchpoint.medium.code, 'direct')
            self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
    
    def test_different_websites_different_channels(self):
        """Test that different websites get different channels."""
        # Create second website
        website2 = Website.objects.create(
            name="Test Website 2",
            base_url="https://test2.com",
            division=self.division
        )
        
        # Create interactions for both websites
        interaction1 = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/contact'
            }
        )
        
        interaction2 = WebInteraction.objects.create(
            website=website2,
            payload={
                'event_type': 'page_view',
                'url': 'https://test2.com/contact'
            }
        )
        
        # Test touchpoint creation
        hint1 = infer_web_touchpoint_hint(interaction1)
        touchpoint1 = self.resolver._get_or_create_touchpoint(hint1)
        
        hint2 = infer_web_touchpoint_hint(interaction2)
        touchpoint2 = self.resolver._get_or_create_touchpoint(hint2)
        
        # Verify different channels
        self.assertEqual(touchpoint1.channel.code, 'test.com')
        self.assertEqual(touchpoint2.channel.code, 'test2.com')
    
    def test_analytics_capabilities(self):
        """Test analytics capabilities with three-dimensional classification."""
        # Create touchpoints with different dimensions
        touchpoints = []
        
        # Different channels
        for channel_code in ['test.com', 'alpha.com', 'beta.com']:
            channel = Channel.objects.create(
                name=f"{channel_code} Channel",
                code=channel_code
            )
            
            # Different mediums
            for medium_code in ['organic', 'social', 'paid']:
                medium = Medium.objects.create(
                    name=f"{medium_code.title()} Medium",
                    code=medium_code
                )
                
                # Different touchpoint types
                for touchpoint_type_code in ['web_page', 'web_form', 'link']:
                    touchpoint_type = TouchpointType.objects.create(
                        name=f"{touchpoint_type_code.title()} Type",
                        code=touchpoint_type_code
                    )
                    
                    touchpoint = Touchpoint.objects.create(
                        name=f"Touchpoint {channel_code} {medium_code} {touchpoint_type_code}",
                        channel=channel,
                        medium=medium,
                        touchpoint_type=touchpoint_type
                    )
                    touchpoints.append(touchpoint)
        
        # Test filtering by channel
        test_com_touchpoints = Touchpoint.objects.filter(channel__code='test.com')
        self.assertEqual(test_com_touchpoints.count(), 9)  # 3 mediums × 3 types
        
        # Test filtering by medium
        organic_touchpoints = Touchpoint.objects.filter(medium__code='organic')
        self.assertEqual(organic_touchpoints.count(), 9)  # 3 channels × 3 types
        
        # Test filtering by touchpoint type
        web_page_touchpoints = Touchpoint.objects.filter(touchpoint_type__code='web_page')
        self.assertEqual(web_page_touchpoints.count(), 9)  # 3 channels × 3 mediums
        
        # Test filtering by combination
        test_com_organic_touchpoints = Touchpoint.objects.filter(
            channel__code='test.com',
            medium__code='organic'
        )
        self.assertEqual(test_com_organic_touchpoints.count(), 3)  # 3 types
        
        # Test filtering by all three dimensions
        specific_touchpoints = Touchpoint.objects.filter(
            channel__code='test.com',
            medium__code='organic',
            touchpoint_type__code='web_page'
        )
        self.assertEqual(specific_touchpoints.count(), 1)
    
    def test_no_overlap_with_action_field(self):
        """Test that TouchpointType doesn't overlap with Action field."""
        # Create touchpoint with web-specific type
        channel = Channel.objects.create(name="Test Channel", code="test.com")
        medium = Medium.objects.create(name="Test Medium", code="direct")
        touchpoint_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        
        touchpoint = Touchpoint.objects.create(
            name="Test Touchpoint",
            channel=channel,
            medium=medium,
            touchpoint_type=touchpoint_type
        )
        
        # Verify touchpoint type is web-specific
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
        
        # Verify it doesn't conflict with action codes
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'page_view')
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'form_submit')
        self.assertNotEqual(touchpoint.touchpoint_type.code, 'click')
    
    def test_web_surface_integration(self):
        """Test integration with WebSurface model."""
        # Create touchpoint type
        touchpoint_type = TouchpointType.objects.create(
            name="Web Page",
            code="web_page"
        )
        
        # Create web surface
        web_surface = WebSurface.objects.create(
            website=self.website,
            path="/test-page",
            title="Test Page",
            touchpoint_class=touchpoint_type
        )
        
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={
                'event_type': 'page_view',
                'url': 'https://test.com/test-page'
            }
        )
        
        # Test touchpoint hint inference
        hint = infer_web_touchpoint_hint(web_interaction)
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        
        # Verify touchpoint type matches web surface
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
        self.assertEqual(web_surface.touchpoint_class.code, 'web_page')
    
    def test_error_handling(self):
        """Test error handling in the integration flow."""
        # Test with invalid data
        web_interaction = WebInteraction.objects.create(
            website=self.website,
            payload={'event_type': 'invalid_event'}
        )
        
        # Should not raise exception
        hint = infer_web_touchpoint_hint(web_interaction)
        self.assertIsNotNone(hint)
        
        # Should use default values
        touchpoint = self.resolver._get_or_create_touchpoint(hint)
        self.assertEqual(touchpoint.touchpoint_type.code, 'web_page')
        self.assertEqual(touchpoint.medium.code, 'direct')
        self.assertEqual(touchpoint.channel.code, 'web')
    
    def test_performance_with_large_dataset(self):
        """Test performance with a large dataset."""
        # Create many touchpoints
        touchpoints = []
        for i in range(100):
            channel = Channel.objects.create(
                name=f"Channel {i}",
                code=f"channel_{i}"
            )
            medium = Medium.objects.create(
                name=f"Medium {i}",
                code=f"medium_{i}"
            )
            touchpoint_type = TouchpointType.objects.create(
                name=f"Type {i}",
                code=f"type_{i}"
            )
            
            touchpoint = Touchpoint.objects.create(
                name=f"Touchpoint {i}",
                channel=channel,
                medium=medium,
                touchpoint_type=touchpoint_type
            )
            touchpoints.append(touchpoint)
        
        # Test query performance
        with self.assertNumQueries(1):  # Should be efficient
            Touchpoint.objects.filter(
                channel__code='channel_50',
                medium__code='medium_50'
            ).count()
        
        # Test complex filtering
        with self.assertNumQueries(1):  # Should be efficient
            Touchpoint.objects.filter(
                channel__code__in=['channel_10', 'channel_20', 'channel_30'],
                medium__code__in=['medium_10', 'medium_20'],
                touchpoint_type__code='type_10'
            ).count()
