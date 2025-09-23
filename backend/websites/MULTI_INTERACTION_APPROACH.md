# 🔄 Multi-Interaction Approach - Page View Events

## 📋 Overview

For a single **Page View Event**, we create **up to 3 separate WebInteraction instances** (and thus 3 Interaction records) to capture different aspects of the user's journey and provide complete attribution tracking.

---

## 🎯 Three Interaction Types

### **1. Page View Interaction**
- **Purpose**: Track the page being viewed on our website
- **Action**: `no_action` or `page_view`
- **Touchpoint**: Viewed page touchpoint
- **Always Created**: Yes, for every page view

### **2. Referrer Click Interaction**
- **Purpose**: Track the click that brought the visitor to our site
- **Action**: `click` or `external_click`
- **Touchpoint**: Referrer page touchpoint
- **Conditionally Created**: Only if external referrer exists

### **3. Session Start Interaction**
- **Purpose**: Track the beginning of a new session
- **Action**: `no_action` or `session_start`
- **Touchpoint**: Viewed page touchpoint (as landing page)
- **Conditionally Created**: Only if new session criteria are met

---

## 🔧 Implementation Logic

### **Server-Side Processing**:

```python
def process_page_view_event(web_interaction_data):
    """Process a page view event and create up to 3 interactions"""
    
    interactions_created = []
    
    # 1. Always create Page View Interaction
    page_view_interaction = create_page_view_interaction(web_interaction_data)
    interactions_created.append(page_view_interaction)
    
    # 2. Create Referrer Click Interaction (if external referrer exists)
    if has_external_referrer(web_interaction_data):
        referrer_click_interaction = create_referrer_click_interaction(web_interaction_data)
        interactions_created.append(referrer_click_interaction)
    
    # 3. Create Session Start Interaction (if new session criteria met)
    if should_start_new_session(web_interaction_data):
        session_start_interaction = create_session_start_interaction(web_interaction_data)
        interactions_created.append(session_start_interaction)
    
    return interactions_created

def create_page_view_interaction(web_interaction_data):
    """Create interaction for the page being viewed"""
    
    # Get or create viewed page touchpoint
    viewed_page_touchpoint = get_or_create_viewed_page_touchpoint(web_interaction_data)
    
    # Get or create action
    action = Action.objects.get_or_create(
        code='no_action',
        defaults={'name': 'Sin Acción', 'description': 'Evento inferido o acción realizada hacia el usuario'}
    )[0]
    
    # Create interaction
    interaction = Interaction.objects.create(
        action=action,
        touchpoint=viewed_page_touchpoint,
        agent=get_or_create_agent(web_interaction_data),
        occurred_at=web_interaction_data['created_at'],
        payload={
            'interaction_type': 'page_view',
            'page_title': web_interaction_data['payload']['page_title'],
            'page_description': web_interaction_data['payload']['page_description']
        }
    )
    
    # Create WebInteraction record
    WebInteraction.objects.create(
        interaction=interaction,
        website=web_interaction_data['website'],
        session_id=web_interaction_data['session_id'],
        visitor_cookie=web_interaction_data['visitor_cookie'],
        user_agent=web_interaction_data['user_agent'],
        utm_source=web_interaction_data['utm_source'],
        utm_medium=web_interaction_data['utm_medium'],
        utm_campaign=web_interaction_data['utm_campaign'],
        payload=web_interaction_data['payload']
    )
    
    return interaction

def create_referrer_click_interaction(web_interaction_data):
    """Create interaction for the referrer click"""
    
    # Get or create referrer page touchpoint
    referrer_page_touchpoint = get_or_create_referrer_page_touchpoint(web_interaction_data)
    
    # Get or create action
    action = Action.objects.get_or_create(
        code='external_click',
        defaults={'name': 'External Click', 'description': 'Click from external source'}
    )[0]
    
    # Create interaction
    interaction = Interaction.objects.create(
        action=action,
        touchpoint=referrer_page_touchpoint,
        agent=get_or_create_agent(web_interaction_data),
        occurred_at=web_interaction_data['created_at'],
        payload={
            'interaction_type': 'referrer_click',
            'referrer_url': web_interaction_data['referrer_url'],
            'referrer_title': web_interaction_data['payload'].get('referrer_title'),
            'referrer_description': web_interaction_data['payload'].get('referrer_description')
        }
    )
    
    # Create WebInteraction record
    WebInteraction.objects.create(
        interaction=interaction,
        website=web_interaction_data['website'],
        session_id=web_interaction_data['session_id'],
        visitor_cookie=web_interaction_data['visitor_cookie'],
        user_agent=web_interaction_data['user_agent'],
        utm_source=web_interaction_data['utm_source'],
        utm_medium=web_interaction_data['utm_medium'],
        utm_campaign=web_interaction_data['utm_campaign'],
        payload=web_interaction_data['payload']
    )
    
    return interaction

def create_session_start_interaction(web_interaction_data):
    """Create interaction for session start"""
    
    # Use the same viewed page touchpoint as landing page
    viewed_page_touchpoint = get_or_create_viewed_page_touchpoint(web_interaction_data)
    
    # Get or create action
    action = Action.objects.get_or_create(
        code='no_action',
        defaults={'name': 'Sin Acción', 'description': 'Evento inferido o acción realizada hacia el usuario'}
    )[0]
    
    # Create interaction
    interaction = Interaction.objects.create(
        action=action,
        touchpoint=viewed_page_touchpoint,
        agent=get_or_create_agent(web_interaction_data),
        occurred_at=web_interaction_data['created_at'],
        payload={
            'interaction_type': 'session_start',
            'session_start_time': web_interaction_data['created_at'].isoformat(),
            'is_new_visitor': is_new_visitor(web_interaction_data),
            'landing_page': True,
            'inference_reason': get_session_start_reason(web_interaction_data)
        }
    )
    
    # Create WebInteraction record
    WebInteraction.objects.create(
        interaction=interaction,
        website=web_interaction_data['website'],
        session_id=web_interaction_data['session_id'],
        visitor_cookie=web_interaction_data['visitor_cookie'],
        user_agent=web_interaction_data['user_agent'],
        utm_source=web_interaction_data['utm_source'],
        utm_medium=web_interaction_data['utm_medium'],
        utm_campaign=web_interaction_data['utm_campaign'],
        payload=web_interaction_data['payload']
    )
    
    return interaction
```

