"""
Web touchpoint inference adapters.

This module provides specialized logic for inferring touchpoint hints
from web interactions, including UTM analysis, referrer parsing, and
web-specific event type mapping.
"""

from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from connectors.protocols import TouchpointHint
from .models import WebInteraction


def infer_web_touchpoint_hint(web_interaction: WebInteraction) -> TouchpointHint:
    """
    Infer touchpoint hint from web interaction data.
    
    This is the specialized logic that belongs in the websites app.
    It analyzes the web interaction data to determine what kind of
    touchpoint should be created.
    
    Args:
        web_interaction: The WebInteraction instance to analyze
        
    Returns:
        TouchpointHint: The inferred touchpoint information
    """
    
    # Determine event type and code
    event_type = _determine_event_type(web_interaction)
    code = _map_event_type_to_code(event_type)
    
    # Create human-friendly label
    label = _create_touchpoint_label(event_type, web_interaction)
    
    # Analyze UTM parameters for medium inference
    medium = _analyze_utm_medium(web_interaction)
    
    # Build metadata
    metadata = _build_metadata(web_interaction, event_type)
    
    return TouchpointHint(
        code=code,
        channel_code=None,  # Let the resolver determine the website-specific channel
        medium_code=medium,
        label=label,
        metadata=metadata
    )


def _determine_event_type(web_interaction: WebInteraction) -> str:
    """
    Determine the event type from web interaction data.
    
    Args:
        web_interaction: The WebInteraction instance
        
    Returns:
        str: The determined event type
    """
    # Check if there's an explicit event type in payload
    if web_interaction.payload:
        event_type = web_interaction.payload.get('event_type')
        if event_type:
            return event_type
    
    # Check if there's an event type in metadata
    if hasattr(web_interaction, 'metadata') and web_interaction.metadata:
        event_type = web_interaction.metadata.get('event_type')
        if event_type:
            return event_type
    
    # Check action code from the related interaction
    action_code = web_interaction.action_code
    if action_code:
        # Map common action codes to event types
        action_to_event_map = {
            'session_start': 'session_start',
            'page_view': 'page_view',
            'page_visit': 'page_view',
            'page_read': 'page_read',
            'form_submit': 'form_submit',
            'form_submission': 'form_submit',
            'button_click': 'click',
            'link_click': 'click',
            'download': 'download',
            'video_play': 'video_play',
            'video_start': 'video_play',
            'search': 'search',
            'newsletter_signup': 'newsletter_signup',
            'purchase': 'purchase',
            'scroll': 'scroll',
            'hover': 'hover',
            'focus': 'focus',
        }
        return action_to_event_map.get(action_code, action_code)
    
    # Check element field for clues
    if web_interaction.element:
        element = web_interaction.element.lower()
        if 'form' in element:
            return 'form_submit'
        elif 'button' in element or 'click' in element:
            return 'click'
        elif 'download' in element:
            return 'download'
        elif 'video' in element:
            return 'video_play'
    
    # Default to page view for generic web interactions
    return 'page_view'


def _map_event_type_to_code(event_type: str) -> str:
    """
    Map event type to touchpoint code.
    
    Args:
        event_type: The event type
        
    Returns:
        str: The touchpoint code
    """
    event_code_map = {
        'session_start': 'web.session_start',
        'page_view': 'web.page_view',
        'page_visit': 'web.page_view',
        'page_read': 'web.page_read',
        'referrer_click': 'web.referrer_page',
        'external_click': 'web.referrer_page',
        'form_submit': 'web.form_submit',
        'form_submission': 'web.form_submit',
        'click': 'web.click',
        'button_click': 'web.click',
        'link_click': 'web.click',
        'download': 'web.download',
        'video_play': 'web.video_play',
        'video_start': 'web.video_play',
        'search': 'web.search',
        'newsletter_signup': 'web.newsletter_signup',
        'purchase': 'web.purchase',
        'add_to_cart': 'web.add_to_cart',
        'remove_from_cart': 'web.remove_from_cart',
        'checkout': 'web.checkout',
        'contact_form': 'web.contact_form',
        'lead_form': 'web.lead_form',
        'scroll': 'web.scroll',
        'hover': 'web.hover',
        'focus': 'web.focus',
        'signup': 'web.signup',
        'login': 'web.login',
        'logout': 'web.logout',
    }
    
    return event_code_map.get(event_type, f'web.{event_type}')


