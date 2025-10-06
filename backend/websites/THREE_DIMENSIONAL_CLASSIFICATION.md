# 🎯 Three-Dimensional Classification System - Technical Implementation (v2.0)

## 📋 Overview

This document provides technical implementation details for the three-dimensional classification system used in the `websites` app with **v2.0 subject-agnostic architecture**. For general usage information, see the main [README.md](./README.md).

## 🏗️ System Architecture

### **Data Model Structure**

```python
# interactions/models.py - Touchpoint model
class Touchpoint(BaseUUIDModelWithActiveStatus):
    # Three-dimensional classification
    channel = models.ForeignKey(Channel, ...)      # WHERE
    medium = models.ForeignKey(Medium, ...)        # HOW  
    touchpoint_type = models.ForeignKey(TouchpointType, ...)  # WHAT
    
    # Hierarchical structure
    parent = models.ForeignKey('self', ...)  # For rollup analytics
```

### **Classification Dimensions**

#### **1. Channel (WHERE) - Where the interaction occurred**
- **Purpose**: Identifies the traffic source or website location
- **Examples**: `esan.edu.pe` (owned), `google` (external), `facebook` (external)
- **Logic**: For internal interactions, website domain; for attribution, UTM source or referrer domain
- **Implementation**: Pre-created in `build_touchpoint_hint_from_event_data()` hint builder

#### **2. Medium (HOW) - How it communicates**
- **Purpose**: Identifies the communication/traffic method
- **Examples**: `organic_search`, `cpc`, `social_media`, `email`, `referral`, `direct`, `web_interaction`
- **Logic**: For attribution, UTM medium or referrer analysis; for internal, `web_interaction`
- **Implementation**: Analyzed in `_parse_utm_for_attribution()` and `_analyze_referrer_medium()`

#### **3. TouchpointType (WHAT) - What type of touchpoint**
- **Purpose**: Identifies the functional type of touchpoint (web-specific)
- **Examples**: `web_page`, `web_form`, `web_button`, `web_video`, `web_search_referral`
- **Logic**: Determined from event type mapping with context-aware selection
- **Implementation**: Mapped in `build_touchpoint_hint_from_event_data()` with `touchpoint_type_map`

## 🔧 v2.0 Implementation Details

### **TouchpointHint Building - Two Modes**

The system builds hints differently based on interaction type:

#### **Mode 1: Internal Interactions** (page_view, page_read, clicks, forms)
```python
# For events that happen ON the website
hint = TouchpointHint(
    code="web_page",  # or touchpoint_type_code for events
    url=full_url,  # The page URL
    channel_code=website_channel,  # Owned website channel
    medium_code="web_interaction",  # Internal interaction medium
    touchpoint_type_code="web_page",  # Event-specific type
    label=page_title,
    metadata={...}
)
```

#### **Mode 2: Attribution Tracking** (referrer, session)
```python
# For tracking WHERE visitors came FROM
hint = TouchpointHint(
    code=composite_code,  # e.g., "google.organic_search.web_search_referral"
    url=referrer_url,  # The external source URL
    parent_code=parent_code,  # For rollup analytics
    channel_code=utm_source or referrer_domain,  # External source
    medium_code=utm_medium or analyzed_medium,  # Traffic method
    touchpoint_type_code="web_search_referral",  # Referral type
    label=f"{channel_name} - {campaign_name}",
    metadata={...}
)
```

### **Channel Determination - v2.0 Approach**

Channel determination happens BEFORE touchpoint resolution in the hint builder:

```python
@classmethod
def build_touchpoint_hint_from_event_data(cls, event_data: dict, website, hint_type: str = 'internal'):
    """
    Build TouchpointHint from raw event data.
    
    hint_type:
        - 'internal': For page views/events ON the website
        - 'referrer': For attribution tracking (WHERE visitor came FROM)
        - 'session': For session start tracking (uses same attribution logic as referrer)
    """
    
    if hint_type in ('referrer', 'session'):
        # ATTRIBUTION MODE: Track external traffic source
        utm_parsed = cls._parse_utm_for_attribution(event_data, referrer, ...)
        channel_code = utm_parsed['channel_code']  # From UTM source or referrer domain
    else:
        # INTERNAL MODE: Track website activity
        channel_code = website.channel.code  # Owned website channel
```

