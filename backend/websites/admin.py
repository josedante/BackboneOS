from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Website, WebSession, WebInteraction, WebAgent


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'division', 'channel', 'active', 'created_at']
    list_filter = ['active', 'division', 'channel', 'created_at']
    search_fields = ['name', 'base_url']
    readonly_fields = ['created_at']
    list_editable = ['active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'base_url', 'division', 'channel')
        }),
        ('Status', {
            'fields': ('active', 'created_at')
        }),
    )


@admin.register(WebSession)
class WebSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id_short', 'website', 'visitor_cookie_short', 'started_at', 
        'duration_display', 'page_count', 'is_bounce', 'utm_source', 'utm_medium'
    ]
    list_filter = [
        'is_bounce', 'website', 'utm_source', 'utm_medium', 'utm_campaign', 
        'started_at', 'ended_at'
    ]
    search_fields = ['session_id', 'visitor_cookie', 'utm_source', 'utm_medium', 'utm_campaign']
    readonly_fields = [
        'session_id', 'visitor_cookie', 'started_at', 'ended_at', 
        'last_activity_at', 'page_count', 'is_bounce', 'conversion_events'
    ]
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Session Identity', {
            'fields': ('session_id', 'visitor_cookie', 'website', 'agent')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'last_activity_at')
        }),
        ('Attribution', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term')
        }),
        ('Context', {
            'fields': ('referrer_url', 'landing_page_url', 'user_agent', 'ip_address')
        }),
        ('Analytics', {
            'fields': ('page_count', 'is_bounce', 'conversion_events')
        }),
    )
    
    def session_id_short(self, obj):
        return f"{obj.session_id[:8]}..." if obj.session_id else "N/A"
    session_id_short.short_description = 'Session ID'
    
    def visitor_cookie_short(self, obj):
        return f"{obj.visitor_cookie[:8]}..." if obj.visitor_cookie else "N/A"
    visitor_cookie_short.short_description = 'Visitor Cookie'
    
    def duration_display(self, obj):
        if obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return f"{duration.total_seconds():.0f}s"
        return "Active"
    duration_display.short_description = 'Duration'


@admin.register(WebInteraction)
class WebInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'interaction_id', 'website', 'session_id_short', 'visitor_cookie_short', 
        'utm_source', 'utm_medium', 'is_bot', 'created_at'
    ]
    list_filter = [
        'is_bot', 'website', 'utm_source', 'utm_medium', 'utm_campaign', 
        'created_at'
    ]
    search_fields = [
        'session_id', 'visitor_cookie', 'utm_source', 'utm_medium', 
        'utm_campaign', 'element', 'user_agent'
    ]
    readonly_fields = ['interaction', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('website', 'session_id', 'visitor_cookie', 'user_agent', 'ip')
        }),
        ('Event Details', {
            'fields': ('element', 'payload', 'is_bot')
        }),
        ('Attribution', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term')
        }),
        ('Client Hints', {
            'fields': ('client_hints',)
        }),
        ('Timing', {
            'fields': ('interaction', 'created_at')
        }),
    )
    
    def interaction_id(self, obj):
        if obj.interaction:
            return str(obj.interaction.pk)[:8]
        return "N/A"
    interaction_id.short_description = 'Interaction ID'
    
    def session_id_short(self, obj):
        return f"{obj.session_id[:8]}..." if obj.session_id else "N/A"
    session_id_short.short_description = 'Session ID'
    
    def visitor_cookie_short(self, obj):
        return f"{obj.visitor_cookie[:8]}..." if obj.visitor_cookie else "N/A"
    visitor_cookie_short.short_description = 'Visitor Cookie'


@admin.register(WebAgent)
class WebAgentAdmin(admin.ModelAdmin):
    list_display = [
        'identifier', 'display_name', 'agent_type', 'browser_family', 
        'os_family', 'device_family', 'is_mobile', 'is_bot', 'created_at'
    ]
    list_filter = [
        'agent_type', 'created_at'
    ]
    search_fields = ['identifier', 'name', 'user_agent']
    readonly_fields = [
        'identifier', 'created_at', 'browser_family', 'browser_version',
        'os_family', 'os_version', 'device_family', 'device_brand', 
        'device_model', 'is_mobile', 'is_bot', 'is_webview', 
        'display_name', 'technical_summary'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('identifier', 'name', 'agent_type', 'created_at')
        }),
        ('Browser Information', {
            'fields': ('browser_family', 'browser_version')
        }),
        ('Operating System', {
            'fields': ('os_family', 'os_version')
        }),
        ('Device Information', {
            'fields': ('device_family', 'device_brand', 'device_model')
        }),
        ('Capabilities', {
            'fields': ('is_mobile', 'is_bot', 'is_webview')
        }),
        ('Display Information', {
            'fields': ('display_name', 'technical_summary')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(agent_type__in=['browser', 'bot', 'device'])