def _create_touchpoint_label(event_type: str, web_interaction: WebInteraction) -> str:
    """
    Create a human-friendly label for the touchpoint.
    
    Args:
        event_type: The event type
        web_interaction: The WebInteraction instance
        
    Returns:
        str: The touchpoint label
    """
    label_map = {
        'session_start': 'Web Session Start',
        'page_view': 'Web Page View',
        'page_visit': 'Web Page Visit',
        'page_read': 'Web Page Read',
        'referrer_click': 'Web Referrer Page',
        'external_click': 'Web External Click',
        'form_submit': 'Web Form Submit',
        'form_submission': 'Web Form Submission',
        'click': 'Web Click',
        'button_click': 'Web Button Click',
        'link_click': 'Web Link Click',
        'download': 'Web Download',
        'video_play': 'Web Video Play',
        'video_start': 'Web Video Start',
        'search': 'Web Search',
        'newsletter_signup': 'Web Newsletter Signup',
        'purchase': 'Web Purchase',
        'add_to_cart': 'Web Add to Cart',
        'remove_from_cart': 'Web Remove from Cart',
        'checkout': 'Web Checkout',
        'contact_form': 'Web Contact Form',
        'lead_form': 'Web Lead Form',
        'scroll': 'Web Scroll',
        'hover': 'Web Hover',
        'focus': 'Web Focus',
        'signup': 'Web Signup',
        'login': 'Web Login',
        'logout': 'Web Logout',
    }
    
    base_label = label_map.get(event_type, f'Web {event_type.title()}')
    
    # Add specific context for referrer pages
    if event_type in ['referrer_click', 'external_click']:
        referrer_url = web_interaction.payload.get('referrer_url') if web_interaction.payload else None
        if referrer_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(referrer_url)
                domain = parsed.netloc.lower()
                if domain.startswith('www.'):
                    domain = domain[4:]
                return f"{base_label} - {domain.title()}"
            except:
                pass
    
    # Add website context if available
    if web_interaction.website:
        website_name = web_interaction.website.name
        return f"{base_label} - {website_name}"
    
    return base_label


def _analyze_utm_medium(web_interaction: WebInteraction) -> str:
    """
    Analyze UTM medium parameter.
    
    Args:
        web_interaction: The WebInteraction instance
        
    Returns:
        str: The analyzed medium code
    """
    # Check if this is a click or page read event - these should have web_page medium
    if hasattr(web_interaction, 'interaction') and web_interaction.interaction and web_interaction.interaction.action:
        action_code = web_interaction.interaction.action.code
        if action_code in ['click', 'page_read']:
            return 'web_page'
    
    if not web_interaction.utm_medium:
        return 'web_direct'
    
    utm_medium = web_interaction.utm_medium.lower().strip()
    
    medium_map = {
        'cpc': 'paid',
        'ppc': 'paid',
        'paid': 'paid',
        'paidsearch': 'paid',
        'paid_search': 'paid',
        'email': 'email',
        'newsletter': 'email',
        'mail': 'email',
        'mailing': 'email',
        'social': 'social',
        'facebook': 'social',
        'twitter': 'social',
        'linkedin': 'social',
        'instagram': 'social',
        'tiktok': 'social',
        'youtube': 'social',
        'referral': 'referral',
        'referrer': 'referral',
        'refer': 'referral',
        'organic': 'organic',
        'seo': 'organic',
        'search': 'organic',
        'natural': 'organic',
        'display': 'display',
        'banner': 'display',
        'cpm': 'display',
        'video': 'video',
        'youtube_ads': 'video',
        'video_ads': 'video',
        'mobile': 'mobile',
        'app': 'mobile',
        'mobile_app': 'mobile',
        'affiliate': 'affiliate',
        'partner': 'affiliate',
        'aff': 'affiliate',
        'content': 'content',
        'blog': 'content',
        'article': 'content',
    }
    
    return medium_map.get(utm_medium, utm_medium)


