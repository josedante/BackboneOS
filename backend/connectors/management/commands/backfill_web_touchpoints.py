"""
Management command to backfill touchpoints for web interactions.

This command specifically handles web interactions and uses the
WebTouchpointResolver for proper web-specific touchpoint resolution.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
import logging

from websites.models import WebInteraction
from websites.resolvers import WebTouchpointResolver
from websites.mapping_providers import WebMappingProvider
from interactions.models import Interaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill touchpoints for existing web interactions"
    
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
            '--limit',
            type=int,
            help='Maximum number of interactions to process (no limit if not specified)'
        )
        parser.add_argument(
            '--website',
            help='Filter by specific website base URL'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-resolution of interactions that already have touchpoints'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        limit = options.get('limit')
        website_filter = options.get('website')
        verbose = options['verbose']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS("Starting web touchpoint backfill process...")
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
        
        # Initialize web-specific resolver
        resolver = WebTouchpointResolver(WebMappingProvider())
        
        # Get web interactions
        queryset = self._get_web_interactions_queryset(website_filter, limit, force)
        
        total = queryset.count()
        self.stdout.write(f"Found {total} web interactions to process")
        
        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("No web interactions need touchpoint backfill")
            )
            return
        
        # Process in batches
        processed = 0
        created = 0
        updated = 0
        errors = 0
        
        for batch in self._batch_queryset(queryset, batch_size):
            batch_processed, batch_created, batch_updated, batch_errors = self._process_batch(
                batch, resolver, dry_run, verbose, force
            )
            
            processed += batch_processed
            created += batch_created
            updated += batch_updated
            errors += batch_errors
            
            # Progress update
            if processed % (batch_size * 5) == 0:  # Every 5 batches
                self.stdout.write(
                    f"Progress: {processed}/{total} interactions processed "
                    f"({created} created, {updated} updated, {errors} errors)"
                )
        
        # Final summary
        self._print_summary(processed, created, updated, errors, dry_run)
    
    def _get_web_interactions_queryset(self, website_filter: str, limit: int, force: bool):
        """Get queryset of web interactions to process."""
        queryset = WebInteraction.objects.select_related(
            'interaction', 'website', 'interaction__action', 'interaction__agent'
        )
        
        # Filter by website if specified
        if website_filter:
            queryset = queryset.filter(website__base_url=website_filter)
        
        # Filter by touchpoint status
        if force:
            # Process all interactions (force re-resolution)
            pass
        else:
            # Only process interactions without touchpoints
            queryset = queryset.filter(interaction__touchpoint__isnull=True)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def _batch_queryset(self, queryset, batch_size: int):
        """Yield batches of queryset."""
        total = queryset.count()
        for i in range(0, total, batch_size):
            yield queryset[i:i + batch_size]
    
    def _process_batch(self, batch, resolver, dry_run: bool, verbose: bool, force: bool):
        """Process a batch of web interactions."""
        batch_processed = 0
        batch_created = 0
        batch_updated = 0
        batch_errors = 0
        
        for web_interaction in batch:
            try:
                if not dry_run:
                    # Resolve touchpoint using web-specific resolver
                    touchpoint = resolver.resolve(web_interaction)
                    
                    # Check if this is a new touchpoint or update
                    had_touchpoint = web_interaction.interaction.touchpoint_id is not None
                    
                    web_interaction.interaction.touchpoint = touchpoint
                    web_interaction.interaction.save(update_fields=['touchpoint'])
                    
                    if had_touchpoint:
                        batch_updated += 1
                    else:
                        batch_created += 1
                else:
                    # In dry run, just simulate the resolution
                    hint = web_interaction.infer_touchpoint_hint()
                    batch_created += 1
                
                batch_processed += 1
                
                if verbose:
                    self._log_interaction_details(web_interaction, dry_run)
                
            except Exception as e:
                batch_errors += 1
                logger.error(f"Error processing WebInteraction {web_interaction.id}: {e}")
                if verbose:
                    self.stderr.write(
                        f"  Error processing WebInteraction {web_interaction.id}: {e}"
                    )
        
        return batch_processed, batch_created, batch_updated, batch_errors
    
    def _log_interaction_details(self, web_interaction: WebInteraction, dry_run: bool):
        """Log detailed information about an interaction."""
        hint = web_interaction.infer_touchpoint_hint()
        
        self.stdout.write(f"  WebInteraction {web_interaction.id}:")
        self.stdout.write(f"    Website: {web_interaction.website.base_url}")
        self.stdout.write(f"    Session: {web_interaction.session_id}")
        self.stdout.write(f"    UTM Source: {web_interaction.utm_source or 'None'}")
        self.stdout.write(f"    UTM Medium: {web_interaction.utm_medium or 'None'}")
        self.stdout.write(f"    Referrer: {web_interaction.referrer_url or 'None'}")
        self.stdout.write(f"    User Agent: {web_interaction.user_agent[:50] + '...' if web_interaction.user_agent and len(web_interaction.user_agent) > 50 else web_interaction.user_agent or 'None'}")
        self.stdout.write(f"    Inferred Hint: {hint.code} | {hint.channel_code} | {hint.medium_code}")
        
        if not dry_run:
            self.stdout.write(f"    Resolved Touchpoint: {web_interaction.interaction.touchpoint.code}")
        
        self.stdout.write("")
    
    def _print_summary(self, processed: int, created: int, updated: int, errors: int, dry_run: bool):
        """Print final summary."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("WEB TOUCHPOINT BACKFILL SUMMARY")
        self.stdout.write("="*60)
        
        if dry_run:
            self.stdout.write(f"DRY RUN: Would have processed {processed} web interactions")
            self.stdout.write(f"DRY RUN: Would have created {processed} touchpoints")
        else:
            self.stdout.write(f"Processed: {processed} web interactions")
            self.stdout.write(f"Created: {created} new touchpoints")
            self.stdout.write(f"Updated: {updated} existing touchpoints")
            self.stdout.write(f"Errors: {errors}")
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {errors} errors occurred during processing")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ All web interactions processed successfully")
            )
        
        # Additional statistics
        if not dry_run and processed > 0:
            success_rate = ((processed - errors) / processed) * 100
            self.stdout.write(f"Success rate: {success_rate:.1f}%")
        
        self.stdout.write("="*60)
