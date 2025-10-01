"""
Management command to ensure all websites have channels.
"""

from django.core.management.base import BaseCommand
from websites.models import Website


class Command(BaseCommand):
    help = 'Ensure all websites have channels created'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        websites_without_channels = Website.objects.filter(channel__isnull=True)
        websites_with_wrong_source_type = Website.objects.filter(
            channel__isnull=False,
            channel__source_type__in=['external', 'direct', 'unknown']
        )
        
        total_websites_to_fix = websites_without_channels.count() + websites_with_wrong_source_type.count()
        
        if total_websites_to_fix == 0:
            self.stdout.write(
                self.style.SUCCESS('All websites already have properly configured channels.')
            )
            return
        
        self.stdout.write(f'Found {total_websites_to_fix} websites that need channel updates:')
        
        # Handle websites without channels
        if websites_without_channels.exists():
            self.stdout.write(f'  {websites_without_channels.count()} websites without channels:')
            for website in websites_without_channels:
                if dry_run:
                    self.stdout.write(f'    Would create channel for: {website.name} ({website.base_url})')
                else:
                    channel = website.ensure_channel()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    Created channel "{channel.code}" for: {website.name}'
                        )
                    )
        
        # Handle websites with wrong source_type
        if websites_with_wrong_source_type.exists():
            self.stdout.write(f'  {websites_with_wrong_source_type.count()} websites with incorrect source_type:')
            for website in websites_with_wrong_source_type:
                if dry_run:
                    self.stdout.write(
                        f'    Would update channel "{website.channel.code}" source_type to "owned" for: {website.name}'
                    )
                else:
                    website.channel.source_type = 'owned'
                    website.channel.save(update_fields=['source_type'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    Updated channel "{website.channel.code}" source_type to "owned" for: {website.name}'
                        )
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Run without --dry-run to create/update the channels.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All website channels have been created/updated.')
            )
