"""
Event fallback storage utilities for connectors.

Provides a generic safety net for failed event processing across all connector types.
This module handles storing failed events and retrying them with exponential backoff.
"""

import logging
import traceback
from typing import Optional
from django.utils import timezone
from django.db import transaction

from .models import FailedEvent

logger = logging.getLogger(__name__)


def store_failed_event(
    connector_type: str,
    event_type: str,
    raw_payload: dict,
    error_message: str,
    error_trace: str = '',
    source_identifier: str = ''
) -> FailedEvent:
    """
    Store a failed event for later retry.
    
    This function creates a FailedEvent record with exponential backoff scheduling.
    The event will be automatically retried by background workers.
    
    Max retries are determined by connector type via FAILED_EVENT_RETRY_CONFIG in settings.
    
    Args:
        connector_type: Type of connector (e.g., 'web', 'email')
        event_type: Type of event (e.g., 'page_view', 'email_open')
        raw_payload: Complete raw event data
        error_message: Error message
        error_trace: Full stack trace (optional)
        source_identifier: Source identifier (optional)
    
    Returns:
        FailedEvent: Created failed event instance
    """
    from datetime import timedelta
    
    failed_event = FailedEvent.objects.create(
        connector_type=connector_type,
        event_type=event_type,
        source_identifier=source_identifier,
        raw_payload=raw_payload,
        error_message=error_message[:5000],  # Truncate if too long
        error_trace=error_trace[:10000],  # Truncate stack trace
        next_retry_at=timezone.now() + timedelta(minutes=1)  # First retry in 1 minute
    )
    
    logger.warning(
        f"Stored failed {connector_type}.{event_type} event for retry. "
        f"Failed event ID: {failed_event.pk}. Error: {error_message[:200]}"
    )
    
    return failed_event


def retry_failed_event(failed_event: FailedEvent) -> bool:
    """
    Retry processing a failed event.
    
    Routes the event to the appropriate processor based on connector type
    and event type. Handles success/failure tracking and exponential backoff.
    
    Args:
        failed_event: FailedEvent instance to retry
    
    Returns:
        bool: True if successful, False if failed
    """
    import sentry_sdk
    
    # Add breadcrumb for retry attempt
    sentry_sdk.add_breadcrumb(
        category='retry',
        message=f'Retrying failed event (attempt {failed_event.retry_count + 1})',
        level='info',
        data={
            'failed_event_id': str(failed_event.pk),
            'connector_type': failed_event.connector_type,
            'event_type': failed_event.event_type,
            'retry_count': failed_event.retry_count,
            'first_failed_at': str(failed_event.first_failed_at),
        }
    )
    
    # Mark as processing
    failed_event.mark_processing()
    
    try:
        # Route to appropriate processor based on connector type
        if failed_event.connector_type == 'web':
            interactions = _retry_web_event(failed_event)
        else:
            # Other connector types can be added here
            raise NotImplementedError(
                f"Connector type '{failed_event.connector_type}' not yet supported for retry"
            )
        
        # Extract interaction IDs
        interaction_ids = [str(i.pk) for i in interactions]
        
        # Mark as success
        failed_event.mark_success(interaction_ids)
        
        logger.info(
            f"Successfully reprocessed failed event {failed_event.pk}. "
            f"Created {len(interactions)} interactions: {interaction_ids}"
        )
        
        # Track successful recovery in Sentry
        time_to_recovery = (timezone.now() - failed_event.first_failed_at).total_seconds()
        sentry_sdk.capture_message(
            f"Successfully recovered failed event after {failed_event.retry_count} retries",
            level='info',
            extras={
                'failed_event_id': str(failed_event.pk),
                'connector_type': failed_event.connector_type,
                'event_type': failed_event.event_type,
                'retry_count': failed_event.retry_count,
                'time_to_recovery_seconds': time_to_recovery,
                'interactions_created': len(interactions),
            }
        )
        
        return True
        
    except Exception as e:
        # Mark as failed (increments retry count, schedules next retry)
        error_trace = traceback.format_exc()
        failed_event.mark_failed(str(e), error_trace)
        
        # Track retry failure with increasing severity
        severity = 'warning' if failed_event.retry_count < 3 else 'error'
        
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('retry_count', failed_event.retry_count)
            scope.set_tag('connector_type', failed_event.connector_type)
            scope.set_tag('event_type', failed_event.event_type)
            scope.set_tag('will_abandon', failed_event.status == 'abandoned')
            
            scope.set_context('failed_event', {
                'id': str(failed_event.pk),
                'first_failed_at': str(failed_event.first_failed_at),
                'retry_count': failed_event.retry_count,
                'max_retries': failed_event.get_max_retries(),
                'status': failed_event.status,
            })
            
            if failed_event.status == 'abandoned':
                # CRITICAL: Event abandoned after max retries
                sentry_sdk.capture_message(
                    f"ABANDONED: Event failed after {failed_event.retry_count} retries",
                    level='error',
                )
            else:
                # Regular retry failure
                sentry_sdk.capture_exception(e)
        
        logger.warning(
            f"Failed to reprocess event {failed_event.pk} (attempt {failed_event.retry_count}). "
            f"Error: {str(e)}. "
            f"{'Will retry at ' + str(failed_event.next_retry_at) if failed_event.status == 'failed' else 'Abandoned after max retries'}"
        )
        
        return False


