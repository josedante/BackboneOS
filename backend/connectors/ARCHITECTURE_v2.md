# Connectors Architecture v2.0 - Subject-Agnostic Design

## Overview

The Touchpoint Resolution System has evolved from a **subject-dependent** architecture to a **subject-agnostic** design, eliminating complexity and improving testability.

## Key Changes

### Version 1.0 (Subject-Dependent) ❌
```python
# Required connector objects to implement TouchpointInferenceProtocol
class WebInteraction(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(...)

# Resolution depended on the object
touchpoint = resolver.resolve(web_interaction)
```

### Version 2.0 (Subject-Agnostic) ✅
```python
# Build hints directly from raw data
hint = TouchpointHint(
    code='web.page_view',
    channel_code='web',
    medium_code='organic',
    touchpoint_type_code='web_page',
    label='Web Page View'
)

# Resolution uses explicit parameters
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier='example.com'
)
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         EVENT SOURCE                             │
│              (Browser, Mobile App, API, etc.)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Raw Event    │
                    │   Data (dict)  │
                    └────────┬───────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │  build_hint_from_    │
                 │  event_data()        │
                 └──────────┬───────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ TouchpointHint │
                    │   (dataclass)  │
                    └────────┬───────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │   DefaultTouchpointResolver        │
        │   .resolve(hint, connector_type,   │
        │            source_identifier)      │
        └────────────┬───────────────────────┘
                     │
                     ├──────────────────────────┐
                     ▼                          ▼
           ┌─────────────────┐      ┌──────────────────┐
           │ MappingProvider │      │ Create/Get       │
           │ .lookup_mapping │      │ - Channel        │
           └────────┬────────┘      │ - Medium         │
                    │               │ - TouchpointType │
                    ▼               └──────────┬───────┘
           ┌─────────────────┐                │
           │ Apply Mapping   │                │
           │ Rule (optional) │                │
           └────────┬────────┘                │
                    │                         │
                    └──────────┬──────────────┘
                               ▼
                    ┌──────────────────┐
                    │   Touchpoint     │
                    │   (created)      │
                    └──────────┬───────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Interaction    │
                    │   (with TP)      │
                    └──────────┬───────┘
                               │
                               ▼
                 ┌─────────────────────────┐
                 │ Connector-specific      │
                 │ Interaction             │
                 │ (WebInteraction, etc.)  │
                 └─────────────────────────┘
```

## Core Components

### 1. TouchpointHint (Dataclass)
```python
@dataclass(frozen=True)
class TouchpointHint:
    code: Optional[str] = None
    channel_code: Optional[str] = None
    medium_code: Optional[str] = None
    touchpoint_type_code: Optional[str] = None
    label: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

**Purpose**: Structured representation of touchpoint data extracted from raw events.

### 2. TouchpointResolverProtocol
```python
class TouchpointResolverProtocol(Protocol):
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        ...
```

**Purpose**: Defines the interface for touchpoint resolution without subject dependency.

### 3. MappingProviderProtocol
```python
class MappingProviderProtocol(Protocol):
    def lookup_mapping(
        self,
        *,
        connector_type: str,
        source_identifier: str,
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        ...
```

**Purpose**: Looks up mapping rules using explicit parameters instead of subject introspection.

### 4. DefaultTouchpointResolver
```python
class DefaultTouchpointResolver:
    def __init__(self, mapping_provider: MappingProviderProtocol):
        self.mapping_provider = mapping_provider
    
    def resolve(
        self,
        hint: TouchpointHint,
        *,
        connector_type: str,
        source_identifier: str = ''
    ) -> Touchpoint:
        # 1. Look up mapping rule
        mapping_rule = self.mapping_provider.lookup_mapping(
            connector_type=connector_type,
            source_identifier=source_identifier,
            hint=hint
        )
        
        # 2. Apply mapping rule if found
        if mapping_rule:
            hint = self._apply_mapping_rule(hint, mapping_rule)
        
        # 3. Get or create touchpoint
        touchpoint = self._get_or_create_touchpoint(hint)
        
        return touchpoint
```

**Purpose**: Core resolution logic that creates touchpoints from hints.

## Event Processing Flow

### 1. Web Event Processing (Complete Example)

```python
# Client sends event data
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products',
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'user_agent': 'Mozilla/5.0...'
}

