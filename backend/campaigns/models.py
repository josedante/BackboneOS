from django.db import models
from backend.models import BaseUUIDModelWithActiveStatus



class Campaign(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    content_type = models.CharField(
        max_length=20,
        choices=[
            ("affinity", "Afinidad"),
            ("category", "Categoría"),
            ("product", "Producto"),
            ("offer", "Oferta"),
            ("brand", "Marca"),
        ],
        blank=True,
        null=True,
        verbose_name="Tipo de contenido comunicacional"
    )

    target_products = models.ManyToManyField('products.Product', blank=True)
    target_offers = models.ManyToManyField('offers.ProductOffering', blank=True)
    target_categories = models.ManyToManyField('products.ProductCategory', blank=True)
    
    # Etapa del embudo de ventas
    SEE = 'see'
    THINK = 'think'
    DO = 'do'
    CARE = 'care'
    ANY = 'any'
    FUNNEL_STAGES = [
        (SEE, 'Ver'),
        (THINK, 'Pensar'),
        (DO, 'Hacer'),
        (CARE, 'Cuidar'),
        (ANY, 'Cualquiera'),
    ]
    funnel_stage = models.CharField(
        max_length=50, blank=True, choices=FUNNEL_STAGES, default=ANY,
        help_text="Etapa del embudo de ventas para la cual está diseñada esta campaña"
    )

    division = models.ForeignKey(
        'our_institution.Division', null=True, blank=True, on_delete=models.SET_NULL
    )
    team = models.ForeignKey(
        'our_institution.Team', null=True, blank=True, on_delete=models.SET_NULL
    )

    channels = models.ManyToManyField('interactions.Channel', blank=True)

    related_industries = models.ManyToManyField('world.Industry', blank=True)
    related_functions = models.ManyToManyField('world.FunctionOrResponsibility', blank=True)
    target_segments = models.ManyToManyField('world.MarketSegment', blank=True)
    descriptors = models.ManyToManyField('world.WorldDescriptor', blank=True)
    tags = models.ManyToManyField('world.Tag', blank=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcampaigns'
    )

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['funnel_stage']),
            models.Index(fields=['content_type']),
            models.Index(fields=['division']),
            models.Index(fields=['team']),
            # Composite indexes for common query patterns
            models.Index(fields=['is_active', 'start_date']),
            models.Index(fields=['is_active', 'content_type']),
            models.Index(fields=['division', 'is_active']),
            models.Index(fields=['funnel_stage', 'is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_active_now(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= (self.end_date or today)
    
    def get_product_performance_analytics(self):
        """Analytics detallados de rendimiento por producto"""
        from django.db.models import Count, Sum, Avg, Q
        from interactions.models import Interaction
        
        # Analytics por producto directo - simplified for now
        product_analytics = []
        for product in self.target_products.all():
            # Count interactions through touchpoints
            interactions_count = Interaction.objects.filter(
                touchpoint__product=product,
                is_active=True
            ).count()
            
            # Count conversions
            conversions_count = Interaction.objects.filter(
                touchpoint__product=product,
                is_active=True,
                action__code__in=['purchase', 'signup', 'download']
            ).count()
            
            # Calculate revenue from offerings
            revenue_generated = sum(
                offering.price for offering in product.productofferings.filter(is_active=True)
            ) if hasattr(product, 'productofferings') else 0
            
            product_analytics.append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'interactions_count': interactions_count,
                'conversions_count': conversions_count,
                'revenue_generated': revenue_generated
            })
        
        # Analytics por categoría - simplified for now
        category_analytics = []
        for category in self.target_categories.all():
            products_count = category.product_set.filter(is_active=True).count()
            
            # Count interactions for all products in this category
            interactions_count = Interaction.objects.filter(
                touchpoint__product__category=category,
                is_active=True
            ).count()
            
            category_analytics.append({
                'id': category.id,
                'name': category.name,
                'code': category.code,
                'products_count': products_count,
                'interactions_count': interactions_count
            })
        
        # Analytics de ofertas - simplified for now
        offer_analytics = []
        for offer in self.target_offers.all():
            # Count interactions for the product associated with this offer
            interactions_count = Interaction.objects.filter(
                touchpoint__product=offer.product,
                is_active=True
            ).count() if offer.product else 0
            
            offer_analytics.append({
                'id': offer.id,
                'name': offer.name,
                'product__name': offer.product.name if offer.product else 'N/A',
                'price': float(offer.price),
                'interactions_count': interactions_count,
                'total_revenue': float(offer.price)
            })
        
        return {
            'by_product': list(product_analytics),
            'by_category': list(category_analytics),
            'by_offer': list(offer_analytics),
            'summary': {
                'total_products': self.target_products.count(),
                'total_categories': self.target_categories.count(),
                'total_offerings': self.target_offers.count(),
                'total_potential_revenue': sum(
                    offering.price for offering in self.target_offers.all()
                )
            }
        }
    
    def get_bundle_analytics(self):
        """Analytics específicos para productos bundle"""
        from django.db.models import Count, Q
        from interactions.models import Interaction
        
        # Find bundle products (products with included_products)
        bundle_products = []
        for product in self.target_products.filter(included_products__isnull=False).distinct():
            bundle_size = product.included_products.count()
            
            # Count interactions for all included products
            bundle_interactions = Interaction.objects.filter(
                touchpoint__product__in=product.included_products.all(),
                is_active=True
            ).count()
            
            bundle_products.append({
                'id': product.id,
                'name': product.name,
                'bundle_size': bundle_size,
                'bundle_interactions': bundle_interactions
            })
        
        return {
            'bundle_products': list(bundle_products),
            'total_bundles': len(bundle_products),
            'avg_bundle_size': sum(b['bundle_size'] for b in bundle_products) / len(bundle_products) if bundle_products else 0
        }
    
    def get_target_summary(self):
        """Resumen de productos, categorías y ofertas objetivo"""
        # Count categories with products manually
        categories_with_products = 0
        for category in self.target_categories.all():
            if category.product_set.exists():
                categories_with_products += 1
        
        return {
            'products': {
                'total': self.target_products.count(),
                'bundles': self.target_products.filter(included_products__isnull=False).count(),
                'individual': self.target_products.filter(included_products__isnull=True).count()
            },
            'categories': {
                'total': self.target_categories.count(),
                'with_products': categories_with_products
            },
            'offers': {
                'total': self.target_offers.count(),
                'active': self.target_offers.filter(is_active=True).count(),
                'total_revenue': sum(offering.price for offering in self.target_offers.all())
            }
        }


class CampaignTouchpoint(models.Model):
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    touchpoint = models.ForeignKey('interactions.Touchpoint', on_delete=models.CASCADE)

    weight = models.FloatField(default=1.0)
    priority = models.PositiveIntegerField(default=0)
    expected_conversions = models.PositiveIntegerField(null=True, blank=True)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('campaign', 'touchpoint')

    def __str__(self):
        return f"{self.campaign.name} -> {self.touchpoint.name}"

    @property
    def is_product_targeted(self):
        return (
            self.touchpoint.product 
            and hasattr(self.campaign, 'product') 
            and self.campaign.product == self.touchpoint.product
        )

    @property
    def is_cross_product(self):
        return (
            self.touchpoint.product 
            and hasattr(self.campaign, 'product') 
            and self.campaign.product != self.touchpoint.product
        )
