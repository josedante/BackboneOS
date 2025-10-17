# Page View Event - Test Run Analysis

## Test Execution Summary

**Test URL:** http://localhost:4321/  
**Test Type:** Direct traffic, landing page (no referrer)  
**Result:** Successfully tracked with multi-interaction approach ✅

## What Was Created

### Database Objects Created

| Object Type | Count | Details |
|-------------|-------|---------|
| Websites | 1 | localhost:4321 |
| Channels | 2 | "direct" + "LOCALHOST:4321" |
| Mediums | 2 | "direct" + "web_interaction" |
| TouchpointTypes | 2 | "web_page" + "web_site_referral" |
| Touchpoints | 2 | Attribution touchpoint + Page touchpoint |
| Actions | 2 | "page_view" + "session_start" |
| Agents | 1 | Safari on macOS (browser) |
| Interactions | 2 | page_view + session_start |
| WebInteractions | 2 | One per interaction |
| WebSessions | 1 | Session tracking |

## Multi-Interaction Approach Explained

The system created **2 interactions** for this single page view because `is_landing_page=true`. This is the multi-interaction approach working correctly:

### Interaction #1: Session Start (Attribution)
```
Touchpoint: direct.direct.web_site_referral (Direct - Direct)
Action: session_start
Purpose: Captures WHERE the traffic came from (attribution)
```

**Taxonomy:**
- **Channel**: `direct` (no external referrer)
- **Medium**: `direct` (synchronous, direct traffic)
- **TouchpointType**: `web_site_referral` (traffic source context)

This interaction records that the session started from direct traffic (user typed URL or used bookmark).

### Interaction #2: Page View (Content)
```
Touchpoint: web_page (The Backbone Group - Deja de pelear con...)
Action: page_view
Purpose: Captures WHAT content was viewed
```

**Taxonomy:**
- **Channel**: `LOCALHOST:4321` (owned website)
- **Medium**: `web_interaction` (internal website interaction)
- **TouchpointType**: `web_page` (page content)

This interaction records the actual page that was viewed.

## Why This Design?

The multi-interaction approach separates **attribution** (where they came from) from **content** (what they did):

1. **Session Start** = Marketing analytics (traffic source, campaigns)
2. **Page View** = Content analytics (engagement, behavior)

This allows you to answer questions like:
- "How many sessions started from Google Ads?" → Query session_start interactions
- "What pages did users from Google Ads view?" → Join session_start + page_view
- "What's the conversion rate by traffic source?" → Group by session_start touchpoint

## Detailed Object Analysis

### Website Created
```
Name: localhost:4321
Base URL: http://localhost:4321
Channel: LOCALHOST:4321 (auto-created)
Division: Default Division
```

### Channels Created

#### 1. Direct Channel (Attribution)
```
Code: direct
Name: Direct
Source Type: owned
Purpose: Represents direct traffic (no referrer)
```

#### 2. Website Channel (Content)
```
Code: LOCALHOST:4321
Name: localhost:4321 Website
Source Type: owned
Purpose: Represents the owned website
```

### Mediums Created

#### 1. Direct Medium (Attribution)
```
Code: direct
Name: Direct
Communication Type: synchronous
Purpose: Direct traffic medium
```

#### 2. Web Interaction Medium (Content)
```
Code: web_interaction
Name: Web Interaction
Communication Type: synchronous
Purpose: Internal website interaction context
```

### TouchpointTypes Created

#### 1. Web Site Referral (Attribution)
```
Code: web_site_referral
Name: Web Site Referral
Purpose: Traffic source classification
```

#### 2. Web Page (Content)
```
Code: web_page
Name: Web Page
Purpose: Website page content
```

### Touchpoints Created

#### 1. Attribution Touchpoint
```
Code: direct.direct.web_site_referral
Name: Direct - Direct
URL: (empty - represents traffic source, not a URL)
Hierarchy: Channel (direct) → Medium (direct) → Type (web_site_referral)
Parent: None
```

#### 2. Page Touchpoint
```
Code: web_page
Name: The Backbone Group - Deja de pelear con la tecnología...
URL: http://localhost:4321/
Hierarchy: Channel (LOCALHOST:4321) → Medium (web_interaction) → Type (web_page)
Parent: None
```

### Actions Created

#### 1. Session Start
```
Code: session_start
Name: Session Start
Description: User started a new session
```

#### 2. Page View
```
Code: page_view
Name: Page View
Description: User viewed a page
```

### Agent Created
```
Type: browser
Name: Safari on macOS
Identifier: web_559824
User Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15...
```

### Interactions Created

#### 1. Session Start Interaction
```
ID: aa3c860c-2393-471d-86e8-031c6e033705
Touchpoint: direct.direct.web_site_referral
Action: session_start
Agent: Safari on macOS
Occurred: 2025-10-17 17:45:59.262630+00:00
Payload:
  - full_url: http://localhost:4321/
  - session_id: sess_68s608nfmw5
  - interaction_type: session_start
  - inferred: true
```

