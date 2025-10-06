# 🌊 Page View Event Flow - Complete Step-by-Step Guide

## 📋 Overview

This document provides a **complete, detailed explanation** of how a `page_view` event flows through the BackboneOS system, from client-side capture to database storage. This is the definitive technical reference for understanding the entire event processing pipeline.

---

## 🎯 Quick Summary

1. **Client-Side Capture** (JavaScript) → Collects event data
2. **HTTP Transmission** → POSTs JSON to backend
3. **View Reception** (Django) → Validates and delegates
4. **Multi-Interaction Processing** → Creates 1-3 interactions
5. **Touchpoint Resolution** → Pre-creation taxonomy building
6. **Database Storage** → Atomic interaction + web_interaction creation

**Result**: A single page view event creates up to **3 separate interactions** with complete attribution tracking.

---

## Phase 1: Client-Side Capture (JavaScript Tracker)

### Location
`backend/websites/static/websites/js/backbone-tracker.min.js`

### Step 1.1: Page Load Detection
```javascript
// Tracker initializes when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();  // Page already loaded
}
```

### Step 1.2: Session & Visitor Management
```javascript
function initializeSession() {
    const existingSession = getCookie('backbone_session_id');
    const lastActivity = getCookie('backbone_last_activity');
    const now = Date.now();
    
    // New session if:
    // - No existing session
    // - 30+ minutes inactive
    // - Cross-domain referrer
    // - UTM parameters changed
    if (!existingSession || (now - parseInt(lastActivity)) > 30*60*1000 
        || hasCrossDomainReferrer() || hasUTMChange()) {
        sessionId = generateSessionId();  // 'sess_' + random16chars
        setCookie('backbone_session_id', sessionId, 24*60*60*1000);
    }
}

function initializeVisitor() {
    visitorCookie = getCookie('backbone_visitor_id');
    if (!visitorCookie) {
        visitorCookie = generateVisitorId();  // 'visitor_' + random16chars
        setCookie('backbone_visitor_id', visitorCookie, 365*24*60*60*1000);
    }
}
```

### Step 1.3: Event Data Collection
```javascript
function trackPageView() {
    pageStartTime = Date.now();
    
    const eventData = {
        // Core identification
        event_type: 'page_view',
        website_base: window.location.origin,  // 'https://example.com'
        full_url: window.location.href,        // Full page URL
        referrer: document.referrer,           // Where visitor came from
        
        // Session tracking
        session_id: sessionId,                 // 'sess_abc123...'
        visitor_cookie: visitorCookie,         // 'visitor_xyz789...'
        
        // Device/browser
        user_agent: navigator.userAgent,       // Full UA string
        
        // Marketing attribution (UTM parameters)
        utm_source: getUrlParam('utm_source'),
        utm_medium: getUrlParam('utm_medium'),
        utm_campaign: getUrlParam('utm_campaign'),
        utm_content: getUrlParam('utm_content'),
        utm_term: getUrlParam('utm_term'),
        
        // Page context
        element: 'body',
        
        // Rich payload
        payload: {
            page_title: document.title,
            page_description: getMetaContent('description'),
            page_category: getPageCategory(),          // blog, products, etc.
            load_time: Math.round(performance.now()),  // Page load time in ms
            is_landing_page: isLandingPage(),          // true if no same-domain referrer
            page_depth: getPageDepth(),                // URL path depth
            word_count: getWordCount(),                // Text content word count
            viewport_size: getViewportSize(),          // '1920x1080'
            screen_resolution: getScreenResolution(),  // '2560x1440'
            language: navigator.language,              // 'en-US'
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        }
    };
    
    sendEvent(eventData);
}
```

### Step 1.4: Event Transmission
```javascript
function sendEventToAPI(eventData, attempt = 1) {
    fetch(CONFIG.apiEndpoint, {  // '/api/websites/events/page-view/'
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(eventData)
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('Event sent successfully:', data);
    })
    .catch(error => {
        // Retry logic: up to 3 attempts
        if (attempt < CONFIG.retryAttempts) {
            setTimeout(() => {
                sendEventToAPI(eventData, attempt + 1);
            }, CONFIG.retryDelay * attempt);
        }
    });
}
```

