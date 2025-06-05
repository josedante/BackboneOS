from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify
import uuid

from backend.models import BaseUUIDModel, BaseUUIDModelWithActiveStatus


class Country(models.Model):
    """Países del mundo"""
    iso3_code = models.CharField(max_length=3, primary_key=True, verbose_name="Código ISO3")
    iso2_code = models.CharField(max_length=2, verbose_name="Código ISO2", unique=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    official_name = models.CharField(max_length=150, verbose_name="Nombre oficial")
    
    # Configuración regional
    phone_code = models.CharField(max_length=5, blank=True, verbose_name="Código telefónico")
    currency_code = models.CharField(max_length=3, blank=True, verbose_name="Código de moneda")
    timezone = models.CharField(max_length=50, blank=True, verbose_name="Zona horaria principal")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ['name']

    def __str__(self):
        return self.name


class Industry(BaseUUIDModelWithActiveStatus):
    """Sectores o industrias de la economía"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Jerarquía de industrias
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='sub_industries',
        verbose_name="Industria padre"
    )
    
    # Clasificación CIIU o similar
    ciiu_code = models.CharField(max_length=10, blank=True, verbose_name="Código CIIU")
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Industria"
        verbose_name_plural = "Industrias"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
    
    @property
    def full_hierarchy_name(self):
        """Nombre completo con jerarquía"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class FunctionOrResponsibility(BaseUUIDModelWithActiveStatus):
    """Funciones o áreas de responsabilidad organizacional"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Jerarquía de funciones
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_functions',
        verbose_name="Función padre"
    )
    
    # Nivel organizacional típico
    OPERATIONAL = 'OP'
    TACTICAL = 'TA'
    STRATEGIC = 'ST'
    EXECUTIVE = 'EX'
    LEVEL_CHOICES = (
        (OPERATIONAL, 'Operativo'),
        (TACTICAL, 'Táctico'),
        (STRATEGIC, 'Estratégico'),
        (EXECUTIVE, 'Ejecutivo'),
    )
    typical_level = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
        verbose_name="Nivel típico"
    )
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Función o Responsabilidad"
        verbose_name_plural = "Funciones o Responsabilidades"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Skill(BaseUUIDModelWithActiveStatus):
    """Habilidades técnicas y blandas"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Categorización de habilidades
    TECHNICAL = 'TE'
    SOFT = 'SO'
    LEADERSHIP = 'LE'
    ANALYTICAL = 'AN'
    CREATIVE = 'CR'
    SKILL_TYPES = (
        (TECHNICAL, 'Técnica'),
        (SOFT, 'Blanda'),
        (LEADERSHIP, 'Liderazgo'),
        (ANALYTICAL, 'Analítica'),
        (CREATIVE, 'Creativa'),
    )
    skill_type = models.CharField(
        max_length=2,
        choices=SKILL_TYPES,
        default=TECHNICAL,
        verbose_name="Tipo de habilidad"
    )
    
    # Nivel de especialización requerido
    BASIC = 'BA'
    INTERMEDIATE = 'IN'
    ADVANCED = 'AD'
    EXPERT = 'EX'
    LEVEL_CHOICES = (
        (BASIC, 'Básico'),
        (INTERMEDIATE, 'Intermedio'),
        (ADVANCED, 'Avanzado'),
        (EXPERT, 'Experto'),
    )
    typical_level_required = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        default=INTERMEDIATE,
        verbose_name="Nivel típico requerido"
    )
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"
        ordering = ['skill_type', 'display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_skill_type_display()})"


class PersonalIDType(BaseUUIDModelWithActiveStatus):
    """Tipos de documentos de identidad personal"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name="País"
    )
    code = models.CharField(max_length=10, verbose_name="Código")
    
    # Configuración de validación
    regex_pattern = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Patrón de validación",
        help_text="Expresión regular para validar el formato"
    )
    max_length = models.PositiveIntegerField(default=20, verbose_name="Longitud máxima")
    min_length = models.PositiveIntegerField(default=1, verbose_name="Longitud mínima")
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Tipo de Documento Personal"
        verbose_name_plural = "Tipos de Documentos Personales"
        unique_together = ('country', 'code')
        ordering = ['country__name', 'display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.country.name})"


class OrganizationType(BaseUUIDModelWithActiveStatus):
    """Tipos de organizaciones"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Clasificación por propiedad
    PRIVATE = "PVT"
    PUBLIC = "PUB"
    MIXED = "MIX"
    NGO = "NGO"
    OWNERSHIP_TYPES = (
        (PRIVATE, "Privada"),
        (PUBLIC, "Pública"),
        (MIXED, "Mixta"),
        (NGO, "ONG/Sin fines de lucro"),
    )
    ownership_type = models.CharField(
        max_length=3,
        choices=OWNERSHIP_TYPES,
        default=PRIVATE,
        verbose_name="Tipo de propiedad"
    )
    
    # Clasificación por tamaño típico
    MICRO = "MI"
    SMALL = "SM"
    MEDIUM = "ME"
    LARGE = "LA"
    ENTERPRISE = "EN"
    SIZE_TYPES = (
        (MICRO, "Microempresa"),
        (SMALL, "Pequeña"),
        (MEDIUM, "Mediana"),
        (LARGE, "Grande"),
        (ENTERPRISE, "Corporación"),
    )
    typical_size = models.CharField(
        max_length=2,
        choices=SIZE_TYPES,
        blank=True,
        verbose_name="Tamaño típico"
    )
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Tipo de Organización"
        verbose_name_plural = "Tipos de Organización"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class OrganizationalIDType(BaseUUIDModelWithActiveStatus):
    """Tipos de documentos de identidad organizacional"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name="País"
    )
    code = models.CharField(max_length=10, verbose_name="Código")
    
    # Configuración de validación
    regex_pattern = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Patrón de validación"
    )
    max_length = models.PositiveIntegerField(default=20, verbose_name="Longitud máxima")
    min_length = models.PositiveIntegerField(default=1, verbose_name="Longitud mínima")
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Tipo de Documento Organizacional"
        verbose_name_plural = "Tipos de Documentos Organizacionales"
        unique_together = ('country', 'code')
        ordering = ['country__name', 'display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.country.name})"


class DescriptorFamily(models.Model):
    """
    Familia semántica a la que pertenece un descriptor del mundo.
    Ejemplos: Industria, Habilidad, Función, Terreno, Marco legal.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, primary_key=True)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True, verbose_name="Activo")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorldDescriptor(BaseUUIDModelWithActiveStatus):
    """
    Descriptor semántico del mundo, agrupado por familia.
    Ejemplos: 'Educación', 'Tecnología médica', 'Montañoso', 'Solar', etc.
    """
    family = models.ForeignKey(DescriptorFamily, on_delete=models.CASCADE, related_name="descriptors")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    # Opcional: para soportar relaciones jerárquicas
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    class Meta:
        unique_together = ("family", "name")
        ordering = ["family__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.family.code})"


class MarketSegment(BaseUUIDModelWithActiveStatus):
    """Segmentos de mercado específicos"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Relaciones con otras entidades del mundo
    industries = models.ManyToManyField(
        Industry,
        blank=True,
        verbose_name="Industrias relacionadas"
    )
    functions = models.ManyToManyField(
        FunctionOrResponsibility,
        blank=True,
        verbose_name="Funciones típicas"
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        verbose_name="Habilidades relevantes"
    )
    descriptors = models.ManyToManyField(
        WorldDescriptor,
        blank=True,
        verbose_name="Descriptores semánticos"
    )
    
    # Características del segmento
    B2B = 'B2B'
    B2C = 'B2C'
    B2G = 'B2G'
    SEGMENT_TYPES = (
        (B2B, 'Business to Business'),
        (B2C, 'Business to Consumer'),
        (B2G, 'Business to Government'),
    )
    segment_type = models.CharField(
        max_length=3,
        choices=SEGMENT_TYPES,
        default=B2B,
        verbose_name="Tipo de segmento"
    )
    
    display_order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Segmento de Mercado"
        verbose_name_plural = "Segmentos de Mercado"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Etiquetas flexibles para clasificación dinámica"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug = models.SlugField(
        max_length=50,
        primary_key=True,
        blank=True,
        verbose_name="Slug"
    )
    # description = models.TextField(blank=True, verbose_name="Descripción")
    # color = models.CharField(
    #     max_length=7,
    #     default='#6B7280',
    #     verbose_name="Color",
    #     help_text="Color en formato hexadecimal"
    # )
    
    # # Categorías de tags
    # GENERAL = 'GE'
    # INDUSTRY = 'IN'
    # FUNCTION = 'FU'
    # SKILL = 'SK'
    # LOCATION = 'LO'
    # STATUS = 'ST'
    # TAG_CATEGORIES = (
    #     (GENERAL, 'General'),
    #     (INDUSTRY, 'Industria'),
    #     (FUNCTION, 'Función'),
    #     (SKILL, 'Habilidad'),
    #     (LOCATION, 'Ubicación'),
    #     (STATUS, 'Estado'),
    # )
    # category = models.CharField(
    #     max_length=2,
    #     choices=TAG_CATEGORIES,
    #     default=GENERAL,
    #     verbose_name="Categoría"
    # )
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Genera el slug automáticamente al guardar"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AcademicDegree(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=50, unique=True)
    code = models.PositiveSmallIntegerField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "code",
        ]


class Position(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=2, unique=True, default="--")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "name",
        ]