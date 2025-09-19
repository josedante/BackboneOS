"""
Management command for monitoring touchpoint resolution system.

This command provides comprehensive monitoring capabilities including
metrics collection, alerting, and system health checks.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from typing import Dict, Any
import json

from connectors.metrics import get_metrics_summary, get_current_metrics, flush_metrics
from connectors.alerting import alert_manager
from connectors.monitoring_models import (
    TouchpointResolutionMetrics, TouchpointSystemHealth, TouchpointAlert
)


class Command(BaseCommand):
    help = "Monitor touchpoint resolution system health and performance"
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        status_parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)'
        )
        
        # Metrics command
        metrics_parser = subparsers.add_parser('metrics', help='Show performance metrics')
        metrics_parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours to analyze (default: 24)'
        )
        metrics_parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)'
        )
        
        # Alerts command
        alerts_parser = subparsers.add_parser('alerts', help='Manage alerts')
        alerts_parser.add_argument(
            '--list',
            action='store_true',
            help='List active alerts'
        )
        alerts_parser.add_argument(
            '--acknowledge',
            help='Acknowledge alert by ID'
        )
        alerts_parser.add_argument(
            '--resolve',
            help='Resolve alert by ID'
        )
        alerts_parser.add_argument(
            '--check',
            action='store_true',
            help='Check for new alerts'
        )
        
        # Health command
        health_parser = subparsers.add_parser('health', help='Check system health')
        health_parser.add_argument(
            '--record',
            action='store_true',
            help='Record current health status'
        )
        health_parser.add_argument(
            '--history',
            type=int,
            default=24,
            help='Show health history for last N hours (default: 24)'
        )
        
        # Flush command
        flush_parser = subparsers.add_parser('flush', help='Flush metrics buffers')
        
        # Collect command
        collect_parser = subparsers.add_parser('collect', help='Collect and store metrics')
        collect_parser.add_argument(
            '--period',
            choices=['hourly', 'daily'],
            default='hourly',
            help='Collection period (default: hourly)'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if not action:
            self.stdout.write(self.style.ERROR("Please specify an action. Use --help for available actions."))
            return
        
        if action == 'status':
            self._show_status(options)
        elif action == 'metrics':
            self._show_metrics(options)
        elif action == 'alerts':
            self._manage_alerts(options)
        elif action == 'health':
            self._manage_health(options)
        elif action == 'flush':
            self._flush_metrics()
        elif action == 'collect':
            self._collect_metrics(options)
    
    def _show_status(self, options):
        """Show current system status."""
        try:
            current_metrics = get_current_metrics()
            alert_summary = alert_manager.get_alert_summary()
            
            if options['format'] == 'json':
                self._output_json({
                    'current_metrics': current_metrics,
                    'alert_summary': alert_summary,
                    'timestamp': timezone.now().isoformat()
                })
            else:
                self._output_status_table(current_metrics, alert_summary)
        
        except Exception as e:
            raise CommandError(f"Failed to get system status: {e}")
    
    def _show_metrics(self, options):
        """Show performance metrics."""
        try:
            hours = options['hours']
            metrics = get_metrics_summary(hours)
            
            if options['format'] == 'json':
                self._output_json(metrics)
            else:
                self._output_metrics_table(metrics, hours)
        
        except Exception as e:
            raise CommandError(f"Failed to get metrics: {e}")
    
    def _manage_alerts(self, options):
        """Manage alerts."""
        try:
            if options.get('list'):
                self._list_alerts()
            elif options.get('acknowledge'):
                self._acknowledge_alert(options['acknowledge'])
            elif options.get('resolve'):
                self._resolve_alert(options['resolve'])
            elif options.get('check'):
                self._check_alerts()
            else:
                self.stdout.write("Please specify an alert action (--list, --acknowledge, --resolve, --check)")
        
        except Exception as e:
            raise CommandError(f"Failed to manage alerts: {e}")
    
    def _manage_health(self, options):
        """Manage system health."""
        try:
            if options.get('record'):
                self._record_health()
            elif options.get('history'):
                self._show_health_history(options['history'])
            else:
                self._show_current_health()
        
        except Exception as e:
            raise CommandError(f"Failed to manage health: {e}")
    
    def _flush_metrics(self):
        """Flush metrics buffers."""
        try:
            flush_metrics()
            self.stdout.write(
                self.style.SUCCESS("✅ Metrics buffers flushed successfully")
            )
        except Exception as e:
            raise CommandError(f"Failed to flush metrics: {e}")
    
    def _collect_metrics(self, options):
        """Collect and store metrics."""
        try:
            period = options['period']
            self._store_metrics(period)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Metrics collected and stored for {period} period")
            )
        except Exception as e:
            raise CommandError(f"Failed to collect metrics: {e}")
    
    def _output_status_table(self, current_metrics: Dict[str, Any], alert_summary: Dict[str, Any]):
        """Output system status in table format."""
        self.stdout.write("\nTouchpoint Resolution System Status")
        self.stdout.write("=" * 50)
        
        # Current metrics
        system = current_metrics.get('system', {})
        self.stdout.write(f"Active Mapping Rules: {system.get('active_mapping_rules', 0)}")
        self.stdout.write(f"Cache Size: {system.get('cache_size', 0)} keys")
        self.stdout.write(f"Database Connections: {system.get('database_connections', 0)}")
        
        # Alert summary
        self.stdout.write(f"\nActive Alerts: {alert_summary.get('total_active', 0)}")
        severity_counts = alert_summary.get('by_severity', {})
        if any(severity_counts.values()):
            self.stdout.write("  By Severity:")
            for severity, count in severity_counts.items():
                if count > 0:
                    self.stdout.write(f"    {severity.title()}: {count}")
        
        # Recent alerts
        recent_alerts = alert_summary.get('recent_alerts', [])
        if recent_alerts:
            self.stdout.write("\nRecent Alerts:")
            for alert in recent_alerts[:5]:
                self.stdout.write(f"  [{alert['severity'].upper()}] {alert['title']}")
        
        self.stdout.write("=" * 50)
    
    def _output_metrics_table(self, metrics: Dict[str, Any], hours: int):
        """Output metrics in table format."""
        self.stdout.write(f"\nTouchpoint Resolution Metrics (Last {hours} hours)")
        self.stdout.write("=" * 60)
        
        self.stdout.write(f"Total Resolutions: {metrics.get('total_resolutions', 0)}")
        self.stdout.write(f"Successful Resolutions: {metrics.get('successful_resolutions', 0)}")
        self.stdout.write(f"Error Rate: {metrics.get('error_rate', 0):.1f}%")
        self.stdout.write(f"Average Resolution Time: {metrics.get('avg_resolution_time_ms', 0):.1f}ms")
        self.stdout.write(f"Max Resolution Time: {metrics.get('max_resolution_time_ms', 0):.1f}ms")
        self.stdout.write(f"Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1f}%")
        
        # Connector breakdown
        connector_breakdown = metrics.get('connector_breakdown', {})
        if connector_breakdown:
            self.stdout.write("\nConnector Breakdown:")
            for connector, stats in connector_breakdown.items():
                avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
                self.stdout.write(f"  {connector}: {stats['count']} resolutions, {avg_time:.1f}ms avg")
        
        # Hourly breakdown
        hourly_breakdown = metrics.get('hourly_breakdown', [])
        if hourly_breakdown:
            self.stdout.write("\nHourly Breakdown (Last 6 hours):")
            for hour_data in hourly_breakdown[:6]:
                hour = hour_data['hour'][-2:]  # Just the hour part
                self.stdout.write(
                    f"  {hour}:00 - {hour_data['resolutions']} resolutions, "
                    f"{hour_data['error_rate']:.1f}% errors, "
                    f"{hour_data['avg_time_ms']:.1f}ms avg"
                )
        
        self.stdout.write("=" * 60)
    
    def _list_alerts(self):
        """List active alerts."""
        alerts = alert_manager.get_active_alerts()
        
        if not alerts:
            self.stdout.write("No active alerts.")
            return
        
        self.stdout.write(f"\nActive Alerts ({alerts.count()}):")
        self.stdout.write("=" * 80)
        self.stdout.write(
            f"{'ID':<8} {'Type':<20} {'Severity':<10} {'Title':<30} {'Triggered':<20}"
        )
        self.stdout.write("-" * 80)
        
        for alert in alerts:
            self.stdout.write(
                f"{str(alert.id)[:8]:<8} "
                f"{alert.alert_type:<20} "
                f"{alert.severity:<10} "
                f"{alert.title[:30]:<30} "
                f"{alert.triggered_at.strftime('%Y-%m-%d %H:%M'):<20}"
            )
        
        self.stdout.write("=" * 80)
    
    def _acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        if alert_manager.acknowledge_alert(alert_id):
            self.stdout.write(
                self.style.SUCCESS(f"✅ Alert {alert_id} acknowledged")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to acknowledge alert {alert_id}")
            )
    
    def _resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_manager.resolve_alert(alert_id):
            self.stdout.write(
                self.style.SUCCESS(f"✅ Alert {alert_id} resolved")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to resolve alert {alert_id}")
            )
    
    def _check_alerts(self):
        """Check for new alerts."""
        new_alerts = alert_manager.check_all_alerts()
        
        if new_alerts:
            self.stdout.write(f"Created {len(new_alerts)} new alerts:")
            for alert in new_alerts:
                self.stdout.write(f"  [{alert.severity.upper()}] {alert.title}")
        else:
            self.stdout.write("No new alerts created.")
    
    def _show_current_health(self):
        """Show current system health."""
        latest_health = TouchpointSystemHealth.objects.order_by('-recorded_at').first()
        
        if not latest_health:
            self.stdout.write("No health data available.")
            return
        
        self.stdout.write(f"\nSystem Health Status: {latest_health.health_status.upper()}")
        self.stdout.write("=" * 40)
        self.stdout.write(f"Recorded At: {latest_health.recorded_at}")
        self.stdout.write(f"Error Rate: {latest_health.error_rate:.1f}%")
        self.stdout.write(f"Avg Resolution Time: {latest_health.avg_resolution_time_ms:.1f}ms")
        self.stdout.write(f"Active Mapping Rules: {latest_health.active_mapping_rules}")
        self.stdout.write(f"Cache Size: {latest_health.cache_size}")
        self.stdout.write(f"Memory Usage: {latest_health.memory_usage_mb:.1f}MB")
        self.stdout.write("=" * 40)
    
    def _record_health(self):
        """Record current system health."""
        try:
            current_metrics = get_current_metrics()
            system_metrics = current_metrics.get('system', {})
            
            # Determine health status
            health_status = 'healthy'
            if system_metrics.get('active_mapping_rules', 0) == 0:
                health_status = 'warning'
            
            health_record = TouchpointSystemHealth.objects.create(
                active_mapping_rules=system_metrics.get('active_mapping_rules', 0),
                cache_size=system_metrics.get('cache_size', 0),
                database_connections=system_metrics.get('database_connections', 0),
                health_status=health_status,
                metadata=current_metrics
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Health recorded: {health_status}")
            )
        
        except Exception as e:
            raise CommandError(f"Failed to record health: {e}")
    
    def _show_health_history(self, hours: int):
        """Show health history."""
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        health_records = TouchpointSystemHealth.objects.filter(
            recorded_at__gte=cutoff_time
        ).order_by('-recorded_at')
        
        if not health_records:
            self.stdout.write(f"No health data for the last {hours} hours.")
            return
        
        self.stdout.write(f"\nHealth History (Last {hours} hours):")
        self.stdout.write("=" * 80)
        self.stdout.write(
            f"{'Time':<20} {'Status':<10} {'Error Rate':<12} {'Avg Time':<12} {'Cache Size':<12}"
        )
        self.stdout.write("-" * 80)
        
        for record in health_records:
            self.stdout.write(
                f"{record.recorded_at.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{record.health_status:<10} "
                f"{record.error_rate:.1f}%{'':<8} "
                f"{record.avg_resolution_time_ms:.1f}ms{'':<6} "
                f"{record.cache_size:<12}"
            )
        
        self.stdout.write("=" * 80)
    
    def _store_metrics(self, period: str):
        """Store aggregated metrics."""
        try:
            # Get metrics for the period
            hours = 1 if period == 'hourly' else 24
            metrics = get_metrics_summary(hours)
            
            # Calculate period boundaries
            now = timezone.now()
            if period == 'hourly':
                period_start = now.replace(minute=0, second=0, microsecond=0)
                period_end = period_start + timezone.timedelta(hours=1)
            else:
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timezone.timedelta(days=1)
            
            # Store metrics
            TouchpointResolutionMetrics.objects.create(
                period_start=period_start,
                period_end=period_end,
                period_type=period,
                total_resolutions=metrics.get('total_resolutions', 0),
                successful_resolutions=metrics.get('successful_resolutions', 0),
                failed_resolutions=metrics.get('total_resolutions', 0) - metrics.get('successful_resolutions', 0),
                avg_resolution_time_ms=metrics.get('avg_resolution_time_ms', 0),
                max_resolution_time_ms=metrics.get('max_resolution_time_ms', 0),
                cache_hit_rate=metrics.get('cache_hit_rate', 0),
                cache_miss_rate=100 - metrics.get('cache_hit_rate', 0),
                connector_breakdown=metrics.get('connector_breakdown', {}),
                metadata=metrics
            )
        
        except Exception as e:
            raise CommandError(f"Failed to store metrics: {e}")
    
    def _output_json(self, data: Dict[str, Any]):
        """Output data in JSON format."""
        self.stdout.write(json.dumps(data, indent=2, default=str))
