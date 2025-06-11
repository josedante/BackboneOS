from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

from backend.models import BaseUUIDModelWithActiveStatus
from world.models import (
    Industry,
    FunctionOrResponsibility,
    Skill,
    WorldDescriptor,
    MarketSegment,
    Tag,
    Country,
)


class Division(BaseUUIDModelWithActiveStatus):
    """División empresarial que agrupa categorías de productos"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "División"
        verbose_name_plural = "Divisiones"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]
        constraints = []

    def __str__(self):
        return self.name

    @property
    def categories_count(self):
        """Cantidad de categorías en la división"""
        return self.categories.filter(is_active=True).count()

    @property
    def products_count(self):
        """Cantidad total de productos en la división"""
        from django.db.models import Count
        return Product.objects.filter(
            category__division=self,
            is_active=True
        ).count()

    def get_revenue_summary(self):
        """Resumen de ingresos potenciales de la división"""
        from django.db.models import Sum, Avg, Count
        
        products = Product.objects.filter(
            category__division=self,
            is_active=True,
            base_price__isnull=False
        )
        
        return {
            'total_products_with_price': products.count(),
            'avg_price': products.aggregate(avg=Avg('base_price'))['avg'],
            'total_potential_value': products.aggregate(total=Sum('base_price'))['total']
        }


class ProductCategory(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    # Relación con División
    division = models.ForeignKey(
        Division,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='categories',
        verbose_name='División'
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )

    class Meta:
        ordering = ['division__name', 'name']
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
            models.Index(fields=['division', 'is_active']),
        ]

    def __str__(self):
        if self.division:
            return f"{self.division.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """Ruta completa: División > Categoría Padre > Hijo > Nieto"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        
        if self.division:
            path.insert(0, self.division.name)
        
        return ' > '.join(path)

    @property
    def level(self):
        """Nivel de profundidad en la jerarquía (sin contar división)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    @property
    def absolute_level(self):
        """Nivel absoluto incluyendo división (División=0, Categoría raíz=1, etc.)"""
        return self.level + 1  # +1 porque la división es nivel 0

    def get_descendants(self):
        """Obtiene todas las subcategorías activas recursivamente"""
        descendants = []
        to_process = list(self.subcategories.filter(is_active=True))
        
        while to_process:
            current = to_process.pop(0)
            descendants.append(current)
            to_process.extend(current.subcategories.filter(is_active=True))
        
        return descendants


class Modality(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Modalidad"
        verbose_name_plural = "Modalidades"

    def __str__(self):
        return self.name


class Customization(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Personalización"
        verbose_name_plural = "Personalizaciones"

    def __str__(self):
        return self.name


class Product(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    canonical_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL del producto",
        help_text="Página principal donde se presenta este producto"
    )
    included_products = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='included_in_products',
        help_text="Otros productos incluidos conceptualmente dentro de este"
    )


    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL)
    modalities = models.ManyToManyField(Modality, blank=True)
    customization = models.ForeignKey(Customization, null=True, blank=True, on_delete=models.SET_NULL)

    duration = models.DurationField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Precio base')
    currency_code = models.CharField(max_length=3, default='PEN', verbose_name='Moneda')

    target_segments = models.ManyToManyField(MarketSegment, blank=True)
    related_industries = models.ManyToManyField(Industry, blank=True)
    related_functions = models.ManyToManyField(FunctionOrResponsibility, blank=True)
    related_skills = models.ManyToManyField(Skill, blank=True)
    descriptors = models.ManyToManyField(WorldDescriptor, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['base_price']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(base_price__gte=0) | models.Q(base_price__isnull=True),
                name='positive_base_price'
            ),
            models.CheckConstraint(
                check=models.Q(currency_code__in=['PEN', 'USD', 'EUR']),
                name='valid_currency_code'
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validaciones de negocio"""
        super().clean()
        
        # Validar precio positivo
        if self.base_price is not None and self.base_price <= Decimal('0'):
            raise ValidationError({'base_price': 'El precio debe ser mayor a 0'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_customizable(self):
        """Verifica si el producto permite personalización"""
        return self.customization is not None

    @property
    def has_canonical_url(self):
        """Verifica si el producto tiene URL canónica"""
        return bool(self.canonical_url)

    @property
    def price_display(self):
        """Precio formateado con moneda"""
        if self.base_price:
            return f"{self.currency_code} {self.base_price:,.2f}"
        return "Precio por consultar"

    @property
    def duration_display(self):
        """Duración en formato legible"""
        if not self.duration:
            return None
        
        total_seconds = int(self.duration.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        
        if days > 0:
            return f"{days} día{'s' if days > 1 else ''}"
        elif hours > 0:
            return f"{hours} hora{'s' if hours > 1 else ''}"
        else:
            return "Menos de 1 hora"

    def get_target_audience(self):
        """Descripción del público objetivo"""
        segments = list(self.target_segments.values_list('name', flat=True))
        return ', '.join(segments) if segments else 'General'

    def get_modalities_display(self):
        """Modalidades disponibles como string"""
        modalities = list(self.modalities.values_list('name', flat=True))
        return ', '.join(modalities) if modalities else 'No especificada'

    def get_related_skills_summary(self):
        """Resumen de habilidades relacionadas por tipo"""
        skills = self.related_skills.values('skill_type', 'name')
        skill_types = {}
        
        for skill in skills:
            skill_type = skill['skill_type']
            if skill_type not in skill_types:
                skill_types[skill_type] = []
            skill_types[skill_type].append(skill['name'])
        
        return skill_types

    # Métodos para manejar productos incluidos
    def get_included_products_list(self):
        """Obtiene la lista de productos incluidos activos"""
        return self.included_products.filter(is_active=True)

    def get_included_products_display(self):
        """Productos incluidos como string para mostrar"""
        included = list(self.included_products.filter(is_active=True).values_list('name', flat=True))
        return ', '.join(included) if included else 'Ninguno'

    def get_parent_products(self):
        """Obtiene los productos que incluyen a este producto"""
        return self.included_in_products.filter(is_active=True)

    def add_included_product(self, product):
        """Agrega un producto a la lista de incluidos con validación"""
        if product == self:
            raise ValidationError("Un producto no puede incluirse a sí mismo")
        
        if product in self.get_included_products_list():
            return False  # Ya está incluido
        
        self.included_products.add(product)
        return True

    def remove_included_product(self, product):
        """Remueve un producto de la lista de incluidos"""
        self.included_products.remove(product)

    def get_total_included_price(self):
        """Calcula el precio total de todos los productos incluidos"""
        included_products = self.get_included_products_list().filter(base_price__isnull=False)
        total = sum(product.base_price for product in included_products)
        return total if total > 0 else None

    def get_bundle_price_display(self):
        """Muestra el precio del bundle (producto principal + incluidos)"""
        main_price = self.base_price or 0
        included_price = self.get_total_included_price() or 0
        total = main_price + included_price
        
        if total > 0:
            return f"{self.currency_code} {total:,.2f} (incluye {len(self.get_included_products_list())} productos)"
        return self.price_display

    @property
    def is_bundle(self):
        """Verifica si este producto es un bundle (tiene productos incluidos)"""
        return self.included_products.filter(is_active=True).exists()

    @property
    def is_included_in_bundles(self):
        """Verifica si este producto está incluido en otros productos"""
        return self.included_in_products.filter(is_active=True).exists()
