"""
Management command to manage touchpoint resolution cache.

This command provides utilities for cache warming, clearing, and monitoring
for the touchpoint resolution system.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.db import transaction
from typing import Dict, Any, List
import time

from connectors.models import TouchpointMappingRule
from connectors.mapping_providers import DatabaseMappingProvider, CachedMappingProvider
from connectors.resolvers import DefaultTouchpointResolver, CachedTouchpointResolver
from connectors.protocols import TouchpointHint


class Command(BaseCommand):
    help = "Manage touchpoint resolution cache"
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')
        
        # Clear command
        clear_parser = subparsers.add_parser('clear', help='Clear touchpoint cache')
        clear_parser.add_argument(
            '--pattern',
            help='Cache key pattern to clear (default: all touchpoint cache)'
        )
        
        # Warm command
        warm_parser = subparsers.add_parser('warm', help='Warm touchpoint cache')
        warm_parser.add_argument(
            '--connector-type',
            help='Specific connector type to warm (default: all)'
        )
        warm_parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for warming (default: 100)'
        )
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show cache statistics')
        stats_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed cache statistics'
        )
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test cache performance')
        test_parser.add_argument(
            '--iterations',
            type=int,
            default=100,
            help='Number of test iterations (default: 100)'
        )
        test_parser.add_argument(
            '--with-cache',
            action='store_true',
            help='Test with cache enabled'
        )
        test_parser.add_argument(
            '--without-cache',
            action='store_true',
            help='Test without cache (baseline)'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if not action:
            self.stdout.write(self.style.ERROR("Please specify an action. Use --help for available actions."))
            return
        
        if action == 'clear':
            self._clear_cache(options)
        elif action == 'warm':
            self._warm_cache(options)
        elif action == 'stats':
            self._show_stats(options)
        elif action == 'test':
            self._test_performance(options)
    
    def _clear_cache(self, options):
        """Clear touchpoint cache."""
        pattern = options.get('pattern', 'touchpoint_*')
        
        try:
            if pattern == 'touchpoint_*':
                # Clear all touchpoint-related cache
                cache.delete_many(cache.keys('touchpoint_*'))
                self.stdout.write(
                    self.style.SUCCESS("✅ Cleared all touchpoint cache")
                )
            else:
                # Clear specific pattern
                keys = cache.keys(pattern)
                if keys:
                    cache.delete_many(keys)
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Cleared {len(keys)} cache entries matching '{pattern}'")
                    )
                else:
                    self.stdout.write(f"No cache entries found matching '{pattern}'")
        
        except Exception as e:
            raise CommandError(f"Failed to clear cache: {e}")
    
    def _warm_cache(self, options):
        """Warm touchpoint cache."""
        connector_type = options.get('connector_type')
        batch_size = options['batch_size']
        
        self.stdout.write("Warming touchpoint cache...")
        
        try:
            # Initialize cached provider
            cached_provider = CachedMappingProvider()
            
            # Get mapping rules to warm
            queryset = TouchpointMappingRule.objects.filter(is_active=True)
            if connector_type:
                queryset = queryset.filter(connector_type=connector_type)
            
            total_rules = queryset.count()
            self.stdout.write(f"Found {total_rules} mapping rules to warm")
            
            if total_rules == 0:
                self.stdout.write("No mapping rules found to warm")
                return
            
            # Warm cache in batches
            warmed = 0
            for i in range(0, total_rules, batch_size):
                batch = queryset[i:i + batch_size]
                
                for rule in batch:
                    # Warm cache for this rule
                    cached_provider.warm_cache_specific_rule(rule)
                    warmed += 1
                
                if warmed % (batch_size * 5) == 0:  # Progress every 5 batches
                    self.stdout.write(f"Warmed {warmed}/{total_rules} rules...")
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Warmed cache for {warmed} mapping rules")
            )
        
        except Exception as e:
            raise CommandError(f"Failed to warm cache: {e}")
    
    def _show_stats(self, options):
        """Show cache statistics."""
        detailed = options.get('detailed', False)
        
        try:
            # Get cache statistics
            cache_keys = cache.keys('touchpoint_*')
            total_keys = len(cache_keys)
            
            self.stdout.write("\nTouchpoint Cache Statistics:")
            self.stdout.write("=" * 40)
            self.stdout.write(f"Total cache keys: {total_keys}")
            
            if detailed and total_keys > 0:
                # Analyze key patterns
                patterns = {}
                for key in cache_keys:
                    # Extract pattern from key
                    if 'mapping' in key:
                        pattern = 'mapping_rules'
                    elif 'resolution' in key:
                        pattern = 'touchpoint_resolution'
                    else:
                        pattern = 'other'
                    
                    patterns[pattern] = patterns.get(pattern, 0) + 1
                
                self.stdout.write("\nKey patterns:")
                for pattern, count in patterns.items():
                    self.stdout.write(f"  {pattern}: {count} keys")
                
                # Show sample keys
                self.stdout.write(f"\nSample keys (first 10):")
                for key in cache_keys[:10]:
                    self.stdout.write(f"  {key}")
                
                if total_keys > 10:
                    self.stdout.write(f"  ... and {total_keys - 10} more")
            
            # Test cache performance
            start_time = time.time()
            test_key = 'touchpoint_test_performance'
            cache.set(test_key, 'test_value', 60)
            cache.get(test_key)
            cache.delete(test_key)
            end_time = time.time()
            
            self.stdout.write(f"\nCache performance test:")
            self.stdout.write(f"  Set/Get/Delete time: {(end_time - start_time) * 1000:.2f}ms")
        
        except Exception as e:
            raise CommandError(f"Failed to get cache statistics: {e}")
    
    def _test_performance(self, options):
        """Test cache performance."""
        iterations = options['iterations']
        with_cache = options.get('with_cache', True)
        without_cache = options.get('without_cache', True)
        
        if not with_cache and not without_cache:
            self.stdout.write("Please specify --with-cache and/or --without-cache")
            return
        
        self.stdout.write(f"Testing touchpoint resolution performance ({iterations} iterations)...")
        
        # Create test data
        test_hints = [
            TouchpointHint(
                code='web.page_read',
                channel_code='web',
                medium_code='organic',
                label='Web Page View'
            ),
            TouchpointHint(
                code='email.open',
                channel_code='email',
                medium_code='email',
                label='Email Open'
            ),
            TouchpointHint(
                code='whatsapp.message_received',
                channel_code='whatsapp',
                medium_code='whatsapp',
                label='WhatsApp Message'
            )
        ]
        
        results = {}
        
        # Test without cache
        if without_cache:
            self.stdout.write("Testing without cache...")
            start_time = time.time()
            
            resolver = DefaultTouchpointResolver(DatabaseMappingProvider())
            
            for i in range(iterations):
                hint = test_hints[i % len(test_hints)]
                resolver.resolve(hint, connector_type='test', source_identifier='')
            
            end_time = time.time()
            results['without_cache'] = {
                'time': end_time - start_time,
                'avg_time': (end_time - start_time) / iterations * 1000  # ms
            }
        
        # Test with cache
        if with_cache:
            self.stdout.write("Testing with cache...")
            
            # Warm cache first
            cached_provider = CachedMappingProvider()
            cached_provider.warm_cache()
            
            start_time = time.time()
            
            resolver = CachedTouchpointResolver(cached_provider)
            
            for i in range(iterations):
                hint = test_hints[i % len(test_hints)]
                resolver.resolve(hint, connector_type='test', source_identifier='')
            
            end_time = time.time()
            results['with_cache'] = {
                'time': end_time - start_time,
                'avg_time': (end_time - start_time) / iterations * 1000  # ms
            }
        
        # Show results
        self.stdout.write("\nPerformance Test Results:")
        self.stdout.write("=" * 50)
        
        for test_type, result in results.items():
            self.stdout.write(f"{test_type.replace('_', ' ').title()}:")
            self.stdout.write(f"  Total time: {result['time']:.3f}s")
            self.stdout.write(f"  Average time: {result['avg_time']:.2f}ms per resolution")
        
        if len(results) == 2:
            speedup = results['without_cache']['time'] / results['with_cache']['time']
            self.stdout.write(f"\nCache speedup: {speedup:.2f}x faster")
        
        self.stdout.write("=" * 50)
