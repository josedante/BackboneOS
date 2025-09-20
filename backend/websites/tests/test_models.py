"""
Model tests for the websites app.

This module tests all model classes in the websites app including:
- Website model
- WebSurface model (including WebForm and WebPage proxy models)
- WebInteraction model
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from entities.models import Organization
from our_institution.models import OurOrganization, Division
from interactions.models import TouchpointClass, Touchpoint, Interaction
from websites.models import Website, WebSurface, WebInteraction, WebForm, WebPage

User = get_user_model()


class WebsiteModelTest(TestCase):
    """Test cases for the Website model."""
    
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
    
    def test_website_creation(self):
        """Test creating a website."""
        website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com'
        )
        
        self.assertEqual(website.name, 'Test Website')
        self.assertEqual(website.base_url, 'https://www.example.com')
        self.assertEqual(website.division, self.division)
        self.assertTrue(website.is_active)
    
    def test_website_str_representation(self):
        """Test string representation of website."""
        website = Website.objects.create(
            division=self.division,
            name='Test Website',
            base_url='https://www.example.com'
        )
        
        self.assertEqual(str(website), 'Test Website (https://www.example.com)')
    
    def test_website_ordering(self):
        """Test website ordering by name."""
        website1 = Website.objects.create(
            division=self.division,
            name='Zebra Website',
            base_url='https://www.zebra.com'
        )
        website2 = Website.objects.create(
            division=self.division,
            name='Alpha Website',
            base_url='https://www.alpha.com'
        )
        
        websites = list(Website.objects.all())
        self.assertEqual(websites[0], website2)  # Alpha should come first
        self.assertEqual(websites[1], website1)  # Zebra should come second


class WebSurfaceModelTest(TestCase):
    """Test cases for the WebSurface model."""
    
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
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page',
            name='Web Page',
            description='A web page touchpoint'
        )
    
    def test_websurface_creation(self):
        """Test creating a web surface."""
        surface = WebSurface.objects.create(
            website=self.website,
            path='/test-page',
            title='Test Page',
            touchpoint_class=self.touchpoint_class
        )
        
        self.assertEqual(surface.website, self.website)
        self.assertEqual(surface.path, '/test-page')
        self.assertEqual(surface.title, 'Test Page')
        self.assertEqual(surface.touchpoint_class, self.touchpoint_class)
        self.assertFalse(surface.is_form)
        self.assertFalse(surface.is_thankyou)
    
    def test_websurface_path_validation(self):
        """Test path validation for web surface."""
        # Valid path
        surface = WebSurface.objects.create(
            website=self.website,
            path='/valid-path',
            title='Valid Page',
            touchpoint_class=self.touchpoint_class
        )
        self.assertEqual(surface.path, '/valid-path')
        
        # Invalid path (doesn't start with /)
        with self.assertRaises(ValidationError):
            surface = WebSurface(
                website=self.website,
                path='invalid-path',  # Missing leading slash
                title='Invalid Page',
                touchpoint_class=self.touchpoint_class
            )
            surface.full_clean()
    
    def test_websurface_proxy_models(self):
        """Test WebForm and WebPage proxy models."""
        # Create a form surface
        form_surface = WebSurface.objects.create(
            website=self.website,
            path='/contact-form',
            title='Contact Form',
            touchpoint_class=self.touchpoint_class,
            is_form=True
        )
        
        # Create a page surface
        page_surface = WebSurface.objects.create(
            website=self.website,
            path='/about',
            title='About Page',
            touchpoint_class=self.touchpoint_class
        )
        
        # Test WebForm proxy model
        web_form = WebForm.objects.get(id=form_surface.id)
        self.assertTrue(web_form.is_form)
        self.assertIsInstance(web_form, WebForm)
        
        # Test WebPage proxy model
        web_page = WebPage.objects.get(id=page_surface.id)
        self.assertFalse(web_page.is_form)
        self.assertIsInstance(web_page, WebPage)


class WebInteractionModelTest(TestCase):
    """Test cases for the WebInteraction model."""
    
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
        self.touchpoint_class = TouchpointClass.objects.create(
            code='web.page',
            name='Web Page',
            description='A web page touchpoint'
        )
        self.touchpoint = Touchpoint.objects.create(
            code='web.test',
            name='Test Touchpoint',
            touchpoint_class=self.touchpoint_class
        )
    
    def test_webinteraction_creation(self):
        """Test creating a web interaction."""
        interaction = Interaction.objects.create(
            touchpoint=self.touchpoint,
            person=None
        )
        
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id='test-session-123',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            ip='192.168.1.1'
        )
        
        self.assertEqual(web_interaction.website, self.website)
        self.assertEqual(web_interaction.session_id, 'test-session-123')
        self.assertEqual(web_interaction.user_agent, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        self.assertEqual(web_interaction.ip, '192.168.1.1')
        self.assertEqual(web_interaction.interaction, interaction)
    
    def test_webinteraction_utm_parameters(self):
        """Test UTM parameter handling."""
        interaction = Interaction.objects.create(
            touchpoint=self.touchpoint,
            person=None
        )
        
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            utm_source='google',
            utm_medium='cpc',
            utm_campaign='summer_sale',
            utm_term='shoes',
            utm_content='banner_ad'
        )
        
        self.assertEqual(web_interaction.utm_source, 'google')
        self.assertEqual(web_interaction.utm_medium, 'cpc')
        self.assertEqual(web_interaction.utm_campaign, 'summer_sale')
        self.assertEqual(web_interaction.utm_term, 'shoes')
        self.assertEqual(web_interaction.utm_content, 'banner_ad')
    
    def test_webinteraction_touchpoint_inference(self):
        """Test touchpoint hint inference."""
        interaction = Interaction.objects.create(
            touchpoint=self.touchpoint,
            person=None
        )
        
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id='test-session-123',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            payload={'event_type': 'page_view', 'page': '/test'}
        )
        
        # Test touchpoint hint inference
        hint = web_interaction.infer_touchpoint_hint()
        self.assertIsNotNone(hint)
        self.assertEqual(hint.code, 'web.page_read')
        self.assertIsNone(hint.channel_code)  # Should be None to let resolver determine
        self.assertEqual(hint.medium_code, 'direct')
    
    def test_webinteraction_automatic_touchpoint_resolution(self):
        """Test automatic touchpoint resolution on save."""
        # Create interaction without touchpoint
        interaction = Interaction.objects.create(
            touchpoint=None,
            person=None
        )
        
        # Create web interaction - should trigger automatic touchpoint resolution
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id='test-session-123',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            payload={'event_type': 'page_view', 'page': '/test'}
        )
        
        # Refresh from database
        interaction.refresh_from_db()
        
        # Should have a touchpoint assigned
        self.assertIsNotNone(interaction.touchpoint)
        self.assertEqual(interaction.touchpoint.code, 'web.page_read')
    
    def test_webinteraction_channel_property(self):
        """Test channel property access through touchpoint."""
        # Create a channel
        from interactions.models import Channel
        channel = Channel.objects.create(
            code='example.com',
            name='Example Website',
            description='Example website channel'
        )
        
        # Create touchpoint with channel
        touchpoint_with_channel = Touchpoint.objects.create(
            code='web.test_with_channel',
            name='Test Touchpoint with Channel',
            touchpoint_class=self.touchpoint_class,
            channel=channel
        )
        
        interaction = Interaction.objects.create(
            touchpoint=touchpoint_with_channel,
            person=None
        )
        
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id='test-session-123'
        )
        
        # Test channel property access
        self.assertEqual(web_interaction.channel, channel)
        self.assertEqual(web_interaction.channel.code, 'example.com')
    
    def test_webinteraction_channel_none_handling(self):
        """Test handling when touchpoint has no channel."""
        interaction = Interaction.objects.create(
            touchpoint=self.touchpoint,  # touchpoint without channel
            person=None
        )
        
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id='test-session-123'
        )
        
        # Test channel property when no channel is set
        self.assertIsNone(web_interaction.channel)