---

## Phase 2: Server-Side Reception (Django View)

### Location
`backend/websites/views.py` → `PageViewEventView`

### Step 2.1: HTTP Request Handling
```python
@method_decorator(csrf_exempt, name='dispatch')  # CSRF exempt for cross-domain tracking
class PageViewEventView(View):
    def post(self, request):
        # Entry point for all page view events
```

### Step 2.2: Request Validation
```python
try:
    # Parse JSON body
    data = json.loads(request.body)
    
    # Validate required fields
    required_fields = ['event_type', 'website_base', 'full_url']
    for field in required_fields:
        if field not in data:
            return JsonResponse({
                'error': f'Missing required field: {field}'
            }, status=400)
    
    # Validate event type
    if data.get('event_type') != 'page_view':
        return JsonResponse({
            'error': 'Only page_view events are supported by this endpoint'
        }, status=400)
```

### Step 2.3: Error Handling Strategy
```python
except json.JSONDecodeError as e:
    # CLIENT ERROR: Invalid JSON
    sentry_sdk.capture_message(
        f"Invalid JSON in page_view event",
        level='warning',
        extras={'raw_body': request.body[:500].decode('utf-8', errors='ignore')}
    )
    return JsonResponse({'error': 'Invalid JSON data'}, status=400)

except ValueError as e:
    # CLIENT ERROR: Invalid data
    sentry_sdk.capture_message(
        f"Invalid data in page_view event: {str(e)}",
        level='warning',
        extras={'event_data': data, 'error': str(e)}
    )
    return JsonResponse({'error': 'Invalid data', 'message': str(e)}, status=400)

except Exception as e:
    # SERVER ERROR: Processing failure
    error_trace = traceback.format_exc()
    
    # Log to Sentry with context
    with sentry_sdk.push_scope() as scope:
        scope.set_tag('connector_type', 'web')
        scope.set_tag('event_type', 'page_view')
        scope.set_tag('has_fallback', 'true')
        scope.set_context('event_data', {
            'full_url': data.get('full_url'),
            'website_base': data.get('website_base')
        })
        sentry_sdk.capture_exception(e)
    
    # Store in fallback queue for retry
    failed_event = store_failed_event(
        connector_type='web',
        event_type='page_view',
        raw_payload=data,
        error_message=str(e),
        error_trace=error_trace,
        source_identifier=data.get('website_base', '')
    )
    
    return JsonResponse({
        'success': False,
        'error': 'Event processing failed but has been queued for retry',
        'fallback_id': str(failed_event.pk),
        'message': 'Your event will be processed automatically'
    }, status=202)  # 202 Accepted - will process later
```

### Step 2.4: Delegation to Processing Logic
```python
# Process the page view event (creates 1-3 interactions)
created_interactions = WebInteraction.process_page_view_event(data)

# Prepare success response
response_data = {
    'success': True,
    'message': f'Successfully processed page view event',
    'interactions_created': len(created_interactions),  # 1-3
    'interaction_ids': [str(interaction.pk) for interaction in created_interactions]
}

logger.info(f"Processed page view: {data.get('full_url')} - Created {len(created_interactions)} interactions")

return JsonResponse(response_data, status=201)  # 201 Created
```

---

## Phase 3: Multi-Interaction Processing

### Location
`backend/websites/models.py` → `WebInteraction.process_page_view_event()`

This is where the magic happens - **one event becomes 1-3 interactions**.

### Step 3.1: Initialization
```python
@classmethod
def process_page_view_event(cls, event_data: dict) -> list:
    """
    Process a page view event and create up to 3 interactions.
    
    CRITICAL: Page view interaction MUST succeed.
    OPTIONAL: Referrer and session interactions fail gracefully.
    """
    from interactions.models import Action
    from connectors.resolvers import DefaultTouchpointResolver
    from connectors.mapping_providers import DatabaseMappingProvider
    
    logger = logging.getLogger(__name__)
    
    # Get or create Website entity
    website_base = event_data.get('website_base')
    if not website_base:
        raise ValueError("website_base is required")
    
    website, _ = Website.objects.get_or_create(
        base_url=website_base,
        defaults={
            'name': cls._extract_domain(website_base),  # 'example.com'
            'division': cls._get_default_division(),
            'active': True
        }
    )
    # Website auto-creates its Channel on save (source_type='owned')
    
    # Initialize touchpoint resolver
    resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
    
    # Get or create Agent (browser)
    agent = cls._get_or_create_agent(event_data.get('user_agent', ''))
    
    interactions = []  # Will hold 1-3 interactions
```

