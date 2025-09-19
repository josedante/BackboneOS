"""
Management command to test touchpoint resolution functionality.

This command allows testing the touchpoint resolution system with
various scenarios and connector types.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from typing import Dict, Any
import json

from interactions.models import Interaction, Action, Agent
from connectors.models import TouchpointMappingRule
from connectors.resolvers import DefaultTouchpointResolver
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol


class MockConnector(TouchpointInferenceProtocol):
    """Mock connector for testing purposes."""
    
    def __init__(self, hint: TouchpointHint, connector_type: str = "test"):
        self.hint = hint
        self.connector_type = connector_type
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return self.hint


class Command(BaseCommand):
    help = "Test touchpoint resolution functionality"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            choices=['basic', 'mapping', 'web', 'email', 'whatsapp', 'all'],
            default='basic',
            help='Test scenario to run (default: basic)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--create-mapping-rules',
            action='store_true',
            help='Create sample mapping rules for testing'
        )
    
    def handle(self, *args, **options):
        scenario = options['scenario']
        verbose = options['verbose']
        create_rules = options['create_mapping_rules']
        
        self.stdout.write(
            self.style.SUCCESS("Starting touchpoint resolution tests...")
        )
        
        # Initialize resolver
        resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
        
        # Create sample mapping rules if requested
        if create_rules:
            self._create_sample_mapping_rules()
        
        # Run tests based on scenario
        if scenario == 'all':
            self._run_all_tests(resolver, verbose)
        else:
            self._run_scenario_test(scenario, resolver, verbose)
        
        self.stdout.write(
            self.style.SUCCESS("Touchpoint resolution tests completed!")
        )
    
    def _run_all_tests(self, resolver, verbose: bool):
        """Run all test scenarios."""
        scenarios = ['basic', 'mapping', 'web', 'email', 'whatsapp']
        
        for scenario in scenarios:
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"Running {scenario.upper()} scenario")
            self.stdout.write('='*50)
            self._run_scenario_test(scenario, resolver, verbose)
    
    def _run_scenario_test(self, scenario: str, resolver, verbose: bool):
        """Run a specific test scenario."""
        if scenario == 'basic':
            self._test_basic_resolution(resolver, verbose)
        elif scenario == 'mapping':
            self._test_mapping_rules(resolver, verbose)
        elif scenario == 'web':
            self._test_web_scenarios(resolver, verbose)
        elif scenario == 'email':
            self._test_email_scenarios(resolver, verbose)
        elif scenario == 'whatsapp':
            self._test_whatsapp_scenarios(resolver, verbose)
    
    def _test_basic_resolution(self, resolver, verbose: bool):
        """Test basic touchpoint resolution."""
        self.stdout.write("Testing basic touchpoint resolution...")
        
        # Test 1: Basic touchpoint creation
        hint = TouchpointHint(
            code='test.basic',
            channel_code='test',
            medium_code='test',
            label='Test Basic Touchpoint'
        )
        
        mock_connector = MockConnector(hint)
        touchpoint = resolver.resolve(mock_connector)
        
        self.stdout.write(f"✅ Created touchpoint: {touchpoint.code}")
        if verbose:
            self.stdout.write(f"   Name: {touchpoint.name}")
            self.stdout.write(f"   TouchpointClass: {touchpoint.touchpoint_class.code if touchpoint.touchpoint_class else 'None'}")
        
        # Test 2: Reuse existing touchpoint
        touchpoint2 = resolver.resolve(mock_connector)
        if touchpoint.id == touchpoint2.id:
            self.stdout.write("✅ Correctly reused existing touchpoint")
        else:
            self.stdout.write("❌ Failed to reuse existing touchpoint")
    
    def _test_mapping_rules(self, resolver, verbose: bool):
        """Test mapping rule functionality."""
        self.stdout.write("Testing mapping rules...")
        
        # Create a test mapping rule
        mapping_rule = TouchpointMappingRule.objects.create(
            connector_type='test',
            source_identifier='',
            event_code='test.basic',
            touchpoint_code='test.mapped',
            touchpoint_label='Mapped Test Touchpoint',
            channel_code='mapped',
            medium_code='mapped',
            priority=200
        )
        
        try:
            # Test with mapping rule
            hint = TouchpointHint(
                code='test.basic',
                channel_code='test',
                medium_code='test',
                label='Test Basic Touchpoint'
            )
            
            mock_connector = MockConnector(hint)
            touchpoint = resolver.resolve(mock_connector)
            
            if touchpoint.code == 'test.mapped':
                self.stdout.write("✅ Mapping rule applied correctly")
                if verbose:
                    self.stdout.write(f"   Original code: test.basic")
                    self.stdout.write(f"   Mapped code: {touchpoint.code}")
            else:
                self.stdout.write("❌ Mapping rule not applied")
        
        finally:
            # Clean up
            mapping_rule.delete()
    
    def _test_web_scenarios(self, resolver, verbose: bool):
        """Test web-specific scenarios."""
        self.stdout.write("Testing web scenarios...")
        
        scenarios = [
            {
                'name': 'Page View',
                'hint': TouchpointHint(
                    code='web.page_read',
                    channel_code='web',
                    medium_code='organic',
                    label='Web Page View',
                    metadata={'url': '/products', 'utm_source': 'google'}
                )
            },
            {
                'name': 'Form Submit',
                'hint': TouchpointHint(
                    code='web.form_submit',
                    channel_code='web',
                    medium_code='paid',
                    label='Web Form Submit',
                    metadata={'form_type': 'contact', 'utm_campaign': 'summer2024'}
                )
            },
            {
                'name': 'Social Traffic',
                'hint': TouchpointHint(
                    code='web.click',
                    channel_code='web',
                    medium_code='social',
                    label='Web Click',
                    metadata={'utm_source': 'facebook', 'utm_medium': 'social'})
            }
        ]
        
        for scenario in scenarios:
            mock_connector = MockConnector(scenario['hint'], 'web')
            touchpoint = resolver.resolve(mock_connector)
            
            self.stdout.write(f"✅ {scenario['name']}: {touchpoint.code}")
            if verbose:
                self.stdout.write(f"   Medium: {scenario['hint'].medium_code}")
                self.stdout.write(f"   Metadata: {scenario['hint'].metadata}")
    
    def _test_email_scenarios(self, resolver, verbose: bool):
        """Test email-specific scenarios."""
        self.stdout.write("Testing email scenarios...")
        
        scenarios = [
            {
                'name': 'Email Open',
                'hint': TouchpointHint(
                    code='email.open',
                    channel_code='email',
                    medium_code='email',
                    label='Email Open',
                    metadata={'campaign_id': 'newsletter_001', 'recipient': 'user@example.com'}
                )
            },
            {
                'name': 'Email Click',
                'hint': TouchpointHint(
                    code='email.click',
                    channel_code='email',
                    medium_code='email',
                    label='Email Click',
                    metadata={'campaign_id': 'promo_002', 'link_url': '/offers'}
                )
            }
        ]
        
        for scenario in scenarios:
            mock_connector = MockConnector(scenario['hint'], 'email')
            touchpoint = resolver.resolve(mock_connector)
            
            self.stdout.write(f"✅ {scenario['name']}: {touchpoint.code}")
            if verbose:
                self.stdout.write(f"   Campaign: {scenario['hint'].metadata.get('campaign_id', 'N/A')}")
    
    def _test_whatsapp_scenarios(self, resolver, verbose: bool):
        """Test WhatsApp-specific scenarios."""
        self.stdout.write("Testing WhatsApp scenarios...")
        
        scenarios = [
            {
                'name': 'Message Received',
                'hint': TouchpointHint(
                    code='whatsapp.message_received',
                    channel_code='whatsapp',
                    medium_code='whatsapp',
                    label='WhatsApp Message Received',
                    metadata={'phone_number': '+1234567890', 'message_type': 'text'}
                )
            },
            {
                'name': 'Media Sent',
                'hint': TouchpointHint(
                    code='whatsapp.media_sent',
                    channel_code='whatsapp',
                    medium_code='whatsapp',
                    label='WhatsApp Media Sent',
                    metadata={'phone_number': '+1234567890', 'media_type': 'image'}
                )
            }
        ]
        
        for scenario in scenarios:
            mock_connector = MockConnector(scenario['hint'], 'whatsapp')
            touchpoint = resolver.resolve(mock_connector)
            
            self.stdout.write(f"✅ {scenario['name']}: {touchpoint.code}")
            if verbose:
                self.stdout.write(f"   Phone: {scenario['hint'].metadata.get('phone_number', 'N/A')}")
    
    def _create_sample_mapping_rules(self):
        """Create sample mapping rules for testing."""
        self.stdout.write("Creating sample mapping rules...")
        
        sample_rules = [
            {
                'connector_type': 'web',
                'source_identifier': '',
                'event_code': 'web.form_submit',
                'touchpoint_code': 'web.lead_form',
                'touchpoint_label': 'Lead Form Submission',
                'channel_code': 'web',
                'medium_code': 'lead_generation',
                'priority': 150
            },
            {
                'connector_type': 'email',
                'source_identifier': '',
                'event_code': 'email.open',
                'touchpoint_code': 'email.newsletter_open',
                'touchpoint_label': 'Newsletter Open',
                'channel_code': 'email',
                'medium_code': 'newsletter',
                'priority': 120
            }
        ]
        
        for rule_data in sample_rules:
            rule, created = TouchpointMappingRule.objects.get_or_create(
                connector_type=rule_data['connector_type'],
                source_identifier=rule_data['source_identifier'],
                event_code=rule_data['event_code'],
                defaults=rule_data
            )
            
            if created:
                self.stdout.write(f"✅ Created mapping rule: {rule}")
            else:
                self.stdout.write(f"ℹ️  Mapping rule already exists: {rule}")
