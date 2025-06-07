from django.db import models
from world.models import Country, Industry, OrganizationType
from backend.models import BaseUUIDModelWithActiveStatus
import uuid


class OurOrganization(BaseUUIDModelWithActiveStatus):
    """
    Representa a la organización propietaria de esta instancia del sistema.
    Se espera que solo haya una instancia activa a la vez.
    """
    name = models.CharField(max_length=190)
    legal_name = models.CharField(max_length=190, blank=True)
    org_type = models.ForeignKey(OrganizationType, null=True, blank=True, on_delete=models.SET_NULL)
    industry = models.ForeignKey(Industry, null=True, blank=True, on_delete=models.SET_NULL)

    tax_id = models.CharField(max_length=30, blank=True, verbose_name="RUC u otro ID tributario")
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)

    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="org/logos/", null=True, blank=True)

    # Contacto directo
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = "Nuestra Organización"
        verbose_name_plural = "Nuestra Organización"

    def __str__(self):
        return self.legal_name or self.name

    def clean(self):
        # Garantizar unicidad de instancia activa
        if self.is_active and OurOrganization.objects.exclude(pk=self.pk).filter(is_active=True).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError("Solo puede haber una organización activa.")


class Division(BaseUUIDModelWithActiveStatus):
    """División estructural de la organización"""
    organization = models.ForeignKey(OurOrganization, on_delete=models.CASCADE, related_name="divisions")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "División"
        verbose_name_plural = "Divisiones"
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'], 
                name='unique_division_name_per_org'
            ),
            models.UniqueConstraint(
                fields=['organization', 'code'], 
                name='unique_division_code_per_org'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    @property
    def units_count(self):
        """Número de unidades en esta división"""
        return self.units.filter(is_active=True).count()
    
    @property
    def teams_count(self):
        """Número de equipos en esta división"""
        return self.teams.filter(is_active=True).count()
    
    @property
    def positions_count(self):
        """Número de posiciones en todas las unidades de esta división"""
        count = 0
        for unit in self.units.filter(is_active=True):
            count += unit.positions.filter(is_active=True).count()
        return count


class Seat(BaseUUIDModelWithActiveStatus):
    """Sede física de la organización propietaria"""
    SEAT_TYPES = (
        ("HQT", "Sede Central"),
        ("SUB", "Sucursal"),
        ("OFF", "Oficina"),
        ("LOC", "Local"),
    )

    organization = models.ForeignKey(OurOrganization, on_delete=models.CASCADE, related_name="seats")
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)
    category = models.CharField(max_length=3, choices=SEAT_TYPES, default="LOC")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Unit(BaseUUIDModelWithActiveStatus):
    """Unidad organizativa dentro de una división"""
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="units")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, verbose_name="Código de la unidad")
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name']
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        constraints = [
            models.UniqueConstraint(
                fields=['division', 'code'], 
                name='unique_unit_code_per_division'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.division.name})"
    
    @property
    def positions_count(self):
        """Número de cargos en esta unidad"""
        return self.positions.filter(is_active=True).count()

    @property
    def full_path(self):
        """Ruta completa de la unidad incluyendo división y jerarquía"""
        path_parts = []
        if self.division:
            path_parts.append(self.division.name)
        
        # Construir jerarquía de unidades
        ancestors = []
        current = self
        while current.parent:
            ancestors.append(current.parent.name)
            current = current.parent
        
        path_parts.extend(reversed(ancestors))
        path_parts.append(self.name)
        
        return " > ".join(path_parts)


class Position(BaseUUIDModelWithActiveStatus):
    """Posición o cargo dentro de una unidad organizativa"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="positions")
    name = models.CharField(max_length=200, verbose_name="Nombre del cargo")
    code = models.CharField(max_length=20, verbose_name="Código del cargo")
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Posición"
        verbose_name_plural = "Posiciones"
        constraints = [
            models.UniqueConstraint(
                fields=['unit', 'code'], 
                name='unique_position_code_per_unit'
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.unit.name}"


class Team(BaseUUIDModelWithActiveStatus):
    """Equipo de trabajo dentro de una división"""
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=190)
    code = models.CharField(max_length=20, verbose_name="Código del equipo")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        constraints = [
            models.UniqueConstraint(
                fields=['division', 'code'], 
                name='unique_team_code_per_division'
            ),
            models.UniqueConstraint(
                fields=['division', 'name'], 
                name='unique_team_name_per_division'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.division.name})"
