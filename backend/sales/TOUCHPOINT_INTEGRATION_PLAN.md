# Sales App Touchpoint Integration Plan

## Overview

This document outlines the implementation plan for integrating the sales app with the Touchpoint Resolution System, taking into account the organizational structure where each division has its own sales team represented by an `interactions.Channel`.

## Current State Analysis

### Channel Structure
- **Division-based Sales Channels**: Each division has a dedicated sales channel following the pattern `"Ventas - {division_name}"`
- **Channel-Touchpoint Relationship**: Channels are now related to Touchpoints, not directly to Interactions
- **Existing Function**: `get_sales_channel_for_division()` already handles channel lookup by division name

### Current Sales Models
1. **SalesOpportunity**: Standalone model with channel field but no touchpoint integration
2. **SalesSession**: Inherits from Interaction, uses manual touchpoint creation
3. **ProductAcquisition**: Inherits from Interaction, uses manual touchpoint creation

## Implementation Plan

### Phase 1: Protocol Implementation

#### 1.1 SalesSession TouchpointInferenceProtocol
- Implement `infer_touchpoint_hint()` method
- Map contact mediums to standardized codes
- Include opportunity and representative context in metadata

#### 1.2 SalesOpportunity Touchpoint Integration
- Add touchpoint resolution to opportunity lifecycle events
- Create touchpoints for opportunity creation, stage changes, and closure
- Link opportunities to division-specific sales channels

### Phase 2: Mapping Rules Configuration

#### 2.1 Default Sales Touchpoint Mappings
- Create mapping rules for different sales contact mediums
- Configure division-specific touchpoint codes
- Set up funnel stage mappings for sales activities

#### 2.2 Channel Management
- Ensure division-specific sales channels exist
- Create channel creation utility functions
- Update channel lookup logic

### Phase 3: Testing and Validation

#### 3.1 Unit Tests
- Test touchpoint inference for all contact mediums
- Test opportunity touchpoint creation
- Test channel resolution by division

#### 3.2 Integration Tests
- Test end-to-end sales session touchpoint resolution
- Test opportunity lifecycle touchpoint creation
- Test cross-division channel handling

### Phase 4: Documentation and Migration

#### 4.1 Documentation Updates
- Update sales app README with touchpoint integration
- Document new touchpoint codes and mappings
- Create usage examples

#### 4.2 Migration Strategy
- Gradual migration from manual to automatic touchpoint creation
- Backward compatibility during transition
- Data migration for existing sales sessions

## Technical Implementation Details

### Touchpoint Codes Structure
```
sales.session.{medium}           # Sales session by medium
sales.opportunity.{stage}        # Opportunity stage changes
sales.acquisition.{product_type} # Product acquisitions
```

### Channel Codes Structure
```
sales.{division_code}            # Division-specific sales channels
```

### Channel Resolution Priority

The sales app follows a specific priority order for determining the sales channel:

1. **Representative's Division** (Highest Priority)
   - The division that the sales representative works for
   - **Human Representatives**: Determined from representative's position/unit/team in organizational structure
   - **AI Agent Representatives**: Determined from agent metadata, represented organization, or operated by person's division
   - Channel code: `sales_{representative_division_code}`

2. **Product's Division** (Fallback)
   - The division associated with the product being sold
   - Determined from product -> category -> division relationship
   - Channel code: `sales_{product_division_code}`

3. **Default Sales Channel** (Lowest Priority)
   - Generic sales channel when no division can be determined
   - Channel code: `sales`

### AI Agent Support

The sales touchpoint system fully supports AI agents as sales representatives:

- **AI Agent Types**: The system recognizes `Agent` instances with `agent_type='ai'` as valid representatives
- **Division Assignment**: AI agents can be assigned to divisions through:
  - Metadata configuration (`division_code` in agent metadata)
  - Represented organization's division structure
  - Represented person's division (if agent represents a person)
  - Operated by person's division (if agent is operated by a person)
- **Touchpoint Metadata**: AI agent interactions include additional metadata:
  - `representative_type`: "ai_agent"
  - `agent_type`: The agent type (e.g., "ai")
  - `agent_name`: The agent's name
  - `agent_metadata`: The agent's configuration metadata

### Metadata Structure
```json
{
  "opportunity_id": "uuid",
  "representative_id": "uuid", 
  "division": "division_name",
  "product_id": "uuid",
  "stage": "opportunity_stage",
  "outcome": "session_outcome"
}
```

## Implementation Steps

### Step 1: Create App-Specific Resolver and Mapping Provider ✅
- [x] Create SalesTouchpointResolver extending DefaultTouchpointResolver
- [x] Create SalesMappingProvider with sales-specific business logic
- [x] Implement division-specific channel resolution
- [x] Add sales-specific touchpoint creation logic

### Step 2: Implement SalesSession Protocol ✅
- [x] Add TouchpointInferenceProtocol import
- [x] Implement infer_touchpoint_hint() method
- [x] Update save() method to use sales-specific resolver
- [x] Test with different contact mediums

### Step 3: Implement SalesOpportunity Touchpoints
- [ ] Add touchpoint resolution to opportunity lifecycle
- [ ] Create opportunity touchpoint creation methods
- [ ] Test opportunity stage change touchpoints

### Step 4: Create Mapping Rules
- [ ] Define default mapping rules for sales touchpoints
- [ ] Create division-specific channel mappings
- [ ] Test mapping rule resolution

### Step 5: Write Comprehensive Tests
- [ ] Unit tests for all new methods
- [ ] Integration tests for touchpoint resolution
- [ ] Test edge cases and error handling

### Step 6: Update Documentation
- [x] Create app-specific resolver pattern documentation
- [ ] Update sales app README
- [ ] Document new touchpoint codes
- [ ] Create usage examples

## Success Criteria

1. **Functional**: All sales interactions create appropriate touchpoints
2. **Performance**: Touchpoint resolution completes within acceptable time limits
3. **Accuracy**: Touchpoints correctly reflect sales context and division
4. **Maintainability**: Code is well-documented and testable
5. **Compatibility**: Existing functionality remains intact

## Risk Mitigation

1. **Backward Compatibility**: Maintain existing manual touchpoint creation as fallback
2. **Performance**: Use caching for frequently accessed channels and touchpoints
3. **Data Integrity**: Validate touchpoint creation and handle errors gracefully
4. **Testing**: Comprehensive test coverage before production deployment

## Timeline

- **Week 1**: Protocol implementation and basic testing
- **Week 2**: Mapping rules and channel management
- **Week 3**: Comprehensive testing and validation
- **Week 4**: Documentation and migration preparation

## Dependencies

- Touchpoint Resolution System (connectors app)
- Interactions app models
- Our Institution app (for division structure)
- Products app (for product relationships)