### Step 3.2: INTERACTION 1 - Page View (CRITICAL)
```python
# ═══════════════════════════════════════════════════════════════
# INTERACTION 1: Page View (CRITICAL - must succeed)
# ═══════════════════════════════════════════════════════════════
try:
    with transaction.atomic():
        # BUILD HINT (internal mode)
        hint_page_view = cls.build_touchpoint_hint_from_event_data(
            event_data, 
            website,
            hint_type='internal'  # Internal website activity
        )
        # Returns TouchpointHint with:
        #   code = "web_page"
        #   url = full_url
        #   channel_code = website.channel.code  (e.g., "example.com")
        #   medium_code = "web_interaction"
        #   touchpoint_type_code = "web_page"
        #   label = page_title
        
        # RESOLVE TOUCHPOINT (pre-creation)
        touchpoint_page_view = resolver.resolve(
            hint_page_view,
            connector_type='web',
            source_identifier=cls._extract_domain(website.base_url)
        )
        # Creates/gets:
        #   - Channel (owned website)
        #   - Medium (web_interaction)
        #   - TouchpointType (web_page)
        #   - Touchpoint (with all three dimensions)
        
        # GET/CREATE ACTION
        action_page_view, _ = Action.objects.get_or_create(
            code='page_view',
            defaults={
                'name': 'Page View',
                'description': 'User viewed a page',
                'action_type': None  # No action type for inferred events
            }
        )
        
        # CREATE INTERACTION + WEBINTERACTION (atomic)
        page_view_interaction = cls._create_web_interaction_with_interaction(
            event_data=event_data,
            agent=agent,
            action=action_page_view,
            touchpoint=touchpoint_page_view,  # Already resolved!
            interaction_payload={
                'interaction_type': 'page_view',
                'full_url': event_data.get('full_url', ''),
                'referrer': event_data.get('referrer', ''),
                'page_title': event_data.get('payload', {}).get('page_title', ''),
                'page_category': event_data.get('payload', {}).get('page_category', ''),
                'load_time': event_data.get('payload', {}).get('load_time'),
                'is_landing_page': event_data.get('payload', {}).get('is_landing_page', False),
                'page_depth': event_data.get('payload', {}).get('page_depth', 1)
            },
            website=website
        )
        
        interactions.append(page_view_interaction)
        logger.debug(f"Created page view interaction for {event_data.get('full_url')}")

except Exception as e:
    # Page view is CRITICAL - re-raise to fail entire request
    logger.error(
        f"CRITICAL: Failed to create page view interaction for {event_data.get('full_url', 'unknown')}: {str(e)}",
        exc_info=True
    )
    raise  # This will trigger fallback queue storage
```

