# BackboneOS Website Tracking Script

## Overview

The BackboneOS Website Tracking Script is a comprehensive JavaScript solution for capturing website interactions and sending them to the BackboneOS API for attribution tracking and customer journey analysis.

## Features

### 🎯 **Core Tracking**
- **Page Views** - Automatic page view tracking with rich metadata
- **Page Reads** - Engagement tracking based on time, scroll depth, and interactions
- **Click Events** - Detailed click tracking with element information
- **Form Submissions** - Form interaction tracking with field analysis
- **Downloads** - File download tracking with file type detection
- **Video Plays** - Video engagement tracking
- **Search Queries** - Search interaction tracking
- **Newsletter Signups** - Email subscription tracking

### 🔍 **Attribution Tracking**
- **UTM Parameters** - Complete UTM parameter capture and analysis
- **Referrer Analysis** - Cross-domain referrer tracking and analysis
- **Session Management** - Intelligent session detection and management
- **Visitor Tracking** - Long-term visitor identification
- **Bot Detection** - Automatic bot detection and filtering

### 📊 **Engagement Metrics**
- **Time on Page** - Precise time tracking
- **Scroll Depth** - Scroll behavior analysis
- **Word Count** - Content analysis for engagement scoring
- **Interaction Count** - User interaction frequency
- **Viewport Tracking** - Screen size and resolution tracking

## Installation

### Option 1: External Script (Recommended)

```html
<!-- Add to your website's <head> section -->
<script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
```

### Option 2: Inline Script

```html
<!-- Add to your website's <head> section -->
<script>
// Copy the entire backbone-tracker.js content here
</script>
```

### Option 3: Django Template Integration

```html
<!-- In your Django template -->
{% load static %}
<script src="{% static 'websites/js/backbone-tracker.js' %}"></script>
```

## Configuration

### Basic Configuration

```html
<script>
// Configure before loading the script
window.BackboneConfig = {
    apiEndpoint: '/api/websites/events/page-view/',
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    engagementThreshold: 30 * 1000, // 30 seconds
    scrollThreshold: 50, // 50% scroll depth
    features: {
        pageViews: true,
        clicks: true,
        formSubmissions: true,
        downloads: true,
        videoPlays: true,
        searches: true,
        newsletterSignups: true
    }
};
</script>
<script src="backbone-tracker.js"></script>
```

### Advanced Configuration

```javascript
window.BackboneConfig = {
    // API Configuration
    apiEndpoint: '/api/websites/events/page-view/',
    
    // Session Configuration
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    visitorCookieExpiry: 365 * 24 * 60 * 60 * 1000, // 1 year
    
    // Engagement Tracking
    engagementThreshold: 30 * 1000, // 30 seconds
    scrollThreshold: 50, // 50% scroll depth
    wordCountThreshold: 200,
    shortContentThreshold: 10 * 1000, // 10 seconds
    
    // Performance Configuration
    batchSize: 10,
    retryAttempts: 3,
    retryDelay: 1000,
    
    // Privacy Configuration
    privacy: {
        respectDoNotTrack: true,
        anonymizeIP: false,
        gdprCompliant: true,
        cookieConsent: true
    },
    
    // Debug Configuration
    debug: {
        enabled: false,
        logEvents: false,
        logErrors: true,
        verbose: false
    }
};
```

## Usage

### Automatic Tracking

The script automatically tracks the following events:

1. **Page Views** - Triggered on page load
2. **Page Reads** - Triggered when engagement criteria are met
3. **Clicks** - Triggered on any click event
4. **Form Submissions** - Triggered on form submit
5. **Downloads** - Triggered on download link clicks
6. **Video Plays** - Triggered on video play events
7. **Search Queries** - Triggered on search form submissions
8. **Newsletter Signups** - Triggered on newsletter form submissions

### Manual Tracking

You can manually track custom events:

```javascript
// Track a custom event
BackboneTracker.trackCustom('product_view', {
    product_id: '12345',
    product_name: 'Amazing Product',
    category: 'electronics',
    price: 99.99
});

// Track e-commerce events
BackboneTracker.trackCustom('add_to_cart', {
    product_id: '12345',
    quantity: 2,
    value: 199.98
});

// Track conversion events
BackboneTracker.trackCustom('purchase', {
    order_id: 'ORD-12345',
    value: 299.97,
    currency: 'USD',
    items: [
        { product_id: '12345', quantity: 2, price: 99.99 },
        { product_id: '67890', quantity: 1, price: 99.99 }
    ]
});
```

### Session and Visitor Information

```javascript
// Get current session ID
const sessionId = BackboneTracker.getSessionId();

// Get visitor cookie
const visitorId = BackboneTracker.getVisitorCookie();

// Check if user is in a session
if (sessionId) {
    console.log('User is in session:', sessionId);
}
```

## Event Data Structure

### Page View Event

