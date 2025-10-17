# Page View Tracking Tools - Quick Reference

## 🎯 What These Tools Do

These tools help you track, validate, and inspect page view events sent from http://localhost:4321/ to the backend API, ensuring all database objects (Channels, Touchpoints, WebInteractions, etc.) are created correctly.

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Start services
docker-compose up -d

# 2. Run monitoring
cd backend
python test_page_view_tracking.py --wait

# 3. Load page in browser
# Open: http://localhost:4321/

# 4. Press ENTER in terminal
# Review results!
```

## 📦 Available Tools

### 1. Interactive Monitor (Recommended First Test)
```bash
python test_page_view_tracking.py --wait
```
- Captures before/after database state
- Shows all created objects with full details
- Validates against expectations
- Color-coded results (✅/❌/⚠️)
- Success rate summary

### 2. Quick Inspection
```bash
python inspect_page_view_data.py
python inspect_page_view_data.py --limit 20
```
- Fast inspection of recent data
- Shows last N interactions
- WebSession summary
- Quick statistics

### 3. Django Management Command
```bash
docker-compose exec backend python manage.py inspect_tracking
docker-compose exec backend python manage.py inspect_tracking --session "sess_abc"
docker-compose exec backend python manage.py inspect_tracking --url "localhost:4321"
```
- Django-integrated inspection
- Advanced filtering options
- Taxonomy validation
- 24-hour statistics

### 4. Live Log Monitor
```bash
./monitor_logs.sh
```
- Real-time Django logs
- Shows event processing flow
- Highlights errors/warnings

## 📊 What Gets Validated

For each page view, the system checks:

- ✅ 1-2 Interactions created (page_view + optional session_start)
- ✅ **Channel** created with source_type='owned'
- ✅ **Medium** is 'web_interaction'
- ✅ **TouchpointType** is 'web_page'
- ✅ **Touchpoint** has correct URL and taxonomy
- ✅ **Action** is 'page_view'
- ✅ **Agent** is 'browser' with user_agent
- ✅ **WebInteraction** has session_id, visitor_cookie, payload
- ✅ **WebSession** created/updated
- ✅ All foreign key relationships valid

## 📚 Documentation

- **Quick Start**: `TRACKING_TEST_QUICK_START.md`
- **Full Guide**: `PAGE_VIEW_TRACKING_TESTING.md`
- **Implementation Summary**: `../TRACKING_IMPLEMENTATION_SUMMARY.md`

## 🎯 Expected Output (Success)

```
✅ ALL CHECKS PASSED!

Total Checks: 18
Passed: 18
Failed: 0
Success Rate: 100.0%
```

## 🔧 Troubleshooting

**No events received?**
- Check browser DevTools → Network tab for API call
- Verify backend is running: `docker-compose ps`
- Check browser console for errors

**Validation failed?**
- Review detailed output from test script
- Check logs: `docker-compose logs backend`
- Inspect objects: `python inspect_page_view_data.py`

## 📖 Full Documentation

See `PAGE_VIEW_TRACKING_TESTING.md` for complete testing guide, expected results, troubleshooting, and advanced usage.

## 🎪 Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| Direct traffic (no referrer) | 1 interaction (page_view) |
| Landing page (is_landing_page=true) | 2 interactions (page_view + session_start) |
| With external referrer | 2-3 interactions (referrer_click + page_view + optional session_start) |
| With UTM parameters | Different Channel/Medium based on UTM |

## 🏗️ Database Objects Created

```
Website (localhost:4321)
  └─ Channel (owned)
       └─ Medium (web_interaction)
            └─ TouchpointType (web_page)
                 └─ Touchpoint (specific page)
                      └─ Interaction
                           └─ WebInteraction
                                └─ WebSession
```

All relationships validated! ✨

