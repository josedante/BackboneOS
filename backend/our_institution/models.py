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
    """Unidad organizativa dentro de la organización propietaria"""
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Position(BaseUUIDModelWithActiveStatus):
    """Posición o cargo dentro de una unidad organizativa"""
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Team(BaseUUIDModelWithActiveStatus):
    """Equipo de trabajo dentro de la organización propietaria"""
    name = models.CharField(max_length=190, unique=True)
    code = models.CharField(max_length=20, unique=True, default=uuid.uuid4)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipos"
