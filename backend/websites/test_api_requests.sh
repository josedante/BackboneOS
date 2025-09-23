#!/bin/bash

# Test script for page view API endpoints
# This script can be run to test the API endpoints with curl

echo "🧪 Testing Page View API Endpoints"
echo "=================================="

# Base URL (adjust if needed)
BASE_URL="http://localhost:8000"
API_ENDPOINT="$BASE_URL/websites/events/page-view/"

echo "API Endpoint: $API_ENDPOINT"
echo ""

# Test 1: New visitor with external referrer
echo "📋 Test 1: New visitor with external referrer (Google search)"
echo "------------------------------------------------------------"

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://google.com/search?q=mba+programs",
    "session_id": "sess_api_test_1_123",
    "visitor_cookie": "visitor_api_test_1_456",
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
      "is_landing_page": true,
      "page_depth": 2,
      "referrer_title": "Google Search Results",
      "referrer_description": "Search results for '\''MBA programs Peru'\''"
    }
  }' | jq '.'

echo ""
echo ""

# Test 2: Direct traffic (no referrer)
echo "📋 Test 2: Direct traffic (no referrer)"
echo "---------------------------------------"

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/",
    "referrer": "",
    "session_id": "sess_api_test_2_123",
    "visitor_cookie": "visitor_api_test_2_456",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "element": "body",
    "payload": {
      "page_title": "ESAN University - Home",
      "page_description": "Welcome to ESAN University",
      "is_landing_page": true
    }
  }' | jq '.'

echo ""
echo ""

# Test 3: Returning visitor (same session)
echo "📋 Test 3: Returning visitor (same session as Test 1)"
echo "----------------------------------------------------"

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://facebook.com/post/123",
    "session_id": "sess_api_test_1_123",
    "visitor_cookie": "visitor_api_test_1_456",
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
  }' | jq '.'

echo ""
echo ""

# Test 4: Error case - missing required field
echo "📋 Test 4: Error case - missing required field"
echo "----------------------------------------------"

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "full_url": "https://esan.edu.pe/programs/mba"
  }' | jq '.'

echo ""
echo ""

# Test 5: Error case - wrong event type
echo "📋 Test 5: Error case - wrong event type"
echo "----------------------------------------"

curl -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "form_submit",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba"
  }' | jq '.'

echo ""
echo ""

echo "✅ API testing completed!"
echo ""
echo "Expected results:"
echo "- Test 1: Should create 3 interactions (page_view, referrer_click, session_start)"
echo "- Test 2: Should create 2 interactions (page_view, session_start)"
echo "- Test 3: Should create 2 interactions (page_view, referrer_click) - no session_start"
echo "- Test 4: Should return 400 error (missing website_base)"
echo "- Test 5: Should return 400 error (wrong event_type)"
