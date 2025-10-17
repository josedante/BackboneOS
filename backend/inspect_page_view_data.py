#!/usr/bin/env python
"""
Quick inspection script for page view data.

This script provides a quick way to inspect recent WebInteractions
and their related objects without running the full monitoring suite.

Usage:
    python inspect_page_view_data.py [--limit N]
"""

import os
import sys
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from interactions.models import Channel, Medium, TouchpointType, Touchpoint, Interaction
from websites.models import Website, WebInteraction, WebSession


def print_separator(char="=", length=80):
    """Print separator line"""
    print(char * length)


def inspect_recent_data(limit=10):
    """Inspect recent page view data"""
    print_separator()
    print(f" RECENT PAGE VIEW DATA (Last {limit} WebInteractions)".center(80))
    print_separator()
    print()
    
    # Get recent WebInteractions
    web_interactions = WebInteraction.objects.select_related(
        'interaction__touchpoint__channel',
        'interaction__touchpoint__medium',
        'interaction__touchpoint__touchpoint_type',
        'interaction__action',
        'interaction__agent',
        'website'
    ).order_by('-created_at')[:limit]
    
    if not web_interactions:
        print("❌ No WebInteractions found in the database.")
        return
    
    print(f"Found {web_interactions.count()} recent WebInteractions\n")
    
    for idx, wi in enumerate(web_interactions, 1):
        print(f"\n{'─' * 80}")
        print(f"WebInteraction #{idx} (ID: {wi.pk})")
        print(f"{'─' * 80}")
        
        # Basic info
        print(f"\n📅 Created: {wi.created_at}")
        print(f"🌐 Website: {wi.website.name} ({wi.website.base_url})")
        
        # Session info
        if wi.session_id:
            print(f"🔖 Session ID: {wi.session_id[:40]}...")
        if wi.visitor_cookie:
            print(f"🍪 Visitor: {wi.visitor_cookie[:40]}...")
        
        # Interaction details
        interaction = wi.interaction
        if interaction:
            print(f"\n⚡ Action: {interaction.action.code if interaction.action else 'None'}")
            print(f"🤖 Agent: {interaction.agent.agent_type if interaction.agent else 'None'}")
            
            # Touchpoint taxonomy
            touchpoint = interaction.touchpoint
            if touchpoint:
                print(f"\n📍 Touchpoint Taxonomy:")
                print(f"   Code: {touchpoint.code}")
                print(f"   URL: {touchpoint.url}")
                
                if touchpoint.channel:
                    print(f"   ├─ Channel: {touchpoint.channel.code} ({touchpoint.channel.source_type})")
                
                if touchpoint.medium:
                    print(f"   ├─ Medium: {touchpoint.medium.code} ({touchpoint.medium.communication_type})")
                
                if touchpoint.touchpoint_type:
                    print(f"   └─ Type: {touchpoint.touchpoint_type.code}")
                
                if touchpoint.parent:
                    print(f"   Parent: {touchpoint.parent.code}")
        
        # UTM parameters
        if any([wi.utm_source, wi.utm_medium, wi.utm_campaign]):
            print(f"\n🎯 Attribution:")
            if wi.utm_source:
                print(f"   Source: {wi.utm_source}")
            if wi.utm_medium:
                print(f"   Medium: {wi.utm_medium}")
            if wi.utm_campaign:
                print(f"   Campaign: {wi.utm_campaign}")
        
        # Payload preview
        if wi.payload:
            print(f"\n📦 Payload: {list(wi.payload.keys())[:5]}")
            if 'page_title' in wi.payload:
                print(f"   Page Title: {wi.payload['page_title']}")
    
    # WebSession summary
    print(f"\n\n{'═' * 80}")
    print(" RECENT WEB SESSIONS".center(80))
    print(f"{'═' * 80}\n")
    
    sessions = WebSession.objects.select_related('website').order_by('-created_at')[:5]
    
    if sessions:
        print(f"Found {sessions.count()} recent WebSessions\n")
        for idx, session in enumerate(sessions, 1):
            print(f"{idx}. Session: {session.session_id[:40]}...")
            print(f"   Website: {session.website.name}")
            print(f"   Pages: {session.page_count}, Bounce: {session.is_bounce}")
            print(f"   Started: {session.started_at}")
            print(f"   Last Activity: {session.last_activity_at}")
            if session.utm_source:
                print(f"   Attribution: {session.utm_source} / {session.utm_medium}")
            print()
    else:
        print("No WebSessions found.")
    
    # Quick stats
    print(f"\n{'═' * 80}")
    print(" QUICK STATISTICS".center(80))
    print(f"{'═' * 80}\n")
    
    cutoff = timezone.now() - timedelta(hours=24)
    
    stats = {
        'Total Interactions (24h)': Interaction.objects.filter(created_at__gte=cutoff).count(),
        'Total WebInteractions (24h)': WebInteraction.objects.filter(created_at__gte=cutoff).count(),
        'Total Websites': Website.objects.count(),
        'Total Channels': Channel.objects.count(),
        'Total Mediums': Medium.objects.count(),
        'Total TouchpointTypes': TouchpointType.objects.count(),
        'Total Touchpoints': Touchpoint.objects.count(),
    }
    
    for key, value in stats.items():
        print(f"{key:<35} {value:>10}")
    
    print(f"\n{'═' * 80}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inspect recent page view data')
    parser.add_argument('--limit', type=int, default=10, help='Number of recent WebInteractions to display')
    
    args = parser.parse_args()
    
    inspect_recent_data(args.limit)


if __name__ == '__main__':
    main()

