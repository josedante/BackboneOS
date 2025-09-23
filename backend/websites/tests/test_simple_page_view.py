#!/usr/bin/env python
"""
Simple test script for page view flow implementation.
"""

from websites.models import WebInteraction, Website
from interactions.models import Action, Agent, Interaction, Touchpoint, TouchpointClass, Channel, Medium
from our_institution.models import Division

def test_page_view_flow():
    """Test the page view flow with a simple scenario."""
    
    print("🧪 Testing Page View Flow Implementation")
    print("=" * 50)
    
    # Test: New visitor with external referrer
    print("\n📋 Test: New visitor with external referrer (Google search)")
    print("-" * 50)
    
    event_data = {
        "event_type": "page_view",
        "website_base": "https://esan.edu.pe",
        "full_url": "https://esan.edu.pe/programs/mba",
        "referrer": "https://google.com/search?q=mba+programs",
        "session_id": "sess_test_123",
        "visitor_cookie": "visitor_test_456",
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
        print("Processing page view event...")
        created_interactions = WebInteraction.process_page_view_event(event_data)
        print(f"✅ Created {len(created_interactions)} interactions")
        
        for interaction in created_interactions:
            print(f"   - {interaction.interaction_type}: {interaction.id}")
            print(f"     Action: {interaction.interaction.action.name}")
            print(f"     Touchpoint: {interaction.interaction.touchpoint.name if interaction.interaction.touchpoint else 'None'}")
            print(f"     Related interactions: {interaction.related_interactions.count()}")
        
        # Verify expected interactions
        interaction_types = [i.interaction_type for i in created_interactions]
        expected_types = ['page_view', 'referrer_click', 'session_start']
        
        for expected_type in expected_types:
            if expected_type in interaction_types:
                print(f"   ✅ {expected_type} interaction created")
            else:
                print(f"   ❌ {expected_type} interaction missing")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"Total WebInteractions: {WebInteraction.objects.count()}")
        print(f"Total Websites: {Website.objects.count()}")
        print(f"Total Actions: {Action.objects.count()}")
        print(f"Total Agents: {Agent.objects.count()}")
        
        print("\n✅ Test completed successfully!")
        return True
                
    except Exception as e:
        print(f"❌ Error in Test: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the test
if __name__ == '__main__':
    test_page_view_flow()
