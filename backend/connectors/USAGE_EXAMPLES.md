# Touchpoint Resolution System - Usage Examples

> **Note**: This documentation reflects the **subject-agnostic architecture** (v2.0, 2025). For migrating from the old architecture, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

This document provides practical, real-world examples of how to use the Touchpoint Resolution System.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Web Connector Examples](#web-connector-examples)
3. [Custom Connector Examples](#custom-connector-examples)
4. [Advanced Scenarios](#advanced-scenarios)
5. [Performance Optimization](#performance-optimization)
6. [Integration Patterns](#integration-patterns)

## Basic Usage

### Example 1: Simple Touchpoint Resolution

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

# Initialize the resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Build a hint from your event data
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View',
    metadata={'url': '/products/laptop'}
)

# Resolve the touchpoint (subject-agnostic)
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)

print(f"Created touchpoint: {touchpoint.name}")
print(f"Channel: {touchpoint.channel.name if touchpoint.channel else 'N/A'}")
print(f"Code: {touchpoint.code}")
```

### Example 2: Event Processing Flow

```python
from websites.models import WebInteraction

# Event data from browser client
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://shop.example.com',
    'full_url': 'https://shop.example.com/products/laptop',
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'utm_campaign': 'summer_sale',
    'referrer': 'https://google.com/search?q=laptops',
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'session_id': 'abc123xyz',
    'visitor_cookie': 'visitor_456'
}

# Process the event (handles touchpoint resolution internally)
interactions = WebInteraction.process_page_view_event(event_data)

print(f"Created {len(interactions)} interactions")
for interaction in interactions:
    print(f"  - {interaction.interaction.touchpoint.name if interaction.interaction.touchpoint else 'No touchpoint'}")
```

## Web Connector Examples

### Example 1: E-commerce Product Page

```python
from websites.models import WebInteraction
from connectors.models import TouchpointMappingRule

# Step 1: Create a mapping rule for product pages
product_rule = TouchpointMappingRule.objects.create(
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
    metadata={
        'category': 'ecommerce',
        'page_type': 'product'
    }
)

# Step 2: Process a product page view event
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://shop.example.com',
    'full_url': 'https://shop.example.com/products/laptop-dell-xps',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'user_agent': 'Mozilla/5.0...',
    'payload': {
        'product_id': 'laptop-dell-xps',
        'product_category': 'electronics',
        'product_price': 1299.99
    }
}

# Process event - mapping rule will be applied
interactions = WebInteraction.process_page_view_event(event_data)

# The touchpoint will have code 'web.product_page' due to the mapping rule
print(f"Touchpoint: {interactions[0].interaction.touchpoint.code}")
# Output: Touchpoint: web.product_page
```

### Example 2: Form Submission with UTM Tracking

```python
from websites.models import WebInteraction

# Contact form submission from paid campaign
event_data = {
    'event_type': 'form_submit',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/contact',
    'utm_source': 'facebook',
    'utm_medium': 'cpc',
    'utm_campaign': 'lead_gen_2025',
    'utm_content': 'contact_form_cta',
    'user_agent': 'Mozilla/5.0...',
    'payload': {
        'form_type': 'contact',
        'fields_filled': ['name', 'email', 'message'],
        'lead_score': 85
    }
}

# Process the form submission
interactions = WebInteraction.process_form_submit_event(event_data)

# Touchpoint will have medium='cpc' from UTM parameters
touchpoint = interactions[0].interaction.touchpoint
print(f"Medium: {touchpoint.medium.code if touchpoint.medium else 'N/A'}")
# Output: Medium: cpc
```

### Example 3: Multi-Interaction Scenario

```python
from websites.models import WebInteraction

# Page view that creates multiple interactions
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://blog.example.com',
    'full_url': 'https://blog.example.com/article/how-to-code',
    'utm_source': 'twitter',
    'utm_medium': 'social',
    'referrer': 'https://twitter.com/user/status/123',
    'user_agent': 'Mozilla/5.0...',
    'session_id': 'session_789',
    'payload': {
        'article_id': 'how-to-code',
        'author': 'Jane Doe',
        'read_time': 5
    }
}

# Process - may create up to 3 interactions:
# 1. Page view interaction
# 2. Referrer click interaction (from Twitter)
# 3. Session start interaction (if new session)
interactions = WebInteraction.process_page_view_event(event_data)

