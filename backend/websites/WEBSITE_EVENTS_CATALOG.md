# 🌐 Website Events Catalog - BackboneOS

## 📋 Overview

This document catalogs all the events that will be captured by the tracking script in your organization's websites, the data that will be sent to BackboneOS, and the expected effects/interactions and touchpoints that will be created.

## 🎯 Purpose

The website tracking system serves as a bridge between your organization's websites and the BackboneOS CRM, automatically capturing user interactions and converting them into structured touchpoints and interactions for analysis, lead generation, and customer journey mapping.

---

## 🏷️ Action Type Categorization

All website events are categorized by **Action Type** for better analytics and reporting:

### **Digital Actions** (`action_type: "digital"`)
- `click` - User clicks on elements
- `page_view` - User views pages  
- `form_submit` - User submits forms
- `page_read` - User meaningfully engages with content

### **Phone Actions** (`action_type: "telefonica"`)
- `incoming_call` - User calls the organization

### **In-Person Actions** (`action_type: "presencial"`)
- `event_attended` - User attends events

### **System Actions** (`action_type: null`)
- `no_action` - Inferred events (session start, email sent, etc.)

This categorization enables:
- **Channel-specific analytics** (digital vs. phone vs. in-person)
- **Reporting by interaction type**
- **Business intelligence** by communication channel

---

## ✅ Implementation Status

### **Completed Features**
- ✅ **PageViewEventProcessor** - Multi-interaction approach (3 independent interactions)
- ✅ **PageReadEventProcessor** - Engagement-focused single interaction
- ✅ **Action Type Categorization** - Digital, phone, in-person, system actions
- ✅ **User Agent Parsing** - ua-parser-python integration
- ✅ **WebSession Model** - Explicit session tracking
- ✅ **WebAgent Proxy Model** - Website-specific agent functionality
- ✅ **Touchpoint Resolution** - Automatic touchpoint and class creation
- ✅ **Comprehensive Testing** - 20 test cases covering all scenarios

### **Test Coverage**
- **PageViewEventProcessor**: 11 test cases
- **PageReadEventProcessor**: 9 test cases
- **Total**: 20 passing tests
- **Scenarios**: New visitors, returning visitors, external referrers, session inference, error handling

### **Production Ready**
- ✅ All tests passing
- ✅ Error handling implemented
- ✅ Data validation in place
- ✅ Performance optimized
- ✅ Documentation complete

---

## 📊 Event Types Catalog

### 1. **Page View Events**

#### **Event Code**: `web.page_view`
- **Description**: Captures when a user loads a page (basic page load event)
- **Trigger**: Page load, navigation, or page visibility change
- **Data Sent**:
  ```json
  {
    "event_type": "page_view",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://google.com/search?q=mba+programs",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "utm_source": "google",
    "utm_medium": "organic",
    "utm_campaign": "mba_search",
    "utm_content": "programs_page",
    "utm_term": "mba programs",
    "element": "body",
    "payload": {
      "page_title": "MBA Programs - ESAN University",
      "page_description": "Comprehensive MBA programs designed for working professionals seeking to advance their careers",
      "page_category": "academic_programs",
      "load_time": 1.2,
      "is_landing_page": false,
      "page_depth": 2,
      "referrer_title": "Google Search Results",
      "referrer_description": "Search results for 'MBA programs Peru'"
    }
  }
  ```

#### **Expected Effects**:
**Two Touchpoints Created:**

1. **Viewed Page Touchpoint**:
   - **Touchpoint Code**: `web.page_view` (e.g., `web.page_view.mba_programs`)
   - **Channel**: `esan.edu.pe` (capture channel - our website)
   - **Medium**: `direct` (internal page view)
   - **TouchpointType**: `web.internal_interaction`
   - **Description**: Page title and description from website script
   - **URL**: Full URL of the viewed page

2. **Referrer Page Touchpoint** (if external referrer exists):
   - **Touchpoint Code**: `web.referrer_page` (e.g., `web.referrer_page.google_search`)
   - **Channel**: `google` (source channel - where visitor came from)
   - **Medium**: `organic` (from referrer analysis)
   - **TouchpointType**: `web.organic_traffic`
   - **Description**: Referrer page title/description
   - **URL**: Referrer URL

**Up to 3 Interactions Created**:

1. **Page View Interaction**:
   - **Action**: `no_action` (action_type: null - inferred event)
   - **Touchpoint**: Viewed page touchpoint
   - **Purpose**: Track the page being viewed