### Step 3.3: INTERACTION 2 - Referrer Click (OPTIONAL)
```python
# ═══════════════════════════════════════════════════════════════
# INTERACTION 2: Referrer Click (OPTIONAL - fails gracefully)
# ═══════════════════════════════════════════════════════════════
referrer = event_data.get('referrer', '')
if referrer and referrer != website_base:
    try:
        with transaction.atomic():
            # BUILD HINT (attribution mode)
            hint_referrer = cls.build_touchpoint_hint_from_event_data(
                event_data, 
                website, 
                hint_type='referrer'  # Attribution tracking
            )
            # Returns TouchpointHint with:
            #   code = "google.organic_search.web_search_referral" (composite)
            #   url = referrer
            #   parent_code = "google.organic_search" (rollup)
            #   channel_code = "google" (from UTM or referrer domain)
            #   medium_code = "organic_search" (from UTM or analysis)
            #   touchpoint_type_code = "web_search_referral"
            #   label = "Google - MBA Programs" (channel + campaign)
            
            # RESOLVE TOUCHPOINT (creates parent + child)
            touchpoint_referrer = resolver.resolve(
                hint_referrer,
                connector_type='web',
                source_identifier=cls._extract_domain(website.base_url)
            )
            
            # GET/CREATE ACTION
            action_referrer, _ = Action.objects.get_or_create(
                code='referrer_click',
                defaults={
                    'name': 'Referrer Click',
                    'description': 'Inferred click on external referrer',
                    'action_type': None  # Inferred action
                }
            )
            
            # CREATE INTERACTION
            referrer_interaction = cls._create_web_interaction_with_interaction(
                event_data=event_data,
                agent=agent,
                action=action_referrer,
                touchpoint=touchpoint_referrer,
                interaction_payload={
                    'interaction_type': 'referrer_click',
                    'full_url': referrer,
                    'referrer': referrer,
                    'inferred': True
                },
                website=website
            )
            
            interactions.append(referrer_interaction)
            logger.debug(f"Created referrer interaction from {referrer}")
    
    except Exception as e:
        # Referrer interaction is OPTIONAL - log warning but continue
        logger.warning(
            f"Failed to create referrer interaction from {referrer}: {str(e)}. "
            f"Continuing with page view only.",
            exc_info=True
        )
        # DO NOT raise - page view already succeeded
```

### Step 3.4: INTERACTION 3 - Session Start (OPTIONAL)
```python
# ═══════════════════════════════════════════════════════════════
# INTERACTION 3: Session Start (OPTIONAL - fails gracefully)
# ═══════════════════════════════════════════════════════════════
is_landing_page = event_data.get('payload', {}).get('is_landing_page', False)
if is_landing_page:
    try:
        with transaction.atomic():
            # BUILD HINT (attribution mode - same as referrer)
            hint_session = cls.build_touchpoint_hint_from_event_data(
                event_data, 
                website, 
                hint_type='session'  # Uses same attribution logic
            )
            
            # RESOLVE TOUCHPOINT
            touchpoint_session = resolver.resolve(
                hint_session,
                connector_type='web',
                source_identifier=cls._extract_domain(website.base_url)
            )
            
            # GET/CREATE ACTION
            action_session, _ = Action.objects.get_or_create(
                code='session_start',
                defaults={
                    'name': 'Session Start',
                    'description': 'User started a new session',
                    'action_type': None  # System action
                }
            )
            
            # CREATE INTERACTION
            session_interaction = cls._create_web_interaction_with_interaction(
                event_data=event_data,
                agent=agent,
                action=action_session,
                touchpoint=touchpoint_session,
                interaction_payload={
                    'interaction_type': 'session_start',
                    'full_url': event_data.get('full_url', ''),
                    'session_id': event_data.get('session_id', ''),
                    'inferred': True
                },
                website=website
            )
            
            interactions.append(session_interaction)
            logger.debug(f"Created session start interaction for session {event_data.get('session_id')}")
    
    except Exception as e:
        # Session interaction is OPTIONAL - log warning but continue
        logger.warning(
            f"Failed to create session start interaction: {str(e)}. "
            f"Continuing without session tracking.",
            exc_info=True
        )

# Return all successfully created interactions (1-3)
return interactions
```

---

## Phase 4: Touchpoint Resolution Deep Dive

### Location
`backend/connectors/resolvers.py` → `DefaultTouchpointResolver.resolve()`

