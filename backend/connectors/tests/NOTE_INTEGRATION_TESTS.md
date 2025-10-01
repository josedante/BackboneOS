# Integration Tests Status

## Overview

The integration tests in `test_touchpoint_resolution_integration.py` were originally written for the v1.0 subject-dependent architecture. They have been partially updated for v2.0.

## Current Status

| Test Class | Status | Notes |
|------------|--------|-------|
| `CompleteResolutionWorkflowTest` | ✅ **Updated** | First 2 tests updated to v2.0 API |
| `SystemIntegrationTest` | ⚠️ **Skipped** | Needs v2.0 update |
| `PerformanceIntegrationTest` | ⚠️ **Skipped** | Needs v2.0 update |
| `ErrorRecoveryIntegrationTest` | ⚠️ **Skipped** | Needs v2.0 update |

## What Was Updated

### ✅ CompleteResolutionWorkflowTest (Partial)

**Updated Tests:**
1. `test_complete_web_resolution_workflow` - Now uses `WebInteraction.process_page_view_event()`
2. Tests event processing flow with mapping rules

**Pattern Used:**
```python
# Create event data dict
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://test.com',
    'full_url': 'https://test.com/products',
    'utm_source': 'google',
    'utm_medium': 'organic',
    ...
}

# Process using v2.0 API
interactions = WebInteraction.process_page_view_event(event_data)

# Verify touchpoint was pre-resolved
self.assertIsNotNone(interactions[0].interaction.touchpoint)
```

## What Needs Updating

### ⚠️ Remaining Tests

The following test classes are currently **skipped** and need similar updates:

1. **SystemIntegrationTest**
   - Tests transaction rollback behavior
   - Update to use event processing methods
   - Verify touchpoints are created transactionally

2. **PerformanceIntegrationTest**
   - Tests bulk event processing
   - Update to process batches of event_data dicts
   - Measure performance of v2.0 resolution

3. **ErrorRecoveryIntegrationTest**
   - Tests error handling and recovery
   - Update to test errors in event processing
   - Verify graceful degradation

## Update Pattern

To update remaining tests, follow this pattern:

### Old (v1.0)
```python
# Create WebInteraction directly
web_interaction = WebInteraction.objects.create(
    interaction=interaction,
    website=website,
    url='https://example.com',
    event_type='page_view',  # ❌ Doesn't exist
    ...
)

# Resolve touchpoint after creation
touchpoint = resolver.resolve(web_interaction)  # ❌ Old API
```

### New (v2.0)
```python
# Create event data dict
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products',
    'user_agent': 'Mozilla/5.0...',
    ...
}

# Process event (creates interaction + web_interaction with touchpoint)
interactions = WebInteraction.process_page_view_event(event_data)

# Touchpoint is already resolved
touchpoint = interactions[0].interaction.touchpoint
```

## Areas Currently Covered

Even with some tests skipped, we still have good coverage:

### ✅ Well Tested (35/35 passing)
- **Core Protocols** - All protocol interfaces
- **Resolvers** - DefaultTouchpointResolver, CachedTouchpointResolver
- **Mapping Providers** - DatabaseMappingProvider, CachedMappingProvider
- **Hint Building** - TouchpointHint creation and usage

### ⚠️ Partially Tested
- **Event Processing** - Basic workflow tested
- **Mapping Rules** - Application tested
- **Web Connector** - Page view events tested

### ❌ Not Currently Tested (Skipped)
- **Transaction Rollback** - SystemIntegrationTest
- **Bulk Performance** - PerformanceIntegrationTest  
- **Error Recovery** - ErrorRecoveryIntegrationTest

## Priority for Updates

1. **High**: `SystemIntegrationTest` - Important for data integrity
2. **Medium**: `ErrorRecoveryIntegrationTest` - Good for robustness
3. **Low**: `PerformanceIntegrationTest` - Nice to have

## How to Contribute

To update a skipped test class:

1. Remove the `@skip` decorator
2. Update `setUp()` to create event_data dicts instead of objects
3. Replace `WebInteraction.objects.create()` with `WebInteraction.process_*_event()`
4. Update assertions to expect touchpoints to be pre-resolved
5. Run tests: `python manage.py test connectors.tests.test_touchpoint_resolution_integration`

## References

- **Working Examples**: See `test_protocols.py`, `test_resolvers.py`, `test_mapping_providers.py`
- **Event Processing**: See `websites/models.py` - `process_page_view_event()` and `process_click_event()`
- **Migration Guide**: See `connectors/MIGRATION_GUIDE.md`

