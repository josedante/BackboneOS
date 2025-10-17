#!/usr/bin/env python
"""
Comprehensive Page View Event Tracking Monitor

This script monitors and validates page view events sent to the backend,
tracking all created database objects and validating against expectations.

Usage:
    python test_page_view_tracking.py --wait  # Wait for incoming event
    python test_page_view_tracking.py --inspect  # Inspect last created objects
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.utils import timezone
from interactions.models import (
    Channel, Medium, TouchpointType, Touchpoint, 
    Action, Agent, Interaction
)
from websites.models import Website, WebInteraction, WebSession


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PageViewTracker:
    """Track and validate page view events"""
    
    def __init__(self):
        self.before_state = {}
        self.after_state = {}
        self.created_objects = {}
        self.validation_results = []
        
    def capture_state(self) -> Dict[str, int]:
        """Capture current database state (object counts)"""
        return {
            'websites': Website.objects.count(),
            'channels': Channel.objects.count(),
            'mediums': Medium.objects.count(),
            'touchpoint_types': TouchpointType.objects.count(),
            'touchpoints': Touchpoint.objects.count(),
            'actions': Action.objects.count(),
            'agents': Agent.objects.count(),
            'interactions': Interaction.objects.count(),
            'web_interactions': WebInteraction.objects.count(),
            'web_sessions': WebSession.objects.count(),
        }
    
    def print_header(self, text: str, color: str = Colors.HEADER):
        """Print formatted header"""
        print(f"\n{color}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{color}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{color}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    def print_section(self, text: str):
        """Print section header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─' * 80}{Colors.ENDC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.ENDC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─' * 80}{Colors.ENDC}")
    
    def print_subsection(self, text: str):
        """Print subsection header"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    
    def print_field(self, name: str, value: Any, indent: int = 0):
        """Print field with formatting"""
        indent_str = "  " * indent
        if value is None:
            value_str = f"{Colors.YELLOW}None{Colors.ENDC}"
        elif isinstance(value, bool):
            value_str = f"{Colors.GREEN if value else Colors.RED}{value}{Colors.ENDC}"
        elif isinstance(value, dict):
            value_str = f"{Colors.CYAN}{json.dumps(value, indent=2)}{Colors.ENDC}"
        else:
            value_str = str(value)
        print(f"{indent_str}{Colors.BOLD}{name}:{Colors.ENDC} {value_str}")
    
    def print_validation(self, check: str, passed: bool, message: str = ""):
        """Print validation result"""
        icon = f"{Colors.GREEN}✅{Colors.ENDC}" if passed else f"{Colors.RED}❌{Colors.ENDC}"
        msg = f" - {message}" if message else ""
        print(f"{icon} {check}{msg}")
        self.validation_results.append((check, passed, message))
    
    def get_recent_objects(self, cutoff_time: Optional[datetime] = None) -> Dict[str, List]:
        """Get objects created after cutoff time"""
        if cutoff_time is None:
            cutoff_time = timezone.now() - timedelta(minutes=5)
        
        return {
            'websites': list(Website.objects.filter(created_at__gte=cutoff_time)),
            'channels': list(Channel.objects.filter(created_at__gte=cutoff_time)),
            'mediums': list(Medium.objects.filter(created_at__gte=cutoff_time)),
            'touchpoint_types': list(TouchpointType.objects.filter(created_at__gte=cutoff_time)),
            'touchpoints': list(Touchpoint.objects.filter(created_at__gte=cutoff_time)),
            'actions': list(Action.objects.filter(created_at__gte=cutoff_time)),
            'agents': list(Agent.objects.filter(created_at__gte=cutoff_time)),
            'interactions': list(Interaction.objects.filter(created_at__gte=cutoff_time)),
            'web_interactions': list(WebInteraction.objects.filter(created_at__gte=cutoff_time)),
            'web_sessions': list(WebSession.objects.filter(created_at__gte=cutoff_time)),
        }
    
    def display_website(self, website: Website):
        """Display website details"""
        self.print_subsection(f"Website: {website.name}")
        self.print_field("ID", website.pk, 1)
        self.print_field("Base URL", website.base_url, 1)
        self.print_field("Name", website.name, 1)
        self.print_field("Division", website.division.name if website.division else None, 1)
        self.print_field("Channel", website.channel.code if website.channel else None, 1)
        self.print_field("Active", website.active, 1)
    
    def display_channel(self, channel: Channel):
        """Display channel details"""
        self.print_subsection(f"Channel: {channel.name}")
        self.print_field("ID", channel.pk, 1)
        self.print_field("Code", channel.code, 1)
        self.print_field("Name", channel.name, 1)
        self.print_field("Source Type", channel.source_type, 1)
        self.print_field("Description", channel.description, 1)
    
    def display_medium(self, medium: Medium):
        """Display medium details"""
        self.print_subsection(f"Medium: {medium.name}")
        self.print_field("ID", medium.pk, 1)
        self.print_field("Code", medium.code, 1)
        self.print_field("Name", medium.name, 1)
        self.print_field("Communication Type", medium.communication_type, 1)
        self.print_field("Description", medium.description, 1)
    
    def display_touchpoint_type(self, tp_type: TouchpointType):
        """Display touchpoint type details"""
        self.print_subsection(f"TouchpointType: {tp_type.name}")
        self.print_field("ID", tp_type.pk, 1)
        self.print_field("Code", tp_type.code, 1)
        self.print_field("Name", tp_type.name, 1)
        self.print_field("Description", tp_type.description, 1)
    
    def display_touchpoint(self, touchpoint: Touchpoint):
        """Display touchpoint details"""
        self.print_subsection(f"Touchpoint: {touchpoint.name}")
        self.print_field("ID", touchpoint.pk, 1)
        self.print_field("Code", touchpoint.code, 1)
        self.print_field("Name", touchpoint.name, 1)
        self.print_field("URL", touchpoint.url, 1)
        self.print_field("Channel", f"{touchpoint.channel.code} ({touchpoint.channel.name})" if touchpoint.channel else None, 1)
        self.print_field("Medium", f"{touchpoint.medium.code} ({touchpoint.medium.name})" if touchpoint.medium else None, 1)
        self.print_field("Type", f"{touchpoint.touchpoint_type.code} ({touchpoint.touchpoint_type.name})" if touchpoint.touchpoint_type else None, 1)
        self.print_field("Parent", touchpoint.parent.code if touchpoint.parent else None, 1)
        self.print_field("Description", touchpoint.description, 1)
    
    def display_action(self, action: Action):
        """Display action details"""
        self.print_subsection(f"Action: {action.name}")
        self.print_field("ID", action.pk, 1)
        self.print_field("Code", action.code, 1)
        self.print_field("Name", action.name, 1)
        self.print_field("Description", action.description, 1)
        self.print_field("Action Type", action.action_type.name if action.action_type else None, 1)
    
    def display_agent(self, agent: Agent):
        """Display agent details"""
        self.print_subsection(f"Agent: {agent.name}")
        self.print_field("ID", agent.pk, 1)
        self.print_field("Type", agent.agent_type, 1)
        self.print_field("Name", agent.name, 1)
        self.print_field("Identifier", agent.identifier, 1)
        if agent.metadata:
            self.print_field("User Agent", agent.metadata.get('user_agent', 'N/A'), 1)
    
    def display_interaction(self, interaction: Interaction):
        """Display interaction details"""
        self.print_subsection(f"Interaction: {interaction.pk}")
        self.print_field("ID", interaction.pk, 1)
        self.print_field("Touchpoint", f"{interaction.touchpoint.code} ({interaction.touchpoint.name})" if interaction.touchpoint else None, 1)
        self.print_field("Action", f"{interaction.action.code} ({interaction.action.name})" if interaction.action else None, 1)
        self.print_field("Agent", f"{interaction.agent.agent_type}: {interaction.agent.name}" if interaction.agent else None, 1)
        self.print_field("Occurred At", interaction.occurred_at, 1)
        self.print_field("Session ID", interaction.session_id, 1)
        if interaction.payload:
            self.print_field("Payload", interaction.payload, 1)
    
    def display_web_interaction(self, web_interaction: WebInteraction):
        """Display web interaction details"""
        self.print_subsection(f"WebInteraction: {web_interaction.pk}")
        self.print_field("ID (Interaction FK)", web_interaction.interaction_id, 1)
        self.print_field("Website", web_interaction.website.name, 1)
        self.print_field("Session ID", web_interaction.session_id, 1)
        self.print_field("Visitor Cookie", web_interaction.visitor_cookie, 1)
        self.print_field("User Agent", web_interaction.user_agent[:80] + "..." if len(web_interaction.user_agent) > 80 else web_interaction.user_agent, 1)
        self.print_field("IP", web_interaction.ip, 1)
        self.print_field("UTM Source", web_interaction.utm_source, 1)
        self.print_field("UTM Medium", web_interaction.utm_medium, 1)
        self.print_field("UTM Campaign", web_interaction.utm_campaign, 1)
        self.print_field("Element", web_interaction.element, 1)
        self.print_field("Is Bot", web_interaction.is_bot, 1)
        if web_interaction.payload:
            self.print_field("Payload", web_interaction.payload, 1)
    
    def display_web_session(self, web_session: WebSession):
        """Display web session details"""
        self.print_subsection(f"WebSession: {web_session.session_id}")
        self.print_field("ID", web_session.pk, 1)
        self.print_field("Session ID", web_session.session_id, 1)
        self.print_field("Website", web_session.website.name, 1)
        self.print_field("Visitor Cookie", web_session.visitor_cookie, 1)
        self.print_field("Page Count", web_session.page_count, 1)
        self.print_field("Is Bounce", web_session.is_bounce, 1)
        self.print_field("Started At", web_session.started_at, 1)
        self.print_field("Last Activity At", web_session.last_activity_at, 1)
        self.print_field("UTM Source", web_session.utm_source, 1)
        self.print_field("UTM Medium", web_session.utm_medium, 1)
        self.print_field("UTM Campaign", web_session.utm_campaign, 1)
        self.print_field("Landing Page URL", web_session.landing_page_url, 1)
        self.print_field("Referrer URL", web_session.referrer_url, 1)
    
    def display_state_diff(self):
        """Display before/after state comparison"""
        self.print_section("DATABASE STATE COMPARISON")
        
        print(f"\n{'Model':<25} {'Before':<15} {'After':<15} {'Change':<15}")
        print("─" * 70)
        
        for model_name in self.before_state.keys():
            before = self.before_state[model_name]
            after = self.after_state[model_name]
            change = after - before
            
            change_str = f"{Colors.GREEN}+{change}{Colors.ENDC}" if change > 0 else f"{change}"
            print(f"{model_name:<25} {before:<15} {after:<15} {change_str:<15}")
    
    def validate_expectations(self, objects: Dict[str, List]):
        """Validate created objects against expectations"""
        self.print_section("VALIDATION RESULTS")
        
        # Get the latest web interactions for validation
        web_interactions = objects['web_interactions']
        interactions = objects['interactions']
        
        # Validate interaction count (1-2 expected for landing pages, 1 for regular pages)
        interaction_count = len(interactions)
        expected_interactions = "1-2 (page_view + optional session_start for landing pages)"
        self.print_validation(
            "Interaction count",
            1 <= interaction_count <= 3,
            f"Expected {expected_interactions}, got {interaction_count}"
        )
        
        # Identify interaction types
        interaction_types = [i.action.code for i in interactions if i.action]
        self.print_subsection(f"Created Interaction Types: {', '.join(interaction_types)}")
        
        if not web_interactions:
            self.print_validation("WebInteractions created", False, "No WebInteractions found")
            return
        
        # Get primary web interaction (page_view)
        page_view_interaction = None
        for wi in web_interactions:
            if wi.interaction.action and wi.interaction.action.code == 'page_view':
                page_view_interaction = wi
                break
        
        if not page_view_interaction:
            self.print_validation("Page view interaction", False, "No page_view interaction found")
            return
        
        self.print_validation("Page view interaction created", True)
        
        # Validate touchpoint relationships
        touchpoint = page_view_interaction.interaction.touchpoint
        if touchpoint:
            self.print_validation("Touchpoint assigned", True)
            
            # Validate Channel
            if touchpoint.channel:
                self.print_validation(
                    "Channel created",
                    True,
                    f"Code: {touchpoint.channel.code}, Type: {touchpoint.channel.source_type}"
                )
                self.print_validation(
                    "Channel source_type is 'owned'",
                    touchpoint.channel.source_type == 'owned',
                    f"Expected 'owned', got '{touchpoint.channel.source_type}'"
                )
            else:
                self.print_validation("Channel assigned", False, "No channel on touchpoint")
            
            # Validate Medium
            if touchpoint.medium:
                self.print_validation(
                    "Medium created",
                    True,
                    f"Code: {touchpoint.medium.code}"
                )
                self.print_validation(
                    "Medium is 'web_interaction'",
                    touchpoint.medium.code == 'web_interaction',
                    f"Expected 'web_interaction', got '{touchpoint.medium.code}'"
                )
            else:
                self.print_validation("Medium assigned", False, "No medium on touchpoint")
            
            # Validate TouchpointType
            if touchpoint.touchpoint_type:
                self.print_validation(
                    "TouchpointType created",
                    True,
                    f"Code: {touchpoint.touchpoint_type.code}"
                )
                self.print_validation(
                    "TouchpointType is 'web_page'",
                    touchpoint.touchpoint_type.code == 'web_page',
                    f"Expected 'web_page', got '{touchpoint.touchpoint_type.code}'"
                )
            else:
                self.print_validation("TouchpointType assigned", False, "No touchpoint_type on touchpoint")
            
            # Validate Touchpoint properties
            self.print_validation(
                "Touchpoint code is 'web_page'",
                touchpoint.code == 'web_page',
                f"Expected 'web_page', got '{touchpoint.code}'"
            )
            
            self.print_validation(
                "Touchpoint URL contains localhost:4321",
                'localhost:4321' in touchpoint.url or '127.0.0.1:4321' in touchpoint.url,
                f"URL: {touchpoint.url}"
            )
            
            self.print_validation(
                "Touchpoint has no parent (page-level)",
                touchpoint.parent is None,
                f"Parent: {touchpoint.parent}"
            )
        else:
            self.print_validation("Touchpoint assigned", False, "No touchpoint on interaction")
        
        # Validate Action
        action = page_view_interaction.interaction.action
        if action:
            self.print_validation(
                "Action code is 'page_view'",
                action.code == 'page_view',
                f"Expected 'page_view', got '{action.code}'"
            )
        else:
            self.print_validation("Action assigned", False, "No action on interaction")
        
        # Validate Agent
        agent = page_view_interaction.interaction.agent
        if agent:
            self.print_validation(
                "Agent type is 'browser'",
                agent.agent_type == 'browser',
                f"Expected 'browser', got '{agent.agent_type}'"
            )
            self.print_validation(
                "Agent has user_agent metadata",
                agent.metadata and 'user_agent' in agent.metadata,
                "User agent present" if agent.metadata and 'user_agent' in agent.metadata else "Missing user_agent"
            )
        else:
            self.print_validation("Agent assigned", False, "No agent on interaction")
        
        # Validate WebInteraction data
        self.print_validation(
            "WebInteraction has session_id",
            bool(page_view_interaction.session_id),
            f"Session ID: {page_view_interaction.session_id[:20]}..." if page_view_interaction.session_id else "Missing"
        )
        
        self.print_validation(
            "WebInteraction has visitor_cookie",
            bool(page_view_interaction.visitor_cookie),
            f"Visitor: {page_view_interaction.visitor_cookie[:20]}..." if page_view_interaction.visitor_cookie else "Missing"
        )
        
        self.print_validation(
            "WebInteraction has payload",
            bool(page_view_interaction.payload),
            f"Keys: {list(page_view_interaction.payload.keys())}" if page_view_interaction.payload else "Empty"
        )
        
        # Validate WebSession
        web_sessions = objects['web_sessions']
        if web_sessions:
            web_session = web_sessions[0]
            self.print_validation(
                "WebSession created/updated",
                True,
                f"Session ID: {web_session.session_id}"
            )
            
            # Check if session IDs match
            if page_view_interaction and page_view_interaction.session_id:
                session_ids_match = page_view_interaction.session_id == web_session.session_id
                self.print_validation(
                    "Session IDs match (WebInteraction ↔ WebSession)",
                    session_ids_match,
                    f"WebInteraction: {page_view_interaction.session_id}, WebSession: {web_session.session_id}"
                )
        else:
            self.print_validation("WebSession created", False, "No WebSession found")
    
    def generate_summary(self):
        """Generate final summary"""
        self.print_section("SUMMARY")
        
        passed = sum(1 for _, p, _ in self.validation_results if p)
        total = len(self.validation_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Total Checks:{Colors.ENDC} {total}")
        print(f"{Colors.BOLD}Passed:{Colors.ENDC} {Colors.GREEN}{passed}{Colors.ENDC}")
        print(f"{Colors.BOLD}Failed:{Colors.ENDC} {Colors.RED}{total - passed}{Colors.ENDC}")
        print(f"{Colors.BOLD}Success Rate:{Colors.ENDC} {percentage:.1f}%")
        
        if percentage == 100:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL CHECKS PASSED!{Colors.ENDC}")
        elif percentage >= 80:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  MOSTLY PASSED (Some issues detected){Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.ENDC}")
        
        # Show failed checks
        failed_checks = [(name, msg) for name, passed, msg in self.validation_results if not passed]
        if failed_checks:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Checks:{Colors.ENDC}")
            for name, msg in failed_checks:
                print(f"  ❌ {name}: {msg}")
    
    def run_inspection(self):
        """Inspect recently created objects"""
        self.print_header("PAGE VIEW EVENT INSPECTION")
        
        cutoff = timezone.now() - timedelta(minutes=5)
        print(f"Inspecting objects created in the last 5 minutes (since {cutoff})")
        
        objects = self.get_recent_objects(cutoff)
        
        # Display each type of object
        if objects['websites']:
            self.print_section(f"WEBSITES ({len(objects['websites'])})")
            for obj in objects['websites']:
                self.display_website(obj)
        
        if objects['channels']:
            self.print_section(f"CHANNELS ({len(objects['channels'])})")
            for obj in objects['channels']:
                self.display_channel(obj)
        
        if objects['mediums']:
            self.print_section(f"MEDIUMS ({len(objects['mediums'])})")
            for obj in objects['mediums']:
                self.display_medium(obj)
        
        if objects['touchpoint_types']:
            self.print_section(f"TOUCHPOINT TYPES ({len(objects['touchpoint_types'])})")
            for obj in objects['touchpoint_types']:
                self.display_touchpoint_type(obj)
        
        if objects['touchpoints']:
            self.print_section(f"TOUCHPOINTS ({len(objects['touchpoints'])})")
            for obj in objects['touchpoints']:
                self.display_touchpoint(obj)
        
        if objects['actions']:
            self.print_section(f"ACTIONS ({len(objects['actions'])})")
            for obj in objects['actions']:
                self.display_action(obj)
        
        if objects['agents']:
            self.print_section(f"AGENTS ({len(objects['agents'])})")
            for obj in objects['agents']:
                self.display_agent(obj)
        
        if objects['interactions']:
            self.print_section(f"INTERACTIONS ({len(objects['interactions'])})")
            for obj in objects['interactions']:
                self.display_interaction(obj)
        
        if objects['web_interactions']:
            self.print_section(f"WEB INTERACTIONS ({len(objects['web_interactions'])})")
            for obj in objects['web_interactions']:
                self.display_web_interaction(obj)
        
        if objects['web_sessions']:
            self.print_section(f"WEB SESSIONS ({len(objects['web_sessions'])})")
            for obj in objects['web_sessions']:
                self.display_web_session(obj)
        
        # Validate
        self.validate_expectations(objects)
        self.generate_summary()
    
    def run_monitoring(self):
        """Monitor for new page view events"""
        self.print_header("PAGE VIEW EVENT MONITOR - READY")
        
        print(f"{Colors.YELLOW}Capturing BEFORE state...{Colors.ENDC}")
        self.before_state = self.capture_state()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Ready to track page view events{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Instructions:{Colors.ENDC}")
        print(f"  1. Open your browser to http://localhost:4321/")
        print(f"  2. Wait for page to load (tracking script will fire)")
        print(f"  3. Press ENTER here when ready to inspect results")
        
        input(f"\n{Colors.YELLOW}Press ENTER after you've loaded the page...{Colors.ENDC}")
        
        print(f"\n{Colors.YELLOW}Capturing AFTER state...{Colors.ENDC}")
        self.after_state = self.capture_state()
        
        # Display state diff
        self.display_state_diff()
        
        # Get and display created objects
        cutoff = timezone.now() - timedelta(minutes=2)
        objects = self.get_recent_objects(cutoff)
        
        # Display all created objects
        if objects['websites']:
            self.print_section(f"CREATED WEBSITES ({len(objects['websites'])})")
            for obj in objects['websites']:
                self.display_website(obj)
        
        if objects['channels']:
            self.print_section(f"CREATED CHANNELS ({len(objects['channels'])})")
            for obj in objects['channels']:
                self.display_channel(obj)
        
        if objects['mediums']:
            self.print_section(f"CREATED MEDIUMS ({len(objects['mediums'])})")
            for obj in objects['mediums']:
                self.display_medium(obj)
        
        if objects['touchpoint_types']:
            self.print_section(f"CREATED TOUCHPOINT TYPES ({len(objects['touchpoint_types'])})")
            for obj in objects['touchpoint_types']:
                self.display_touchpoint_type(obj)
        
        if objects['touchpoints']:
            self.print_section(f"CREATED TOUCHPOINTS ({len(objects['touchpoints'])})")
            for obj in objects['touchpoints']:
                self.display_touchpoint(obj)
        
        if objects['actions']:
            self.print_section(f"CREATED ACTIONS ({len(objects['actions'])})")
            for obj in objects['actions']:
                self.display_action(obj)
        
        if objects['agents']:
            self.print_section(f"CREATED AGENTS ({len(objects['agents'])})")
            for obj in objects['agents']:
                self.display_agent(obj)
        
        if objects['interactions']:
            self.print_section(f"CREATED INTERACTIONS ({len(objects['interactions'])})")
            for obj in objects['interactions']:
                self.display_interaction(obj)
        
        if objects['web_interactions']:
            self.print_section(f"CREATED WEB INTERACTIONS ({len(objects['web_interactions'])})")
            for obj in objects['web_interactions']:
                self.display_web_interaction(obj)
        
        if objects['web_sessions']:
            self.print_section(f"CREATED WEB SESSIONS ({len(objects['web_sessions'])})")
            for obj in objects['web_sessions']:
                self.display_web_session(obj)
        
        # Validate results
        self.validate_expectations(objects)
        self.generate_summary()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track and validate page view events')
    parser.add_argument('--wait', action='store_true', help='Wait for incoming event (interactive mode)')
    parser.add_argument('--inspect', action='store_true', help='Inspect recent objects (last 5 minutes)')
    
    args = parser.parse_args()
    
    tracker = PageViewTracker()
    
    if args.inspect:
        tracker.run_inspection()
    elif args.wait:
        tracker.run_monitoring()
    else:
        # Default: run in monitoring mode
        tracker.run_monitoring()


if __name__ == '__main__':
    main()