### Step 4.1: Resolution Entry Point
```python
@transaction.atomic
def resolve(
    self,
    hint: TouchpointHint,
    *,
    connector_type: str,  # 'web'
    source_identifier: str = ''  # 'example.com'
) -> Touchpoint:
    """
    Resolve touchpoint from hint with explicit parameters.
    
    This is the core taxonomy engine that creates:
    - Channel
    - Medium
    - TouchpointType
    - Touchpoint (with hierarchical parent if specified)
    """
    with track_resolution(connector_type, {'hint_code': hint.code}) as tracker:
        try:
            # Step 1: Check for mapping rule overrides
            mapping_rule = self.mapping_provider.lookup_mapping(
                connector_type=connector_type,
                source_identifier=source_identifier,
                hint=hint
            )
            
            if mapping_rule:
                hint = self._apply_mapping_rule(hint, mapping_rule)
            
            # Step 2: Create or get touchpoint
            touchpoint = self._get_or_create_touchpoint(hint)
            
            tracker.record_success(
                cache_hit=False,
                mapping_applied=bool(mapping_rule),
                touchpoint_created=True
            )
            
            return touchpoint
        
        except Exception as e:
            tracker.record_error(str(e))
            raise
```

### Step 4.2: Create Taxonomy Hierarchy
```python
def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
    """
    Create the full touchpoint taxonomy.
    
    Order:
    1. Channel
    2. Medium
    3. TouchpointType
    4. Parent Touchpoint (if specified)
    5. Child Touchpoint
    """
    
    # 1. GET/CREATE CHANNEL
    channel = None
    if hint.channel_code:
        channel, _ = Channel.objects.get_or_create(
            code=hint.channel_code,  # e.g., "google" or "example.com"
            defaults={
                'name': self._format_code_as_name(hint.channel_code),  # "Google"
                'description': f"Auto-generated channel for {hint.channel_code}",
                'source_type': 'external'  # or 'owned' for websites
            }
        )
    
    # 2. GET/CREATE MEDIUM
    medium = None
    if hint.medium_code:
        medium, _ = Medium.objects.get_or_create(
            code=hint.medium_code,  # e.g., "organic_search" or "web_interaction"
            defaults={
                'name': self._format_code_as_name(hint.medium_code),  # "Organic Search"
                'description': f"Auto-generated medium for {hint.medium_code}",
                'communication_type': 'asynchronous'
            }
        )
    
    # 3. GET/CREATE TOUCHPOINT TYPE
    touchpoint_type = None
    if hint.touchpoint_type_code:
        touchpoint_type, _ = TouchpointType.objects.get_or_create(
            code=hint.touchpoint_type_code,  # e.g., "web_page" or "web_search_referral"
            defaults={
                'name': self._format_code_as_name(hint.touchpoint_type_code),  # "Web Page"
                'description': f"Auto-generated touchpoint type for {hint.touchpoint_type_code}"
            }
        )
    
    # 4. CREATE PARENT TOUCHPOINT (if specified)
    parent_touchpoint = None
    if hint.parent_code:
        # Determine parent URL and name based on hint type
        if hint.parent_code == "web_page" and hint.url:
            # Page-level parent: same URL as child
            parent_url = hint.url
            parent_name = hint.metadata.get('page_title', '') or self._format_code_as_name(hint.parent_code)
        else:
            # Campaign-level parent: no URL (rollup)
            parent_url = ''
            parent_name = f"{self._format_code_as_name(hint.channel_code or '')} - {self._format_code_as_name(hint.medium_code or '')}"
        
        parent_touchpoint, _ = Touchpoint.objects.get_or_create(
            code=hint.parent_code,  # e.g., "google.cpc" or "web_page"
            url=parent_url,
            defaults={
                'name': parent_name,
                'channel': channel,
                'medium': medium,
                'touchpoint_type': touchpoint_type,
                'parent': None,  # Parents have no parent
                'description': f"Parent touchpoint for rollup analytics: {hint.parent_code}",
                'is_active': True
            }
        )
    
    # 5. CREATE/GET CHILD TOUCHPOINT (or standalone if no parent)
    touchpoint_code = hint.code or f"generic.{hint.channel_code or 'unknown'}"
    touchpoint_name = hint.label or hint.code or 'Generic Touchpoint'
    
    touchpoint, created = Touchpoint.objects.get_or_create(
        code=touchpoint_code,
        url=hint.url or '',
        defaults={
            'name': touchpoint_name,
            'channel': channel,
            'medium': medium,
            'touchpoint_type': touchpoint_type,
            'parent': parent_touchpoint,  # Link to parent for rollup
            'description': f"Auto-generated touchpoint for {touchpoint_code}",
            'is_active': True
        }
    )
    
    return touchpoint
```

