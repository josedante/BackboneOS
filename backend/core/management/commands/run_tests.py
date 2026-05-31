"""
Management command for running different test suites.

This command provides various options for running tests:
- Unit tests only
- Integration tests only
- API tests only
- Performance tests only
- All tests with coverage
- Specific app tests
- Parallel test execution
- Test with different databases
"""

import os
import sys
import subprocess
import argparse
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.test.utils import get_runner


class Command(BaseCommand):
    """Run different test suites with various options."""
    
    help = 'Run different test suites with various options'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--type',
            choices=['unit', 'integration', 'api', 'performance', 'all', 'smoke'],
            default='all',
            help='Type of tests to run'
        )
        
        parser.add_argument(
            '--app',
            type=str,
            help='Specific app to test'
        )
        
        parser.add_argument(
            '--coverage',
            action='store_true',
            help='Run tests with coverage report'
        )
        
        parser.add_argument(
            '--parallel',
            action='store_true',
            help='Run tests in parallel'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
        
        parser.add_argument(
            '--keep-db',
            action='store_true',
            help='Keep test database after tests'
        )
        
        parser.add_argument(
            '--failfast',
            action='store_true',
            help='Stop on first failure'
        )
        
        parser.add_argument(
            '--pattern',
            type=str,
            help='Test file pattern to match'
        )
        
        parser.add_argument(
            '--markers',
            type=str,
            help='Pytest markers to include'
        )
        
        parser.add_argument(
            '--exclude-markers',
            type=str,
            help='Pytest markers to exclude'
        )
        
        parser.add_argument(
            '--html-report',
            action='store_true',
            help='Generate HTML coverage report'
        )
        
        parser.add_argument(
            '--xml-report',
            action='store_true',
            help='Generate XML coverage report'
        )
        
        parser.add_argument(
            '--junit-xml',
            type=str,
            help='Generate JUnit XML report'
        )
        
        parser.add_argument(
            '--database',
            choices=['sqlite', 'postgresql', 'mysql'],
            default='sqlite',
            help='Database to use for testing'
        )
        
        parser.add_argument(
            '--workers',
            type=int,
            default=4,
            help='Number of parallel workers'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Test timeout in seconds'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write(
            self.style.SUCCESS('Starting test execution...')
        )
        
        # Determine test command based on type
        if options['type'] == 'unit':
            self.run_unit_tests(options)
        elif options['type'] == 'integration':
            self.run_integration_tests(options)
        elif options['type'] == 'api':
            self.run_api_tests(options)
        elif options['type'] == 'performance':
            self.run_performance_tests(options)
        elif options['type'] == 'smoke':
            self.run_smoke_tests(options)
        else:  # all
            self.run_all_tests(options)
    
    def run_unit_tests(self, options):
        """Run unit tests only."""
        self.stdout.write(self.style.WARNING('Running unit tests...'))
        
        cmd = self.build_pytest_command(options)
        cmd.extend(['-m', 'unit'])
        
        if options['exclude_markers']:
            cmd.extend(['-m', f'not {options["exclude_markers"]}'])
        
        self.execute_command(cmd)
    
    def run_integration_tests(self, options):
        """Run integration tests only."""
        self.stdout.write(self.style.WARNING('Running integration tests...'))
        
        cmd = self.build_pytest_command(options)
        cmd.extend(['-m', 'integration'])
        
        self.execute_command(cmd)
    
    def run_api_tests(self, options):
        """Run API tests only."""
        self.stdout.write(self.style.WARNING('Running API tests...'))
        
        cmd = self.build_pytest_command(options)
        cmd.extend(['-m', 'api'])
        
        self.execute_command(cmd)
    
    def run_performance_tests(self, options):
        """Run performance tests only."""
        self.stdout.write(self.style.WARNING('Running performance tests...'))
        
        cmd = self.build_pytest_command(options)
        cmd.extend(['-m', 'performance'])
        
        # Performance tests need more time
        cmd.extend(['--timeout', str(options['timeout'] * 2)])
        
        self.execute_command(cmd)
    
    def run_smoke_tests(self, options):
        """Run smoke tests only."""
        self.stdout.write(self.style.WARNING('Running smoke tests...'))
        
        cmd = self.build_pytest_command(options)
        cmd.extend(['-m', 'smoke'])
        
        self.execute_command(cmd)
    
    def run_all_tests(self, options):
        """Run all tests."""
        self.stdout.write(self.style.WARNING('Running all tests...'))
        
        cmd = self.build_pytest_command(options)
        
        # Exclude slow tests by default unless specifically requested
        if not options['markers'] or 'slow' not in options['markers']:
            cmd.extend(['-m', 'not slow'])
        
        self.execute_command(cmd)
    
    def build_pytest_command(self, options):
        """Build pytest command with options."""
        cmd = ['python', '-m', 'pytest']
        
        # Add verbosity
        if options['verbose']:
            cmd.append('-v')
        else:
            cmd.append('-q')
        
        # Add failfast
        if options['failfast']:
            cmd.append('-x')
        
        # Add keep database
        if options['keep_db']:
            cmd.append('--reuse-db')
        
        # Add parallel execution
        if options['parallel']:
            cmd.extend(['-n', str(options['workers'])])
        
        # Add coverage
        if options['coverage']:
            cmd.extend(['--cov=.', '--cov-report=term-missing'])
            
            if options['html_report']:
                cmd.append('--cov-report=html:htmlcov')
            
            if options['xml_report']:
                cmd.append('--cov-report=xml')
        
        # Add JUnit XML report
        if options['junit_xml']:
            cmd.extend(['--junitxml', options['junit_xml']])
        
        # Add pattern
        if options['pattern']:
            cmd.extend(['-k', options['pattern']])
        
        # Add markers
        if options['markers']:
            cmd.extend(['-m', options['markers']])
        
        # Add app filter
        if options['app']:
            cmd.append(f'{options["app"]}/')
        
        # Add timeout
        cmd.extend(['--timeout', str(options['timeout'])])
        
        # Add Django settings
        cmd.extend(['--ds', 'backend.test_settings'])
        
        return cmd
    
    def execute_command(self, cmd):
        """Execute the test command."""
        self.stdout.write(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('Tests completed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Tests failed!')
                )
                sys.exit(result.returncode)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Command failed: {e}')
            )
            sys.exit(e.returncode)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('pytest not found. Please install it: pip install pytest pytest-django')
            )
            sys.exit(1)