2. **Referrer Click Interaction** (if external referrer exists):
   - **Action**: `click` (action_type: "digital")
   - **Touchpoint**: Referrer page touchpoint
   - **Purpose**: Track the click that brought visitor to our site

3. **Session Start Interaction** (if new session criteria met):
   - **Action**: `no_action` (action_type: null - inferred event)
   - **Touchpoint**: Viewed page touchpoint (landing page)
   - **Purpose**: Track the beginning of a new session

**Usage**: Complete attribution tracking with separate interactions for page view, referrer click, and session start

---

### 2. **Page Read Events**

#### **Event Code**: `web.page_read`
- **Description**: Captures when a user meaningfully engages with a page (meets read criteria)
- **Trigger**: Page meets engagement criteria (time on page, scroll depth, interaction)
- **Read Criteria**: 
  - Time on page ≥ 30 seconds, OR
  - Scroll depth ≥ 50%, OR
  - User interaction (click, form focus, video play), OR
  - Page contains < 200 words and time ≥ 10 seconds
- **Prerequisites**: Requires a previous page view event in the same session
- **Data Sent**:
  ```json
  {
    "event_type": "page_read",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "element": "body",
    "payload": {
      "page_title": "MBA Programs - ESAN University",
      "page_description": "Comprehensive MBA programs designed for working professionals",
      "page_category": "academic_programs",
      "time_on_page": 45,
      "scroll_depth": 75,
      "read_criteria_met": "scroll_depth",
      "word_count": 1200,
      "interactions_count": 3
    }
  }
  ```

#### **Expected Effects**:
- **Single Interaction Created**: `page_read` action (no UTM fields)
- **Touchpoint Created**: `web.page_read.{page_title}` with `web_page` medium
- **Channel**: Website domain (e.g., `esan.edu.pe`)
- **TouchpointType**: `web.internal_interaction`
- **Session Activity**: Updates session last activity timestamp
- **Content Analysis**: High engagement indicator for content performance

---

### 3. **Form Submission Events**

#### **Event Code**: `web.form_submit`
- **Description**: Captures when a user submits a form (contact, lead generation, application)
- **Trigger**: Form submission, button click on form
- **Data Sent**:
  ```json
  {
    "event_type": "form_submit",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/contact",
    "referrer": "https://esan.edu.pe/programs/mba",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "utm_source": "facebook",
    "utm_medium": "social",
    "utm_campaign": "mba_lead_gen",
    "element": "form#contact-form",
    "payload": {
      "form_id": "contact-form",
      "form_type": "contact",
      "fields_submitted": ["name", "email", "phone", "interest"],
      "form_data": {
        "name": "Juan Pérez",
        "email": "juan@email.com",
        "interest": "MBA Program"
      }
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.lead_form` or `web.contact_form`
- **Channel**: `facebook` (source) or `esan.edu.pe` (capture)
- **Medium**: `social`
- **TouchpointType**: `web.social_traffic`
- **Interaction**: Form submission with lead data
- **Lead Creation**: Potential lead record if email/contact info provided

---

### 4. **Internal Click Events**

#### **Event Code**: `web.click`
- **Description**: Captures user clicks on buttons, links, CTAs
- **Trigger**: Click on interactive elements
- **Data Sent**:
  ```json
  {
    "event_type": "click",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://esan.edu.pe/",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "element": "button#apply-now",
    "payload": {
      "clicked_element": "Apply Now Button",
      "element_id": "apply-now",
      "element_class": "cta-button primary",
      "click_position": {"x": 150, "y": 300},
      "target_url": "https://esan.edu.pe/apply/mba"
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.click`
- **Channel**: `esan.edu.pe` (internal click)
- **Medium**: `direct` (internal navigation)
- **TouchpointType**: `web.internal_traffic`
- **Interaction**: Click interaction with element details

---

### 5. **Download Events**

#### **Event Code**: `web.download`
- **Description**: Captures when users download files (brochures, applications, documents)
- **Trigger**: File download initiation
- **Data Sent**:
  ```json
  {
    "event_type": "download",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://esan.edu.pe/programs/mba",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "utm_source": "email",
    "utm_medium": "email",
    "utm_campaign": "mba_newsletter",
    "element": "a#brochure-download",
    "payload": {
      "file_name": "MBA_Program_Brochure_2024.pdf",
      "file_type": "pdf",
      "file_size": "2.5MB",
      "download_url": "https://esan.edu.pe/downloads/mba-brochure.pdf"
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.download`
- **Channel**: `email` (source) or `esan.edu.pe` (capture)
- **Medium**: `email`
- **TouchpointType**: `web.email_traffic`
- **Interaction**: Download interaction with file details
- **Engagement Score**: High engagement indicator

