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
        
        # Analytics por producto directo
        product_analytics = self.target_products.annotate(
            interactions_count=Count(
                'touchpoints__interactions',
                filter=Q(touchpoints__interactions__is_active=True)
            ),
            conversions_count=Count(
                'touchpoints__interactions__action__code',
                filter=Q(
                    touchpoints__interactions__is_active=True,
                    touchpoints__interactions__action__code__in=['purchase', 'signup', 'download']
                )
            ),
            revenue_generated=Sum(
                'offerings__price',
                filter=Q(offerings__campaign_offerings__campaign=self)
            )
        ).values(
            'id', 'name', 'code', 'interactions_count', 
            'conversions_count', 'revenue_generated'
        )
        
        # Analytics por categoría
        category_analytics = self.target_categories.annotate(
            products_count=Count('product', filter=Q(product__is_active=True)),
            interactions_count=Count(
                'product__touchpoints__interactions',
                filter=Q(product__touchpoints__interactions__is_active=True)
            )
        ).values(
            'id', 'name', 'code', 'products_count', 'interactions_count'
        )
        
        # Analytics de ofertas
        offer_analytics = self.target_offers.annotate(
            interactions_count=Count(
                'product__touchpoints__interactions',
                filter=Q(product__touchpoints__interactions__is_active=True)
            ),
            total_revenue=Sum('price')
        ).values(
            'id', 'name', 'product__name', 'price', 
            'interactions_count', 'total_revenue'
        )
        
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
        
        bundle_products = self.target_products.filter(
            included_products__isnull=False
        ).annotate(
            bundle_size=Count('included_products'),
            bundle_interactions=Count(
                'included_products__touchpoints__interactions',
                filter=Q(included_products__touchpoints__interactions__is_active=True)
            )
        ).values(
            'id', 'name', 'bundle_size', 'bundle_interactions'
        )
        
        return {
            'bundle_products': list(bundle_products),
            'total_bundles': len(bundle_products),
            'avg_bundle_size': sum(b['bundle_size'] for b in bundle_products) / len(bundle_products) if bundle_products else 0
        }
    
    def get_target_summary(self):
        """Resumen de productos, categorías y ofertas objetivo"""
        return {
            'products': {
                'total': self.target_products.count(),
                'bundles': self.target_products.filter(included_products__isnull=False).count(),
                'individual': self.target_products.filter(included_products__isnull=True).count()
            },
            'categories': {
                'total': self.target_categories.count(),
                'with_products': self.target_categories.filter(product__isnull=False).count()
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
