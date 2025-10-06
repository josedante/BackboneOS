from django.db import models
from django.core.exceptions import ValidationError
from backend.models import BaseUUIDModelWithActiveStatus

from world.models import (
    Industry,
    FunctionOrResponsibility as Area,
    Skill,
    WorldDescriptor,
)


class Agent(BaseUUIDModelWithActiveStatus):
    ''' This defines an Agent for the user or potential customer '''
    
    AGENT_TYPES = [
        ('browser', 'Navegador Web'),
        ('human', 'Humano'),
        ('system', 'Sistema externo'),
        ('device', 'Dispositivo físico'),
        ('bot', 'Bot automatizado'),
        ('ai', 'Agente de Inteligencia Artificial'),
        ('other', 'Otro'),
    ]

    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES, default='other')
    name = models.CharField(max_length=100, blank=True)
    identifier = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    operated_by = models.ForeignKey(
        'entities.Person', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='agents_operated'
    )
    represents_person = models.ForeignKey(
        'entities.Person', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='agents_representing_as_person'
    )
    represents_organization = models.ForeignKey(
        'entities.Organization', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='agents_representing_as_organization'
    )

    class Meta:
        ordering = ['agent_type', 'name']
        indexes = [
            models.Index(fields=['agent_type']),
            models.Index(fields=['identifier']),
            models.Index(fields=['is_active']),
            models.Index(fields=['operated_by']),
            models.Index(fields=['represents_person']),
            models.Index(fields=['represents_organization']),
        ]

    def generate_name(self):
        if self.agent_type == 'browser':
            return self.metadata.get('user_agent', '[navegador anónimo]')[:40] if self.metadata else '[navegador]'
        elif self.agent_type == 'human':
            return str(self.operated_by or self.represents_person or 'Humano')
        elif self.agent_type == 'bot':
            return f"Bot {self.identifier}" if self.identifier else 'Bot sin ID'
        elif self.agent_type == 'system':
            return f"Sistema externo ({self.identifier})" if self.identifier else 'Sistema externo'
        return f"Agente ({self.get_agent_type_display()})"

    def clean(self):
        if self.represents_person and self.represents_organization:
            raise ValidationError("Un agente no puede representar simultáneamente a una persona y una organización.")

        if not self.name:
            self.name = self.generate_name()

    def __str__(self):
        label = self.name or self.generate_name()
        if self.represents_person:
            label += f" \u2194 {self.represents_person.full_name}"
        elif self.represents_organization:
            label += f" \u2194 {self.represents_organization.name}"
        return label


class Medium(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # NEW: Communication characteristics
    COMMUNICATION_TYPE_CHOICES = [
        ('synchronous', 'Comunicación Síncrona'),
        ('asynchronous', 'Comunicación Asíncrona'),
        ('real_time', 'Tiempo Real'),
        ('batch', 'Por Lotes')
    ]
    communication_type = models.CharField(
        max_length=20,
        choices=COMMUNICATION_TYPE_CHOICES,
        default='asynchronous',
        help_text="Tipo de comunicación que soporta este medium"
    )
    

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['communication_type']),
        ]

    def __str__(self):
        return self.name


class Channel(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    
    # REMOVED: medium = models.ForeignKey(Medium, ...)  # ← REMOVED - Medium ahora está en Touchpoint
    
    # NEW: Source classification
    SOURCE_TYPE_CHOICES = [
        ('external', 'Fuente Externa'),
        ('owned', 'Propiedad Propia'),
        ('direct', 'Tráfico Directo'),
        ('unknown', 'Fuente Desconocida')
    ]
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='external',
        help_text="Tipo de fuente de tráfico"
    )
    

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['source_type']),
        ]

    def __str__(self):
        return self.name


