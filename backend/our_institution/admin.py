from django.contrib import admin
from .models import OurOrganization, Division, Seat, Unit, Position, Team

@admin.register(OurOrganization)
class OurOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'org_type', 'industry', 'country', 'is_active')
    list_filter = ('is_active', 'org_type', 'industry', 'country')
    search_fields = ('name', 'legal_name', 'tax_id', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'legal_name', 'org_type', 'industry')
        }),
        ('Información Legal', {
            'fields': ('tax_id', 'country')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organization', 'units_count', 'teams_count', 'is_active')
    list_filter = ('is_active', 'organization', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'units_count', 'teams_count', 'positions_count')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'name', 'code', 'description')
        }),
        ('Estadísticas', {
            'fields': ('units_count', 'teams_count', 'positions_count'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'organization', 'is_active')
    list_filter = ('is_active', 'category', 'organization')
    search_fields = ('name', 'code')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'name', 'code', 'category')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'division', 'parent', 'positions_count', 'is_active')
    list_filter = ('is_active', 'division', 'parent')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'positions_count', 'full_path')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('division', 'parent')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('division', 'name', 'code', 'description')
        }),
        ('Jerarquía', {
            'fields': ('parent', 'full_path')
        }),
        ('Estadísticas', {
            'fields': ('positions_count',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'unit', 'division_name', 'is_active')
    list_filter = ('is_active', 'unit__division')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'division_name')
    
    def division_name(self, obj):
        return obj.unit.division.name if obj.unit.division else '-'
    division_name.short_description = 'División'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('unit__division')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('unit', 'name', 'code', 'description')
        }),
        ('Contexto', {
            'fields': ('division_name',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'division', 'is_active')
    list_filter = ('is_active', 'division')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('division')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('division', 'name', 'code', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
