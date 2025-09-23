# 🎯 Dual Touchpoint Approach - Page View Events

## 📋 Overview

For **Page View Events**, we create **two separate touchpoints** to capture both the destination page and the source that brought the visitor there. This provides complete attribution and journey tracking.

---

## 🔄 Dual Touchpoint Strategy

### **Touchpoint 1: Viewed Page**
- **Purpose**: Track the page being viewed on our website
- **Channel**: Our website domain (e.g., `esan.edu.pe`)
- **Medium**: `direct` (internal page view)
- **TouchpointClass**: `web.internal_interaction`

### **Touchpoint 2: Referrer Page**
- **Purpose**: Track the source that sent the visitor to us
- **Channel**: Source domain (e.g., `google`, `facebook`)
- **Medium**: Inferred from referrer analysis
- **TouchpointClass**: Traffic source classification

---

## 📊 Implementation Details

### **Viewed Page Touchpoint Creation**:

```python
def create_viewed_page_touchpoint(web_interaction):
    """Create touchpoint for the page being viewed"""
    
    # Extract page information
    page_title = web_interaction.payload.get('page_title', '')
    page_description = web_interaction.payload.get('page_description', '')
    page_url = web_interaction.full_url
    
    # Create touchpoint code
    touchpoint_code = f"web.page_view.{slugify(page_title)}"
    
    # Get or create channel (our website)
    website_channel = get_or_create_website_channel(web_interaction.website)
    
    # Get or create touchpoint class
    touchpoint_class = get_or_create_touchpoint_class(
        code='web.internal_interaction',
        name='Internal Website Interaction'
    )
    
    # Create touchpoint
    touchpoint = Touchpoint.objects.get_or_create(
        code=touchpoint_code,
        defaults={
            'name': page_title,
            'description': page_description,
            'url': page_url,
            'touchpoint_class': touchpoint_class,
            'channel': website_channel,
            'is_active': True
        }
    )[0]
    
    return touchpoint
```

### **Referrer Page Touchpoint Creation**:

```python
def create_referrer_page_touchpoint(web_interaction):
    """Create touchpoint for the referrer page"""
    
    if not web_interaction.referrer_url:
        return None
    
    # Analyze referrer
    referrer_info = analyze_referrer(web_interaction.referrer_url)
    
    # Extract referrer information
    referrer_title = web_interaction.payload.get('referrer_title', referrer_info['title'])
    referrer_description = web_interaction.payload.get('referrer_description', referrer_info['description'])
    
    # Create touchpoint code
    touchpoint_code = f"web.referrer_page.{referrer_info['source']}"
    
    # Get or create source channel
    source_channel = get_or_create_source_channel(referrer_info['source'])
    
    # Get or create touchpoint class based on medium
    medium = referrer_info['medium']
    touchpoint_class_code = f"web.{medium}_traffic"
    touchpoint_class = get_or_create_touchpoint_class(
        code=touchpoint_class_code,
        name=f"{medium.title()} Traffic"
    )
    
    # Create touchpoint
    touchpoint = Touchpoint.objects.get_or_create(
        code=touchpoint_code,
        defaults={
            'name': referrer_title,
            'description': referrer_description,
            'url': web_interaction.referrer_url,
            'touchpoint_class': touchpoint_class,
            'channel': source_channel,
            'is_active': True
        }
    )[0]
    
    return touchpoint
```

---

## 🎯 Touchpoint Examples

### **Example 1: Google Search Referrer**

**Page View Event**:
- **Viewed Page**: `https://esan.edu.pe/programs/mba`
- **Referrer**: `https://google.com/search?q=mba+programs+peru`

**Touchpoints Created**:

1. **Viewed Page Touchpoint**:
   - **Code**: `web.page_view.mba_programs_esan_university`
   - **Name**: "MBA Programs - ESAN University"
   - **Description**: "Comprehensive MBA programs designed for working professionals"
   - **Channel**: `esan.edu.pe`
   - **TouchpointClass**: `web.internal_interaction`

2. **Referrer Page Touchpoint**:
   - **Code**: `web.referrer_page.google_search`
   - **Name**: "Google Search Results"
   - **Description**: "Search results for 'MBA programs Peru'"
   - **Channel**: `google`
   - **TouchpointClass**: `web.organic_traffic`

### **Example 2: Facebook Social Referrer**