```javascript
{
    event_type: 'page_view',
    website_base: 'https://example.com',
    full_url: 'https://example.com/products/amazing-product',
    referrer: 'https://google.com/search?q=amazing+product',
    session_id: 'sess_abc123def456',
    visitor_cookie: 'visitor_xyz789uvw012',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    utm_source: 'google',
    utm_medium: 'organic',
    utm_campaign: 'product_search',
    utm_content: 'product_page',
    utm_term: 'amazing product',
    element: 'body',
    payload: {
        page_title: 'Amazing Product - Example Store',
        page_description: 'The most amazing product you will ever see',
        page_category: 'products',
        load_time: 1250,
        is_landing_page: false,
        page_depth: 2,
        word_count: 450,
        viewport_size: '1920x1080',
        screen_resolution: '1920x1080',
        language: 'en-US',
        timezone: 'America/New_York'
    }
}
```

### Page Read Event

```javascript
{
    event_type: 'page_read',
    website_base: 'https://example.com',
    full_url: 'https://example.com/products/amazing-product',
    session_id: 'sess_abc123def456',
    visitor_cookie: 'visitor_xyz789uvw012',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    element: 'body',
    payload: {
        page_title: 'Amazing Product - Example Store',
        page_description: 'The most amazing product you will ever see',
        page_category: 'products',
        time_on_page: 45,
        scroll_depth: 75,
        read_criteria_met: 'scroll_depth',
        word_count: 450,
        interactions_count: 3,
        max_scroll_depth: 75
    }
}
```

### Click Event

```javascript
{
    event_type: 'click',
    website_base: 'https://example.com',
    full_url: 'https://example.com/products/amazing-product',
    referrer: 'https://google.com/search?q=amazing+product',
    session_id: 'sess_abc123def456',
    visitor_cookie: 'visitor_xyz789uvw012',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    utm_source: 'google',
    utm_medium: 'organic',
    utm_campaign: 'product_search',
    element: '#add-to-cart-button',
    payload: {
        clicked_element: 'BUTTON',
        element_id: 'add-to-cart-button',
        element_class: 'btn btn-primary',
        click_position: { x: 150, y: 300 },
        target_url: '',
        text_content: 'Add to Cart'
    }
}
```

### Form Submit Event

```javascript
{
    event_type: 'form_submit',
    website_base: 'https://example.com',
    full_url: 'https://example.com/contact',
    referrer: 'https://example.com/about',
    session_id: 'sess_abc123def456',
    visitor_cookie: 'visitor_xyz789uvw012',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    utm_source: 'google',
    utm_medium: 'organic',
    utm_campaign: 'contact_page',
    element: '#contact-form',
    payload: {
        form_id: 'contact-form',
        form_type: 'contact',
        fields_submitted: ['name', 'email', 'message'],
        form_data: {
            name: 'John Doe',
            email: 'john@example.com',
            message: 'I am interested in your product'
        }
    }
}
```

## Integration Examples

### E-commerce Website

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="csrf-token" content="{{ csrf_token }}">
    <script>
        window.BackboneConfig = {
            apiEndpoint: '/api/websites/events/page-view/',
            features: {
                pageViews: true,
                clicks: true,
                formSubmissions: true,
                downloads: true
            }
        };
    </script>
    <script src="backbone-tracker.js"></script>
</head>
<body>
    <!-- Your website content -->
    
    <script>
        // Track product views
        document.addEventListener('DOMContentLoaded', function() {
            const productId = document.querySelector('[data-product-id]')?.dataset.productId;
            if (productId) {
                BackboneTracker.trackCustom('product_view', {
                    product_id: productId,
                    product_name: document.title,
                    category: 'electronics'
                });
            }
        });
        
        // Track add to cart
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', function() {
                BackboneTracker.trackCustom('add_to_cart', {
                    product_id: this.dataset.productId,
                    quantity: 1,
                    value: parseFloat(this.dataset.price)
                });
            });
        });
    </script>
</body>
</html>
```

### Blog Website

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="csrf-token" content="{{ csrf_token }}">
    <script src="backbone-tracker.js"></script>
</head>
<body>
    <article>
        <h1>Amazing Blog Post</h1>
        <p>Content here...</p>
    </article>
    
    <script>
        // Track article engagement
        let articleStartTime = Date.now();
        let maxScrollDepth = 0;
        
        window.addEventListener('scroll', function() {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            maxScrollDepth = Math.max(maxScrollDepth, scrollPercent);
        });
        
        window.addEventListener('beforeunload', function() {
            const timeOnPage = Date.now() - articleStartTime;
            BackboneTracker.trackCustom('article_engagement', {
                article_title: document.title,
                time_on_page: Math.round(timeOnPage / 1000),
                scroll_depth: maxScrollDepth,
                word_count: document.body.textContent.split(/\s+/).length
            });
        });
    </script>
</body>
</html>
```

### Lead Generation Website

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="csrf-token" content="{{ csrf_token }}">
    <script src="backbone-tracker.js"></script>
