# App-Specific Touchpoint Resolver Pattern

## Overview

This document outlines the established pattern for implementing app-specific touchpoint resolvers and mapping providers in the BackboneOS system. This pattern ensures that each app can provide specialized touchpoint resolution logic while maintaining consistency with the overall touchpoint resolution framework.

## Pattern Structure

### 1. App-Specific Resolver

Each app should implement its own resolver that extends `DefaultTouchpointResolver`:

```python
# apps/{app_name}/resolvers.py
from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol

class {AppName}TouchpointResolver(DefaultTouchpointResolver):
    """
    {App}-specific touchpoint resolver with {app}-specific logic.
    """
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """Get connector type for {app} interactions."""
        return '{app}'
    
    def _ensure_required_fields(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> TouchpointHint:
        """
        Ensure {app}-specific required fields with {app}-specific defaults.
        """
        # App-specific logic here
        return hint
    
    def _resolve_touchpoint(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint):
        """
        Create touchpoint with {app}-specific defaults.
        """
        # App-specific touchpoint creation logic
        pass
```

### 2. App-Specific Mapping Provider

Each app should implement its own mapping provider:

```python
# apps/{app_name}/resolvers.py
class {AppName}MappingProvider:
    """
    {App}-specific mapping provider with business logic.
    """
    
    def lookup_mapping(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint):
        """
        Look up {app}-specific mapping rules.
        """
        # App-specific mapping logic
        pass
```

### 3. Model Integration

Models in each app should use the app-specific resolver:

```python
# apps/{app_name}/models.py
from .resolvers import {AppName}TouchpointResolver, {AppName}MappingProvider

class {AppModel}(Interaction):
    def save(self, *args, **kwargs):
        if not self.touchpoint:
            try:
                resolver = {AppName}TouchpointResolver({AppName}MappingProvider())
                resolved_touchpoint = resolver.resolve(self)
                self.touchpoint = resolved_touchpoint
            except Exception as e:
                # Fallback to manual touchpoint creation
                self._create_manual_touchpoint()
        
        super().save(*args, **kwargs)
```

## Implementation Examples

### Sales App Implementation

The sales app implements this pattern with:

1. **SalesTouchpointResolver**: Handles division-based sales channels, opportunity context, and sales-specific touchpoint creation
2. **SalesMappingProvider**: Provides sales-specific mapping rules and business logic
3. **SalesSession Model**: Uses the sales-specific resolver for automatic touchpoint creation

Key features:
- **Representative-first channel resolution**: Prioritizes the sales representative's division over the product's division
- **AI Agent Support**: Full support for AI agents as sales representatives with division assignment
- Division-specific channel resolution (`sales_{division_code}`)
- Sales context in touchpoint metadata
- Appropriate funnel stage assignment based on interaction type
- Fallback to manual touchpoint creation

**Business Rule**: The sales channel is determined by the division that the sales representative works for, not the product being sold. This ensures proper attribution to the sales team handling the interaction.

**AI Agent Integration**: The sales touchpoint's main characteristic is the participating representative, which can be either a human User or an AI Agent. AI agents are fully supported with:
- Division assignment through metadata configuration
- Proper channel resolution based on agent's division
- Enhanced metadata tracking for AI agent interactions
- Seamless integration with existing touchpoint resolution system

### Websites App Implementation

The websites app implements this pattern with:

1. **WebTouchpointResolver**: Handles UTM analysis, referrer analysis, and web-specific touchpoint logic
2. **Web-specific channel resolution**: Creates website-specific channels for better tracking
3. **UTM parameter analysis**: Analyzes UTM parameters to determine traffic sources

Key features:
- UTM parameter analysis for traffic source detection
- Referrer analysis for external click detection
- Website-specific channel creation
- Native app detection via user agent analysis

## Benefits of This Pattern

### 1. **Separation of Concerns**
- Each app handles its own touchpoint resolution logic
- Generic framework remains clean and focused
- Business logic is encapsulated within the appropriate app

### 2. **Extensibility**
- New apps can easily implement their own resolvers
- Existing apps can extend their resolvers without affecting others
- Framework can be enhanced without breaking app-specific logic

### 3. **Maintainability**
- App-specific logic is co-located with the app
- Changes to one app's touchpoint logic don't affect others
- Clear boundaries between generic and specific functionality

### 4. **Testability**
- Each app can test its own touchpoint resolution logic
- Mocking and testing is simplified with app-specific components
- Integration tests can focus on app-specific scenarios

## Implementation Guidelines

### 1. **Naming Conventions**
- Resolver: `{AppName}TouchpointResolver`
- Mapping Provider: `{AppName}MappingProvider`
- File: `apps/{app_name}/resolvers.py`

### 2. **Required Methods**
- `_get_connector_type()`: Return the app's connector type
- `_ensure_required_fields()`: Provide app-specific defaults
- `_resolve_touchpoint()`: Create touchpoints with app-specific logic

### 3. **Error Handling**
- Always provide fallback to manual touchpoint creation
- Log errors for debugging
- Ensure system continues to function even if resolution fails

### 4. **Documentation**
- Document app-specific business logic
- Provide examples of expected touchpoint codes
- Explain channel and medium code conventions

## Future Implementations

When implementing touchpoint resolution for new apps, follow this pattern:

1. **Create app-specific resolver** extending `DefaultTouchpointResolver`
2. **Create app-specific mapping provider** with business logic
3. **Update models** to use the app-specific resolver
4. **Write comprehensive tests** for the app-specific logic
5. **Document the implementation** following this pattern

## Migration Strategy

For existing apps that don't follow this pattern:

1. **Create app-specific resolver** with current logic
2. **Create app-specific mapping provider** with current rules
3. **Update models** to use app-specific resolver
4. **Test thoroughly** to ensure no regression
5. **Remove generic resolver usage** once confirmed working

This pattern ensures consistency, maintainability, and extensibility across all apps in the BackboneOS system.
