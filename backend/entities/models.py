from django.db import models
from django.core.exceptions import ValidationError
from world.models import (
    Country,
    PersonalIDType,
    OrganizationalIDType,
    OrganizationType,
    Industry,
    FunctionOrResponsibility,
    Skill,
    AcademicDegree,
)
from backend.models import BaseUUIDModelWithActiveStatus


class Person(BaseUUIDModelWithActiveStatus):
    first_name = models.CharField(max_length=63, blank=True)
    middle_name = models.CharField(max_length=63, blank=True)
    fathers_name = models.CharField(max_length=63, blank=True)
    mothers_name = models.CharField(max_length=63, blank=True)

    gender = models.CharField(
        max_length=2,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('UD', 'No definido')],
        default='UD'
    )
    birthday = models.DateField(null=True, blank=True)
    marital_status = models.CharField(
        max_length=2,
        choices=[
            ('SG', 'Soltero'),
            ('MR', 'Casado'),
            ('DV', 'Divorciado'),
            ('SP', 'Separado'),
            ('WD', 'Viudo'),
            ('CH', 'Conviviente'),
            ('UD', 'No definido'),
        ],
        default='UD'
    )

    country_of_nationality = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    id_type = models.ForeignKey(PersonalIDType, null=True, blank=True, on_delete=models.SET_NULL)
    id_number = models.CharField(max_length=50, blank=True)

    portrait = models.ImageField(upload_to="public/profiles/", null=True, blank=True)

    class Meta:
        unique_together = ("id_type", "id_number")

    def __str__(self):
        return f"{self.first_name} {self.fathers_name}".strip()

    @property
    def full_name(self):
        """Nombre completo de la persona"""
        parts = [self.first_name, self.middle_name, self.fathers_name, self.mothers_name]
        return " ".join(part for part in parts if part).strip()

    @property
    def primary_contact(self):
        """Contacto principal de la persona"""
        return self.contacts.filter(is_primary=True, is_active=True).first()

    @property
    def primary_email(self):
        """Email principal de la persona"""
        primary = self.primary_contact
        return primary.email if primary and primary.email else None

    @property
    def primary_phone(self):
        """Teléfono principal de la persona"""
        primary = self.primary_contact
        return primary.phone if primary and primary.phone else None

    @property
    def primary_address(self):
        """Dirección principal de la persona"""
        return self.physicaladdress_set.filter(
            is_primary=True, is_active=True
        ).first()

    def get_semantic_profile(self):
        """Perfil semántico completo de la persona"""
        try:
            profile = self.individualprofile
            return {
                'academic_degree': profile.academic_degree,
                'industries': list(profile.industries.filter(is_active=True)),
                'skills': list(profile.skills.filter(is_active=True)),
                'functions': list(profile.functions.filter(is_active=True)),
                'preferred_contact_medium': profile.preferred_contact_medium,
                'allows_marketing': profile.allows_marketing
            }
        except IndividualProfile.DoesNotExist:
            return None

    def has_complete_profile(self):
        """Verifica si la persona tiene un perfil completo"""
        try:
            profile = self.individualprofile
            return (
                bool(self.first_name and self.fathers_name) and
                bool(self.primary_contact) and
                bool(profile.academic_degree) and
                profile.industries.exists()
            )
        except IndividualProfile.DoesNotExist:
            return False

    @property
    def full_name(self):
        """Nombre completo de la persona"""
        parts = [self.first_name, self.middle_name, self.fathers_name, self.mothers_name]
        return " ".join(part for part in parts if part).strip()

    @property
    def primary_contact(self):
        """Contacto principal de la persona"""
        return self.contacts.filter(is_primary=True, is_active=True).first()

    @property
    def primary_email(self):
        """Email principal de la persona"""
        primary = self.primary_contact
        return primary.email if primary and primary.email else None

    @property
    def primary_phone(self):
        """Teléfono principal de la persona"""
        primary = self.primary_contact
        return primary.phone if primary and primary.phone else None

    @property
    def primary_address(self):
        """Dirección principal de la persona"""
        return self.physicaladdress_set.filter(
            is_primary=True, is_active=True
        ).first()

    def get_semantic_profile(self):
        """Perfil semántico completo de la persona"""
        try:
            profile = self.individualprofile
            return {
                'academic_degree': profile.academic_degree,
                'industries': list(profile.industries.filter(is_active=True)),
                'skills': list(profile.skills.filter(is_active=True)),
                'functions': list(profile.functions.filter(is_active=True)),
                'preferred_contact_medium': profile.preferred_contact_medium,
                'allows_marketing': profile.allows_marketing
            }
        except IndividualProfile.DoesNotExist:
            return None

    def has_complete_profile(self):
        """Verifica si la persona tiene un perfil completo"""
        try:
            profile = self.individualprofile
            return (
                bool(self.first_name and self.fathers_name) and
                bool(self.primary_contact) and
                bool(profile.academic_degree) and
                profile.industries.exists()
            )
        except IndividualProfile.DoesNotExist:
            return False


class ContactDetail(BaseUUIDModelWithActiveStatus):
    person = models.ForeignKey(Person, related_name="contacts", on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_primary = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["is_primary", "verified"])]

    def __str__(self):
        return self.email or self.phone or "Contacto"