#### 2. Page View Interaction
```
ID: 03580425-c0a4-43a2-870b-94596cbaaf2a
Touchpoint: web_page
Action: page_view
Agent: Safari on macOS
Occurred: 2025-10-17 17:45:59.218814+00:00
Payload:
  - full_url: http://localhost:4321/
  - page_title: The Backbone Group - Deja de pelear con la tecnología...
  - page_category: other
  - is_landing_page: true
  - load_time: 6152ms
  - page_depth: 0
  - language: es-419
  - timezone: America/Lima
  - word_count: 719
  - viewport_size: 1656x1730
  - screen_resolution: 3360x1890
```

### WebInteractions Created

Both interactions have corresponding WebInteractions with:
- **Session ID**: sess_68s608nfmw5
- **Visitor Cookie**: visitor_xxj6wi736ab
- **User Agent**: Safari on macOS
- **Payload**: Rich page metadata

### WebSession Created

```
Session ID: sess_e4d6034e7e6d4c5e  ⚠️ MISMATCH!
Visitor Cookie: visitor_xxj6wi736ab
Page Count: 2
Is Bounce: False
Started At: 2025-10-17 17:45:59.234919+00:00
Last Activity At: 2025-10-17 17:45:59.266630+00:00
Landing Page URL: (to be checked)
UTM Source: (empty - direct traffic)
```

## Issue Detected: Session ID Mismatch ⚠️

**Problem:** The WebSession has a different session_id than the WebInteractions:
- **WebInteractions**: `sess_68s608nfmw5`
- **WebSession**: `sess_e4d6034e7e6d4c5e`

**Impact:** This breaks the relationship between WebInteractions and their WebSession. Queries like "get all interactions in this session" won't work correctly.

**Cause:** Likely in the `WebSession.infer_session_for_interaction()` method - it may be generating a new session_id instead of using the one from the WebInteraction.

**Recommended Fix:** Update `WebSession.infer_session_for_interaction()` to use the session_id from the WebInteraction.

## Validation Results

### Expected vs Actual

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Interaction count | 1-2 | 2 | ✅ Pass |
| Interactions types | page_view + session_start | page_view + session_start | ✅ Pass |
| Page view touchpoint | web_page | web_page | ✅ Pass |
| Attribution touchpoint | direct | direct | ✅ Pass |
| Channel (page) | owned, LOCALHOST:4321 | owned, LOCALHOST:4321 | ✅ Pass |
| Medium (page) | web_interaction | web_interaction | ✅ Pass |
| TouchpointType (page) | web_page | web_page | ✅ Pass |
| Session ID match | Should match | **Mismatch** | ❌ Fail |

## Recommendations

### 1. Fix Session ID Mismatch (High Priority)

The WebSession should use the same session_id as the WebInteractions. Check the `WebSession.infer_session_for_interaction()` method.

### 2. Consider Consolidating Direct Traffic Objects

Currently creates separate Channel/Medium for "direct" traffic. Could potentially reuse or merge these with the website's default taxonomy.

### 3. Update Documentation

The PAGE_VIEW_EVENT_FLOW.md should be updated to reflect that landing pages create:
- 1 session_start interaction (attribution)
- 1 page_view interaction (content)

## Overall Assessment

**Status:** ✅ **Mostly Successful**

The page view event was successfully tracked with the multi-interaction approach working as designed. The taxonomy (Channel → Medium → TouchpointType → Touchpoint) is properly created for both attribution and content interactions.

The only issue is the session ID mismatch between WebInteractions and WebSession, which should be fixed to maintain data integrity.

## Next Steps

1. **Fix the session ID mismatch** by updating the WebSession creation logic
2. **Re-run the test** to verify the fix
3. **Test additional scenarios**:
   - Page view with UTM parameters
   - Page view with external referrer
   - Multiple page views in same session
   - Non-landing page (should create only 1 interaction)

## Understanding Your Data

To query your data effectively:

### Get all interactions for a session:
```python
WebInteraction.objects.filter(session_id='sess_68s608nfmw5')
```

### Get attribution for a session:
```python
Interaction.objects.filter(
    action__code='session_start',
    webinteraction__session_id='sess_68s608nfmw5'
).first().touchpoint
```

### Get pages viewed in a session:
```python
Interaction.objects.filter(
    action__code='page_view',
    webinteraction__session_id='sess_68s608nfmw5'
)
```

### Analyze traffic sources:
```python
from django.db.models import Count
Interaction.objects.filter(
    action__code='session_start'
).values(
    'touchpoint__channel__code',
    'touchpoint__medium__code'
).annotate(count=Count('id'))
```

This structure enables powerful attribution and content analytics! 🚀