print(f"Created {len(interactions)} interactions:")
for i, interaction in enumerate(interactions, 1):
    tp = interaction.interaction.touchpoint
    action = interaction.interaction.action
    print(f"{i}. Action: {action.name if action else 'N/A'}, "
          f"Touchpoint: {tp.code if tp else 'N/A'}")
```

## Custom Connector Examples

### Example 1: Mobile App Events

```python
from connectors.protocols import TouchpointHint
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from interactions.models import Interaction, Action, Agent

def process_mobile_event(event_data: dict):
    """Process events from a mobile application."""
    
    # Step 1: Build hint from mobile event data
    hint = TouchpointHint(
        code=f"mobile.{event_data['screen_name']}",
        channel_code='mobile_app',
        medium_code='app',
        touchpoint_type_code='mobile_screen',
        label=f"Mobile {event_data['screen_name'].replace('_', ' ').title()}",
        metadata={
            'device_type': event_data.get('device_type'),
            'app_version': event_data.get('app_version'),
            'os_version': event_data.get('os_version'),
        }
    )
    
    # Step 2: Resolve touchpoint
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    touchpoint = resolver.resolve(
        hint,
        connector_type='mobile',
        source_identifier=event_data.get('app_id', 'ios_app')
    )
    
    # Step 3: Create agent
    agent, _ = Agent.objects.get_or_create(
        identifier=event_data.get('device_id'),
        defaults={
            'agent_type': 'mobile_device',
            'display_name': f"Mobile Device {event_data.get('device_type')}"
        }
    )
    
    # Step 4: Get action
    action, _ = Action.objects.get_or_create(
        code='screen_view',
        defaults={
            'name': 'Screen View',
            'description': 'User viewed a screen in the mobile app'
        }
    )
    
    # Step 5: Create interaction with touchpoint
    interaction = Interaction.objects.create(
        touchpoint=touchpoint,
        action=action,
        agent=agent,
        payload=event_data,
        occurred_at=event_data.get('timestamp')
    )
    
    return interaction

# Usage
mobile_event = {
    'screen_name': 'product_detail',
    'app_id': 'com.example.shop',
    'app_version': '2.1.0',
    'device_id': 'device_abc123',
    'device_type': 'iPhone',
    'os_version': '17.2',
    'timestamp': timezone.now(),
    'metadata': {
        'product_id': 'laptop-001',
        'category': 'electronics'
    }
}

interaction = process_mobile_event(mobile_event)
print(f"Created mobile interaction: {interaction.touchpoint.code}")
```

### Example 2: API Integration Events

```python
from connectors.protocols import TouchpointHint
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

class APIEventProcessor:
    """Process events from API integrations."""
    
    def __init__(self):
        self.resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    def build_hint_from_api_call(self, api_data: dict) -> TouchpointHint:
        """Build touchpoint hint from API call data."""
        return TouchpointHint(
            code=f"api.{api_data['endpoint']}",
            channel_code='api',
            medium_code='integration',
            touchpoint_type_code='api_endpoint',
            label=f"API {api_data['method']} {api_data['endpoint']}",
            metadata={
                'method': api_data['method'],
                'version': api_data.get('api_version', 'v1'),
                'client_id': api_data.get('client_id'),
            }
        )
    
    def process_api_call(self, api_data: dict):
        """Process an API call as a touchpoint interaction."""
        hint = self.build_hint_from_api_call(api_data)
        
        touchpoint = self.resolver.resolve(
            hint,
            connector_type='api',
            source_identifier=api_data.get('client_id', '')
        )
        
        # Get or create API agent
        agent, _ = Agent.objects.get_or_create(
            identifier=api_data['client_id'],
            defaults={
                'agent_type': 'api_client',
                'display_name': f"API Client {api_data['client_id']}"
            }
        )
        
        # Create action
        action, _ = Action.objects.get_or_create(
            code=f"api_{api_data['method'].lower()}",
            defaults={
                'name': f"API {api_data['method']}",
                'description': f"API {api_data['method']} request"
            }
        )
        
        # Create interaction
        interaction = Interaction.objects.create(
            touchpoint=touchpoint,
            action=action,
            agent=agent,
            payload=api_data,
            occurred_at=timezone.now()
        )
        
        return interaction

# Usage
processor = APIEventProcessor()

api_call = {
    'endpoint': '/orders',
    'method': 'POST',
    'client_id': 'partner_123',
    'api_version': 'v2',
    'request_data': {'order_id': 'ORD-456', 'amount': 299.99}
}

