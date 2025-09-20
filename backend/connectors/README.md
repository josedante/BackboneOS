# Touchpoint Resolution System

A comprehensive Django framework for automatic, configurable touchpoint creation across multiple communication channels including web, email, and WhatsApp.

## 🚀 Features

- **Automatic Touchpoint Resolution**: Intelligent touchpoint creation based on interaction data
- **Configurable Mapping Rules**: Admin-configurable rules for custom touchpoint creation
- **Multi-Channel Support**: Web, email, WhatsApp, and custom connector support
- **Performance Monitoring**: Comprehensive metrics collection and alerting
- **Admin Interface**: Enhanced Django admin with dashboards and analytics
- **Management Commands**: Powerful CLI tools for operations and maintenance
- **Integration Tests**: Complete end-to-end testing suite
- **Extensible Architecture**: Protocol-based design for easy extension

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

# Initialize resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Resolve touchpoint
touchpoint = resolver.resolve(interaction)
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
    touchpoint = resolver.resolve(interaction)
    tracker.record_success(cache_hit=False, mapping_applied=True, touchpoint_created=True)
```

## 🏗️ Architecture

### Core Components

- **TouchpointInferenceProtocol**: Interface for inferring touchpoint hints
- **TouchpointResolverProtocol**: Interface for resolving touchpoints
- **MappingProviderProtocol**: Interface for mapping rule lookup
- **DefaultTouchpointResolver**: Generic resolution logic
- **DatabaseMappingProvider**: Database-backed mapping rule lookup

### Resolution Flow

```
Interaction → Touchpoint Hint → Mapping Rule Lookup → Touchpoint Creation
```

### Supported Connectors

- **Web Connector**: Website interactions (page views, form submissions, etc.)
- **Email Connector**: Email interactions (opens, clicks, bounces, etc.)
- **WhatsApp Connector**: WhatsApp interactions (messages, media, etc.)
- **Custom Connectors**: Extensible protocol for new connector types

## 📚 Documentation

### Comprehensive Guides

- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference with examples
- **[Usage Examples](USAGE_EXAMPLES.md)**: Practical, real-world usage scenarios
- **[Quick Reference](QUICK_REFERENCE.md)**: Quick reference guide for developers
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)**: Detailed implementation roadmap
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)**: Current implementation status
- **[Admin Interface Guide](ADMIN_INTERFACE_GUIDE.md)**: Admin interface documentation

### Test Documentation

- **[Integration Tests Guide](tests/INTEGRATION_TESTS_GUIDE.md)**: Complete testing documentation

## 💡 Usage Examples

### Web Connector

```python
from websites.models import WebInteraction

# Create web interaction
web_interaction = WebInteraction.objects.create(
    url='https://example.com/products/laptop',
    event_type='web.page_view',
    person=person,
    occurred_at=timezone.now()
)

# Resolve touchpoint
touchpoint = resolver.resolve(web_interaction)
print(f"Created touchpoint: {touchpoint.name}")
```

### Email Connector

```python
from email_connector.models import EmailInteraction

# Create email interaction
email_interaction = EmailInteraction.objects.create(
    email_address='user@example.com',
    event_type='email.open',
    person=person,
    occurred_at=timezone.now()
)

# Resolve touchpoint
touchpoint = resolver.resolve(email_interaction)
print(f"Email touchpoint: {touchpoint.name}")
```

### Custom Connector

```python
from connectors.protocols import TouchpointInferenceProtocol

class CustomInteraction(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self):
        return {
            'connector_type': 'custom',
            'source_identifier': 'mobile_app',
            'event_code': 'mobile.screen_view',
            'metadata': {'screen': 'product_detail'}
        }

# Use custom interaction
custom_interaction = CustomInteraction()
touchpoint = resolver.resolve(custom_interaction)
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
interactions = Interaction.objects.select_related('touchpoint', 'action', 'person')

# Batch processing
def process_in_batches(queryset, batch_size=100):
    for i in range(0, queryset.count(), batch_size):
        batch = queryset[i:i + batch_size]
        process_batch(batch)

# Caching
from django.core.cache import cache
cache_key = f"touchpoint:{interaction.id}"
touchpoint = cache.get(cache_key)
if not touchpoint:
    touchpoint = resolver.resolve(interaction)
    cache.set(cache_key, touchpoint, 3600)
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
- **Usage Examples**: `USAGE_EXAMPLES.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Implementation Guide**: `IMPLEMENTATION_PLAN.md`
- **Admin Interface Guide**: `ADMIN_INTERFACE_GUIDE.md`
- **Integration Tests Guide**: `tests/INTEGRATION_TESTS_GUIDE.md`

## 🎯 Roadmap

### Completed Features

- ✅ Core touchpoint resolution framework
- ✅ Web connector implementation
- ✅ Performance monitoring and metrics
- ✅ Enhanced admin interface
- ✅ Management commands
- ✅ Integration tests
- ✅ Comprehensive documentation

### Future Enhancements

- 🔄 Email connector (independent package)
- 🔄 WhatsApp connector (independent package)
- 🔄 Advanced analytics and reporting
- 🔄 Machine learning-based touchpoint optimization
- 🔄 Real-time dashboard
- 🔄 API rate limiting and throttling

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