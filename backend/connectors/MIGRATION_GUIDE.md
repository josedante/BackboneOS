# Migration Guide: Subject-Dependent → Subject-Agnostic Architecture

## Overview

The connectors app has been refactored to use a **simplified subject-agnostic approach** that eliminates the need for connector objects to implement `TouchpointInferenceProtocol`. This guide helps you migrate existing code.

## What Changed

### Before (Subject-Dependent)
```python
from connectors.protocols import TouchpointInferenceProtocol

class WebInteraction(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(code='web.page_view', ...)

# Usage
resolver.resolve(web_interaction)  # Pass the whole object
```

### After (Subject-Agnostic)
```python
from connectors.protocols import TouchpointHint

# Build hint directly from raw event data
hint = TouchpointHint(code='web.page_view', ...)

# Usage
resolver.resolve(hint, connector_type='web', source_identifier='example.com')
```

## Breaking Changes

### 1. Removed: `TouchpointInferenceProtocol`

**Before:**
```python
class CustomConnector(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(...)
```

**After:**
```python
# No protocol needed - build hints directly
def build_hint_from_event(event_data: dict) -> TouchpointHint:
    return TouchpointHint(
        code=event_data['event_type'],
        channel_code=event_data['channel'],
        medium_code=event_data.get('medium'),
        touchpoint_type_code=event_data.get('type'),
        label=event_data.get('label', ''),
        metadata=event_data.get('metadata', {})
    )
```

### 2. Updated: Resolver Signatures

**Before:**
```python
resolver.resolve(subject: TouchpointInferenceProtocol) -> Touchpoint
```

**After:**
```python
resolver.resolve(
    hint: TouchpointHint,
    *,
    connector_type: str,
    source_identifier: str = ''
) -> Touchpoint
```

### 3. Updated: Mapping Provider Signatures

**Before:**
```python
provider.lookup_mapping(
    subject: TouchpointInferenceProtocol,
    hint: TouchpointHint
) -> Optional[TouchpointMappingRule]
```

**After:**
```python
provider.lookup_mapping(
    *,
    connector_type: str,
    source_identifier: str,
    hint: TouchpointHint
) -> Optional[TouchpointMappingRule]
```

## Migration Steps

### Step 1: Update Resolver Calls

**Before:**
```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(web_interaction)
```

**After:**
```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint

# Build hint from your data source
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View'
)

resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)
```

### Step 2: Replace `infer_touchpoint_hint()` Methods

**Before:**
```python
class WebInteraction(AbstractConnectorInteraction):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(
            code=f"web.{self.event_type}",
            channel_code=self._determine_channel(),
            medium_code=self._determine_medium(),
            label=f"Web {self.event_type.title()}"
        )
```

**After:**
```python
class WebInteraction(AbstractConnectorInteraction):
    @classmethod
    def build_touchpoint_hint_from_event_data(cls, event_data: dict, website) -> TouchpointHint:
        """Build hint directly from raw event data."""
        channel_code = website.channel.code if website.channel else cls._extract_domain(website.base_url)
        medium_code = event_data.get('utm_medium') or cls._analyze_referrer_medium(event_data.get('referrer', ''))
        
        return TouchpointHint(
            code=f"web.{event_data.get('event_type', 'page_view')}",
            channel_code=channel_code,
            medium_code=medium_code,
            touchpoint_type_code='web_page',
            label=f"Web {event_data['event_type'].replace('_', ' ').title()}",
            metadata={
                'website': website.base_url,
                'utm_source': event_data.get('utm_source', ''),
                'utm_campaign': event_data.get('utm_campaign', ''),
            }
        )
```

### Step 3: Update Event Processing Flow

**Before (Post-Creation Resolution):**
```python
# Create interaction first
web_interaction = WebInteraction.objects.create(
    website=website,
    url=url,
    ...
)

# Resolve touchpoint after creation
touchpoint = resolver.resolve(web_interaction)
web_interaction.interaction.touchpoint = touchpoint
web_interaction.interaction.save()
```

**After (Pre-Creation Resolution):**
```python
# Build hint from event data
hint = WebInteraction.build_touchpoint_hint_from_event_data(event_data, website)

# Resolve touchpoint BEFORE creating interaction
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier=website.base_url
)

# Create interaction with touchpoint already assigned
interaction = Interaction.objects.create(
    touchpoint=touchpoint,
    action=action,
    agent=agent,
    occurred_at=event_data.get('occurred_at')
)

# Create web interaction linked to interaction
web_interaction = WebInteraction.objects.create(
    interaction=interaction,
    website=website,
    ...
)
```

