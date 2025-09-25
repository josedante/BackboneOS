# 🔄 Multi-Interaction Approach - Page View Events

## 📋 Overview

For a single **Page View Event**, we create **up to 3 separate WebInteraction instances** (and thus 3 Interaction records) to capture different aspects of the user's journey and provide complete attribution tracking.

**✅ IMPLEMENTED**: This approach is fully functional in the current codebase.

---

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

---

## 🔧 Implementation

### **Current Implementation**:

The multi-interaction approach is implemented through:

1. **`PageViewEventProcessor`** class in `processors.py`
2. **`WebInteraction.process_page_view_event()`** class method in `models.py`
3. **Server-side session inference logic** for determining new sessions

### **Key Components**:

```python
# Usage: Process a page view event
interactions = WebInteraction.process_page_view_event(event_data)

# This creates up to 3 WebInteraction instances:
# 1. Page View Interaction (always)
# 2. Referrer Click Interaction (if external referrer)
# 3. Session Start Interaction (if new session)
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
   - **Action**: `no_action`
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

## ✅ Implementation Status

**FULLY IMPLEMENTED** - The multi-interaction approach is working in the current codebase:

- ✅ **PageViewEventProcessor**: Creates up to 3 interactions per page view
- ✅ **Session Inference**: Server-side logic for determining new sessions
- ✅ **Touchpoint Resolution**: Handles multiple touchpoints per event
- ✅ **Action Configuration**: Uses `no_action` and `external_click` actions
- ✅ **WebSession Integration**: Links interactions to session tracking

This multi-interaction approach provides granular tracking of every aspect of a user's page view, enabling comprehensive analytics and attribution analysis.
