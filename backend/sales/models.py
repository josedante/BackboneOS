from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid

from backend.models import BaseUUIDModelWithActiveStatus

from interactions.models import Interaction, Touchpoint, Channel, Agent, TouchpointInstance

User = get_user_model()

class ProductAcquisition(Interaction):
    """Registro de una adquisición efectiva de producto"""

    offering = models.ForeignKey(
        'offers.ProductOffering',
        on_delete=models.PROTECT,
        related_name='acquisitions'
    )

    price_paid = models.DecimalField(max_digits=12, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    discount_reason = models.CharField(max_length=200, blank=True)

    CASH = "cash"
    INSTALLMENTS = "installments"
    LETTER = "letter"
    PAYMENT_OPTIONS = [
        (CASH, "Contado"),
        (INSTALLMENTS, "Cuotas"),
        (LETTER, "Carta por cobrar"),
    ]
    payment_modality = models.CharField(
        max_length=20,
        choices=PAYMENT_OPTIONS,
        default=CASH,
    )

    notes = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Adquisición de Producto"
        verbose_name_plural = "Adquisiciones de Productos"
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['offering']),
            models.Index(fields=['price_paid']),
            models.Index(fields=['payment_modality']),
            models.Index(fields=['occurred_at']),
        ]

    def clean(self):
        super().clean()

        # 1. Producto desde la oferta
        if not self.product and self.offering:
            self.product = self.offering.product

        # 2. Touchpoint por defecto si no está definido
        if not self.touchpoint:
            self.touchpoint = Touchpoint.objects.filter(code="product_acquisition").first()
            if not self.touchpoint:
                self.touchpoint = Touchpoint.objects.create(
                    name="Adquisición de Producto",
                    code="product_acquisition",
                    funnel_stage="do",  # o "decision"
                    description="Registro de una compra o matrícula de producto"
                )

        # 3. Canal inferido desde la oferta
        if not self.channel and self.offering and self.offering.channels.exists():
            self.channel = self.offering.channels.first()

        # 4. Agente representando a la persona
        if not self.agent and self.person:
            self.agent = Agent.objects.filter(represents_person=self.person).first()

        # 5. Representante por default desde touchpoint
        if not self.representative and self.touchpoint and self.touchpoint.assigned_staff:
            self.representative = self.touchpoint.assigned_staff

        # 6. Etapa JTBD
        if not self.jtbd_stage or self.jtbd_stage == "any":
            self.jtbd_stage = "job_decision"

        # 7. Fecha de ocurrencia
        if not self.occurred_at:
            self.occurred_at = timezone.now()

    def __str__(self):
        person = self.resolved_person
        product = self.offering.product.name if self.offering else "-"
        date = self.occurred_at.strftime('%Y-%m-%d') if self.occurred_at else "?"
        return f"{person.full_name if person else 'Cliente desconocido'} → {product} ({date})"


def get_sales_channel_for_division(division_name):
    """
    Devuelve el canal de ventas correspondiente al nombre de la división.
    Ejemplos de entrada: "Pregrado", "Posgrado", "Educación Ejecutiva"
    """
    try:
        return Channel.objects.get(name__iexact=f"Ventas - {division_name.strip()}")
    except Channel.DoesNotExist:
        return None


class SalesSource(models.Model):
    code = models.CharField(max_length=4, unique=True)
    label = models.CharField(max_length=100)

    SOURCE_GROUPS = [
        ("web", "Web"),
        ("email", "Correo"),
        ("call", "Llamada"),
        ("event", "Evento"),
        ("referral", "Referido"),
        ("other", "Otro"),
    ]
    group = models.CharField(max_length=20, choices=SOURCE_GROUPS)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['group', 'label']
        verbose_name = "Fuente de origen"
        verbose_name_plural = "Fuentes de origen"

    def __str__(self):
        return f"[{self.code}] {self.label} ({self.get_group_display()})"

class SalesState(models.Model):
    value = models.SmallIntegerField(unique=True, help_text="Identificador único para ordenamiento y comparación.")
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True, help_text="Código único para referencia rápida, sin espacios ni caracteres especiales.")
    is_terminal = models.BooleanField(default=False)
    requires_attention = models.BooleanField(default=False)
    color = models.CharField(max_length=20, default='default')

    def __str__(self):
        return f"{self.value} – {self.name}"

    class Meta:
        ordering = ['value']
        verbose_name = 'estado de oportunidad'
        verbose_name_plural = 'estados de oportunidad'


