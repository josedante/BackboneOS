# 🖥️ Server-Side Session Inference - BackboneOS

## 📋 Overview

Instead of capturing session start events on the client side, we capture **page views** and **infer session starts on the server**. This approach is more reliable, consistent, and provides better data quality.

---

## 🎯 Why Server-Side Inference is Better

### **Client-Side Problems**:
- **Inconsistent Logic**: Different browsers handle sessions differently
- **JavaScript Errors**: Client-side errors can break session tracking
- **Ad Blockers**: May block client-side tracking scripts
- **Network Issues**: Failed requests can cause session gaps
- **Complexity**: More complex client-side code to maintain

### **Server-Side Benefits**:
- **Consistent Logic**: Single source of truth for session rules
- **Reliable**: Server-side processing is more stable
- **Complete Data**: All page views are captured regardless of client issues
- **Simpler Client**: Minimal JavaScript required
- **Better Analytics**: More accurate session boundaries

---

## 🔧 Implementation Approach

### **Client-Side (Simple)**:
```javascript
// Minimal client-side tracking
window.BackboneTracker = {
  init: function() {
    this.sessionId = this.getOrCreateSessionId();
    this.trackPageView();
    this.setupEngagementTracking();
  },
  
  trackPageView: function() {
    this.track('page_view', {
      page_title: document.title,
      page_category: this.getPageCategory(),
      load_time: this.getLoadTime(),
      is_landing_page: this.isLandingPage(),
      page_depth: this.getPageDepth()
    });
  }
};
```

### **Server-Side (Intelligent)**:
```python
# Server-side session inference
class SessionInferenceService:
    def process_page_view(self, web_interaction):
        """Process page view and infer session start if needed"""
        
        # Check if this should trigger a new session
        session_start_reason = self.should_start_new_session(web_interaction)
        
        if session_start_reason:
            # Create session start event
            self.create_session_start_event(web_interaction, session_start_reason)
        
        # Always create the page view event
        self.create_page_view_event(web_interaction)
    
    def should_start_new_session(self, web_interaction):
        """Determine if this page view should start a new session"""
        
        visitor_cookie = web_interaction.visitor_cookie
        
        # 1. New visitor (no previous interactions)
        if not self.has_previous_interactions(visitor_cookie):
            return 'new_visitor'
        
        # 2. Session timeout (gap > 30 minutes)
        last_interaction = self.get_last_interaction(visitor_cookie)
        if self.is_session_timeout(last_interaction, web_interaction):
            return 'session_timeout'
        
        # 3. Cross-domain referrer
        if self.is_cross_domain_referrer(web_interaction):
            return 'cross_domain'
        
        # 4. UTM parameter change
        if self.has_utm_parameter_change(visitor_cookie, web_interaction):
            return 'utm_change'
        
        # 5. Device/browser change
        if self.has_device_change(visitor_cookie, web_interaction):
            return 'device_change'
        
        # 6. Manual session reset
        if self.is_manual_session_reset(web_interaction):
            return 'manual_reset'
        
        return None  # Continue existing session
```

---

## 📊 Session Inference Logic

### **1. New Visitor Detection**
```python
def is_new_visitor(self, visitor_cookie):
    """Check if this is a new visitor"""
    return not WebInteraction.objects.filter(
        visitor_cookie=visitor_cookie
    ).exists()
```

### **2. Session Timeout Detection**
```python
def is_session_timeout(self, last_interaction, current_interaction):
    """Check if session has timed out"""
    if not last_interaction:
        return False
    
    time_gap = current_interaction.created_at - last_interaction.created_at
    timeout_duration = timedelta(minutes=30)
    
    return time_gap > timeout_duration
```

### **3. Cross-Domain Referrer Detection**
```python
def is_cross_domain_referrer(self, web_interaction):
    """Check if referrer is from different domain"""
    if not web_interaction.referrer_url:
        return False
    
    referrer_domain = urlparse(web_interaction.referrer_url).netloc
    website_domain = urlparse(web_interaction.website.base_url).netloc
    
    return referrer_domain != website_domain
```

