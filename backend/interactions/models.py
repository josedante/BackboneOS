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

    def clean(self):
        if self.operated_by and self.represents_person is None:
            self.represents_person = self.operated_by

    def __str__(self):
        label = self.name or self.identifier or f"Agente ({self.get_agent_type_display()})"
        if self.represents_person:
            label += f" \u2194 {self.represents_person.full_name}"
        elif self.represents_organization:
            label += f" \u2194 {self.represents_organization.name}"
        return label


class Medium(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
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


class Channel(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    medium = models.ForeignKey(Medium, on_delete=models.SET_NULL, null=True, blank=True, related_name="channels")

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['medium']),
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


class TouchpointClass(BaseUUIDModelWithActiveStatus):
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
    touchpoint_class = models.ForeignKey(TouchpointClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='touchpoints')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, blank=True, unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    assigned_staff = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='assigned_touchpoints',
        help_text="Miembro del equipo responsable de este punto de contacto"
    )
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
        help_text="Etapa del embudo de ventas para el cual fue diseñado este punto de contacto"
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
            models.Index(fields=['touchpoint_class']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Interaction(BaseUUIDModelWithActiveStatus):
    person = models.ForeignKey('entities.Person', null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    organization = models.ForeignKey('entities.Organization', null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    touchpoint = models.ForeignKey(Touchpoint, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.ForeignKey(Action, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    representative = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='interactions_represented',
        help_text="Miembro de la organización que ejecutó esta interacción"
    )
    occurred_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='interactions', help_text="Producto vinculado a esta interacción"
    )
    JOB_STAGES = [
        ('job_oblivious', 'Trabajo Desconocido'),
        ('job_awareness', 'Conciencia del Trabajo'),
        ('job_research', 'Investigación'),
        ('job_decision', 'Toma de decisión'),
        ('job_execution', 'Ejecución'),
        ('job_solved', 'Resuelto'),
        ('stage_unknown', 'Etapa Desconocida'),
    ]
    jtbd_stage = models.CharField(
        max_length=50, blank=True, choices=JOB_STAGES, default='any',
        verbose_name="Etapa JTBD",
        help_text="Etapa del proceso de progreso del cliente (Jobs to Be Done)"
    )

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['person']),
            models.Index(fields=['organization']),
            models.Index(fields=['touchpoint']),
            models.Index(fields=['action']),
            models.Index(fields=['channel']),
            models.Index(fields=['agent']),
            models.Index(fields=['representative']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['is_active', 'occurred_at']),
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

    def __str__(self):
        return f"Interacción de {self.person or self.organization} en {self.touchpoint}"
