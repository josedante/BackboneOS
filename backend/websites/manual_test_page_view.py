#!/usr/bin/env python
"""
Manual test script for page view flow implementation.

This script can be run within the Docker environment to test the page view
event processing flow manually.
"""

import os
import sys
import django
import json
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from websites.models import WebInteraction, Website
from interactions.models import Action, Agent, Interaction, Touchpoint, TouchpointClass, Channel, Medium
from our_institution.models import Division


def test_page_view_flow():
    """Test the page view flow with various scenarios."""
    
    print("🧪 Testing Page View Flow Implementation")
    print("=" * 50)
    
    # Test 1: New visitor with external referrer
    print("\n📋 Test 1: New visitor with external referrer (Google search)")
    print("-" * 50)
    
    event_data_1 = {
        "event_type": "page_view",
        "website_base": "https://esan.edu.pe",
        "full_url": "https://esan.edu.pe/programs/mba",
        "referrer": "https://google.com/search?q=mba+programs",
        "session_id": "sess_test_1_123",
        "visitor_cookie": "visitor_test_1_456",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "utm_source": "google",
        "utm_medium": "organic",
        "utm_campaign": "mba_search",
        "utm_content": "programs_page",
        "utm_term": "mba programs",
        "element": "body",
        "payload": {
            "page_title": "MBA Programs - ESAN University",
            "page_description": "Comprehensive MBA programs designed for working professionals",
            "page_category": "academic_programs",
            "load_time": 1.2,
            "is_landing_page": True,
            "page_depth": 2,
            "referrer_title": "Google Search Results",
            "referrer_description": "Search results for 'MBA programs Peru'"
        }
    }
    
    try:
        created_interactions_1 = WebInteraction.process_page_view_event(event_data_1)
        print(f"✅ Created {len(created_interactions_1)} interactions")
        
        for interaction in created_interactions_1:
            print(f"   - {interaction.interaction_type}: {interaction.id}")
            print(f"     Action: {interaction.interaction.action.name}")
            print(f"     Touchpoint: {interaction.interaction.touchpoint.name if interaction.interaction.touchpoint else 'None'}")
            print(f"     Related interactions: {interaction.related_interactions.count()}")
        
        # Verify expected interactions
        interaction_types = [i.interaction_type for i in created_interactions_1]
        expected_types = ['page_view', 'referrer_click', 'session_start']
        
        for expected_type in expected_types:
            if expected_type in interaction_types:
                print(f"   ✅ {expected_type} interaction created")
            else:
                print(f"   ❌ {expected_type} interaction missing")
                
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
    
    # Test 2: Direct traffic (no referrer)
    print("\n📋 Test 2: Direct traffic (no referrer)")
    print("-" * 50)
    
    event_data_2 = {
        "event_type": "page_view",
        "website_base": "https://esan.edu.pe",
        "full_url": "https://esan.edu.pe/",
        "referrer": "",
        "session_id": "sess_test_2_123",
        "visitor_cookie": "visitor_test_2_456",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "element": "body",
        "payload": {
            "page_title": "ESAN University - Home",
            "page_description": "Welcome to ESAN University",
            "is_landing_page": True
        }
    }
    
    try:
        created_interactions_2 = WebInteraction.process_page_view_event(event_data_2)
        print(f"✅ Created {len(created_interactions_2)} interactions")
        
        for interaction in created_interactions_2:
            print(f"   - {interaction.interaction_type}: {interaction.id}")
            print(f"     Action: {interaction.interaction.action.name}")
            print(f"     Touchpoint: {interaction.interaction.touchpoint.name if interaction.interaction.touchpoint else 'None'}")
        
        # Verify expected interactions (should not have referrer_click)
        interaction_types = [i.interaction_type for i in created_interactions_2]
        expected_types = ['page_view', 'session_start']
        
        for expected_type in expected_types:
            if expected_type in interaction_types:
                print(f"   ✅ {expected_type} interaction created")
            else:
                print(f"   ❌ {expected_type} interaction missing")
        
        if 'referrer_click' not in interaction_types:
            print(f"   ✅ No referrer_click interaction (as expected for direct traffic)")
        else:
            print(f"   ❌ Unexpected referrer_click interaction for direct traffic")
                
    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
    
    # Test 3: Returning visitor (should not create session_start)
    print("\n📋 Test 3: Returning visitor (existing session)")
    print("-" * 50)
    
    event_data_3 = {
        "event_type": "page_view",
        "website_base": "https://esan.edu.pe",
        "full_url": "https://esan.edu.pe/programs/mba",
        "referrer": "https://facebook.com/post/123",
        "session_id": "sess_test_1_123",  # Same session as Test 1
        "visitor_cookie": "visitor_test_1_456",  # Same visitor as Test 1
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "utm_source": "facebook",
        "utm_medium": "social",
        "utm_campaign": "mba_promotion",
        "element": "body",
        "payload": {
            "page_title": "MBA Programs - ESAN University",
            "page_description": "Comprehensive MBA programs designed for working professionals",
            "referrer_title": "Facebook Post",
            "referrer_description": "MBA promotion post on Facebook"
        }
    }
    
    try:
        created_interactions_3 = WebInteraction.process_page_view_event(event_data_3)
        print(f"✅ Created {len(created_interactions_3)} interactions")
        
        for interaction in created_interactions_3:
            print(f"   - {interaction.interaction_type}: {interaction.id}")
            print(f"     Action: {interaction.interaction.action.name}")
            print(f"     Touchpoint: {interaction.interaction.touchpoint.name if interaction.interaction.touchpoint else 'None'}")
        
        # Verify expected interactions (should not have session_start)
        interaction_types = [i.interaction_type for i in created_interactions_3]
        expected_types = ['page_view', 'referrer_click']
        
        for expected_type in expected_types:
            if expected_type in interaction_types:
                print(f"   ✅ {expected_type} interaction created")
            else:
                print(f"   ❌ {expected_type} interaction missing")
        
        if 'session_start' not in interaction_types:
            print(f"   ✅ No session_start interaction (as expected for returning visitor)")
        else:
            print(f"   ❌ Unexpected session_start interaction for returning visitor")
                
    except Exception as e:
        print(f"❌ Error in Test 3: {e}")
    
    # Test 4: Test website creation
    print("\n📋 Test 4: Website creation from event data")
    print("-" * 50)
    
    event_data_4 = {
        "event_type": "page_view",
        "website_base": "https://newwebsite.com",
        "full_url": "https://newwebsite.com/page",
        "session_id": "sess_test_4_123",
        "visitor_cookie": "visitor_test_4_456",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "element": "body",
        "payload": {
            "page_title": "New Website Page"
        }
    }
    
    try:
        # Check if website exists before
        website_exists_before = Website.objects.filter(base_url="https://newwebsite.com").exists()
        print(f"Website exists before: {website_exists_before}")
        
        created_interactions_4 = WebInteraction.process_page_view_event(event_data_4)
        print(f"✅ Created {len(created_interactions_4)} interactions")
        
        # Check if website was created
        website_exists_after = Website.objects.filter(base_url="https://newwebsite.com").exists()
        print(f"Website exists after: {website_exists_after}")
        
        if website_exists_after and not website_exists_before:
            new_website = Website.objects.get(base_url="https://newwebsite.com")
            print(f"   ✅ Website created: {new_website.name}")
            print(f"   ✅ Website active: {new_website.active}")
        else:
            print(f"   ❌ Website creation failed")
                
    except Exception as e:
        print(f"❌ Error in Test 4: {e}")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    total_interactions = WebInteraction.objects.count()
    total_websites = Website.objects.count()
    total_actions = Action.objects.count()
    total_agents = Agent.objects.count()
    
    print(f"Total WebInteractions created: {total_interactions}")
    print(f"Total Websites created: {total_websites}")
    print(f"Total Actions created: {total_actions}")
    print(f"Total Agents created: {total_agents}")
    
    # Show some sample data
    print("\n📋 Sample Interactions:")
    recent_interactions = WebInteraction.objects.all().order_by('-created_at')[:5]
    for interaction in recent_interactions:
        print(f"   - {interaction.interaction_type} | {interaction.website.name} | {interaction.session_id}")
    
    print("\n✅ Manual testing completed!")


if __name__ == '__main__':
    test_page_view_flow()