### **Medium Determination - v2.0 Approach**

Medium is analyzed from UTM parameters or referrer domain:

```python
@classmethod
def _analyze_referrer_medium(cls, referrer: str, target_url: str = '') -> str:
    """
    Analyze referrer URL to determine traffic medium.
    Returns: 'cpc', 'organic_search', 'social_media', 'email', 'referral', 'direct'
    """
    
    # Check for paid traffic indicators (gclid, fbclid, utm_medium=cpc)
    if any(param in target_url_lower for param in ['gclid=', 'fbclid=', 'msclkid=']):
        return 'cpc'
    
    # Search engines → organic_search
    if any(engine in referrer_lower for engine in ['google.', 'bing.', 'yahoo.']):
        return 'organic_search'
    
    # Social platforms → social_media
    if any(social in referrer_lower for social in ['facebook.', 'linkedin.', 'twitter.']):
        return 'social_media'
    
    # Email indicators → email
    if any(indicator in referrer_lower for indicator in ['mail.google', 'outlook.', 'mailchimp']):
        return 'email'
    
    # Default → referral
    return 'referral'
```

### **TouchpointType Determination - v2.0 Approach**

TouchpointType is mapped from event type with context awareness:

```python
# For INTERNAL interactions (hint_type='internal')
touchpoint_type_map = {
    'page_view': 'web_page',
    'page_read': 'web_page',
    'form_submit': 'web_form',
    'click': 'web_button',
    'download': 'web_file',
    'video_play': 'web_video',
    'search': 'web_search',
    'newsletter_signup': 'web_signup',
}
touchpoint_type_code = touchpoint_type_map.get(event_type, 'web_page')

# For ATTRIBUTION interactions (hint_type='referrer'/'session')
# Determined by _resolve_referrer_touchpoint_type() based on medium and context
tp_info = cls._resolve_referrer_touchpoint_type(medium_code, website, referrer)
# Returns: 'web_search_referral', 'web_social_referral', 'web_email_referral', etc.
```

## 📊 Classification Examples (v2.0)

### **Example 1: Page View from Organic Google Search**

**Input Event:**
```json
{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://google.com/search?q=mba+programs+peru",
    "utm_source": "",  # No UTM parameters
    "utm_medium": "",
    "payload": {
        "is_landing_page": true,
        "page_title": "MBA Programs"
    }
}
```

**Output: 3 Interactions with 3 Different Touchpoints:**

1. **Page View Interaction** (internal):
   - Touchpoint Code: `web_page`
   - Channel: `esan.edu.pe` (owned website)
   - Medium: `web_interaction` (internal)
   - TouchpointType: `web_page`

2. **Referrer Click Interaction** (attribution):
   - Touchpoint Code: `google.organic_search.web_search_referral`
   - Channel: `google` (referrer domain)
   - Medium: `organic_search` (analyzed from referrer)
   - TouchpointType: `web_search_referral`

3. **Session Start Interaction** (attribution):
   - Touchpoint Code: `google.organic_search.web_search_referral`
   - Channel: `google` (same as referrer)
   - Medium: `organic_search`
   - TouchpointType: `web_search_referral`

---

### **Example 2: Paid Google Campaign with UTM**

**Input Event:**
```json
{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://google.com/search?q=mba",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "summer_mba_2025",
    "payload": {
        "is_landing_page": true,
        "page_title": "MBA Programs"
    }
}
```

**Output: 3 Interactions:**

1. **Page View** (internal):
   - Channel: `esan.edu.pe`
   - Medium: `web_interaction`
   - TouchpointType: `web_page`

2. **Referrer Click** (attribution with UTM):
   - Channel: `google` (from UTM source)
   - Medium: `cpc` (from UTM medium)
   - TouchpointType: `web_search_referral`
   - Parent Code: `google.cpc` (rollup)
   - Child Code: `google.cpc.web_search_referral.summer_mba_2025`

3. **Session Start** (attribution):
   - Same classification as referrer click

---

### **Example 3: Internal Navigation (No Referrer)**

**Input Event:**
```json
{
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/about",
    "referrer": "https://esan.edu.pe/programs/mba",  # Internal referrer
    "payload": {
        "is_landing_page": false,
        "page_title": "About Us"
    }
}
```

**Output: 1 Interaction Only:**

