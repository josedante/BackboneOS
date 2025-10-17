# Page View Tracking - Quick Start Guide

## Quick Test (5 minutes)

### Step 1: Start Services
```bash
# From project root
docker-compose up -d
```

### Step 2: Run Interactive Monitor
```bash
cd backend
python test_page_view_tracking.py --wait
```

### Step 3: Trigger Event
1. Open http://localhost:4321/ in your browser
2. Wait for page to load completely
3. Go back to terminal and press ENTER

### Step 4: Review Results
The script will display:
- ✅ Database state changes (before/after)
- ✅ All created objects with full details
- ✅ Validation results (green = pass, red = fail)
- ✅ Final summary with success rate

## What to Expect

### Successful Test Output:
```
✅ Interaction count - Expected 1-2, got 1
✅ Page view interaction created
✅ Touchpoint assigned
✅ Channel created - Code: localhost:4321, Type: owned
✅ Channel source_type is 'owned'
✅ Medium created - Code: web_interaction
✅ Medium is 'web_interaction'
✅ TouchpointType created - Code: web_page
✅ TouchpointType is 'web_page'
✅ Touchpoint code is 'web_page'
✅ Touchpoint URL contains localhost:4321
✅ Touchpoint has no parent (page-level)
✅ Action code is 'page_view'
✅ Agent type is 'browser'
✅ Agent has user_agent metadata
✅ WebInteraction has session_id
✅ WebInteraction has visitor_cookie
✅ WebInteraction has payload
✅ WebSession created/updated

✅ ALL CHECKS PASSED!
```

## Quick Inspection (After Test)

```bash
# Quick look at recent data
python inspect_page_view_data.py

# Or use Django command
docker-compose exec backend python manage.py inspect_tracking
```

## Monitor Live Logs (Optional)

```bash
# In a separate terminal
cd backend
./monitor_logs.sh

# Then load the page and watch the logs
```

## Key Objects Created

For each page view at http://localhost:4321/:

1. **Website** - localhost:4321
2. **Channel** - localhost:4321 (owned)
3. **Medium** - web_interaction (asynchronous)
4. **TouchpointType** - web_page
5. **Touchpoint** - The specific page URL
6. **Action** - page_view
7. **Agent** - Browser with user agent
8. **Interaction** - Links everything together
9. **WebInteraction** - Web-specific data
10. **WebSession** - Session tracking

## All relationships are validated to ensure proper foreign keys!

## Tool Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `test_page_view_tracking.py` | Full validation | `python test_page_view_tracking.py --wait` |
| `inspect_page_view_data.py` | Quick inspection | `python inspect_page_view_data.py` |
| `monitor_logs.sh` | Live logs | `./monitor_logs.sh` |
| `inspect_tracking` (Django) | Admin inspection | `docker-compose exec backend python manage.py inspect_tracking` |

## Troubleshooting

**No events received?**
1. Check if backend is running: `docker-compose ps`
2. Check browser console for errors
3. Verify tracking script is loaded

**Validation failed?**
1. Review the detailed output from test script
2. Check logs: `docker-compose logs backend`
3. Inspect objects: `python inspect_page_view_data.py`

## Full Documentation

See `PAGE_VIEW_TRACKING_TESTING.md` for complete documentation, advanced usage, and troubleshooting.

