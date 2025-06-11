from django.db import models
from backend.models import BaseUUIDModelWithActiveStatus


class ProductOffering(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='offerings',
        help_text="Producto ofrecido en esta oferta comercial"
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='USD')

    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    duration_days = models.PositiveIntegerField(null=True, blank=True, help_text="Duración de la suscripción en días (si aplica)")

    landing_url = models.URLField(blank=True, null=True)

    # Contexto y segmentación
    channels = models.ManyToManyField('interactions.Channel', blank=True, help_text="Canales permitidos para esta oferta")
    seats = models.ManyToManyField('our_institution.Seat', blank=True)
    target_segments = models.ManyToManyField('world.MarketSegment', blank=True)
    related_industries = models.ManyToManyField('world.Industry', blank=True)
    related_functions = models.ManyToManyField('world.FunctionOrResponsibility', blank=True)
    descriptors = models.ManyToManyField('world.WorldDescriptor', blank=True)
    tags = models.ManyToManyField('world.Tag', blank=True)

    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-valid_from', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['currency_code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.product.name})"

    @property
    def is_currently_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (not self.valid_from or self.valid_from <= today) and (not self.valid_until or self.valid_until >= today)

    @property
    def price_display(self):
        return f"{self.currency_code} {self.price:,.2f}"