1. **Page View** (internal):
   - Channel: `esan.edu.pe`
   - Medium: `web_interaction`
   - TouchpointType: `web_page`
   
*Note: No referrer click (same website) and no session start (not landing page)*

---

### **Example 4: Form Submission Event**

**Input Event:**
```json
{
    "event_type": "form_submit",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/contact",
    "payload": {
        "form_id": "contact-form",
        "form_type": "contact"
    }
}
```

**Output: 1 Interaction:**

1. **Form Submit** (internal):
   - Touchpoint Code: `web_form` (event-specific)
   - Channel: `esan.edu.pe`
   - Medium: `web_interaction`
   - TouchpointType: `web_form`
   - Parent Code: `web_page` (form is on a page)

## 🏗️ Hierarchical Touchpoint Structure

The v2.0 system supports parent-child touchpoint relationships for rollup analytics:

### **Parent Touchpoints** (for campaign rollup)
```python
# Example: Google CPC campaign rollup
Parent Touchpoint:
    code: "google.cpc"
    url: ""  # No URL for rollup touchpoints
    channel: google
    medium: cpc
    touchpoint_type: web_search_referral
    parent: None
```

### **Child Touchpoints** (for granular tracking)
```python
# Example: Specific campaign creative
Child Touchpoint:
    code: "google.cpc.web_search_referral.summer_mba_2025"
    url: "https://google.com/search..."
    channel: google
    medium: cpc
    touchpoint_type: web_search_referral
    parent: [Parent Touchpoint]  # Links to parent for rollup
```

This enables:
- **Campaign-level analytics**: Roll up all interactions by parent
- **Creative-level analytics**: Track specific ad performance by child
- **Flexible reporting**: Query at any hierarchy level

## 🧪 v2.0 Testing

### **Test Coverage**
- ✅ **All event processors**: 8/8 processors tested
- ✅ **Pre-creation resolution**: Touchpoint resolved before Interaction
- ✅ **Hint building**: Internal vs. attribution modes
- ✅ **UTM parsing**: Campaign parameter handling
- ✅ **Referrer analysis**: Medium detection from domains
- ✅ **Hierarchical structure**: Parent-child touchpoint creation
- ✅ **Multi-interaction**: Page view creates 1-3 interactions

### **Key Test Scenarios**
- **v2.0 flow**: Complete event → hint → resolution → interaction
- **Attribution tracking**: UTM precedence over referrer analysis
- **Internal tracking**: Website activity without attribution
- **Hierarchical touchpoints**: Parent-child relationships
- **Edge cases**: Missing data, invalid URLs, bot detection

## 🎯 v2.0 Benefits

### **Architectural Benefits**
- **Pre-Creation Resolution**: Touchpoints resolved before database save
- **Subject-Agnostic**: No object passing, explicit parameters only
- **Testable**: Direct dict input, no mock objects needed
- **Explicit Data Flow**: All classification logic visible in hint builder
- **23% Code Reduction**: Removed 453 lines of v1.0 code

### **Analytical Benefits**
- **Dual-Mode Classification**: Internal activity + external attribution
- **Hierarchical Analytics**: Campaign rollup + creative granularity
- **Multi-Interaction Support**: Comprehensive page view attribution
- **Flexible Reporting**: Group by any dimension or hierarchy level
- **Clear Separation**: Internal touchpoints vs. attribution touchpoints

### **Business Benefits**
- **Complete Attribution**: WHERE visitors came FROM (referrer) + what they DID (page view)
- **Campaign ROI**: Track campaigns with rollup analytics
- **Traffic Analysis**: Organic vs. paid, search vs. social, etc.
- **Journey Mapping**: Session start + page views + conversions
- **Scalability**: Easy to add new event types and attribution sources

---

## 📚 Related Documentation

- **[README.md](./README.md)**: General overview and getting started
- **[MULTI_INTERACTION_APPROACH.md](./MULTI_INTERACTION_APPROACH.md)**: Multi-interaction details
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)**: Implementation status
- **[WEBSITE_EVENTS_CATALOG.md](./WEBSITE_EVENTS_CATALOG.md)**: Complete events catalog

---

This v2.0 three-dimensional classification system provides a robust foundation for web interaction analysis with pre-creation resolution, hierarchical structure, and dual-mode classification for internal activity tracking and external attribution analysis.