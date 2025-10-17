# Page View Event Tracking - Testing Guide

This guide explains how to test and validate page view events using the comprehensive monitoring tools.

## Overview

When you load a page at http://localhost:4321/ with the tracking script installed, the system should:

1. Capture the page view event from the JavaScript tracker
2. Send it to the backend API at http://localhost:8000/api/websites/events/page-view/
3. Create multiple database objects:
   - Website (or retrieve existing)
   - Channel (for the website domain)
   - Medium (web_interaction)
   - TouchpointType (web_page)
   - Touchpoint (the specific page)
   - Action (page_view)
   - Agent (browser)
   - Interaction (links all of the above)
   - WebInteraction (extends Interaction with web-specific data)
   - WebSession (session tracking)

## Prerequisites

1. Backend services running (Docker):
   ```bash
   docker-compose up -d
   ```

2. Frontend/website running at http://localhost:4321/

3. Tracking script installed on the page

## Testing Methods

We provide 4 tools for comprehensive tracking and validation:

### Method 1: Interactive Monitoring (Recommended for First Test)

**Tool:** `test_page_view_tracking.py`

This is the most comprehensive tool. It captures the before/after state and validates all created objects.

```bash
# Navigate to backend directory
cd backend

# Run in interactive mode
python test_page_view_tracking.py --wait

# Follow the instructions:
# 1. Script will capture BEFORE state
# 2. Open http://localhost:4321/ in your browser
# 3. Press ENTER in the terminal
# 4. Script will capture AFTER state and validate
```

**What it does:**
- ✅ Captures database state before and after
- ✅ Shows exactly which objects were created
- ✅ Displays full details of each object
- ✅ Validates against expectations
- ✅ Shows all relationships (Channel → Medium → TouchpointType → Touchpoint)
- ✅ Color-coded output (green = pass, red = fail, yellow = warning)
- ✅ Final summary with success rate

### Method 2: Quick Inspection

**Tool:** `inspect_page_view_data.py`

Quick inspection of recently created objects (last 5 minutes).

```bash
cd backend

# Inspect recent data (default: last 10 interactions)
python inspect_page_view_data.py

# Inspect more interactions
python inspect_page_view_data.py --limit 20
```

**What it shows:**
- Recent WebInteractions with full details
- Touchpoint taxonomy (Channel → Medium → Type)
- WebSessions
- Quick statistics

### Method 3: Django Management Command

**Tool:** Django `inspect_tracking` command

Use Django's management interface for inspection.

```bash
cd backend

# Basic inspection
docker-compose exec backend python manage.py inspect_tracking

# With custom limit
docker-compose exec backend python manage.py inspect_tracking --limit 20

# Filter by session
docker-compose exec backend python manage.py inspect_tracking --session "sess_abc123"

# Filter by URL
docker-compose exec backend python manage.py inspect_tracking --url "localhost:4321"

# Statistics only
docker-compose exec backend python manage.py inspect_tracking --stats-only
```

**What it shows:**
- Recent interactions with full taxonomy
- Statistics (24h)
- Taxonomy validation
- Action breakdown

### Method 4: Live Log Monitoring

**Tool:** `monitor_logs.sh`

Watch backend logs in real-time to see the event processing flow.

```bash
cd backend

# Start log monitoring
./monitor_logs.sh

# In another terminal, load the page at http://localhost:4321/
# Watch the logs for event processing
```

**What it shows:**
- Real-time event reception
- Object creation messages
- Touchpoint resolution process
- Any errors or warnings

## Recommended Testing Workflow

### First Test (Complete Validation)

1. **Start log monitoring** (Terminal 1):
   ```bash
   cd backend
   ./monitor_logs.sh
   ```

2. **Run interactive monitoring** (Terminal 2):
   ```bash
   cd backend
   python test_page_view_tracking.py --wait
   ```

3. **Load the page**:
   - Open http://localhost:4321/ in your browser
   - Wait for page to fully load

4. **Complete the test**:
   - Switch back to Terminal 2
   - Press ENTER
   - Review the comprehensive report

5. **Check logs**:
   - Switch to Terminal 1
   - Review any errors or warnings

### Subsequent Tests (Quick Check)

```bash
cd backend

# Quick inspection
python inspect_page_view_data.py

# Or use Django command
docker-compose exec backend python manage.py inspect_tracking
```

## Expected Results

For a direct page view (no referrer, new session) at http://localhost:4321/:

### Database Objects Created

1. **Website**
   - base_url: "http://localhost:4321"
   - name: "localhost:4321" or extracted domain
   - active: true

2. **Channel**
   - code: "localhost:4321" (or similar)
   - source_type: "owned"
   - name: Website name

3. **Medium**
   - code: "web_interaction"
   - communication_type: "asynchronous"
   - name: "Web Interaction"

4. **TouchpointType**
   - code: "web_page"
   - name: "Web Page"

5. **Touchpoint**
   - code: "web_page"
   - url: "http://localhost:4321/"
   - channel: → Channel (owned)
   - medium: → Medium (web_interaction)
   - touchpoint_type: → TouchpointType (web_page)
   - parent: null (page-level touchpoint)