interaction = processor.process_api_call(api_call)
print(f"API interaction created: {interaction.touchpoint.code}")
```

## Advanced Scenarios

### Example 1: Multi-Source Attribution

```python
from connectors.protocols import TouchpointHint
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from websites.models import WebInteraction

def analyze_customer_journey(visitor_cookie: str):
    """Analyze all touchpoints in a customer's journey."""
    
    # Get all interactions for this visitor
    web_interactions = WebInteraction.objects.filter(
        visitor_cookie=visitor_cookie
    ).select_related(
        'interaction__touchpoint__channel',
        'interaction__touchpoint__medium',
        'interaction__action'
    ).order_by('interaction__occurred_at')
    
    journey = []
    for web_int in web_interactions:
        interaction = web_int.interaction
        touchpoint = interaction.touchpoint
        
        journey.append({
            'timestamp': interaction.occurred_at,
            'action': interaction.action.name if interaction.action else 'N/A',
            'touchpoint': touchpoint.code if touchpoint else 'N/A',
            'channel': touchpoint.channel.code if touchpoint and touchpoint.channel else 'N/A',
            'medium': touchpoint.medium.code if touchpoint and touchpoint.medium else 'N/A',
            'url': web_int.url,
            'utm_campaign': web_int.utm_campaign
        })
    
    return journey

# Usage
journey = analyze_customer_journey('visitor_abc123')
print(f"Customer journey ({len(journey)} touchpoints):")
for i, step in enumerate(journey, 1):
    print(f"{i}. {step['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
          f"{step['action']} via {step['channel']}/{step['medium']}")
```

### Example 2: Campaign Performance Analysis

```python
from django.db.models import Count
from websites.models import WebInteraction

def analyze_campaign_performance(campaign_name: str):
    """Analyze touchpoint performance for a specific campaign."""
    
    # Get all interactions for this campaign
    campaign_interactions = WebInteraction.objects.filter(
        utm_campaign=campaign_name
    ).select_related(
        'interaction__touchpoint__channel',
        'interaction__touchpoint__medium',
        'interaction__action'
    )
    
    # Group by touchpoint
    touchpoint_stats = {}
    
    for web_int in campaign_interactions:
        touchpoint = web_int.interaction.touchpoint
        if not touchpoint:
            continue
        
        tp_code = touchpoint.code
        if tp_code not in touchpoint_stats:
            touchpoint_stats[tp_code] = {
                'name': touchpoint.name,
                'channel': touchpoint.channel.code if touchpoint.channel else 'N/A',
                'medium': touchpoint.medium.code if touchpoint.medium else 'N/A',
                'count': 0,
                'unique_visitors': set()
            }
        
        touchpoint_stats[tp_code]['count'] += 1
        if web_int.visitor_cookie:
            touchpoint_stats[tp_code]['unique_visitors'].add(web_int.visitor_cookie)
    
    # Convert to list and add unique visitor count
    results = []
    for code, stats in touchpoint_stats.items():
        results.append({
            'touchpoint_code': code,
            'touchpoint_name': stats['name'],
            'channel': stats['channel'],
            'medium': stats['medium'],
            'total_interactions': stats['count'],
            'unique_visitors': len(stats['unique_visitors'])
        })
    
    # Sort by total interactions
    results.sort(key=lambda x: x['total_interactions'], reverse=True)
    
    return results

# Usage
performance = analyze_campaign_performance('summer_sale_2025')
print(f"Campaign Performance:")
for tp in performance:
    print(f"  {tp['touchpoint_name']}: {tp['total_interactions']} interactions "
          f"({tp['unique_visitors']} unique visitors)")
```

## Performance Optimization

### Example 1: Batch Event Processing

```python
from django.db import transaction
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

def process_events_batch(events: list[dict], batch_size: int = 100):
    """Process events in batches with caching for performance."""
    
    # Use cached resolver for better performance
    cached_provider = CachedMappingProvider()
    cached_provider.warm_cache()  # Warm up the cache
    resolver = CachedTouchpointResolver(cached_provider)
    
    total_processed = 0
    total_created = 0
    errors = []
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        
        with transaction.atomic():
            for event in batch:
                try:
                    # Process event based on type
                    if event['event_type'] == 'page_view':
                        WebInteraction.process_page_view_event(event)
                    elif event['event_type'] == 'form_submit':
                        WebInteraction.process_form_submit_event(event)
                    # ... other event types
                    
                    total_created += 1
                except Exception as e:
                    errors.append({
                        'event': event,
                        'error': str(e)
                    })
                
                total_processed += 1
        
        # Progress indicator
        print(f"Processed {total_processed}/{len(events)} events...")
    
    return {
        'total_processed': total_processed,
        'total_created': total_created,
        'errors': len(errors),
        'error_details': errors
    }

