/**
 * BackboneOS Website Tracker
 * 
 * This script captures website interactions and sends them to the BackboneOS API
 * for comprehensive attribution tracking and customer journey analysis.
 * 
 * Features:
 * - Page view tracking with multi-interaction approach
 * - User agent parsing and bot detection
 * - UTM parameter tracking
 * - Session management
 * - Engagement tracking (scroll depth, time on page)
 * - Form submission tracking
 * - Click event tracking
 * - Download tracking
 * - Video play tracking
 * - Search tracking
 * - Newsletter signup tracking
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        baseApiEndpoint: 'https://your-backboneos-domain.com/api/websites/events/',
        sessionTimeout: 30 * 60 * 1000, // 30 minutes
        engagementThreshold: 30 * 1000, // 30 seconds
        scrollThreshold: 50, // 50% scroll depth
        wordCountThreshold: 200,
        shortContentThreshold: 10 * 1000, // 10 seconds
        retryAttempts: 3,
        retryDelay: 1000
    };

    // Global state
    let sessionId = null;
    let visitorCookie = null;
    let pageStartTime = null;
    let scrollDepth = 0;
    let maxScrollDepth = 0;
    let engagementTimer = null;
    let hasUserInteraction = false;
    let interactionCount = 0;

    /**
     * Initialize the BackboneOS tracker
     */
    function init() {
        try {
            // Initialize session and visitor tracking
            initializeSession();
            initializeVisitor();
            
            // Track page view
            trackPageView();
            
            // Setup engagement tracking
            setupEngagementTracking();
            
            // Setup event listeners
            setupEventListeners();
            
            console.log('BackboneOS Tracker initialized successfully');
        } catch (error) {
            console.error('BackboneOS Tracker initialization failed:', error);
        }
    }

    /**
     * Initialize session tracking
     */
    function initializeSession() {
        // Check for existing session
        const existingSession = getCookie('backbone_session_id');
        const lastActivity = getCookie('backbone_last_activity');
        
        const now = Date.now();
        const sessionTimeout = CONFIG.sessionTimeout;
        
        // Create new session if:
        // - No existing session
        // - Session expired (30+ minutes gap)
        // - Cross-domain referrer
        // - UTM parameter change
        if (!existingSession || 
            !lastActivity || 
            (now - parseInt(lastActivity)) > sessionTimeout ||
            hasCrossDomainReferrer() ||
            hasUTMChange()) {
            
            sessionId = generateSessionId();
            setCookie('backbone_session_id', sessionId, 24 * 60 * 60 * 1000); // 24 hours
        } else {
            sessionId = existingSession;
        }
        
        // Update last activity
        setCookie('backbone_last_activity', now.toString(), 24 * 60 * 60 * 1000);
    }

    /**
     * Initialize visitor tracking
     */
    function initializeVisitor() {
        visitorCookie = getCookie('backbone_visitor_id');
        
        if (!visitorCookie) {
            visitorCookie = generateVisitorId();
            setCookie('backbone_visitor_id', visitorCookie, 365 * 24 * 60 * 60 * 1000); // 1 year
        }
    }

    /**
     * Track page view event
     */
    function trackPageView() {
        pageStartTime = Date.now();
        
        const eventData = {
            event_type: 'page_view',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            utm_source: getUrlParam('utm_source'),
            utm_medium: getUrlParam('utm_medium'),
            utm_campaign: getUrlParam('utm_campaign'),
            utm_content: getUrlParam('utm_content'),
            utm_term: getUrlParam('utm_term'),
            element: 'body',
            payload: {
                page_title: document.title,
                page_description: getMetaContent('description'),
                page_category: getPageCategory(),
                load_time: getLoadTime(),
                is_landing_page: isLandingPage(),
                page_depth: getPageDepth(),
                referrer_title: getReferrerTitle(),
                referrer_description: getReferrerDescription(),
                word_count: getWordCount(),
                viewport_size: getViewportSize(),
                screen_resolution: getScreenResolution(),
                language: navigator.language,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }
        };

        sendEvent(eventData);
    }

    /**
     * Setup engagement tracking
     */
    function setupEngagementTracking() {
        // Track scroll depth
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(updateScrollDepth, 100);
        });
        
        // Track time on page
        engagementTimer = setInterval(checkEngagement, 5000);
        
        // Track user interactions
        document.addEventListener('click', function(e) {
            hasUserInteraction = true;
            interactionCount++;
            trackClick(e);
        });
        
        document.addEventListener('focus', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                hasUserInteraction = true;
                interactionCount++;
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', function(e) {
            hasUserInteraction = true;
            trackFormSubmit(e);
        });
        
        // Track downloads
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' && isDownloadLink(e.target)) {
                trackDownload(e.target);
            }
        });
        
        // Track video plays
        document.addEventListener('play', function(e) {
            if (e.target.tagName === 'VIDEO') {
                trackVideoPlay(e.target);
            }
        });
        
        // Track search
        document.addEventListener('submit', function(e) {
            if (isSearchForm(e.target)) {
                trackSearch(e.target);
            }
        });
    }

    /**
     * Setup event listeners for various interactions
     */
    function setupEventListeners() {
        // Track newsletter signups
        document.addEventListener('submit', function(e) {
            if (isNewsletterForm(e.target)) {
                trackNewsletterSignup(e.target);
            }
        });
        
        // Track page visibility changes
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                trackPageVisibilityChange('hidden');
            } else {
                trackPageVisibilityChange('visible');
            }
        });
        
        // Track beforeunload
        window.addEventListener('beforeunload', function() {
            trackPageUnload();
        });
    }


    /**
     * Update scroll depth
     */
    function updateScrollDepth() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = Math.round((scrollTop / documentHeight) * 100);
        
        scrollDepth = Math.max(scrollDepth, scrollPercent);
        maxScrollDepth = Math.max(maxScrollDepth, scrollPercent);
    }

    /**
     * Check engagement criteria
     */
    function checkEngagement() {
        const timeOnPage = Date.now() - pageStartTime;
        const wordCount = getWordCount();
        
        // Check if page read criteria is met
        if (shouldTrackPageRead(timeOnPage, maxScrollDepth, wordCount)) {
            trackPageRead(timeOnPage, maxScrollDepth, wordCount);
            clearInterval(engagementTimer);
        }
    }

    /**
     * Determine if page read should be tracked
     */
    function shouldTrackPageRead(timeOnPage, scrollDepth, wordCount) {
        return (
            timeOnPage >= CONFIG.engagementThreshold || // 30+ seconds
            scrollDepth >= CONFIG.scrollThreshold || // 50%+ scroll
            hasUserInteraction || // Any interaction
            (wordCount < CONFIG.wordCountThreshold && timeOnPage >= CONFIG.shortContentThreshold) // Short content, 10+ seconds
        );
    }

    /**
     * Track page read event
     */
    function trackPageRead(timeOnPage, scrollDepth, wordCount) {
        const eventData = {
            event_type: 'page_read',
            website_base: window.location.origin,
            full_url: window.location.href,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            element: 'body',
            payload: {
                page_title: document.title,
                page_description: getMetaContent('description'),
                page_category: getPageCategory(),
                time_on_page: Math.round(timeOnPage / 1000),
                scroll_depth: scrollDepth,
                read_criteria_met: getReadCriteriaMet(timeOnPage, scrollDepth, wordCount),
                word_count: wordCount,
                interactions_count: interactionCount,
                max_scroll_depth: maxScrollDepth
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track click events
     */
    function trackClick(event) {
        const eventData = {
            event_type: 'click',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            utm_source: getUrlParam('utm_source'),
            utm_medium: getUrlParam('utm_medium'),
            utm_campaign: getUrlParam('utm_campaign'),
            element: getElementSelector(event.target),
            payload: {
                clicked_element: event.target.tagName,
                element_id: event.target.id || '',
                element_class: event.target.className || '',
                click_position: {
                    x: event.clientX,
                    y: event.clientY
                },
                target_url: event.target.href || '',
                text_content: event.target.textContent?.substring(0, 100) || ''
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track form submissions
     */
    function trackFormSubmit(event) {
        const form = event.target;
        const eventData = {
            event_type: 'form_submit',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            utm_source: getUrlParam('utm_source'),
            utm_medium: getUrlParam('utm_medium'),
            utm_campaign: getUrlParam('utm_campaign'),
            element: getElementSelector(form),
            payload: {
                form_id: form.id || '',
                form_type: getFormType(form),
                fields_submitted: getFormFields(form),
                form_data: getFormData(form)
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track downloads
     */
    function trackDownload(link) {
        const eventData = {
            event_type: 'download',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            utm_source: getUrlParam('utm_source'),
            utm_medium: getUrlParam('utm_medium'),
            utm_campaign: getUrlParam('utm_campaign'),
            element: getElementSelector(link),
            payload: {
                file_name: getFileName(link.href),
                file_type: getFileType(link.href),
                file_size: 'unknown',
                download_url: link.href
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track video plays
     */
    function trackVideoPlay(video) {
        const eventData = {
            event_type: 'video_play',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            element: getElementSelector(video),
            payload: {
                video_id: video.id || '',
                video_title: video.title || '',
                video_duration: video.duration || 0,
                video_source: video.src || '',
                play_position: video.currentTime || 0
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track search events
     */
    function trackSearch(form) {
        const searchInput = form.querySelector('input[type="search"], input[name*="search"], input[name*="query"]');
        if (!searchInput) return;

        const eventData = {
            event_type: 'search',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            element: getElementSelector(form),
            payload: {
                search_query: searchInput.value,
                search_results_count: 'unknown',
                search_category: getSearchCategory(form),
                filters_applied: getSearchFilters(form)
            }
        };

        sendEvent(eventData);
    }

    /**
     * Track newsletter signups
     */
    function trackNewsletterSignup(form) {
        const emailInput = form.querySelector('input[type="email"]');
        if (!emailInput) return;

        const eventData = {
            event_type: 'newsletter_signup',
            website_base: window.location.origin,
            full_url: window.location.href,
            referrer: document.referrer,
            session_id: sessionId,
            visitor_cookie: visitorCookie,
            user_agent: navigator.userAgent,
            utm_source: getUrlParam('utm_source'),
            utm_medium: getUrlParam('utm_medium'),
            utm_campaign: getUrlParam('utm_campaign'),
            element: getElementSelector(form),
            payload: {
                email: emailInput.value,
                newsletter_type: getNewsletterType(form),
                interests: getNewsletterInterests(form),
                source_page: window.location.pathname
            }
        };

        sendEvent(eventData);
    }

    /**
     * Send event to API immediately
     */
    function sendEvent(eventData) {
        const eventType = eventData.event_type;
        const endpoint = getEndpointForEventType(eventType);
        
        sendEventToAPI(endpoint, eventData);
    }

    /**
     * Get the appropriate endpoint for an event type
     */
    function getEndpointForEventType(eventType) {
        const eventTypeMap = {
            'page_view': 'page-view/',
            'page_read': 'page-read/',
            'click': 'click/',
            'form_submit': 'form-submit/',
            'download': 'download/',
            'video_play': 'video-play/',
            'search': 'search/',
            'newsletter_signup': 'newsletter-signup/'
        };
        
        const endpoint = eventTypeMap[eventType];
        if (!endpoint) {
            console.warn(`Unknown event type: ${eventType}, using page-view endpoint`);
            return CONFIG.baseApiEndpoint + 'page-view/';
        }
        
        return CONFIG.baseApiEndpoint + endpoint;
    }

    /**
     * Send event to API with retry logic
     */
    function sendEventToAPI(endpoint, eventData, attempt = 1) {
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(eventData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('BackboneOS event sent successfully:', data);
        })
        .catch(error => {
            console.error('BackboneOS event failed:', error);
            
            // Retry if attempts remaining
            if (attempt < CONFIG.retryAttempts) {
                setTimeout(() => {
                    sendEventToAPI(endpoint, eventData, attempt + 1);
                }, CONFIG.retryDelay * attempt);
            }
        });
    }

    // Utility functions
    function generateSessionId() {
        return 'sess_' + Math.random().toString(36).substr(2, 16);
    }

    function generateVisitorId() {
        return 'visitor_' + Math.random().toString(36).substr(2, 16);
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function setCookie(name, value, maxAge) {
        document.cookie = `${name}=${value}; max-age=${maxAge}; path=/; SameSite=Lax`;
    }

    function getUrlParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param) || '';
    }

    function getMetaContent(name) {
        const meta = document.querySelector(`meta[name="${name}"]`);
        return meta ? meta.content : '';
    }

    function getPageCategory() {
        // Try to determine page category from URL path
        const path = window.location.pathname.toLowerCase();
        if (path.includes('/blog/') || path.includes('/news/')) return 'blog';
        if (path.includes('/products/') || path.includes('/services/')) return 'products';
        if (path.includes('/about/') || path.includes('/company/')) return 'about';
        if (path.includes('/contact/') || path.includes('/support/')) return 'contact';
        if (path.includes('/pricing/') || path.includes('/plans/')) return 'pricing';
        return 'other';
    }

    function getLoadTime() {
        return Math.round(performance.now());
    }

    function isLandingPage() {
        return document.referrer === '' || 
               !document.referrer.includes(window.location.hostname);
    }

    function getPageDepth() {
        return window.location.pathname.split('/').filter(segment => segment).length;
    }

    function getReferrerTitle() {
        // This would need to be implemented with server-side referrer analysis
        return '';
    }

    function getReferrerDescription() {
        // This would need to be implemented with server-side referrer analysis
        return '';
    }

    function getWordCount() {
        const text = document.body.textContent || '';
        return text.split(/\s+/).filter(word => word.length > 0).length;
    }

    function getViewportSize() {
        return `${window.innerWidth}x${window.innerHeight}`;
    }

    function getScreenResolution() {
        return `${screen.width}x${screen.height}`;
    }

    function hasCrossDomainReferrer() {
        if (!document.referrer) return false;
        try {
            const referrerHost = new URL(document.referrer).hostname;
            return referrerHost !== window.location.hostname;
        } catch {
            return false;
        }
    }

    function hasUTMChange() {
        // Check if UTM parameters have changed from previous page
        const currentUTM = getUrlParam('utm_source') + getUrlParam('utm_medium') + getUrlParam('utm_campaign');
        const storedUTM = getCookie('backbone_utm_params');
        setCookie('backbone_utm_params', currentUTM, 24 * 60 * 60 * 1000);
        return currentUTM !== storedUTM;
    }

    function getReadCriteriaMet(timeOnPage, scrollDepth, wordCount) {
        if (timeOnPage >= CONFIG.engagementThreshold) return 'time_on_page';
        if (scrollDepth >= CONFIG.scrollThreshold) return 'scroll_depth';
        if (hasUserInteraction) return 'user_interaction';
        if (wordCount < CONFIG.wordCountThreshold && timeOnPage >= CONFIG.shortContentThreshold) return 'short_content';
        return 'none';
    }

    function getElementSelector(element) {
        if (element.id) return `#${element.id}`;
        if (element.className) return `.${element.className.split(' ')[0]}`;
        return element.tagName.toLowerCase();
    }

    function isDownloadLink(link) {
        const href = link.href.toLowerCase();
        const downloadExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.tar', '.gz'];
        return downloadExtensions.some(ext => href.includes(ext)) || link.hasAttribute('download');
    }

    function isSearchForm(form) {
        const searchInputs = form.querySelectorAll('input[type="search"], input[name*="search"], input[name*="query"]');
        return searchInputs.length > 0;
    }

    function isNewsletterForm(form) {
        const emailInputs = form.querySelectorAll('input[type="email"]');
        const newsletterKeywords = ['newsletter', 'subscribe', 'signup', 'email'];
        const formText = form.textContent.toLowerCase();
        return emailInputs.length > 0 && newsletterKeywords.some(keyword => formText.includes(keyword));
    }

    function getFormType(form) {
        const formText = form.textContent.toLowerCase();
        if (formText.includes('contact')) return 'contact';
        if (formText.includes('newsletter') || formText.includes('subscribe')) return 'newsletter';
        if (formText.includes('signup') || formText.includes('register')) return 'signup';
        if (formText.includes('login')) return 'login';
        return 'general';
    }

    function getFormFields(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        return Array.from(inputs).map(input => input.name || input.id || input.type).filter(Boolean);
    }

    function getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    }

    function getFileName(url) {
        return url.split('/').pop().split('?')[0];
    }

    function getFileType(url) {
        const extension = url.split('.').pop().split('?')[0].toLowerCase();
        return extension;
    }

    function getSearchCategory(form) {
        // Try to determine search category from form context
        const formText = form.textContent.toLowerCase();
        if (formText.includes('product')) return 'products';
        if (formText.includes('service')) return 'services';
        if (formText.includes('blog') || formText.includes('article')) return 'content';
        return 'general';
    }

    function getSearchFilters(form) {
        // Extract any applied filters from the form
        const filters = [];
        const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
        const selects = form.querySelectorAll('select');
        
        checkboxes.forEach(cb => {
            if (cb.name) filters.push(`${cb.name}:${cb.value}`);
        });
        
        selects.forEach(select => {
            if (select.name && select.value) filters.push(`${select.name}:${select.value}`);
        });
        
        return filters;
    }

    function getNewsletterType(form) {
        const formText = form.textContent.toLowerCase();
        if (formText.includes('marketing')) return 'marketing';
        if (formText.includes('news')) return 'news';
        if (formText.includes('updates')) return 'updates';
        return 'general';
    }

    function getNewsletterInterests(form) {
        const interests = [];
        const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach(cb => {
            if (cb.name && cb.name.includes('interest')) {
                interests.push(cb.value);
            }
        });
        return interests;
    }

    function getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.content : '';
    }

    function trackPageVisibilityChange(state) {
        // Track when user switches tabs or minimizes browser
        console.log('Page visibility changed to:', state);
    }

    function trackPageUnload() {
        // Track page unload for session management
        const timeOnPage = Date.now() - pageStartTime;
        console.log('Page unload - time on page:', timeOnPage);
    }

    // Initialize tracker when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose tracker to global scope for manual tracking
    window.BackboneTracker = {
        track: sendEvent,
        trackCustom: function(eventType, data) {
            const eventData = {
                event_type: eventType,
                website_base: window.location.origin,
                full_url: window.location.href,
                session_id: sessionId,
                visitor_cookie: visitorCookie,
                user_agent: navigator.userAgent,
                payload: data
            };
            sendEvent(eventData);
        },
        getSessionId: function() { return sessionId; },
        getVisitorCookie: function() { return visitorCookie; }
    };

})();
