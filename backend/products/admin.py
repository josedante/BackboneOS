from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Division, ProductCategory, Modality, Customization, Product


class HasCanonicalUrlFilter(admin.SimpleListFilter):
    title = 'URL Canónica'
    parameter_name = 'has_canonical_url'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Con URL'),
            ('no', 'Sin URL'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(canonical_url__isnull=True).exclude(canonical_url='')
        if self.value() == 'no':
            return queryset.filter(Q(canonical_url__isnull=True) | Q(canonical_url=''))
        return queryset


class IsBundleFilter(admin.SimpleListFilter):
    title = 'Tipo de Producto'
    parameter_name = 'is_bundle'

    def lookups(self, request, model_admin):
        return (
            ('bundle', 'Bundles (con productos incluidos)'),
            ('individual', 'Productos individuales'),
            ('included', 'Incluidos en otros productos'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'bundle':
            return queryset.filter(included_products__isnull=False).distinct()
        if self.value() == 'individual':
            return queryset.filter(included_products__isnull=True, included_in_products__isnull=True)
        if self.value() == 'included':
            return queryset.filter(included_in_products__isnull=False).distinct()
        return queryset


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'categories_count', 'products_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    prepopulated_fields = {'code': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            categories_count=Count('categories', filter=Q(categories__is_active=True)),
            products_count=Count('categories__product', filter=Q(categories__product__is_active=True))
        )
    
    def categories_count(self, obj):
        return obj.categories_count
    categories_count.short_description = 'Categorías'
    categories_count.admin_order_field = 'categories_count'
    
    def products_count(self, obj):
        return obj.products_count
    products_count.short_description = 'Productos'
    products_count.admin_order_field = 'products_count'


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'division', 'full_path', 'level', 'products_count', 'is_active')
    list_filter = ('is_active', 'division', 'parent')
    search_fields = ('name', 'code', 'description')
    ordering = ('division__name', 'name',)
    prepopulated_fields = {'code': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'division', 'parent')
        }),
        ('Estado', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product', filter=Q(product__is_active=True))
        )
    
    def products_count(self, obj):
        count = getattr(obj, 'products_count', 0)
        if count > 0:
            url = reverse('admin:products_product_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{}</a>',
                url, obj.id, count
            )
        return count
    products_count.short_description = 'Productos'
    products_count.admin_order_field = 'products_count'


class ModalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'products_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product', filter=Q(product__is_active=True))
        )
    
    def products_count(self, obj):
        count = getattr(obj, 'products_count', 0)
        return count
    products_count.short_description = 'Productos'
    products_count.admin_order_field = 'products_count'


class CustomizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'products_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product', filter=Q(product__is_active=True))
        )
    
    def products_count(self, obj):
        count = getattr(obj, 'products_count', 0)
        return count
    products_count.short_description = 'Productos'
    products_count.admin_order_field = 'products_count'


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'category', 'price_display', 'duration_display', 
        'target_audience_summary', 'modalities_summary', 'included_products_count',
        'is_bundle_display', 'is_customizable', 'has_canonical_url_display', 'is_active'
    )
    list_filter = (
        'is_active', 'category', 'modalities', 'currency_code',
        'target_segments', 'related_industries', 'customization', HasCanonicalUrlFilter, IsBundleFilter
    )
    search_fields = (
        'name', 'code', 'description', 'canonical_url',
        'category__name', 'tags__name',
        'target_segments__name', 'related_industries__name'
    )
    ordering = ('name',)
    prepopulated_fields = {'code': ('name',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'description', 'canonical_url', 'category')
        }),
        ('Productos Incluidos', {
            'fields': ('included_products',),
            'description': 'Otros productos que están incluidos conceptualmente dentro de este producto'
        }),
        ('Configuración del Producto', {
            'fields': ('modalities', 'customization', 'duration')
        }),
        ('Pricing', {
            'fields': ('base_price', 'currency_code'),
            'classes': ('collapse',)
        }),
        ('Segmentación de Mercado', {
            'fields': (
                'target_segments', 'related_industries', 
                'related_functions', 'related_skills'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos y Clasificación', {
            'fields': ('descriptors', 'tags'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = (
        'included_products', 'modalities', 'target_segments', 'related_industries',
        'related_functions', 'related_skills', 'descriptors', 'tags'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'customization'
        ).prefetch_related(
            'included_products', 'modalities', 'target_segments', 'related_industries',
            'related_functions', 'related_skills', 'tags'
        )
    
    def target_audience_summary(self, obj):
        segments = obj.target_segments.all()[:3]
        if segments:
            names = [s.name for s in segments]
            extra = obj.target_segments.count() - 3
            if extra > 0:
                names.append(f"(+{extra} más)")
            return ', '.join(names)
        return 'General'
    target_audience_summary.short_description = 'Público Objetivo'
    
    def modalities_summary(self, obj):
        modalities = obj.modalities.all()[:2]
        names = [m.name for m in modalities]
        extra = obj.modalities.count() - 2
        if extra > 0:
            names.append(f"(+{extra})")
        return ', '.join(names) if names else 'No especificada'
    modalities_summary.short_description = 'Modalidades'
    
    def included_products_count(self, obj):
        count = obj.included_products.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<span style="color: green;">✓ {} producto{}</span>',
                count, 's' if count > 1 else ''
            )
        return format_html('<span style="color: gray;">✗ Ninguno</span>')
    included_products_count.short_description = 'Productos Incluidos'
    
    def is_bundle_display(self, obj):
        if obj.is_bundle:
            bundle_price = obj.get_bundle_price_display()
            return format_html(
                '<span style="color: blue;">📦 Bundle<br/><small>{}</small></span>',
                bundle_price
            )
        return format_html('<span style="color: gray;">Producto Individual</span>')
    is_bundle_display.short_description = 'Tipo'
    
    def is_customizable(self, obj):
        if obj.customization:
            return format_html(
                '<span style="color: green;">✓ {}</span>', 
                obj.customization.name
            )
        return format_html('<span style="color: gray;">✗ Estándar</span>')
    is_customizable.short_description = 'Personalizable'
    is_customizable.admin_order_field = 'customization'

    def has_canonical_url_display(self, obj):
        if obj.canonical_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: green;">✓ Ver URL</a>', 
                obj.canonical_url
            )
        return format_html('<span style="color: gray;">✗ Sin URL</span>')
    has_canonical_url_display.short_description = 'URL Canónica'
    has_canonical_url_display.admin_order_field = 'canonical_url'
    
    # Acciones personalizadas
    actions = ['make_active', 'make_inactive', 'duplicate_product']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} productos activados.')
    make_active.short_description = "Activar productos seleccionados"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} productos desactivados.')
    make_inactive.short_description = "Desactivar productos seleccionados"
    
    def duplicate_product(self, request, queryset):
        for product in queryset:
            # Duplicar producto
            new_product = Product.objects.get(pk=product.pk)
            new_product.pk = None
            new_product.name = f"{product.name} (Copia)"
            new_product.code = f"{product.code}_COPY"
            new_product.save()
            
            # Copiar relaciones M2M
            new_product.included_products.set(product.included_products.all())
            new_product.modalities.set(product.modalities.all())
            new_product.target_segments.set(product.target_segments.all())
            new_product.related_industries.set(product.related_industries.all())
            new_product.related_functions.set(product.related_functions.all())
            new_product.related_skills.set(product.related_skills.all())
            new_product.descriptors.set(product.descriptors.all())
            new_product.tags.set(product.tags.all())
        
        count = queryset.count()
        self.message_user(request, f'{count} productos duplicados.')
    duplicate_product.short_description = "Duplicar productos seleccionados"


# Registro de modelos
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Modality, ModalityAdmin)
admin.site.register(Customization, CustomizationAdmin)
admin.site.register(Product, ProductAdmin)

# Configuración del admin site
admin.site.site_header = 'BackboneOS - Gestión de Productos'
admin.site.site_title = 'BackboneOS Products'
admin.site.index_title = 'Panel de Administración de Productos'
