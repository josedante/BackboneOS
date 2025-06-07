from django.contrib import admin
from .models import OurOrganization, Seat, Unit, Position, Team

@admin.register(OurOrganization)
class OurOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'org_type', 'industry', 'country', 'is_active')
    search_fields = ('name', 'legal_name', 'tax_id')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'organization', 'is_active')
    list_filter = ('category', 'organization')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    search_fields = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'is_active')
    search_fields = ('title',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')
