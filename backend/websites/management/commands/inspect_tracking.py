"""
Django management command to inspect page view tracking data.

Usage:
    python manage.py inspect_tracking
    python manage.py inspect_tracking --limit 20
    python manage.py inspect_tracking --session SESSION_ID
    python manage.py inspect_tracking --url "http://localhost:4321/"
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from interactions.models import (
    Channel, Medium, TouchpointType, Touchpoint,
    Action, Agent, Interaction
)
from websites.models import Website, WebInteraction, WebSession


class Command(BaseCommand):
    help = 'Inspect page view tracking data and validate taxonomy'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of recent WebInteractions to display'
        )
        parser.add_argument(
            '--session',
            type=str,
            help='Filter by session ID'
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Filter by URL (contains)'
        )
        parser.add_argument(
            '--stats-only',
            action='store_true',
            help='Show only statistics'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        session_id = options['session']
        url_filter = options['url']
        stats_only = options['stats_only']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(' PAGE VIEW TRACKING INSPECTION '.center(80)))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        if not stats_only:
            self._display_interactions(limit, session_id, url_filter)
        
        self._display_statistics()
        self._validate_taxonomy()
    
    def _display_interactions(self, limit, session_id, url_filter):
        """Display recent web interactions"""
        self.stdout.write(self.style.HTTP_INFO('─' * 80))
        self.stdout.write(self.style.HTTP_INFO(' RECENT WEB INTERACTIONS'))
        self.stdout.write(self.style.HTTP_INFO('─' * 80))
        self.stdout.write('')
        
        # Build query
        query = WebInteraction.objects.select_related(
            'interaction__touchpoint__channel',
            'interaction__touchpoint__medium',
            'interaction__touchpoint__touchpoint_type',
            'interaction__touchpoint__parent',
            'interaction__action',
            'interaction__agent',
            'website'
        ).order_by('-created_at')
        
        # Apply filters
        if session_id:
            query = query.filter(session_id=session_id)
        if url_filter:
            query = query.filter(interaction__touchpoint__url__icontains=url_filter)
        
        web_interactions = query[:limit]
        
        if not web_interactions:
            self.stdout.write(self.style.WARNING('No WebInteractions found'))
            return
        
        for idx, wi in enumerate(web_interactions, 1):
            self._display_interaction_detail(idx, wi)
    
    def _display_interaction_detail(self, idx, wi):
        """Display details for a single interaction"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'WebInteraction #{idx}'))
        self.stdout.write(f'ID: {wi.pk}')
        self.stdout.write(f'Created: {wi.created_at}')
        self.stdout.write(f'Website: {wi.website.name} ({wi.website.base_url})')
        
        if wi.session_id:
            self.stdout.write(f'Session: {wi.session_id[:40]}...')
        if wi.visitor_cookie:
            self.stdout.write(f'Visitor: {wi.visitor_cookie[:40]}...')
        
        # Interaction details
        interaction = wi.interaction
        if interaction:
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('Interaction Details:'))
            
            if interaction.action:
                self.stdout.write(f'  Action: {interaction.action.code} ({interaction.action.name})')
            
            if interaction.agent:
                self.stdout.write(f'  Agent: {interaction.agent.agent_type} - {interaction.agent.name[:50]}')
            
            # Touchpoint taxonomy
            touchpoint = interaction.touchpoint
            if touchpoint:
                self.stdout.write('')
                self.stdout.write(self.style.HTTP_INFO('Touchpoint Taxonomy:'))
                self.stdout.write(f'  Code: {touchpoint.code}')
                self.stdout.write(f'  Name: {touchpoint.name}')
                self.stdout.write(f'  URL: {touchpoint.url}')
                
                if touchpoint.channel:
                    self.stdout.write(
                        f'  Channel: {touchpoint.channel.code} '
                        f'({touchpoint.channel.name}, {touchpoint.channel.source_type})'
                    )
                
                if touchpoint.medium:
                    self.stdout.write(
                        f'  Medium: {touchpoint.medium.code} '
                        f'({touchpoint.medium.name}, {touchpoint.medium.communication_type})'
                    )
                
                if touchpoint.touchpoint_type:
                    self.stdout.write(
                        f'  Type: {touchpoint.touchpoint_type.code} '
                        f'({touchpoint.touchpoint_type.name})'
                    )
                
                if touchpoint.parent:
                    self.stdout.write(f'  Parent: {touchpoint.parent.code} ({touchpoint.parent.name})')
        
        # UTM parameters
        if any([wi.utm_source, wi.utm_medium, wi.utm_campaign]):
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('Attribution:'))
            if wi.utm_source:
                self.stdout.write(f'  Source: {wi.utm_source}')
            if wi.utm_medium:
                self.stdout.write(f'  Medium: {wi.utm_medium}')
            if wi.utm_campaign:
                self.stdout.write(f'  Campaign: {wi.utm_campaign}')
        
        # Payload preview
        if wi.payload:
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('Payload Keys:'))
            self.stdout.write(f'  {", ".join(list(wi.payload.keys())[:10])}')
            if 'page_title' in wi.payload:
                self.stdout.write(f'  Page Title: {wi.payload["page_title"]}')
        
        self.stdout.write(self.style.SUCCESS('─' * 80))
    
    def _display_statistics(self):
        """Display statistics"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(' STATISTICS (Last 24 Hours) '.center(80)))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        cutoff = timezone.now() - timedelta(hours=24)
        
        # Count objects
        stats = {
            'Interactions': Interaction.objects.filter(created_at__gte=cutoff).count(),
            'WebInteractions': WebInteraction.objects.filter(created_at__gte=cutoff).count(),
            'WebSessions': WebSession.objects.filter(created_at__gte=cutoff).count(),
            'Unique Sessions': WebInteraction.objects.filter(
                created_at__gte=cutoff
            ).values('session_id').distinct().count(),
            'Unique Visitors': WebInteraction.objects.filter(
                created_at__gte=cutoff
            ).values('visitor_cookie').distinct().count(),
        }
        
        for key, value in stats.items():
            self.stdout.write(f'{key:<30} {value:>10}')
        
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Total Database Objects:'))
        
        total_stats = {
            'Websites': Website.objects.count(),
            'Channels': Channel.objects.count(),
            'Mediums': Medium.objects.count(),
            'TouchpointTypes': TouchpointType.objects.count(),
            'Touchpoints': Touchpoint.objects.count(),
            'Actions': Action.objects.count(),
            'Agents': Agent.objects.count(),
        }
        
        for key, value in total_stats.items():
            self.stdout.write(f'{key:<30} {value:>10}')
        
        # Action breakdown
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Actions (24h):'))
        action_stats = Interaction.objects.filter(
            created_at__gte=cutoff
        ).values('action__code', 'action__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for stat in action_stats:
            action_name = stat['action__name'] or 'Unknown'
            self.stdout.write(f'  {action_name:<25} {stat["count"]:>5}')
    
    def _validate_taxonomy(self):
        """Validate taxonomy completeness"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(' TAXONOMY VALIDATION '.center(80)))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        # Check for touchpoints without taxonomy
        incomplete_touchpoints = Touchpoint.objects.filter(
            Q(channel__isnull=True) | 
            Q(medium__isnull=True) | 
            Q(touchpoint_type__isnull=True)
        ).count()
        
        if incomplete_touchpoints > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {incomplete_touchpoints} touchpoints have incomplete taxonomy'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All touchpoints have complete taxonomy')
            )
        
        # Check for interactions without touchpoints
        no_touchpoint = Interaction.objects.filter(touchpoint__isnull=True).count()
        if no_touchpoint > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {no_touchpoint} interactions without touchpoint assignment'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All interactions have touchpoint assignments')
            )
        
        # Check for interactions without actions
        no_action = Interaction.objects.filter(action__isnull=True).count()
        if no_action > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {no_action} interactions without action assignment'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All interactions have action assignments')
            )
        
        # Check for web_page touchpoints
        web_page_count = Touchpoint.objects.filter(code='web_page').count()
        self.stdout.write('')
        self.stdout.write(f"📄 'web_page' touchpoints: {web_page_count}")
        
        # Check for owned channels
        owned_channels = Channel.objects.filter(source_type='owned').count()
        self.stdout.write(f"🏠 'owned' channels: {owned_channels}")
        
        # Check for web_interaction medium
        web_interaction_medium = Medium.objects.filter(code='web_interaction').count()
        self.stdout.write(f"🌐 'web_interaction' medium: {web_interaction_medium}")
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))

