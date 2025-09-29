# BackboneOS Tracking Script Integration Guide

## Quick Start

### 1. Basic Integration

Add this code to your website's `<head>` section:

```html
<!-- Add CSRF token for Django -->
<meta name="csrf-token" content="{{ csrf_token }}">

<!-- Load BackboneOS tracking script -->
<script src="https://your-backboneos-domain.com/static/websites/js/backbone-tracker.min.js"></script>
```

### 2. Advanced Integration

```html
<!-- Configure tracking before loading script -->
<script>
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
<script src="backbone-tracker.min.js"></script>
```

## What Gets Tracked Automatically

### ✅ **Page Views**
- Every page load
- Rich metadata (title, description, category)
- UTM parameters
- Referrer information
- User agent and device info

### ✅ **Engagement Tracking**
- Time on page
- Scroll depth
- Word count analysis
- User interactions
- Page read events

### ✅ **User Interactions**
- Click events
- Form submissions
- Download clicks
- Video plays
- Search queries
- Newsletter signups

### ✅ **Session Management**
- Session detection
- Visitor identification
- Cross-domain tracking
- UTM parameter changes

## Manual Tracking

### Custom Events

```javascript
// Track custom events
BackboneTracker.trackCustom('product_view', {
    product_id: '12345',
    product_name: 'Amazing Product',
    category: 'electronics',
    price: 99.99
});

// E-commerce tracking
BackboneTracker.trackCustom('add_to_cart', {
    product_id: '12345',
    quantity: 2,
    value: 199.98
});

// Conversion tracking
BackboneTracker.trackCustom('purchase', {
    order_id: 'ORD-12345',
    value: 299.97,
    currency: 'USD'
});
```

### Session Information

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

## Configuration Options

### Basic Configuration

```javascript
window.BackboneConfig = {
    // API endpoint
    apiEndpoint: '/api/websites/events/page-view/',
    
    // Session settings
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
    retryDelay: 1000
};
```

### Feature Toggles

```javascript
window.BackboneConfig = {
    features: {
        pageViews: true,        // Track page views
        pageReads: true,        // Track page reads
        clicks: true,           // Track click events
        formSubmissions: true,  // Track form submissions
        downloads: true,        // Track downloads
        videoPlays: true,       // Track video plays
        searches: true,         // Track search queries
        newsletterSignups: true, // Track newsletter signups
        scrollTracking: true,   // Track scroll depth
        timeTracking: true,     // Track time on page
        utmTracking: true,      // Track UTM parameters
        referrerTracking: true, // Track referrers
        botDetection: true,     // Detect and filter bots
        engagementTracking: true // Track engagement metrics
    }
};
```

### Privacy Settings

```javascript
window.BackboneConfig = {
    privacy: {
        respectDoNotTrack: true,  // Respect DNT header
        anonymizeIP: false,    // Anonymize IP addresses
        gdprCompliant: true,      // GDPR compliance mode
        cookieConsent: true       // Require cookie consent
    }
};
```

### Debug Settings

```javascript
window.BackboneConfig = {
    debug: {
        enabled: true,      // Enable debug mode
        logEvents: true,    // Log all events to console
        logErrors: true,    // Log errors to console
        verbose: true       // Verbose logging
    }
};
```

## Integration Examples

### E-commerce Website

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="csrf-token" content="{{ csrf_token }}">
    <script src="backbone-tracker.min.js"></script>
</head>
<body>
    <div class="product">
        <h1>Amazing Product</h1>
        <button onclick="addToCart()">Add to Cart</button>
    </div>
    
    <script>
        function addToCart() {
            // Track add to cart event
            BackboneTracker.trackCustom('add_to_cart', {
                product_id: '12345',
                product_name: 'Amazing Product',
                quantity: 1,
                value: 99.99
            });
            
            // Your add to cart logic here
            console.log('Product added to cart');
        }
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
    <script src="backbone-tracker.min.js"></script>
</head>
<body>
    <article>
        <h1>Blog Post Title</h1>
        <p>Blog content here...</p>
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
    <script src="backbone-tracker.min.js"></script>
</head>
<body>
    <form id="lead-form">
        <input type="text" name="name" placeholder="Your Name" required>
        <input type="email" name="email" placeholder="Your Email" required>
        <button type="submit">Get Free Quote</button>
    </form>
    
    <script>
        document.getElementById('lead-form').addEventListener('submit', function(e) {
            // Track lead generation
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

## Testing

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

### Test Events

```javascript
// Test page view
BackboneTracker.trackCustom('test_page_view', {
    test_data: 'This is a test page view event'
});

// Test custom event
BackboneTracker.trackCustom('test_custom_event', {
    event_name: 'test_event',
    timestamp: new Date().toISOString()
});
```

### Check Console

Open your browser's developer console to see:
- Event tracking logs
- API requests
- Error messages
- Debug information

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

## Support

For technical support:

- **Documentation**: [BackboneOS Documentation](https://docs.backboneos.com)
- **API Reference**: [BackboneOS API Docs](https://api.backboneos.com/docs)
- **GitHub Issues**: [BackboneOS GitHub](https://github.com/backboneos/backboneos)
- **Community Forum**: [BackboneOS Community](https://community.backboneos.com)

## License

This tracking script is part of the BackboneOS project and is licensed under the MIT License.
