# Touchpoint Resolution System - Quick Reference

## ⚡ Architecture Update (2025)

**The system now uses a simplified subject-agnostic approach:**
- ✅ No more `TouchpointInferenceProtocol` required
- ✅ Build `TouchpointHint` directly from raw event data
- ✅ Resolvers accept explicit parameters (`hint`, `connector_type`, `source_identifier`)
- ✅ Touchpoints resolved **before** creating Interaction/WebInteraction objects

## Quick Start

### 1. Basic Resolution (New Approach)
```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

# Create hint from event data
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View'
)

# Resolve touchpoint with explicit parameters
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)
```

### 2. Create Mapping Rule
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
    touchpoint_type_code='web_page',
    priority=100,
    is_active=True
)
```

### 3. Monitor Performance
```python
from connectors.metrics import track_resolution

with track_resolution('web', {'url': 'example.com'}) as tracker:
    touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
    tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)
```

## Management Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `backfill_touchpoints` | Backfill missing touchpoints | `python manage.py backfill_touchpoints --batch-size=100` |
| `test_touchpoint_resolution` | Test resolution logic | `python manage.py test_touchpoint_resolution --connector-type=web` |
| `manage_mapping_rules` | CRUD operations on rules | `python manage.py manage_mapping_rules list` |
| `manage_touchpoint_cache` | Cache management | `python manage.py manage_touchpoint_cache clear` |
| `monitor_touchpoint_system` | System monitoring | `python manage.py monitor_touchpoint_system --period=hour` |
| `cleanup_touchpoint_events` | Data cleanup | `python manage.py cleanup_touchpoint_events --retention-days=30` |

## Common Patterns

### Web Connector (Event Processing)
```python
from websites.models import WebInteraction

# Page view event (from browser)
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products/laptop',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'user_agent': 'Mozilla/5.0...'
}

# Process event (creates Interaction + WebInteraction with touchpoint)
interactions = WebInteraction.process_page_view_event(event_data)

# Form submission event
form_event_data = {
    'event_type': 'form_submit',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/contact/',
    'payload': {'form_type': 'contact'},
    'user_agent': 'Mozilla/5.0...'
}
interactions = WebInteraction.process_form_submit_event(form_event_data)
```

### Direct Touchpoint Resolution
```python
from connectors.protocols import TouchpointHint
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

# Build hint from raw data
hint = TouchpointHint(
    code='email.open',
    channel_code='email',
    medium_code='email',
    touchpoint_type_code='email_open',
    label='Email Open',
    metadata={'campaign_id': 'newsletter_001'}
)

# Resolve
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(hint, connector_type='email', source_identifier='campaign_001')
```

### Custom Connector Pattern
```python
def build_hint_from_custom_event(event_data: dict) -> TouchpointHint:
    """Build hint from custom event structure."""
    return TouchpointHint(
        code=f"mobile.{event_data['action']}",
        channel_code='mobile_app',
        medium_code='app',
        touchpoint_type_code='mobile_action',
        label=f"Mobile {event_data['action'].title()}",
        metadata=event_data.get('metadata', {})
    )

# Usage
hint = build_hint_from_custom_event({'action': 'purchase', 'amount': 99.99})
touchpoint = resolver.resolve(hint, connector_type='mobile', source_identifier='ios_app')
```

## Mapping Rule Priorities

| Priority | Use Case | Example |
|----------|----------|---------|
| 200+ | High priority rules | Campaign-specific mappings |
| 100-199 | Standard rules | General page mappings |
| 50-99 | Low priority rules | Fallback mappings |
| 1-49 | Default rules | Generic mappings |

## Channel Codes

| Channel | Code | Description |
|---------|------|-------------|
| Web | `web` | Website interactions |
| Email | `email` | Email interactions |
| WhatsApp | `whatsapp` | WhatsApp interactions |
| Mobile | `mobile` | Mobile app interactions |
| API | `api` | API interactions |

## Medium Codes

| Medium | Code | Description |
|--------|------|-------------|
| Organic | `organic` | Organic traffic |
| Paid | `paid` | Paid advertising |
| Direct | `direct` | Direct traffic |
| Referral | `referral` | Referral traffic |
| Social | `social` | Social media |
| Email | `email` | Email campaigns |
| Newsletter | `newsletter` | Newsletter campaigns |

## Event Codes

### Web Events
- `web.page_view` - Page view
- `web.form_submit` - Form submission
- `web.button_click` - Button click
- `web.download` - File download

### Email Events
- `email.open` - Email opened
- `email.click` - Link clicked
- `email.bounce` - Email bounced
- `email.unsubscribe` - Unsubscribed

### WhatsApp Events
- `whatsapp.message_received` - Message received
- `whatsapp.message_sent` - Message sent
- `whatsapp.media_received` - Media received
- `whatsapp.media_sent` - Media sent

## Error Handling

### Common Exceptions
```python
from connectors.exceptions import TouchpointResolutionError

