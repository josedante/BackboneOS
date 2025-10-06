"""
Celery tasks for connectors app - handles automatic retry of failed events.
"""

from celery import shared_task
import sentry_sdk
from django.utils import timezone
import logging

from .fallback import get_events_ready_for_retry, retry_failed_event

logger = logging.getLogger(__name__)


@shared_task(
    name='connectors.retry_failed_events',
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def retry_failed_events_task(self):
    """
    Periodic task to automatically retry failed events.
    
    Runs every 5 minutes via Celery Beat to process events that are ready for retry.
    
    Returns:
        dict: Summary of retry results with success/failure counts
    """
    # Start Sentry transaction for performance monitoring
    with sentry_sdk.start_transaction(
        op="task",
        name="retry_failed_events",
        description="Automatic retry of failed connector events"
    ) as transaction:
        
        try:
            # Get events ready for retry (limit to 50 per batch)
            events_to_retry = get_events_ready_for_retry()[:50]
            
            if not events_to_retry:
                logger.debug("No failed events ready for retry")
                return {'success': 0, 'failed': 0, 'total': 0}
            
            logger.info(f"Starting retry batch: {len(events_to_retry)} events")
            
            # Track results
            success_count = 0
            failure_count = 0
            
            # Process each event
            for event in events_to_retry:
                with sentry_sdk.start_span(
                    op="retry_event",
                    description=f"{event.connector_type}.{event.event_type}"
                ) as span:
                    span.set_tag('event_id', str(event.pk))
                    span.set_tag('connector_type', event.connector_type)
                    span.set_tag('event_type', event.event_type)
                    span.set_tag('retry_count', event.retry_count)
                    
                    try:
                        success = retry_failed_event(event)
                        
                        if success:
                            success_count += 1
                            span.set_tag('result', 'success')
                        else:
                            failure_count += 1
                            span.set_tag('result', 'failed')
                            
                    except Exception as e:
                        failure_count += 1
                        span.set_tag('result', 'error')
                        
                        # Log error to Sentry
                        sentry_sdk.capture_exception(
                            e,
                            extras={
                                'event_id': str(event.pk),
                                'connector_type': event.connector_type,
                                'event_type': event.event_type,
                                'retry_count': event.retry_count
                            }
                        )
                        
                        logger.error(
                            f"Exception during retry of event {event.pk}: {str(e)}",
                            exc_info=True
                        )
            
            # Calculate metrics
            total_processed = success_count + failure_count
            failure_rate = failure_count / total_processed if total_processed > 0 else 0
            
            # Set transaction data
            transaction.set_data('success_count', success_count)
            transaction.set_data('failure_count', failure_count)
            transaction.set_data('failure_rate', failure_rate)
            
            # Alert on high failure rate (>50%)
            if failure_rate > 0.5 and total_processed >= 5:
                sentry_sdk.capture_message(
                    f"High failure rate in event retry batch: {failure_rate:.1%} ({failure_count}/{total_processed} failed)",
                    level='warning',
                    extras={
                        'success_count': success_count,
                        'failure_count': failure_count,
                        'total_processed': total_processed,
                        'failure_rate': failure_rate,
                        'batch_time': timezone.now().isoformat()
                    }
                )
            
            # Log summary
            logger.info(
                f"Retry batch completed: {success_count} succeeded, {failure_count} failed "
                f"(failure rate: {failure_rate:.1%})"
            )
            
            return {
                'success': success_count,
                'failed': failure_count,
                'total': total_processed,
                'failure_rate': failure_rate
            }
            
        except Exception as e:
            # Critical error in the task itself
            logger.critical(f"Critical error in retry_failed_events_task: {str(e)}", exc_info=True)
            
            # Capture to Sentry with high priority
            with sentry_sdk.push_scope() as scope:
                scope.level = 'error'
                scope.set_tag('task_error', 'true')
                sentry_sdk.capture_exception(e)
            
            # Re-raise to trigger Celery retry mechanism
            raise self.retry(exc=e)


@shared_task(name='connectors.retry_single_event')
def retry_single_event_task(event_id):
    """
    Task to retry a single failed event (useful for manual intervention).
    
    Args:
        event_id: UUID of the FailedEvent to retry
        
    Returns:
        dict: Retry result with success status
    """
    from .models import FailedEvent
    
    with sentry_sdk.start_transaction(op="task", name="retry_single_event"):
        try:
            event = FailedEvent.objects.get(pk=event_id, status__in=['pending', 'retrying'])
            success = retry_failed_event(event)
            
            logger.info(f"Manual retry of event {event_id}: {'SUCCESS' if success else 'FAILED'}")
            
            return {
                'event_id': str(event_id),
                'success': success,
                'status': event.status,
                'retry_count': event.retry_count
            }
            
        except FailedEvent.DoesNotExist:
            logger.error(f"Event {event_id} not found or not retryable")
            return {
                'event_id': str(event_id),
                'success': False,
                'error': 'Event not found or not retryable'
            }
        
        except Exception as e:
            logger.error(f"Error in manual retry of event {event_id}: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            
            return {
                'event_id': str(event_id),
                'success': False,
                'error': str(e)
            }

