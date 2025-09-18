# 🚀 Touchpoint Resolution System - Implementation Plan

## 📋 Executive Summary

This document outlines a phased implementation plan for the Touchpoint Resolution System in BackboneOS. The system will provide automatic, configurable touchpoint creation for all connector types while maintaining clean separation between generic framework logic (connectors app) and specialized connector logic (websites, emails, etc.).

## 🎯 Core Principles

1. **Generic Framework**: Connectors app provides the abstract framework and protocols
2. **Specialized Implementations**: Each connector app implements its own touchpoint inference logic
3. **Configurable Business Rules**: Admin-configurable mappings without code changes
4. **Backward Compatibility**: Existing functionality remains intact during migration
5. **Performance First**: Optimized queries and caching for production scale

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CONNECTORS APP                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Protocols     │  │   Resolvers     │  │   Mappings  │ │
│  │   & Interfaces  │  │   (Generic)     │  │   (Config)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   WEBSITES APP                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Web Adapters  │  │   UTM Analysis  │  │   Web Logic │ │
│  │   (Specialized) │  │   (Specialized) │  │   (Special) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 INTERACTIONS APP                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Touchpoints   │  │   Channels      │  │  Interactions│ │
│  │   (Core)        │  │   (Core)        │  │   (Core)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Implementation Phases

### **Phase 1: Core Framework (Week 1-2)**
*Foundation and protocols*

### **Phase 2: Websites Integration (Week 3-4)**
*First concrete implementation*

### **Phase 3: Configuration & Admin (Week 5-6)**
*Business rule management*

### **Phase 4: Migration & Backfill (Week 7-8)**
*Data migration and cleanup*

### **Phase 5: Future Connectors (Week 9+)**
*Email, WhatsApp, etc.*

---

## 🔧 Phase 1: Core Framework

### **1.1 Protocols and Interfaces**

**File: `connectors/protocols.py`**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class TouchpointHint:
    """Standardized hint structure for touchpoint inference."""
    code: Optional[str] = None              # e.g. "web.page_read", "email.open"
    channel_code: Optional[str] = None      # e.g. "web", "email", "chat"
    medium_code: Optional[str] = None       # e.g. "organic", "paid", "referral"
    label: Optional[str] = None             # Human-friendly name
    metadata: dict = None                   # Additional context
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})

class TouchpointInferenceProtocol(Protocol):
    """Protocol that connector models must implement."""
    def infer_touchpoint_hint(self) -> TouchpointHint: ...

class TouchpointResolverProtocol(Protocol):
    """Protocol for touchpoint resolution strategies."""
    def resolve(self, subject: TouchpointInferenceProtocol) -> 'Touchpoint': ...

