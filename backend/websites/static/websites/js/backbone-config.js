/**
 * BackboneOS Tracker Configuration
 * 
 * This file contains the configuration options for the BackboneOS tracking script.
 * You can customize these settings to match your tracking requirements.
 */

window.BackboneConfig = {
    // API Configuration
    apiEndpoint: '/api/websites/events/page-view/',
    
    // Session Configuration
    sessionTimeout: 30 * 60 * 1000, // 30 minutes in milliseconds
    visitorCookieExpiry: 365 * 24 * 60 * 60 * 1000, // 1 year in milliseconds
    
    // Engagement Tracking
    engagementThreshold: 30 * 1000, // 30 seconds in milliseconds
    scrollThreshold: 50, // 50% scroll depth
    wordCountThreshold: 200, // Minimum words for content analysis
    shortContentThreshold: 10 * 1000, // 10 seconds for short content
    
    // Performance Configuration
    batchSize: 10, // Number of events to batch together
    retryAttempts: 3, // Number of retry attempts for failed requests
    retryDelay: 1000, // Base delay between retries in milliseconds
    
    // Tracking Features (enable/disable specific tracking)
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
    
    // Custom Event Types
    customEvents: {
        // Add your custom event types here
        // Example:
        // 'product_view': true,
        // 'add_to_cart': true,
        // 'checkout_start': true,
        // 'purchase': true
    },
    
    // Page Categories (customize based on your site structure)
    pageCategories: {
        '/blog/': 'blog',
        '/news/': 'news',
        '/products/': 'products',
        '/services/': 'services',
        '/about/': 'about',
        '/company/': 'about',
        '/contact/': 'contact',
        '/support/': 'contact',
        '/pricing/': 'pricing',
        '/plans/': 'pricing',
        '/help/': 'support',
        '/faq/': 'support'
    },
    
    // Form Types (customize based on your forms)
    formTypes: {
        contact: ['contact', 'inquiry', 'message'],
        newsletter: ['newsletter', 'subscribe', 'email'],
        signup: ['signup', 'register', 'join'],
        login: ['login', 'signin', 'auth'],
        search: ['search', 'query', 'find']
    },
    
    // Download File Types
    downloadExtensions: [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.ppt', '.pptx', '.zip', '.rar', '.tar', 
        '.gz', '.mp4', '.avi', '.mov', '.mp3', 
        '.wav', '.jpg', '.png', '.gif', '.svg'
    ],
    
    // Social Media Domains
    socialDomains: [
        'facebook.com', 'twitter.com', 'linkedin.com',
        'instagram.com', 'youtube.com', 'tiktok.com',
        'pinterest.com', 'reddit.com', 'snapchat.com'
    ],
    
    // Search Engine Domains
    searchEngines: [
        'google.com', 'bing.com', 'yahoo.com',
        'duckduckgo.com', 'baidu.com', 'yandex.com'
    ],
    
    // Email Service Domains
    emailServices: [
        'gmail.com', 'outlook.com', 'yahoo.com',
        'hotmail.com', 'icloud.com', 'aol.com'
    ],
    
    // Bot User Agent Patterns
    botPatterns: [
        'googlebot', 'bingbot', 'slurp', 'duckduckbot',
        'baiduspider', 'yandexbot', 'facebookexternalhit',
        'twitterbot', 'linkedinbot', 'whatsapp',
        'telegrambot', 'applebot', 'crawler', 'spider'
    ],
    
    // Debug Configuration
    debug: {
        enabled: false, // Set to true for development
        logEvents: false, // Log all events to console
        logErrors: true, // Log errors to console
        verbose: false // Verbose logging
    },
    
    // Privacy Configuration
    privacy: {
        respectDoNotTrack: true, // Respect DNT header
        anonymizeIP: false, // Anonymize IP addresses
        dataRetention: 365, // Data retention in days
        gdprCompliant: true, // GDPR compliance mode
        cookieConsent: true // Require cookie consent
    },
    
    // Performance Configuration
    performance: {
        lazyLoad: true, // Lazy load tracking script
        deferExecution: true, // Defer script execution
        minifyOutput: false, // Minify output in production
        compressionEnabled: true // Enable gzip compression
    }
};

/**
 * Custom Configuration Override
 * 
 * You can override any configuration by setting window.BackboneConfig
 * before the tracking script loads:
 * 
 * <script>
 * window.BackboneConfig = {
 *     apiEndpoint: '/custom/api/endpoint/',
 *     sessionTimeout: 60 * 60 * 1000, // 1 hour
 *     features: {
 *         pageViews: true,
 *         clicks: false,
 *         formSubmissions: true
 *     }
 * };
 * </script>
 * <script src="backbone-tracker.js"></script>
 */