def _retry_web_event(failed_event: FailedEvent):
    """
    Retry a web event by routing to the appropriate processor.
    
    Args:
        failed_event: FailedEvent instance with connector_type='web'
    
    Returns:
        list: List of created WebInteraction instances
    """
    from websites.models import WebInteraction
    
    # Map event types to processor methods
    processor_map = {
        'page_view': WebInteraction.process_page_view_event,
        'page_read': WebInteraction.process_page_read_event,
        'click': WebInteraction.process_click_event,
        'form_submit': WebInteraction.process_form_submit_event,
        'download': WebInteraction.process_download_event,
        'video_play': WebInteraction.process_video_play_event,
        'search': WebInteraction.process_search_event,
        'newsletter_signup': WebInteraction.process_newsletter_signup_event,
    }
    
    processor = processor_map.get(failed_event.event_type)
    if not processor:
        raise ValueError(f"Unknown web event type: {failed_event.event_type}")
    
    # Process the event
    with transaction.atomic():
        interactions = processor(failed_event.raw_payload)
    
    return interactions


def get_events_ready_for_retry():
    """
    Get all failed events that are ready for retry.
    
    Filters events by:
    - Status: 'failed' (not 'pending', 'processing', 'success', or 'abandoned')
    - next_retry_at: Due now or overdue
    - is_active: True
    
    Returns:
        QuerySet: FailedEvent instances ready for retry, ordered by retry time
    """
    return FailedEvent.objects.filter(
        status='failed',
        next_retry_at__lte=timezone.now(),
        is_active=True
    ).order_by('next_retry_at')


def get_abandoned_events():
    """
    Get all abandoned events (max retries exceeded).
    
    These events require manual intervention through the admin interface.
    
    Returns:
        QuerySet: FailedEvent instances with status='abandoned'
    """
    return FailedEvent.objects.filter(
        status='abandoned',
        is_active=True
    ).order_by('-first_failed_at')


def get_failure_stats():
    """
    Get statistics about failed events for monitoring.
    
    Returns:
        dict: Statistics about failed events
    """
    from django.db.models import Count, Avg
    from datetime import timedelta
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    return {
        'total_pending': FailedEvent.objects.filter(status='pending', is_active=True).count(),
        'total_failed': FailedEvent.objects.filter(status='failed', is_active=True).count(),
        'total_abandoned': FailedEvent.objects.filter(status='abandoned', is_active=True).count(),
        'total_processing': FailedEvent.objects.filter(status='processing', is_active=True).count(),
        'total_success_24h': FailedEvent.objects.filter(
            status='success',
            processed_at__gte=last_24h,
            is_active=True
        ).count(),
        'by_connector_type': dict(
            FailedEvent.objects.filter(is_active=True)
            .values('connector_type', 'status')
            .annotate(count=Count('id'))
            .values_list('connector_type', 'count')
        ),
        'avg_retries_to_success': FailedEvent.objects.filter(
            status='success',
            is_active=True
        ).aggregate(avg=Avg('retry_count'))['avg'] or 0,
    }

