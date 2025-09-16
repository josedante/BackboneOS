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
    Gender,
    MaritalStatus,
)
from backend.models import BaseUUIDModelWithActiveStatus


class Person(BaseUUIDModelWithActiveStatus):
    first_name = models.CharField(max_length=63, blank=True)
    middle_name = models.CharField(max_length=63, blank=True)
    last_name = models.CharField(max_length=63, blank=True)
    second_last_name = models.CharField(max_length=63, blank=True)

    gender = models.ForeignKey(Gender, null=True, blank=True, on_delete=models.SET_NULL)
    birthday = models.DateField(null=True, blank=True)
    marital_status = models.ForeignKey(MaritalStatus, null=True, blank=True, on_delete=models.SET_NULL)

    country_of_nationality = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    id_type = models.ForeignKey(PersonalIDType, null=True, blank=True, on_delete=models.SET_NULL)
    id_number = models.CharField(max_length=50, blank=True)

    portrait = models.ImageField(upload_to="public/profiles/", null=True, blank=True)

    class Meta:
        unique_together = ("id_type", "id_number")
        indexes = [
            # Índices básicos para búsquedas frecuentes
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['gender']),
            models.Index(fields=['marital_status']),
            models.Index(fields=['birthday']),
            models.Index(fields=['country_of_nationality']),
            models.Index(fields=['id_type']),
            models.Index(fields=['id_type', 'id_number']),
            models.Index(fields=['is_active']),
            # Índices compuestos para analytics y filtrado
            models.Index(fields=['is_active', 'country_of_nationality']),
            models.Index(fields=['is_active', 'gender']),
            models.Index(fields=['is_active', 'marital_status']),
            models.Index(fields=['is_active', 'birthday']),
            # Índices para búsquedas demográficas
            models.Index(fields=['gender', 'country_of_nationality']),
            models.Index(fields=['marital_status', 'gender']),
            # Índices para ordenamiento frecuente
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        """Nombre completo de la persona"""
        parts = [self.first_name, self.middle_name, self.last_name, self.second_last_name]
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

    def get_organizations(self):
        """Organizaciones donde esta persona tiene membresía activa"""
        # Esta relación se implementará cuando tengamos el modelo de membresías
        return []

    def get_recent_activities(self, limit=5):
        """Actividades recientes relacionadas con esta persona"""
        # Esta funcionalidad se implementará con el sistema de actividades
        return []

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
                bool(self.first_name and self.last_name) and
                bool(self.primary_contact) and
                bool(profile.academic_degree) and
                profile.industries.exists()
            )
        except IndividualProfile.DoesNotExist:
            return False


class ContactDetail(BaseUUIDModelWithActiveStatus):
    person = models.ForeignKey(Person, null=True, blank=True, related_name="contacts", on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', null=True, blank=True, related_name="contacts", on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_primary = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(person__isnull=False) | models.Q(organization__isnull=False),
                name='contact_must_have_owner'
            ),
            models.CheckConstraint(
                check=~(models.Q(person__isnull=False) & models.Q(organization__isnull=False)),
                name='contact_single_owner_only'
            )
        ]
        indexes = [
            # Índices principales para consultas frecuentes
            models.Index(fields=["person"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["is_primary"]),
            models.Index(fields=["verified"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
            # Índices compuestos para filtrado común
            models.Index(fields=["person", "is_primary"]),
            models.Index(fields=["organization", "is_primary"]),
            models.Index(fields=["person", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["is_active", "is_primary"]),
            models.Index(fields=["is_active", "verified"]),
            models.Index(fields=["is_primary", "verified"]),
            # Índices para búsquedas de contacto
            models.Index(fields=["email", "verified"]),
            models.Index(fields=["phone", "verified"]),
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["phone", "is_active"]),
            # Índices para analytics de contacto
            models.Index(fields=["person", "verified"]),
            models.Index(fields=["organization", "verified"]),
        ]

    def __str__(self):
        return self.email or self.phone or "Contacto"

    @property
    def owner(self):
        """Propietario del contacto"""
        return self.person or self.organization

    def clean(self):
        """Validación personalizada"""
        if not self.person and not self.organization:
            raise ValidationError("El contacto debe tener un propietario (persona u organización).")
        
        if self.person and self.organization:
            raise ValidationError("El contacto no puede pertenecer a una persona y organización al mismo tiempo.")


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

    class Meta:
        indexes = [
            # Índices para consultas semánticas frecuentes
            models.Index(fields=['person']),
            models.Index(fields=['academic_degree']),
            models.Index(fields=['preferred_contact_medium']),
            models.Index(fields=['accepts_privacy_policy']),
            models.Index(fields=['allows_marketing']),
            models.Index(fields=['is_active']),
            # Índices compuestos para filtrado común
            models.Index(fields=['is_active', 'academic_degree']),
            models.Index(fields=['is_active', 'allows_marketing']),
            models.Index(fields=['is_active', 'preferred_contact_medium']),
            models.Index(fields=['is_active', 'accepts_privacy_policy']),
            # Índices para analytics y segmentación
            models.Index(fields=['academic_degree', 'allows_marketing']),
            models.Index(fields=['preferred_contact_medium', 'allows_marketing']),
            models.Index(fields=['accepts_privacy_policy', 'allows_marketing']),
            # Índices para perfilado semántico
            models.Index(fields=['person', 'is_active']),
            models.Index(fields=['academic_degree', 'preferred_contact_medium']),
        ]


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
        indexes = [
            # Índices para búsquedas frecuentes
            models.Index(fields=['name']),
            models.Index(fields=['legal_name']),
            models.Index(fields=['org_type']),
            models.Index(fields=['industry']),
            models.Index(fields=['country']),
            models.Index(fields=['id_type']),
            models.Index(fields=['id_type', 'id_number']),
            # Índices para consultas de analytics
            models.Index(fields=['is_active', 'org_type']),
            models.Index(fields=['is_active', 'industry']),
            models.Index(fields=['is_active', 'country']),
            # Índices compuestos para filtrado y analytics
            models.Index(fields=['org_type', 'industry']),
            models.Index(fields=['country', 'industry']),
            models.Index(fields=['is_active']),
        ]

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
            # Índices principales para consultas frecuentes
            models.Index(fields=['is_primary']),
            models.Index(fields=['use_for_billing']),
            models.Index(fields=['owner_person']),
            models.Index(fields=['owner_org']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
            # Índices para búsquedas geográficas
            models.Index(fields=['country', 'city']),
            models.Index(fields=['region_or_state', 'city']),
            # Índices compuestos para filtrado común
            models.Index(fields=['is_active', 'is_primary']),
            models.Index(fields=['is_active', 'use_for_billing']),
            models.Index(fields=['owner_person', 'is_primary']),
            models.Index(fields=['owner_org', 'is_primary']),
            models.Index(fields=['owner_person', 'is_active']),
            models.Index(fields=['owner_org', 'is_active']),
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