class SalesOpportunity(BaseUUIDModelWithActiveStatus):
    person = models.ForeignKey('entities.Person', null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey('entities.Organization', null=True, blank=True, on_delete=models.SET_NULL)

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='sales_opportunities'
    )
    offering = models.ForeignKey(
        'offers.ProductOffering', null=True, blank=True, on_delete=models.SET_NULL
    )

    expected_value = models.DecimalField(max_digits=12, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="USD")

    SOURCE_CHOICES = [
        ("web", "Web"),
        ("email", "Correo"),
        ("call", "Llamada"),
        ("event", "Evento"),
        ("referral", "Referido"),
        ("other", "Otro"),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="web")
    source_detail = models.ForeignKey('SalesSource', null=True, blank=True, on_delete=models.SET_NULL)

    channel = models.ForeignKey('interactions.Channel', null=True, blank=True, on_delete=models.SET_NULL)

    stage = models.CharField(
        max_length=20,
        choices=[
            ('new', 'Nuevo'),
            ('interested', 'Interesado'),
            ('evaluating', 'Evaluando'),
            ('ready', 'Listo para decidir'),
            ('won', 'Convertido'),
            ('lost', 'Perdido'),
        ],
        default='new',
    )

    state = models.ForeignKey('SalesState', on_delete=models.PROTECT, null=True, blank=True)


    probability = models.PositiveSmallIntegerField(default=0)
    expected_closing_date = models.DateField(null=True, blank=True)

    representative = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('person', 'organization', 'offering')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.person} → {self.product}"

    def clean(self):
        super().clean()

        if self.stage == "lost" and not self.notes:
            raise ValidationError("Debe registrar el motivo de pérdida en las notas.")

        if self.stage == "won" and not self.expected_closing_date:
            raise ValidationError("Debe registrar una fecha estimada de cierre al convertir.")

        if not self.channel:
            if self.person and self.product:
                previous_interaction = (
                    Interaction.objects.filter(
                        individual_customer=self.person,
                        product=self.product,
                    ).order_by('-date').first()
                )
                if previous_interaction and previous_interaction.channel:
                    self.channel = previous_interaction.channel

            if not self.channel and hasattr(self.product, 'division') and self.product.division:
                suggested_channel = get_sales_channel_for_division(self.product.division.name)
                if suggested_channel:
                    self.channel = suggested_channel


class SalesSession(Interaction):
    opportunity = models.ForeignKey(
        SalesOpportunity, on_delete=models.CASCADE, related_name='sales_sessions'
    )
    representative = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class ContactMedium(models.IntegerChoices):
        UNKNOWN = 0, "Desconocido"
        EMAIL = 10, "Correo electrónico"
        OTHER = 20, "Otro medio"
        TEXTING = 30, "Mensaje de texto"
        WHATSAPP = 35, "WhatsApp"
        TELEPHONE = 40, "Teléfono o llamada de audio"
        VIDEOCALL = 60, "Video llamada"
        ON_CAMPUS = 80, "Vino al campus"
        OUT_OF_CAMPUS = 100, "Fuera del campus"

    contacted_via = models.PositiveSmallIntegerField(
        choices=ContactMedium.choices,
        default=ContactMedium.EMAIL,
        verbose_name="medio"
    )

    class Initiator(models.IntegerChoices):
        EITHER = 0, "Cualquiera"
        REP = 1, "Representante"
        CUSTOMER = 2, "Cliente"

    initiated_by = models.PositiveSmallIntegerField(
        choices=Initiator.choices,
        default=Initiator.EITHER,
        verbose_name="iniciado por"
    )

    how_long = models.DurationField(null=True, blank=True)
    lead_state = models.SmallIntegerField(null=True, blank=True)
    progress = models.SmallIntegerField(default=0)

    outcome = models.CharField(
        max_length=50,
        choices=[
            ('interested', 'Interesado'),
            ('not_interested', 'No interesado'),
            ('follow_up', 'Requiere seguimiento'),
            ('converted', 'Convertido'),
            ('no_show', 'No se presentó'),
        ],
        default='follow_up'
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)

    def clean(self):
        super().clean()

        if not self.channel and self.product and hasattr(self.product, 'division') and self.product.division:
            suggested_channel = get_sales_channel_for_division(self.product.division.name)
            if suggested_channel:
                self.channel = suggested_channel

    def save(self, *args, **kwargs):
        if not self.touchpoint:
            ventas_channel, _ = Channel.objects.get_or_create(name="Ventas")
            base_tp, _ = Touchpoint.objects.get_or_create(
                name="Sesión de ventas",
                channel=ventas_channel,
                defaults={"code": "sales_session", "funnel_stage": "engage"}
            )
            medium_label = self.get_contacted_via_display()
            tp_code = f"sales_session_{slugify(medium_label)}"

            medium_instance = base_tp.medium if hasattr(base_tp, 'medium') else None
            detailed_tp, _ = Touchpoint.objects.get_or_create(
                code=tp_code,
                channel=ventas_channel,
                defaults={
                    "name": f"Contacto vía {medium_label}",
                    "parent": base_tp,
                    "medium": medium_instance,
                }
            )
            if self.product and self.representative:
                tp_instance, _ = TouchpointInstance.objects.get_or_create(
                    touchpoint_class=detailed_tp,
                    product=self.product,
                    representative=self.representative
                )
                self.touchpoint = tp_instance

            self.touchpoint = detailed_tp
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']

