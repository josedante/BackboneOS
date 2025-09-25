from django.contrib import admin
from .models import ProductOffering


@admin.register(ProductOffering)
class ProductOfferingAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'price_display', 'discount_percentage', 'currency_code',
        'is_currently_valid', 'is_active', 'valid_from', 'valid_until'
    ]
    
    list_filter = [
        'is_active', 'currency_code', 'auto_renew', 'valid_from', 'valid_until',
        'channels', 'target_segments'
    ]
    
    search_fields = [
        'name', 'code', 'description'
    ]
    
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_currently_valid', 'price_display', 'discount_percentage', 'is_discounted']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Producto y Pricing', {
            'fields': ('product', 'price', 'currency_code', 'price_display', 'discount_percentage', 'is_discounted')
        }),
        ('Vigencia', {
            'fields': ('valid_from', 'valid_until', 'is_currently_valid')
        }),
        ('Suscripción', {
            'fields': ('auto_renew', 'duration_days'),
            'classes': ('collapse',)
        }),
        ('Configuración Comercial', {
            'fields': ('landing_url', 'channels', 'seats'),
            'classes': ('collapse',)
        }),
        ('Segmentación Semántica', {
            'fields': ('target_segments', 'related_industries', 'related_functions', 'descriptors', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = [
        'channels', 'seats', 'target_segments', 'related_industries',
        'related_functions', 'descriptors', 'tags'
    ]
    
    actions = ['activate_offerings', 'deactivate_offerings', 'duplicate_offerings']
    
    def get_queryset(self, request):
        """Optimizar consultas del admin"""
        return super().get_queryset(request).prefetch_related(
            'product', 'channels', 'target_segments', 'related_industries'
        )
    
    def activate_offerings(self, request, queryset):
        """Acción para activar ofertas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ofertas activadas correctamente.')
    activate_offerings.short_description = 'Activar ofertas seleccionadas'
    
    def deactivate_offerings(self, request, queryset):
        """Acción para desactivar ofertas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ofertas desactivadas correctamente.')
    deactivate_offerings.short_description = 'Desactivar ofertas seleccionadas'
    
    def duplicate_offerings(self, request, queryset):
        """Acción para duplicar ofertas"""
        duplicated_count = 0
        for offering in queryset:
            # Crear copia
            new_offering = ProductOffering.objects.create(
                name=f"{offering.name} (Copia)",
                code=f"{offering.code}_copy_{offering.id}",
                description=offering.description,
                price=offering.price,
                currency_code=offering.currency_code,
                auto_renew=offering.auto_renew,
                duration_days=offering.duration_days,
                landing_url=offering.landing_url,
                metadata=offering.metadata,
                is_active=False
            )
            
            # Copiar relación FK de producto
            new_offering.product = offering.product
            new_offering.save()
            
            # Copiar relaciones M2M
            new_offering.channels.set(offering.channels.all())
            new_offering.seats.set(offering.seats.all())
            new_offering.target_segments.set(offering.target_segments.all())
            new_offering.related_industries.set(offering.related_industries.all())
            new_offering.related_functions.set(offering.related_functions.all())
            new_offering.descriptors.set(offering.descriptors.all())
            new_offering.tags.set(offering.tags.all())
            
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} ofertas duplicadas correctamente.')
    duplicate_offerings.short_description = 'Duplicar ofertas seleccionadas'