---

### 6. **Video Play Events**

#### **Event Code**: `web.video_play`
- **Description**: Captures when users start playing videos
- **Trigger**: Video play button click or autoplay
- **Data Sent**:
  ```json
  {
    "event_type": "video_play",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/programs/mba",
    "referrer": "https://esan.edu.pe/",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "element": "video#mba-intro-video",
    "payload": {
      "video_id": "mba-intro-video",
      "video_title": "MBA Program Introduction",
      "video_duration": 180,
      "video_source": "youtube",
      "play_position": 0
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.video_play`
- **Channel**: `esan.edu.pe`
- **Medium**: `direct`
- **TouchpointType**: `web.internal_interaction`
- **Interaction**: Video engagement with content details
- **Engagement Score**: High engagement indicator

---

### 7. **Search Events**

#### **Event Code**: `web.search`
- **Description**: Captures internal website searches
- **Trigger**: Search form submission or search API calls
- **Data Sent**:
  ```json
  {
    "event_type": "search",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/search",
    "referrer": "https://esan.edu.pe/",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "element": "form#search-form",
    "payload": {
      "search_query": "executive education",
      "search_results_count": 12,
      "search_category": "programs",
      "filters_applied": ["type:executive", "location:lima"]
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.search`
- **Channel**: `esan.edu.pe`
- **Medium**: `direct`
- **TouchpointType**: `web.internal_interaction`
- **Interaction**: Search interaction with query details
- **Intent Analysis**: Search terms for content optimization

---

### 8. **Newsletter Signup Events**

#### **Event Code**: `web.newsletter_signup`
- **Description**: Captures newsletter or email list subscriptions
- **Trigger**: Newsletter form submission
- **Data Sent**:
  ```json
  {
    "event_type": "newsletter_signup",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/newsletter",
    "referrer": "https://esan.edu.pe/blog",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "utm_source": "blog",
    "utm_medium": "content",
    "utm_campaign": "newsletter_promotion",
    "element": "form#newsletter-signup",
    "payload": {
      "email": "juan@email.com",
      "newsletter_type": "academic_updates",
      "interests": ["mba", "executive_education"],
      "source_page": "blog"
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.newsletter_signup`
- **Channel**: `blog` (source) or `esan.edu.pe` (capture)
- **Medium**: `content`
- **TouchpointType**: `web.content_traffic`
- **Interaction**: Newsletter signup with contact details
- **Lead Creation**: Email subscriber record
- **Marketing List**: Addition to newsletter distribution list

---

### 9. **E-commerce Events** (if applicable)

#### **Event Code**: `web.purchase`
- **Description**: Captures purchase completions
- **Trigger**: Order confirmation or payment success
- **Data Sent**:
  ```json
  {
    "event_type": "purchase",
    "website_base": "https://esan.edu.pe",
    "full_url": "https://esan.edu.pe/checkout/success",
    "referrer": "https://esan.edu.pe/checkout",
    "session_id": "sess_abc123",
    "visitor_cookie": "visitor_xyz789",
    "user_agent": "Mozilla/5.0...",
    "utm_source": "google",
    "utm_medium": "paid",
    "utm_campaign": "mba_application_fee",
    "element": "div#order-confirmation",
    "payload": {
      "order_id": "ORD-2024-001",
      "total_amount": 150.00,
      "currency": "USD",
      "items": [
        {
          "product": "MBA Application Fee",
          "quantity": 1,
          "price": 150.00
        }
      ],
      "payment_method": "credit_card"
    }
  }
  ```

#### **Expected Effects**:
- **Touchpoint Created**: `web.purchase`
- **Channel**: `google` (source) or `esan.edu.pe` (capture)
- **Medium**: `paid`
- **TouchpointType**: `web.paid_traffic`
- **Interaction**: Purchase interaction with transaction details
- **Revenue Tracking**: Revenue attribution to marketing campaigns
- **Customer Status**: Potential customer conversion

---

## 🔄 Server-Inferred Events

