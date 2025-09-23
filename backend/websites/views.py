"""
Views for website interactions and page view event processing.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .models import WebInteraction

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PageViewEventView(View):
    """
    View to handle page view events from website tracking scripts.
    
    This view processes page view events and creates multiple interactions
    using the multi-interaction approach.
    """
    
    def post(self, request):
        """
        Process a page view event.
        
        Expected JSON payload:
        {
            "event_type": "page_view",
            "website_base": "https://esan.edu.pe",
            "full_url": "https://esan.edu.pe/programs/mba",
            "referrer": "https://google.com/search?q=mba+programs",
            "session_id": "sess_abc123",
            "visitor_cookie": "visitor_xyz789",
            "user_agent": "Mozilla/5.0...",
            "utm_source": "google",
            "utm_medium": "organic",
            "utm_campaign": "mba_search",
            "utm_content": "programs_page",
            "utm_term": "mba programs",
            "element": "body",
            "payload": {
                "page_title": "MBA Programs - ESAN University",
                "page_description": "Comprehensive MBA programs...",
                "page_category": "academic_programs",
                "load_time": 1.2,
                "is_landing_page": false,
                "page_depth": 2,
                "referrer_title": "Google Search Results",
                "referrer_description": "Search results for 'MBA programs Peru'"
            }
        }
        """
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process page_view events
            if data.get('event_type') != 'page_view':
                return JsonResponse({
                    'error': 'Only page_view events are supported by this endpoint'
                }, status=400)
            
            # Process the page view event
            created_interactions = WebInteraction.process_page_view_event(data)
            
            # Prepare response
            response_data = {
                'success': True,
                'message': f'Successfully processed page view event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed page view event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing page view event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)