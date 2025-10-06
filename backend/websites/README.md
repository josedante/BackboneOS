# 🌐 Websites App - BackboneOS

## 📋 Overview

The `websites` app extends BackboneOS's interaction core to capture and organize interactions from websites using a **modernized v2.0 architecture**. It provides:

- **Anonymous and authenticated web interaction tracking**
- **Subject-agnostic touchpoint resolution** with pre-creation pattern
- **Advanced traffic analysis** (UTM, referrer, user agent with ua-parser)
- **Multi-interaction approach** for comprehensive attribution
- **Integration** with organizational structure and CRM

## 🎯 Three-Dimensional Classification System

### **Channel (WHERE) - Where the interaction occurred**
- **Purpose**: Identifies the context/location where the interaction happened
- **Examples**: `test.com`, `example.org`, `mywebsite.com`
- **Logic**: Determined from the website domain (normalized)
- **Source Type**: Automatically set to `'owned'` for websites

### **Medium (HOW) - How it communicates**
- **Purpose**: Identifies the communication method
- **Examples**: `organic`, `cpc`, `social`, `email`, `referral`, `direct`
- **Logic**: UTM parameters take precedence, then referrer analysis, then defaults
- **Analysis**: Comprehensive referrer analysis with domain mapping

### **TouchpointType (WHAT) - What type of touchpoint**
- **Purpose**: Identifies the functional type of touchpoint (web-specific)
- **Examples**: `web_page`, `web_form`, `web_button`, `web_download`, `web_video`
- **Logic**: Determined from event type mapping
- **No overlap**: Doesn't overlap with `interactions.Interaction.action` field

### **Example Classification:**
```python
# Event: "Contact form submission on example.com from Google Ads"
Channel: "example.com" (WHERE: happened on example.com website)
Medium: "cpc" (HOW: arrived from paid search - utm_medium=cpc)
TouchpointType: "web_form" (WHAT: web form submission)
```

## 🔄 Multi-Interaction Approach

For a single **Page View Event**, we create **up to 3 separate WebInteraction instances**:

### **1. Page View Interaction** (Always Created)
- **Purpose**: Track the page being viewed on our website
- **Action**: `page_view`
- **Touchpoint**: Viewed page touchpoint
- **Created**: Always, for every page view

### **2. Referrer Click Interaction** (Conditional)
- **Purpose**: Track the click that brought the visitor to our site
- **Action**: `referrer_click`
- **Touchpoint**: Referrer page touchpoint
- **Created**: Only if external referrer exists and differs from website

### **3. Session Start Interaction** (Conditional)
- **Purpose**: Track the beginning of a new session
- **Action**: `session_start`
- **Touchpoint**: Session start touchpoint
- **Created**: Only if `is_landing_page=True`

## 🏗️ Core Models

### `Website`
Represents a website managed by the organization.
- **Fields**: `name`, `base_url`, `channel`, `division`, `active`
- **Auto-Channel Creation**: Automatically creates/updates `Channel` with `source_type='owned'` on save
- **Relationship**: Linked to Division for organizational structure
- **Usage**: Primary source for web interaction tracking

### `WebInteraction`
Model extending `AbstractConnectorInteraction` with **v2.0 architecture**:
- **Browser fields**: `session_id`, `visitor_cookie`, `user_agent`, `client_hints`, `ip`
- **UTM attribution**: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- **Events**: `element`, `payload`, `is_bot`
- **v2.0 Resolution**: Uses pre-creation touchpoint resolution (no post-save hooks)
- **Event Processors**: 8 static event processors using canonical v2.0 pattern

### `WebAgent`
Represents browser/device information parsed from user agent.
- **Fields**: `user_agent`, `browser_family`, `browser_version`, `os_family`, `os_version`, `device_family`, `is_mobile`, `is_tablet`, `is_pc`, `is_bot`
- **ua-parser Integration**: Uses `ua-parser-js` for accurate parsing and bot detection
- **Auto-Creation**: Automatically created from user agent strings

### `WebSession`
Represents a web session - a continuous period of user activity.
- **Simple session logic**: Session continues if within 30 minutes, otherwise new session
- **Session tracking**: Session identity, timing, and attribution
- **Analytics**: Page count, bounce detection, conversion events
- **Integration**: Links to Website and Agent models

## 🔧 v2.0 Touchpoint Resolution System

### **Subject-Agnostic Architecture**

The websites app uses the **modernized v2.0 resolution pattern**:

```python
# ✅ v2.0 Pattern (Current)
# Step 1: Build hint from raw event data
hint = WebInteraction.build_touchpoint_hint_from_event_data(event_data, website)

# Step 2: Resolve touchpoint BEFORE creating interaction
resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
touchpoint = resolver.resolve(
    hint,
    connector_type='web',
    source_identifier=cls._extract_domain(website.base_url)
)

# Step 3: Create Interaction + WebInteraction with touchpoint already assigned
interaction = Interaction.objects.create(
    touchpoint=touchpoint,  # Already resolved!
    action=action,
    agent=agent
)
web_interaction = WebInteraction.objects.create(
    interaction=interaction,
    website=website,
    ...
)
```