try:
    touchpoint = resolver.resolve(subject)
except TouchpointResolutionError as e:
    print(f"Resolution failed: {e.message}")
```

### Fallback Strategy
```python
def safe_resolve(subject):
    try:
        return resolver.resolve(subject)
    except Exception:
        return create_fallback_touchpoint(subject)
```

## Performance Tips

### 1. Use select_related
```python
interactions = Interaction.objects.select_related('person', 'action')
```

### 2. Batch Processing
```python
for batch in chunks(interactions, 100):
    process_batch(batch)
```

### 3. Caching
```python
from django.core.cache import cache

cache_key = f"touchpoint:{interaction.id}"
touchpoint = cache.get(cache_key)
if not touchpoint:
    touchpoint = resolver.resolve(interaction)
    cache.set(cache_key, touchpoint, 3600)
```

## Monitoring

### Check System Health
```python
from connectors.monitoring_models import TouchpointSystemHealth

health = TouchpointSystemHealth.objects.latest('recorded_at')
print(f"System status: {health.health_status}")
```

### Get Recent Events
```python
from connectors.monitoring_models import TouchpointResolutionEvent

recent_events = TouchpointResolutionEvent.objects.filter(
    occurred_at__gte=timezone.now() - timedelta(hours=1)
)
```

### Calculate Success Rate
```python
total = recent_events.count()
successful = recent_events.filter(error_occurred=False).count()
success_rate = successful / total if total > 0 else 0
```

## Admin Interface

### Access Points
- **Mapping Rules**: `/admin/connectors/touchpointmappingrule/`
- **Resolution Events**: `/admin/connectors/touchpointresolutionevent/`
- **Alerts**: `/admin/connectors/touchpointalert/`
- **Metrics**: `/admin/connectors/touchpointresolutionmetrics/`
- **System Health**: `/admin/connectors/touchpointsystemhealth/`

### Custom Views
- **Dashboard**: `/admin/connectors/touchpointmappingrule/dashboard/`
- **Analytics**: `/admin/connectors/touchpointmappingrule/analytics/`
- **Performance**: `/admin/connectors/touchpointmappingrule/performance/`

## Testing

### Unit Tests
```python
def test_touchpoint_resolution():
    interaction = create_test_interaction()
    touchpoint = resolver.resolve(interaction)
    assert touchpoint.code == 'expected_code'
```

### Integration Tests
```python
def test_end_to_end_resolution():
    interaction = create_test_interaction()
    touchpoint = resolver.resolve(interaction)
    assert touchpoint.channel.code == 'web'
    assert touchpoint.is_active
```

## Troubleshooting

### Common Issues

1. **Mapping rule not applied**
   - Check rule priority
   - Verify source_identifier matching
   - Ensure rule is active

2. **Slow resolution**
   - Check database performance
   - Review mapping rule complexity
   - Consider caching

3. **High error rate**
   - Review error logs
   - Check data quality
   - Validate mapping rules

### Debug Commands
```bash
# Test resolution
python manage.py test_touchpoint_resolution --connector-type=web --verbose

# Check system health
python manage.py monitor_touchpoint_system --health-check

# View recent errors
python manage.py shell
>>> from connectors.monitoring_models import TouchpointResolutionEvent
>>> TouchpointResolutionEvent.objects.filter(error_occurred=True).order_by('-occurred_at')[:10]
```

## Configuration

### Settings
```python
# settings.py
TOUCHPOINT_RESOLUTION = {
    'DEFAULT_CACHE_TTL': 3600,
    'MAX_RESOLUTION_TIME_MS': 1000,
    'ENABLE_MONITORING': True,
}
```

### Environment Variables
```bash
TOUCHPOINT_CACHE_TTL=3600
TOUCHPOINT_MONITORING_ENABLED=true
TOUCHPOINT_ALERT_EMAIL=admin@example.com
```

## Best Practices

1. **Use specific mapping rules** - Avoid overly generic rules
2. **Set appropriate priorities** - Higher priority for specific cases
3. **Monitor performance** - Track resolution times and error rates
4. **Handle errors gracefully** - Always have fallback strategies
5. **Test thoroughly** - Test with various scenarios and edge cases
6. **Document mappings** - Use descriptive labels and metadata
7. **Regular cleanup** - Clean up old events and metrics
8. **Cache when possible** - Use caching for frequently accessed data

## Support

- **Full Documentation**: `API_DOCUMENTATION.md`
- **Usage Examples**: `USAGE_EXAMPLES.md`
- **Implementation Guide**: `IMPLEMENTATION_PLAN.md`
- **Admin Interface Guide**: `ADMIN_INTERFACE_GUIDE.md`
- **Integration Tests Guide**: `tests/INTEGRATION_TESTS_GUIDE.md`
