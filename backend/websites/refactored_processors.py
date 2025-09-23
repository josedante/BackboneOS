"""
Refactored page view event processors with improved architecture.

This module contains the refactored logic for processing page view events,
applying lessons learned from PageReadEventProcessor and ClickEventProcessor.
"""

from django.db import transaction
from django.utils import timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging

from interactions.models import Action, Agent, Interaction, Touchpoint, Channel, TouchpointClass, Medium
from .models import WebInteraction, Website, WebAgent, WebSession
from .base_processors import BaseWebEventProcessor

logger = logging.getLogger(__name__)


class RefactoredPageViewEventProcessor(BaseWebEventProcessor):
    """
    Refactored processor for page view events that creates multiple interactions.
    
    This processor implements the multi-interaction approach where a single
    page view event can create up to 3 separate WebInteraction instances:
    1. Page View Interaction (always created)
    2. Referrer Click Interaction (if external referrer exists)
    3. Session Start Interaction (if new session criteria met)
    
    Improvements applied:
    - Inherits from BaseWebEventProcessor (eliminates code duplication)
    - Specific touchpoint creation for each interaction type
    - Proper transaction management
    - Enhanced error handling and logging
    - Consistent channel and medium management
    """
    
    def __init__(self, event_data: Dict[str, Any]):
        """
        Initialize the processor with event data.
        
        Args:
            event_data: Dictionary containing the page view event data
        """
        super().__init__(event_data)
        self.created_interactions = []
        
    @transaction.atomic
    def process(self) -> List[WebInteraction]:
        """
        Process the page view event and create all applicable interactions.
        
        Returns:
            List[WebInteraction]: List of created WebInteraction instances
        """
        try:
            # Check session start criteria BEFORE creating any interactions
            should_start_session = self._should_start_new_session()
            has_external_referrer = self._has_external_referrer()
            
            # Get or create WebSession
            self.web_session = self._get_or_create_session(should_start_session)
            
            # 1. Always create Page View Interaction
            page_view_interaction = self._create_page_view_interaction()
            self.created_interactions.append(page_view_interaction)
            
            # 2. Create Referrer Click Interaction (if external referrer exists)
            if has_external_referrer:
                referrer_click_interaction = self._create_referrer_click_interaction()
                self.created_interactions.append(referrer_click_interaction)
            
            # 3. Create Session Start Interaction (if new session criteria met)
            if should_start_session:
                session_start_interaction = self._create_session_start_interaction()
                self.created_interactions.append(session_start_interaction)
            
            # Update session activity
            self.web_session.update_activity()
            
            logger.info(f"Successfully created {len(self.created_interactions)} interactions for page view event")
            return self.created_interactions
            
        except Exception as e:
            logger.error(f"Error processing page view event: {e}")
            raise
    
    def _has_external_referrer(self) -> bool:
        """Check if there's an external referrer."""
        referrer = self.event_data.get('referrer')
        if not referrer:
            return False
        
        try:
            parsed_referrer = urlparse(referrer)
            referrer_domain = parsed_referrer.netloc.lower()
            
            parsed_website = urlparse(self.website.base_url)
            website_domain = parsed_website.netloc.lower()
            
            # Remove www. prefix for comparison
            if referrer_domain.startswith('www.'):
                referrer_domain = referrer_domain[4:]
            if website_domain.startswith('www.'):
                website_domain = website_domain[4:]
            
            return referrer_domain != website_domain
        except Exception as e:
            logger.warning(f"Error parsing referrer URL {referrer}: {e}")
            return True  # Assume external if we can't parse
    
    def _should_start_new_session(self) -> bool:
        """
        Determine if this should start a new session.
        
        This implements the server-side session inference logic.
        """
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            return True  # No session info = new session
        
        # Check if this is the first interaction for this session
        existing_interactions = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).exists()
        
        if not existing_interactions:
            return True  # First interaction = new session
        
        # Check for session timeout using WebSession.ended_at
        try:
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active:
                return True  # Session expired = new session
        except WebSession.DoesNotExist:
            return True  # No session exists = new session
        
        return False  # Existing active session
    
    def _create_page_view_interaction(self) -> WebInteraction:
        """Create the page view interaction with specific touchpoint."""
        # Create interaction payload with all event data
        interaction_payload = {
            'interaction_type': 'page_view',
            'full_url': self.event_data.get('full_url'),
            'session_id': self.event_data.get('session_id'),
            'visitor_cookie': self.event_data.get('visitor_cookie')
        }
        
        # Add all payload data from event
        event_payload = self.event_data.get('payload', {})
        interaction_payload.update(event_payload)
        
        # Create base interaction
        web_interaction = self._create_base_web_interaction(
            action_code='no_action',
            action_name='Sin Acción',
            action_description='Evento inferido o acción realizada hacia el usuario',
            interaction_type='page_view',
            payload=interaction_payload
        )
        
        # Create specific page view touchpoint
        page_touchpoint = self._create_page_view_touchpoint()
        if page_touchpoint:
            web_interaction.interaction.touchpoint = page_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_referrer_click_interaction(self) -> WebInteraction:
        """Create the referrer click interaction with specific touchpoint."""
        # Create interaction
        interaction = Interaction.objects.create(
            action=Action.objects.get_or_create(
                code='external_click',
                defaults={'name': 'External Click', 'description': 'Click from external source'}
            )[0],
            agent=self._get_or_create_agent(),
            occurred_at=timezone.now(),
            payload={
                'interaction_type': 'referrer_click',
                'referrer_url': self.event_data.get('referrer'),
                'referrer_title': self.event_data.get('payload', {}).get('referrer_title'),
                'referrer_description': self.event_data.get('payload', {}).get('referrer_description'),
                'session_id': self.event_data.get('session_id'),
                'visitor_cookie': self.event_data.get('visitor_cookie')
            }
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        # Create specific referrer click touchpoint
        referrer_touchpoint = self._create_referrer_click_touchpoint()
        if referrer_touchpoint:
            web_interaction.interaction.touchpoint = referrer_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_session_start_interaction(self) -> WebInteraction:
        """Create the session start interaction with specific touchpoint."""
        # Create interaction
        interaction = Interaction.objects.create(
            action=Action.objects.get_or_create(
                code='no_action',
                defaults={'name': 'Sin Acción', 'description': 'Evento inferido o acción realizada hacia el usuario'}
            )[0],
            agent=self._get_or_create_agent(),
            occurred_at=timezone.now(),
            payload={
                'interaction_type': 'session_start',
                'session_start_time': timezone.now().isoformat(),
                'is_new_visitor': not self._has_existing_visitor(),
                'landing_page': True,
                'inference_reason': self._get_session_start_reason(),
                'page_title': self.event_data.get('payload', {}).get('page_title'),
                'full_url': self.event_data.get('full_url'),
                'session_id': self.event_data.get('session_id'),
                'visitor_cookie': self.event_data.get('visitor_cookie')
            }
        )
        
        # Create WebInteraction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id=self.event_data.get('session_id', ''),
            visitor_cookie=self.event_data.get('visitor_cookie', ''),
            user_agent=self.event_data.get('user_agent', ''),
            utm_source=self.event_data.get('utm_source', ''),
            utm_medium=self.event_data.get('utm_medium', ''),
            utm_campaign=self.event_data.get('utm_campaign', ''),
            utm_content=self.event_data.get('utm_content', ''),
            utm_term=self.event_data.get('utm_term', ''),
            element=self.event_data.get('element', ''),
            payload=self.event_data.get('payload', {})
        )
        
        # Create specific session start touchpoint
        session_touchpoint = self._create_session_start_touchpoint()
        if session_touchpoint:
            web_interaction.interaction.touchpoint = session_touchpoint
            web_interaction.interaction.save(update_fields=['touchpoint'])
        
        return web_interaction
    
    def _create_page_view_touchpoint(self) -> Optional[Touchpoint]:
        """Create specific touchpoint for page view interaction."""
        try:
            # Get page data
            payload = self.event_data.get('payload', {})
            page_title = payload.get('page_title', 'Unknown Page')
            page_description = payload.get('page_description', '')
            full_url = self.event_data.get('full_url', '')
            
            # Get channel and medium
            channel, medium = self._get_or_create_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.internal_interaction',
                defaults={'name': 'Internal Web Interaction'}
            )
            
            # Create touchpoint code
            touchpoint_code = f"web.page_view.{page_title.lower().replace(' ', '_').replace('-', '_')}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': page_title,
                    'description': page_description,
                    'url': full_url,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating page view touchpoint: {e}")
            return None
    
    def _create_referrer_click_touchpoint(self) -> Optional[Touchpoint]:
        """Create specific touchpoint for referrer click interaction."""
        try:
            referrer_url = self.event_data.get('referrer', '')
            if not referrer_url:
                return None
            
            # Get channel and medium
            channel, medium = self._get_or_create_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.external_click',
                defaults={'name': 'External Click'}
            )
            
            # Create touchpoint code
            parsed_referrer = urlparse(referrer_url)
            referrer_domain = parsed_referrer.netloc.lower()
            touchpoint_code = f"web.referrer_click.{referrer_domain.replace('.', '_')}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': f"Referrer: {referrer_domain}",
                    'description': f"Click from {referrer_url}",
                    'url': referrer_url,
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating referrer click touchpoint: {e}")
            return None
    
    def _create_session_start_touchpoint(self) -> Optional[Touchpoint]:
        """Create specific touchpoint for session start interaction."""
        try:
            # Get channel and medium
            channel, medium = self._get_or_create_channel_and_medium()
            
            # Get or create touchpoint class
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code='web.session_start',
                defaults={'name': 'Session Start'}
            )
            
            # Create touchpoint code
            session_id = self.event_data.get('session_id', 'unknown')
            touchpoint_code = f"web.session_start.{session_id}"
            
            # Get or create touchpoint
            touchpoint, _ = Touchpoint.objects.get_or_create(
                code=touchpoint_code,
                defaults={
                    'name': f"Session Start: {session_id}",
                    'description': f"Session started with ID {session_id}",
                    'url': self.event_data.get('full_url', ''),
                    'channel': channel,
                    'touchpoint_class': touchpoint_class
                }
            )
            
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error creating session start touchpoint: {e}")
            return None
    
    def _has_existing_visitor(self) -> bool:
        """Check if visitor has existing interactions."""
        visitor_cookie = self.event_data.get('visitor_cookie')
        if not visitor_cookie:
            return False
        
        return WebInteraction.objects.filter(
            visitor_cookie=visitor_cookie
        ).exists()
    
    def _get_session_start_reason(self) -> str:
        """Get the reason for session start inference."""
        session_id = self.event_data.get('session_id')
        visitor_cookie = self.event_data.get('visitor_cookie')
        
        if not session_id or not visitor_cookie:
            return 'no_session_info'
        
        # Check if this is the first interaction for this session
        existing_interactions = WebInteraction.objects.filter(
            session_id=session_id,
            visitor_cookie=visitor_cookie
        ).exists()
        
        if not existing_interactions:
            return 'first_interaction'
        
        # Check for session timeout using WebSession.ended_at
        try:
            session = WebSession.objects.get(session_id=session_id)
            if not session.is_session_active:
                return 'session_timeout'
        except WebSession.DoesNotExist:
            return 'session_timeout'  # No session exists = timeout
        
        return 'unknown'