### **Event Processing Flow**

All 8 event processors follow the canonical `process_click_event` pattern:

1. **Get/Create Website** - From `event_data['website_base']`
2. **Build TouchpointHint** - From raw `event_data` dict (static method)
3. **Resolve Touchpoint** - Pre-creation, with explicit parameters
4. **Get/Create Agent** - From user agent string (with ua-parser)
5. **Get/Create Action** - Event-specific action code
6. **Create Atomically** - Interaction + WebInteraction together

### **Available Event Processors**

| Event Type | Processor Method | Action Code | TouchpointType |
|------------|------------------|-------------|----------------|
| Page View | `process_page_view_event()` | `page_view` | `web_page` |
| Page Read | `process_page_read_event()` | `page_read` | `web_page` |
| Click | `process_click_event()` | `click` | `web_button` |
| Form Submit | `process_form_submit_event()` | `form_submit` | `web_form` |
| Download | `process_download_event()` | `download` | `web_download` |
| Video Play | `process_video_play_event()` | `video_play` | `web_video` |
| Search | `process_search_event()` | `search` | `web_search` |
| Newsletter Signup | `process_newsletter_signup_event()` | `newsletter_signup` | `web_signup` |

## 🧪 Testing Coverage

### **Test Suite**
- **Model tests**: Website, WebInteraction, WebAgent, WebSession
- **Integration tests**: Complete v2.0 touchpoint resolution flow
- **Event processing tests**: Multi-interaction approach validation
- **Mapping rule tests**: Custom touchpoint code application

### **Test Scenarios**
- ✅ UTM analysis: Different UTM parameter combinations
- ✅ Referrer analysis: Organic, social, referral traffic
- ✅ User agent parsing: Browser, OS, device detection with ua-parser
- ✅ Bot detection: Accurate bot identification
- ✅ Domain normalization: Source identifier extraction
- ✅ Pre-creation resolution: Touchpoint resolved before Interaction
- ✅ Mapping rules: Custom touchpoint codes applied correctly
- ✅ Multi-interaction: Page view creates 1-3 interactions

## 📁 File Structure

```
websites/
├── models.py              # Website, WebInteraction, WebAgent, WebSession (v2.0)
├── admin.py               # Admin configuration
├── views.py               # Event view endpoints (individual per event type)
├── urls.py                # API routes (individual event endpoints)
├── tests/                 # Test suite
├── static/
│   └── websites/
│       └── js/
│           ├── backbone-tracker.js      # Client-side tracker (no batching)
│           └── backbone-config.js       # Tracker configuration
├── management/
│   └── commands/
│       └── ensure_website_channels.py   # Channel management command
├── README.md              # This documentation (v2.0 updated)
├── PAGE_VIEW_EVENT_FLOW.md            # ★ Complete flow explanation (NEW)
├── IMPLEMENTATION_SUMMARY.md           # Implementation status
├── MULTI_INTERACTION_APPROACH.md       # Multi-interaction details
├── THREE_DIMENSIONAL_CLASSIFICATION.md # Classification system (v2.0 updated)
├── EVENT_DIFFERENTIATION_SUMMARY.md    # Event differentiation
├── WEBSITE_EVENTS_CATALOG.md          # Complete events catalog
├── TRACKING_SCRIPT_DOCUMENTATION.md   # Client-side tracking docs
├── TESTING_GAPS.md        # ★ Testing coverage analysis & improvement plan (NEW)
└── migrations/            # Database migrations
```

## 📚 Additional Documentation

### **Architecture & Implementation**
- **[PAGE_VIEW_EVENT_FLOW.md](./PAGE_VIEW_EVENT_FLOW.md)**: **★ COMPREHENSIVE GUIDE** - Complete step-by-step flow explanation
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)**: Current implementation status
- **[THREE_DIMENSIONAL_CLASSIFICATION.md](./THREE_DIMENSIONAL_CLASSIFICATION.md)**: Technical implementation of classification system
- **[MULTI_INTERACTION_APPROACH.md](./MULTI_INTERACTION_APPROACH.md)**: Multi-interaction approach for page views

### **Event Processing**
- **[WEBSITE_EVENTS_CATALOG.md](./WEBSITE_EVENTS_CATALOG.md)**: Complete catalog of website events
- **[EVENT_DIFFERENTIATION_SUMMARY.md](./EVENT_DIFFERENTIATION_SUMMARY.md)**: Event type differentiation

### **Testing & Quality**
- **[TESTING_GAPS.md](./TESTING_GAPS.md)**: **★ COVERAGE ANALYSIS** - Comprehensive testing gaps analysis and improvement plan
- **[TRACKING_SCRIPT_DOCUMENTATION.md](./TRACKING_SCRIPT_DOCUMENTATION.md)**: Client-side tracking implementation

## 🚀 Getting Started

### **Processing Events (v2.0 API)**

