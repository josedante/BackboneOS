from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ContactDetail, IndividualProfile, Organization, Person, PhysicalAddress
from .selectors import (
    addresses_active_queryset,
    contacts_active_queryset,
    organizations_active_queryset,
    people_active_queryset,
    profiles_active_queryset,
)
from .serializers import (
    ContactDetailListSerializer,
    ContactDetailSerializer,
    EntitiesChoicesSerializer,
    IndividualProfileCreateUpdateSerializer,
    IndividualProfileSerializer,
    OrganizationCreateUpdateSerializer,
    OrganizationDetailSerializer,
    OrganizationListSerializer,
    PersonCreateUpdateSerializer,
    PersonDetailSerializer,
    PersonListSerializer,
    PhysicalAddressCreateUpdateSerializer,
    PhysicalAddressSerializer,
)
from .services import (
    create_individual_profile,
    create_organization,
    create_person,
    delete_organization,
    delete_person,
    organization_write_payload_from_validated,
    person_write_payload_from_validated,
    update_organization,
    update_person,
)


class PersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de personas naturales

    Proporciona operaciones CRUD completas con filtrado semántico,
    búsqueda avanzada y endpoints especializados.
    """

    queryset = Person.objects.none()  # overridden in get_queryset

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'gender',
        'marital_status',
        'country_of_nationality',
        'id_type',
        'is_active',
    ]
    search_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'second_last_name',
        'id_number',
        'contacts__email',
        'contacts__phone',
    ]
    ordering_fields = ['first_name', 'last_name', 'created_at', 'birthday']
    ordering = ['-created_at']

    def get_queryset(self):
        return people_active_queryset(action=self.action)

    def get_serializer_class(self):
        if self.action == 'list':
            return PersonListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return PersonCreateUpdateSerializer
        return PersonDetailSerializer

    def perform_create(self, serializer):
        payload = person_write_payload_from_validated(serializer.validated_data)
        person = create_person(data=payload)
        serializer.instance = person

    def perform_update(self, serializer):
        payload = person_write_payload_from_validated(serializer.validated_data)
        partial = self.action == 'partial_update'
        person = update_person(serializer.instance, data=payload, partial=partial)
        serializer.instance = person

    def perform_destroy(self, instance):
        delete_person(instance)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Obtener perfil semántico de la persona"""
        person = self.get_object()
        try:
            profile = person.individualprofile
            serializer = IndividualProfileSerializer(profile)
            return Response(serializer.data)
        except IndividualProfile.DoesNotExist:
            return Response(
                {'detail': 'La persona no tiene perfil individual creado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=['post'])
    def create_profile(self, request, pk=None):
        """Crear perfil individual para la persona"""
        person = self.get_object()
        try:
            profile = create_individual_profile(person, data=dict(request.data))
        except DjangoValidationError as exc:
            detail = exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        serializer = IndividualProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Obtener todos los contactos de la persona"""
        person = self.get_object()
        contacts = contacts_active_queryset().filter(person=person)
        serializer = ContactDetailSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Obtener todas las direcciones de la persona"""
        person = self.get_object()
        addresses = addresses_active_queryset().filter(owner_person=person)
        serializer = PhysicalAddressSerializer(addresses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_semantic(self, request):
        """Búsqueda semántica avanzada de personas"""
        queryset = self.get_queryset()

        industry = request.query_params.get('industry')
        skill = request.query_params.get('skill')
        function = request.query_params.get('function')
        academic_degree = request.query_params.get('academic_degree')

        if industry:
            queryset = queryset.filter(individualprofile__industries__id=industry)
        if skill:
            queryset = queryset.filter(individualprofile__skills__id=skill)
        if function:
            queryset = queryset.filter(individualprofile__functions__id=function)
        if academic_degree:
            queryset = queryset.filter(individualprofile__academic_degree__id=academic_degree)

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContactDetailViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de detalles de contacto"""

    queryset = ContactDetail.objects.none()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_primary', 'verified', 'person']
    search_fields = ['email', 'phone', 'person__first_name', 'person__last_name']
    ordering = ['-is_primary', '-created_at']

    def get_queryset(self):
        return contacts_active_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            return ContactDetailListSerializer
        return ContactDetailSerializer


class IndividualProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de perfiles individuales"""

    queryset = IndividualProfile.objects.none()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'academic_degree',
        'preferred_contact_medium',
        'accepts_privacy_policy',
        'allows_marketing',
    ]
    search_fields = [
        'person__first_name',
        'person__last_name',
        'industries__name',
        'skills__name',
        'functions__name',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        return profiles_active_queryset()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return IndividualProfileCreateUpdateSerializer
        return IndividualProfileSerializer

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analytics de perfiles individuales"""
        queryset = self.get_queryset()

        analytics = {
            'total_profiles': queryset.count(),
            'by_academic_degree': list(
                queryset.values('academic_degree__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
            'by_contact_medium': list(
                queryset.values('preferred_contact_medium')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'marketing_consent': {
                'allows': queryset.filter(allows_marketing=True).count(),
                'denies': queryset.filter(allows_marketing=False).count(),
            },
            'top_industries': list(
                queryset.values('industries__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
            'top_skills': list(
                queryset.values('skills__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
        }

        return Response(analytics)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de organizaciones"""

    queryset = Organization.objects.none()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['org_type', 'industry', 'country', 'id_type']
    search_fields = ['name', 'legal_name', 'id_number', 'main_address']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return organizations_active_queryset(action=self.action)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return OrganizationCreateUpdateSerializer
        return OrganizationDetailSerializer

    def perform_create(self, serializer):
        payload = organization_write_payload_from_validated(serializer.validated_data)
        org = create_organization(data=payload)
        serializer.instance = org

    def perform_update(self, serializer):
        payload = organization_write_payload_from_validated(serializer.validated_data)
        partial = self.action == 'partial_update'
        org = update_organization(serializer.instance, data=payload, partial=partial)
        serializer.instance = org

    def perform_destroy(self, instance):
        delete_organization(instance)

    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Obtener todas las direcciones de la organización"""
        organization = self.get_object()
        addresses = addresses_active_queryset().filter(owner_org=organization)
        serializer = PhysicalAddressSerializer(addresses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analytics de organizaciones"""
        queryset = self.get_queryset()

        analytics = {
            'total_organizations': queryset.count(),
            'by_type': list(
                queryset.values('org_type__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'by_industry': list(
                queryset.values('industry__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
            'by_country': list(
                queryset.values('country__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
        }

        return Response(analytics)


class PhysicalAddressViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de direcciones físicas"""

    queryset = PhysicalAddress.objects.none()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'owner_person',
        'owner_org',
        'country',
        'is_primary',
        'use_for_billing',
    ]
    search_fields = [
        'address',
        'address_extra',
        'city',
        'region_or_state',
        'owner_person__first_name',
        'owner_person__last_name',
        'owner_org__name',
    ]
    ordering = ['-is_primary', '-created_at']

    def get_queryset(self):
        return addresses_active_queryset()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PhysicalAddressCreateUpdateSerializer
        return PhysicalAddressSerializer


class EntitiesChoicesViewSet(viewsets.ViewSet):
    """ViewSet para obtener choices de campos de entities"""

    def list(self, request):
        """Obtener todos los choices disponibles"""
        serializer = EntitiesChoicesSerializer({})
        return Response(serializer.data)