---

## 📊 Example Scenarios

### **Scenario 1: New Visitor with External Referrer**

**Page View Event**: New visitor comes from Google search to `/programs/mba`

**3 Interactions Created**:

1. **Page View Interaction**:
   - **Action**: `no_action`
   - **Touchpoint**: `web.page_view.mba_programs_esan_university`
   - **Purpose**: Track page being viewed

2. **Referrer Click Interaction**:
   - **Action**: `external_click`
   - **Touchpoint**: `web.referrer_page.google_search`
   - **Purpose**: Track click from Google

3. **Session Start Interaction**:
   - **Action**: `session_start`
   - **Touchpoint**: `web.page_view.mba_programs_esan_university` (landing page)
   - **Purpose**: Track new session beginning

### **Scenario 2: Returning Visitor with External Referrer**

**Page View Event**: Returning visitor comes from Facebook to `/contact`

**2 Interactions Created**:

1. **Page View Interaction**:
   - **Action**: `no_action`
   - **Touchpoint**: `web.page_view.contact_us`
   - **Purpose**: Track page being viewed

2. **Referrer Click Interaction**:
   - **Action**: `external_click`
   - **Touchpoint**: `web.referrer_page.facebook_post`
   - **Purpose**: Track click from Facebook

3. **Session Start Interaction**: Not created (not a new session)

### **Scenario 3: Direct Traffic (No Referrer)**

**Page View Event**: User types URL directly to `/`

**1-2 Interactions Created**:

1. **Page View Interaction**:
   - **Action**: `no_action`
   - **Touchpoint**: `web.page_view.homepage`
   - **Purpose**: Track page being viewed

2. **Referrer Click Interaction**: Not created (no external referrer)

3. **Session Start Interaction**: Created if new session criteria met

---

## 🎯 Business Benefits

### **Complete Attribution**:
- **Source Tracking**: Know exactly where visitors came from
- **Page Performance**: Track which pages are most viewed
- **Session Analysis**: Understand session boundaries and patterns

### **Detailed Analytics**:
- **Referrer Performance**: Which external sources drive most traffic
- **Landing Page Analysis**: Which pages are most common entry points
- **User Journey Mapping**: Complete path from source to destination

### **Marketing Intelligence**:
- **Campaign Attribution**: Link external clicks to internal page views
- **Conversion Tracking**: Track complete user journey
- **ROI Analysis**: Measure effectiveness of different traffic sources

---

## 🔧 Database Schema Considerations

### **WebInteraction Model**:
```python
class WebInteraction(AbstractConnectorInteraction):
    # ... existing fields ...
    
    # Add field to track interaction type
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ('page_view', 'Page View'),
            ('referrer_click', 'Referrer Click'),
            ('session_start', 'Session Start'),
        ],
        default='page_view'
    )
    
    # Add field to link related interactions
    related_interactions = models.ManyToManyField(
        'self',
        blank=True,
        help_text="Other interactions created from the same page view event"
    )
```

### **Interaction Model**:
```python
class Interaction(BaseUUIDModelWithActiveStatus):
    # ... existing fields ...
    
    # Add field to track interaction sequence
    interaction_sequence = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Sequence number for interactions from same event"
    )
```

---

## 🚀 Implementation Checklist

- [ ] **Update Models**: Add interaction_type and related_interactions fields
- [ ] **Implement Multi-Interaction Logic**: Create up to 3 interactions per page view
- [ ] **Configure Actions**: Set up no_action, external_click, session_start actions
- [ ] **Update Touchpoint Resolution**: Handle multiple touchpoints per event
- [ ] **Test Scenarios**: Verify all 3 interaction types are created correctly
- [ ] **Update Analytics**: Modify reporting to handle multiple interactions
- [ ] **Performance Optimization**: Ensure efficient creation of multiple records
- [ ] **Data Validation**: Verify data integrity across related interactions

This multi-interaction approach provides granular tracking of every aspect of a user's page view, enabling comprehensive analytics and attribution analysis.
