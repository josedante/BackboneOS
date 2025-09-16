from django.contrib import admin

from world.models import (
    Country, Industry, FunctionOrResponsibility, Skill,
    PersonalIDType, OrganizationType, OrganizationalIDType,
    DescriptorFamily, WorldDescriptor, MarketSegment, Tag,
    AcademicDegree, Position, Gender, MaritalStatus
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso3_code', 'timezone')
    search_fields = ('name', 'iso3_code')
    ordering = ('name',)
    list_filter = ('timezone',)
    
    # fieldsets = (
    #     (None, {
    #         'fields': ('name', 'iso3_code', 'timezone')
    #     }),
    # )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(PersonalIDType)
class PersonalIDTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('name', 'code')
    ordering = ('name',)
    list_filter = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'country')
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(AcademicDegree)
class AcademicDegreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('code',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'ciiu_code', 'display_order', 'is_active')
    search_fields = ('name', 'code', 'description', 'ciiu_code')
    list_filter = ('is_active', 'parent')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'parent', 'ciiu_code', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(FunctionOrResponsibility)
class FunctionOrResponsibilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'typical_level', 'display_order', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'typical_level', 'parent')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'parent', 'typical_level', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'skill_type', 'typical_level_required', 'display_order', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'skill_type', 'typical_level_required')
    ordering = ('skill_type', 'display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'skill_type', 'typical_level_required', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'ownership_type', 'typical_size', 'display_order', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'ownership_type', 'typical_size')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'ownership_type', 'typical_size', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(OrganizationalIDType)
class OrganizationalIDTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country', 'display_order', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'country')
    ordering = ('country__name', 'display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'country', 'regex_pattern', 'max_length', 'min_length', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(DescriptorFamily)
class DescriptorFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(WorldDescriptor)
class WorldDescriptorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'family', 'parent', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'family', 'parent')
    ordering = ('family__name', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'family', 'parent')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(MarketSegment)
class MarketSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'segment_type', 'display_order', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'segment_type')
    ordering = ('display_order', 'name')
    filter_horizontal = ('industries', 'functions', 'skills', 'descriptors')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'segment_type', 'display_order')
        }),
        ('Relaciones', {
            'fields': ('industries', 'functions', 'skills', 'descriptors'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'display_order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )