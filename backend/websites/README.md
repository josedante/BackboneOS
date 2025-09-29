# 🌐 Websites App - BackboneOS

## 📋 Overview

The `websites` app extends BackboneOS's interaction core to capture and organize interactions from websites. It provides:

- **Anonymous and authenticated web interaction tracking**
- **Automatic touchpoint resolution** with three-dimensional classification
- **Advanced traffic analysis** (UTM, referrer, user agent)
- **Multi-interaction approach** for comprehensive attribution
- **Integration** with organizational structure and CRM

## 🎯 Three-Dimensional Classification System

### **Channel (WHERE) - Where the interaction occurred**
- **Purpose**: Identifies the context/location where the interaction happened
- **Examples**: `esan.edu.pe`, `alpha.com`, `mobile_app`
- **Logic**: Determined from the website URL where the interaction occurred
- **Not**: Traffic source (that's the medium's responsibility)

### **Medium (HOW) - How it communicates**
- **Purpose**: Identifies the communication method
- **Examples**: `organic_search`, `social_media`, `cpc`, `email`, `referral`, `direct`
- **Logic**: UTM parameters take precedence, then referrer analysis, then defaults
- **Analysis**: Comprehensive referrer analysis with domain mapping

### **TouchpointType (WHAT) - What type of touchpoint**
- **Purpose**: Identifies the functional type of touchpoint (web-specific)
- **Examples**: `web_page`, `web_form`, `link`, `button`, `web_download`
- **Logic**: Determined from event type with intelligent click classification
- **No overlap**: Doesn't overlap with `interactions.Interaction.action` field

### **Example Classification:**
```
Interaction: "Contact form submission on ESAN"
- Channel: "esan.edu.pe" (WHERE: happened on ESAN's website)
- Medium: "organic_search" (HOW: arrived from organic search)
- TouchpointType: "web_form" (WHAT: web form submission)
```

## 🔄 Multi-Interaction Approach

For a single **Page View Event**, we create **up to 3 separate WebInteraction instances**:

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

## 🏗️ Core Models

### `Website`
Represents a website managed by the organization.
- **Fields**: `name`, `base_url`, `active`
- **Relationship**: Can be linked to one or more divisions
- **Usage**: Primary source for `WebSurface` entities

### `WebSurface`
Central entity describing a **URL-addressable surface** (page or form) on the website.
- **Key fields**: `path`, `exact_match`, `regex`, `title`, `product`
- **Relationship**: Has a `TouchpointType` and `Touchpoint` for integration
- **Properties**: `matches(path)` to verify URL matching
- **Flags**: `is_form`, `is_thankyou` for surface classification

### `WebInteraction`
Model extending `AbstractConnectorInteraction` and implementing `TouchpointInferenceProtocol`:
- **Browser fields**: `session_id`, `visitor_cookie`, `user_agent`, `client_hints`, `ip`
- **UTM attribution**: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- **Events**: `element`, `payload`, `is_bot`
- **Automatic resolution**: Implements `infer_touchpoint_hint()` and `_ensure_touchpoint()`
- **Integration**: Automatically connects with the touchpoint system

## 🔧 Touchpoint Resolution System

### **WebTouchpointResolver**
Specialized resolver extending the generic framework with web-specific logic:

- **Three-dimensional classification**: Implements Channel (WHERE), Medium (HOW), TouchpointType (WHAT)
- **UTM analysis**: Prioritizes UTM parameters for medium determination
- **Referrer analysis**: Detects organic, social, and referral traffic for medium
- **User agent analysis**: Identifies native app traffic and WebViews
- **Site-specific channels**: Uses website domain as channel code (WHERE)
- **Web-specific types**: TouchpointType based on web functionality (`web_page`, `web_form`, `link`, `button`)
- **Intelligent click classification**: Distinguishes between `link` and `button` based on selector

### **Resolution Flow**
1. `WebInteraction.save()` → `_ensure_touchpoint()` executes automatically
2. `infer_touchpoint_hint()` analyzes context and creates specialized hint
3. `WebTouchpointResolver.resolve()` applies rules and creates touchpoint with three-dimensional classification
4. Touchpoint automatically assigned to interaction with all three dimensions

## 📊 Channel Differentiation Strategy

### **Organic vs Paid Traffic Distinction**

| Traffic Type | UTM Source | Referrer | Final Channel | Use Case |
|--------------|------------|----------|---------------|----------|
| Organic Google | (empty) | `google.com/search` | `google.com` | Natural search results |
| Paid Google | `google` | `google.com/search` | `google` | Google Ads campaigns |
| Organic Facebook | (empty) | `facebook.com/post` | `facebook.com` | Organic social posts |
| Paid Facebook | `facebook` | `facebook.com/post` | `facebook` | Facebook Ads campaigns |

### **Benefits**
- **Clear Attribution**: Easy distinction between organic and paid performance
- **Marketing Analytics**: Better ROI analysis for paid campaigns
- **Reporting Granularity**: Separate tracking of organic vs paid performance

## 🧪 Testing Coverage

### **Test Suite**
- **28 tests passing**: Complete coverage of all functionality
- **Model tests**: Website, WebSurface, WebInteraction
- **Resolver tests**: WebTouchpointResolver with all scenarios
- **Adapter tests**: WebTouchpointAdapter with different event types
- **Integration tests**: Complete touchpoint resolution flow
- **Mapping provider tests**: WebMappingProvider and caching

