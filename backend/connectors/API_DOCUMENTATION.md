# Touchpoint Resolution System - API Documentation v2.0

> **Version**: 2.0 (Subject-Agnostic Architecture)  
> **Last Updated**: January 2025  
> **Migration Guide**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for v1.0 → v2.0 migration

## Overview

The Touchpoint Resolution System provides a comprehensive API for automatic touchpoint creation and management. The v2.0 architecture uses a **subject-agnostic** approach where touchpoints are resolved from hints built directly from raw event data, rather than requiring objects to implement specific protocols.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Core API](#core-api)
3. [Protocols](#protocols)
4. [Resolvers](#resolvers)
5. [Mapping Providers](#mapping-providers)
6. [Models](#models)
7. [Management Commands](#management-commands)
8. [Performance Monitoring](#performance-monitoring)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

## Core Concepts

### Resolution Flow (v2.0)

```
Raw Event Data → TouchpointHint → Resolver → Touchpoint
                      ↓              ↓
                 (Structured)   (Mapping Rules)
```

### Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **TouchpointHint** | Dataclass containing touchpoint metadata | ✅ Core |
| **TouchpointResolverProtocol** | Interface for touchpoint resolution | ✅ Core |
| **MappingProviderProtocol** | Interface for mapping rule lookup | ✅ Core |
| **DefaultTouchpointResolver** | Subject-agnostic resolution logic | ✅ Core |
| **CachedTouchpointResolver** | Caching resolver for performance | ✅ Core |
| **DatabaseMappingProvider** | Database-backed mapping rules | ✅ Core |
| **CachedMappingProvider** | Cached mapping provider | ✅ Core |
| **TouchpointMappingRule** | Admin-configurable mapping rules | ✅ Model |

### ~~Removed Components~~ (v1.0)

- ❌ **TouchpointInferenceProtocol**: No longer required (v2.0 uses explicit parameters)
- ❌ **Subject-dependent resolution**: Replaced with hint-based resolution

## Core API

### TouchpointHint

Dataclass representing touchpoint metadata extracted from raw events.

#### Definition

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class TouchpointHint:
    """Immutable hint for touchpoint resolution."""
    
    code: Optional[str] = None
    channel_code: Optional[str] = None
    medium_code: Optional[str] = None
    touchpoint_type_code: Optional[str] = None
    label: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

#### Usage

```python
from connectors.protocols import TouchpointHint

# Create a hint
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View',
    metadata={'url': '/products', 'utm_campaign': 'summer_sale'}
)

# Hints are immutable
# hint.code = 'new_code'  # Raises AttributeError
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | `str` | No | Unique touchpoint code (e.g., 'web.page_view') |
| `channel_code` | `str` | No | Channel identifier (WHERE: 'web', 'email', etc.) |
| `medium_code` | `str` | No | Medium identifier (HOW: 'organic', 'cpc', etc.) |
| `touchpoint_type_code` | `str` | No | Touchpoint type (WHAT: 'web_page', 'email_open', etc.) |
| `label` | `str` | No | Human-readable label |
| `metadata` | `dict` | No | Additional metadata (defaults to empty dict) |

## Protocols

### TouchpointResolverProtocol

Interface for touchpoint resolvers.

```python
from typing import Protocol
from connectors.protocols import TouchpointHint
from interactions.models import Touchpoint

class TouchpointResolverProtocol(Protocol):
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        """
        Resolve a touchpoint from a hint.
        
        Args:
            hint: TouchpointHint with touchpoint metadata
            connector_type: Type of connector ('web', 'email', 'mobile', etc.)
            source_identifier: Source-specific identifier (domain, app_id, etc.)
        
        Returns:
            Touchpoint: Created or existing touchpoint
        """
        ...
```

### MappingProviderProtocol

Interface for mapping rule providers.

```python
from typing import Protocol, Optional
from connectors.models import TouchpointMappingRule

class MappingProviderProtocol(Protocol):
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        """
        Look up a mapping rule for the given parameters.
        
        Args:
            connector_type: Type of connector
            source_identifier: Source-specific identifier
            hint: TouchpointHint to match against
        
        Returns:
            TouchpointMappingRule or None if no match found
        """
        ...
```

## Resolvers

### DefaultTouchpointResolver

Standard touchpoint resolver with subject-agnostic API.

#### Initialization

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

resolver = DefaultTouchpointResolver(
    mapping_provider=DatabaseMappingProvider()
)
```

#### resolve()

```python
def resolve(
    self,
    hint: TouchpointHint,
    *,
    connector_type: str,
    source_identifier: str = ''
) -> Touchpoint
```

**Parameters:**
- `hint` (TouchpointHint): Touchpoint metadata
- `connector_type` (str, keyword-only): Connector type identifier
- `source_identifier` (str, keyword-only, optional): Source-specific identifier

**Returns:**
- `Touchpoint`: Created or existing touchpoint

**Example:**

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

hint = TouchpointHint(
    code='web.form_submit',
    channel_code='web',
    medium_code='cpc',
    touchpoint_type_code='web_form',
    label='Contact Form Submit'
)

touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)

print(f"Touchpoint: {touchpoint.code}")
print(f"Channel: {touchpoint.channel.code if touchpoint.channel else 'N/A'}")
print(f"Medium: {touchpoint.medium.code if touchpoint.medium else 'N/A'}")
```

### CachedTouchpointResolver

Resolver with built-in caching for high-performance scenarios.

#### Initialization

```python
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

resolver = CachedTouchpointResolver(
    mapping_provider=CachedMappingProvider(),
    cache_timeout=3600,  # 1 hour
    use_cache=True
)
```

#### Usage

```python
# Same API as DefaultTouchpointResolver
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)

# Cache is automatically managed
```

#### Configuration

```python
# Disable caching
resolver.use_cache = False

# Change cache timeout
resolver.cache_timeout = 7200  # 2 hours
```

## Mapping Providers

### DatabaseMappingProvider

Standard database-backed mapping rule provider.

#### Initialization

```python
from connectors.mapping_providers import DatabaseMappingProvider

provider = DatabaseMappingProvider(
    cache_timeout=3600,
    use_cache=True
)
```

#### lookup_mapping()

```python
def lookup_mapping(
    self,
    *,
    connector_type: str,
    source_identifier: str,
    hint: TouchpointHint
) -> Optional[TouchpointMappingRule]
```

**Priority Resolution:**
1. Specific source + event code match
2. Connector type + event code match
3. Global event code match

**Example:**

```python
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

provider = DatabaseMappingProvider()

hint = TouchpointHint(code='web.page_view')

# Look up mapping rule
rule = provider.lookup_mapping(
    connector_type='web',
    source_identifier='shop.example.com',
    hint=hint
)

if rule:
    print(f"Matched rule: {rule.touchpoint_code}")
    print(f"Priority: {rule.priority}")
else:
    print("No matching rule found")
```

### CachedMappingProvider

Database provider with caching.

```python
from connectors.mapping_providers import CachedMappingProvider

provider = CachedMappingProvider()

# Warm cache for better performance
provider.warm_cache()

# Use normally
rule = provider.lookup_mapping(
    connector_type='web',
    source_identifier='example.com',
    hint=hint
)
```

## Models

### TouchpointMappingRule

Model for admin-configurable mapping rules.

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `connector_type` | `CharField` | Yes | Connector type ('web', 'email', etc.) |
| `source_identifier` | `CharField` | No | Source-specific identifier |
| `event_code` | `CharField` | Yes | Event code to match |
| `touchpoint_code` | `CharField` | Yes | Target touchpoint code |
| `touchpoint_label` | `CharField` | No | Target touchpoint label |
| `channel_code` | `CharField` | No | Target channel code |
| `medium_code` | `CharField` | No | Target medium code |
| `touchpoint_type_code` | `CharField` | No | Target touchpoint type |
| `priority` | `IntegerField` | No | Rule priority (higher = more specific) |
| `is_active` | `BooleanField` | No | Whether rule is active |
| `metadata` | `JSONField` | No | Additional metadata |

#### Create Rule

```python
from connectors.models import TouchpointMappingRule

rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='shop.example.com',
    event_code='web.page_view',
    touchpoint_code='web.product_page',
    touchpoint_label='Product Page View',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    priority=200,
    is_active=True,
    metadata={'category': 'ecommerce'}
)
```

#### Query Rules

```python
# Active rules for web connector
web_rules = TouchpointMappingRule.objects.filter(
    connector_type='web',
    is_active=True
)

# High priority rules
priority_rules = TouchpointMappingRule.objects.filter(
    priority__gte=150
).order_by('-priority')

# Rules for specific source
source_rules = TouchpointMappingRule.objects.filter(
    source_identifier='example.com'
)
```

#### Update Rule

```python
rule = TouchpointMappingRule.objects.get(id=rule_id)
rule.priority = 250
rule.metadata['updated'] = True
rule.save()
```

#### Delete Rule

```python
rule = TouchpointMappingRule.objects.get(id=rule_id)
rule.delete()

# Or soft delete (deactivate)
rule.is_active = False
rule.save()
```

## Management Commands

### test_touchpoint_resolution

Test the touchpoint resolution system.

```bash
# Basic test
python manage.py test_touchpoint_resolution

# Test specific scenario
python manage.py test_touchpoint_resolution --scenario=web

# Verbose output
python manage.py test_touchpoint_resolution --verbose

# Create sample mapping rules
python manage.py test_touchpoint_resolution --create-mapping-rules
```

**Scenarios:**
- `basic`: Basic touchpoint creation
- `mapping`: Mapping rule application
- `web`: Web-specific scenarios
- `email`: Email-specific scenarios
- `whatsapp`: WhatsApp-specific scenarios
- `all`: All scenarios

### manage_mapping_rules

Manage touchpoint mapping rules.

```bash
# List all rules
python manage.py manage_mapping_rules list

# List web rules only
python manage.py manage_mapping_rules list --connector-type=web

# Create new rule
python manage.py manage_mapping_rules create \
    --connector-type=web \
    --source-identifier=example.com \
    --event-code=web.page_view \
    --touchpoint-code=web.home_page \
    --touchpoint-label="Home Page View" \
    --channel-code=web \
    --medium-code=organic \
    --priority=150

# Update rule
python manage.py manage_mapping_rules update --id=123 --priority=200

# Delete rule
python manage.py manage_mapping_rules delete --id=123

# Activate/deactivate rule
python manage.py manage_mapping_rules activate --id=123
python manage.py manage_mapping_rules deactivate --id=123
```

### manage_touchpoint_cache

Manage touchpoint resolution cache.

```bash
# Show cache stats
python manage.py manage_touchpoint_cache stats

# Clear cache
python manage.py manage_touchpoint_cache clear

# Warm cache
python manage.py manage_touchpoint_cache warm

# Performance test
python manage.py manage_touchpoint_cache test-performance --iterations=1000
```

### monitor_touchpoint_system

Monitor system health and metrics.

```bash
# System health check
python manage.py monitor_touchpoint_system health

# View metrics
python manage.py monitor_touchpoint_system metrics

# Metrics for specific period
python manage.py monitor_touchpoint_system metrics --hours=24

# Export metrics
python manage.py monitor_touchpoint_system metrics --export=metrics.json
```

### backfill_touchpoints

Backfill missing touchpoints for existing interactions.

```bash
# Backfill all
python manage.py backfill_touchpoints

# Specific connector type
python manage.py backfill_touchpoints --connector-type=web

# With batch size
python manage.py backfill_touchpoints --batch-size=100

# Limit number of records
python manage.py backfill_touchpoints --limit=1000

# Dry run
python manage.py backfill_touchpoints --dry-run
```

## Performance Monitoring

### Track Resolution

```python
from connectors.metrics import track_resolution

with track_resolution('web', {'url': 'example.com'}) as tracker:
    # Your resolution logic
    touchpoint = resolver.resolve(
        hint,
        connector_type='web',
        source_identifier='example.com'
    )
    
    # Record success
    tracker.record_success(
        cache_hit=False,
        mapping_applied=True,
        touchpoint_created=True
    )
```

### Get Metrics

```python
from connectors.monitoring_models import TouchpointResolutionMetrics
from datetime import datetime, timedelta

# Latest metrics
latest = TouchpointResolutionMetrics.objects.latest('period_start')

# Metrics for last 24 hours
yesterday = datetime.now() - timedelta(days=1)
recent_metrics = TouchpointResolutionMetrics.objects.filter(
    period_start__gte=yesterday
)

# Calculate success rate
for metric in recent_metrics:
    success_rate = (metric.successful_resolutions / metric.total_resolutions * 100
                   if metric.total_resolutions > 0 else 0)
    print(f"{metric.connector_type}: {success_rate:.2f}% success rate")
```

### Get Events

```python
from connectors.monitoring_models import TouchpointResolutionEvent

# Recent events
recent = TouchpointResolutionEvent.objects.filter(
    occurred_at__gte=datetime.now() - timedelta(hours=1)
).order_by('-occurred_at')

# Errors only
errors = TouchpointResolutionEvent.objects.filter(
    error_occurred=True
).order_by('-occurred_at')[:10]

# Slow resolutions
slow = TouchpointResolutionEvent.objects.filter(
    resolution_time_ms__gte=1000  # > 1 second
).order_by('-resolution_time_ms')
```

## Error Handling

### HTTP Response Codes (Event API)

When processing events through API endpoints (e.g., `PageViewEventView`), the system uses standard HTTP codes with intelligent fallback:

| Code | Status | Meaning | Client Action |
|------|--------|---------|---------------|
| `201` | Created | Event processed successfully | Continue normal operation |
| `202` | Accepted | Event stored for automatic retry (system error) | No action needed - event will be reprocessed |
| `400` | Bad Request | Invalid input (client error) | Fix request and retry |
| `500` | Server Error | Catastrophic failure (processing + fallback failed) | Contact support |

#### 201 Created Response

Successful event processing:

```json
{
  "success": true,
  "message": "Successfully processed page view event",
  "interactions_created": 3,
  "interaction_ids": [
    "uuid-1",
    "uuid-2",
    "uuid-3"
  ]
}
```

#### 202 Accepted Response (Fallback)

System error occurred, event stored for retry:

```json
{
  "success": false,
  "error": "Event processing failed but has been queued for retry",
  "fallback_id": "6d542e78-8a12-4743-81e8-3a4c79077779",
  "message": "Your event will be processed automatically"
}
```

**What happens next:**
1. Event is stored in `FailedEvent` table
2. Celery Beat picks it up within 5 minutes
3. System retries with exponential backoff
4. Up to 5 retry attempts (configurable per connector)
5. Success → interactions created automatically
6. Failure → logged to Sentry, visible in admin

#### 400 Bad Request Response

Client sent invalid data:

```json
{
  "error": "Invalid JSON data"
}
```

or

```json
{
  "error": "Invalid data",
  "message": "Missing required field: full_url"
}
```

**Client action:** Fix the request and retry immediately.

#### 500 Server Error Response (Catastrophic)

Both event processing AND fallback storage failed:

```json
{
  "error": "Internal server error",
  "message": "Unable to process event"
}
```

**Client action:** Contact support - indicates serious system issue.

### Error Classification

The system classifies errors into three categories:

#### 1. Client Errors (4xx) - NOT Stored in Fallback

**Triggers:**
- Invalid JSON (`json.JSONDecodeError`)
- Missing required fields (`ValueError`)
- Invalid data format (`ValueError`)

**Example:**
```python
except json.JSONDecodeError as e:
    sentry_sdk.capture_message("Invalid JSON", level='warning')
    return JsonResponse({'error': 'Invalid JSON data'}, status=400)

except ValueError as e:
    sentry_sdk.capture_message(f"Invalid data: {e}", level='warning')
    return JsonResponse({'error': 'Invalid data'}, status=400)
```

**Sentry Level:** `warning` (client-side issue)

#### 2. System Errors (5xx) - Stored in Fallback

**Triggers:**
- Database connection errors
- Timeout errors
- Import errors
- Unexpected exceptions

**Example:**
```python
except Exception as e:
    error_trace = traceback.format_exc()
    
    # Log to Sentry
    with sentry_sdk.push_scope() as scope:
        scope.set_tag('has_fallback', 'true')
        sentry_sdk.capture_exception(e)
    
    # Store in fallback
    failed_event = store_failed_event(
        connector_type='web',
        event_type='page_view',
        raw_payload=data,
        error_message=str(e),
        error_trace=error_trace,
        source_identifier=data.get('website_base', '')
    )
    
    return JsonResponse({
        'success': False,
        'error': 'Event processing failed but has been queued for retry',
        'fallback_id': str(failed_event.pk)
    }, status=202)
```

**Sentry Level:** `error` (system issue, but recoverable)

#### 3. Catastrophic Failures - Both Processing and Fallback Failed

**Triggers:**
- Database completely unavailable
- Disk space exhausted
- System resources critically low

**Example:**
```python
except Exception as fallback_error:
    # Critical Sentry alert
    with sentry_sdk.push_scope() as scope:
        scope.level = 'fatal'
        scope.set_tag('catastrophic_failure', 'true')
        sentry_sdk.capture_message(
            "CATASTROPHIC: Failed to process AND store in fallback!",
            level='fatal'
        )
    
    return JsonResponse({
        'error': 'Internal server error',
        'message': 'Unable to process event'
    }, status=500)
```

**Sentry Level:** `fatal` (immediate intervention required)

### Fallback System API

For detailed fallback system documentation, see **[FALLBACK_SYSTEM.md](FALLBACK_SYSTEM.md)**.

#### store_failed_event()

Stores a failed event for automatic retry.

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

print(f"Failed event stored: {failed_event.pk}")
print(f"Status: {failed_event.status}")
print(f"Next retry: {failed_event.next_retry_at}")
```

**Parameters:**
- `connector_type` (str): Connector type ('web', 'email', etc.)
- `event_type` (str): Event type ('page_view', 'form_submit', etc.)
- `raw_payload` (dict): Original event data
- `error_message` (str): Error description
- `error_trace` (str): Full traceback
- `source_identifier` (str): Source identifier (domain, etc.)

**Returns:** `FailedEvent` instance

#### retry_failed_event()

Manually retry a failed event.

```python
from connectors.fallback import retry_failed_event
from connectors.models import FailedEvent

event = FailedEvent.objects.get(pk=event_id)
success = retry_failed_event(event)

if success:
    print(f"Event processed successfully!")
    print(f"Interactions created: {event.interaction_ids}")
else:
    print(f"Retry failed, scheduled for: {event.next_retry_at}")
```

**Parameters:**
- `event` (FailedEvent): Event to retry

**Returns:** `bool` - True if successful, False otherwise

#### get_events_ready_for_retry()

Query events ready for retry.

```python
from connectors.fallback import get_events_ready_for_retry

events = get_events_ready_for_retry()
print(f"Found {len(events)} events ready for retry")

for event in events:
    print(f"Event: {event.id}")
    print(f"  Type: {event.connector_type}.{event.event_type}")
    print(f"  Retries: {event.retry_count}/{event.get_max_retries()}")
```

**Returns:** `QuerySet[FailedEvent]`

### Common Exceptions

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from django.core.exceptions import ValidationError

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

try:
    touchpoint = resolver.resolve(
        hint,
        connector_type='web',
        source_identifier='example.com'
    )
except ValidationError as e:
    # Handle validation errors
    print(f"Validation error: {e}")
except Exception as e:
    # Handle other errors
    print(f"Resolution error: {e}")
```

### Error Tracking

```python
from connectors.metrics import track_resolution

with track_resolution('web', {'url': 'example.com'}) as tracker:
    try:
        touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
        tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)
    except Exception as e:
        # Automatically recorded as error
        tracker.record_error(str(e))
        raise
```

## Best Practices

### 1. Build Hints from Raw Data

```python
# ✅ Good: Build hint from raw event data
def build_hint_from_event(event_data: dict, website) -> TouchpointHint:
    return TouchpointHint(
        code=f"web.{event_data['event_type']}",
        channel_code=website.channel.code if website.channel else 'web',
        medium_code=event_data.get('utm_medium', 'organic'),
        touchpoint_type_code='web_page',
        label=f"Web {event_data['event_type'].title()}",
        metadata={'url': event_data['full_url']}
    )

# ❌ Avoid: Hardcoding values
hint = TouchpointHint(code='web.page_view', channel_code='web')  # Too generic
```

### 2. Resolve Before Creating Interactions

```python
# ✅ Good: Pre-creation resolution
hint = build_hint_from_event(event_data, website)
touchpoint = resolver.resolve(hint, connector_type='web', source_identifier=website.base_url)
interaction = Interaction.objects.create(touchpoint=touchpoint, ...)

# ❌ Avoid: Post-creation resolution (v1.0 pattern, no longer supported)
interaction = Interaction.objects.create(...)
touchpoint = resolver.resolve(interaction)  # Won't work in v2.0
```

### 3. Use Caching for High Volume

```python
# ✅ Good: Use cached resolver for high-volume scenarios
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

cached_provider = CachedMappingProvider()
cached_provider.warm_cache()
resolver = CachedTouchpointResolver(cached_provider)

# Process many events efficiently
for event in events:
    hint = build_hint(event)
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
    # ... create interaction
```

### 4. Use Event Processing Methods

```python
# ✅ Good: Use built-in event processing
from websites.models import WebInteraction

interactions = WebInteraction.process_page_view_event(event_data)

# ❌ Avoid: Manual creation without proper flow
web_interaction = WebInteraction.objects.create(...)  # Missing touchpoint resolution!
```

### 5. Monitor Performance

```python
# ✅ Good: Track resolution performance
from connectors.metrics import track_resolution

with track_resolution('web', metadata) as tracker:
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
    tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)

# Review metrics regularly
```

## API Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| **2.0** | 2025-01 | Subject-agnostic architecture, pre-creation resolution, explicit parameters |
| **1.0** | 2024-12 | Original subject-dependent architecture with TouchpointInferenceProtocol |

## See Also

- **[ARCHITECTURE_v2.md](ARCHITECTURE_v2.md)** - Architecture overview
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - v1.0 → v2.0 migration
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - Practical examples
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick patterns
- **[README.md](README.md)** - Main documentation
