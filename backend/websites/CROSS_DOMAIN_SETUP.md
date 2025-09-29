# Cross-Domain Tracking Setup Guide

## Overview

The BackboneOS tracking script is designed to run on external websites (different domains) and send data to your BackboneOS server. This requires proper CORS (Cross-Origin Resource Sharing) configuration.

## Server Configuration

### 1. Install Django CORS Headers

```bash
pip install django-cors-headers
```

### 2. Add to Django Settings

```python
# settings.py

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'corsheaders',
]

# Add to MIDDLEWARE
MIDDLEWARE = [
    # ... other middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
    "https://client-domain.com",
    # Add all domains that will use the tracking script
]

# For development/testing (not recommended for production)
CORS_ALLOW_ALL_ORIGINS = True

# Allow credentials for session tracking
CORS_ALLOW_CREDENTIALS = True

# Allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Allowed methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

### 3. Update API Views

```python
# websites/views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import json

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
@never_cache
def page_view_event(request):
    """
    Handle page view events from external websites.
    Supports CORS for cross-domain requests.
    """
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    try:
        data = json.loads(request.body)
        
        # Process the event data using your existing logic
        interactions = WebInteraction.process_page_view_event(data)
        
        # Return success response with CORS headers
        response = JsonResponse({
            "status": "success", 
            "message": "Event processed",
            "interactions_created": len(interactions)
        })
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
        
    except Exception as e:
        error_response = JsonResponse({
            "status": "error", 
            "message": str(e)
        }, status=400)
        
        # Add CORS headers to error response
        error_response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        error_response['Access-Control-Allow-Credentials'] = 'true'
        
        return error_response
```

### 4. Update URL Configuration

```python
# websites/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('events/page-view/', views.page_view_event, name='page-view-event'),
    # ... other URLs
]
```

## Client Configuration

### 1. Basic Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your Website</title>
    
    <!-- Load BackboneOS tracking script -->
    <script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
</head>
<body>
    <!-- Your website content -->
</body>
</html>
```

### 2. Advanced Configuration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your Website</title>
    
    <!-- Configure tracking before loading script -->
    <script>
        window.BackboneConfig = {
            // Full API endpoint URL
            apiEndpoint: 'https://your-backboneos-domain.com/api/websites/events/page-view/',
            
            // Session configuration
            sessionTimeout: 30 * 60 * 1000, // 30 minutes
            visitorCookieExpiry: 365 * 24 * 60 * 60 * 1000, // 1 year
            
            // Engagement settings
            engagementThreshold: 30 * 1000, // 30 seconds
            scrollThreshold: 50, // 50% scroll depth
            wordCountThreshold: 200,
            shortContentThreshold: 10 * 1000, // 10 seconds
            
            // Performance settings
            batchSize: 10,
            retryAttempts: 3,
            retryDelay: 1000,
            
            // Feature toggles
            features: {
                pageViews: true,
                pageReads: true,
                clicks: true,
                formSubmissions: true,
                downloads: true,
                videoPlays: true,
                searches: true,
                newsletterSignups: true,
                scrollTracking: true,
                timeTracking: true,
                utmTracking: true,
                referrerTracking: true,
                botDetection: true,
                engagementTracking: true
            },
            
            // Privacy settings
            privacy: {
                respectDoNotTrack: true,
                anonymizeIP: false,
                gdprCompliant: true,
                cookieConsent: true
            },
            
            // Debug settings
            debug: {
                enabled: false,
                logEvents: false,
                logErrors: true,
                verbose: false
            }
        };
    </script>
    
    <!-- Load BackboneOS tracking script -->
    <script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
</head>
<body>
    <!-- Your website content -->
</body>
</html>
```

## Testing Cross-Domain Setup

### 1. Test CORS Configuration

```javascript
// Test script to verify CORS setup
fetch('https://your-backboneos-domain.com/api/websites/events/page-view/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        event_type: 'test',
        website_base: window.location.origin,
        full_url: window.location.href,
        session_id: 'test_session',
        visitor_cookie: 'test_visitor',
        user_agent: navigator.userAgent
    })
})
.then(response => response.json())
.then(data => console.log('CORS test successful:', data))
.catch(error => console.error('CORS test failed:', error));
```

### 2. Browser Developer Tools

1. Open browser developer tools (F12)
2. Go to Network tab
3. Load your website with the tracking script
4. Look for requests to your BackboneOS domain
5. Check for CORS errors in the console

### 3. Common CORS Issues

#### Issue: "Access to fetch at '...' from origin '...' has been blocked by CORS policy"

**Solution:** Add the client domain to `CORS_ALLOWED_ORIGINS` in Django settings.

#### Issue: "Request header field x-csrftoken is not allowed by Access-Control-Allow-Headers"

**Solution:** Add `'x-csrftoken'` to `CORS_ALLOW_HEADERS` in Django settings.

#### Issue: "Credentials flag is true, but the 'Access-Control-Allow-Credentials' header is not set"

**Solution:** Set `CORS_ALLOW_CREDENTIALS = True` in Django settings.

## Production Considerations

### 1. Security

```python
# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://trusted-client-1.com",
    "https://trusted-client-2.com",
    # Only add trusted domains
]

# Never use in production
# CORS_ALLOW_ALL_ORIGINS = True
```

### 2. Rate Limiting

```python
# Add rate limiting for API endpoints
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def page_view_event(request):
    # ... your view logic
```

### 3. Monitoring

```python
# Add logging for cross-domain requests
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def page_view_event(request):
    origin = request.headers.get('Origin', 'unknown')
    logger.info(f"Cross-domain request from: {origin}")
    
    # ... your view logic
```

## Troubleshooting

### 1. Check CORS Headers

```bash
# Test CORS with curl
curl -H "Origin: https://your-client-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backboneos-domain.com/api/websites/events/page-view/
```

### 2. Browser Console Errors

Common errors and solutions:

- **"CORS policy"** → Check `CORS_ALLOWED_ORIGINS` setting
- **"Credentials"** → Set `CORS_ALLOW_CREDENTIALS = True`
- **"Headers"** → Add required headers to `CORS_ALLOW_HEADERS`
- **"Methods"** → Add required methods to `CORS_ALLOW_METHODS`

### 3. Network Tab Analysis

1. Look for OPTIONS requests (preflight)
2. Check response headers for CORS headers
3. Verify the actual POST request succeeds

## Example Complete Setup

### Server (Django)

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'corsheaders',
    'websites',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Client (External Website)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Client Website</title>
    <script>
        window.BackboneConfig = {
            apiEndpoint: 'https://your-backboneos-domain.com/api/websites/events/page-view/',
            features: {
                pageViews: true,
                clicks: true,
                formSubmissions: true
            }
        };
    </script>
    <script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
</head>
<body>
    <h1>Welcome to Our Website</h1>
    <p>This page is being tracked by BackboneOS!</p>
</body>
</html>
```

This setup ensures that the tracking script can successfully send data from external websites to your BackboneOS server while maintaining security and proper CORS configuration.
