# Touchpoint Resolution System - Usage Examples

This document provides practical, real-world examples of how to use the Touchpoint Resolution System in various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Web Connector Examples](#web-connector-examples)
3. [Email Connector Examples](#email-connector-examples)
4. [WhatsApp Connector Examples](#whatsapp-connector-examples)
5. [Custom Connector Examples](#custom-connector-examples)
6. [Advanced Scenarios](#advanced-scenarios)
7. [Integration Patterns](#integration-patterns)
8. [Performance Optimization](#performance-optimization)

## Basic Usage

### Example 1: Simple Touchpoint Resolution

```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from websites.models import WebInteraction

# Initialize the resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

# Create a web interaction
web_interaction = WebInteraction.objects.create(
    url='https://example.com/products/laptop',
    event_type='web.page_view',
    person=person,
    occurred_at=timezone.now()
)

# Resolve the touchpoint
touchpoint = resolver.resolve(web_interaction)

print(f"Created touchpoint: {touchpoint.name}")
print(f"Channel: {touchpoint.channel.name}")
print(f"Code: {touchpoint.code}")
```

### Example 2: Batch Processing

```python
from django.db import transaction
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

def process_interactions_batch(interactions, batch_size=100):
    """Process interactions in batches for better performance."""
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    total_processed = 0
    total_created = 0
    total_errors = 0
    
    for i in range(0, len(interactions), batch_size):
        batch = interactions[i:i + batch_size]
        
        with transaction.atomic():
            for interaction in batch:
                try:
                    touchpoint = resolver.resolve(interaction)
                    total_created += 1
                except Exception as e:
                    print(f"Error processing interaction {interaction.id}: {e}")
                    total_errors += 1
                
                total_processed += 1
        
        print(f"Processed batch {i//batch_size + 1}: {total_processed}/{len(interactions)}")
    
    return {
        'processed': total_processed,
        'created': total_created,
        'errors': total_errors
    }

# Usage
interactions = WebInteraction.objects.filter(touchpoint__isnull=True)[:1000]
results = process_interactions_batch(interactions)
print(f"Results: {results}")
```

## Web Connector Examples

### Example 1: E-commerce Product Page

```python
from websites.models import WebInteraction
from connectors.models import TouchpointMappingRule

# Create mapping rule for product pages
product_rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='shop.example.com/products/',
    event_code='web.page_view',
    touchpoint_code='web.product_page_view',
    touchpoint_label='Product Page View',
    channel_code='web',
    medium_code='organic',
    priority=100,
    is_active=True,
    metadata={
        'category': 'product',
        'funnel_stage': 'think',
        'conversion_goal': 'add_to_cart'
    }
)

# Create product page interaction
product_interaction = WebInteraction.objects.create(
    url='https://shop.example.com/products/laptop-dell-xps-13',
    event_type='web.page_view',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'product_id': 'laptop-dell-xps-13',
        'category': 'electronics',
        'price': 1299.99
    }
)

# Resolve touchpoint
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(product_interaction)

print(f"Touchpoint: {touchpoint.name}")
print(f"Code: {touchpoint.code}")
print(f"Metadata: {touchpoint.metadata}")
```

### Example 2: Form Submission

```python
# Create mapping rule for contact form
contact_form_rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='example.com/contact/',
    event_code='web.form_submit',
    touchpoint_code='web.contact_form_submit',
    touchpoint_label='Contact Form Submission',
    channel_code='web',
    medium_code='organic',
    priority=150,
    is_active=True,
    metadata={
        'form_type': 'contact',
        'funnel_stage': 'do',
        'conversion_goal': 'lead_generation'
    }
)

# Create form submission interaction
form_interaction = WebInteraction.objects.create(
    url='https://example.com/contact/',
    event_type='web.form_submit',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'form_data': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Interested in your services'
        }
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(form_interaction)
print(f"Form submission touchpoint: {touchpoint.name}")
```

### Example 3: Blog Post Reading

```python
# Create mapping rule for blog posts
blog_rule = TouchpointMappingRule.objects.create(
    connector_type='web',
    source_identifier='blog.example.com/posts/',
    event_code='web.page_view',
    touchpoint_code='web.blog_post_read',
    touchpoint_label='Blog Post Read',
    channel_code='web',
    medium_code='organic',
    priority=80,
    is_active=True,
    metadata={
        'content_type': 'blog',
        'funnel_stage': 'see',
        'engagement_goal': 'content_consumption'
    }
)

# Create blog reading interaction
blog_interaction = WebInteraction.objects.create(
    url='https://blog.example.com/posts/10-tips-for-better-marketing',
    event_type='web.page_view',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'post_id': '10-tips-for-better-marketing',
        'category': 'marketing',
        'read_time_seconds': 180
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(blog_interaction)
print(f"Blog reading touchpoint: {touchpoint.name}")
```

## Email Connector Examples

### Example 1: Newsletter Open

```python
# Create mapping rule for newsletter opens
newsletter_rule = TouchpointMappingRule.objects.create(
    connector_type='email',
    source_identifier='newsletter@example.com',
    event_code='email.open',
    touchpoint_code='email.newsletter_open',
    touchpoint_label='Newsletter Email Open',
    channel_code='email',
    medium_code='newsletter',
    priority=100,
    is_active=True,
    metadata={
        'email_type': 'newsletter',
        'funnel_stage': 'see',
        'engagement_goal': 'email_engagement'
    }
)

# Create email open interaction (would be created by email connector)
email_interaction = EmailInteraction.objects.create(
    email_address='user@example.com',
    event_type='email.open',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'campaign_id': 'summer_newsletter_2024',
        'subject': 'Summer Sale - 50% Off Everything!',
        'template_id': 'newsletter_template_001'
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(email_interaction)
print(f"Email open touchpoint: {touchpoint.name}")
```

### Example 2: Email Click

```python
# Create mapping rule for email clicks
email_click_rule = TouchpointMappingRule.objects.create(
    connector_type='email',
    source_identifier='marketing@example.com',
    event_code='email.click',
    touchpoint_code='email.marketing_click',
    touchpoint_label='Marketing Email Click',
    channel_code='email',
    medium_code='marketing',
    priority=120,
    is_active=True,
    metadata={
        'email_type': 'marketing',
        'funnel_stage': 'think',
        'conversion_goal': 'website_traffic'
    }
)

# Create email click interaction
email_click_interaction = EmailInteraction.objects.create(
    email_address='user@example.com',
    event_type='email.click',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'campaign_id': 'product_launch_2024',
        'link_url': 'https://example.com/products/new-product',
        'link_text': 'Learn More About Our New Product'
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(email_click_interaction)
print(f"Email click touchpoint: {touchpoint.name}")
```

## WhatsApp Connector Examples

### Example 1: Message Received

```python
# Create mapping rule for WhatsApp messages
whatsapp_rule = TouchpointMappingRule.objects.create(
    connector_type='whatsapp',
    source_identifier='+1234567890',
    event_code='whatsapp.message_received',
    touchpoint_code='whatsapp.message_received',
    touchpoint_label='WhatsApp Message Received',
    channel_code='whatsapp',
    medium_code='direct',
    priority=100,
    is_active=True,
    metadata={
        'message_type': 'text',
        'funnel_stage': 'care',
        'engagement_goal': 'customer_support'
    }
)

# Create WhatsApp message interaction
whatsapp_interaction = WhatsAppInteraction.objects.create(
    phone_number='+1234567890',
    event_type='whatsapp.message_received',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'message_text': 'Hi, I need help with my order',
        'message_id': 'msg_123456789',
        'conversation_id': 'conv_987654321'
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(whatsapp_interaction)
print(f"WhatsApp message touchpoint: {touchpoint.name}")
```

### Example 2: Media Message

```python
# Create mapping rule for media messages
media_rule = TouchpointMappingRule.objects.create(
    connector_type='whatsapp',
    source_identifier='+1234567890',
    event_code='whatsapp.media_received',
    touchpoint_code='whatsapp.media_received',
    touchpoint_label='WhatsApp Media Received',
    channel_code='whatsapp',
    medium_code='direct',
    priority=110,
    is_active=True,
    metadata={
        'message_type': 'media',
        'funnel_stage': 'care',
        'engagement_goal': 'media_sharing'
    }
)

# Create WhatsApp media interaction
media_interaction = WhatsAppInteraction.objects.create(
    phone_number='+1234567890',
    event_type='whatsapp.media_received',
    person=person,
    occurred_at=timezone.now(),
    metadata={
        'media_type': 'image',
        'media_url': 'https://example.com/media/image.jpg',
        'message_id': 'msg_123456790',
        'conversation_id': 'conv_987654321'
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(media_interaction)
print(f"WhatsApp media touchpoint: {touchpoint.name}")
```

## Custom Connector Examples

### Example 1: Mobile App Integration

```python
from connectors.protocols import TouchpointInferenceProtocol

class MobileAppInteraction(TouchpointInferenceProtocol):
    def __init__(self, user_id, screen_name, action_type, metadata=None):
        self.user_id = user_id
        self.screen_name = screen_name
        self.action_type = action_type
        self.metadata = metadata or {}
        self.occurred_at = timezone.now()
    
    def infer_touchpoint_hint(self):
        return {
            'connector_type': 'mobile_app',
            'source_identifier': f'mobile_app_{self.user_id}',
            'event_code': f'mobile.{self.action_type}',
            'metadata': {
                'screen_name': self.screen_name,
                'user_id': self.user_id,
                **self.metadata
            }
        }
    
    def get_person(self):
        # Try to find person by user_id
        try:
            return Person.objects.get(user_id=self.user_id)
        except Person.DoesNotExist:
            return None
    
    def get_occurred_at(self):
        return self.occurred_at

# Create mapping rule for mobile app
mobile_rule = TouchpointMappingRule.objects.create(
    connector_type='mobile_app',
    source_identifier='mobile_app_',
    event_code='mobile.screen_view',
    touchpoint_code='mobile.screen_view',
    touchpoint_label='Mobile App Screen View',
    channel_code='mobile',
    medium_code='app',
    priority=100,
    is_active=True,
    metadata={
        'platform': 'mobile',
        'funnel_stage': 'see',
        'engagement_goal': 'app_usage'
    }
)

# Create mobile app interaction
mobile_interaction = MobileAppInteraction(
    user_id='user_123',
    screen_name='product_detail',
    action_type='screen_view',
    metadata={
        'product_id': 'laptop_001',
        'category': 'electronics'
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(mobile_interaction)
print(f"Mobile app touchpoint: {touchpoint.name}")
```

### Example 2: API Integration

```python
class APIInteraction(TouchpointInferenceProtocol):
    def __init__(self, api_endpoint, method, user_id, metadata=None):
        self.api_endpoint = api_endpoint
        self.method = method
        self.user_id = user_id
        self.metadata = metadata or {}
        self.occurred_at = timezone.now()
    
    def infer_touchpoint_hint(self):
        return {
            'connector_type': 'api',
            'source_identifier': f'api_{self.api_endpoint}',
            'event_code': f'api.{self.method.lower()}',
            'metadata': {
                'endpoint': self.api_endpoint,
                'method': self.method,
                'user_id': self.user_id,
                **self.metadata
            }
        }
    
    def get_person(self):
        try:
            return Person.objects.get(user_id=self.user_id)
        except Person.DoesNotExist:
            return None
    
    def get_occurred_at(self):
        return self.occurred_at

# Create mapping rule for API interactions
api_rule = TouchpointMappingRule.objects.create(
    connector_type='api',
    source_identifier='api_/api/v1/orders',
    event_code='api.post',
    touchpoint_code='api.order_creation',
    touchpoint_label='API Order Creation',
    channel_code='api',
    medium_code='direct',
    priority=100,
    is_active=True,
    metadata={
        'api_type': 'order',
        'funnel_stage': 'do',
        'conversion_goal': 'order_creation'
    }
)

# Create API interaction
api_interaction = APIInteraction(
    api_endpoint='/api/v1/orders',
    method='POST',
    user_id='user_123',
    metadata={
        'order_id': 'order_456',
        'total_amount': 99.99
    }
)

# Resolve touchpoint
touchpoint = resolver.resolve(api_interaction)
print(f"API touchpoint: {touchpoint.name}")
```

## Advanced Scenarios

### Example 1: Conditional Mapping Rules

```python
from connectors.models import TouchpointMappingRule

# Create conditional mapping based on URL parameters
def create_conditional_mapping():
    # Rule for product pages with specific category
    product_category_rule = TouchpointMappingRule.objects.create(
        connector_type='web',
        source_identifier='shop.example.com/products/',
        event_code='web.page_view',
        touchpoint_code='web.product_category_view',
        touchpoint_label='Product Category View',
        channel_code='web',
        medium_code='organic',
        priority=150,
        is_active=True,
        metadata={
            'category': 'electronics',
            'funnel_stage': 'think',
            'conditional': True
        }
    )
    
    # Rule for product pages with sale parameter
    sale_product_rule = TouchpointMappingRule.objects.create(
        connector_type='web',
        source_identifier='shop.example.com/products/',
        event_code='web.page_view',
        touchpoint_code='web.sale_product_view',
        touchpoint_label='Sale Product View',
        channel_code='web',
        medium_code='organic',
        priority=200,  # Higher priority
        is_active=True,
        metadata={
            'sale': True,
            'funnel_stage': 'do',
            'conditional': True
        }
    )

# Custom resolver with conditional logic
class ConditionalTouchpointResolver(DefaultTouchpointResolver):
    def _apply_mapping_rule(self, hint, mapping_rule):
        # Check if rule has conditional metadata
        if mapping_rule.metadata.get('conditional'):
            # Apply conditional logic
            if mapping_rule.metadata.get('category'):
                # Check if URL contains category
                if mapping_rule.metadata['category'] in hint.get('metadata', {}).get('url', ''):
                    return super()._apply_mapping_rule(hint, mapping_rule)
            elif mapping_rule.metadata.get('sale'):
                # Check if URL has sale parameter
                if 'sale=true' in hint.get('metadata', {}).get('url', ''):
                    return super()._apply_mapping_rule(hint, mapping_rule)
        
        return super()._apply_mapping_rule(hint, mapping_rule)
```

### Example 2: Multi-Channel Campaign Tracking

```python
def create_campaign_mapping_rules(campaign_id):
    """Create mapping rules for a multi-channel campaign."""
    
    # Web campaign rule
    web_rule = TouchpointMappingRule.objects.create(
        connector_type='web',
        source_identifier='example.com',
        event_code='web.page_view',
        touchpoint_code=f'web.campaign_{campaign_id}_view',
        touchpoint_label=f'Campaign {campaign_id} Web View',
        channel_code='web',
        medium_code='campaign',
        priority=100,
        is_active=True,
        metadata={
            'campaign_id': campaign_id,
            'channel': 'web',
            'funnel_stage': 'see'
        }
    )
    
    # Email campaign rule
    email_rule = TouchpointMappingRule.objects.create(
        connector_type='email',
        source_identifier='campaign@example.com',
        event_code='email.open',
        touchpoint_code=f'email.campaign_{campaign_id}_open',
        touchpoint_label=f'Campaign {campaign_id} Email Open',
        channel_code='email',
        medium_code='campaign',
        priority=100,
        is_active=True,
        metadata={
            'campaign_id': campaign_id,
            'channel': 'email',
            'funnel_stage': 'see'
        }
    )
    
    # WhatsApp campaign rule
    whatsapp_rule = TouchpointMappingRule.objects.create(
        connector_type='whatsapp',
        source_identifier='+1234567890',
        event_code='whatsapp.message_received',
        touchpoint_code=f'whatsapp.campaign_{campaign_id}_message',
        touchpoint_label=f'Campaign {campaign_id} WhatsApp Message',
        channel_code='whatsapp',
        medium_code='campaign',
        priority=100,
        is_active=True,
        metadata={
            'campaign_id': campaign_id,
            'channel': 'whatsapp',
            'funnel_stage': 'care'
        }
    )
    
    return [web_rule, email_rule, whatsapp_rule]

# Usage
campaign_rules = create_campaign_mapping_rules('summer_sale_2024')
print(f"Created {len(campaign_rules)} campaign mapping rules")
```

### Example 3: A/B Testing Integration

```python
def create_ab_test_mapping_rules(test_id, variants):
    """Create mapping rules for A/B testing."""
    rules = []
    
    for variant in variants:
        rule = TouchpointMappingRule.objects.create(
            connector_type='web',
            source_identifier='example.com',
            event_code='web.page_view',
            touchpoint_code=f'web.ab_test_{test_id}_variant_{variant}',
            touchpoint_label=f'A/B Test {test_id} Variant {variant}',
            channel_code='web',
            medium_code='ab_test',
            priority=100,
            is_active=True,
            metadata={
                'ab_test_id': test_id,
                'variant': variant,
                'test_type': 'ab_test',
                'funnel_stage': 'see'
            }
        )
        rules.append(rule)
    
    return rules

# Usage
ab_test_rules = create_ab_test_mapping_rules(
    'homepage_hero_2024',
    ['control', 'variant_a', 'variant_b']
)
print(f"Created {len(ab_test_rules)} A/B test mapping rules")
```

## Integration Patterns

### Example 1: Django Signals Integration

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

# Initialize resolver
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())

@receiver(post_save, sender=WebInteraction)
def auto_resolve_touchpoint(sender, instance, created, **kwargs):
    """Automatically resolve touchpoint when interaction is created."""
    if created and not instance.touchpoint:
        try:
            touchpoint = resolver.resolve(instance)
            instance.touchpoint = touchpoint
            instance.save(update_fields=['touchpoint'])
            print(f"Auto-resolved touchpoint for interaction {instance.id}")
        except Exception as e:
            print(f"Failed to auto-resolve touchpoint: {e}")

@receiver(post_save, sender=EmailInteraction)
def auto_resolve_email_touchpoint(sender, instance, created, **kwargs):
    """Automatically resolve touchpoint for email interactions."""
    if created and not instance.touchpoint:
        try:
            touchpoint = resolver.resolve(instance)
            instance.touchpoint = touchpoint
            instance.save(update_fields=['touchpoint'])
            print(f"Auto-resolved email touchpoint for interaction {instance.id}")
        except Exception as e:
            print(f"Failed to auto-resolve email touchpoint: {e}")
```

### Example 2: Celery Task Integration

```python
from celery import shared_task
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

@shared_task
def resolve_touchpoint_async(interaction_id, interaction_type):
    """Asynchronously resolve touchpoint for interaction."""
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    try:
        # Get interaction based on type
        if interaction_type == 'web':
            from websites.models import WebInteraction
            interaction = WebInteraction.objects.get(id=interaction_id)
        elif interaction_type == 'email':
            from email_connector.models import EmailInteraction
            interaction = EmailInteraction.objects.get(id=interaction_id)
        else:
            raise ValueError(f"Unknown interaction type: {interaction_type}")
        
        # Resolve touchpoint
        touchpoint = resolver.resolve(interaction)
        
        # Update interaction
        interaction.touchpoint = touchpoint
        interaction.save(update_fields=['touchpoint'])
        
        return {
            'success': True,
            'touchpoint_id': touchpoint.id,
            'touchpoint_code': touchpoint.code
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Usage
# In your interaction creation code
def create_web_interaction(data):
    interaction = WebInteraction.objects.create(**data)
    
    # Queue touchpoint resolution
    resolve_touchpoint_async.delay(interaction.id, 'web')
    
    return interaction
```

### Example 3: REST API Integration

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

@api_view(['POST'])
def resolve_touchpoint_api(request):
    """API endpoint for touchpoint resolution."""
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    try:
        # Get interaction data from request
        interaction_data = request.data
        
        # Create interaction object (this would depend on your implementation)
        interaction = create_interaction_from_data(interaction_data)
        
        # Resolve touchpoint
        touchpoint = resolver.resolve(interaction)
        
        return Response({
            'success': True,
            'touchpoint': {
                'id': touchpoint.id,
                'code': touchpoint.code,
                'name': touchpoint.name,
                'channel': touchpoint.channel.name if touchpoint.channel else None
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

def create_interaction_from_data(data):
    """Create interaction object from API data."""
    # This would depend on your specific implementation
    # For example, if you have a generic interaction model:
    from interactions.models import Interaction
    
    return Interaction.objects.create(
        interaction_type=data['interaction_type'],
        occurred_at=data['occurred_at'],
        metadata=data.get('metadata', {}),
        # ... other fields
    )
```

## Performance Optimization

### Example 1: Caching Strategy

```python
from django.core.cache import cache
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

class CachedTouchpointResolver(DefaultTouchpointResolver):
    def __init__(self, mapping_provider, cache_ttl=3600):
        super().__init__(mapping_provider)
        self.cache_ttl = cache_ttl
    
    def resolve(self, subject):
        # Create cache key
        cache_key = f"touchpoint_resolution:{subject.__class__.__name__}:{hash(str(subject))}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Resolve touchpoint
        touchpoint = super().resolve(subject)
        
        # Cache the result
        cache.set(cache_key, touchpoint, self.cache_ttl)
        
        return touchpoint

# Usage
cached_resolver = CachedTouchpointResolver(DatabaseMappingProvider(), cache_ttl=3600)
touchpoint = cached_resolver.resolve(interaction)
```

### Example 2: Bulk Processing

```python
def bulk_resolve_touchpoints(interactions):
    """Bulk resolve touchpoints for better performance."""
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    # Pre-fetch related objects
    interactions = interactions.select_related('person', 'action')
    
    # Group by type for batch processing
    web_interactions = [i for i in interactions if hasattr(i, 'url')]
    email_interactions = [i for i in interactions if hasattr(i, 'email_address')]
    
    results = []
    
    # Process web interactions
    for interaction in web_interactions:
        try:
            touchpoint = resolver.resolve(interaction)
            results.append({
                'interaction_id': interaction.id,
                'touchpoint_id': touchpoint.id,
                'success': True
            })
        except Exception as e:
            results.append({
                'interaction_id': interaction.id,
                'error': str(e),
                'success': False
            })
    
    # Process email interactions
    for interaction in email_interactions:
        try:
            touchpoint = resolver.resolve(interaction)
            results.append({
                'interaction_id': interaction.id,
                'touchpoint_id': touchpoint.id,
                'success': True
            })
        except Exception as e:
            results.append({
                'interaction_id': interaction.id,
                'error': str(e),
                'success': False
            })
    
    return results

# Usage
interactions = Interaction.objects.filter(touchpoint__isnull=True)[:1000]
results = bulk_resolve_touchpoints(interactions)
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Successfully resolved: {len(successful)}")
print(f"Failed to resolve: {len(failed)}")
```

### Example 3: Database Optimization

```python
def optimized_resolution_query():
    """Optimized query for touchpoint resolution."""
    from django.db import connection
    
    # Use raw SQL for complex queries
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                i.id,
                i.interaction_type,
                i.occurred_at,
                p.id as person_id,
                p.first_name,
                p.last_name
            FROM interactions_interaction i
            LEFT JOIN entities_person p ON i.person_id = p.id
            WHERE i.touchpoint_id IS NULL
            AND i.occurred_at >= %s
            ORDER BY i.occurred_at DESC
            LIMIT 1000
        """, [timezone.now() - timedelta(days=7)])
        
        return cursor.fetchall()

# Usage
interactions_data = optimized_resolution_query()
print(f"Found {len(interactions_data)} interactions to process")
```

## Error Handling and Monitoring

### Example 1: Comprehensive Error Handling

```python
import logging
from connectors.metrics import track_resolution
from connectors.alerting import alert_manager

logger = logging.getLogger(__name__)

def robust_touchpoint_resolution(subject, max_retries=3):
    """Robust touchpoint resolution with error handling and monitoring."""
    
    for attempt in range(max_retries):
        try:
            with track_resolution(
                connector_type=subject.__class__.__name__.lower(),
                metadata={'attempt': attempt + 1}
            ) as tracker:
                
                resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
                touchpoint = resolver.resolve(subject)
                
                tracker.record_success(
                    cache_hit=False,
                    mapping_applied=True,
                    touchpoint_created=True
                )
                
                return touchpoint
                
        except Exception as e:
            logger.error(f"Resolution attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                # Last attempt failed, trigger alert
                alert_manager.trigger_alert(
                    alert_type='resolution_failure',
                    severity='error',
                    title='Touchpoint Resolution Failed',
                    message=f'Failed to resolve touchpoint after {max_retries} attempts: {e}',
                    connector_type=subject.__class__.__name__.lower(),
                    threshold_value=max_retries,
                    actual_value=attempt + 1
                )
                
                # Create fallback touchpoint
                return create_fallback_touchpoint(subject)
            
            # Wait before retry
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff

def create_fallback_touchpoint(subject):
    """Create a fallback touchpoint when resolution fails."""
    from interactions.models import Touchpoint, TouchpointClass, Channel
    
    # Get or create fallback channel
    channel, _ = Channel.objects.get_or_create(
        code='fallback',
        defaults={'name': 'Fallback Channel'}
    )
    
    # Get or create fallback touchpoint class
    touchpoint_class, _ = TouchpointClass.objects.get_or_create(
        code='fallback',
        defaults={
            'name': 'Fallback Touchpoint Class',
            'description': 'Fallback touchpoint class for failed resolutions'
        }
    )
    
    # Create fallback touchpoint
    touchpoint = Touchpoint.objects.create(
        code=f'fallback.{subject.__class__.__name__.lower()}',
        name=f'Fallback {subject.__class__.__name__}',
        touchpoint_class=touchpoint_class,
        channel=channel,
        description=f'Fallback touchpoint for {subject.__class__.__name__}',
        is_active=True
    )
    
    return touchpoint
```

### Example 2: Performance Monitoring

```python
from connectors.monitoring_models import TouchpointResolutionEvent
from django.utils import timezone
from datetime import timedelta

def monitor_resolution_performance():
    """Monitor touchpoint resolution performance."""
    
    # Get recent events
    recent_events = TouchpointResolutionEvent.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(hours=1)
    )
    
    # Calculate metrics
    total_events = recent_events.count()
    successful_events = recent_events.filter(error_occurred=False).count()
    error_rate = (total_events - successful_events) / total_events if total_events > 0 else 0
    
    avg_resolution_time = recent_events.aggregate(
        avg_time=models.Avg('resolution_time_ms')
    )['avg_time'] or 0
    
    # Check thresholds
    if error_rate > 0.05:  # 5% error rate threshold
        alert_manager.trigger_alert(
            alert_type='high_error_rate',
            severity='warning',
            title='High Error Rate Detected',
            message=f'Error rate is {error_rate:.2%} (threshold: 5%)',
            connector_type='all',
            threshold_value=0.05,
            actual_value=error_rate
        )
    
    if avg_resolution_time > 1000:  # 1 second threshold
        alert_manager.trigger_alert(
            alert_type='slow_resolution',
            severity='warning',
            title='Slow Resolution Time',
            message=f'Average resolution time is {avg_resolution_time:.2f}ms (threshold: 1000ms)',
            connector_type='all',
            threshold_value=1000,
            actual_value=avg_resolution_time
        )
    
    return {
        'total_events': total_events,
        'successful_events': successful_events,
        'error_rate': error_rate,
        'avg_resolution_time': avg_resolution_time
    }

# Usage
performance_metrics = monitor_resolution_performance()
print(f"Performance metrics: {performance_metrics}")
```

This comprehensive usage examples document provides practical, real-world scenarios for using the Touchpoint Resolution System. Each example includes complete code that can be adapted to your specific use case.
