"""
Management command to backfill touchpoints for existing interactions.

This command processes existing interactions that don't have touchpoints
and creates them using the touchpoint resolution system.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
import logging

from interactions.models import Interaction
from connectors.models import TouchpointMappingRule
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill touchpoints for existing interactions without touchpoints"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of interactions to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--connector-type',
            choices=['web', 'email', 'whatsapp', 'all'],
            default='all',
            help='Specific connector type to process (default: all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of interactions to process (no limit if not specified)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        connector_type = options['connector_type']
        limit = options.get('limit')
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting touchpoint backfill process..."
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
        
        # Initialize resolver
        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        
        # Get interactions without touchpoints
        queryset = self._get_interactions_queryset(connector_type, limit)
        
        total = queryset.count()
        self.stdout.write(f"Found {total} interactions without touchpoints")
        
        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("No interactions need touchpoint backfill")
            )
            return
        
        # Process in batches
        processed = 0
        created = 0
        errors = 0
        
        for batch in self._batch_queryset(queryset, batch_size):
            batch_processed, batch_created, batch_errors = self._process_batch(
                batch, resolver, dry_run, verbose
            )
            
            processed += batch_processed
            created += batch_created
            errors += batch_errors
            
            # Progress update
            if processed % (batch_size * 5) == 0:  # Every 5 batches
                self.stdout.write(
                    f"Progress: {processed}/{total} interactions processed "
                    f"({created} touchpoints created, {errors} errors)"
                )
        
        # Final summary
        self._print_summary(processed, created, errors, dry_run)
    
    def _get_interactions_queryset(self, connector_type: str, limit: int):
        """Get queryset of interactions without touchpoints."""
        queryset = Interaction.objects.filter(
            touchpoint__isnull=True
        ).select_related('action', 'agent')
        
        # Filter by connector type if specified
        if connector_type != 'all':
            # This would need to be adapted based on how connector types are identified
            # For now, we'll use a simple approach based on action codes
            if connector_type == 'web':
                queryset = queryset.filter(action__code__startswith='web_')
            elif connector_type == 'email':
                queryset = queryset.filter(action__code__startswith='email_')
            elif connector_type == 'whatsapp':
                queryset = queryset.filter(action__code__startswith='whatsapp_')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def _batch_queryset(self, queryset, batch_size: int):
        """Yield batches of queryset."""
        total = queryset.count()
        for i in range(0, total, batch_size):
            yield queryset[i:i + batch_size]
    
    def _process_batch(self, batch, resolver, dry_run: bool, verbose: bool):
        """Process a batch of interactions."""
        batch_processed = 0
        batch_created = 0
        batch_errors = 0
        
        for interaction in batch:
            try:
                if not dry_run:
                    # For now, we'll create a generic touchpoint
                    # In a real implementation, this would need to identify
                    # the connector type and use the appropriate resolver
                    touchpoint = self._create_generic_touchpoint(interaction)
                    interaction.touchpoint = touchpoint
                    interaction.save(update_fields=['touchpoint'])
                    batch_created += 1
                
                batch_processed += 1
                
                if verbose:
                    self.stdout.write(
                        f"  Processed interaction {interaction.id}: "
                        f"action={interaction.action.code if interaction.action else 'None'}"
                    )
                
            except Exception as e:
                batch_errors += 1
                logger.error(f"Error processing interaction {interaction.id}: {e}")
                if verbose:
                    self.stderr.write(
                        f"  Error processing interaction {interaction.id}: {e}"
                    )
        
        return batch_processed, batch_created, batch_errors
    
    def _create_generic_touchpoint(self, interaction):
        """Create a generic touchpoint for an interaction."""
        from interactions.models import Touchpoint, TouchpointClass, Channel
        
        # Determine channel based on interaction context or use generic
        # For now, we'll infer the channel from the action or use a default
        if interaction.action and interaction.action.code:
            action_code = interaction.action.code
            if action_code.startswith('web_'):
                channel_code = 'web'
                channel_name = 'Web'
            elif action_code.startswith('email_'):
                channel_code = 'email'
                channel_name = 'Email'
            elif action_code.startswith('whatsapp_'):
                channel_code = 'whatsapp'
                channel_name = 'WhatsApp'
            else:
                channel_code = 'generic'
                channel_name = 'Generic'
        else:
            channel_code = 'generic'
            channel_name = 'Generic'
        
        # Get or create the channel
        channel, _ = Channel.objects.get_or_create(
            code=channel_code,
            defaults={'name': f'{channel_name} Channel'}
        )
        
        # Get or create a touchpoint class based on the channel
        touchpoint_class_code = f"{channel_code}_generic"
        touchpoint_class, _ = TouchpointClass.objects.get_or_create(
            code=touchpoint_class_code,
            defaults={
                'name': f'{channel_name} Generic Touchpoint Class',
                'description': f'Generic touchpoint class for {channel_name} interactions'
            }
        )
        
        # Create touchpoint with channel
        action_code = interaction.action.code if interaction.action else 'unknown'
        touchpoint_code = f"{channel_code}.{action_code}"
        touchpoint, _ = Touchpoint.objects.get_or_create(
            code=touchpoint_code,
            defaults={
                'name': f"{channel_name} {action_code.title()}",
                'touchpoint_class': touchpoint_class,
                'channel': channel,
                'description': f"Auto-generated touchpoint for {action_code} in {channel_name}",
                'is_active': True
            }
        )
        
        return touchpoint
    
    def _print_summary(self, processed: int, created: int, errors: int, dry_run: bool):
        """Print final summary."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("BACKFILL SUMMARY")
        self.stdout.write("="*50)
        
        if dry_run:
            self.stdout.write(f"DRY RUN: Would have processed {processed} interactions")
            self.stdout.write(f"DRY RUN: Would have created {processed} touchpoints")
        else:
            self.stdout.write(f"Processed: {processed} interactions")
            self.stdout.write(f"Created: {created} touchpoints")
            self.stdout.write(f"Errors: {errors}")
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {errors} errors occurred during processing")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ All interactions processed successfully")
            )
        
        self.stdout.write("="*50)