---

## Phase 5: Interaction & WebInteraction Creation

### Location
`backend/websites/models.py` → `_create_web_interaction_with_interaction()`

### Step 5.1: Atomic Creation
```python
@classmethod
def _create_web_interaction_with_interaction(
    cls, 
    event_data: dict, 
    agent, 
    action, 
    interaction_payload: dict, 
    website, 
    touchpoint=None,
    **web_interaction_kwargs
) -> 'WebInteraction':
    """
    Create WebInteraction with proper creation order.
    
    Order:
    1. Touchpoint (already resolved before calling this method)
    2. Interaction (with touchpoint assigned)
    3. WebInteraction (with interaction as primary key)
    """
    from interactions.models import Interaction
    
    # 1. CREATE CORE INTERACTION
    interaction = Interaction.objects.create(
        agent=agent,
        action=action,
        touchpoint=touchpoint,  # Already resolved!
        payload=interaction_payload,
        occurred_at=event_data.get('occurred_at')
    )
    
    # 2. CREATE WEBINTERACTION (extends Interaction via OneToOneField)
    web_interaction = cls.objects.create(
        interaction=interaction,  # Primary key
        website=website,
        session_id=event_data.get('session_id', ''),
        visitor_cookie=event_data.get('visitor_cookie', ''),
        user_agent=event_data.get('user_agent', ''),
        ip=event_data.get('ip_address'),
        utm_source=event_data.get('utm_source', ''),
        utm_medium=event_data.get('utm_medium', ''),
        utm_campaign=event_data.get('utm_campaign', ''),
        utm_content=event_data.get('utm_content', ''),
        utm_term=event_data.get('utm_term', ''),
        element=event_data.get('element', ''),
        payload=event_data.get('payload', {}),
        is_bot=cls._is_bot_user_agent(event_data.get('user_agent', '')),
        **web_interaction_kwargs
    )
    
    return web_interaction
```

---

## 📊 Data Model Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      Page View Event                         │
│  (1 event → 1-3 interactions)                               │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   INTERACTION 1       INTERACTION 2       INTERACTION 3
   (Page View)      (Referrer Click)     (Session Start)
   [CRITICAL]         [OPTIONAL]          [OPTIONAL]
        │                    │                    │
        ├─ Agent             ├─ Agent             ├─ Agent
        ├─ Action            ├─ Action            ├─ Action
        │  (page_view)       │  (referrer_click)  │  (session_start)
        ├─ Touchpoint        ├─ Touchpoint        ├─ Touchpoint
        │   │                │   │                │   │
        │   ├─ Channel       │   ├─ Channel       │   ├─ Channel
        │   │  (owned)       │   │  (external)    │   │  (external)
        │   ├─ Medium        │   ├─ Medium        │   ├─ Medium
        │   │  (web_int.)    │   │  (organic_s.)  │   │  (organic_s.)
        │   └─ Type          │   └─ Type          │   └─ Type
        │      (web_page)    │      (web_search_  │      (web_search_
        │                    │       referral)     │       referral)
        └─ WebInteraction    └─ WebInteraction    └─ WebInteraction
           (UTM, session)       (UTM, session)       (UTM, session)
