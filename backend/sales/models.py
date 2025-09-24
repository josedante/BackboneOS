from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid

from backend.models import BaseUUIDModelWithActiveStatus

from interactions.models import Interaction, Touchpoint, Channel, Agent
from connectors.protocols import TouchpointInferenceProtocol, TouchpointHint
from .resolvers import SalesTouchpointResolver, SalesMappingProvider

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

    class Meta:
        verbose_name = "Adquisición de Producto"
        verbose_name_plural = "Adquisiciones de Productos"
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['offering']),
            models.Index(fields=['price_paid']),
            models.Index(fields=['payment_modality']),
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

        # 6. Fecha de ocurrencia
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
    Crea el canal si no existe, usando el código de la división ProductDivision.
    Ejemplos de entrada: "Pregrado", "Posgrado", "Educación Ejecutiva"
    """
    from interactions.models import Channel
    from products.models import Division as ProductDivision
    
    division_name = division_name.strip()
    channel_name = f"Ventas - {division_name}"
    
    try:
        return Channel.objects.get(name__iexact=channel_name)
    except Channel.DoesNotExist:
        # Try to find the ProductDivision to get the correct code
        try:
            product_division = ProductDivision.objects.get(name=division_name)
            channel_code = f"sales_{product_division.code.lower()}"
        except ProductDivision.DoesNotExist:
            # Fallback: generate code from name
            channel_code = f"sales_{division_name.lower().replace(' ', '_')}"
        
        channel, created = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': channel_name,
                'description': f"Canal de ventas para {division_name}"
            }
        )
        return channel


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
                        person=self.person,
                        product=self.product,
                    ).order_by('-occurred_at').first()
                )
                if previous_interaction and previous_interaction.channel:
                    self.channel = previous_interaction.channel

            # Priority 1: Representative's division
            if not self.channel and self.representative:
                representative_division = self._get_representative_division_for_opportunity()
                if representative_division:
                    suggested_channel = get_sales_channel_for_division(representative_division.name)
                    if suggested_channel:
                        self.channel = suggested_channel
            
            # Priority 2: Product's division (fallback)
            if not self.channel and self.product and self.product.category and self.product.category.division:
                suggested_channel = get_sales_channel_for_division(self.product.category.division.name)
                if suggested_channel:
                    self.channel = suggested_channel
    
    def _get_representative_division_for_opportunity(self):
        """
        Get the division that the sales representative works for.
        
        The representative can be either a human User or an AI Agent.
        For AI agents, we look at their metadata or the organization they represent.
        
        Returns:
            Division or None: The representative's division
        """
        if not self.representative:
            return None
        
        representative = self.representative
        
        # Handle AI Agent representatives
        if hasattr(representative, 'agent_type') and representative.agent_type == 'ai':
            return self._get_ai_agent_division_for_opportunity(representative)
        
        # Handle human User representatives
        return self._get_human_representative_division_for_opportunity(representative)
    
    def _get_ai_agent_division_for_opportunity(self, ai_agent):
        """
        Get the division for an AI agent representative.
        
        AI agents can be associated with divisions through:
        1. Metadata configuration
        2. The organization they represent
        3. The person they represent (if that person has a division)
        
        Args:
            ai_agent: The AI Agent instance
            
        Returns:
            Division or None: The AI agent's division
        """
        # Check metadata for division assignment
        if ai_agent.metadata and 'division_code' in ai_agent.metadata:
            division_code = ai_agent.metadata['division_code']
            try:
                from our_institution.models import Division
                return Division.objects.get(code=division_code, is_active=True)
            except Division.DoesNotExist:
                pass
        
        # Check if AI agent represents an organization with a division
        if ai_agent.represents_organization:
            try:
                # Look for division through organization structure
                org = ai_agent.represents_organization
                if hasattr(org, 'divisions') and org.divisions.exists():
                    # Return the first active division
                    return org.divisions.filter(is_active=True).first()
            except AttributeError:
                pass
        
        # Check if AI agent represents a person with a division
        if ai_agent.represents_person:
            person = ai_agent.represents_person
            # Try to get division from person's position/unit
            try:
                if hasattr(person, 'position') and person.position:
                    position = person.position
                    if hasattr(position, 'unit') and position.unit:
                        return position.unit.division
            except AttributeError:
                pass
        
        # Check if AI agent is operated by a person with a division
        if ai_agent.operated_by:
            person = ai_agent.operated_by
            try:
                if hasattr(person, 'position') and person.position:
                    position = person.position
                    if hasattr(position, 'unit') and position.unit:
                        return position.unit.division
            except AttributeError:
                pass
        
        return None
    
    def _get_human_representative_division_for_opportunity(self, human_representative):
        """
        Get the division for a human representative.
        
        Args:
            human_representative: The User instance
            
        Returns:
            Division or None: The human representative's division
        """
        # Try to get division from representative's position/unit
        try:
            if hasattr(human_representative, 'position') and human_representative.position:
                position = human_representative.position
                if hasattr(position, 'unit') and position.unit:
                    return position.unit.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a direct division assignment
        try:
            if hasattr(human_representative, 'division') and human_representative.division:
                return human_representative.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a team with a division
        try:
            if hasattr(human_representative, 'team') and human_representative.team:
                if hasattr(human_representative.team, 'division') and human_representative.team.division:
                    return human_representative.team.division
        except AttributeError:
            pass
        
        return None


class SalesSession(Interaction):
    opportunity = models.ForeignKey(
        SalesOpportunity, on_delete=models.CASCADE, related_name='sales_sessions'
    )

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

    def infer_touchpoint_hint(self) -> TouchpointHint:
        """
        Infer touchpoint hint for sales session based on contact medium and context.
        
        Returns:
            TouchpointHint: Structured hint for touchpoint resolution
        """
        # Map contact mediums to standardized codes
        medium_mapping = {
            self.ContactMedium.EMAIL: "email",
            self.ContactMedium.TELEPHONE: "phone",
            self.ContactMedium.VIDEOCALL: "video",
            self.ContactMedium.WHATSAPP: "whatsapp",
            self.ContactMedium.TEXTING: "sms",
            self.ContactMedium.ON_CAMPUS: "in_person",
            self.ContactMedium.OUT_OF_CAMPUS: "in_person",
            self.ContactMedium.OTHER: "other",
            self.ContactMedium.UNKNOWN: "unknown",
        }
        
        medium_code = medium_mapping.get(self.contacted_via, "unknown")
        medium_label = self.get_contacted_via_display()
        
        # Determine channel code based on division (prioritize representative's division)
        channel_code = "sales"
        
        # Priority 1: Representative's division (highest priority)
        if self.representative:
            representative_division = self._get_representative_division()
            if representative_division:
                channel_code = f"sales_{representative_division.code.lower()}"
        
        # Priority 2: Product's division (fallback)
        if channel_code == "sales" and self.opportunity and self.opportunity.product and self.opportunity.product.category:
            if self.opportunity.product.category.division:
                channel_code = f"sales_{self.opportunity.product.category.division.code.lower()}"
        
        # Build metadata with sales context
        metadata = {
            "opportunity_id": str(self.opportunity.id) if self.opportunity else None,
            "representative_id": str(self.representative.id) if self.representative else None,
            "outcome": self.outcome,
            "progress": self.progress,
            "initiated_by": self.get_initiated_by_display(),
            "contact_medium": medium_label,
        }
        
        # Add representative type information
        if self.representative:
            if hasattr(self.representative, 'agent_type'):
                # AI Agent representative
                metadata["representative_type"] = "ai_agent"
                metadata["agent_type"] = self.representative.agent_type
                metadata["agent_name"] = self.representative.name
                if self.representative.metadata:
                    metadata["agent_metadata"] = self.representative.metadata
            else:
                # Human User representative
                metadata["representative_type"] = "human_user"
                metadata["representative_username"] = self.representative.username
        
        # Add product and division context if available
        if self.opportunity and self.opportunity.product:
            metadata["product_id"] = str(self.opportunity.product.id)
            if self.opportunity.product.category and self.opportunity.product.category.division:
                metadata["division"] = self.opportunity.product.category.division.name
                metadata["division_code"] = self.opportunity.product.category.division.code
        
        return TouchpointHint(
            code=f"sales.session.{medium_code}",
            channel_code=channel_code,
            medium_code=medium_code,
            label=f"Sesión de ventas vía {medium_label}",
            metadata=metadata
        )
    
    def _get_representative_division(self):
        """
        Get the division that the sales representative works for.
        
        The representative can be either a human User or an AI Agent.
        For AI agents, we look at their metadata or the organization they represent.
        
        Returns:
            Division or None: The representative's division
        """
        if not self.representative:
            return None
        
        representative = self.representative
        
        # Handle AI Agent representatives
        if hasattr(representative, 'agent_type') and representative.agent_type == 'ai':
            return self._get_ai_agent_division(representative)
        
        # Handle human User representatives
        return self._get_human_representative_division(representative)
    
    def _get_ai_agent_division(self, ai_agent):
        """
        Get the division for an AI agent representative.
        
        AI agents can be associated with divisions through:
        1. Metadata configuration
        2. The organization they represent
        3. The person they represent (if that person has a division)
        
        Args:
            ai_agent: The AI Agent instance
            
        Returns:
            Division or None: The AI agent's division
        """
        # Check metadata for division assignment
        if ai_agent.metadata and 'division_code' in ai_agent.metadata:
            division_code = ai_agent.metadata['division_code']
            try:
                from our_institution.models import Division
                return Division.objects.get(code=division_code, is_active=True)
            except Division.DoesNotExist:
                pass
        
        # Check if AI agent represents an organization with a division
        if ai_agent.represents_organization:
            try:
                # Look for division through organization structure
                org = ai_agent.represents_organization
                if hasattr(org, 'divisions') and org.divisions.exists():
                    # Return the first active division
                    return org.divisions.filter(is_active=True).first()
            except AttributeError:
                pass
        
        # Check if AI agent represents a person with a division
        if ai_agent.represents_person:
            person = ai_agent.represents_person
            # Try to get division from person's position/unit
            try:
                if hasattr(person, 'position') and person.position:
                    position = person.position
                    if hasattr(position, 'unit') and position.unit:
                        return position.unit.division
            except AttributeError:
                pass
        
        # Check if AI agent is operated by a person with a division
        if ai_agent.operated_by:
            person = ai_agent.operated_by
            try:
                if hasattr(person, 'position') and person.position:
                    position = person.position
                    if hasattr(position, 'unit') and position.unit:
                        return position.unit.division
            except AttributeError:
                pass
        
        return None
    
    def _get_human_representative_division(self, human_representative):
        """
        Get the division for a human representative.
        
        Args:
            human_representative: The User instance
            
        Returns:
            Division or None: The human representative's division
        """
        # Try to get division from representative's position/unit
        try:
            if hasattr(human_representative, 'position') and human_representative.position:
                position = human_representative.position
                if hasattr(position, 'unit') and position.unit:
                    return position.unit.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a direct division assignment
        try:
            if hasattr(human_representative, 'division') and human_representative.division:
                return human_representative.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a team with a division
        try:
            if hasattr(human_representative, 'team') and human_representative.team:
                if hasattr(human_representative.team, 'division') and human_representative.team.division:
                    return human_representative.team.division
        except AttributeError:
            pass
        
        return None

    def clean(self):
        super().clean()

        if not self.channel and self.product and self.product.category and self.product.category.division:
            suggested_channel = get_sales_channel_for_division(self.product.category.division.name)
            if suggested_channel:
                self.channel = suggested_channel

    def save(self, *args, **kwargs):
        # Use sales-specific touchpoint resolution framework if no touchpoint is set
        if not self.touchpoint:
            try:
                resolver = SalesTouchpointResolver(SalesMappingProvider())
                resolved_touchpoint = resolver.resolve(self)
                self.touchpoint = resolved_touchpoint
            except Exception as e:
                # Fallback to manual touchpoint creation if resolution fails
                self._create_manual_touchpoint()
        
        super().save(*args, **kwargs)
    
    def _create_manual_touchpoint(self):
        """
        Fallback method for manual touchpoint creation.
        This maintains backward compatibility if touchpoint resolution fails.
        """
        # Get or create division-specific sales channel (prioritize representative's division)
        sales_channel = None
        
        # Priority 1: Representative's division
        if self.representative:
            representative_division = self._get_representative_division()
            if representative_division:
                channel_name = f"Ventas - {representative_division.name}"
                # Get or create medium for the contact method
                medium = self._get_or_create_medium_for_contact()
                sales_channel, _ = Channel.objects.get_or_create(
                    name=channel_name,
                    defaults={
                        "code": f"sales_{representative_division.code.lower()}",
                        "description": f"Canal de ventas para {representative_division.name}",
                        "medium": medium
                    }
                )
        
        # Priority 2: Product's division (fallback)
        if not sales_channel and self.opportunity and self.opportunity.product and self.opportunity.product.category:
            if self.opportunity.product.category.division:
                channel_name = f"Ventas - {self.opportunity.product.category.division.name}"
                medium = self._get_or_create_medium_for_contact()
                sales_channel, _ = Channel.objects.get_or_create(
                    name=channel_name,
                    defaults={
                        "code": f"sales_{self.opportunity.product.category.division.code.lower()}",
                        "description": f"Canal de ventas para {self.opportunity.product.category.division.name}",
                        "medium": medium
                    }
                )
            else:
                medium = self._get_or_create_medium_for_contact()
                sales_channel, _ = Channel.objects.get_or_create(
                    name="Ventas",
                    defaults={"code": "sales", "description": "Canal de ventas general", "medium": medium}
                )
        else:
            medium = self._get_or_create_medium_for_contact()
            sales_channel, _ = Channel.objects.get_or_create(
                name="Ventas",
                defaults={"code": "sales", "description": "Canal de ventas general", "medium": medium}
            )
        
        # Create base touchpoint
        base_tp, _ = Touchpoint.objects.get_or_create(
            name="Sesión de ventas",
            channel=sales_channel,
            defaults={"code": "sales_session"}
        )
        
        # Create detailed touchpoint based on contact medium
        medium_label = self.get_contacted_via_display()
        tp_code = f"sales_session_{slugify(medium_label)}"
        
        detailed_tp, _ = Touchpoint.objects.get_or_create(
            code=tp_code,
            channel=sales_channel,
            defaults={
                "name": f"Contacto vía {medium_label}",
                "description": f"Touchpoint de ventas creado manualmente para {medium_label}"
            }
        )
        
        # Assign the detailed touchpoint directly
        self.touchpoint = detailed_tp

    def _get_or_create_medium_for_contact(self):
        """
        Get or create Medium object based on the contact method used.
        
        Returns:
            Medium: The medium object for the contact method
        """
        from interactions.models import Medium
        
        # Map contact mediums to medium codes
        medium_mapping = {
            self.ContactMedium.EMAIL: "email",
            self.ContactMedium.TELEPHONE: "phone", 
            self.ContactMedium.VIDEOCALL: "video",
            self.ContactMedium.WHATSAPP: "whatsapp",
            self.ContactMedium.TEXTING: "sms",
            self.ContactMedium.ON_CAMPUS: "in_person",
            self.ContactMedium.OUT_OF_CAMPUS: "in_person",
            self.ContactMedium.OTHER: "other",
            self.ContactMedium.UNKNOWN: "unknown",
        }
        
        medium_code = medium_mapping.get(self.contacted_via, "unknown")
        medium_name = self.get_contacted_via_display()
        
        medium, _ = Medium.objects.get_or_create(
            code=medium_code,
            defaults={
                "name": medium_name,
                "description": f"Medio de contacto: {medium_name}"
            }
        )
        
        return medium

    class Meta:
        ordering = ['-occurred_at']

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