class TaggedOpportunity(models.Model):
    opportunity = models.OneToOneField(
        'SalesOpportunity', related_name="applied_tags", on_delete=models.CASCADE
    )
    tags = models.ManyToManyField('users.UserTag')

    def __str__(self):
        return str(self.opportunity)

    @property
    def tags_list(self):
        return ",".join(str(tag.pk) for tag in self.tags.all())


class ContactList(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    offering = models.ForeignKey('offers.ProductOffering', null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    filter_stage = models.CharField(
        max_length=20,
        blank=True,
        choices=SalesOpportunity._meta.get_field('stage').choices,
    )
    filter_probability_min = models.PositiveSmallIntegerField(null=True, blank=True)
    filter_probability_max = models.PositiveSmallIntegerField(null=True, blank=True)
    filter_tags = models.ManyToManyField('users.UserTag', blank=True)

    filters = models.JSONField(blank=True, default=dict, help_text="Reglas dinámicas de filtrado para esta lista.")

    build_in_background = models.BooleanField(default=True)
    building_task_uuid = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f"Lista para {self.product}"

    def members_queryset(self):
        filters = self.filters or {}
        qs = SalesOpportunity.objects.filter(product=self.product)

        if self.offering:
            qs = qs.filter(offering=self.offering)

        if self.filter_stage:
            qs = qs.filter(stage=self.filter_stage)
        if self.filter_probability_min is not None:
            qs = qs.filter(probability__gte=self.filter_probability_min)
        if self.filter_probability_max is not None:
            qs = qs.filter(probability__lte=self.filter_probability_max)
        if self.filter_tags.exists():
            tagged_ids = TaggedOpportunity.objects.filter(opportunity__in=qs, tags__in=self.filter_tags.all()).values_list('opportunity', flat=True)
            qs = qs.filter(id__in=tagged_ids).distinct()

        if stage := filters.get("stage"):
            qs = qs.filter(stage=stage)

        if min_prob := filters.get("min_probability"):
            qs = qs.filter(probability__gte=min_prob)

        if max_prob := filters.get("max_probability"):
            qs = qs.filter(probability__lte=max_prob)

        if tags := filters.get("tags"):
            qs = qs.filter(person__tags__in=tags)

        if last_date := filters.get("last_interaction_before"):
            qs = qs.filter(person__interaction__date__lt=last_date).distinct()

        return qs.distinct()


    @property
    def members(self):
        from django.core.cache import cache
        cache_key = f"contactlist:{self.pk}:members"
        cached = cache.get(cache_key)
        if cached:
            return cached

        qs = self.members_queryset()

        result = list(qs)
        cache.set(cache_key, result, timeout=3600)
        return result
