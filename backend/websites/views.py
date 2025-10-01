"""
Views for website interactions and event processing.
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


@method_decorator(csrf_exempt, name='dispatch')
class PageReadEventView(View):
    """
    View to handle page read events from website tracking scripts.
    
    Page read events track meaningful page engagement.
    """
    
    def post(self, request):
        """Process a page read event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process page_read events
            if data.get('event_type') != 'page_read':
                return JsonResponse({
                    'error': 'Only page_read events are supported by this endpoint'
                }, status=400)
            
            # Process the page read event
            created_interactions = WebInteraction.process_page_read_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed page read event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed page read event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing page read event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ClickEventView(View):
    """
    View to handle click events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a click event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process click events
            if data.get('event_type') != 'click':
                return JsonResponse({
                    'error': 'Only click events are supported by this endpoint'
                }, status=400)
            
            # Process the click event
            created_interactions = WebInteraction.process_click_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed click event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed click event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing click event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FormSubmitEventView(View):
    """
    View to handle form submission events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a form submission event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process form_submit events
            if data.get('event_type') != 'form_submit':
                return JsonResponse({
                    'error': 'Only form_submit events are supported by this endpoint'
                }, status=400)
            
            # Process the form submission event
            created_interactions = WebInteraction.process_form_submit_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed form submission event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed form submission event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing form submission event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DownloadEventView(View):
    """
    View to handle download events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a download event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process download events
            if data.get('event_type') != 'download':
                return JsonResponse({
                    'error': 'Only download events are supported by this endpoint'
                }, status=400)
            
            # Process the download event
            created_interactions = WebInteraction.process_download_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed download event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed download event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing download event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VideoPlayEventView(View):
    """
    View to handle video play events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a video play event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process video_play events
            if data.get('event_type') != 'video_play':
                return JsonResponse({
                    'error': 'Only video_play events are supported by this endpoint'
                }, status=400)
            
            # Process the video play event
            created_interactions = WebInteraction.process_video_play_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed video play event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed video play event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing video play event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SearchEventView(View):
    """
    View to handle search events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a search event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process search events
            if data.get('event_type') != 'search':
                return JsonResponse({
                    'error': 'Only search events are supported by this endpoint'
                }, status=400)
            
            # Process the search event
            created_interactions = WebInteraction.process_search_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed search event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed search event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing search event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterSignupEventView(View):
    """
    View to handle newsletter signup events from website tracking scripts.
    """
    
    def post(self, request):
        """Process a newsletter signup event."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['event_type', 'website_base', 'full_url']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Only process newsletter_signup events
            if data.get('event_type') != 'newsletter_signup':
                return JsonResponse({
                    'error': 'Only newsletter_signup events are supported by this endpoint'
                }, status=400)
            
            # Process the newsletter signup event
            created_interactions = WebInteraction.process_newsletter_signup_event(data)
            
            response_data = {
                'success': True,
                'message': 'Successfully processed newsletter signup event',
                'interactions_created': len(created_interactions),
                'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
            }
            
            logger.info(f"Processed newsletter signup event: {data.get('full_url')} - Created {len(created_interactions)} interactions")
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error processing newsletter signup event: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)