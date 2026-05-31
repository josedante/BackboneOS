# Page View Event Tracking - Implementation Summary

## Overview

A comprehensive monitoring and validation system has been implemented to track page view events from http://localhost:4321/ to the backend, capturing all received data and generated objects.

## What Was Created

### 1. Main Monitoring Script
**File:** `backend/test_page_view_tracking.py`

**Features:**
- Interactive monitoring with before/after state capture
- Comprehensive object display (Websites, Channels, Mediums, TouchpointTypes, Touchpoints, Actions, Agents, Interactions, WebInteractions, WebSessions)
- Automated validation against expected results
- Color-coded output (✅ green = pass, ❌ red = fail, ⚠️ yellow = warning)
- Detailed validation report with success rate
- Can run in two modes:
  - `--wait`: Interactive mode (captures before/after)
  - `--inspect`: Quick inspection of last 5 minutes

**Usage:**
```bash
cd backend
python test_page_view_tracking.py --wait    # Interactive monitoring
python test_page_view_tracking.py --inspect # Quick inspection
```

### 2. Log Monitoring Helper
**File:** `backend/monitor_logs.sh`

**Features:**
- Real-time Django log monitoring
- Filters for relevant event processing messages
- Shows touchpoint resolution, object creation, errors/warnings
- Color-coded output from Docker logs

**Usage:**
```bash
cd backend
./monitor_logs.sh
```

### 3. Quick Inspection Script
**File:** `backend/inspect_page_view_data.py`

**Features:**
- Displays recent WebInteractions (default: last 10)
- Shows complete touchpoint taxonomy
- Displays WebSession data
- Quick statistics (24-hour window)
- Lightweight and fast

**Usage:**
```bash
cd backend
python inspect_page_view_data.py           # Last 10 interactions
python inspect_page_view_data.py --limit 20 # Last 20 interactions
```

### 4. Django Management Command
**File:** `backend/websites/management/commands/inspect_tracking.py`

**Features:**
- Integrated with Django's management system
- Detailed interaction display with taxonomy
- Statistics and metrics (24-hour window)
- Taxonomy validation (checks for incomplete touchpoints)
- Multiple filter options (session, URL)
- Action breakdown

**Usage:**
```bash
docker-compose exec backend python manage.py inspect_tracking
docker-compose exec backend python manage.py inspect_tracking --limit 20
docker-compose exec backend python manage.py inspect_tracking --session "sess_abc123"
docker-compose exec backend python manage.py inspect_tracking --url "localhost:4321"
docker-compose exec backend python manage.py inspect_tracking --stats-only
```

### 5. Documentation

**File:** [tracking/README.md](README.md) (guía canónica; antiguamente `backend/PAGE_VIEW_TRACKING_TESTING.md`)
- Complete testing guide
- Expected results and validation checklist
- Troubleshooting section
- Advanced usage examples