# Server receives and processes
class WebInteraction:
    @classmethod
    def process_page_view_event(cls, event_data: dict):
        # Step 1: Get website
        website, _ = Website.objects.get_or_create(
            base_url=event_data['website_base']
        )
        
        # Step 2: Build hint from raw data
        hint = cls.build_touchpoint_hint_from_event_data(event_data, website)
        
        # Step 3: Resolve touchpoint BEFORE creating interaction
        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        touchpoint = resolver.resolve(
            hint,
            connector_type='web',
            source_identifier=website.base_url
        )
        
        # Step 4: Get/create agent and action
        agent = cls._get_or_create_agent(event_data.get('user_agent'))
        action, _ = Action.objects.get_or_create(code='page_view')
        
        # Step 5: Create interaction WITH touchpoint
        interaction = Interaction.objects.create(
            touchpoint=touchpoint,
            action=action,
            agent=agent,
            occurred_at=event_data.get('occurred_at')
        )
        
        # Step 6: Create web interaction
        web_interaction = cls.objects.create(
            interaction=interaction,
            website=website,
            url=event_data['full_url'],
            utm_source=event_data.get('utm_source'),
            utm_medium=event_data.get('utm_medium'),
            # ... other fields
        )
        
        return [web_interaction]
```

## Benefits

### 1. Simpler Testing
```python
# OLD: Needed mock connector classes
class MockConnector(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self):
        return TouchpointHint(...)

# NEW: Direct hint creation
hint = TouchpointHint(code='test.code', ...)
touchpoint = resolver.resolve(hint, connector_type='test', source_identifier='')
```

### 2. More Flexible
- Hints can be built from any data source (API, file, database, etc.)
- No coupling between connectors and resolution logic
- Easier to add new connector types

### 3. Better Performance
- Pre-creation resolution avoids extra database operations
- Touchpoints resolved before interactions are created
- Cleaner transaction boundaries

### 4. Clearer Code
- Explicit parameters make dependencies obvious
- No hidden dependencies on object state
- Easier to understand data flow

## Three-Dimensional Classification

Each touchpoint is classified along three dimensions:

### 1. Channel (WHERE)
**Where did the interaction originate?**
- `web` - Website traffic
- `email` - Email campaigns
- `mobile_app` - Mobile application
- `social` - Social media
- `api` - API integration

### 2. Medium (HOW)
**How did they get there?**
- `organic` - Organic search/direct
- `cpc` / `paid` - Paid advertising
- `social` - Social media referral
- `email` - Email campaign
- `referral` - External referral

### 3. Touchpoint Type (WHAT)
**What type of touchpoint is it?**
- `web_page` - Web page view
- `web_form` - Form submission
- `email_open` - Email opened
- `email_click` - Email link clicked
- `mobile_screen` - Mobile screen view

### Example
```python
TouchpointHint(
    code='web.product_view',
    channel_code='web',           # WHERE: Website
    medium_code='cpc',             # HOW: Paid search
    touchpoint_type_code='web_page',  # WHAT: Page view
    label='Product Page View'
)
```

This creates a touchpoint representing: **A product page view (WHAT) on the website (WHERE) from paid search (HOW)**

## Migration Path

For migrating from v1.0 to v2.0, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

### Quick Migration Checklist
- [ ] Remove `TouchpointInferenceProtocol` implementations
- [ ] Add `build_touchpoint_hint_from_event_data()` methods
- [ ] Update resolver calls to new signature
- [ ] Move touchpoint resolution before interaction creation
- [ ] Update tests to use direct hint creation
- [ ] Remove mock connector classes

## Documentation

- **[README.md](README.md)** - Main documentation and overview
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick patterns and commands
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - Practical examples
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - v1.0 → v2.0 migration
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0** | 2025-01 | Subject-agnostic architecture, pre-creation resolution |
| **1.0** | 2024-12 | Original subject-dependent architecture |