### **Test Scenarios**
- **UTM analysis**: Different UTM parameter combinations
- **Referrer analysis**: Organic, social, referral traffic
- **User agent analysis**: Native apps, WebViews, browsers
- **Site-specific channels**: Different website domains
- **Semantic classification**: Different traffic mediums
- **Automatic resolution**: Automatic touchpoint creation

## 📁 File Structure

```
websites/
├── models.py              # Website, WebSurface, WebInteraction, UrlRoutingRule
├── resolvers.py           # WebTouchpointResolver and CachedWebTouchpointResolver
├── mapping_providers.py   # WebMappingProvider and CachedWebMappingProvider
├── adapters.py            # WebTouchpointAdapter (infer_web_touchpoint_hint)
├── processors.py          # Event processors with multi-interaction approach
├── admin.py               # Admin configuration
├── views.py               # ViewSets and API logic
├── urls.py                # API routes
├── tests/                 # Comprehensive test suite
│   ├── test_models.py
│   ├── test_resolvers.py
│   ├── test_adapters.py
│   ├── test_integration.py
│   └── test_three_dimensional_classification.py
├── README.md              # This documentation
├── MULTI_INTERACTION_APPROACH.md           # Multi-interaction approach details
├── THREE_DIMENSIONAL_CLASSIFICATION.md    # Technical implementation details
├── EVENT_DIFFERENTIATION_SUMMARY.md       # Event type differentiation
├── SERVER_SIDE_SESSION_INFERENCE.md       # Session inference logic
├── WEBSITE_EVENTS_CATALOG.md              # Complete events catalog
└── migrations/            # Database migrations
```

## 📚 Additional Documentation

### **Technical Implementation**
- **[THREE_DIMENSIONAL_CLASSIFICATION.md](./THREE_DIMENSIONAL_CLASSIFICATION.md)**: Detailed technical implementation of the three-dimensional classification system
- **[MULTI_INTERACTION_APPROACH.md](./MULTI_INTERACTION_APPROACH.md)**: Multi-interaction approach for page view events

### **Event Processing**
- **[EVENT_DIFFERENTIATION_SUMMARY.md](./EVENT_DIFFERENTIATION_SUMMARY.md)**: Event type differentiation and improvements
- **[SERVER_SIDE_SESSION_INFERENCE.md](./SERVER_SIDE_SESSION_INFERENCE.md)**: Server-side session inference logic
- **[WEBSITE_EVENTS_CATALOG.md](./WEBSITE_EVENTS_CATALOG.md)**: Complete catalog of website events and their effects

## 🎯 Value for BackboneOS

The `websites` app converts **anonymous web activity** into traceable interactions within the CRM, bridging the gap between **digital marketing** and **customer management**:

### **Key Benefits**
- **Automatic resolution**: Touchpoints created automatically without manual intervention
- **Advanced attribution**: UTM, referrer, and user agent analysis for better traffic understanding
- **Site-specific channels**: Each website has its own channel for granular analysis
- **Semantic classification**: TouchpointType based on web functionality for better categorization
- **Native app detection**: Identification of mobile app traffic vs. web browsers
- **Channel differentiation**: Distinction between capture channel vs. origin channel
- **Better customer journey**: Deeper understanding of customer journey

## 🔄 Recent Changes and Migration

### **Three-Dimensional Classification Update (January 2025)**

The `websites` app has been updated to implement the new three-dimensional classification system:

#### **Data Model Changes:**
- **Medium moved**: From `Channel` to `Touchpoint` for better separation of responsibilities
- **TouchpointClass → TouchpointType**: Renamed for clarity
- **Updated relationships**: Touchpoint now has `channel`, `medium`, and `touchpoint_type`

#### **Classification Logic Changes:**
- **Channel**: Now represents WHERE the interaction occurred (website), not traffic source
- **Medium**: Represents HOW it communicates (organic, social, paid, etc.)
- **TouchpointType**: Web-specific types that don't overlap with the `action` field

#### **Updated TouchpointType Examples:**
```python
# Before (overlapped with action)
'page_view', 'form_submit', 'click', 'download'

# Now (web-specific, no overlap)
'web_page', 'web_form', 'link', 'button', 'web_download'
```

#### **Automatic Migration:**
- Existing migrations have been updated
- System is compatible with existing data
- No manual intervention required

---

## 🚀 Getting Started

### **Basic Usage**
```python
# Create a WebInteraction
web_interaction = WebInteraction.objects.create(
    interaction=interaction,
    website=website,
    session_id="sess_123",
    visitor_cookie="visitor_456",
    user_agent="Mozilla/5.0...",
    utm_source="google",
    utm_medium="cpc",
    referrer_url="https://google.com/search?q=example",
    payload={"event_type": "page_view", "page_title": "Home Page"}
)

# Touchpoint is automatically resolved and assigned
print(web_interaction.touchpoint.channel.name)  # "google"
print(web_interaction.touchpoint.medium.name)   # "cpc"
print(web_interaction.touchpoint.touchpoint_type.name)  # "web_page"
```

### **API Endpoints**
- `POST /api/websites/interactions/` - Create web interaction
- `GET /api/websites/interactions/` - List web interactions
- `GET /api/websites/surfaces/` - List web surfaces
- `GET /api/websites/websites/` - List websites

---

👉 The `websites` app is the bridge between **web traffic** and BackboneOS's **CRM ecosystem**, now with advanced analysis capabilities and automatic touchpoint resolution.