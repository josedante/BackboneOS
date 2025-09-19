"""
Management command to clean up old touchpoint resolution events and metrics.

This command implements data retention policies to prevent database bloat
while maintaining useful historical data for analysis.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from typing import Dict, Any

from connectors.monitoring_models import (
    TouchpointResolutionEvent,
    TouchpointResolutionMetrics,
    TouchpointCacheMetrics,
    TouchpointSystemHealth,
    TouchpointAlert
)


class Command(BaseCommand):
    help = "Clean up old touchpoint monitoring data according to retention policies"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup without confirmation prompts'
        )
        parser.add_argument(
            '--retention-days',
            type=int,
            default=90,
            help='Number of days to retain detailed events (default: 90)'
        )
        parser.add_argument(
            '--metrics-retention-days',
            type=int,
            default=365,
            help='Number of days to retain aggregated metrics (default: 365)'
        )
        parser.add_argument(
            '--alerts-retention-days',
            type=int,
            default=180,
            help='Number of days to retain resolved alerts (default: 180)'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        retention_days = options['retention_days']
        metrics_retention_days = options['metrics_retention_days']
        alerts_retention_days = options['alerts_retention_days']
        
        self.stdout.write("Touchpoint Data Cleanup")
        self.stdout.write("=" * 50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
        
        # Calculate cutoff dates
        events_cutoff = timezone.now() - timedelta(days=retention_days)
        metrics_cutoff = timezone.now() - timedelta(days=metrics_retention_days)
        alerts_cutoff = timezone.now() - timedelta(days=alerts_retention_days)
        
        # Get counts of what would be deleted
        cleanup_stats = self._get_cleanup_stats(events_cutoff, metrics_cutoff, alerts_cutoff)
        
        # Show what will be cleaned up
        self._show_cleanup_summary(cleanup_stats, retention_days, metrics_retention_days, alerts_retention_days)
        
        # Confirm if not forced
        if not force and not dry_run:
            confirm = input("\nProceed with cleanup? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("Cleanup cancelled.")
                return
        
        # Perform cleanup
        if not dry_run:
            self._perform_cleanup(events_cutoff, metrics_cutoff, alerts_cutoff)
        else:
            self.stdout.write("\nDRY RUN: Would have cleaned up the data shown above.")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Cleanup completed successfully!"))
    
    def _get_cleanup_stats(self, events_cutoff, metrics_cutoff, alerts_cutoff) -> Dict[str, int]:
        """Get statistics about what would be cleaned up."""
        return {
            'old_events': TouchpointResolutionEvent.objects.filter(
                occurred_at__lt=events_cutoff
            ).count(),
            'old_metrics': TouchpointResolutionMetrics.objects.filter(
                period_start__lt=metrics_cutoff
            ).count(),
            'old_cache_metrics': TouchpointCacheMetrics.objects.filter(
                period_start__lt=metrics_cutoff
            ).count(),
            'old_health_records': TouchpointSystemHealth.objects.filter(
                recorded_at__lt=metrics_cutoff
            ).count(),
            'resolved_alerts': TouchpointAlert.objects.filter(
                status='resolved',
                resolved_at__lt=alerts_cutoff
            ).count(),
            'dismissed_alerts': TouchpointAlert.objects.filter(
                status='dismissed',
                triggered_at__lt=alerts_cutoff
            ).count(),
        }
    
    def _show_cleanup_summary(self, stats: Dict[str, int], retention_days: int, 
                            metrics_retention_days: int, alerts_retention_days: int):
        """Show summary of what will be cleaned up."""
        self.stdout.write(f"\nRetention Policy:")
        self.stdout.write(f"  Detailed Events: {retention_days} days")
        self.stdout.write(f"  Aggregated Metrics: {metrics_retention_days} days")
        self.stdout.write(f"  Resolved Alerts: {alerts_retention_days} days")
        
        self.stdout.write(f"\nData to be cleaned up:")
        self.stdout.write(f"  Old Resolution Events: {stats['old_events']:,}")
        self.stdout.write(f"  Old Resolution Metrics: {stats['old_metrics']:,}")
        self.stdout.write(f"  Old Cache Metrics: {stats['old_cache_metrics']:,}")
        self.stdout.write(f"  Old Health Records: {stats['old_health_records']:,}")
        self.stdout.write(f"  Resolved Alerts: {stats['resolved_alerts']:,}")
        self.stdout.write(f"  Dismissed Alerts: {stats['dismissed_alerts']:,}")
        
        total_records = sum(stats.values())
        self.stdout.write(f"\nTotal records to delete: {total_records:,}")
    
    def _perform_cleanup(self, events_cutoff, metrics_cutoff, alerts_cutoff):
        """Perform the actual cleanup."""
        with transaction.atomic():
            # Clean up old events
            deleted_events = TouchpointResolutionEvent.objects.filter(
                occurred_at__lt=events_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_events:,} old resolution events")
            
            # Clean up old metrics
            deleted_metrics = TouchpointResolutionMetrics.objects.filter(
                period_start__lt=metrics_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_metrics:,} old resolution metrics")
            
            # Clean up old cache metrics
            deleted_cache_metrics = TouchpointCacheMetrics.objects.filter(
                period_start__lt=metrics_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_cache_metrics:,} old cache metrics")
            
            # Clean up old health records
            deleted_health = TouchpointSystemHealth.objects.filter(
                recorded_at__lt=metrics_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_health:,} old health records")
            
            # Clean up resolved alerts
            deleted_resolved_alerts = TouchpointAlert.objects.filter(
                status='resolved',
                resolved_at__lt=alerts_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_resolved_alerts:,} resolved alerts")
            
            # Clean up dismissed alerts
            deleted_dismissed_alerts = TouchpointAlert.objects.filter(
                status='dismissed',
                triggered_at__lt=alerts_cutoff
            ).delete()[0]
            self.stdout.write(f"✅ Deleted {deleted_dismissed_alerts:,} dismissed alerts")
