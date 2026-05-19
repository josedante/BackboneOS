import json
import logging
import traceback

import sentry_sdk
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from connectors.fallback import store_failed_event
from .services import process_web_event

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ['event_type', 'website_base', 'full_url']


@method_decorator(csrf_exempt, name='dispatch')
class WebEventView(View):
    """Base view for all website tracking events.

    Subclasses set `event_type` to the expected event string (e.g. 'page_view').
    All validation, error handling, Sentry reporting, and fallback queuing
    live here so concrete views stay trivial.
    """
    event_type: str = ''

    def post(self, request):
        data = None
        try:
            data = json.loads(request.body)

            for field in REQUIRED_FIELDS:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            if data.get('event_type') != self.event_type:
                return JsonResponse(
                    {'error': f'Only {self.event_type} events are supported by this endpoint'},
                    status=400,
                )

            try:
                interactions = process_web_event(self.event_type, data)
            except PermissionError as e:
                logger.warning(f"Rejected event from unauthorized domain: {data['website_base']}")
                store_failed_event(
                    connector_type='web',
                    event_type=self.event_type,
                    raw_payload=data,
                    error_message=str(e),
                    error_trace='Domain validation failed',
                    source_identifier=data.get('website_base', ''),
                )
                return JsonResponse({'error': 'Forbidden', 'message': str(e)}, status=403)

            logger.info(
                f"Processed {self.event_type} event: {data.get('full_url')} "
                f"- Created {len(interactions)} interactions"
            )
            return JsonResponse({
                'success': True,
                'message': f'Successfully processed {self.event_type} event',
                'interactions_created': len(interactions),
                'interaction_ids': [str(i.pk) for i in interactions],
            }, status=201)

        except json.JSONDecodeError:
            sentry_sdk.capture_message(
                f"Invalid JSON in {self.event_type} event",
                level='warning',
                extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')},
            )
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        except ValueError as e:
            sentry_sdk.capture_message(
                f"Invalid data in {self.event_type} event: {str(e)}",
                level='warning',
                extras={'event_data': data or {}, 'error': str(e)},
            )
            logger.warning(f"Invalid data in {self.event_type} event: {str(e)}")
            return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)

        except Exception as e:
            error_trace = traceback.format_exc()
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('connector_type', 'web')
                scope.set_tag('event_type', self.event_type)
                scope.set_tag('has_fallback', 'true')
                if data:
                    scope.set_context('event_data', {
                        'full_url': data.get('full_url'),
                        'website_base': data.get('website_base'),
                        'session_id': data.get('session_id'),
                        'has_referrer': bool(data.get('referrer')),
                    })
                sentry_sdk.capture_exception(e)

            try:
                failed_event = store_failed_event(
                    connector_type='web',
                    event_type=self.event_type,
                    raw_payload=data or {},
                    error_message=str(e),
                    error_trace=error_trace,
                    source_identifier=(data or {}).get('website_base', ''),
                )
                logger.error(
                    f"CRITICAL: Failed to process {self.event_type} event. "
                    f"Stored in fallback (ID: {failed_event.pk})",
                    exc_info=True,
                )
                return JsonResponse({
                    'success': False,
                    'error': 'Event processing failed but has been queued for retry',
                    'fallback_id': str(failed_event.pk),
                    'message': 'Your event will be processed automatically',
                }, status=202)

            except Exception as fallback_error:
                with sentry_sdk.push_scope() as scope:
                    scope.level = 'fatal'
                    scope.set_tag('catastrophic_failure', 'true')
                    scope.set_context('original_error', {'message': str(e)})
                    scope.set_context('fallback_error', {'message': str(fallback_error)})
                    sentry_sdk.capture_message(
                        "CATASTROPHIC: Failed to process event AND failed to store in fallback!",
                        level='fatal',
                    )
                logger.critical(
                    f"CATASTROPHIC FAILURE: Original error: {str(e)} | Fallback error: {str(fallback_error)}",
                    exc_info=True,
                )
                return JsonResponse(
                    {'error': 'Internal server error', 'message': 'Unable to process event'},
                    status=500,
                )


class PageViewEventView(WebEventView):
    event_type = 'page_view'


class PageReadEventView(WebEventView):
    event_type = 'page_read'


class ClickEventView(WebEventView):
    event_type = 'click'


class FormSubmitEventView(WebEventView):
    event_type = 'form_submit'


class DownloadEventView(WebEventView):
    event_type = 'download'


class VideoPlayEventView(WebEventView):
    event_type = 'video_play'


class SearchEventView(WebEventView):
    event_type = 'search'


class NewsletterSignupEventView(WebEventView):
    event_type = 'newsletter_signup'