```python
from websites.models import WebInteraction
from django.utils import timezone

# Event data from client (JavaScript tracker)
event_data = {
    'event_type': 'click',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/products',
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'utm_campaign': 'summer_sale',
    'referrer': 'https://google.com/search',
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'session_id': 'sess_abc123',
    'visitor_cookie': 'visitor_xyz789',
    'ip_address': '192.168.1.1',
    'occurred_at': timezone.now(),
    'payload': {
        'clicked_element': 'button',
        'element_id': 'buy-now',
        'text_content': 'Buy Now'
    }
}

# Process event using v2.0 API (returns list of created interactions)
interactions = WebInteraction.process_click_event(event_data)

# Access the created interaction
web_interaction = interactions[0]
print(web_interaction.interaction.touchpoint.code)  # 'web.click'
print(web_interaction.interaction.touchpoint.channel.code)  # 'example.com'
print(web_interaction.interaction.touchpoint.medium.code)  # 'cpc'
print(web_interaction.interaction.touchpoint.touchpoint_type.code)  # 'web_button'
```

### **Multi-Interaction Page View**

```python
# Page view can create 1-3 interactions
event_data = {
    'event_type': 'page_view',
    'website_base': 'https://example.com',
    'full_url': 'https://example.com/landing',
    'referrer': 'https://google.com/search',
    'utm_source': 'google',
    'utm_medium': 'organic',
    'user_agent': 'Mozilla/5.0...',
    'session_id': 'new_session',
    'occurred_at': timezone.now(),
    'payload': {
        'is_landing_page': True,
        'page_title': 'Welcome to Example'
    }
}

# Creates 3 interactions: page_view + referrer_click + session_start
interactions = WebInteraction.process_page_view_event(event_data)
print(f"Created {len(interactions)} interactions")  # "Created 3 interactions"
```

### **API Endpoints**

```
# Event Processing Endpoints (Individual per event type)
POST /api/websites/events/page-view/
POST /api/websites/events/page-read/
POST /api/websites/events/click/
POST /api/websites/events/form-submit/
POST /api/websites/events/download/
POST /api/websites/events/video-play/
POST /api/websites/events/search/
POST /api/websites/events/newsletter-signup/

# Data Access Endpoints
GET /api/websites/interactions/    # List web interactions
GET /api/websites/websites/         # List websites
```

## 🎯 Value for BackboneOS

The `websites` app converts **anonymous web activity** into traceable interactions within the CRM:

### **Key Benefits**
- ✅ **Subject-Agnostic Resolution**: Clean, testable touchpoint resolution
- ✅ **Pre-Creation Pattern**: Touchpoints resolved before database save
- ✅ **Accurate User Agent Parsing**: ua-parser for browser/OS/device detection
- ✅ **Bot Detection**: Automatic bot identification
- ✅ **Advanced Attribution**: UTM, referrer analysis for traffic understanding
- ✅ **Auto-Channel Creation**: Websites automatically create owned channels
- ✅ **Multi-Interaction Support**: Comprehensive page view attribution
- ✅ **Domain Normalization**: Consistent source identifier handling
- ✅ **Mapping Rules Support**: Custom touchpoint codes via database rules

## 🔄 Recent Changes - v2.0 Migration (January 2025)

### **Architecture Modernization**

The websites app has been **completely migrated to v2.0 architecture**:

#### **✅ Completed Changes:**
- **Removed v1.0 code**: 453 lines of obsolete protocol implementations removed (23% code reduction)
- **Pre-creation resolution**: All 8 event processors use pre-creation touchpoint resolution
- **Subject-agnostic API**: All resolver calls use explicit parameters, no object passing
- **Static hint building**: `build_touchpoint_hint_from_event_data()` from raw event data
- **Atomic creation**: `_create_web_interaction_with_interaction()` helper method
- **ua-parser integration**: Accurate user agent parsing and bot detection
- **Domain normalization**: `source_identifier` uses extracted domain for mapping rules
- **No post-save hooks**: `WebInteraction.save()` no longer auto-resolves touchpoints

#### **Removed v1.0 Components:**
- ❌ `infer_touchpoint_hint()` - Subject-dependent inference
- ❌ `infer_multi_touchpoint_hints()` - Multi-interaction protocol
- ❌ `_ensure_touchpoint()` - Post-creation resolution
- ❌ 12+ instance-based helper methods
- ❌ Old multi-interaction helper methods

#### **v2.0 Benefits:**
- 🎯 **23% smaller codebase**: Cleaner, more maintainable code
- 🎯 **Faster**: 2 database saves instead of 3+ per interaction
- 🎯 **Testable**: Direct dict input, no mock objects needed
- 🎯 **Explicit**: All data flow is visible and traceable
- 🎯 **Scalable**: Easy to add new event types following template pattern

---

👉 The `websites` app is the bridge between **web traffic** and BackboneOS's **CRM ecosystem**, now with a **modernized v2.0 architecture** for clean, fast, and maintainable event processing.
