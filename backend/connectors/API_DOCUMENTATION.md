# Touchpoint Resolution System - API Documentation

## Overview

The Touchpoint Resolution System provides a comprehensive API for automatic touchpoint creation and management across multiple communication channels. This system enables automatic, configurable touchpoint creation for various connector types including web, email, and WhatsApp.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [API Endpoints](#api-endpoints)
3. [Management Commands](#management-commands)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Performance Monitoring](#performance-monitoring)
7. [Best Practices](#best-practices)

## Core Concepts

### Touchpoint Resolution Flow

```
Interaction → Touchpoint Hint → Mapping Rule Lookup → Touchpoint Creation
```

### Key Components

- **TouchpointInferenceProtocol**: Interface for inferring touchpoint hints
- **TouchpointResolverProtocol**: Interface for resolving touchpoints
- **MappingProviderProtocol**: Interface for mapping rule lookup
- **TouchpointMappingRule**: Admin-configurable rules for touchpoint creation
- **DefaultTouchpointResolver**: Generic resolution logic
- **DatabaseMappingProvider**: Database-backed mapping rule lookup

## API Endpoints

### 1. Touchpoint Resolution

#### Resolve Touchpoint
```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

# Initialize resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Resolve touchpoint
touchpoint = resolver.resolve(subject)
```

**Parameters:**
- `subject`: Object implementing `TouchpointInferenceProtocol`

**Returns:**
- `Touchpoint`: Created or existing touchpoint object

**Example:**
```python
# Web interaction example
from websites.models import WebInteraction

web_interaction = WebInteraction.objects.get(id=123)
touchpoint = resolver.resolve(web_interaction)
```

### 2. Mapping Rule Management

#### Create Mapping Rule
```python
from connectors.models import TouchpointMappingRule

rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='example.com',
    event_code='web.page_view',
    touchpoint_code='web.home_page_view',
    touchpoint_label='Home Page View',
    channel_code='web',
    medium_code='organic',
    priority=100,
    is_active=True,
    metadata={'campaign': 'summer_sale'}
)
```

#### Update Mapping Rule
```python
rule = TouchpointMappingRule.objects.get(id=rule_id)
rule.priority = 150
rule.metadata['campaign'] = 'winter_sale'
rule.save()
```

#### Delete Mapping Rule
```python
rule = TouchpointMappingRule.objects.get(id=rule_id)
rule.delete()
```

#### List Mapping Rules
```python
# Get all active rules
active_rules = TouchpointMappingRule.objects.filter(is_active=True)

# Get rules for specific connector
web_rules = TouchpointMappingRule.objects.filter(connector_type='web')

# Get rules with specific priority
high_priority_rules = TouchpointMappingRule.objects.filter(priority__gte=100)
```

### 3. Performance Monitoring

#### Track Resolution Performance
```python
from connectors.metrics import track_resolution

with track_resolution(connector_type='web', metadata={'url': 'example.com'}) as tracker:
    # Your resolution logic here
    touchpoint = resolver.resolve(subject)
    tracker.record_success(
        cache_hit=False,
        mapping_applied=True,
        touchpoint_created=True
    )
```

#### Get System Metrics
```python
from connectors.monitoring_models import TouchpointResolutionMetrics

# Get latest metrics
latest_metrics = TouchpointResolutionMetrics.objects.latest('period_start')

# Get metrics for specific period
from datetime import date, timedelta
yesterday = date.today() - timedelta(days=1)
daily_metrics = TouchpointResolutionMetrics.objects.filter(
    period_type='daily',
    period_start=yesterday
)
```

#### Alert Management
```python
from connectors.alerting import alert_manager

# Trigger alert
alert_manager.trigger_alert(
    alert_type='high_error_rate',
    severity='critical',
    title='High Error Rate Detected',
    message='Error rate for web connector exceeded 10%',
    connector_type='web',
    threshold_value=0.1,
    actual_value=0.15
)

# Acknowledge alert
alert = TouchpointAlert.objects.get(id=alert_id)
alert.acknowledge()

# Resolve alert
alert.resolve()
```

## Management Commands

### 1. Backfill Touchpoints

```bash
# Backfill all interactions
python manage.py backfill_touchpoints

# Backfill with specific options
python manage.py backfill_touchpoints \
    --batch-size=50 \
    --connector-type=web \
    --limit=1000 \
    --verbose

# Dry run to see what would be processed
python manage.py backfill_touchpoints --dry-run
```

### 2. Test Touchpoint Resolution

```bash
# Test web connector
python manage.py test_touchpoint_resolution \
    --connector-type=web \
    --event-code=web.page_view

# Test with custom data
python manage.py test_touchpoint_resolution \
    --connector-type=email \
    --event-code=email.open \
    --metadata='{"campaign": "newsletter"}'
```

### 3. Manage Mapping Rules

```bash
# List all rules
python manage.py manage_mapping_rules list

# Create new rule
python manage.py manage_mapping_rules create \
    --connector-type=web \
    --event-code=web.form_submit \
    --touchpoint-code=web.contact_form \
    --priority=100

# Update existing rule
python manage.py manage_mapping_rules update \
    --id=123 \
    --priority=150

# Delete rule
python manage.py manage_mapping_rules delete --id=123
```

### 4. Cache Management

```bash
# Clear cache
python manage.py manage_touchpoint_cache clear

# Warm cache
python manage.py manage_touchpoint_cache warm

# Get cache statistics
python manage.py manage_touchpoint_cache stats

# Test cache performance
python manage.py manage_touchpoint_cache test
```

### 5. System Monitoring

```bash
# Get system health report
python manage.py monitor_touchpoint_system

# Get metrics for specific period
python manage.py monitor_touchpoint_system --period=hour

# Check system health
python manage.py monitor_touchpoint_system --health-check
```

### 6. Data Cleanup

```bash
# Clean up old events
python manage.py cleanup_touchpoint_events

# Clean up with custom retention
python manage.py cleanup_touchpoint_events \
    --retention-days=30 \
    --dry-run
```

## Usage Examples

### Example 1: Web Page View Resolution

```python
from websites.models import WebInteraction
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

# Create web interaction
web_interaction = WebInteraction.objects.create(
    url='https://example.com/products/laptop',
    event_type='web.page_view',
    person=person,
    occurred_at=timezone.now()
)

# Resolve touchpoint
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(web_interaction)

print(f"Created touchpoint: {touchpoint.name}")
print(f"Channel: {touchpoint.channel.name}")
print(f"Code: {touchpoint.code}")
```

### Example 2: Custom Mapping Rule

```python
from connectors.models import TouchpointMappingRule

# Create custom mapping for product pages
rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='example.com/products/',
    event_code='web.page_view',
    touchpoint_code='web.product_page_view',
    touchpoint_label='Product Page View',
    channel_code='web',
    medium_code='organic',
    priority=200,  # High priority
    is_active=True,
    metadata={
        'category': 'product',
        'funnel_stage': 'think'
    }
)

# Now all product page views will use this mapping
```

### Example 3: Batch Processing

```python
from django.db import transaction
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

def process_interactions_batch(interactions):
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    with transaction.atomic():
        for interaction in interactions:
            try:
                touchpoint = resolver.resolve(interaction)
                print(f"Processed interaction {interaction.id}")
            except Exception as e:
                print(f"Error processing interaction {interaction.id}: {e}")
                # Continue with next interaction
                continue

# Usage
interactions = WebInteraction.objects.filter(touchpoint__isnull=True)[:100]
process_interactions_batch(interactions)
```

### Example 4: Performance Monitoring

```python
from connectors.metrics import track_resolution
from connectors.alerting import alert_manager
import time

def monitored_resolution(subject):
    start_time = time.time()
    
    with track_resolution(
        connector_type='web',
        metadata={'url': getattr(subject, 'url', 'unknown')}
    ) as tracker:
        try:
            touchpoint = resolver.resolve(subject)
            
            # Check performance
            resolution_time = time.time() - start_time
            if resolution_time > 1.0:  # 1 second threshold
                alert_manager.trigger_alert(
                    alert_type='slow_resolution',
                    severity='warning',
                    title='Slow Resolution Time',
                    message=f'Resolution took {resolution_time:.2f}s',
                    connector_type='web',
                    threshold_value=1.0,
                    actual_value=resolution_time
                )
            
            tracker.record_success(
                cache_hit=False,
                mapping_applied=True,
                touchpoint_created=True
            )
            
            return touchpoint
            
        except Exception as e:
            tracker.record_error(str(e), type(e).__name__)
            raise
```

### Example 5: Custom Connector Integration

```python
from connectors.protocols import TouchpointInferenceProtocol
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

class CustomInteraction(TouchpointInferenceProtocol):
    def __init__(self, source, event_type, metadata=None):
        self.source = source
        self.event_type = event_type
        self.metadata = metadata or {}
        self.occurred_at = timezone.now()
    
    def infer_touchpoint_hint(self):
        return {
            'connector_type': 'custom',
            'source_identifier': self.source,
            'event_code': self.event_type,
            'metadata': self.metadata
        }
    
    def get_person(self):
        # Return person if available
        return None
    
    def get_occurred_at(self):
        return self.occurred_at

# Usage
custom_interaction = CustomInteraction(
    source='mobile_app',
    event_type='app.screen_view',
    metadata={'screen': 'product_detail'}
)

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(custom_interaction)
```

## Error Handling

### Common Exceptions

#### TouchpointResolutionError
```python
from connectors.exceptions import TouchpointResolutionError

try:
    touchpoint = resolver.resolve(subject)
except TouchpointResolutionError as e:
    print(f"Resolution failed: {e.message}")
    print(f"Error type: {e.error_type}")
```

#### MappingRuleNotFound
```python
from connectors.exceptions import MappingRuleNotFound

try:
    rule = mapping_provider.lookup_mapping(subject, hint)
except MappingRuleNotFound:
    # Use default resolution
    touchpoint = create_default_touchpoint(hint)
```

### Error Recovery Strategies

```python
def robust_resolution(subject, max_retries=3):
    for attempt in range(max_retries):
        try:
            return resolver.resolve(subject)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, create fallback
                return create_fallback_touchpoint(subject)
            
            # Wait before retry
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
```

## Performance Monitoring

### Metrics Collection

```python
from connectors.monitoring_models import TouchpointResolutionEvent

# Get recent events
recent_events = TouchpointResolutionEvent.objects.filter(
    occurred_at__gte=timezone.now() - timedelta(hours=1)
)

# Calculate success rate
total_events = recent_events.count()
successful_events = recent_events.filter(error_occurred=False).count()
success_rate = successful_events / total_events if total_events > 0 else 0

# Get average resolution time
avg_time = recent_events.aggregate(
    avg_time=models.Avg('resolution_time_ms')
)['avg_time']
```

### Health Checks

```python
from connectors.monitoring_models import TouchpointSystemHealth

def check_system_health():
    latest_health = TouchpointSystemHealth.objects.latest('recorded_at')
    
    if latest_health.health_status == 'healthy':
        return True
    elif latest_health.health_status == 'degraded':
        # Log warning
        logger.warning("System health is degraded")
        return True
    else:
        # System is unhealthy
        logger.error("System health is critical")
        return False
```

## Best Practices

### 1. Mapping Rule Design

```python
# Good: Specific and descriptive
rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='shop.example.com/products/',
    event_code='web.page_view',
    touchpoint_code='web.product_page_view',
    touchpoint_label='Product Page View',
    channel_code='web',
    medium_code='organic',
    priority=100,
    metadata={
        'category': 'product',
        'funnel_stage': 'think',
        'campaign': 'product_catalog'
    }
)

# Avoid: Too generic
rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='example.com',
    event_code='web.page_view',
    touchpoint_code='web.page_view',
    # ... too generic, will match everything
)
```

### 2. Performance Optimization

```python
# Use select_related for database efficiency
interactions = Interaction.objects.select_related(
    'touchpoint', 'action', 'person'
).filter(touchpoint__isnull=True)

# Batch processing
def process_in_batches(queryset, batch_size=100):
    for i in range(0, queryset.count(), batch_size):
        batch = queryset[i:i + batch_size]
        process_batch(batch)
```

### 3. Error Handling

```python
# Always use try-catch for resolution
try:
    touchpoint = resolver.resolve(subject)
except Exception as e:
    logger.error(f"Resolution failed for {subject}: {e}")
    # Create fallback or skip
    continue
```

### 4. Monitoring Integration

```python
# Always track resolution performance
with track_resolution(connector_type, metadata) as tracker:
    try:
        touchpoint = resolver.resolve(subject)
        tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)
    except Exception as e:
        tracker.record_error(str(e), type(e).__name__)
        raise
```

### 5. Testing

```python
# Test with various scenarios
def test_resolution_scenarios():
    # Test with mapping rule
    subject_with_mapping = create_test_subject_with_mapping()
    touchpoint1 = resolver.resolve(subject_with_mapping)
    assert touchpoint1.code == 'expected_code'
    
    # Test without mapping rule
    subject_without_mapping = create_test_subject_without_mapping()
    touchpoint2 = resolver.resolve(subject_without_mapping)
    assert touchpoint2.code == 'default_code'
    
    # Test error handling
    invalid_subject = create_invalid_subject()
    with pytest.raises(TouchpointResolutionError):
        resolver.resolve(invalid_subject)
```

## Configuration

### Settings

```python
# settings.py

# Touchpoint Resolution Settings
TOUCHPOINT_RESOLUTION = {
    'DEFAULT_CACHE_TTL': 3600,  # 1 hour
    'MAX_RESOLUTION_TIME_MS': 1000,  # 1 second
    'ENABLE_MONITORING': True,
    'RETENTION_DAYS': {
        'detailed_events': 90,
        'aggregated_metrics': 365,
    }
}

# Monitoring Settings
TOUCHPOINT_MONITORING = {
    'ENABLE_ALERTS': True,
    'ALERT_THRESHOLDS': {
        'error_rate': 0.05,  # 5%
        'resolution_time_ms': 1000,  # 1 second
    }
}
```

### Environment Variables

```bash
# .env
TOUCHPOINT_CACHE_TTL=3600
TOUCHPOINT_MONITORING_ENABLED=true
TOUCHPOINT_ALERT_EMAIL=admin@example.com
```

## Troubleshooting

### Common Issues

1. **Resolution Timeout**
   - Check system performance
   - Review mapping rule complexity
   - Consider caching strategies

2. **Mapping Rule Not Applied**
   - Verify rule priority
   - Check source_identifier matching
   - Ensure rule is active

3. **High Error Rate**
   - Review error logs
   - Check data quality
   - Validate mapping rules

4. **Cache Issues**
   - Clear cache: `python manage.py manage_touchpoint_cache clear`
   - Check cache configuration
   - Monitor cache hit rates

### Debug Commands

```bash
# Test resolution
python manage.py test_touchpoint_resolution --connector-type=web --verbose

# Check system health
python manage.py monitor_touchpoint_system --health-check

# View recent events
python manage.py shell
>>> from connectors.monitoring_models import TouchpointResolutionEvent
>>> TouchpointResolutionEvent.objects.filter(error_occurred=True).order_by('-occurred_at')[:10]
```

## Support

For additional support and documentation:

- **Implementation Guide**: `IMPLEMENTATION_PLAN.md`
- **Architecture Overview**: `IMPLEMENTATION_SUMMARY.md`
- **Admin Interface Guide**: `ADMIN_INTERFACE_GUIDE.md`
- **Integration Tests Guide**: `tests/INTEGRATION_TESTS_GUIDE.md`

## Version History

- **v1.0.0**: Initial implementation with web connector
- **v1.1.0**: Added performance monitoring and metrics
- **v1.2.0**: Enhanced admin interface and management commands
- **v1.3.0**: Added integration tests and comprehensive documentation
