from django.contrib import admin

from world.models import Country, PersonalIDType, AcademicDegree, Position

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