def _analyze_referrer(web_interaction: WebInteraction) -> str:
    """
    Analyze referrer URL to determine medium.
    
    Args:
        web_interaction: The WebInteraction instance
        
    Returns:
        str: The determined medium code
    """
    # Check if there's a referrer URL in payload or metadata
    referrer_url = None
    
    if web_interaction.payload:
        referrer_url = web_interaction.payload.get('referrer_url') or web_interaction.payload.get('referrer')
    
    if not referrer_url and hasattr(web_interaction, 'metadata') and web_interaction.metadata:
        referrer_url = web_interaction.metadata.get('referrer_url') or web_interaction.metadata.get('referrer')
    
    if not referrer_url:
        return 'web_direct'
    
    try:
        parsed = urlparse(referrer_url)
        hostname = parsed.hostname.lower() if parsed.hostname else ''
        
        # Social media domains
        social_domains = [
            'facebook.com', 'fb.com', 'twitter.com', 'x.com', 't.co',
            'linkedin.com', 'instagram.com', 'tiktok.com', 'youtube.com',
            'pinterest.com', 'reddit.com', 'snapchat.com', 'whatsapp.com'
        ]
        
        for domain in social_domains:
            if domain in hostname:
                return 'social'
        
        # Search engines
        search_domains = [
            'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
            'baidu.com', 'yandex.com', 'ask.com', 'aol.com'
        ]
        
        for domain in search_domains:
            if domain in hostname:
                return 'organic'
        
        # Email providers (for email links)
        email_domains = [
            'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
            'mail.yahoo.com', 'mail.google.com'
        ]
        
        for domain in email_domains:
            if domain in hostname:
                return 'email'
        
        # If it's an external referrer, it's referral
        if hostname and not hostname.startswith('localhost') and not hostname.startswith('127.0.0.1'):
            return 'referral'
        
        return 'web_direct'
        
    except Exception:
        return 'unknown'


def _build_metadata(web_interaction: WebInteraction, event_type: str) -> Dict[str, Any]:
    """
    Build metadata dictionary for the touchpoint hint.
    
    Args:
        web_interaction: The WebInteraction instance
        event_type: The determined event type
        
    Returns:
        Dict[str, Any]: The metadata dictionary
    """
    metadata = {
        'event_type': event_type,
        'session_id': web_interaction.session_id,
        'visitor_cookie': web_interaction.visitor_cookie,
        'is_bot': web_interaction.is_bot,
    }
    
    # Add website information
    if web_interaction.website:
        metadata['website_id'] = str(web_interaction.website.id)
        metadata['website_name'] = web_interaction.website.name
        metadata['website_url'] = web_interaction.website.base_url
    
    # Add UTM parameters if available
    utm_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
    for param in utm_params:
        value = getattr(web_interaction, param, None)
        if value:
            metadata[param] = value
    
    # Add element information
    if web_interaction.element:
        metadata['element'] = web_interaction.element
    
    # Add payload data
    if web_interaction.payload:
        metadata['payload'] = web_interaction.payload
    
    # Add user agent
    if web_interaction.user_agent:
        metadata['user_agent'] = web_interaction.user_agent
    
    # Add IP address (if not sensitive)
    if web_interaction.ip:
        metadata['ip_address'] = str(web_interaction.ip)
    
    # Add client hints
    if web_interaction.client_hints:
        metadata['client_hints'] = web_interaction.client_hints
    
    return metadata


def analyze_utm_medium(utm_medium: str) -> str:
    """
    Analyze UTM medium parameter (standalone function for backward compatibility).
    
    Args:
        utm_medium: The UTM medium parameter value
        
    Returns:
        str: The analyzed medium code
    """
    if not utm_medium:
        return 'web_direct'
    
    utm_medium = utm_medium.lower().strip()
    
    medium_map = {
        'cpc': 'paid',
        'ppc': 'paid',
        'paid': 'paid',
        'email': 'email',
        'social': 'social',
        'referral': 'referral',
        'organic': 'organic',
        'seo': 'organic',
    }
    
    return medium_map.get(utm_medium, utm_medium)


def analyze_referrer(referrer_url: str) -> str:
    """
    Analyze referrer URL to determine medium (standalone function for backward compatibility).
    
    Args:
        referrer_url: The referrer URL
        
    Returns:
        str: The determined medium code
    """
    if not referrer_url:
        return 'web_direct'
    
    try:
        parsed = urlparse(referrer_url)
        hostname = parsed.hostname.lower() if parsed.hostname else ''
        
        # Social media domains
        social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'tiktok.com']
        if any(domain in hostname for domain in social_domains):
            return 'social'
        
        # Search engines
        search_domains = ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com']
        if any(domain in hostname for domain in search_domains):
            return 'organic'
        
        # If it's an external referrer, it's referral
        if hostname:
            return 'referral'
        
        return 'web_direct'
    except Exception:
        return 'unknown'
