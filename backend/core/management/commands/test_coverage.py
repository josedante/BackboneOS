"""
Management command for generating comprehensive test coverage reports.

This command provides detailed coverage analysis including:
- Overall coverage percentage
- Coverage by module/file
- Coverage by line
- Missing line coverage
- Coverage trends over time
- HTML and XML reports
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """Generate comprehensive test coverage reports."""
    
    help = 'Generate comprehensive test coverage reports'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--html',
            action='store_true',
            help='Generate HTML coverage report'
        )
        
        parser.add_argument(
            '--xml',
            action='store_true',
            help='Generate XML coverage report'
        )
        
        parser.add_argument(
            '--json',
            action='store_true',
            help='Generate JSON coverage report'
        )
        
        parser.add_argument(
            '--fail-under',
            type=float,
            default=80.0,
            help='Fail if coverage is below this percentage'
        )
        
        parser.add_argument(
            '--include',
            type=str,
            help='Include only these files/modules'
        )
        
        parser.add_argument(
            '--omit',
            type=str,
            help='Omit these files/modules from coverage'
        )
        
        parser.add_argument(
            '--show-missing',
            action='store_true',
            help='Show missing line numbers'
        )
        
        parser.add_argument(
            '--skip-covered',
            action='store_true',
            help='Skip files with 100% coverage'
        )
        
        parser.add_argument(
            '--precision',
            type=int,
            default=2,
            help='Number of decimal places in coverage percentage'
        )
        
        parser.add_argument(
            '--sort',
            choices=['name', 'coverage', 'lines'],
            default='coverage',
            help='Sort coverage report by this field'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='coverage_reports',
            help='Directory for coverage reports'
        )
        
        parser.add_argument(
            '--compare',
            type=str,
            help='Compare with previous coverage report'
        )
        
        parser.add_argument(
            '--trend',
            action='store_true',
            help='Show coverage trend over time'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write(
            self.style.SUCCESS('Generating coverage report...')
        )
        
        # Create output directory
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        # Run tests with coverage
        self.run_tests_with_coverage(options)
        
        # Generate reports
        if options['html']:
            self.generate_html_report(options)
        
        if options['xml']:
            self.generate_xml_report(options)
        
        if options['json']:
            self.generate_json_report(options)
        
        # Show coverage summary
        self.show_coverage_summary(options)
        
        # Check coverage threshold
        self.check_coverage_threshold(options)
        
        # Show trend if requested
        if options['trend']:
            self.show_coverage_trend(options)
    
    def run_tests_with_coverage(self, options):
        """Run tests with coverage collection."""
        settings_module = os.environ.get(
            'DJANGO_SETTINGS_MODULE', 'backend.test_settings'
        )
        cmd = [
            'python', '-m', 'pytest',
            '--cov=.',
            '--cov-report=term-missing',
            '--ds', settings_module
        ]
        
        # Add coverage options
        if options['include']:
            cmd.extend(['--cov-include', options['include']])
        
        if options['omit']:
            cmd.extend(['--cov-omit', options['omit']])
        
        if options['show_missing']:
            cmd.append('--cov-report=term-missing')
        
        if options['skip_covered']:
            cmd.append('--cov-report=term-missing:skip-covered')
        
        # Add precision
        cmd.extend(['--cov-report=term-missing:precision={}'.format(options['precision'])])
        
        # Add sort
        cmd.extend(['--cov-report=term-missing:sort={}'.format(options['sort'])])
        
        self.stdout.write(f"Running tests with coverage: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode != 0:
                self.stdout.write(
                    self.style.ERROR('Tests failed during coverage collection')
                )
                self.stdout.write(result.stderr)
                sys.exit(result.returncode)
            
            self.stdout.write(result.stdout)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Coverage collection failed: {e}')
            )
            sys.exit(e.returncode)
    
    def generate_html_report(self, options):
        """Generate HTML coverage report."""
        self.stdout.write('Generating HTML coverage report...')
        
        cmd = [
            'python', '-m', 'coverage', 'html',
            '-d', os.path.join(options['output_dir'], 'htmlcov')
        ]
        
        if options['include']:
            cmd.extend(['--include', options['include']])
        
        if options['omit']:
            cmd.extend(['--omit', options['omit']])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'HTML report generated: {options["output_dir"]}/htmlcov/index.html'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate HTML report')
                )
                self.stdout.write(result.stderr)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'HTML report generation failed: {e}')
            )
    
    def generate_xml_report(self, options):
        """Generate XML coverage report."""
        self.stdout.write('Generating XML coverage report...')
        
        xml_file = os.path.join(options['output_dir'], 'coverage.xml')
        
        cmd = [
            'python', '-m', 'coverage', 'xml',
            '-o', xml_file
        ]
        
        if options['include']:
            cmd.extend(['--include', options['include']])
        
        if options['omit']:
            cmd.extend(['--omit', options['omit']])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'XML report generated: {xml_file}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate XML report')
                )
                self.stdout.write(result.stderr)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'XML report generation failed: {e}')
            )
    
    def generate_json_report(self, options):
        """Generate JSON coverage report."""
        self.stdout.write('Generating JSON coverage report...')
        
        json_file = os.path.join(options['output_dir'], 'coverage.json')
        
        cmd = [
            'python', '-m', 'coverage', 'json',
            '-o', json_file
        ]
        
        if options['include']:
            cmd.extend(['--include', options['include']])
        
        if options['omit']:
            cmd.extend(['--omit', options['omit']])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'JSON report generated: {json_file}')
            )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate JSON report')
                )
                self.stdout.write(result.stderr)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'JSON report generation failed: {e}')
            )
    
    def show_coverage_summary(self, options):
        """Show coverage summary."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('COVERAGE SUMMARY')
        self.stdout.write('='*50)
        
        cmd = ['python', '-m', 'coverage', 'report']
        
        if options['include']:
            cmd.extend(['--include', options['include']])
        
        if options['omit']:
            cmd.extend(['--omit', options['omit']])
        
        if options['show_missing']:
            cmd.append('--show-missing')
        
        if options['skip_covered']:
            cmd.append('--skip-covered')
        
        cmd.extend(['--precision', str(options['precision'])])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(result.stdout)
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate coverage summary')
                )
                self.stdout.write(result.stderr)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Coverage summary failed: {e}')
            )
    
    def check_coverage_threshold(self, options):
        """Check if coverage meets the threshold."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('COVERAGE THRESHOLD CHECK')
        self.stdout.write('='*50)
        
        cmd = [
            'python', '-m', 'coverage', 'report',
            '--fail-under', str(options['fail_under'])
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Coverage threshold met: >= {options["fail_under"]}%'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Coverage threshold not met: < {options["fail_under"]}%'
                    )
                )
                sys.exit(1)
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Coverage threshold check failed: {e}')
            )
            sys.exit(1)
    
    def show_coverage_trend(self, options):
        """Show coverage trend over time."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('COVERAGE TREND')
        self.stdout.write('='*50)
        
        # This would require storing historical coverage data
        # For now, just show current coverage
        self.stdout.write('Coverage trend analysis not yet implemented.')
        self.stdout.write('Consider using tools like codecov or coveralls for trend analysis.')
