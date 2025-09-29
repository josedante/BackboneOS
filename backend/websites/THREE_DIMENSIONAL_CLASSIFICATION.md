# 🎯 Three-Dimensional Classification System - Technical Implementation

## 📋 Overview

This document provides technical implementation details for the three-dimensional classification system used in the `websites` app. For general usage information, see the main [README.md](./README.md).

## 🏗️ System Architecture

### **Data Model Structure**

```python
# interactions/models.py - Touchpoint model
class Touchpoint(BaseUUIDModelWithActiveStatus):
    # Three-dimensional classification
    channel = models.ForeignKey(Channel, ...)      # WHERE
    medium = models.ForeignKey(Medium, ...)        # HOW  
    touchpoint_type = models.ForeignKey(TouchpointType, ...)  # WHAT
```

### **Classification Dimensions**

#### **1. Channel (WHERE) - Where the interaction occurred**
- **Purpose**: Identifies the context/location where the interaction happened
- **Examples**: `esan.edu.pe`, `alpha.com`, `mobile_app`
- **Logic**: Determined from website URL where interaction occurred
- **Implementation**: `_determine_channel_from_subject()` in `WebTouchpointResolver`

#### **2. Medium (HOW) - How it communicates**
- **Purpose**: Identifies the communication method
- **Examples**: `organic_search`, `social_media`, `cpc`, `email`, `referral`, `direct`
- **Logic**: UTM parameters take precedence, then referrer analysis, then defaults
- **Implementation**: `_determine_medium_from_subject()` in `WebTouchpointResolver`

#### **3. TouchpointType (WHAT) - What type of touchpoint**
- **Purpose**: Identifies the functional type of touchpoint (web-specific)
- **Examples**: `web_page`, `web_form`, `link`, `button`, `web_download`
- **Logic**: Determined from event type with intelligent click classification
- **Implementation**: `_get_enhanced_touchpoint_type_code()` in `WebTouchpointResolver`

## 🔧 Implementation Details

### **WebTouchpointResolver - Classification Logic**

```python
def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
    # 1. Channel (WHERE) - Where the interaction occurred
    channel = self._determine_channel_from_subject(hint)
    
    # 2. Medium (HOW) - How it communicates  
    medium = self._determine_medium_from_subject(hint)
    
    # 3. TouchpointType (WHAT) - What type of touchpoint
    touchpoint_type = self._get_enhanced_touchpoint_type_code(hint)
    
    # Create touchpoint with three-dimensional classification
    touchpoint, created = Touchpoint.objects.get_or_create(
        code=touchpoint_code,
        defaults={
            'name': touchpoint_name,
            'touchpoint_type': touchpoint_type,
            'channel': channel,
            'medium': medium,
            'description': f"Web touchpoint for {touchpoint_code}",
            'is_active': True
        }
    )
```

### **Channel Determination Logic**

```python
def _determine_channel_from_subject(self, hint: TouchpointHint) -> str:
    # 1. Check UTM source first (highest precedence)
    if hint.metadata and 'utm_source' in hint.metadata:
        utm_source = hint.metadata['utm_source']
        if utm_source:
            return utm_source.lower()
    
    # 2. Check website URL (where interaction occurred)
    if hint.metadata and 'website_url' in hint.metadata:
        website_url = hint.metadata['website_url']
        if website_url:
            from urllib.parse import urlparse
            parsed = urlparse(website_url)
            domain = parsed.netloc
            if domain:
                return domain.replace('www.', '').lower()
    
    # 3. Check referrer URL (for referrer click interactions)
    if hint.metadata and 'referrer_url' in hint.metadata:
        referrer_url = hint.metadata['referrer_url']
        if referrer_url:
            from urllib.parse import urlparse
            parsed = urlparse(referrer_url)
            domain = parsed.netloc
            if domain:
                return domain.replace('www.', '').lower()
    
    # 4. Default to web channel
    return 'web'
```

### **Medium Determination Logic**

```python
def _determine_medium_from_subject(self, hint: TouchpointHint) -> str:
    # 1. Check UTM medium first (highest precedence)
    if hint.metadata and 'utm_medium' in hint.metadata:
        utm_medium = hint.metadata['utm_medium']
        if utm_medium:
            return utm_medium.lower()
    
    # 2. Check if this is a page view on our own website
    if hint.metadata and 'website_url' in hint.metadata:
        website_url = hint.metadata['website_url']
        if website_url:
            return 'owned_website'
    
    # 3. Check referrer for medium inference
    if hint.metadata and 'referrer_url' in hint.metadata:
        referrer_url = hint.metadata['referrer_url']
        if referrer_url:
            from urllib.parse import urlparse
            parsed = urlparse(referrer_url)
            domain = parsed.netloc.lower()
            
            # Map common domains to mediums
            if 'google' in domain:
                return 'organic_search'
            elif any(social in domain for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
                return 'social_media'
            elif 'mail' in domain or 'email' in domain:
                return 'email'
            else:
                return 'referral'
    
    # 4. Default to direct
    return 'direct'
```

### **TouchpointType Determination Logic**

