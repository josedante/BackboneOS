from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Person, ContactDetail, IndividualProfile, Organization, PhysicalAddress


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 'get_primary_contact', 'gender', 'birthday', 
        'country_of_nationality', 'id_type', 'id_number', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'gender', 'marital_status', 'country_of_nationality', 
        'id_type', 'created_at'
    ]
    search_fields = [
        'first_name', 'middle_name', 'fathers_name', 'mothers_name', 
        'id_number', 'contacts__email', 'contacts__phone'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'middle_name', 'fathers_name', 'mothers_name', 'portrait')
        }),
        ('Detalles Demográficos', {
            'fields': ('gender', 'birthday', 'marital_status', 'country_of_nationality')
        }),
        ('Identificación', {
            'fields': ('id_type', 'id_number')
        }),
        ('Metadatos', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.fathers_name}".strip() or "Sin nombre"
    get_full_name.short_description = 'Nombre Completo'
    
    def get_primary_contact(self, obj):
        primary = obj.contacts.filter(is_primary=True).first()
        if primary:
            if primary.email:
                return format_html('<span title="Email primario">{}</span>', primary.email)
            elif primary.phone:
                return format_html('<span title="Teléfono primario">{}</span>', primary.phone)
        return format_html('<span style="color: orange;">Sin contacto</span>')
    get_primary_contact.short_description = 'Contacto Principal'


@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    list_display = ['person', 'get_contact_info', 'is_primary', 'verified', 'is_active']
    list_filter = ['is_primary', 'verified', 'is_active', 'created_at']
    search_fields = ['email', 'phone', 'person__first_name', 'person__fathers_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_contact_info(self, obj):
        if obj.email:
            return format_html('<strong>📧</strong> {}', obj.email)
        elif obj.phone:
            return format_html('<strong>📱</strong> {}', obj.phone)
        return "Sin información"
    get_contact_info.short_description = 'Información de Contacto'


@admin.register(IndividualProfile)
class IndividualProfileAdmin(admin.ModelAdmin):
    list_display = [
        'person', 'get_academic_degree', 'get_industries_count', 
        'get_skills_count', 'preferred_contact_medium', 'allows_marketing'
    ]
    list_filter = [
        'academic_degree', 'preferred_contact_medium', 'accepts_privacy_policy', 
        'allows_marketing', 'is_active'
    ]
    search_fields = [
        'person__first_name', 'person__fathers_name',
        'industries__name', 'skills__name', 'functions__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    filter_horizontal = ['functions', 'industries', 'skills']
    
    fieldsets = (
        ('Persona', {
            'fields': ('person',)
        }),
        ('Perfil Semántico', {
            'fields': ('academic_degree', 'functions', 'industries', 'skills')
        }),
        ('Preferencias', {
            'fields': ('preferred_contact_medium', 'accepts_privacy_policy', 'allows_marketing')
        }),
        ('Metadatos', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_academic_degree(self, obj):
        return obj.academic_degree.name if obj.academic_degree else "No especificado"
    get_academic_degree.short_description = 'Nivel Académico'
    
    def get_industries_count(self, obj):
        count = obj.industries.count()
        return format_html('<span style="color: blue;">{} industrias</span>', count)
    get_industries_count.short_description = 'Industrias'
    
    def get_skills_count(self, obj):
        count = obj.skills.count()
        return format_html('<span style="color: green;">{} habilidades</span>', count)
    get_skills_count.short_description = 'Habilidades'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'legal_name', 'org_type', 'industry', 'country', 
        'id_type', 'id_number', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'org_type', 'industry', 'country', 'id_type', 'created_at'
    ]
    search_fields = [
        'name', 'legal_name', 'id_number', 'main_address'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'legal_name', 'org_type', 'industry')
        }),
        ('Identificación Legal', {
            'fields': ('id_type', 'id_number')
        }),
        ('Ubicación', {
            'fields': ('main_address', 'country')
        }),
        ('Metadatos', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PhysicalAddress)
class PhysicalAddressAdmin(admin.ModelAdmin):
    list_display = [
        'get_owner', 'address', 'city', 'country', 
        'is_primary', 'use_for_billing', 'is_active'
    ]
    list_filter = [
        'is_primary', 'use_for_billing', 'is_active', 'country', 'created_at'
    ]
    search_fields = [
        'address', 'address_extra', 'city', 'region_or_state',
        'owner_person__first_name', 'owner_person__fathers_name',
        'owner_org__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Propietario', {
            'fields': ('owner_person', 'owner_org')
        }),
        ('Dirección', {
            'fields': ('address', 'address_extra', 'city', 'region_or_state', 'country', 'zip_code')
        }),
        ('Configuración', {
            'fields': ('is_primary', 'use_for_billing')
        }),
        ('Metadatos', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_owner(self, obj):
        if obj.owner_person:
            return format_html('<strong>👤</strong> {}', obj.owner_person)
        elif obj.owner_org:
            return format_html('<strong>🏢</strong> {}', obj.owner_org)
        return "Sin propietario"
    get_owner.short_description = 'Propietario'


# Configuración del admin site
admin.site.site_header = 'BackboneOS - Gestión de Entidades'
admin.site.site_title = 'BackboneOS Entities'
admin.site.index_title = 'Panel de Administración de Entidades'
