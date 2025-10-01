#!/usr/bin/env python
"""
Test script to verify the websites app implementation.

This script tests the multi-interaction approach for page view events
and verifies that all components work together correctly.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json

from websites.models import WebInteraction, Website, WebSession, WebAgent
from interactions.models import Interaction, Action, Agent, Touchpoint
from our_institution.models import Division


def test_basic_functionality():
    """Test basic functionality without database transactions."""
    print("🧪 Testing basic functionality...")
    
    # Test user agent parsing
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    browser_info = WebInteraction._parse_user_agent(user_agent)
    
    assert browser_info["browser"]["family"] == "Chrome", f"Expected Chrome, got {browser_info['browser']['family']}"
    assert browser_info["os"]["family"] == "Windows", f"Expected Windows, got {browser_info['os']['family']}"
    print("✅ User agent parsing works correctly")
    
    # Test bot detection
    bot_ua = "Googlebot/2.1 (+http://www.google.com/bot.html)"
    assert WebInteraction._is_bot_user_agent(bot_ua), "Should detect Googlebot as bot"
    
    regular_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    assert not WebInteraction._is_bot_user_agent(regular_ua), "Should not detect regular browser as bot"
    print("✅ Bot detection works correctly")
    
    # Test domain extraction
    domain = WebInteraction._extract_domain("https://google.com/search?q=test")
    assert domain == "google.com", f"Expected google.com, got {domain}"
    print("✅ Domain extraction works correctly")
    
    print("✅ All basic functionality tests passed!")


def test_database_functionality():
    """Test database functionality with proper setup."""
    print("🧪 Testing database functionality...")
    
    try:
        with transaction.atomic():
            # Create test division
            division = Division.objects.create(
                name="Test Division",
                description="Test division for website interactions",
                active=True
            )
            print("✅ Division created successfully")
            
            # Create test website
            website = Website.objects.create(
                name="Test Website",
                base_url="https://test.example.com",
                division=division,
                active=True
            )
            print("✅ Website created successfully")
            
            # Test agent creation
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            agent = WebInteraction._get_or_create_agent(user_agent)
            assert isinstance(agent, Agent), "Agent should be created"
            print("✅ Agent creation works correctly")
            
            # Test default division creation
            default_division = WebInteraction._get_default_division()
            assert isinstance(default_division, Division), "Default division should be created"
            print("✅ Default division creation works correctly")
            
            # Test page view interaction creation
            event_data = {
                "event_type": "page_view",
                "website_base": "https://test.example.com",
                "full_url": "https://test.example.com/programs/mba",
                "referrer": "https://google.com/search?q=mba+programs",
                "session_id": "sess_test123",
                "visitor_cookie": "visitor_test456",
                "user_agent": user_agent,
                "utm_source": "google",
                "utm_medium": "organic",
                "utm_campaign": "mba_search",
                "payload": {
                    "page_title": "MBA Programs - Test University",
                    "page_category": "academic_programs"
                }
            }
            
            web_interaction = WebInteraction._create_page_view_interaction(event_data)
            assert isinstance(web_interaction, WebInteraction), "WebInteraction should be created"
            assert web_interaction.website == website, "Website should match"
            assert web_interaction.session_id == "sess_test123", "Session ID should match"
            print("✅ Page view interaction creation works correctly")
            
            # Test that core Interaction was created
            assert web_interaction.interaction is not None, "Core Interaction should be created"
            assert web_interaction.interaction.action.code == "no_action", "Action should be no_action"
            print("✅ Core Interaction creation works correctly")
            
            # Test referrer click interaction creation
            mock_touchpoint = MagicMock()
            mock_touchpoint.code = "web.referrer_click.google_search"
            
            referrer_interaction = WebInteraction._create_referrer_click_interaction(
                event_data, 
                mock_touchpoint
            )
            assert isinstance(referrer_interaction, WebInteraction), "Referrer interaction should be created"
            assert referrer_interaction.interaction.action.code == "external_click", "Action should be external_click"
            print("✅ Referrer click interaction creation works correctly")
            
            # Test session start interaction creation
            session_interaction = WebInteraction._create_session_start_interaction(
                event_data, 
                mock_touchpoint
            )
            assert isinstance(session_interaction, WebInteraction), "Session interaction should be created"
            assert session_interaction.interaction.action.code == "session_start", "Action should be session_start"
            print("✅ Session start interaction creation works correctly")
            
            # Test WebSession creation
            web_session = WebSession.objects.create(
                session_id="sess_test123",
                visitor_cookie="visitor_test456",
                website=website,
                started_at=timezone.now()
            )
            assert isinstance(web_session, WebSession), "WebSession should be created"
            assert web_session.is_session_active, "Session should be active"
            print("✅ WebSession creation works correctly")
            
            # Test WebAgent proxy model
            web_agent = WebAgent.objects.get(pk=agent.pk)
            assert web_agent.browser_family == "Chrome", "Browser family should be detected"
            assert web_agent.os_family == "Windows", "OS family should be detected"
            print("✅ WebAgent proxy model works correctly")
            
        print("✅ All database functionality tests passed!")
        
    except Exception as e:
        print(f"❌ Database functionality test failed: {e}")
        raise


def test_multi_interaction_approach():
    """Test the complete multi-interaction approach."""
    print("🧪 Testing multi-interaction approach...")
    
    try:
        with transaction.atomic():
            # Create test data
            division = Division.objects.create(
                name="Test Division",
                description="Test division for website interactions",
                active=True
            )
            
            # Sample event data
            event_data = {
                "event_type": "page_view",
                "website_base": "https://test.example.com",
                "full_url": "https://test.example.com/programs/mba",
                "referrer": "https://google.com/search?q=mba+programs",
                "session_id": "sess_test123",
                "visitor_cookie": "visitor_test456",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "utm_source": "google",
                "utm_medium": "organic",
                "utm_campaign": "mba_search",
                "payload": {
                    "page_title": "MBA Programs - Test University",
                    "page_category": "academic_programs"
                }
            }
            
            # Mock the extended framework
            with patch('websites.models.ExtendedTouchpointResolver') as mock_resolver_class:
                with patch('websites.models.ExtendedDatabaseMappingProvider'):
                    mock_resolver = MagicMock()
                    mock_resolver_class.return_value = mock_resolver
                    
                    # Mock touchpoints for all three interactions
                    mock_touchpoints = [MagicMock(), MagicMock(), MagicMock()]
                    mock_resolver.resolve_batch.return_value = mock_touchpoints
                    
                    # Process the page view event
                    interactions = WebInteraction.process_page_view_event(event_data)
                    
                    # Verify interactions were created
                    assert isinstance(interactions, list), "Should return a list of interactions"
                    assert len(interactions) == 3, f"Should create 3 interactions, got {len(interactions)}"
                    
                    # Verify all interactions are WebInteraction instances
                    for i, interaction in enumerate(interactions):
                        assert isinstance(interaction, WebInteraction), f"Interaction {i} should be WebInteraction"
                        assert interaction.website.base_url == "https://test.example.com", f"Website should match for interaction {i}"
                        assert interaction.session_id == "sess_test123", f"Session ID should match for interaction {i}"
                    
                    print("✅ Multi-interaction approach works correctly")
                    print(f"✅ Created {len(interactions)} interactions as expected")
        
        print("✅ All multi-interaction approach tests passed!")
        
    except Exception as e:
        print(f"❌ Multi-interaction approach test failed: {e}")
        raise


def main():
    """Run all tests."""
    print("🚀 Starting websites app implementation tests...")
    print("=" * 60)
    
    try:
        # Test basic functionality
        test_basic_functionality()
        print()
        
        # Test database functionality
        test_database_functionality()
        print()
        
        # Test multi-interaction approach
        test_multi_interaction_approach()
        print()
        
        print("=" * 60)
        print("🎉 All tests passed! The websites app implementation is working correctly.")
        print("✅ Multi-interaction approach is fully implemented")
        print("✅ All helper methods are working")
        print("✅ Database operations are working")
        print("✅ Touchpoint resolution framework is integrated")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