**Page View Event**:
- **Viewed Page**: `https://esan.edu.pe/contact`
- **Referrer**: `https://facebook.com/esanuniversity/posts/123456`

**Touchpoints Created**:

1. **Viewed Page Touchpoint**:
   - **Code**: `web.page_view.contact_us`
   - **Name**: "Contact Us - ESAN University"
   - **Description**: "Get in touch with our admissions team"
   - **Channel**: `esan.edu.pe`
   - **TouchpointClass**: `web.internal_interaction`

2. **Referrer Page Touchpoint**:
   - **Code**: `web.referrer_page.facebook_post`
   - **Name**: "Facebook Post - ESAN University"
   - **Description**: "Social media post about MBA programs"
   - **Channel**: `facebook`
   - **TouchpointClass**: `web.social_traffic`

### **Example 3: Direct Traffic (No Referrer)**

**Page View Event**:
- **Viewed Page**: `https://esan.edu.pe/`
- **Referrer**: None (direct traffic)

**Touchpoints Created**:

1. **Viewed Page Touchpoint**:
   - **Code**: `web.page_view.homepage`
   - **Name**: "Homepage - ESAN University"
   - **Description**: "Welcome to ESAN University"
   - **Channel**: `esan.edu.pe`
   - **TouchpointClass**: `web.internal_interaction`

2. **Referrer Page Touchpoint**: None (no referrer)

---

## 🔧 JavaScript Implementation

### **Enhanced Page View Tracking**:

```javascript
trackPageView: function() {
  this.pageStartTime = new Date();
  
  // Get page information
  const pageInfo = {
    page_title: document.title,
    page_description: this.getPageDescription(),
    page_category: this.getPageCategory(),
    load_time: this.getLoadTime(),
    is_landing_page: this.isLandingPage(),
    page_depth: this.getPageDepth()
  };
  
  // Get referrer information
  const referrerInfo = this.getReferrerInfo();
  if (referrerInfo) {
    pageInfo.referrer_title = referrerInfo.title;
    pageInfo.referrer_description = referrerInfo.description;
  }
  
  this.track('page_view', pageInfo);
},

getPageDescription: function() {
  // Try to get meta description
  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) {
    return metaDesc.getAttribute('content');
  }
  
  // Fallback to page title
  return document.title;
},

getReferrerInfo: function() {
  const referrer = document.referrer;
  if (!referrer) return null;
  
  try {
    const referrerUrl = new URL(referrer);
    const hostname = referrerUrl.hostname;
    
    // Analyze referrer type
    if (hostname.includes('google.com')) {
      return {
        title: 'Google Search Results',
        description: 'Search results from Google'
      };
    } else if (hostname.includes('facebook.com')) {
      return {
        title: 'Facebook Post',
        description: 'Social media post from Facebook'
      };
    } else if (hostname.includes('linkedin.com')) {
      return {
        title: 'LinkedIn Post',
        description: 'Professional network post from LinkedIn'
      };
    } else {
      return {
        title: `${hostname} Page`,
        description: `Referral from ${hostname}`
      };
    }
  } catch (e) {
    return null;
  }
}
```

---

## 📈 Business Benefits

### **Complete Attribution**:
- **Source Tracking**: Know exactly where visitors came from
- **Page Performance**: Track which pages are most viewed
- **Journey Mapping**: Understand complete user paths

### **Marketing Intelligence**:
- **Referrer Analysis**: Which sources drive most traffic
- **Page Popularity**: Which content resonates most
- **Conversion Paths**: How users navigate through the site

### **Content Optimization**:
- **Page Descriptions**: Rich metadata for each page
- **Referrer Context**: Understanding of user intent
- **Engagement Metrics**: Page view vs. page read ratios

---

## 🚀 Implementation Checklist

- [ ] **Update JavaScript**: Add page description and referrer info extraction
- [ ] **Implement Touchpoint Creation**: Dual touchpoint creation logic
- [ ] **Configure Channels**: Set up website and source channels
- [ ] **Create Touchpoint Classes**: Internal interaction and traffic source classes
- [ ] **Test Referrer Analysis**: Verify referrer detection and classification
- [ ] **Validate Touchpoints**: Ensure both touchpoints are created correctly
- [ ] **Monitor Performance**: Track touchpoint creation performance
- [ ] **Analytics Integration**: Connect to reporting dashboards

This dual touchpoint approach provides complete visibility into both the destination and source of every page view, enabling comprehensive user journey analysis and marketing attribution.