### **4. UTM Parameter Change Detection**
```python
def has_utm_parameter_change(self, visitor_cookie, current_interaction):
    """Check if UTM parameters have changed"""
    last_interaction = self.get_last_interaction(visitor_cookie)
    if not last_interaction:
        return False
    
    current_utm = {
        'utm_source': current_interaction.utm_source,
        'utm_medium': current_interaction.utm_medium,
        'utm_campaign': current_interaction.utm_campaign
    }
    
    last_utm = {
        'utm_source': last_interaction.utm_source,
        'utm_medium': last_interaction.utm_medium,
        'utm_campaign': last_interaction.utm_campaign
    }
    
    return current_utm != last_utm
```

### **5. Device Change Detection**
```python
def has_device_change(self, visitor_cookie, current_interaction):
    """Check if device/browser has changed"""
    last_interaction = self.get_last_interaction(visitor_cookie)
    if not last_interaction:
        return False
    
    return current_interaction.user_agent != last_interaction.user_agent
```

---

## 🔄 Data Flow

### **Simplified Flow**:
```
1. User visits page
2. JavaScript sends page_view event
3. Server processes page_view
4. Server infers session_start if needed
5. Both events stored in database
6. Analytics and reporting use both events
```

### **Event Creation**:
```python
def create_session_start_event(self, web_interaction, reason):
    """Create a session start event based on page view"""
    
    # Create the session start interaction
    session_start_interaction = Interaction.objects.create(
        action=Action.objects.get(code='session_start'),
        touchpoint=self.resolve_touchpoint(web_interaction),
        agent=self.resolve_agent(web_interaction),
        occurred_at=web_interaction.created_at,
        payload={
            'inference_reason': reason,
            'inferred_from_page_view': True,
            'original_page_view_id': web_interaction.id
        }
    )
    
    # Create the web interaction record
    WebInteraction.objects.create(
        interaction=session_start_interaction,
        website=web_interaction.website,
        session_id=web_interaction.session_id,
        visitor_cookie=web_interaction.visitor_cookie,
        user_agent=web_interaction.user_agent,
        utm_source=web_interaction.utm_source,
        utm_medium=web_interaction.utm_medium,
        utm_campaign=web_interaction.utm_campaign,
        payload={
            'session_start_time': web_interaction.created_at.isoformat(),
            'is_new_visitor': reason == 'new_visitor',
            'landing_page': True,
            'inference_reason': reason
        }
    )
```

---

## 📈 Benefits

### **Data Quality**:
- **Consistent Session Boundaries**: All sessions follow same rules
- **Complete Coverage**: No missed session starts due to client issues
- **Accurate Attribution**: Better campaign and source attribution
- **Reliable Analytics**: More trustworthy session metrics

### **Performance**:
- **Faster Client**: Minimal JavaScript execution
- **Better UX**: No client-side session logic delays
- **Reduced Errors**: Fewer client-side failures
- **Scalable**: Server-side processing scales better

### **Maintenance**:
- **Single Source of Truth**: Session logic in one place
- **Easier Updates**: Change session rules without client updates
- **Better Testing**: Server-side logic easier to test
- **Simpler Debugging**: Centralized session logic

---

## 🚀 Implementation Steps

1. **Update Client Code**: Simplify to only track page views
2. **Implement Server Logic**: Add session inference service
3. **Update Database**: Ensure proper indexing for session queries
4. **Test Session Rules**: Verify all session triggers work correctly
5. **Monitor Performance**: Track server-side processing performance
6. **Validate Analytics**: Ensure session metrics are accurate

---

## 📊 Success Metrics

- **Session Accuracy**: % of sessions properly inferred
- **Data Completeness**: % of page views with proper session context
- **Performance**: Server-side processing time
- **Client Reliability**: % of successful page view captures
- **Analytics Quality**: Accuracy of session-based metrics

This server-side approach provides more reliable, consistent, and maintainable session tracking while simplifying the client-side implementation.
