from rest_framework import serializers
from .models import Person, ContactDetail, IndividualProfile, Organization, PhysicalAddress
from world.serializers import (
    CountrySerializer, PersonalIDTypeSerializer, OrganizationalIDTypeSerializer,
    OrganizationTypeSerializer, IndustrySerializer, FunctionSerializer,
    SkillSerializer, AcademicDegreeSerializer
)


class ContactDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalles de contacto"""
    
    class Meta:
        model = ContactDetail
        fields = [
            'id', 'person', 'organization', 'email', 'phone', 'is_primary', 'verified', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactDetailListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de contactos"""
    
    class Meta:
        model = ContactDetail
        fields = ['id', 'email', 'phone', 'is_primary', 'verified']


class PersonListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de personas"""
    full_name = serializers.SerializerMethodField()
    primary_contact = serializers.SerializerMethodField()
    country_name = serializers.CharField(source='country_of_nationality.name', read_only=True)
    
    class Meta:
        model = Person
        fields = [
            'id', 'full_name', 'gender', 'birthday', 'primary_contact',
            'country_name', 'is_active', 'created_at'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.fathers_name}".strip() or "Sin nombre"
    
    def get_primary_contact(self, obj):
        primary = obj.contacts.filter(is_primary=True).first()
        if primary:
            return {
                'type': 'email' if primary.email else 'phone',
                'value': primary.email or primary.phone,
                'verified': primary.verified
            }
        return None


class PersonDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de persona"""
    full_name = serializers.SerializerMethodField()
    contacts = ContactDetailSerializer(many=True, read_only=True)
    country_of_nationality = CountrySerializer(read_only=True)
    id_type = PersonalIDTypeSerializer(read_only=True)
    profile = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    
    class Meta:
        model = Person
        fields = [
            'id', 'first_name', 'middle_name', 'fathers_name', 'mothers_name',
            'full_name', 'gender', 'birthday', 'marital_status', 
            'country_of_nationality', 'id_type', 'id_number', 'portrait',
            'contacts', 'profile', 'addresses',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.fathers_name}".strip() or "Sin nombre"
    
    def get_profile(self, obj):
        try:
            profile = obj.individualprofile
            return {
                'id': profile.id,
                'academic_degree': profile.academic_degree.name if profile.academic_degree else None,
                'industries_count': profile.industries.count(),
                'skills_count': profile.skills.count(),
                'functions_count': profile.functions.count(),
                'preferred_contact_medium': profile.preferred_contact_medium,
                'allows_marketing': profile.allows_marketing
            }
        except IndividualProfile.DoesNotExist:
            return None
    
    def get_addresses(self, obj):
        addresses = obj.physicaladdress_set.filter(is_active=True)
        return [{
            'id': addr.id,
            'address': addr.address,
            'city': addr.city,
            'country': addr.country.name if addr.country else None,
            'is_primary': addr.is_primary,
            'use_for_billing': addr.use_for_billing
        } for addr in addresses]


class PersonCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar personas"""
    
    class Meta:
        model = Person
        fields = [
            'first_name', 'middle_name', 'fathers_name', 'mothers_name',
            'gender', 'birthday', 'marital_status', 
            'country_of_nationality', 'id_type', 'id_number', 'portrait',
            'is_active'
        ]
    
    def validate(self, data):
        # Validar unicidad de documento si se proporciona
        if data.get('id_type') and data.get('id_number'):
            queryset = Person.objects.filter(
                id_type=data['id_type'],
                id_number=data['id_number']
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe una persona con este tipo y número de documento."
                )
        
        return data


class IndividualProfileSerializer(serializers.ModelSerializer):
    """Serializer completo para perfil individual"""
    person = PersonListSerializer(read_only=True)
    academic_degree = AcademicDegreeSerializer(read_only=True)
    industries = IndustrySerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    functions = FunctionSerializer(many=True, read_only=True)
    
    class Meta:
        model = IndividualProfile
        fields = [
            'id', 'person', 'academic_degree', 'industries', 'skills', 'functions',
            'accepts_privacy_policy', 'allows_marketing', 'preferred_contact_medium',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IndividualProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar perfil individual"""
    
    class Meta:
        model = IndividualProfile
        fields = [
            'person', 'academic_degree', 'industries', 'skills', 'functions',
            'accepts_privacy_policy', 'allows_marketing', 'preferred_contact_medium',
            'is_active'
        ]


class OrganizationListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de organizaciones"""
    org_type_name = serializers.CharField(source='org_type.name', read_only=True)
    industry_name = serializers.CharField(source='industry.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'legal_name', 'org_type_name', 'industry_name',
            'country_name', 'is_active', 'created_at'
        ]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de organización"""
    org_type = OrganizationTypeSerializer(read_only=True)
    industry = IndustrySerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    id_type = OrganizationalIDTypeSerializer(read_only=True)
    addresses = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'legal_name', 'org_type', 'industry',
            'id_type', 'id_number', 'main_address', 'country',
            'addresses', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_addresses(self, obj):
        addresses = obj.physicaladdress_set.filter(is_active=True)
        return [{
            'id': addr.id,
            'address': addr.address,
            'city': addr.city,
            'country': addr.country.name if addr.country else None,
            'is_primary': addr.is_primary,
            'use_for_billing': addr.use_for_billing
        } for addr in addresses]


class OrganizationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar organizaciones"""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'legal_name', 'org_type', 'industry',
            'id_type', 'id_number', 'main_address', 'country', 'is_active'
        ]
    
    def validate(self, data):
        # Validar unicidad de documento organizacional
        if data.get('id_type') and data.get('id_number'):
            queryset = Organization.objects.filter(
                id_type=data['id_type'],
                id_number=data['id_number']
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe una organización con este tipo y número de documento."
                )
        
        return data


class PhysicalAddressSerializer(serializers.ModelSerializer):
    """Serializer para direcciones físicas"""
    owner_person = PersonListSerializer(read_only=True)
    owner_org = OrganizationListSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    
    class Meta:
        model = PhysicalAddress
        fields = [
            'id', 'owner_person', 'owner_org', 'address', 'address_extra',
            'city', 'region_or_state', 'country', 'zip_code',
            'is_primary', 'use_for_billing', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhysicalAddressCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar direcciones"""
    
    class Meta:
        model = PhysicalAddress
        fields = [
            'owner_person', 'owner_org', 'address', 'address_extra',
            'city', 'region_or_state', 'country', 'zip_code',
            'is_primary', 'use_for_billing', 'is_active'
        ]
    
    def validate(self, data):
        # Validar que tenga al menos un propietario
        if not data.get('owner_person') and not data.get('owner_org'):
            raise serializers.ValidationError(
                "La dirección debe tener un propietario (persona u organización)."
            )
        
        # Validar que no tenga ambos propietarios
        if data.get('owner_person') and data.get('owner_org'):
            raise serializers.ValidationError(
                "La dirección no puede tener tanto persona como organización como propietario."
            )
        
        return data


# Serializers para choice fields (útiles para formularios)
class EntitiesChoicesSerializer(serializers.Serializer):
    """Serializer para obtener choices de entities"""
    gender_choices = serializers.SerializerMethodField()
    marital_status_choices = serializers.SerializerMethodField()
    contact_medium_choices = serializers.SerializerMethodField()
    
    def get_gender_choices(self, obj):
        return [{'value': choice[0], 'label': choice[1]} for choice in Person._meta.get_field('gender').choices]
    
    def get_marital_status_choices(self, obj):
        return [{'value': choice[0], 'label': choice[1]} for choice in Person._meta.get_field('marital_status').choices]
    
    def get_contact_medium_choices(self, obj):
        return [{'value': choice[0], 'label': choice[1]} for choice in IndividualProfile._meta.get_field('preferred_contact_medium').choices]
