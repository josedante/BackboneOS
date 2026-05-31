"""
Management command to wait for database to be ready.

This command is useful in Docker environments where the database
service might take time to start up and be ready to accept connections.
"""

import time
import sys
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Wait for database to be ready."""
    
    help = 'Wait for database to be ready'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Timeout in seconds (default: 60)'
        )
        
        parser.add_argument(
            '--interval',
            type=int,
            default=2,
            help='Check interval in seconds (default: 2)'
        )
        
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database to check (default: default)'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        timeout = options['timeout']
        interval = options['interval']
        database = options['database']
        
        self.stdout.write(
            self.style.WARNING(
                f'Waiting for database "{database}" to be ready...'
            )
        )
        
        start_time = time.time()
        
        while True:
            try:
                # Try to connect to the database
                db_conn = connections[database]
                db_conn.cursor()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Database "{database}" is ready!'
                    )
                )
                return
                
            except OperationalError as e:
                elapsed_time = time.time() - start_time
                
                if elapsed_time >= timeout:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Timeout waiting for database "{database}" '
                            f'after {timeout} seconds'
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR(f'Last error: {e}')
                    )
                    sys.exit(1)
                
                self.stdout.write(
                    f'Database "{database}" not ready, waiting... '
                    f'({elapsed_time:.1f}s/{timeout}s)'
                )
                time.sleep(interval)