### Step 4: Update Tests

**Before:**
```python
class MockConnector(TouchpointInferenceProtocol):
    def __init__(self, hint: TouchpointHint):
        self.hint = hint
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return self.hint

# Test
connector = MockConnector(hint)
touchpoint = resolver.resolve(connector)
```

**After:**
```python
# No mock connector needed!
hint = TouchpointHint(
    code='test.code',
    channel_code='test',
    medium_code='test',
    label='Test'
)

touchpoint = resolver.resolve(hint, connector_type='test', source_identifier='')
```

### Step 5: Update Management Commands

**Before:**
```python
from connectors.protocols import TouchpointInferenceProtocol

class MockConnector(TouchpointInferenceProtocol):
    def __init__(self, hint: TouchpointHint):
        self.hint = hint
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return self.hint

mock = MockConnector(hint)
touchpoint = resolver.resolve(mock)
```

**After:**
```python
# Direct resolution
hint = TouchpointHint(...)
touchpoint = resolver.resolve(hint, connector_type='web', source_identifier='example.com')
```

## Benefits of the New Architecture

### 1. Simpler Testing
- No need for mock connector classes
- Direct hint creation from test data
- Explicit parameter passing makes tests clearer

### 2. More Flexible
- Hints can be built from any data source
- No coupling between connectors and resolution logic
- Easier to add new connector types

### 3. Better Performance
- Pre-creation resolution avoids extra database saves
- Touchpoints resolved before interactions are created
- Cleaner transaction boundaries

### 4. Clearer Code
- Explicit parameters (`connector_type`, `source_identifier`)
- No hidden dependencies on object state
- Easier to understand data flow

## Common Patterns

### Pattern 1: Event Processing
```python
@classmethod
def process_event(cls, event_data: dict):
    # Step 1: Build hint from raw data
    hint = cls.build_touchpoint_hint_from_event_data(event_data, website)
    
    # Step 2: Resolve touchpoint
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    touchpoint = resolver.resolve(
        hint,
        connector_type='web',
        source_identifier=website.base_url
    )
    
    # Step 3: Create interaction with touchpoint
    interaction = Interaction.objects.create(
        touchpoint=touchpoint,
        action=action,
        agent=agent
    )
    
    # Step 4: Create connector-specific interaction
    connector_interaction = cls.objects.create(
        interaction=interaction,
        # ... connector-specific fields
    )
    
    return connector_interaction
```

### Pattern 2: Batch Processing
```python
def process_events_batch(events: list[dict]):
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    for event in events:
        # Build hint
        hint = build_hint_from_event(event)
        
        # Resolve touchpoint
        touchpoint = resolver.resolve(
            hint,
            connector_type=event['type'],
            source_identifier=event.get('source', '')
        )
        
        # Create with resolved touchpoint
        create_interaction(event, touchpoint)
```

### Pattern 3: Custom Hint Builder
```python
class CustomEventProcessor:
    @staticmethod
    def build_hint(event: dict) -> TouchpointHint:
        return TouchpointHint(
            code=event['action_type'],
            channel_code=event['channel'],
            medium_code=event.get('medium', 'direct'),
            touchpoint_type_code=event.get('type', 'custom'),
            label=event.get('name', ''),
            metadata=event.get('metadata', {})
        )
    
    def process(self, event: dict):
        hint = self.build_hint(event)
        touchpoint = self.resolver.resolve(
            hint,
            connector_type='custom',
            source_identifier=event.get('app_id', '')
        )
        # ... create interaction
```

## Checklist

- [ ] Remove `TouchpointInferenceProtocol` imports
- [ ] Remove `infer_touchpoint_hint()` method implementations
- [ ] Add `build_touchpoint_hint_from_event_data()` class methods
- [ ] Update all `resolver.resolve()` calls to new signature
- [ ] Update all `provider.lookup_mapping()` calls to new signature
- [ ] Move touchpoint resolution before interaction creation
- [ ] Remove mock connector classes from tests
- [ ] Update management commands
- [ ] Run tests to verify changes
- [ ] Update documentation

## Support

For questions or issues during migration:
1. Review the updated examples in `USAGE_EXAMPLES.md`
2. Check the `QUICK_REFERENCE.md` for patterns
3. Run tests: `python manage.py test connectors.tests`
4. Check the implementation in `websites/models.py` for reference

## Version History

- **v2.0 (2025)**: Subject-agnostic architecture introduced
- **v1.0 (2024)**: Original subject-dependent architecture

