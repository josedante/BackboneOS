"""
Management command to manage touchpoint mapping rules.

This command provides utilities for creating, listing, updating, and deleting
touchpoint mapping rules.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from typing import Dict, Any, List
import json

from connectors.models import TouchpointMappingRule


class Command(BaseCommand):
    help = "Manage touchpoint mapping rules"
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List mapping rules')
        list_parser.add_argument(
            '--connector-type',
            help='Filter by connector type'
        )
        list_parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active rules'
        )
        list_parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)'
        )
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create a mapping rule')
        create_parser.add_argument(
            '--connector-type',
            required=True,
            help='Connector type (e.g., web, email, whatsapp)'
        )
        create_parser.add_argument(
            '--source-identifier',
            default='',
            help='Source identifier (e.g., website URL, email domain)'
        )
        create_parser.add_argument(
            '--event-code',
            required=True,
            help='Event code (e.g., web.page_read, email.open)'
        )
        create_parser.add_argument(
            '--touchpoint-code',
            required=True,
            help='Resulting touchpoint code'
        )
        create_parser.add_argument(
            '--touchpoint-label',
            help='Human-readable touchpoint label'
        )
        create_parser.add_argument(
            '--channel-code',
            help='Channel code override'
        )
        create_parser.add_argument(
            '--medium-code',
            help='Medium code override'
        )
        create_parser.add_argument(
            '--priority',
            type=int,
            default=100,
            help='Rule priority (higher = more specific, default: 100)'
        )
        create_parser.add_argument(
            '--metadata',
            help='Additional metadata as JSON string'
        )
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update a mapping rule')
        update_parser.add_argument(
            '--id',
            required=True,
            help='Rule ID to update'
        )
        update_parser.add_argument(
            '--touchpoint-code',
            help='New touchpoint code'
        )
        update_parser.add_argument(
            '--touchpoint-label',
            help='New touchpoint label'
        )
        update_parser.add_argument(
            '--channel-code',
            help='New channel code'
        )
        update_parser.add_argument(
            '--medium-code',
            help='New medium code'
        )
        update_parser.add_argument(
            '--priority',
            type=int,
            help='New priority'
        )
        update_parser.add_argument(
            '--active',
            type=bool,
            help='Active status (true/false)'
        )
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a mapping rule')
        delete_parser.add_argument(
            '--id',
            required=True,
            help='Rule ID to delete'
        )
        delete_parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation'
        )
        
        # Import command
        import_parser = subparsers.add_parser('import', help='Import mapping rules from JSON file')
        import_parser.add_argument(
            '--file',
            required=True,
            help='JSON file path containing mapping rules'
        )
        import_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export mapping rules to JSON file')
        export_parser.add_argument(
            '--file',
            help='Output JSON file path (default: stdout)'
        )
        export_parser.add_argument(
            '--connector-type',
            help='Filter by connector type'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if not action:
            self.stdout.write(self.style.ERROR("Please specify an action. Use --help for available actions."))
            return
        
        if action == 'list':
            self._list_rules(options)
        elif action == 'create':
            self._create_rule(options)
        elif action == 'update':
            self._update_rule(options)
        elif action == 'delete':
            self._delete_rule(options)
        elif action == 'import':
            self._import_rules(options)
        elif action == 'export':
            self._export_rules(options)
    
    def _list_rules(self, options):
        """List mapping rules."""
        queryset = TouchpointMappingRule.objects.all()
        
        # Apply filters
        if options.get('connector_type'):
            queryset = queryset.filter(connector_type=options['connector_type'])
        
        if options.get('active_only'):
            queryset = queryset.filter(is_active=True)
        
        # Order by priority and connector type
        queryset = queryset.order_by('-priority', 'connector_type', 'event_code')
        
        rules = list(queryset)
        
        if not rules:
            self.stdout.write("No mapping rules found.")
            return
        
        if options['format'] == 'json':
            self._output_json(rules)
        else:
            self._output_table(rules)
    
    def _output_table(self, rules: List[TouchpointMappingRule]):
        """Output rules in table format."""
        self.stdout.write("\nTouchpoint Mapping Rules:")
        self.stdout.write("=" * 120)
        self.stdout.write(
            f"{'ID':<8} {'Type':<10} {'Source':<20} {'Event':<20} {'Touchpoint':<20} {'Channel':<10} {'Medium':<10} {'Priority':<8} {'Active':<6}"
        )
        self.stdout.write("-" * 120)
        
        for rule in rules:
            self.stdout.write(
                f"{str(rule.id)[:8]:<8} "
                f"{rule.connector_type:<10} "
                f"{rule.source_identifier[:20]:<20} "
                f"{rule.event_code[:20]:<20} "
                f"{rule.touchpoint_code[:20]:<20} "
                f"{rule.channel_code[:10]:<10} "
                f"{rule.medium_code[:10]:<10} "
                f"{rule.priority:<8} "
                f"{'Yes' if rule.is_active else 'No':<6}"
            )
        
        self.stdout.write("=" * 120)
        self.stdout.write(f"Total: {len(rules)} rules")
    
    def _output_json(self, rules: List[TouchpointMappingRule]):
        """Output rules in JSON format."""
        data = []
        for rule in rules:
            data.append({
                'id': str(rule.id),
                'connector_type': rule.connector_type,
                'source_identifier': rule.source_identifier,
                'event_code': rule.event_code,
                'touchpoint_code': rule.touchpoint_code,
                'touchpoint_label': rule.touchpoint_label,
                'channel_code': rule.channel_code,
                'medium_code': rule.medium_code,
                'priority': rule.priority,
                'is_active': rule.is_active,
                'metadata': rule.metadata,
                'created_at': rule.created_at.isoformat(),
                'updated_at': rule.updated_at.isoformat()
            })
        
        self.stdout.write(json.dumps(data, indent=2))
    
    def _create_rule(self, options):
        """Create a new mapping rule."""
        try:
            metadata = {}
            if options.get('metadata'):
                metadata = json.loads(options['metadata'])
            
            rule = TouchpointMappingRule.objects.create(
                connector_type=options['connector_type'],
                source_identifier=options['source_identifier'],
                event_code=options['event_code'],
                touchpoint_code=options['touchpoint_code'],
                touchpoint_label=options.get('touchpoint_label', ''),
                channel_code=options.get('channel_code', ''),
                medium_code=options.get('medium_code', ''),
                priority=options['priority'],
                metadata=metadata
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created mapping rule: {rule}")
            )
            
        except Exception as e:
            raise CommandError(f"Failed to create mapping rule: {e}")
    
    def _update_rule(self, options):
        """Update an existing mapping rule."""
        try:
            rule = TouchpointMappingRule.objects.get(id=options['id'])
            
            # Update fields if provided
            if options.get('touchpoint_code'):
                rule.touchpoint_code = options['touchpoint_code']
            if options.get('touchpoint_label'):
                rule.touchpoint_label = options['touchpoint_label']
            if options.get('channel_code'):
                rule.channel_code = options['channel_code']
            if options.get('medium_code'):
                rule.medium_code = options['medium_code']
            if options.get('priority'):
                rule.priority = options['priority']
            if options.get('active') is not None:
                rule.is_active = options['active']
            
            rule.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Updated mapping rule: {rule}")
            )
            
        except TouchpointMappingRule.DoesNotExist:
            raise CommandError(f"Mapping rule with ID {options['id']} not found")
        except Exception as e:
            raise CommandError(f"Failed to update mapping rule: {e}")
    
    def _delete_rule(self, options):
        """Delete a mapping rule."""
        try:
            rule = TouchpointMappingRule.objects.get(id=options['id'])
            
            if not options.get('force'):
                confirm = input(f"Are you sure you want to delete rule '{rule}'? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Deletion cancelled.")
                    return
            
            rule.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Deleted mapping rule: {rule}")
            )
            
        except TouchpointMappingRule.DoesNotExist:
            raise CommandError(f"Mapping rule with ID {options['id']} not found")
        except Exception as e:
            raise CommandError(f"Failed to delete mapping rule: {e}")
    
    def _import_rules(self, options):
        """Import mapping rules from JSON file."""
        file_path = options['file']
        dry_run = options.get('dry_run', False)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise CommandError("JSON file must contain an array of mapping rules")
            
            imported = 0
            skipped = 0
            
            for rule_data in data:
                try:
                    # Check if rule already exists
                    existing = TouchpointMappingRule.objects.filter(
                        connector_type=rule_data['connector_type'],
                        source_identifier=rule_data.get('source_identifier', ''),
                        event_code=rule_data['event_code']
                    ).first()
                    
                    if existing:
                        self.stdout.write(f"⚠️  Skipping existing rule: {existing}")
                        skipped += 1
                        continue
                    
                    if not dry_run:
                        TouchpointMappingRule.objects.create(**rule_data)
                    
                    self.stdout.write(f"✅ {'Would import' if dry_run else 'Imported'}: {rule_data['connector_type']}:{rule_data['event_code']}")
                    imported += 1
                    
                except Exception as e:
                    self.stdout.write(f"❌ Failed to import rule: {e}")
            
            if dry_run:
                self.stdout.write(f"\nDRY RUN: Would import {imported} rules, skip {skipped} existing")
            else:
                self.stdout.write(f"\nImported {imported} rules, skipped {skipped} existing")
                
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise CommandError(f"Failed to import rules: {e}")
    
    def _export_rules(self, options):
        """Export mapping rules to JSON file."""
        queryset = TouchpointMappingRule.objects.all()
        
        if options.get('connector_type'):
            queryset = queryset.filter(connector_type=options['connector_type'])
        
        rules = list(queryset)
        data = []
        
        for rule in rules:
            data.append({
                'connector_type': rule.connector_type,
                'source_identifier': rule.source_identifier,
                'event_code': rule.event_code,
                'touchpoint_code': rule.touchpoint_code,
                'touchpoint_label': rule.touchpoint_label,
                'channel_code': rule.channel_code,
                'medium_code': rule.medium_code,
                'priority': rule.priority,
                'is_active': rule.is_active,
                'metadata': rule.metadata
            })
        
        output = json.dumps(data, indent=2)
        
        if options.get('file'):
            with open(options['file'], 'w') as f:
                f.write(output)
            self.stdout.write(f"✅ Exported {len(rules)} rules to {options['file']}")
        else:
            self.stdout.write(output)
