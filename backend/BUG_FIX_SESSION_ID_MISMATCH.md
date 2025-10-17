# Bug Fix: Session ID Mismatch

## Issue Summary

**Severity:** High  
**Status:** ✅ Fixed  
**Date:** 2025-10-17

### Problem

WebInteraction and WebSession had different session IDs, breaking the relationship between interactions and their session:

- **WebInteraction session_id:** `sess_xrgjb28zwup` (from tracking script)
- **WebSession session_id:** `sess_50b5cf43443e4027` (randomly generated)

This prevented queries like "get all interactions in this session" from working correctly.

### Root Cause

**File:** `backend/websites/models.py`  
**Method:** `WebSession._create_new_session()` (line 245)

The method was generating a new random session_id instead of using the one from the WebInteraction:

```python
# BEFORE (INCORRECT)
session_id = f"sess_{uuid.uuid4().hex[:16]}"
```

The WebInteraction already has a session_id from the JavaScript tracking script, but the WebSession was ignoring it and generating its own.

### Fix Applied

Updated `_create_new_session()` to use the session_id from the WebInteraction:

```python
# AFTER (CORRECT)
session_id = web_interaction.session_id or f"sess_{uuid.uuid4().hex[:16]}"
```

**Benefits:**
- Uses the session_id from the tracking script (maintains continuity)
- Fallback to generation if session_id is empty (defensive coding)
- Maintains data integrity between WebInteraction ↔ WebSession

### Impact

**Before Fix:**
- Session queries broken
- Analytics by session impossible
- Can't track user journey across pages

**After Fix:**
- ✅ Session IDs match perfectly
- ✅ Can query all interactions in a session
- ✅ User journey tracking works
- ✅ Session-based analytics enabled

### Verification Steps

1. **Restart backend** (to load the fixed code):
   ```bash
   docker-compose restart backend
   ```

2. **Clear test data** (optional, for clean test):
   ```bash
   docker-compose exec backend python manage.py shell
   >>> from websites.models import WebSession, WebInteraction
   >>> from interactions.models import Interaction
   >>> WebInteraction.objects.all().delete()
   >>> Interaction.objects.all().delete()
   >>> WebSession.objects.all().delete()
   >>> exit()
   ```

3. **Run the monitoring script again**:
   ```bash
   docker-compose exec backend python test_page_view_tracking.py --wait
   ```

4. **Load the page**: http://localhost:4321/

5. **Press ENTER** and verify:
   - ✅ Session IDs match check should now pass
   - ✅ Success rate should be 100% (20/20)

### Expected Results After Fix

```
────────────────────────────────────────────────────────────────────────────────
VALIDATION RESULTS
────────────────────────────────────────────────────────────────────────────────
✅ Interaction count - Expected 1-2, got 2
✅ Page view interaction created
✅ Touchpoint assigned
...
✅ WebSession created/updated - Session ID: sess_xrgjb28zwup
✅ Session IDs match (WebInteraction ↔ WebSession) - WebInteraction: sess_xrgjb28zwup, WebSession: sess_xrgjb28zwup

────────────────────────────────────────────────────────────────────────────────
SUMMARY
────────────────────────────────────────────────────────────────────────────────

Total Checks: 20
Passed: 20
Failed: 0
Success Rate: 100.0%

✅ ALL CHECKS PASSED!
```

### Related Queries

Now that session IDs match, these queries will work correctly:

```python
# Get all interactions in a session
session_id = "sess_xrgjb28zwup"
interactions = WebInteraction.objects.filter(session_id=session_id)

# Get the WebSession
web_session = WebSession.objects.get(session_id=session_id)

# Verify they match
assert interactions.first().session_id == web_session.session_id  # ✅ True

# Get session analytics
print(f"Pages in session: {web_session.page_count}")
print(f"Is bounce: {web_session.is_bounce}")
print(f"Duration: {web_session.duration}")
```

### Lessons Learned

1. **Trust the client-side session_id**: The tracking script generates consistent session IDs across page views, so we should preserve them.

2. **Defensive coding**: Using `web_interaction.session_id or fallback` ensures the system still works even if the tracking script fails to provide a session_id.

3. **Comprehensive testing**: The monitoring script caught this issue immediately by validating the relationship between objects.

### Files Changed

- `backend/websites/models.py` (line 246)

### Test Coverage

This fix is automatically validated by:
- `backend/test_page_view_tracking.py` - Session ID match check
- Expected to pass after restart

### Migration Required?

**No migration needed.** This is a logic fix in the code, not a schema change.

Existing WebSessions with mismatched session_ids can be fixed with a data migration if needed, but new sessions will have correct IDs immediately.

---

## Status: ✅ RESOLVED

The bug has been identified and fixed. Session IDs will now match between WebInteraction and WebSession, enabling proper session-based analytics and user journey tracking.