# Usage
events = [
    {
        'event_type': 'page_view',
        'website_base': 'https://example.com',
        'full_url': 'https://example.com/page1',
        'user_agent': 'Mozilla/5.0...'
    },
    # ... more events
]

results = process_events_batch(events, batch_size=50)
print(f"Results: {results['total_created']} interactions created, "
      f"{results['errors']} errors")
```

### Example 2: Preload Common Touchpoints

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from interactions.models import Touchpoint

def preload_common_touchpoints():
    """Preload common touchpoints for better performance."""
    
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    common_hints = [
        TouchpointHint(
            code='web.page_view',
            channel_code='web',
            medium_code='organic',
            touchpoint_type_code='web_page',
            label='Web Page View'
        ),
        TouchpointHint(
            code='web.form_submit',
            channel_code='web',
            medium_code='organic',
            touchpoint_type_code='web_form',
            label='Web Form Submit'
        ),
        # ... more common touchpoints
    ]
    
    created_touchpoints = []
    for hint in common_hints:
        touchpoint = resolver.resolve(
            hint,
            connector_type='web',
            source_identifier=''
        )
        created_touchpoints.append(touchpoint)
    
    return created_touchpoints

# Run once at application startup or via management command
touchpoints = preload_common_touchpoints()
print(f"Preloaded {len(touchpoints)} common touchpoints")
```

## Integration Patterns

### Example 1: Webhook Integration

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def webhook_handler(request):
    """Handle webhook events from external services."""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Build hint from webhook data
        hint = TouchpointHint(
            code=f"webhook.{data['event_type']}",
            channel_code='webhook',
            medium_code='integration',
            touchpoint_type_code='webhook_event',
            label=f"Webhook {data['event_type'].title()}",
            metadata=data.get('metadata', {})
        )
        
        # Resolve touchpoint
        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        touchpoint = resolver.resolve(
            hint,
            connector_type='webhook',
            source_identifier=data.get('source', 'external')
        )
        
        # Create interaction
        # ... (create agent, action, interaction)
        
        return JsonResponse({'success': True, 'touchpoint': touchpoint.code})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### Example 2: Background Task Processing

```python
from celery import shared_task
from websites.models import WebInteraction

@shared_task
def process_event_async(event_data: dict):
    """Process event asynchronously using Celery."""
    
    try:
        event_type = event_data.get('event_type')
        
        if event_type == 'page_view':
            interactions = WebInteraction.process_page_view_event(event_data)
        elif event_type == 'form_submit':
            interactions = WebInteraction.process_form_submit_event(event_data)
        else:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return {
            'success': True,
            'interactions_created': len(interactions)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Usage
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products',
    'user_agent': 'Mozilla/5.0...'
}

# Queue for async processing
task = process_event_async.delay(event_data)
print(f"Task queued: {task.id}")
```

## Best Practices

### 1. Always Build Hints from Raw Data
```python
# Good: Build hint from raw event data
hint = WebInteraction.build_touchpoint_hint_from_event_data(event_data, website)

# Avoid: Hardcoding hint values
hint = TouchpointHint(code='web.page_view', ...)  # Only for testing/examples
```

### 2. Resolve Touchpoints Before Creating Interactions
```python
# Good: Pre-creation resolution
hint = build_hint(event_data)
touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
interaction = Interaction.objects.create(touchpoint=touchpoint, ...)

# Avoid: Post-creation resolution (old pattern)
interaction = Interaction.objects.create(...)
touchpoint = resolver.resolve(interaction)  # This won't work anymore
```

### 3. Use Caching for High-Volume Scenarios
```python
# Good: Use cached resolver for performance
from connectors.resolvers import CachedTouchpointResolver
from connectors.mapping_providers import CachedMappingProvider

resolver = CachedTouchpointResolver(CachedMappingProvider())

# Avoid: Creating new resolver instances in loops
for event in events:
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())  # Don't do this
    touchpoint = resolver.resolve(...)
```

### 4. Leverage Event Processing Methods
```python
# Good: Use built-in event processing
interactions = WebInteraction.process_page_view_event(event_data)

# Avoid: Manual creation without touchpoint resolution
web_interaction = WebInteraction.objects.create(...)  # Missing touchpoint!
```

## Further Reading

- [README.md](README.md) - Main documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick patterns
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migration from old architecture
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