### **Session Start Events** (Not Website Events)

**Session Start** events are **not captured by the website tracking script**. Instead, they are **server-inferred** from page view patterns:

#### **Inference Logic**:
- **New Visitor**: First page view from a new visitor cookie
- **Session Timeout**: Gap > 30 minutes between page views from same visitor  
- **Cross-Domain Referrer**: Page view with external referrer domain
- **UTM Parameter Change**: Page view with different UTM parameters than previous
- **Device/Browser Change**: Page view with different user agent than previous
- **Manual Session Reset**: Page view after logout/login indicators

#### **Event Code**: `web.session_start`
#### **Expected Effects**:
- **Touchpoint Created**: `web.session_start`
- **Channel**: Source channel (e.g., `google`) or capture channel (e.g., `esan.edu.pe`)
- **Medium**: Inferred from UTM or referrer analysis
- **TouchpointType**: Traffic source classification (e.g., `web.organic_traffic`)
- **Interaction**: Session start interaction with visitor classification
- **Session Tracking**: Establishes session context for subsequent events

---

## 🔄 Data Flow Architecture

### 1. **Event Capture Flow**
```
Website User Action → JavaScript Tracker → API Endpoint → WebInteraction Model → Touchpoint Resolution → Interaction Creation
```

### 2. **Touchpoint Resolution Process**
```
WebInteraction → infer_touchpoint_hint() → WebTouchpointResolver → Touchpoint Creation → Interaction Assignment
```

### 3. **Channel and Medium Analysis**
```
UTM Parameters → Medium Classification → Channel Assignment → TouchpointType Creation
```

### 4. **Session and Engagement Tracking**
```
Session Start → Page Views → Engagement Criteria → Page Read Events → User Journey Mapping
```

---

## 🎯 Expected Interactions and Touchpoints

### **Touchpoint Classes Created**:

1. **`web.social_traffic`** - Social media traffic
2. **`web.organic_traffic`** - Organic search traffic  
3. **`web.paid_traffic`** - Paid advertising traffic
4. **`web.email_traffic`** - Email/Newsletter traffic
5. **`web.referral_traffic`** - Referral traffic
6. **`web.direct_traffic`** - Direct traffic
7. **`web.internal_traffic`** - Internal website traffic
8. **`web.internal_interaction`** - Internal website interactions
9. **`web.mobile_traffic`** - Mobile app traffic
10. **`web.app_traffic`** - Native app traffic
11. **`web.display_traffic`** - Display advertising traffic
12. **`web.video_traffic`** - Video advertising traffic
13. **`web.affiliate_traffic`** - Affiliate traffic
14. **`web.content_traffic`** - Content marketing traffic

### **Channels Created**:

- **Source Channels**: `google`, `facebook`, `twitter`, `linkedin`, `email`, `substack`, etc.
- **Capture Channels**: `esan.edu.pe`, `ue.edu.pe`, `esanuniversity.pe`, etc.

### **Interactions Created**:

Each event creates an `Interaction` record with:
- **Person/Organization**: If identifiable from form data
- **Touchpoint**: Automatically resolved touchpoint
- **Action**: Corresponding action (session_start, page_view, page_read, form_submit, click, etc.)
- **Agent**: Browser/device information
- **Payload**: Event-specific data
- **Metadata**: UTM parameters, referrer, session info

---

## 📈 Business Value

### **Lead Generation**:
- Form submissions create lead records
- Email signups build marketing lists
- Download events indicate high engagement

### **Customer Journey Mapping**:
- Track user progression through website
- Identify high-value touchpoints
- Measure conversion funnels
- Session-based journey analysis

### **Marketing Attribution**:
- UTM parameter tracking
- Campaign performance measurement
- Channel effectiveness analysis
- Session-level attribution

### **Content Optimization**:
- Page view vs. page read analytics
- Search query analysis
- Video engagement metrics
- Engagement scoring

### **Sales Intelligence**:
- Purchase event tracking
- Revenue attribution
- Customer behavior patterns
- Session quality scoring

---

## 🔧 Implementation Requirements

