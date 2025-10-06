# 🔄 Event Fallback & Recovery System

> **Version**: 1.0  
> **Last Updated**: October 2025  
> **Status**: ✅ Production Ready

## Overview

The Event Fallback & Recovery System provides automatic retry and recovery mechanisms for failed event processing. When critical system errors occur during event processing (5xx errors), events are automatically stored for retry with exponential backoff, ensuring no data loss even during temporary system failures.

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Core Components](#core-components)
3. [Error Classification](#error-classification)
4. [Retry Strategy](#retry-strategy)
5. [API Reference](#api-reference)
6. [Celery Tasks](#celery-tasks)
7. [Admin Interface](#admin-interface)
8. [Configuration](#configuration)
9. [Monitoring](#monitoring)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Architecture

### System Flow

```
┌─────────────┐
│ Event API   │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│             Event Processing                         │
│  ┌───────────────────────────────────────────────┐ │
│  │ Success? → 201 Created ✅                      │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ Client Error (4xx)? → 400 Bad Request ⚠️       │ │
│  │ (Logged to Sentry, NOT stored in fallback)    │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ System Error (5xx)?                           │ │
│  │   ↓                                            │ │
│  │ Store in FailedEvent → 202 Accepted 🔄        │ │
│  │   ↓                                            │ │
│  │ Sentry Alert (error level)                    │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ Catastrophic Failure?                         │ │
│  │   (Both processing AND fallback failed)       │ │
│  │   ↓                                            │ │
│  │ Sentry Alert (fatal level) → 500 Error 💥     │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Celery Beat     │
│  (Every 5 min)   │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Retry Failed Events Task                   │
│  ┌────────────────────────────────────────┐ │
│  │ 1. Get events ready for retry          │ │
│  │ 2. Process each event (max 50/batch)   │ │
│  │ 3. Update status & schedule next retry │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Event Reprocessing              │
│  Success → Mark as 'processed' ✅ │
│  Failure → Exponential backoff ⏱️ │
│  Max retries → Mark as 'failed' ❌ │
└──────────────────────────────────┘
```

### Key Principles

1. **No Data Loss**: All critical failures are captured and queued for retry
2. **Graceful Degradation**: System returns 202 Accepted to acknowledge receipt
3. **Exponential Backoff**: Intelligent retry scheduling prevents system overload
4. **Comprehensive Monitoring**: Sentry integration at all error levels
5. **Manual Intervention**: Admin interface for managing failed events

## Core Components

### 1. FailedEvent Model

Database model for storing failed events.

```python
from connectors.models import FailedEvent

# Fields:
# - id (UUID): Unique identifier
# - connector_type (str): 'web', 'email', 'payment', etc.
# - event_type (str): 'page_view', 'form_submit', etc.
# - source_identifier (str): Source identifier (domain, app_id, etc.)
# - raw_payload (JSON): Original event data
# - status (str): 'pending', 'retrying', 'processed', 'failed', 'abandoned'
# - error_message (str): Error message from failure
# - error_trace (text): Full error traceback
# - retry_count (int): Number of retry attempts
# - first_failed_at (datetime): Initial failure timestamp
# - last_retry_at (datetime): Last retry attempt timestamp
# - next_retry_at (datetime): Scheduled next retry
# - processed_at (datetime): Successful processing timestamp
# - interaction_ids (JSON): Created interaction IDs (after success)
```

#### Status Values

| Status | Description |
|--------|-------------|
| `pending` | Waiting for initial retry |
| `retrying` | Currently being retried |
| `processed` | Successfully processed |
| `failed` | Exceeded max retries |
| `abandoned` | Manually abandoned (won't retry) |

### 2. Fallback Functions

**Module**: `connectors/fallback.py`

#### store_failed_event()

Stores a failed event for later retry.

```python
from connectors.fallback import store_failed_event

failed_event = store_failed_event(
    connector_type='web',
    event_type='page_view',
    raw_payload={'full_url': 'https://example.com', ...},
    error_message='Database connection timeout',
    error_trace='Traceback (most recent call last)...',
    source_identifier='example.com'
)
```

**Parameters:**
- `connector_type` (str): Connector type identifier
- `event_type` (str): Event type identifier
- `raw_payload` (dict): Original event data
- `error_message` (str): Error description
- `error_trace` (str): Full error traceback
- `source_identifier` (str): Source identifier

**Returns:** `FailedEvent` instance

**Sentry Integration:**
- Logs storage with `info` level
- Includes event ID in context

#### retry_failed_event()

Attempts to reprocess a failed event.

```python
from connectors.fallback import retry_failed_event
from connectors.models import FailedEvent

event = FailedEvent.objects.get(pk=event_id)
success = retry_failed_event(event)

if success:
    print(f"Event processed successfully!")
else:
    print(f"Event retry failed, will retry later")
```

**Parameters:**
- `event` (FailedEvent): Event to retry

**Returns:** `bool` - True if successful, False otherwise

**Behavior:**
- Routes to correct processor based on `connector_type` and `event_type`
- Updates status to 'retrying' during processing
- On success: Sets status to 'processed', stores interaction IDs
- On failure: Increments retry count, schedules next retry
- On max retries: Sets status to 'failed'

**Sentry Integration:**
- Tracks retry attempts with breadcrumbs
- Logs success with `info` level
- Logs failures with `warning` or `error` level

#### get_events_ready_for_retry()

Queries for events ready to be retried.

```python
from connectors.fallback import get_events_ready_for_retry

events = get_events_ready_for_retry()
print(f"Found {len(events)} events ready for retry")
```

**Returns:** `QuerySet[FailedEvent]` - Events with status 'pending' or 'retrying' and `next_retry_at <= now`

### 3. Model Methods

#### FailedEvent.get_max_retries()

Returns maximum retry count for the connector type.

```python
event = FailedEvent.objects.get(pk=event_id)
max_retries = event.get_max_retries()
print(f"Max retries: {max_retries}")
```

**Configuration:** `settings.FAILED_EVENT_RETRY_CONFIG`

#### FailedEvent.calculate_next_retry()

Calculates next retry time using exponential backoff.

```python
event = FailedEvent(retry_count=2)
next_retry = event.calculate_next_retry()
# Returns ~4 minutes from now (base_delay * 2^retry_count)
```

**Formula:** `next_retry = now + (60 seconds * 2^retry_count)`

| Retry # | Delay |
|---------|-------|
| 1 | ~1 minute |
| 2 | ~2 minutes |
| 3 | ~4 minutes |
| 4 | ~8 minutes |
| 5 | ~16 minutes |

#### FailedEvent.mark_processing()

Marks event as currently being retried.

```python
event.mark_processing()
# Sets status='retrying', last_retry_at=now
```

#### FailedEvent.mark_success()

Marks event as successfully processed.

```python
event.mark_success(interaction_ids=['uuid1', 'uuid2'])
# Sets status='processed', processed_at=now, stores interaction_ids
```

#### FailedEvent.mark_failed()

Marks event as failed (exceeded max retries or permanent failure).

```python
event.mark_failed(error_message="Permanent error", error_trace="...")
# Sets status='failed', updates error details
```

## Error Classification

### 1. Client Errors (4xx) - NOT Stored in Fallback

**Examples:**
- Invalid JSON (`JSONDecodeError`)
- Missing required fields (`ValueError`)
- Invalid data format (`ValueError`)

**Handling:**
```python
except json.JSONDecodeError as e:
    # Log to Sentry as warning
    sentry_sdk.capture_message("Invalid JSON", level='warning')
    return JsonResponse({'error': 'Invalid JSON data'}, status=400)

except ValueError as e:
    # Log to Sentry as warning
    sentry_sdk.capture_message(f"Invalid data: {e}", level='warning')
    return JsonResponse({'error': 'Invalid data'}, status=400)
```

**Response:** `400 Bad Request` (client should fix the request)

### 2. System Errors (5xx) - Stored in Fallback

**Examples:**
- Database connection errors
- Timeout errors
- Import errors
- Unexpected exceptions

**Handling:**
```python
except Exception as e:
    error_trace = traceback.format_exc()
    
    # Log to Sentry with context
    with sentry_sdk.push_scope() as scope:
        scope.set_tag('has_fallback', 'true')
        sentry_sdk.capture_exception(e)
    
    # Store in fallback
    failed_event = store_failed_event(...)
    
    return JsonResponse({
        'success': False,
        'error': 'Event processing failed but has been queued for retry',
        'fallback_id': str(failed_event.pk)
    }, status=202)  # Accepted - will process later
```

**Response:** `202 Accepted` (acknowledged, will retry)

### 3. Catastrophic Failures - Both Processing and Fallback Failed

**Scenario:** System error during processing AND unable to store in fallback database.

**Handling:**
```python
except Exception as fallback_error:
    # Critical alert to Sentry
    with sentry_sdk.push_scope() as scope:
        scope.level = 'fatal'
        scope.set_tag('catastrophic_failure', 'true')
        sentry_sdk.capture_message(
            "CATASTROPHIC: Failed to process AND store in fallback!",
            level='fatal'
        )
    
    return JsonResponse({
        'error': 'Internal server error'
    }, status=500)
```

**Response:** `500 Internal Server Error`

## Retry Strategy

### Exponential Backoff Schedule

```
Retry Attempt | Delay      | Cumulative Time
─────────────┼────────────┼────────────────
1             | ~1 minute  | 1 minute
2             | ~2 minutes | 3 minutes
3             | ~4 minutes | 7 minutes
4             | ~8 minutes | 15 minutes
5             | ~16 minutes| 31 minutes
```

### Configuration

Per-connector-type maximum retry attempts:

```python
# settings.py
FAILED_EVENT_RETRY_CONFIG = {
    'web': 5,          # Web events: 5 retries (~31 min total)
    'email': 3,        # Email events: 3 retries (~7 min total)
    'payment': 10,     # Payment events: 10 retries (critical)
    'default': 3       # Other events: 3 retries
}
```

### Automatic Processing

Celery Beat runs the retry task every 5 minutes:

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'retry-failed-events': {
        'task': 'connectors.retry_failed_events',
        'schedule': 300.0,  # 5 minutes
    }
}
```

## API Reference

### HTTP Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| `201` | Created | Event processed successfully |
| `202` | Accepted | Event stored for retry (system error occurred) |
| `400` | Bad Request | Client error (fix request and retry) |
| `500` | Server Error | Catastrophic failure (contact support) |

### Response Format (202 Accepted)

```json
{
  "success": false,
  "error": "Event processing failed but has been queued for retry",
  "fallback_id": "6d542e78-8a12-4743-81e8-3a4c79077779",
  "message": "Your event will be processed automatically"
}
```

### Response Format (500 Error)

```json
{
  "error": "Internal server error",
  "message": "Unable to process event"
}
```

## Celery Tasks

### retry_failed_events_task

**Task Name:** `connectors.retry_failed_events`

**Schedule:** Every 5 minutes (Celery Beat)

**Batch Size:** 50 events per run

**Function:**
```python
from connectors.tasks import retry_failed_events_task

# Manual trigger
result = retry_failed_events_task()
# Returns: {'success': 5, 'failed': 2, 'total': 7, 'failure_rate': 0.286}
```

**Monitoring:**
- Sentry transaction for performance tracking
- Automatic alerts if failure rate > 50%
- Detailed error logging

**Process:**
1. Query events ready for retry (max 50)
2. Process each event sequentially
3. Track success/failure counts
4. Calculate failure rate
5. Alert if failure rate > 50%

### retry_single_event_task

**Task Name:** `connectors.retry_single_event`

**Purpose:** Manual retry of individual events (from admin or API)

**Function:**
```python
from connectors.tasks import retry_single_event_task

# Retry specific event
result = retry_single_event_task(event_id='uuid-here')
# Returns: {'event_id': 'uuid', 'success': True, 'status': 'processed'}
```

## Admin Interface

### Access

**URL:** `/admin/connectors/failedevent/`

### Features

#### List View

- **Columns:**
  - ID (UUID)
  - Connector Type
  - Event Type
  - Status (with color coding)
  - Retry Count / Max Retries
  - First Failed At
  - Next Retry At
  - Source Identifier (truncated)

- **Filters:**
  - Connector Type
  - Event Type
  - Status
  - First Failed At (date range)
  - Next Retry At (date range)

- **Search:**
  - Event ID
  - Source Identifier
  - Error Message
  - Interaction IDs

#### Detail View

- **Event Information:** ID, connector type, event type, source, status
- **Retry Configuration:** Retry count, max retries, next retry time
- **Timeline:** First failed, last retry, processed timestamps
- **Error Details:** Error message, formatted traceback (collapsible)
- **Event Payload:** Formatted JSON (collapsible)
- **Results:** Interaction IDs created (if successful)

#### Custom Actions

##### 1. Retry Selected Events

Manually trigger retry for selected events.

**Usage:**
1. Select events with status 'pending' or 'retrying'
2. Choose "Retry selected events" from actions dropdown
3. Click "Go"

**Result:** Events are immediately reprocessed.

##### 2. Abandon Selected Events

Mark events as abandoned (won't retry).

**Usage:**
1. Select events to abandon
2. Choose "Abandon selected events"
3. Click "Go"

**Result:** Status changed to 'abandoned', removed from retry queue.

##### 3. Reset Retry Count

Give failed events another chance by resetting retry count.

**Usage:**
1. Select events with status 'failed'
2. Choose "Reset retry count (give another chance)"
3. Click "Go"

**Result:** 
- Retry count reset to 0
- Status changed to 'pending'
- Next retry scheduled for immediate processing

### Status Color Coding

| Status | Color | Badge |
|--------|-------|-------|
| `pending` | Blue | 🔵 |
| `retrying` | Yellow | 🟡 |
| `processed` | Green | 🟢 |
| `failed` | Red | 🔴 |
| `abandoned` | Gray | ⚫ |

## Configuration

### Django Settings

```python
# backend/settings.py

# Per-connector-type max retries
FAILED_EVENT_RETRY_CONFIG = {
    'web': 5,          # 5 retries for web events
    'email': 3,        # 3 retries for email
    'payment': 10,     # 10 retries for critical payment events
    'default': 3       # Default for unlisted connectors
}

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    'retry-failed-events': {
        'task': 'connectors.retry_failed_events',
        'schedule': 300.0,  # Every 5 minutes
        'options': {
            'expires': 60.0,  # Task expires after 1 minute
        }
    }
}

# Sentry configuration (ensure it's enabled)
SENTRY_DSN = 'https://your-sentry-dsn'
SENTRY_ENVIRONMENT = 'production'
SENTRY_TRACES_SAMPLE_RATE = 0.1
```

## Monitoring

### Sentry Integration

#### Error Levels

| Level | Trigger | Action |
|-------|---------|--------|
| `warning` | Client errors (4xx), retry failures | Review logs |
| `error` | System errors (5xx), stored in fallback | Investigate root cause |
| `fatal` | Catastrophic failures (processing + fallback fail) | Immediate action required |

#### Tags

- `connector_type`: Connector identifier
- `event_type`: Event type
- `has_fallback`: 'true' for events stored in fallback
- `catastrophic_failure`: 'true' for double failures
- `task_error`: 'true' for Celery task errors

#### Context

- `event_data`: Event payload details (URL, session, etc.)
- `original_error`: Original error in catastrophic failures
- `fallback_error`: Fallback storage error in catastrophic failures

#### Transactions

- `retry_failed_events`: Performance monitoring for retry batches
- `retry_single_event`: Performance monitoring for manual retries

### Metrics to Monitor

1. **Fallback Queue Size:**
   ```python
   pending_count = FailedEvent.objects.filter(status='pending').count()
   retrying_count = FailedEvent.objects.filter(status='retrying').count()
   ```

2. **Success Rate:**
   ```python
   total = FailedEvent.objects.count()
   processed = FailedEvent.objects.filter(status='processed').count()
   success_rate = (processed / total * 100) if total > 0 else 0
   ```

3. **Retry Distribution:**
   ```python
   from django.db.models import Count
   FailedEvent.objects.values('retry_count').annotate(count=Count('id'))
   ```

4. **Failure Rate by Connector:**
   ```python
   from django.db.models import Count, Q
   FailedEvent.objects.values('connector_type').annotate(
       total=Count('id'),
       failed=Count('id', filter=Q(status='failed'))
   )
   ```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Queue Size | > 100 events | > 500 events |
| Failure Rate | > 10% | > 25% |
| Retry Batch Failure | > 30% | > 50% |
| Catastrophic Failures | > 0 | > 5 per hour |

## Best Practices

### 1. Event Processing Views

```python
# ✅ Good: Complete error handling with fallback
def post(self, request):
    try:
        data = json.loads(request.body)
        # ... validation
        interactions = WebInteraction.process_page_view_event(data)
        return JsonResponse({...}, status=201)
    
    except json.JSONDecodeError as e:
        # Client error - don't store in fallback
        sentry_sdk.capture_message("Invalid JSON", level='warning')
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except ValueError as e:
        # Validation error - don't store in fallback
        sentry_sdk.capture_message(f"Invalid data: {e}", level='warning')
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
    except Exception as e:
        # System error - store in fallback
        error_trace = traceback.format_exc()
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('has_fallback', 'true')
            sentry_sdk.capture_exception(e)
        
        try:
            failed_event = store_failed_event(...)
            return JsonResponse({...}, status=202)
        except Exception as fallback_error:
            # Catastrophic failure
            sentry_sdk.capture_message("CATASTROPHIC!", level='fatal')
            return JsonResponse({'error': 'Server error'}, status=500)

# ❌ Bad: No fallback handling
def post(self, request):
    data = json.loads(request.body)
    interactions = WebInteraction.process_page_view_event(data)
    return JsonResponse({...}, status=201)
    # Missing all error handling!
```

### 2. Manual Intervention

```python
# ✅ Good: Investigate before retrying
from connectors.models import FailedEvent

# Find problematic events
failed_events = FailedEvent.objects.filter(
    status='failed',
    connector_type='web'
).order_by('-first_failed_at')[:10]

for event in failed_events:
    print(f"Event: {event.id}")
    print(f"Error: {event.error_message}")
    print(f"Retries: {event.retry_count}")
    print(f"Payload: {event.raw_payload}")
    print("---")
    
# Fix root cause, then reset retry count via admin
```

### 3. Monitoring Dashboard

```python
# ✅ Good: Regular monitoring
from django.utils import timezone
from datetime import timedelta

def get_fallback_health():
    now = timezone.now()
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)
    
    return {
        'pending': FailedEvent.objects.filter(status='pending').count(),
        'retrying': FailedEvent.objects.filter(status='retrying').count(),
        'processed_last_hour': FailedEvent.objects.filter(
            status='processed',
            processed_at__gte=hour_ago
        ).count(),
        'failed_last_day': FailedEvent.objects.filter(
            status='failed',
            first_failed_at__gte=day_ago
        ).count()
    }
```

### 4. Cleanup Policy

```python
# ✅ Good: Regular cleanup of old processed events
from django.core.management.base import BaseCommand
from connectors.models import FailedEvent
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Keep processed events for 90 days
        cutoff = timezone.now() - timedelta(days=90)
        deleted = FailedEvent.objects.filter(
            status='processed',
            processed_at__lt=cutoff
        ).delete()
        
        self.stdout.write(f"Deleted {deleted[0]} old processed events")
```

## Troubleshooting

### Issue: Events Stuck in 'retrying' Status

**Symptoms:**
- Events show status 'retrying' for extended periods
- Retry task appears to hang

**Diagnosis:**
```python
from connectors.models import FailedEvent
from django.utils import timezone

stuck_events = FailedEvent.objects.filter(
    status='retrying',
    last_retry_at__lt=timezone.now() - timedelta(minutes=10)
)

for event in stuck_events:
    print(f"Event {event.id} stuck since {event.last_retry_at}")
```

**Solution:**
1. Check Celery worker logs for errors
2. Manually reset stuck events:
   ```python
   stuck_events.update(status='pending', next_retry_at=timezone.now())
   ```

### Issue: High Failure Rate

**Symptoms:**
- Many events reaching 'failed' status
- Sentry alerts for high failure rate

**Diagnosis:**
```python
from django.db.models import Count

# Get common error patterns
FailedEvent.objects.filter(status='failed').values(
    'error_message'
).annotate(count=Count('id')).order_by('-count')[:10]
```

**Solution:**
1. Identify common error message
2. Fix root cause in event processing
3. Reset failed events to give them another chance

### Issue: Queue Growing Too Large

**Symptoms:**
- Pending/retrying count > 100
- Processing falling behind

**Diagnosis:**
```python
from connectors.models import FailedEvent
from django.db.models import Count

# Distribution by connector type
FailedEvent.objects.filter(
    status__in=['pending', 'retrying']
).values('connector_type').annotate(count=Count('id'))
```

**Solution:**
1. Increase Celery worker instances
2. Reduce Celery Beat interval (e.g., every 2 minutes)
3. Increase batch size in retry task

### Issue: Catastrophic Failures

**Symptoms:**
- Sentry fatal alerts
- 500 errors returned to clients

**Diagnosis:**
1. Check database connectivity
2. Check disk space for fallback table
3. Check Sentry logs for both errors

**Solution:**
1. Restore database connectivity
2. Free up disk space
3. Once fixed, events should start processing normally

## Conclusion

The Event Fallback & Recovery System provides comprehensive protection against data loss during system failures. Key benefits:

- **Zero Data Loss**: All critical failures are captured
- **Automatic Recovery**: Background workers retry failed events
- **Intelligent Scheduling**: Exponential backoff prevents overload
- **Full Visibility**: Admin interface + Sentry monitoring
- **Manual Override**: Admin actions for special cases

The system is designed to handle temporary failures gracefully while alerting administrators to persistent issues requiring intervention.

## See Also

- **[README.md](README.md)** - Main connectors documentation
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[ADMIN_INTERFACE_GUIDE.md](ADMIN_INTERFACE_GUIDE.md)** - Admin interface guide

