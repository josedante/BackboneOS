# 🖥️ Simple Session Management - BackboneOS

## 📋 Overview

Simple session management logic: **session continues if the new interaction falls within the 30-minute window, otherwise create a new session**.

## 🎯 Session Logic

### **Simple Rule**:
- **Within 30 minutes**: Continue existing session
- **Beyond 30 minutes**: Create new session

### **Implementation**:
```python
@classmethod
def infer_session_for_interaction(cls, web_interaction: 'WebInteraction') -> 'WebSession':
    """
    Simple logic: session continues if within 30 minutes, otherwise create new session.
    """
    visitor_cookie = web_interaction.visitor_cookie
    website = web_interaction.website
    occurred_at = web_interaction.occurred_at
    
    # Check for existing active session within 30-minute window
    timeout_threshold = occurred_at - timedelta(minutes=30)
    
    # Look for recent session with same visitor cookie
    recent_session = cls.objects.filter(
        visitor_cookie=visitor_cookie,
        website=website,
        last_activity_at__gte=timeout_threshold,
        ended_at__isnull=True
    ).order_by('-last_activity_at').first()
    
    if recent_session:
        # Continue existing session
        recent_session.last_activity_at = occurred_at
        recent_session.page_count += 1
        recent_session.is_bounce = False  # Multiple pages = not a bounce
        recent_session.save()
        return recent_session
    
    # Create new session
    return cls._create_new_session(web_interaction)
```

## 🎯 Benefits

### **Simplicity**:
- **Easy to understand**: Single rule for session management
- **Easy to maintain**: No complex logic to debug
- **Easy to test**: Simple test cases

### **Reliability**:
- **Consistent behavior**: Same logic for all interactions
- **Predictable results**: Clear session boundaries
- **Minimal edge cases**: Simple timeout logic

### **Performance**:
- **Fast queries**: Simple database lookups
- **Efficient processing**: Minimal computation
- **Scalable**: Works with high-volume traffic

## 📊 Session Lifecycle

### **Session Creation**:
1. New visitor arrives
2. No existing session within 30 minutes
3. Create new session with visitor data

### **Session Continuation**:
1. Existing visitor returns
2. Within 30 minutes of last activity
3. Update existing session

### **Session Timeout**:
1. Visitor returns after 30+ minutes
2. Create new session
3. Previous session remains in history

## 🔧 Usage

### **Automatic Session Inference**:
```python
# Session is automatically inferred when saving interactions
web_interaction = WebInteraction.objects.create(...)
# Session is automatically assigned
```

### **Manual Session Management**:
```python
# Get or create session for interaction
session = WebSession.infer_session_for_interaction(web_interaction)
```

## 📈 Analytics

### **Session Metrics**:
- **Total Sessions**: Count of all sessions
- **Active Sessions**: Currently active sessions
- **Bounce Rate**: Single-page sessions
- **Session Duration**: Time between first and last interaction

### **Session Patterns**:
- **Session Length**: Pages per session
- **Session Frequency**: Sessions per visitor
- **Session Attribution**: UTM parameters and referrers

This simplified approach provides reliable session management with minimal complexity.