class IndividualProfile(BaseUUIDModelWithActiveStatus):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)

    functions = models.ManyToManyField(FunctionOrResponsibility, blank=True)
    industries = models.ManyToManyField(Industry, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    academic_degree = models.ForeignKey(AcademicDegree, null=True, blank=True, on_delete=models.SET_NULL)

    accepts_privacy_policy = models.BooleanField(default=False)
    allows_marketing = models.BooleanField(default=False)

    preferred_contact_medium = models.CharField(
        max_length=2,
        choices=[
            ('EM', 'Email'),
            ('TX', 'Texto'),
            ('PH', 'Teléfono'),
            ('VD', 'Videollamada'),
            ('IP', 'Presencial'),
            ('NN', 'Desconocido'),
        ],
        default='NN'
    )


class Organization(BaseUUIDModelWithActiveStatus):
    name = models.CharField(max_length=190)
    legal_name = models.CharField(max_length=190, blank=True)
    org_type = models.ForeignKey(OrganizationType, null=True, blank=True, on_delete=models.SET_NULL)
    industry = models.ForeignKey(Industry, null=True, blank=True, on_delete=models.SET_NULL)

    id_type = models.ForeignKey(OrganizationalIDType, null=True, blank=True, on_delete=models.SET_NULL)
    id_number = models.CharField(max_length=20)

    main_address = models.CharField(max_length=190, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("id_type", "id_number")

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        """Nombre para mostrar (legal_name si existe, sino name)"""
        return self.legal_name if self.legal_name else self.name

    @property
    def primary_address(self):
        """Dirección principal de la organización"""
        return self.physicaladdress_set.filter(
            is_primary=True, is_active=True
        ).first()

    @property
    def billing_address(self):
        """Dirección de facturación de la organización"""
        return self.physicaladdress_set.filter(
            use_for_billing=True, is_active=True
        ).first()

    def get_all_addresses(self):
        """Todas las direcciones activas de la organización"""
        return self.physicaladdress_set.filter(is_active=True)

    def has_complete_info(self):
        """Verifica si la organización tiene información completa"""
        return (
            bool(self.name) and
            bool(self.org_type) and
            bool(self.industry) and
            bool(self.country) and
            bool(self.id_type and self.id_number)
        )

    @property
    def primary_contact(self):
        """Contacto principal de la organización"""
        return self.contacts.filter(is_primary=True, is_active=True).first()

    @property
    def primary_email(self):
        """Email principal de la organización"""
        primary = self.primary_contact
        return primary.email if primary and primary.email else None

    @property
    def primary_phone(self):
        """Teléfono principal de la organización"""
        primary = self.primary_contact
        return primary.phone if primary and primary.phone else None

    @property
    def primary_address(self):
        """Dirección principal de la organización"""
        return self.physicaladdress_set.filter(
            is_primary=True, is_active=True
        ).first()

    def get_semantic_profile(self):
        """Perfil semántico completo de la organización"""
        return {
            'industry': self.industry,
            'org_type': self.org_type,
            'country': self.country
        }

    def has_complete_profile(self):
        """Verifica si la organización tiene un perfil completo"""
        return (
            bool(self.name) and
            bool(self.industry) and
            bool(self.org_type) and
            bool(self.country) and
            bool(self.id_type and self.id_number)
        )


class PhysicalAddress(BaseUUIDModelWithActiveStatus):
    """Direcciones físicas asociables a personas u organizaciones"""
    
    # Propietario (solo uno de los dos debe estar definido)
    owner_person = models.ForeignKey(
        Person, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        verbose_name="Persona propietaria"
    )
    owner_org = models.ForeignKey(
        Organization, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        verbose_name="Organización propietaria"
    )
    
    # Información de la dirección
    address = models.CharField(max_length=255, verbose_name="Dirección")
    address_extra = models.CharField(max_length=100, blank=True, verbose_name="Información adicional")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    region_or_state = models.CharField(max_length=100, blank=True, verbose_name="Región o Estado")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name="País")
    zip_code = models.CharField(max_length=20, blank=True, verbose_name="Código postal")
    
    # Configuración
    is_primary = models.BooleanField(default=False, verbose_name="Dirección principal")
    use_for_billing = models.BooleanField(default=False, verbose_name="Usar para facturación")
    
    class Meta:
        verbose_name = "Dirección Física"
        verbose_name_plural = "Direcciones Físicas"
        constraints = [
            models.CheckConstraint(
                check=models.Q(owner_person__isnull=False) | models.Q(owner_org__isnull=False),
                name='address_must_have_owner'
            ),
            models.CheckConstraint(
                check=~(models.Q(owner_person__isnull=False) & models.Q(owner_org__isnull=False)),
                name='address_single_owner_only'
            )
        ]
        indexes = [
            models.Index(fields=['is_primary']),
            models.Index(fields=['use_for_billing']),
            models.Index(fields=['owner_person']),
            models.Index(fields=['owner_org']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        if self.owner_person:
            return f"Dirección de {self.owner_person} - {self.city}"
        elif self.owner_org:
            return f"Dirección de {self.owner_org} - {self.city}"
        return f"Dirección - {self.city}"

    @property
    def full_address(self):
        """Dirección completa formateada"""
        parts = [self.address]
        if self.address_extra:
            parts.append(self.address_extra)
        parts.append(self.city)
        if self.region_or_state:
            parts.append(self.region_or_state)
        if self.country:
            parts.append(str(self.country))
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)

    @property
    def owner(self):
        """Propietario de la dirección"""
        return self.owner_person or self.owner_org

    def clean(self):
        """Validación personalizada"""
        if not self.owner_person and not self.owner_org:
            raise ValidationError("La dirección debe tener un propietario (persona u organización).")
        
        if self.owner_person and self.owner_org:
            raise ValidationError("La dirección no puede pertenecer a una persona y organización al mismo tiempo.")