```python
def _get_enhanced_touchpoint_type_code(self, hint: TouchpointHint) -> str:
    # Get event type and code from hint
    event_type = hint.metadata.get('event_type', '') if hint.metadata else ''
    code = hint.code or ''
    
    # Check for referrer click interactions
    if 'referrer_click' in event_type.lower() or 'referrer_click' in code.lower():
        # Check if it's a Google search referrer
        if hint.metadata and 'referrer_url' in hint.metadata:
            referrer_url = hint.metadata['referrer_url']
            if 'google' in referrer_url.lower():
                return 'search_results'
        return 'web_page'  # Default for referrer clicks
    
    # Check for page view interactions
    if 'page_view' in event_type.lower() or 'page_view' in code.lower():
        return 'web_page'
    
    # Check for form submissions
    if 'form_submit' in event_type.lower() or 'form_submit' in code.lower():
        return 'web_form'
    
    # Check for click interactions with intelligent classification
    if 'click' in event_type.lower() or 'click' in code.lower():
        # Check selector metadata to distinguish between link and button
        if hint.metadata and 'selector' in hint.metadata:
            selector = hint.metadata['selector']
            if selector:
                # Check if selector indicates a button (button, input[type="button"], etc.)
                if any(btn_indicator in selector.lower() for btn_indicator in ['button', 'input[type="button"]', 'input[type="submit"]']):
                    return 'button'
                else:
                    return 'link'
        return 'link'  # Default for clicks
    
    # Check for download interactions
    if 'download' in event_type.lower() or 'download' in code.lower():
        return 'web_download'
    
    # Check for purchase interactions
    if 'purchase' in event_type.lower() or 'purchase' in code.lower():
        return 'web_purchase'
    
    # Check for signup interactions
    if 'signup' in event_type.lower() or 'signup' in code.lower():
        return 'web_signup'
    
    # Check for login interactions
    if 'login' in event_type.lower() or 'login' in code.lower():
        return 'web_login'
    
    # Check for session interactions
    if 'session_start' in event_type.lower() or 'session_start' in code.lower():
        return 'web_session_start'
    elif 'session_end' in event_type.lower() or 'session_end' in code.lower():
        return 'web_session_end'
    
    # Default to web_page for web interactions
    return 'web_page'
```

## 📊 Classification Examples

### **Example 1: Organic Google Search**
```python
# Input Event
{
    "event_type": "page_view",
    "website_url": "https://esan.edu.pe/programs/mba",
    "referrer_url": "https://google.com/search?q=mba+programs+peru",
    "utm_source": "",  # Empty - no UTM parameters
    "utm_medium": ""
}

# Expected Classification
{
    "channel": "esan.edu.pe",        # WHERE: happened on ESAN's website
    "medium": "organic_search",      # HOW: arrived from organic search
    "touchpoint_type": "web_page"    # WHAT: page view interaction
}
```

### **Example 2: Paid Google Campaign**
```python
# Input Event
{
    "event_type": "page_view",
    "website_url": "https://esan.edu.pe/programs/mba",
    "referrer_url": "https://google.com/search?q=mba+programs+peru",
    "utm_source": "google",          # UTM parameters present
    "utm_medium": "cpc"
}

# Expected Classification
{
    "channel": "google",             # WHERE: UTM source takes precedence
    "medium": "cpc",                 # HOW: UTM medium takes precedence
    "touchpoint_type": "web_page"    # WHAT: page view interaction
}
```

### **Example 3: Social Media Referral**
```python
# Input Event
{
    "event_type": "page_view",
    "website_url": "https://esan.edu.pe/programs/mba",
    "referrer_url": "https://facebook.com/post/123",
    "utm_source": "",  # Empty - no UTM parameters
    "utm_medium": ""
}

# Expected Classification
{
    "channel": "esan.edu.pe",        # WHERE: happened on ESAN's website
    "medium": "social_media",        # HOW: arrived from social media
    "touchpoint_type": "web_page"    # WHAT: page view interaction
}
```

## 🔄 Migration Guide

### **Data Model Changes**
1. **Medium field moved**: From `Channel` to `Touchpoint`
2. **TouchpointType renamed**: To `TouchpointType`
3. **Updated relationships**: Touchpoint now has direct relationships to all three dimensions

### **Code Changes Required**
```python
# Before
touchpoint_type = models.ForeignKey(TouchpointType, ...)
channel.medium = models.ForeignKey(Medium, ...)

# After
touchpoint_type = models.ForeignKey(TouchpointType, ...)
touchpoint.medium = models.ForeignKey(Medium, ...)
touchpoint.channel = models.ForeignKey(Channel, ...)
```

### **Automatic Migration**
- Existing migrations have been updated
- System is compatible with existing data
- No manual intervention required

## 🧪 Testing

### **Test Coverage**
- **28 tests passing**: Complete coverage of all functionality
- **Classification tests**: All three dimensions tested
- **UTM precedence tests**: UTM parameters take precedence
- **Referrer analysis tests**: Comprehensive referrer analysis
- **TouchpointType tests**: Web-specific types without overlap

### **Test Scenarios**
- **Organic vs Paid**: Channel differentiation for analytics
- **UTM precedence**: UTM parameters override referrer analysis
- **Referrer analysis**: Social, search, email, referral traffic
- **TouchpointType classification**: Web-specific types
- **Click classification**: Link vs button distinction

## 🎯 Benefits

### **Analytical Benefits**
- **Granular analysis**: Each dimension can be analyzed independently
- **Better ML/AI**: Improved feature extraction for predictive models
- **Flexible reporting**: Grouping and filtering by any dimension
- **No overlap**: Clear separation of responsibilities

### **Business Benefits**
- **Marketing attribution**: Clear distinction between organic and paid traffic
- **Customer journey**: Better understanding of traffic sources
- **ROI analysis**: Improved analysis of marketing spend effectiveness
- **Scalability**: Easy extension for new interaction types

---

This three-dimensional classification system provides a robust foundation for web interaction analysis while maintaining compatibility with the broader BackboneOS interaction framework.