```

---

## 🎯 Key Design Patterns

### 1. Multi-Interaction Approach
**One event → Multiple perspectives**
- Page view: What was viewed
- Referrer click: How they arrived
- Session start: Journey beginning

### 2. Graceful Degradation
**Critical vs. Optional**
- Page view MUST succeed → raises exception on failure
- Referrer/session MAY fail → logs warning, continues

### 3. Three-Dimensional Taxonomy
**Channel × Medium × TouchpointType**
- Channel: WHERE (owned website vs. external source)
- Medium: HOW (web interaction vs. traffic method)
- TouchpointType: WHAT (page, form, button, referral)

### 4. Hierarchical Touchpoints
**Parent-child for rollup analytics**
- Parent: Campaign rollup (e.g., "google.cpc")
- Child: Specific creative (e.g., "google.cpc.web_search_referral.summer_mba_2025")

### 5. Pre-Creation Resolution
**Touchpoint resolved BEFORE interaction**
- Build hint from raw data
- Resolve touchpoint
- Create interaction with touchpoint already assigned

### 6. Dual-Mode Classification
**Internal vs. Attribution**
- Internal: Track website activity (channel=website, medium=web_interaction)
- Attribution: Track traffic source (channel=source, medium=analyzed)

### 7. Atomic Transactions
**Each interaction wrapped in transaction.atomic()**
- Page view: atomic block
- Referrer: separate atomic block
- Session: separate atomic block

### 8. Fallback Queue
**Failed events stored for retry**
- Server errors (5xx) → store in fallback
- Client errors (4xx) → reject immediately
- Fallback processed by Celery tasks

---

## 📈 Performance Characteristics

### Database Operations per Page View

**Minimal Case** (no referrer, not landing page):
- 1 Website lookup/create
- 1 Agent lookup/create
- 1 Channel lookup/create (via Website)
- 1 Medium lookup/create
- 1 TouchpointType lookup/create
- 1 Touchpoint lookup/create
- 1 Action lookup/create
- 1 Interaction create
- 1 WebInteraction create
- **Total: ~9 database operations**

**Maximum Case** (with referrer + landing page):
- All of above PLUS:
- 2 more Channel lookups/creates (referrer channel)
- 2 more Medium lookups/creates
- 2 more TouchpointType lookups/creates
- 2 more parent Touchpoint creates (for hierarchy)
- 2 more child Touchpoint creates
- 2 more Action lookups/creates
- 2 more Interactions creates
- 2 more WebInteractions creates
- **Total: ~27 database operations**

**Optimizations**:
- Lookups benefit from database indexes
- get_or_create uses SELECT FOR UPDATE
- Transactions ensure atomicity
- Caching can be added at resolver level

---

## ✅ Success Criteria

A page view event is considered successfully processed when:

1. ✅ **Page view interaction created** (minimum requirement)
2. ✅ **All taxonomy created** (Channel, Medium, TouchpointType, Touchpoint)
3. ✅ **Response sent** (201 Created with interaction IDs)

Optional success indicators:
- ✅ Referrer click interaction created (if referrer exists)
- ✅ Session start interaction created (if landing page)
- ✅ Hierarchical touchpoints created (if parent_code specified)

---

## 🔍 Debugging Tips

### Check Event Reception
```bash
# Check Django logs
tail -f /path/to/django.log | grep "Processed page view"
```

### Check Database
```sql
-- Check latest interactions
SELECT 
    i.id,
    i.occurred_at,
    a.code as action,
    t.code as touchpoint,
    c.code as channel,
    m.code as medium,
    tt.code as touchpoint_type
FROM interactions_interaction i
LEFT JOIN interactions_action a ON i.action_id = a.id
LEFT JOIN interactions_touchpoint t ON i.touchpoint_id = t.id
LEFT JOIN interactions_channel c ON t.channel_id = c.id
LEFT JOIN interactions_medium m ON t.medium_id = m.id
LEFT JOIN interactions_touchpointtype tt ON t.touchpoint_type_id = tt.id
ORDER BY i.occurred_at DESC
LIMIT 10;
```

### Check Fallback Queue
```sql
-- Check failed events
SELECT * FROM connectors_failedevent
WHERE connector_type = 'web' 
  AND event_type = 'page_view'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 📚 Related Documentation

- **[README.md](./README.md)**: General overview
- **[MULTI_INTERACTION_APPROACH.md](./MULTI_INTERACTION_APPROACH.md)**: Multi-interaction details
- **[THREE_DIMENSIONAL_CLASSIFICATION.md](./THREE_DIMENSIONAL_CLASSIFICATION.md)**: Taxonomy system
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)**: Implementation status
- **[WEBSITE_EVENTS_CATALOG.md](./WEBSITE_EVENTS_CATALOG.md)**: All event types

---

This document provides the complete, authoritative explanation of how a page_view event flows through BackboneOS from capture to storage.

