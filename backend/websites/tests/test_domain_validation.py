"""
Tests for website domain validation functionality.

Tests the validation of domains before processing tracking events.
"""
import pytest
import json
from django.test import TestCase, Client
from django.urls import reverse
from websites.models import Website
from our_institution.models import Division, OurOrganization
from world.models import Country
from connectors.models import FailedEvent


@pytest.mark.django_db
class TestWebsiteDomainValidation(TestCase):
    """Test domain validation for website tracking events."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        # Create required organizational structure
        self.country = Country.objects.create(
            iso3_code='USA',
            iso2_code='US',
            name='United States',
            official_name='United States of America'
        )
        
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            is_active=True,
            country=self.country
        )
        
        # Create a division for websites
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST",
            organization=self.organization
        )
        
        # Create an active registered website
        self.active_website = Website.objects.create(
            name="Active Test Site",
            base_url="https://active-site.com",
            division=self.division,
            active=True
        )
        
        # Create an inactive registered website
        self.inactive_website = Website.objects.create(
            name="Inactive Test Site",
            base_url="https://inactive-site.com",
            division=self.division,
            active=False
        )
    
    def test_validate_registered_active_website(self):
        """Test that registered and active websites pass validation."""
        website = Website.validate_domain_or_reject("https://active-site.com")
        
        self.assertEqual(website, self.active_website)
        self.assertTrue(website.active)
    
    def test_reject_unregistered_website(self):
        """Test that unregistered websites raise PermissionError."""
        with self.assertRaises(PermissionError) as context:
            Website.validate_domain_or_reject("https://unregistered-site.com")
        
        self.assertIn("not registered", str(context.exception))
    
    def test_reject_inactive_website(self):
        """Test that inactive websites raise PermissionError."""
        with self.assertRaises(PermissionError) as context:
            Website.validate_domain_or_reject("https://inactive-site.com")
        
        self.assertIn("inactive", str(context.exception))
    
    def test_reject_invalid_url_format(self):
        """Test that malformed URLs raise PermissionError."""
        with self.assertRaises(PermissionError) as context:
            Website.validate_domain_or_reject("not-a-valid-url")
        
        self.assertIn("Invalid URL format", str(context.exception))
    
    def test_url_normalization(self):
        """Test that URLs are normalized correctly."""
        # Should match even with trailing slashes or paths
        website = Website.validate_domain_or_reject("https://active-site.com/")
        self.assertEqual(website, self.active_website)
        
        website = Website.validate_domain_or_reject("https://active-site.com/some/path")
        self.assertEqual(website, self.active_website)


@pytest.mark.django_db
class TestPageViewEventDomainValidation(TestCase):
    """Test domain validation for page view events."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        # Create required organizational structure
        self.country = Country.objects.create(
            iso3_code='USA',
            iso2_code='US',
            name='United States',
            official_name='United States of America'
        )
        
        self.organization = OurOrganization.objects.create(
            name='Test Organization',
            is_active=True,
            country=self.country
        )
        
        # Create a division
        self.division = Division.objects.create(
            name="Test Division",
            code="TEST",
            organization=self.organization
        )
        
        # Create an active website
        self.website = Website.objects.create(
            name="Test Site",
            base_url="https://test-site.com",
            division=self.division,
            active=True
        )
        
        # Base event data
        self.event_data = {
            "event_type": "page_view",
            "website_base": "https://test-site.com",
            "full_url": "https://test-site.com/page",
            "session_id": "test_session_123",
            "visitor_cookie": "visitor_abc",
            "user_agent": "Mozilla/5.0 Test Browser",
        }
    
    def test_allowed_domain_processes_event(self):
        """Test that events from allowed domains are processed."""
        response = self.client.post(
            '/api/websites/events/page-view/',
            data=json.dumps(self.event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data['success'])
    
    def test_unregistered_domain_rejected(self):
        """Test that events from unregistered domains are rejected."""
        self.event_data['website_base'] = "https://unregistered-site.com"
        self.event_data['full_url'] = "https://unregistered-site.com/page"
        
        response = self.client.post(
            '/api/websites/events/page-view/',
            data=json.dumps(self.event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'Forbidden')
        self.assertIn('not registered', response_data['message'])
    
    def test_inactive_domain_rejected(self):
        """Test that events from inactive domains are rejected."""
        # Create inactive website
        inactive_site = Website.objects.create(
            name="Inactive Site",
            base_url="https://inactive-site.com",
            division=self.division,
            active=False
        )
        
        self.event_data['website_base'] = "https://inactive-site.com"
        self.event_data['full_url'] = "https://inactive-site.com/page"
        
        response = self.client.post(
            '/api/websites/events/page-view/',
            data=json.dumps(self.event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'Forbidden')
        self.assertIn('inactive', response_data['message'])
    
    def test_rejected_event_stored_in_failed_event(self):
        """Test that rejected events are stored in FailedEvent for audit."""
        initial_count = FailedEvent.objects.count()
        
        self.event_data['website_base'] = "https://unregistered-site.com"
        self.event_data['full_url'] = "https://unregistered-site.com/page"
        
        response = self.client.post(
            '/api/websites/events/page-view/',
            data=json.dumps(self.event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        
        # Check that a FailedEvent was created
        self.assertEqual(FailedEvent.objects.count(), initial_count + 1)
        
        # Verify the failed event details
        failed_event = FailedEvent.objects.latest('created_at')
        self.assertEqual(failed_event.connector_type, 'web')
        self.assertEqual(failed_event.event_type, 'page_view')
        self.assertEqual(failed_event.source_identifier, 'https://unregistered-site.com')
        self.assertIn('not registered', failed_event.error_message)
        self.assertEqual(failed_event.raw_payload['website_base'], 'https://unregistered-site.com')


@pytest.mark.django_db
class TestAllEventEndpointsDomainValidation(TestCase):
    """Test that all event endpoints validate domains."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        # Note: We don't need to create organization/division for these tests
        # since we're testing rejection of unregistered domains
    
    def test_page_read_event_validates_domain(self):
        """Test page_read endpoint validates domains."""
        event_data = {
            "event_type": "page_read",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/page",
        }
        
        response = self.client.post(
            '/api/websites/events/page-read/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_click_event_validates_domain(self):
        """Test click endpoint validates domains."""
        event_data = {
            "event_type": "click",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/page",
        }
        
        response = self.client.post(
            '/api/websites/events/click/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_form_submit_event_validates_domain(self):
        """Test form_submit endpoint validates domains."""
        event_data = {
            "event_type": "form_submit",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/page",
        }
        
        response = self.client.post(
            '/api/websites/events/form-submit/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_download_event_validates_domain(self):
        """Test download endpoint validates domains."""
        event_data = {
            "event_type": "download",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/file.pdf",
        }
        
        response = self.client.post(
            '/api/websites/events/download/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_video_play_event_validates_domain(self):
        """Test video_play endpoint validates domains."""
        event_data = {
            "event_type": "video_play",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/video",
        }
        
        response = self.client.post(
            '/api/websites/events/video-play/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_search_event_validates_domain(self):
        """Test search endpoint validates domains."""
        event_data = {
            "event_type": "search",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/search",
        }
        
        response = self.client.post(
            '/api/websites/events/search/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_newsletter_signup_event_validates_domain(self):
        """Test newsletter_signup endpoint validates domains."""
        event_data = {
            "event_type": "newsletter_signup",
            "website_base": "https://unregistered.com",
            "full_url": "https://unregistered.com/newsletter",
        }
        
        response = self.client.post(
            '/api/websites/events/newsletter-signup/',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)

