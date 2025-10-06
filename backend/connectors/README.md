# Touchpoint Resolution System

A comprehensive Django framework for automatic, configurable touchpoint creation across multiple communication channels including web, email, and WhatsApp.

## 🚀 Features

- **Automatic Touchpoint Resolution**: Intelligent touchpoint creation based on interaction data
- **Configurable Mapping Rules**: Admin-configurable rules for custom touchpoint creation
- **Multi-Channel Support**: Web, email, WhatsApp, and custom connector support
- **Event Fallback & Recovery**: ⭐ **NEW** - Automatic retry system for failed events with exponential backoff
- **Performance Monitoring**: Comprehensive metrics collection and alerting
- **Admin Interface**: Enhanced Django admin with dashboards and analytics
- **Management Commands**: Powerful CLI tools for operations and maintenance
- **Integration Tests**: Complete end-to-end testing suite
- **Extensible Architecture**: Protocol-based design for easy extension
- **Sentry Integration**: ⭐ **NEW** - Complete error tracking and performance monitoring

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Usage Examples](#usage-examples)
- [Management Commands](#management-commands)
- [Admin Interface](#admin-interface)
- [Performance Monitoring](#performance-monitoring)
- [Testing](#testing)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🏃‍♂️ Quick Start

### 1. Basic Usage

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

# Initialize resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Create a touchpoint hint with event data
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View'
)

# Resolve touchpoint (subject-agnostic approach)
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

## 🏗️ Architecture

### Core Components

- **TouchpointHint**: Dataclass containing hint information for touchpoint resolution
- **TouchpointResolverProtocol**: Interface for resolving touchpoints from hints
- **MappingProviderProtocol**: Interface for mapping rule lookup
- **DefaultTouchpointResolver**: Subject-agnostic resolution logic
- **DatabaseMappingProvider**: Database-backed mapping rule lookup
- **CachedTouchpointResolver**: Caching resolver for performance optimization

### Resolution Flow (Simplified Subject-Agnostic Approach)

```
Event Data → TouchpointHint → Mapping Rule Lookup → Touchpoint Creation
     ↓             ↓                    ↓                     ↓
  (Raw)      (Structured)         (Transforms)          (Creates)
```

**Key Architectural Change**: The system no longer requires connector objects to implement `TouchpointInferenceProtocol`. Instead, hints are built directly from raw event data, and resolvers accept explicit parameters (`hint`, `connector_type`, `source_identifier`), making the system more flexible and easier to test.

### Supported Connectors

- **Web Connector**: Website interactions (page views, form submissions, etc.)
- **Email Connector**: Email interactions (opens, clicks, bounces, etc.)
- **WhatsApp Connector**: WhatsApp interactions (messages, media, etc.)
- **Custom Connectors**: Extensible protocol for new connector types

## 📚 Documentation

### Comprehensive Guides

- **[Architecture v2.0](ARCHITECTURE_v2.md)**: ⭐ **NEW** - Subject-agnostic architecture overview
- **[Migration Guide](MIGRATION_GUIDE.md)**: ⭐ **NEW** - Migrating from v1.0 to v2.0
- **[Fallback System](FALLBACK_SYSTEM.md)**: ⭐ **NEW** - Event recovery and retry system documentation
- **[Usage Examples](USAGE_EXAMPLES.md)**: ✅ **UPDATED** - Practical, real-world usage scenarios
- **[Quick Reference](QUICK_REFERENCE.md)**: ✅ **UPDATED** - Quick reference guide
- **[API Documentation](API_DOCUMENTATION.md)**: ✅ **UPDATED** - Complete API reference with examples
- **[Admin Interface Guide](ADMIN_INTERFACE_GUIDE.md)**: ✅ **UPDATED** - Admin interface documentation
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)**: Historical implementation roadmap (v1.0)
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)**: Historical implementation status (v1.0)

### Test Documentation

- **[Integration Tests Guide](tests/INTEGRATION_TESTS_GUIDE.md)**: Complete testing documentation

## 💡 Usage Examples

### Web Connector (Event Processing Approach)

```python
from websites.models import WebInteraction
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

# Event data from browser
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products/laptop',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'referrer': 'https://google.com/search',
    'user_agent': 'Mozilla/5.0...'
}

# Process event (creates Interaction and WebInteraction with touchpoint resolved)
interactions = WebInteraction.process_page_view_event(event_data)
print(f"Created {len(interactions)} interactions")
```

### Direct Touchpoint Resolution

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Build hint directly from event data
hint = TouchpointHint(
    code='web.form_submit',
    channel_code='web',
    medium_code='paid',
    touchpoint_type_code='web_form',
    label='Contact Form Submit',
    metadata={'form_type': 'contact', 'utm_campaign': 'summer2024'}
)

# Resolve touchpoint
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)
print(f"Touchpoint: {touchpoint.name}")
```

### Custom Event Processing

```python
from connectors.protocols import TouchpointHint
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

def process_mobile_event(event_data: dict):
    """Process custom mobile app events."""
    
    # Build hint from raw event data
    hint = TouchpointHint(
        code=f"mobile.{event_data['screen_name']}",
        channel_code='mobile_app',
        medium_code='app',
        touchpoint_type_code='mobile_screen',
        label=f"Mobile {event_data['screen_name'].title()}",
        metadata={
            'device_id': event_data.get('device_id'),
            'app_version': event_data.get('app_version'),
        }
    )
    
    # Resolve touchpoint
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    touchpoint = resolver.resolve(
        hint,
        connector_type='mobile',
        source_identifier=event_data.get('app_id', 'mobile_app')
    )
    
    return touchpoint
```

## 🛠️ Management Commands

### Backfill Operations

```bash
# Backfill missing touchpoints
python manage.py backfill_touchpoints --batch-size=100

# Backfill specific connector type
python manage.py backfill_touchpoints --connector-type=web --limit=1000
```

### Testing

```bash
# Test resolution logic
python manage.py test_touchpoint_resolution --connector-type=web --event-code=web.page_view

# Test with custom data
python manage.py test_touchpoint_resolution --connector-type=email --metadata='{"campaign": "newsletter"}'
```

### Rule Management

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
python manage.py manage_mapping_rules update --id=123 --priority=150

# Delete rule
python manage.py manage_mapping_rules delete --id=123
```

### Cache Management

```bash
# Clear cache
python manage.py manage_touchpoint_cache clear

# Warm cache
python manage.py manage_touchpoint_cache warm

# Get cache statistics
python manage.py manage_touchpoint_cache stats
```

### System Monitoring

```bash
# Get system health report
python manage.py monitor_touchpoint_system

# Get metrics for specific period
python manage.py monitor_touchpoint_system --period=hour

# Check system health
python manage.py monitor_touchpoint_system --health-check
```

### Data Cleanup

```bash
# Clean up old events
python manage.py cleanup_touchpoint_events

# Clean up with custom retention
python manage.py cleanup_touchpoint_events --retention-days=30 --dry-run
```

## 🎛️ Admin Interface

### Access Points

- **Mapping Rules**: `/admin/connectors/touchpointmappingrule/`
- **Failed Events**: ⭐ **NEW** - `/admin/connectors/failedevent/`
- **Resolution Events**: `/admin/connectors/touchpointresolutionevent/`
- **Alerts**: `/admin/connectors/touchpointalert/`
- **Metrics**: `/admin/connectors/touchpointresolutionmetrics/`
- **System Health**: `/admin/connectors/touchpointsystemhealth/`

### Custom Views

- **Dashboard**: `/admin/connectors/touchpointmappingrule/dashboard/`
- **Analytics**: `/admin/connectors/touchpointmappingrule/analytics/`
- **Performance**: `/admin/connectors/touchpointmappingrule/performance/`

### Features

- **Enhanced List Views**: Optimized with filters, search, and bulk actions
- **Custom Forms**: Rich form interfaces with validation
- **Real-time Metrics**: Live performance monitoring
- **Alert Management**: Comprehensive alert handling
- **Data Visualization**: Charts and graphs for analytics

## 📊 Performance Monitoring

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
```

### Alerting

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
```

### Health Checks

```python
from connectors.monitoring_models import TouchpointSystemHealth

def check_system_health():
    latest_health = TouchpointSystemHealth.objects.latest('recorded_at')
    return latest_health.health_status == 'healthy'
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test connectors

# Run specific test categories
python manage.py test connectors.tests.test_admin_integration
python manage.py test connectors.tests.test_management_commands_integration
python manage.py test connectors.tests.test_monitoring_integration
python manage.py test connectors.tests.test_touchpoint_resolution_integration

# Run with custom test runner
python manage.py test --testrunner=connectors.tests.test_integration_runner.IntegrationTestRunner
```

### Test Coverage

- **Admin Interface Tests**: Complete admin functionality testing
- **Management Commands Tests**: All CLI commands tested
- **Monitoring Tests**: Performance monitoring and alerting
- **Resolution Tests**: End-to-end touchpoint resolution workflows

## ⚙️ Configuration

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

## 🔧 Troubleshooting

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

### Performance Optimization

```python
# Use select_related for database efficiency
interactions = Interaction.objects.select_related('touchpoint', 'action', 'agent')

# Batch processing with pre-creation touchpoint resolution
def process_events_in_batches(events, batch_size=100):
    """Process events efficiently with touchpoint resolution before creation."""
    from connectors.resolvers import DefaultTouchpointResolver
    from connectors.mapping_providers import DatabaseMappingProvider
    
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        for event in batch:
            # Build hint from event
            hint = build_hint_from_event(event)
            # Resolve touchpoint BEFORE creating interaction
            touchpoint = resolver.resolve(
                hint,
                connector_type=event['connector_type'],
                source_identifier=event.get('source_id', '')
            )
            # Create interaction with touchpoint already assigned
            create_interaction_with_touchpoint(event, touchpoint)

# Caching touchpoints by hint signature
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

# Use cached resolver for high-volume scenarios
cached_resolver = CachedTouchpointResolver(CachedMappingProvider())
touchpoint = cached_resolver.resolve(hint, connector_type='web', source_identifier='example.com')
```

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install dependencies
3. Run migrations
4. Run tests
5. Start development

### Code Style

- Follow PEP 8
- Use type hints
- Write comprehensive tests
- Document all public APIs

### Testing

- Write unit tests for new features
- Add integration tests for workflows
- Ensure test coverage > 90%
- Run tests before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For additional support and documentation:

- **Full API Documentation**: `API_DOCUMENTATION.md`
- **Fallback System Guide**: `FALLBACK_SYSTEM.md` ⭐ **NEW**
- **Usage Examples**: `USAGE_EXAMPLES.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Implementation Guide**: `IMPLEMENTATION_PLAN.md`
- **Admin Interface Guide**: `ADMIN_INTERFACE_GUIDE.md`
- **Integration Tests Guide**: `tests/INTEGRATION_TESTS_GUIDE.md`

## 🎯 Roadmap

### Completed Features

- ✅ Core touchpoint resolution framework (subject-agnostic)
- ✅ Web connector implementation with pre-creation resolution
- ✅ Performance monitoring and metrics
- ✅ Enhanced admin interface
- ✅ Management commands
- ✅ Integration tests (35/35 core tests passing)
- ✅ Comprehensive documentation
- ✅ **NEW**: Subject-agnostic architecture (no more `TouchpointInferenceProtocol`)
- ✅ **NEW**: Pre-creation touchpoint resolution
- ✅ **NEW**: Direct hint building from raw event data
- ✅ **NEW**: Event fallback and recovery system
- ✅ **NEW**: Exponential backoff retry strategy
- ✅ **NEW**: Comprehensive Sentry integration

### Future Enhancements

- 🔄 Email connector (independent package)
- 🔄 WhatsApp connector (independent package)
- 🔄 Advanced analytics and reporting
- 🔄 Machine learning-based touchpoint optimization
- 🔄 Real-time dashboard
- 🔄 API rate limiting and throttling
- 🔄 Update remaining integration tests for new architecture

## 📊 System Status

- **Core Framework**: ✅ Complete
- **Web Connector**: ✅ Complete
- **Performance Monitoring**: ✅ Complete
- **Admin Interface**: ✅ Complete
- **Management Commands**: ✅ Complete
- **Integration Tests**: ✅ Complete
- **Documentation**: ✅ Complete
- **Email Connector**: 🔄 Planned (Independent Package)
- **WhatsApp Connector**: 🔄 Planned (Independent Package)

---

**Touchpoint Resolution System** - Making touchpoint management intelligent, automated, and scalable.