**File:** [tracking/README.md](README.md#inicio-rapido-5-minutos)
- Quick 5-minute test guide
- Expected output examples
- Tool reference table
- Common troubleshooting

## How It Works

### Event Flow

1. **Page Load**: User opens http://localhost:4321/
2. **Tracking Script**: JavaScript tracker captures page view data
3. **API Call**: POST to http://localhost:8000/api/websites/events/page-view/
4. **Backend Processing**:
   - `PageViewEventView.post()` receives event
   - `WebInteraction.process_page_view_event()` processes data
   - Creates/retrieves Website
   - Builds TouchpointHint from event data
   - Resolves Touchpoint (creates Channel, Medium, TouchpointType if needed)
   - Creates Action and Agent
   - Creates Interaction + WebInteraction atomically
   - Updates/creates WebSession
5. **Response**: Returns success with interaction IDs

### Objects Created

For a direct page view at http://localhost:4321/:

```
Website
  └─ Channel (localhost:4321, source_type='owned')
       └─ Medium (web_interaction, communication_type='asynchronous')
            └─ TouchpointType (web_page)
                 └─ Touchpoint (code='web_page', url='http://localhost:4321/')
                      └─ Interaction (action=page_view, agent=browser)
                           └─ WebInteraction (session_id, visitor_cookie, payload)
                                └─ WebSession (session tracking)
```

### Validation Checks

The monitoring script validates:

1. **Interaction Count**: 1-2 interactions (page_view + optional session_start)
2. **Channel**: Created with source_type='owned'
3. **Medium**: Code is 'web_interaction'
4. **TouchpointType**: Code is 'web_page'
5. **Touchpoint**: Code is 'web_page', URL contains 'localhost:4321', no parent
6. **Action**: Code is 'page_view'
7. **Agent**: Type is 'browser', has user_agent metadata
8. **WebInteraction**: Has session_id, visitor_cookie, payload
9. **WebSession**: Created or updated correctly
10. **Foreign Keys**: All relationships properly linked

## Next Steps

### To Run the Test:

1. **Ensure services are running:**
   ```bash
   docker-compose up -d
   docker-compose ps  # Verify all services are up
   ```

2. **Run the monitoring script:**
   ```bash
   cd backend
   python test_page_view_tracking.py --wait
   ```

3. **Load the page:**
   - Open http://localhost:4321/ in your browser
   - Wait for page to fully load

4. **Complete validation:**
   - Return to terminal
   - Press ENTER
   - Review the comprehensive report

5. **Check results:**
   - Look for ✅ ALL CHECKS PASSED!
   - Review any ❌ failures or ⚠️ warnings
   - Check the summary statistics

### Optional: Monitor Logs Simultaneously

In a separate terminal:
```bash
cd backend
./monitor_logs.sh
```

This will show real-time event processing as you load the page.

## Expected Results

### Successful Test Output

```
================================================================================
                     PAGE VIEW EVENT MONITOR - READY                          
================================================================================

Capturing BEFORE state...

✓ Ready to track page view events

Instructions:
  1. Open your browser to http://localhost:4321/
  2. Wait for page to load (tracking script will fire)
  3. Press ENTER here when ready to inspect results

Press ENTER after you've loaded the page...

Capturing AFTER state...

────────────────────────────────────────────────────────────────────────────────
                         DATABASE STATE COMPARISON                            
────────────────────────────────────────────────────────────────────────────────

Model                     Before          After           Change         
──────────────────────────────────────────────────────────────────────
websites                  0               1               +1
channels                  0               1               +1
mediums                   0               1               +1
touchpoint_types          0               1               +1
touchpoints               0               1               +1
actions                   0               1               +1
agents                    0               1               +1
interactions              0               1               +1
web_interactions          0               1               +1
web_sessions              0               1               +1

... [Detailed object displays] ...

────────────────────────────────────────────────────────────────────────────────
                            VALIDATION RESULTS                                
────────────────────────────────────────────────────────────────────────────────

✅ Interaction count - Expected 1-2, got 1
✅ Page view interaction created
✅ Touchpoint assigned
✅ Channel created - Code: localhost:4321, Type: owned
✅ Channel source_type is 'owned' - Expected 'owned', got 'owned'
✅ Medium created - Code: web_interaction
✅ Medium is 'web_interaction' - Expected 'web_interaction', got 'web_interaction'
✅ TouchpointType created - Code: web_page
✅ TouchpointType is 'web_page' - Expected 'web_page', got 'web_page'
✅ Touchpoint code is 'web_page' - Expected 'web_page', got 'web_page'
✅ Touchpoint URL contains localhost:4321 - URL: http://localhost:4321/
✅ Touchpoint has no parent (page-level) - Parent: None
✅ Action code is 'page_view' - Expected 'page_view', got 'page_view'
✅ Agent type is 'browser' - Expected 'browser', got 'browser'
✅ Agent has user_agent metadata - User agent present
✅ WebInteraction has session_id - Session ID: sess_abc123...
✅ WebInteraction has visitor_cookie - Visitor: visitor_xyz789...
✅ WebInteraction has payload - Keys: ['page_title', 'page_description', ...]
✅ WebSession created/updated - Session ID: sess_abc123

────────────────────────────────────────────────────────────────────────────────
                                  SUMMARY                                      
────────────────────────────────────────────────────────────────────────────────

Total Checks: 18
Passed: 18
Failed: 0
Success Rate: 100.0%

✅ ALL CHECKS PASSED!
```

## Troubleshooting

### No events captured

**Symptoms:** After pressing ENTER, no new objects appear in the AFTER state.

**Solutions:**
1. Check if backend is running: `docker-compose ps`
2. Verify page loaded: Open browser DevTools → Network tab, look for POST to `/api/websites/events/page-view/`
3. Check browser console for JavaScript errors
4. Verify tracking script is loaded on the page

### Validation failures

**Symptoms:** Some checks show ❌ red failures.

**Solutions:**
1. Review the specific failure message in the validation output
2. Check backend logs: `docker-compose logs backend | tail -100`
3. Run inspection to see actual values: `python inspect_page_view_data.py`
4. Check [tracking/README.md](README.md) troubleshooting section

### Incomplete taxonomy

**Symptoms:** Touchpoints missing Channel, Medium, or TouchpointType.

**Solutions:**
1. Run taxonomy validation: `docker-compose exec backend python manage.py inspect_tracking --stats-only`
2. Check touchpoint resolution in logs
3. Verify the build_touchpoint_hint_from_event_data method is working correctly

## Tools Reference

| Tool | Purpose | Best For |
|------|---------|----------|
| `test_page_view_tracking.py` | Full validation with before/after | Initial testing, debugging |
| `inspect_page_view_data.py` | Quick data inspection | Quick checks, monitoring |
| `monitor_logs.sh` | Real-time log viewing | Debugging, understanding flow |
| `inspect_tracking` (Django) | Admin-level inspection | Production checks, statistics |

## Architecture Notes

### Multi-Interaction Approach

A single page view can create up to 3 interactions:

1. **Page View Interaction** (always): The main interaction
2. **Referrer Click** (optional): If came from external referrer
3. **Session Start** (optional): If is_landing_page=true

### Touchpoint Resolution Pattern (v2.0)

The system uses the modernized v2.0 pattern:

```python
# 1. Build hint from event data
hint = WebInteraction.build_touchpoint_hint_from_event_data(event_data, website)

# 2. Resolve touchpoint BEFORE creating interaction
touchpoint = resolver.resolve(hint, connector_type='web', source_identifier=domain)

# 3. Create objects with touchpoint already assigned
interaction = Interaction.objects.create(touchpoint=touchpoint, ...)
web_interaction = WebInteraction.objects.create(interaction=interaction, ...)
```

### Three-Dimensional Taxonomy

Every touchpoint has three dimensions:

1. **Channel**: WHERE the interaction came from (e.g., localhost:4321, google, facebook)
2. **Medium**: HOW they communicated (e.g., web_interaction, organic_search, social_media)
3. **TouchpointType**: WHAT type of interaction (e.g., web_page, web_form, web_button)

## Summary

The monitoring system is now ready to track and validate all page view events from http://localhost:4321/. The tools provide comprehensive visibility into:

- What data is received from the tracking script
- What objects are created in the database
- How objects are related (taxonomy)
- Whether everything matches expectations

Run `python test_page_view_tracking.py --wait` to start your first comprehensive test!