### **JavaScript Tracking Script**:
```javascript
// Simplified tracking implementation - server infers session starts
window.BackboneTracker = {
  sessionId: null,
  pageStartTime: null,
  scrollDepth: 0,
  engagementTimer: null,
  
  init: function() {
    // Simple initialization - server will infer session starts
    this.sessionId = this.getOrCreateSessionId();
    this.trackPageView();
    this.setupEngagementTracking();
  },
  
  trackPageView: function() {
    this.pageStartTime = new Date();
    this.track('page_view', {
      page_title: document.title,
      page_category: this.getPageCategory(),
      load_time: this.getLoadTime(),
      is_landing_page: this.isLandingPage(),
      page_depth: this.getPageDepth()
    });
  },
  
  setupEngagementTracking: function() {
    // Track scroll depth
    window.addEventListener('scroll', this.throttle(() => {
      this.scrollDepth = Math.max(this.scrollDepth, this.getScrollDepth());
    }, 100));
    
    // Track time on page
    this.engagementTimer = setInterval(() => {
      this.checkEngagementCriteria();
    }, 5000);
    
    // Track interactions
    document.addEventListener('click', (e) => {
      this.trackClick(e);
    });
  },
  
  checkEngagementCriteria: function() {
    const timeOnPage = (new Date() - this.pageStartTime) / 1000;
    const wordCount = this.getWordCount();
    
    // Check if page read criteria is met
    if (this.shouldTrackPageRead(timeOnPage, this.scrollDepth, wordCount)) {
      this.trackPageRead(timeOnPage, this.scrollDepth, wordCount);
    }
  },
  
  shouldTrackPageRead: function(timeOnPage, scrollDepth, wordCount) {
    return (
      timeOnPage >= 30 || // 30+ seconds
      scrollDepth >= 50 || // 50%+ scroll
      this.hasUserInteraction() || // Any interaction
      (wordCount < 200 && timeOnPage >= 10) // Short content, 10+ seconds
    );
  },
  
  trackPageRead: function(timeOnPage, scrollDepth, wordCount) {
    this.track('page_read', {
      time_on_page: timeOnPage,
      scroll_depth: scrollDepth,
      read_criteria_met: this.getReadCriteriaMet(timeOnPage, scrollDepth, wordCount),
      word_count: wordCount,
      interactions_count: this.getInteractionCount()
    });
  },
  
  track: function(eventType, data) {
    fetch('/api/websites/events/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        event_type: eventType,
        website_base: window.location.origin,
        full_url: window.location.href,
        referrer: document.referrer,
        session_id: this.sessionId,
        visitor_cookie: this.getVisitorCookie(),
        user_agent: navigator.userAgent,
        utm_source: this.getUrlParam('utm_source'),
        utm_medium: this.getUrlParam('utm_medium'),
        utm_campaign: this.getUrlParam('utm_campaign'),
        utm_content: this.getUrlParam('utm_content'),
        utm_term: this.getUrlParam('utm_term'),
        element: data.element || '',
        payload: data.payload || {}
      })
    });
  }
};

// Initialize tracker when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  BackboneTracker.init();
});
```

### **API Endpoint**:
- **URL**: `/api/websites/events/`
- **Method**: `POST`
- **Authentication**: CSRF token required
- **Rate Limiting**: Implemented to prevent abuse

### **Database Schema**:
- **WebInteraction**: Stores web-specific event data
- **Interaction**: Core interaction record
- **Touchpoint**: Automatically resolved touchpoint
- **TouchpointType**: Traffic source classification
- **Channel**: Source and capture channels

---

## 🚀 Next Steps

1. **Deploy Tracking Script**: Implement JavaScript tracker with session and engagement tracking
2. **Configure UTM Parameters**: Set up campaign tracking
3. **Test Event Capture**: Verify all event types are captured correctly
4. **Monitor Performance**: Track system performance and data quality
5. **Analytics Dashboard**: Build reporting interface for captured data
6. **Lead Management**: Integrate with CRM lead management workflows
7. **Session Analytics**: Implement session-based journey analysis

---

## 📊 Success Metrics

- **Event Capture Rate**: % of user actions captured
- **Touchpoint Resolution**: % of events with resolved touchpoints
- **Lead Generation**: Number of leads created from form submissions
- **Attribution Accuracy**: % of traffic properly attributed to sources
- **System Performance**: API response times and error rates
- **Engagement Quality**: Page read vs. page view ratios
- **Session Quality**: Average session duration and engagement

This comprehensive event catalog ensures that your organization's websites will provide rich, actionable data to BackboneOS, enabling better customer understanding, improved marketing attribution, and enhanced lead generation capabilities with proper differentiation between page views, meaningful page reads, and session tracking.
