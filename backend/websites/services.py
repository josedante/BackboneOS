from __future__ import annotations

_EVENT_PROCESSORS: dict[str, str] = {
    'page_view': 'process_page_view_event',
    'page_read': 'process_page_read_event',
    'click': 'process_click_event',
    'form_submit': 'process_form_submit_event',
    'download': 'process_download_event',
    'video_play': 'process_video_play_event',
    'search': 'process_search_event',
    'newsletter_signup': 'process_newsletter_signup_event',
}


def process_web_event(event_type: str, data: dict) -> list:
    """Validate the event's domain and dispatch to the appropriate WebInteraction processor.

    Raises PermissionError if the domain is not registered.
    Raises KeyError if event_type is not a known event.
    """
    from .models import Website, WebInteraction
    Website.validate_domain_or_reject(data['website_base'])
    method_name = _EVENT_PROCESSORS[event_type]
    return getattr(WebInteraction, method_name)(data)
