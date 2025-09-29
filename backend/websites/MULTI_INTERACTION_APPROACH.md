# 🔄 Multi-Interaction Approach - Page View Events

## 📋 Overview

For a single **Page View Event**, we create **up to 3 separate WebInteraction instances** (and thus 3 Interaction records) to capture different aspects of the user's journey and provide complete attribution tracking.

**✅ IMPLEMENTED**: This approach is fully functional in the current codebase.

## 🎯 Three Interaction Types

### **1. Page View Interaction**
- **Purpose**: Track the page being viewed on our website
- **Action**: `no_action`
- **Touchpoint**: Viewed page touchpoint
- **Always Created**: Yes, for every page view

### **2. Referrer Click Interaction**
- **Purpose**: Track the click that brought the visitor to our site
- **Action**: `external_click`
- **Touchpoint**: Referrer page touchpoint
- **Conditionally Created**: Only if external referrer exists

### **3. Session Start Interaction**
- **Purpose**: Track the beginning of a new session
- **Action**: `no_action`
- **Touchpoint**: Viewed page touchpoint (as landing page)
- **Conditionally Created**: Only if new session criteria are met

## 🏗️ Implementation Architecture

### **PageViewEventProcessor**
The `PageViewEventProcessor` class implements the multi-interaction approach:

```python
class PageViewEventProcessor(BaseWebEventProcessor):
    def process_page_view_event(self, event_data: dict) -> list:
        """
        Process a page view event and create up to 3 interactions:
        1. Page View Interaction
        2. Referrer Click Interaction (if external referrer exists)
        3. Session Start Interaction (if new session)
        """
        interactions = []
        
        # 1. Always create Page View Interaction
        page_view_interaction = self._create_page_view_interaction(event_data)
        interactions.append(page_view_interaction)
        
        # 2. Create Referrer Click Interaction if external referrer exists
        if self._has_external_referrer(event_data):
            referrer_interaction = self._create_referrer_click_interaction(event_data)
            interactions.append(referrer_interaction)
        
        # 3. Create Session Start Interaction if new session
        if self._is_new_session(event_data):
            session_interaction = self._create_session_start_interaction(event_data)
            interactions.append(session_interaction)
        
        return interactions
```

### **Business Logic**

#### **Page View Interaction**
- **Always created** for every page view event
- **Touchpoint**: The page being viewed
- **Channel**: Website domain where interaction occurred
- **Medium**: Determined from UTM parameters or referrer analysis
- **TouchpointType**: `web_page`

#### **Referrer Click Interaction**
- **Conditionally created** only if external referrer exists
- **Touchpoint**: The referrer page (e.g., Google search results)
- **Channel**: Referrer domain (e.g., `google.com`)
- **Medium**: Determined from referrer analysis (e.g., `organic_search`)
- **TouchpointType**: `search_results` for search engines, `web_page` for others

#### **Session Start Interaction**
- **Conditionally created** only if new session criteria are met
- **Touchpoint**: The landing page (same as page view)
- **Channel**: Website domain where interaction occurred
- **Medium**: Same as page view interaction
- **TouchpointType**: `web_page`

## 📊 Example Scenarios

### **Scenario 1: New Visitor from Google Search**
```python
# Input Event
{
    "event_type": "page_view",
    "website_url": "https://esan.edu.pe/programs/mba",
    "referrer_url": "https://google.com/search?q=mba+programs+peru",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789"
}

# Expected Output: 3 Interactions Created
[
    {
        "type": "Page View Interaction",
        "action": "no_action",
        "touchpoint": "web_page.mba_programs_esan_university",
        "channel": "esan.edu.pe",
        "medium": "owned_website",
        "touchpoint_type": "web_page"
    },
    {
        "type": "Referrer Click Interaction", 
        "action": "external_click",
        "touchpoint": "web.referrer_page.google_search",
        "channel": "google.com",
        "medium": "organic_search",
        "touchpoint_type": "search_results"
    },
    {
        "type": "Session Start Interaction",
        "action": "no_action", 
        "touchpoint": "web_page.mba_programs_esan_university",
        "channel": "esan.edu.pe",
        "medium": "owned_website",
        "touchpoint_type": "web_page"
    }
]
```

### **Scenario 2: Paid Google Campaign**
```python
# Input Event
{
    "event_type": "page_view",
    "website_url": "https://esan.edu.pe/programs/mba",
    "referrer_url": "https://google.com/search?q=mba+programs+peru",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "mba_search"
}

# Expected Output: 3 Interactions Created
[
    {
        "type": "Page View Interaction",
        "action": "no_action",
        "touchpoint": "web_page.mba_programs_esan_university",
        "channel": "google",  # UTM source takes precedence
        "medium": "cpc",      # UTM medium takes precedence
        "touchpoint_type": "web_page"
    },
    {
        "type": "Referrer Click Interaction",
        "action": "external_click", 
        "touchpoint": "web.referrer_page.google_search",
        "channel": "google",  # UTM source takes precedence
        "medium": "cpc",      # UTM medium takes precedence
        "touchpoint_type": "search_results"
    },
    {
        "type": "Session Start Interaction",
        "action": "no_action",
        "touchpoint": "web_page.mba_programs_esan_university", 
        "channel": "google",  # UTM source takes precedence
        "medium": "cpc",      # UTM medium takes precedence
        "touchpoint_type": "web_page"
    }
]
```

## 🎯 Benefits

### **Complete Attribution Tracking**
- **Page View**: Tracks what page was viewed
- **Referrer Click**: Tracks how the visitor arrived
- **Session Start**: Tracks the beginning of new sessions

### **Marketing Analytics**
- **Traffic Source Analysis**: Clear understanding of how visitors arrive
- **Session Tracking**: Better understanding of user behavior
- **Attribution**: Complete attribution chain from source to conversion

### **Customer Journey**
- **Complete Journey**: Full picture of user's path to conversion
- **Touchpoint Analysis**: Understanding of all touchpoints in the journey
- **Behavioral Insights**: Better understanding of user behavior patterns

## 🔧 Technical Implementation

### **Event Processing Flow**
1. **Event Received**: Page view event arrives at the processor
2. **Analysis**: Processor analyzes event data for referrer and session information
3. **Interaction Creation**: Up to 3 interactions are created based on analysis
4. **Touchpoint Resolution**: Each interaction gets its touchpoint resolved automatically
5. **Storage**: All interactions are stored in the database

### **Conditional Logic**
- **Referrer Click**: Only created if external referrer exists
- **Session Start**: Only created if new session criteria are met
- **Page View**: Always created for every page view event

### **Performance Considerations**
- **Efficient Processing**: Minimal overhead for conditional interaction creation
- **Database Optimization**: Efficient storage and retrieval of multiple interactions
- **Caching**: Touchpoint resolution is cached for performance

## 🧪 Testing

### **Test Coverage**
- **Multi-interaction creation**: Tests for all three interaction types
- **Conditional logic**: Tests for referrer and session conditions
- **Touchpoint resolution**: Tests for automatic touchpoint assignment
- **Edge cases**: Tests for various event scenarios

### **Test Scenarios**
- **New visitor**: All three interactions created
- **Returning visitor**: Only page view interaction created
- **No referrer**: Only page view and session start interactions
- **UTM parameters**: UTM precedence over referrer analysis

---

This multi-interaction approach provides comprehensive attribution tracking while maintaining performance and scalability.