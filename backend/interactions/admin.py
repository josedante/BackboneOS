from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from .models import (
    Agent, Medium, Channel, ActionType, Action, 
    TouchpointType, Touchpoint, Interaction
)


@admin.register(Medium)
class MediumAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'communication_type', 'is_active', 'touchpoints_count']
    list_filter = ['is_active', 'communication_type']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def touchpoints_count(self, obj):
        return obj.touchpoints.count()
    touchpoints_count.short_description = 'Touchpoints'


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'source_type', 'is_active', 'interactions_count', 'touchpoints_count']
    list_filter = ['is_active', 'source_type']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def interactions_count(self, obj):
        # Count interactions through touchpoints
        from django.db.models import Count, Q
        return obj.touchpoints.filter(is_active=True).aggregate(
            total=Count('interaction', filter=Q(interaction__is_active=True))
        )['total'] or 0
    interactions_count.short_description = 'Interacciones'
    
    def touchpoints_count(self, obj):
        return obj.touchpoints.filter(is_active=True).count()
    touchpoints_count.short_description = 'Touchpoints'


@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'actions_count']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def actions_count(self, obj):
        return obj.actions.count()
    actions_count.short_description = 'Acciones'


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'action_type', 'is_active', 'interactions_count']
    list_filter = ['is_active', 'action_type']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def interactions_count(self, obj):
        return obj.interaction_set.count()
    interactions_count.short_description = 'Interacciones'


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'agent_type', 'represents_display', 'operated_by', 
        'is_active', 'interactions_count'
    ]
    list_filter = ['agent_type', 'is_active']
    search_fields = ['name', 'identifier']
    ordering = ['agent_type', 'name']
    autocomplete_fields = ['operated_by', 'represents_person', 'represents_organization']
    
    def represents_display(self, obj):
        if obj.represents_person:
            return format_html(
                '<span style="color: blue;">👤 {}</span>', 
                obj.represents_person.full_name
            )
        elif obj.represents_organization:
            return format_html(
                '<span style="color: green;">🏢 {}</span>', 
                obj.represents_organization.name
            )
        return '-'
    represents_display.short_description = 'Representa'
    
    def interactions_count(self, obj):
        return obj.interactions.count()
    interactions_count.short_description = 'Interacciones'


@admin.register(TouchpointType)
class TouchpointTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'touchpoints_count']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def touchpoints_count(self, obj):
        return obj.touchpoints.count()
    touchpoints_count.short_description = 'Touchpoints'


@admin.register(Touchpoint)
class TouchpointAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'touchpoint_type', 'channel', 'medium', 'content_type', 'product', 
        'assigned_staff', 'is_active', 'interactions_count'
    ]
    list_filter = [
        'is_active', 'content_type', 'touchpoint_type', 'channel', 'medium',
        'related_industries', 'related_functions'
    ]
    search_fields = ['name', 'code', 'description', 'url']
    autocomplete_fields = [
        'touchpoint_type', 'channel', 'medium', 'assigned_staff', 'product',
        'related_industries', 'related_functions', 'related_skills', 'related_descriptors'
    ]
    filter_horizontal = ['related_industries', 'related_functions', 'related_skills', 'related_descriptors']
    ordering = ['name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'touchpoint_type', 'channel', 'medium', 'description', 'is_active')
        }),
        ('Configuración de Negocio', {
            'fields': ('content_type', 'product', 'assigned_staff')
        }),
        ('Detalles Técnicos', {
            'fields': ('url', 'external_id'),
            'classes': ('collapse',)
        }),
        ('Segmentación Semántica', {
            'fields': ('related_industries', 'related_functions', 'related_skills', 'related_descriptors'),
            'classes': ('collapse',)
        }),
    )
    
    def interactions_count(self, obj):
        count = obj.interaction_set.count()
        if count > 0:
            url = reverse('admin:interactions_interaction_changelist') + f'?touchpoint__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    interactions_count.short_description = 'Interacciones'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = [
        'occurred_at', 'entity_display', 'touchpoint', 'action', 
        'channel_display', 'agent_display', 'duration_display', 'is_active'
    ]
    list_filter = [
        'is_active', 'occurred_at', 'touchpoint__channel', 'action', 'agent__agent_type'
    ]
    search_fields = [
        'person__full_name', 'organization__name', 'touchpoint__name',
        'action__name', 'source', 'user_agent', 'ip_address', 'session_id'
    ]
    autocomplete_fields = [
        'person', 'organization', 'touchpoint', 'action', 
        'agent', 'representative', 'product'
    ]
    ordering = ['-occurred_at']
    date_hierarchy = 'occurred_at'
    
    fieldsets = (
        ('Entidades Involucradas', {
            'fields': ('person', 'organization', 'agent', 'representative')
        }),
        ('Detalles de la Interacción', {
            'fields': ('touchpoint', 'action', 'product')
        }),
        ('Contexto Temporal', {
            'fields': ('occurred_at', 'duration_seconds', 'session_id')
        }),
        ('Contexto Técnico', {
            'fields': ('source', 'user_agent', 'ip_address', 'referrer_url'),
            'classes': ('collapse',)
        }),
        ('Geolocalización', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Datos Adicionales', {
            'fields': ('payload', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def entity_display(self, obj):
        entity = obj.resolved_person or obj.resolved_organization
        if not entity:
            return mark_safe('<em>Anónimo</em>')
        
        if obj.resolved_person:
            return format_html(
                '<span style="color: blue;">👤 {}</span>', 
                entity.full_name
            )
        else:
            return format_html(
                '<span style="color: green;">🏢 {}</span>', 
                entity.name
            )
    entity_display.short_description = 'Entidad'
    
    def agent_display(self, obj):
        if not obj.agent:
            return '-'
        
        agent_icons = {
            'browser': '🌐',
            'human': '👤', 
            'system': '💻',
            'device': '📱',
            'bot': '🤖',
            'ai': '🧠',
            'other': '❓'
        }
        
        icon = agent_icons.get(obj.agent.agent_type, '❓')
        return format_html(
            '{} {}', 
            icon, 
            obj.agent.name[:30] + '...' if len(obj.agent.name) > 30 else obj.agent.name
        )
    agent_display.short_description = 'Agente'
    
    def channel_display(self, obj):
        if obj.touchpoint and obj.touchpoint.channel:
            return obj.touchpoint.channel.name
        return '-'
    channel_display.short_description = 'Canal'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'person', 'organization', 'touchpoint', 'action', 
            'agent', 'representative', 'product', 'touchpoint__channel'
        ).prefetch_related(
            'agent__represents_person', 'agent__represents_organization'
        )
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} interacciones marcadas como activas.')
    mark_as_active.short_description = 'Marcar como activas'
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} interacciones marcadas como inactivas.')
    mark_as_inactive.short_description = 'Marcar como inactivas'