</head>
<body>
    <form id="lead-form">
        <input type="text" name="name" placeholder="Your Name" required>
        <input type="email" name="email" placeholder="Your Email" required>
        <input type="tel" name="phone" placeholder="Your Phone">
        <button type="submit">Get Free Quote</button>
    </form>
    
    <script>
        // Track lead generation
        document.getElementById('lead-form').addEventListener('submit', function(e) {
            const formData = new FormData(this);
            BackboneTracker.trackCustom('lead_generation', {
                lead_type: 'quote_request',
                source_page: window.location.pathname,
                utm_source: new URLSearchParams(window.location.search).get('utm_source'),
                utm_medium: new URLSearchParams(window.location.search).get('utm_medium'),
                utm_campaign: new URLSearchParams(window.location.search).get('utm_campaign')
            });
        });
    </script>
</body>
</html>
```

## Privacy and Compliance

### GDPR Compliance

```javascript
window.BackboneConfig = {
    privacy: {
        gdprCompliant: true,
        cookieConsent: true,
        respectDoNotTrack: true,
        anonymizeIP: true
    }
};
```

### Cookie Consent Integration

```javascript
// Example integration with cookie consent banner
function initializeTracking() {
    if (hasCookieConsent()) {
        // Load tracking script
        loadScript('backbone-tracker.js');
    }
}

function hasCookieConsent() {
    // Check your cookie consent implementation
    return localStorage.getItem('cookie_consent') === 'accepted';
}
```

## Performance Optimization

### Lazy Loading

```javascript
// Load tracking script only when needed
function loadTrackingScript() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadScript);
    } else {
        loadScript();
    }
}

function loadScript() {
    const script = document.createElement('script');
    script.src = 'backbone-tracker.js';
    script.async = true;
    document.head.appendChild(script);
}
```

### Batch Processing

```javascript
window.BackboneConfig = {
    batchSize: 20, // Process 20 events at once
    retryAttempts: 3,
    retryDelay: 1000
};
```

## Debugging

### Enable Debug Mode

```javascript
window.BackboneConfig = {
    debug: {
        enabled: true,
        logEvents: true,
        logErrors: true,
        verbose: true
    }
};
```

### Manual Event Testing

```javascript
// Test event sending
BackboneTracker.trackCustom('test_event', {
    test_data: 'This is a test event',
    timestamp: new Date().toISOString()
});
```

## Troubleshooting

### Common Issues

1. **Events not being sent**
   - Check API endpoint configuration
   - Verify CSRF token is present
   - Check browser console for errors

2. **Session not persisting**
   - Check cookie settings
   - Verify domain configuration
   - Check for cookie blocking

3. **Performance issues**
   - Reduce batch size
   - Enable lazy loading
   - Check for memory leaks

### Browser Compatibility

- **Modern Browsers**: Chrome 60+, Firefox 55+, Safari 12+, Edge 79+
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Legacy Support**: Internet Explorer 11+ (with polyfills)

## API Reference

### BackboneTracker Methods

```javascript
// Track custom event
BackboneTracker.trackCustom(eventType, data)

// Get session ID
BackboneTracker.getSessionId()

// Get visitor cookie
BackboneTracker.getVisitorCookie()

// Track event (internal method)
BackboneTracker.track(eventData)
```

### Configuration Options

```javascript
window.BackboneConfig = {
    // API Configuration
    apiEndpoint: string,
    
    // Session Configuration
    sessionTimeout: number,
    visitorCookieExpiry: number,
    
    // Engagement Configuration
    engagementThreshold: number,
    scrollThreshold: number,
    wordCountThreshold: number,
    shortContentThreshold: number,
    
    // Performance Configuration
    batchSize: number,
    retryAttempts: number,
    retryDelay: number,
    
    // Feature Toggles
    features: {
        pageViews: boolean,
        pageReads: boolean,
        clicks: boolean,
        formSubmissions: boolean,
        downloads: boolean,
        videoPlays: boolean,
        searches: boolean,
        newsletterSignups: boolean
    },
    
    // Privacy Configuration
    privacy: {
        respectDoNotTrack: boolean,
        anonymizeIP: boolean,
        gdprCompliant: boolean,
        cookieConsent: boolean
    },
    
    // Debug Configuration
    debug: {
        enabled: boolean,
        logEvents: boolean,
        logErrors: boolean,
        verbose: boolean
    }
};
```

## Support

For technical support and questions:

- **Documentation**: [BackboneOS Documentation](https://docs.backboneos.com)
- **API Reference**: [BackboneOS API Docs](https://api.backboneos.com/docs)
- **GitHub Issues**: [BackboneOS GitHub](https://github.com/backboneos/backboneos)
- **Community Forum**: [BackboneOS Community](https://community.backboneos.com)

## License

This tracking script is part of the BackboneOS project and is licensed under the MIT License. See the LICENSE file for details.