6. **Action**
   - code: "page_view"
   - name: "Page View"

7. **Agent**
   - agent_type: "browser"
   - metadata: Contains user_agent string

8. **Interaction** (1-2 created)
   - Primary: page_view interaction
   - Optional: session_start (if is_landing_page=true)
   - touchpoint: → Touchpoint
   - action: → Action (page_view)
   - agent: → Agent (browser)

9. **WebInteraction**
   - Extends Interaction (uses Interaction.pk as FK)
   - session_id: From tracking script
   - visitor_cookie: From tracking script
   - payload: Page metadata (title, description, etc.)

10. **WebSession**
    - session_id: Matches WebInteraction.session_id
    - page_count: 1 (or incremented if existing)
    - is_bounce: true (if page_count=1)

### Validation Checklist

The monitoring script validates:

- ✅ 1-2 interactions created
- ✅ Channel has source_type='owned'
- ✅ Medium is 'web_interaction'
- ✅ TouchpointType is 'web_page'
- ✅ Touchpoint code is 'web_page'
- ✅ Touchpoint URL contains 'localhost:4321'
- ✅ Touchpoint has no parent (page-level)
- ✅ Action code is 'page_view'
- ✅ Agent type is 'browser'
- ✅ Agent has user_agent metadata
- ✅ WebInteraction has session_id
- ✅ WebInteraction has visitor_cookie
- ✅ WebInteraction has payload
- ✅ WebSession created/updated
- ✅ All foreign key relationships correct

## Troubleshooting

### No events received

**Check:**
1. Is the tracking script loaded on the page?
   - Open browser DevTools → Network tab
   - Look for request to `/api/websites/events/page-view/`

2. Is the backend running?
   ```bash
   docker-compose ps
   curl http://localhost:8000/health/
   ```

3. Check browser console for errors
   - Open DevTools → Console

### Events received but validation fails

**Check:**
1. Review the validation report from `test_page_view_tracking.py`
2. Check backend logs for errors:
   ```bash
   docker-compose logs backend | grep -i error
   ```

3. Inspect objects directly:
   ```bash
   docker-compose exec backend python manage.py inspect_tracking
   ```

### Touchpoint taxonomy incomplete

If touchpoints are missing Channel/Medium/Type:

```bash
# Check the resolution process
docker-compose exec backend python manage.py shell
>>> from websites.models import WebInteraction
>>> wi = WebInteraction.objects.latest('created_at')
>>> wi.interaction.touchpoint
>>> wi.interaction.touchpoint.channel
>>> wi.interaction.touchpoint.medium
>>> wi.interaction.touchpoint.touchpoint_type
```

## Advanced Usage

### Test with UTM Parameters

```bash
# Open URL with UTM params
http://localhost:4321/?utm_source=google&utm_medium=cpc&utm_campaign=test
```

Expected: Different Channel/Medium based on UTM parameters

### Test with Referrer

```bash
# Navigate from another page
# 1. Open http://example.com in browser
# 2. Click link to http://localhost:4321/
```

Expected: 2-3 interactions (referrer_click + page_view + optional session_start)

### Compare Multiple Page Views

```bash
# Run inspection before
python inspect_page_view_data.py > before.txt

# Load page multiple times

# Run inspection after
python inspect_page_view_data.py > after.txt

# Compare
diff before.txt after.txt
```

## Django Admin Inspection

You can also inspect data via Django Admin:

1. Open http://localhost:8000/admin/
2. Navigate to:
   - Interactions → Interactions
   - Websites → Web Interactions
   - Interactions → Touchpoints
   - Interactions → Channels
   - Interactions → Mediums

## Database Queries (Advanced)

For direct SQL inspection:

```bash
docker-compose exec backend python manage.py dbshell

-- Recent interactions
SELECT i.id, a.code as action, tp.code as touchpoint, tp.url
FROM interactions_interaction i
LEFT JOIN interactions_action a ON i.action_id = a.id
LEFT JOIN interactions_touchpoint tp ON i.touchpoint_id = tp.id
ORDER BY i.created_at DESC
LIMIT 10;

-- Touchpoint taxonomy
SELECT 
    tp.code as touchpoint_code,
    c.code as channel,
    c.source_type,
    m.code as medium,
    tt.code as type
FROM interactions_touchpoint tp
LEFT JOIN interactions_channel c ON tp.channel_id = c.id
LEFT JOIN interactions_medium m ON tp.medium_id = m.id
LEFT JOIN interactions_touchpointtype tt ON tp.touchpoint_type_id = tt.id
ORDER BY tp.created_at DESC
LIMIT 10;
```

## Summary

The comprehensive monitoring tools provide multiple ways to track and validate page view events:

1. **Interactive Monitoring**: Full before/after comparison with validation
2. **Quick Inspection**: Fast check of recent data
3. **Management Command**: Django-integrated inspection
4. **Live Logs**: Real-time event processing

Use the interactive monitoring tool for your first test to get a complete validation report.