class ActionType(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Action(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    action_type = models.ForeignKey(ActionType, null=True, blank=True, on_delete=models.SET_NULL, related_name='actions')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class TouchpointType(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Touchpoint(BaseUUIDModelWithActiveStatus):
    # NEW: Three-dimensional classification
    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='touchpoints',
        help_text="Canal de tráfico (DÓNDE vino la interacción)"
    )
    medium = models.ForeignKey(
        Medium, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='touchpoints',
        help_text="Método de comunicación (CÓMO se comunica)"
    )
    touchpoint_type = models.ForeignKey(
        TouchpointType, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='touchpoints',
        help_text="Tipo funcional (QUÉ tipo de touchpoint)"
    )
    
    # Hierarchical structure for campaign/creative granularity
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text="Parent touchpoint for hierarchical organization (e.g., campaign-level child of source-level parent)"
    )
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, blank=True, unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    assigned_staff = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='assigned_touchpoints',
        help_text="Miembro del equipo responsable de este punto de contacto"
    )

    # Content type choices for strategic communication classification
    AFFINITY = 'affinity'
    CATEGORY = 'category'
    PRODUCT = 'product'
    BRAND = 'brand'
    CONTENT_TYPE_CHOICES = [
        (AFFINITY, 'Afinidad'),
        (CATEGORY, 'Categoría'),
        (PRODUCT, 'Producto'),
        (BRAND, 'Marca'),
    ]
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipo de contenido comunicacional",
        help_text="Clasificación del enfoque estratégico del contenido asociado a este touchpoint"
    )

    product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='touchpoints', help_text="Producto principal asociado a este punto de contacto"
    )
    
    related_industries = models.ManyToManyField(Industry, blank=True)
    related_functions = models.ManyToManyField(Area, blank=True)
    related_skills = models.ManyToManyField(Skill, blank=True)
    related_descriptors = models.ManyToManyField(WorldDescriptor, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['touchpoint_type']),  # Updated from touchpoint_type
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['channel']),
            models.Index(fields=['medium']),  # NEW: Medium index
            # NEW: Composite indexes for three-dimensional analysis
            models.Index(fields=['channel', 'medium']),
            models.Index(fields=['medium', 'touchpoint_type']),
            models.Index(fields=['channel', 'touchpoint_type']),
        ]

    def __str__(self):
        return self.name


class Interaction(BaseUUIDModelWithActiveStatus):
    """
    Represents an interaction between a person and a touchpoint.
    
    The organization field is optional and serves to distinguish between:
    - Corporate customers: interactions with organization set (B2B)
    - Individual customers: interactions without organization (B2C)
    """
    person = models.ForeignKey('entities.Person', null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    organization = models.ForeignKey(
        'entities.Organization', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='interactions',
        help_text="Optional organization for corporate customers (B2B). Leave empty for individual customers (B2C)."
    )
    touchpoint = models.ForeignKey(Touchpoint, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.ForeignKey(Action, on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    representative = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='interactions_represented',
        help_text="Miembro de la organización que ejecutó esta interacción"
    )

    payload = models.JSONField(blank=True, null=True)

    occurred_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=200, blank=True)

    # Duración de la interacción
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Contexto de sesión para agrupación
    session_id = models.CharField(max_length=100, blank=True)

    # Geolocalización
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Referrer y contexto
    referrer_url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    metadata = models.JSONField(blank=True, null=True)

    product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='interactions', help_text="Producto vinculado a esta interacción"
        
    )

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['person']),
            models.Index(fields=['organization']),
            models.Index(fields=['touchpoint']),
            models.Index(fields=['action']),
            models.Index(fields=['agent']),
            models.Index(fields=['representative']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['is_active', 'occurred_at']),
            # Composite index for touchpoint-channel filtering (common pattern)
            models.Index(fields=['touchpoint', 'is_active']),
            # Nuevos índices para campos añadidos
            models.Index(fields=['session_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['duration_seconds']),
            models.Index(fields=['source']),
            # Índices compuestos para analytics
            models.Index(fields=['touchpoint', 'occurred_at']),
            models.Index(fields=['agent', 'occurred_at']),
        ]

    def clean(self):
        if self.person is None and self.agent:
            expected = self.agent.represents_person or self.agent.operated_by
            if expected and self.person != expected:
                self.person = expected

        if self.organization is None and self.agent:
            expected_org = self.agent.represents_organization
            if expected_org and self.organization != expected_org:
                self.organization = expected_org

        if not self.representative and self.touchpoint and self.touchpoint.assigned_staff:
            self.representative = self.touchpoint.assigned_staff

        if not self.product and self.touchpoint and self.touchpoint.product:
            self.product = self.touchpoint.product

    @property
    def resolved_person(self):
        return self.person or (self.agent.represents_person if self.agent else None) or (self.agent.operated_by if self.agent else None)

    @property
    def resolved_organization(self):
        return self.organization or (self.agent.represents_organization if self.agent else None)

    @property
    def channel(self):
        """Get the channel through the touchpoint relationship"""
        return self.touchpoint.channel if self.touchpoint else None

    @property
    def geographic_location(self):
        """Retorna tupla (lat, lng) si ambas coordenadas están disponibles"""
        if self.latitude is not None and self.longitude is not None:
            return (float(self.latitude), float(self.longitude))
        return None

    @property
    def has_duration(self):
        """Indica si la interacción tiene duración medida"""
        return self.duration_seconds is not None and self.duration_seconds > 0

    @property
    def duration_display(self):
        """Formatea la duración para display humano"""
        if not self.has_duration:
            return "Sin duración"
        
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s" if remaining_seconds else f"{minutes}m"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m" if remaining_minutes else f"{hours}h"

    def __str__(self):
        entity = self.resolved_person or self.resolved_organization
        if entity:
            return f"Interacción de {entity} en {self.touchpoint or 'punto no especificado'}"
        return f"Interacción anónima en {self.touchpoint or 'punto no especificado'}"