class MappingProviderProtocol(Protocol):
    """Protocol for mapping rule providers."""
    def lookup_mapping(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> Optional['MappingRule']: ...
```

### **1.2 Generic Resolver Framework**

**File: `connectors/resolvers.py`**
```python
from django.db import transaction
from interactions.models import Touchpoint, TouchpointClass, Channel
from .protocols import TouchpointInferenceProtocol, TouchpointResolverProtocol, TouchpointHint

class DefaultTouchpointResolver:
    """
    Generic touchpoint resolver that works with any connector type.
    Delegates specialized logic to connector-specific adapters.
    """
    
    def __init__(self, mapping_provider: 'MappingProviderProtocol'):
        self.mapping_provider = mapping_provider
    
    @transaction.atomic
    def resolve(self, subject: TouchpointInferenceProtocol) -> Touchpoint:
        """
        Resolve touchpoint for any connector type.
        
        Strategy:
        1. Get hint from connector-specific inference
        2. Apply configurable mapping overrides
        3. Fallback to connector-specific defaults
        4. Create or get touchpoint
        """
        hint = subject.infer_touchpoint_hint()
        
        # Apply mapping overrides
        mapping_rule = self.mapping_provider.lookup_mapping(subject, hint)
        if mapping_rule:
            hint = self._apply_mapping_rule(hint, mapping_rule)
        
        # Ensure we have required fields
        final_hint = self._ensure_required_fields(subject, hint)
        
        # Create or get touchpoint
        return self._get_or_create_touchpoint(final_hint)
    
    def _apply_mapping_rule(self, hint: TouchpointHint, rule: 'MappingRule') -> TouchpointHint:
        """Apply mapping rule overrides to hint."""
        return TouchpointHint(
            code=rule.touchpoint_code or hint.code,
            channel_code=rule.channel_code or hint.channel_code,
            medium_code=rule.medium_code or hint.medium_code,
            label=rule.label or hint.label,
            metadata={**hint.metadata, **rule.metadata}
        )
    
    def _ensure_required_fields(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> TouchpointHint:
        """Ensure hint has required fields, using connector-specific defaults."""
        # This will be overridden by connector-specific resolvers
        return hint
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
        """Create or get touchpoint from hint."""
        # Get or create channel
        channel = None
        if hint.channel_code:
            channel, _ = Channel.objects.get_or_create(
                code=hint.channel_code,
                defaults={'name': hint.channel_code.title()}
            )
        
        # Get or create touchpoint class
        touchpoint_class = None
        if hint.code:
            class_code = hint.code.split('.')[0]  # e.g., "web" from "web.page_read"
            touchpoint_class, _ = TouchpointClass.objects.get_or_create(
                code=class_code,
                defaults={
                    'name': class_code.title(),
                    'channel': channel
                }
            )
        
        # Create or get touchpoint
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=hint.code or f"generic.{subject.__class__.__name__.lower()}",
            defaults={
                'name': hint.label or hint.code or 'Generic Touchpoint',
                'touchpoint_class': touchpoint_class,
                'description': f"Auto-generated touchpoint for {subject.__class__.__name__}",
                'is_active': True
            }
        )
        
        return touchpoint
```

### **1.3 Mapping Configuration Model**

**File: `connectors/models.py` (additions)**
```python
# Add to existing models.py

class TouchpointMappingRule(BaseUUIDModelWithActiveStatus):
    """
    Configurable mapping rules for touchpoint resolution.
    Allows admins to override default touchpoint creation logic.
    """
    
    # Scope - which connector/source this applies to
    connector_type = models.CharField(max_length=50)  # "web", "email", "whatsapp"
    source_identifier = models.CharField(max_length=200, blank=True)  # website URL, email domain, etc.
    
    # Event matching
    event_code = models.CharField(max_length=100)  # "web.page_read", "email.open"
    
    # Resulting touchpoint configuration
    touchpoint_code = models.CharField(max_length=100)
    touchpoint_label = models.CharField(max_length=200, blank=True)
    channel_code = models.CharField(max_length=50, blank=True)
    medium_code = models.CharField(max_length=50, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    priority = models.PositiveIntegerField(default=100)  # Higher = more specific
    
    class Meta:
        ordering = ['-priority', 'connector_type', 'event_code']
        indexes = [
            models.Index(fields=['connector_type', 'event_code']),
            models.Index(fields=['source_identifier', 'event_code']),
            models.Index(fields=['priority']),
        ]
        unique_together = [
            ('connector_type', 'source_identifier', 'event_code'),
        ]
    
    def __str__(self):
        return f"{self.connector_type}:{self.event_code} -> {self.touchpoint_code}"
```

### **1.4 Database Mapping Provider**

**File: `connectors/mapping_providers.py`**
```python
from typing import Optional
from .protocols import TouchpointInferenceProtocol, TouchpointHint, MappingProviderProtocol
from .models import TouchpointMappingRule

class DatabaseMappingProvider:
    """
    Database-backed mapping provider for configurable touchpoint rules.
    """
    
    def lookup_mapping(
        self, 
        subject: TouchpointInferenceProtocol, 
        hint: TouchpointHint
    ) -> Optional[TouchpointMappingRule]:
        """
        Look up mapping rule for the given subject and hint.
        
        Priority:
        1. Specific source + event code
        2. Generic connector type + event code
        3. Generic event code only
        """
        if not hint.code:
            return None
        
        # Get connector type from subject class
        connector_type = self._get_connector_type(subject)
        source_identifier = self._get_source_identifier(subject)
        
        # Try specific source first
        if source_identifier:
            rule = TouchpointMappingRule.objects.filter(
                connector_type=connector_type,
                source_identifier=source_identifier,
                event_code=hint.code,
                is_active=True
            ).order_by('-priority').first()
            
            if rule:
                return rule
        
        # Try generic connector type
        rule = TouchpointMappingRule.objects.filter(
            connector_type=connector_type,
            source_identifier='',
            event_code=hint.code,
            is_active=True
        ).order_by('-priority').first()
        
        if rule:
            return rule
        
        # Try generic event code
        rule = TouchpointMappingRule.objects.filter(
            connector_type='',
            source_identifier='',
            event_code=hint.code,
            is_active=True
        ).order_by('-priority').first()
        
        return rule
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """Extract connector type from subject class name."""
        class_name = subject.__class__.__name__.lower()
        if class_name.startswith('web'):
            return 'web'
        elif class_name.startswith('email'):
            return 'email'
        elif class_name.startswith('whatsapp'):
            return 'whatsapp'
        return 'generic'
    
    def _get_source_identifier(self, subject: TouchpointInferenceProtocol) -> str:
        """Extract source identifier from subject."""
        # This will be overridden by connector-specific providers
        return ''
```

---

## 🌐 Phase 2: Websites Integration

### **2.1 Web-Specific Touchpoint Resolver**

**File: `websites/resolvers.py`**
```python
from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint
from .models import WebInteraction, Website

class WebTouchpointResolver(DefaultTouchpointResolver):
    """
    Web-specific touchpoint resolver with UTM analysis and web-specific defaults.
    """
    
    def _ensure_required_fields(self, subject, hint: TouchpointHint) -> TouchpointHint:
        """Ensure web-specific required fields."""
        if not hint.channel_code:
            hint = TouchpointHint(
                code=hint.code,
                channel_code='web',
                medium_code=hint.medium_code or 'unknown',
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Analyze UTM parameters if available
        if hasattr(subject, 'utm_medium') and subject.utm_medium:
            medium = self._analyze_utm_medium(subject.utm_medium)
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code=medium,
                label=hint.label,
                metadata=hint.metadata
            )
        
        return hint
    
    def _analyze_utm_medium(self, utm_medium: str) -> str:
        """Analyze UTM medium to determine proper medium code."""
        utm_medium = utm_medium.lower()
        
        if utm_medium in ['cpc', 'ppc', 'paid']:
            return 'paid'
        elif utm_medium in ['email', 'newsletter']:
            return 'email'
        elif utm_medium in ['social', 'facebook', 'twitter', 'linkedin']:
            return 'social'
        elif utm_medium in ['referral', 'referrer']:
            return 'referral'
        elif utm_medium in ['organic', 'seo']:
            return 'organic'
        else:
            return utm_medium
```

### **2.2 Web-Specific Mapping Provider**

**File: `websites/mapping_providers.py`**
```python
from connectors.mapping_providers import DatabaseMappingProvider
from connectors.protocols import TouchpointInferenceProtocol

class WebMappingProvider(DatabaseMappingProvider):
    """
    Web-specific mapping provider that understands website URLs and UTM parameters.
    """
    
    def _get_source_identifier(self, subject: TouchpointInferenceProtocol) -> str:
        """Extract website URL as source identifier."""
        if hasattr(subject, 'website') and subject.website:
            return subject.website.base_url
        return ''
```

### **2.3 Web Touchpoint Adapters**

**File: `websites/adapters.py`**
```python
from urllib.parse import urlparse, parse_qs
from connectors.protocols import TouchpointHint
from .models import WebInteraction

def infer_web_touchpoint_hint(web_interaction: WebInteraction) -> TouchpointHint:
    """
    Infer touchpoint hint from web interaction data.
    This is the specialized logic that belongs in the websites app.
    """
    
    # Determine event type and code
    if hasattr(web_interaction, 'event_type'):
        event_type = web_interaction.event_type
    else:
        event_type = 'page_read'  # Default for generic WebInteraction
    
    # Map event types to touchpoint codes
    event_code_map = {
        'page_read': 'web.page_read',
        'form_submit': 'web.form_submit',
        'click': 'web.click',
        'download': 'web.download',
        'video_play': 'web.video_play',
    }
    
    code = event_code_map.get(event_type, 'web.generic')
    
    # Create human-friendly label
    label_map = {
        'page_read': 'Web Page View',
        'form_submit': 'Web Form Submit',
        'click': 'Web Click',
        'download': 'Web Download',
        'video_play': 'Web Video Play',
    }
    
    label = label_map.get(event_type, 'Web Interaction')
    
    # Analyze UTM parameters for medium inference
    medium = 'organic'  # Default
    if hasattr(web_interaction, 'utm_medium') and web_interaction.utm_medium:
        medium = analyze_utm_medium(web_interaction.utm_medium)
    elif hasattr(web_interaction, 'referrer_url') and web_interaction.referrer_url:
        medium = analyze_referrer(web_interaction.referrer_url)
    
    # Build metadata
    metadata = {
        'event_type': event_type,
        'url': getattr(web_interaction, 'url', ''),
        'session_id': getattr(web_interaction, 'session_id', ''),
    }
    
    # Add UTM parameters if available
    for utm_param in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']:
        if hasattr(web_interaction, utm_param):
            value = getattr(web_interaction, utm_param)
            if value:
                metadata[utm_param] = value
    
    return TouchpointHint(
        code=code,
        channel_code='web',
        medium_code=medium,
        label=label,
        metadata=metadata
    )

def analyze_utm_medium(utm_medium: str) -> str:
    """Analyze UTM medium parameter."""
    utm_medium = utm_medium.lower()
    
    medium_map = {
        'cpc': 'paid',
        'ppc': 'paid',
        'paid': 'paid',
        'email': 'email',
        'social': 'social',
        'referral': 'referral',
        'organic': 'organic',
        'seo': 'organic',
    }
    
    return medium_map.get(utm_medium, utm_medium)

def analyze_referrer(referrer_url: str) -> str:
    """Analyze referrer URL to determine medium."""
    if not referrer_url:
        return 'direct'
    
    try:
        parsed = urlparse(referrer_url)
        hostname = parsed.hostname.lower() if parsed.hostname else ''
        
        # Social media domains
        social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'tiktok.com']
        if any(domain in hostname for domain in social_domains):
            return 'social'
        
        # Search engines
        search_domains = ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com']
        if any(domain in hostname for domain in search_domains):
            return 'organic'
        
        # If it's an external referrer, it's referral
        if hostname:
            return 'referral'
        
        return 'direct'
    except Exception:
        return 'unknown'
```

### **2.4 Update WebInteraction Model**

**File: `websites/models.py` (modifications)**
```python
# Add to existing WebInteraction class

from connectors.protocols import TouchpointInferenceProtocol, TouchpointHint
from .adapters import infer_web_touchpoint_hint

class WebInteraction(AbstractConnectorInteraction, TouchpointInferenceProtocol):
    # ... existing fields ...
    
    def infer_touchpoint_hint(self) -> TouchpointHint:
        """
        Implement TouchpointInferenceProtocol.
        Delegates to specialized web adapter.
        """
        return infer_web_touchpoint_hint(self)
    
    def _ensure_touchpoint(self):
        """
        Ensure this web interaction has a proper touchpoint.
        Uses the new touchpoint resolution system.
        """
        if not self.interaction.touchpoint_id:
            from .resolvers import WebTouchpointResolver
            from .mapping_providers import WebMappingProvider
            
            resolver = WebTouchpointResolver(WebMappingProvider())
            touchpoint = resolver.resolve(self)
            
            self.interaction.touchpoint = touchpoint
            self.interaction.save(update_fields=['touchpoint'])
    
    def save(self, *args, **kwargs):
        """Override save to ensure touchpoint resolution."""
        super().save(*args, **kwargs)
        self._ensure_touchpoint()
```

---

## ⚙️ Phase 3: Configuration & Admin

### **3.1 Admin Interface**

**File: `connectors/admin.py`**
```python
from django.contrib import admin
from .models import TouchpointMappingRule

@admin.register(TouchpointMappingRule)
class TouchpointMappingRuleAdmin(admin.ModelAdmin):
    list_display = [
        'connector_type', 'source_identifier', 'event_code', 
        'touchpoint_code', 'channel_code', 'medium_code', 'priority', 'is_active'
    ]
    list_filter = ['connector_type', 'is_active', 'channel_code', 'medium_code']
    search_fields = ['event_code', 'touchpoint_code', 'source_identifier']
    ordering = ['-priority', 'connector_type', 'event_code']
    
    fieldsets = (
        ('Scope', {
            'fields': ('connector_type', 'source_identifier', 'event_code')
        }),
        ('Touchpoint Configuration', {
            'fields': ('touchpoint_code', 'touchpoint_label', 'channel_code', 'medium_code')
        }),
        ('Advanced', {
            'fields': ('priority', 'metadata', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
```

### **3.2 Management Commands**

**File: `connectors/management/commands/test_touchpoint_resolution.py`**
```python
from django.core.management.base import BaseCommand
from websites.models import WebInteraction
from websites.resolvers import WebTouchpointResolver
from websites.mapping_providers import WebMappingProvider

class Command(BaseCommand):
    help = "Test touchpoint resolution for existing web interactions"
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Number of interactions to test')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        resolver = WebTouchpointResolver(WebMappingProvider())
        
        web_interactions = WebInteraction.objects.select_related('interaction')[:limit]
        
        for web_interaction in web_interactions:
            hint = web_interaction.infer_touchpoint_hint()
            touchpoint = resolver.resolve(web_interaction)
            
            self.stdout.write(f"WebInteraction {web_interaction.id}:")
            self.stdout.write(f"  Hint: {hint}")
            self.stdout.write(f"  Resolved Touchpoint: {touchpoint}")
            self.stdout.write("")
```

---

## 🔄 Phase 4: Migration & Backfill

### **4.1 Backfill Command**

**File: `connectors/management/commands/backfill_touchpoints.py`**
```python
from django.core.management.base import BaseCommand
from django.db import transaction
from websites.models import WebInteraction
from websites.resolvers import WebTouchpointResolver
from websites.mapping_providers import WebMappingProvider

class Command(BaseCommand):
    help = "Backfill touchpoints for existing interactions"
    
    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100, help='Batch size for processing')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
        parser.add_argument('--connector-type', choices=['web', 'email', 'whatsapp'], help='Specific connector type to process')
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        connector_type = options.get('connector_type')
        
        if connector_type == 'web' or not connector_type:
            self.backfill_web_interactions(batch_size, dry_run)
    
    def backfill_web_interactions(self, batch_size: int, dry_run: bool):
        """Backfill touchpoints for web interactions."""
        resolver = WebTouchpointResolver(WebMappingProvider())
        
        # Get web interactions without touchpoints
        queryset = WebInteraction.objects.filter(
            interaction__touchpoint__isnull=True
        ).select_related('interaction')
        
        total = queryset.count()
        self.stdout.write(f"Found {total} web interactions without touchpoints")
        
        processed = 0
        created = 0
        
        for batch in self.batch_queryset(queryset, batch_size):
            with transaction.atomic():
                for web_interaction in batch:
                    try:
                        if not dry_run:
                            touchpoint = resolver.resolve(web_interaction)
                            web_interaction.interaction.touchpoint = touchpoint
                            web_interaction.interaction.save(update_fields=['touchpoint'])
                            created += 1
                        
                        processed += 1
                        
                        if processed % 100 == 0:
                            self.stdout.write(f"Processed {processed}/{total} interactions")
                    
                    except Exception as e:
                        self.stderr.write(f"Error processing WebInteraction {web_interaction.id}: {e}")
        
        if dry_run:
            self.stdout.write(f"DRY RUN: Would have created {total} touchpoints")
        else:
            self.stdout.write(f"Successfully created {created} touchpoints for {processed} interactions")
    
    def batch_queryset(self, queryset, batch_size):
        """Yield batches of queryset."""
        for i in range(0, queryset.count(), batch_size):
            yield queryset[i:i + batch_size]
```

### **4.2 Migration Strategy**

**File: `connectors/migrations/0002_add_touchpoint_mapping_rules.py`**
```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('connectors', '0001_initial'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='TouchpointMappingRule',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('connector_type', models.CharField(max_length=50)),
                ('source_identifier', models.CharField(blank=True, max_length=200)),
                ('event_code', models.CharField(max_length=100)),
                ('touchpoint_code', models.CharField(max_length=100)),
                ('touchpoint_label', models.CharField(blank=True, max_length=200)),
                ('channel_code', models.CharField(blank=True, max_length=50)),
                ('medium_code', models.CharField(blank=True, max_length=50)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('priority', models.PositiveIntegerField(default=100)),
            ],
            options={
                'ordering': ['-priority', 'connector_type', 'event_code'],
            },
        ),
        migrations.AddIndex(
            model_name='touchpointmappingrule',
            index=models.Index(fields=['connector_type', 'event_code'], name='connectors_t_connect_8a1b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='touchpointmappingrule',
            index=models.Index(fields=['source_identifier', 'event_code'], name='connectors_t_source_9d3e4f_idx'),
        ),
        migrations.AddIndex(
            model_name='touchpointmappingrule',
            index=models.Index(fields=['priority'], name='connectors_t_priorit_5g6h7i_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='touchpointmappingrule',
            unique_together={('connector_type', 'source_identifier', 'event_code')},
        ),
    ]
```

---

## 🚀 Phase 5: Future Connectors

### **5.1 Email Connector Example**

**File: `emails/adapters.py`**
```python
from connectors.protocols import TouchpointHint
from .models import EmailInteraction

def infer_email_touchpoint_hint(email_interaction: EmailInteraction) -> TouchpointHint:
    """Infer touchpoint hint from email interaction."""
    
    event_code_map = {
        'open': 'email.open',
        'click': 'email.click',
        'bounce': 'email.bounce',
        'unsubscribe': 'email.unsubscribe',
        'spam': 'email.spam',
    }
    
    code = event_code_map.get(email_interaction.event_type, 'email.generic')
    
    # Email-specific medium analysis
    medium = 'email'
    if email_interaction.campaign_type:
        if email_interaction.campaign_type == 'newsletter':
            medium = 'newsletter'
        elif email_interaction.campaign_type == 'promotional':
            medium = 'promotional'
    
    return TouchpointHint(
        code=code,
        channel_code='email',
        medium_code=medium,
        label=f"Email {email_interaction.event_type.title()}",
        metadata={
            'event_type': email_interaction.event_type,
            'campaign_id': getattr(email_interaction, 'campaign_id', ''),
            'recipient': getattr(email_interaction, 'recipient', ''),
        }
    )
```

### **5.2 WhatsApp Connector Example**

**File: `whatsapp/adapters.py`**
```python
from connectors.protocols import TouchpointHint
from .models import WhatsAppInteraction

def infer_whatsapp_touchpoint_hint(whatsapp_interaction: WhatsAppInteraction) -> TouchpointHint:
    """Infer touchpoint hint from WhatsApp interaction."""
    
    event_code_map = {
        'message_received': 'whatsapp.message_received',
        'message_sent': 'whatsapp.message_sent',
        'media_received': 'whatsapp.media_received',
        'media_sent': 'whatsapp.media_sent',
    }
    
    code = event_code_map.get(whatsapp_interaction.event_type, 'whatsapp.generic')
    
    return TouchpointHint(
        code=code,
        channel_code='whatsapp',
        medium_code='whatsapp',
        label=f"WhatsApp {whatsapp_interaction.event_type.replace('_', ' ').title()}",
        metadata={
            'event_type': whatsapp_interaction.event_type,
            'phone_number': getattr(whatsapp_interaction, 'phone_number', ''),
            'message_type': getattr(whatsapp_interaction, 'message_type', ''),
        }
    )
```

---

## 📊 Testing Strategy

### **Unit Tests**

**File: `connectors/tests/test_resolvers.py`**
```python
from django.test import TestCase
from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol
from interactions.models import Touchpoint

class MockConnector(TouchpointInferenceProtocol):
    def infer_touchpoint_hint(self) -> TouchpointHint:
        return TouchpointHint(
            code='test.generic',
            channel_code='test',
            medium_code='test',
            label='Test Touchpoint'
        )

class TouchpointResolverTests(TestCase):
    def setUp(self):
        self.resolver = DefaultTouchpointResolver(None)
        self.mock_connector = MockConnector()
    
    def test_resolve_creates_touchpoint(self):
        touchpoint = self.resolver.resolve(self.mock_connector)
        
        self.assertIsInstance(touchpoint, Touchpoint)
        self.assertEqual(touchpoint.code, 'test.generic')
        self.assertEqual(touchpoint.name, 'Test Touchpoint')
    
    def test_resolve_reuses_existing_touchpoint(self):
        # Create touchpoint first
        touchpoint1 = self.resolver.resolve(self.mock_connector)
        
        # Resolve again
        touchpoint2 = self.resolver.resolve(self.mock_connector)
        
        self.assertEqual(touchpoint1.id, touchpoint2.id)
```

### **Integration Tests**

**File: `websites/tests/test_touchpoint_resolution.py`**
```python
from django.test import TestCase
from websites.models import WebInteraction, Website
from interactions.models import Interaction, Action
from our_institution.models import Division, OurOrganization

class WebTouchpointResolutionTests(TestCase):
    def setUp(self):
        # Create test data
        self.org = OurOrganization.objects.create(name="Test Org")
        self.division = Division.objects.create(
            organization=self.org,
            name="Test Division",
            code="TEST"
        )
        self.website = Website.objects.create(
            name="Test Website",
            base_url="https://test.com",
            division=self.division
        )
        self.action = Action.objects.create(
            name="Page View",
            code="page_view"
        )
    
    def test_web_interaction_creates_touchpoint(self):
        # Create interaction
        interaction = Interaction.objects.create(
            action=self.action,
            occurred_at=timezone.now()
        )
        
        # Create web interaction
        web_interaction = WebInteraction.objects.create(
            interaction=interaction,
            website=self.website,
            session_id="test_session",
            utm_medium="organic"
        )
        
        # Verify touchpoint was created
        interaction.refresh_from_db()
        self.assertIsNotNone(interaction.touchpoint)
        self.assertEqual(interaction.touchpoint.code, 'web.page_read')
        self.assertEqual(interaction.touchpoint.touchpoint_class.code, 'web')
```

---

## 📈 Performance Considerations

### **Caching Strategy**

**File: `connectors/cache.py`**
```python
from django.core.cache import cache
from typing import Optional
from .models import TouchpointMappingRule

class TouchpointCache:
    """Cache for touchpoint resolution to improve performance."""
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_mapping_rule(cls, connector_type: str, source_identifier: str, event_code: str) -> Optional[TouchpointMappingRule]:
        """Get mapping rule from cache."""
        cache_key = f"touchpoint_mapping:{connector_type}:{source_identifier}:{event_code}"
        return cache.get(cache_key)
    
    @classmethod
    def set_mapping_rule(cls, connector_type: str, source_identifier: str, event_code: str, rule: TouchpointMappingRule):
        """Cache mapping rule."""
        cache_key = f"touchpoint_mapping:{connector_type}:{source_identifier}:{event_code}"
        cache.set(cache_key, rule, cls.CACHE_TIMEOUT)
    
    @classmethod
    def invalidate_mapping_rules(cls):
        """Invalidate all mapping rule caches."""
        cache.delete_many(cache.keys("touchpoint_mapping:*"))
```

### **Database Optimizations**

1. **Indexes**: Already defined in the mapping rule model
2. **Select Related**: Use `select_related` for touchpoint queries
3. **Batch Processing**: Process interactions in batches for backfill
4. **Connection Pooling**: Ensure proper database connection management

---

## 🔒 Security Considerations

1. **Input Validation**: Validate all mapping rule inputs
2. **Permission Checks**: Ensure only authorized users can modify mapping rules
3. **SQL Injection**: Use Django ORM to prevent SQL injection
4. **Rate Limiting**: Implement rate limiting for touchpoint resolution

---

## 📋 Rollback Plan

1. **Feature Flags**: Use feature flags to enable/disable touchpoint resolution
2. **Database Backup**: Full backup before migration
3. **Gradual Rollout**: Enable for specific connectors first
4. **Monitoring**: Monitor performance and error rates
5. **Quick Disable**: Ability to quickly disable the system if issues arise

---

## 📊 Success Metrics

1. **Touchpoint Coverage**: % of interactions with touchpoints
2. **Resolution Performance**: Average time to resolve touchpoint
3. **Mapping Rule Usage**: % of interactions using custom mapping rules
4. **Error Rate**: % of failed touchpoint resolutions
5. **Admin Adoption**: % of admins using mapping rules

---

## 🎯 Conclusion

This implementation plan provides a robust, scalable, and maintainable touchpoint resolution system that:

- ✅ **Maintains Clean Architecture**: Generic logic in connectors, specialized logic in connector apps
- ✅ **Enables Business Flexibility**: Configurable mapping rules without code changes
- ✅ **Supports Future Growth**: Easy to add new connector types
- ✅ **Ensures Data Quality**: Consistent touchpoint creation across all connectors
- ✅ **Optimizes Performance**: Caching and database optimizations
- ✅ **Provides Safety**: Comprehensive testing and rollback plans

The phased approach allows for gradual implementation with minimal risk, while the protocol-based design ensures extensibility for future connector types.
