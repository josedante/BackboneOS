"""
Views for website interactions and event processing.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
import traceback
import sentry_sdk

from .models import WebInteraction
from connectors.fallback import store_failed_event

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
            
        except json.JSONDecodeError as e:
            # Client sent invalid JSON - log warning to Sentry
            sentry_sdk.capture_message(
                f"Invalid JSON in page_view event",
                level='warning',
                extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')}
            )
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        
        except ValueError as e:
            # Data validation errors (4xx) - log to Sentry but don't store in fallback
            sentry_sdk.capture_message(
                f"Invalid data in page_view event: {str(e)}",
                level='warning',
                extras={
                    'event_data': data if 'data' in locals() else {},
                    'error': str(e)
                }
            )
            logger.warning(f"Invalid data in page_view event: {str(e)}")
            return JsonResponse({
                'error': 'Invalid data',
                'message': str(e)
            }, status=400)
            
        except Exception as e:
            # CRITICAL: System errors (5xx) - capture in Sentry and store in fallback
            error_trace = traceback.format_exc()
            
            # Set Sentry context with rich data
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'page_view')
                scope.set_tag('has_fallback', 'true')
                
                # Add contextual data
                if 'data' in locals():
                    scope.set_context('event_data', {
                        'full_url': data.get('full_url'),
                        'website_base': data.get('website_base'),
                        'session_id': data.get('session_id'),
                        'has_referrer': bool(data.get('referrer')),
                    })
                
                # Capture the exception with context
                sentry_sdk.capture_exception(e)
            
            # Attempt to store in fallback for retry
            try:
                failed_event = store_failed_event(
                    connector_type='web',
                    event_type='page_view',
                    raw_payload=data if 'data' in locals() else {},
                    error_message=str(e),
                    error_trace=error_trace,
                    source_identifier=data.get('website_base', '') if 'data' in locals() else ''
                )
                
                logger.error(
                    f"CRITICAL: Failed to process page view event. "
                    f"Stored in fallback queue (ID: {failed_event.pk}) for retry. "
                    f"Error: {str(e)}",
                    exc_info=True
                )
                
                return JsonResponse({
                    'success': False,
                    'error': 'Event processing failed but has been queued for retry',
                    'fallback_id': str(failed_event.pk),
                    'message': 'Your event will be processed automatically'
                }, status=202)  # 202 Accepted - will process later
                
            except Exception as fallback_error:
                # CATASTROPHIC: Even fallback failed!
                
                # Send critical alert to Sentry
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    scope.set_context('original_error', {'message': str(e)})
                    scope.set_context('fallback_error', {'message': str(fallback_error)})
                    
                    sentry_sdk.capture_message(
                        "CATASTROPHIC: Failed to process event AND failed to store in fallback!",
                        level='fatal'
                    )
                
                logger.critical(
                    f"CATASTROPHIC FAILURE: Original error: {str(e)} | Fallback error: {str(fallback_error)}",
                    exc_info=True
                )
                
                return JsonResponse({
                    'error': 'Internal server error',
                    'message': 'Unable to process event'
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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(
                f"Invalid JSON in page_read event",
                level='warning',
                extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')}
            )
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        except ValueError as e:
            sentry_sdk.capture_message(
                f"Invalid data in page_read event: {str(e)}",
                level='warning',
                extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)}
            )
            logger.warning(f"Invalid data in page_read event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
            
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'page_read')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {
                        'full_url': data.get('full_url'),
                        'website_base': data.get('website_base')
                    })
                sentry_sdk.capture_exception(e)
            
            try:
                failed_event = store_failed_event(
                    connector_type='web',
                    event_type='page_read',
                    raw_payload=data if 'data' in locals() else {},
                    error_message=str(e),
                    error_trace=error_trace,
                    source_identifier=data.get('website_base', '') if 'data' in locals() else ''
                )
                logger.error(f"CRITICAL: Failed to process page_read event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'error': 'Event processing failed but has been queued for retry',
                    'fallback_id': str(failed_event.pk),
                    'message': 'Your event will be processed automatically'
                }, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in click event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in click event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in click event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
            
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'click')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            
            try:
                failed_event = store_failed_event(
                    connector_type='web', event_type='click', raw_payload=data if 'data' in locals() else {},
                    error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else ''
                )
                logger.error(f"CRITICAL: Failed to process click event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in form_submit event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in form_submit event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in form_submit event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'form_submit')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            try:
                failed_event = store_failed_event(connector_type='web', event_type='form_submit', raw_payload=data if 'data' in locals() else {}, error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else '')
                logger.error(f"CRITICAL: Failed to process form_submit event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in download event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in download event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in download event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'download')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            try:
                failed_event = store_failed_event(connector_type='web', event_type='download', raw_payload=data if 'data' in locals() else {}, error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else '')
                logger.error(f"CRITICAL: Failed to process download event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in video_play event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in video_play event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in video_play event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'video_play')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            try:
                failed_event = store_failed_event(connector_type='web', event_type='video_play', raw_payload=data if 'data' in locals() else {}, error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else '')
                logger.error(f"CRITICAL: Failed to process video_play event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in search event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in search event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in search event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'search')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            try:
                failed_event = store_failed_event(connector_type='web', event_type='search', raw_payload=data if 'data' in locals() else {}, error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else '')
                logger.error(f"CRITICAL: Failed to process search event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)


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
            
        except json.JSONDecodeError as e:
            sentry_sdk.capture_message(f"Invalid JSON in newsletter_signup event", level='warning', extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')})
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            sentry_sdk.capture_message(f"Invalid data in newsletter_signup event: {str(e)}", level='warning', extras={'event_data': data if 'data' in locals() else {}, 'error': str(e)})
            logger.warning(f"Invalid data in newsletter_signup event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)
        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', 'newsletter_signup')
                scope.set_tag('has_fallback', 'true')
                if 'data' in locals():
                    scope.set_context('event_data', {'full_url': data.get('full_url'), 'website_base': data.get('website_base')})
                sentry_sdk.capture_exception(e)
            try:
                failed_event = store_failed_event(connector_type='web', event_type='newsletter_signup', raw_payload=data if 'data' in locals() else {}, error_message=str(e), error_trace=error_trace, source_identifier=data.get('website_base', '') if 'data' in locals() else '')
                logger.error(f"CRITICAL: Failed to process newsletter_signup event. Stored in fallback (ID: {failed_event.pk})", exc_info=True)
                return JsonResponse({'success': False, 'error': 'Event processing failed but has been queued for retry', 'fallback_id': str(failed_event.pk), 'message': 'Your event will be processed automatically'}, status=202)
            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    sentry_sdk.capture_message("CATASTROPHIC: Failed to process event AND failed to store in fallback!", level='fatal')
                logger.critical(f"CATASTROPHIC FAILURE: {str(e)} | Fallback: {str(fallback_error)}", exc_info=True)
                return JsonResponse({'error': 'Internal server error', 'message': 'Unable to process event'}, status=500)