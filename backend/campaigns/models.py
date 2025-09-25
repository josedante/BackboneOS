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
