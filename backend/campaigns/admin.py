from django.contrib import admin
from .models import Campaign, CampaignTouchpoint


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_date', 'end_date', 'budget', 'is_active', 'is_active_now', 'division', 'team']
    list_filter = ['is_active', 'start_date', 'end_date', 'division', 'team', 'related_industries']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_active_now']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Temporalidad y Presupuesto', {
            'fields': ('start_date', 'end_date', 'budget')
        }),
        ('Organización', {
            'fields': ('division', 'team', 'parent')
        }),
        ('Canales', {
            'fields': ('channels',)
        }),
        ('Segmentación Semántica', {
            'fields': ('related_industries', 'related_functions', 'target_segments', 'descriptors', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['channels', 'related_industries', 'related_functions', 'target_segments', 'descriptors', 'tags']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('division', 'team', 'parent')


@admin.register(CampaignTouchpoint)
class CampaignTouchpointAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'touchpoint', 'weight', 'priority', 'expected_conversions', 'budget_allocated', 'is_product_targeted']
    list_filter = ['campaign', 'weight', 'priority']
    search_fields = ['campaign__name', 'touchpoint__name']
    readonly_fields = ['is_product_targeted', 'is_cross_product']
    
    fieldsets = (
        ('Relación', {
            'fields': ('campaign', 'touchpoint')
        }),
        ('Configuración', {
            'fields': ('weight', 'priority', 'expected_conversions', 'budget_allocated')
        }),
        ('Propiedades', {
            'fields': ('is_product_targeted', 'is_cross_product'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign', 'touchpoint')
