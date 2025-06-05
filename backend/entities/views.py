from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404

from .models import Person, ContactDetail, IndividualProfile, Organization, PhysicalAddress
from .serializers import (
    PersonListSerializer, PersonDetailSerializer, PersonCreateUpdateSerializer,
    ContactDetailSerializer, ContactDetailListSerializer,
    IndividualProfileSerializer, IndividualProfileCreateUpdateSerializer,
    OrganizationListSerializer, OrganizationDetailSerializer, OrganizationCreateUpdateSerializer,
    PhysicalAddressSerializer, PhysicalAddressCreateUpdateSerializer,
    EntitiesChoicesSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de personas naturales
    
    Proporciona operaciones CRUD completas con filtrado semántico,
    búsqueda avanzada y endpoints especializados.
    """
    queryset = Person.objects.select_related(
        'country_of_nationality', 'id_type'
    ).prefetch_related(
        'contacts', 'individualprofile'
    ).filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'gender', 'marital_status', 'country_of_nationality',
        'id_type', 'is_active'
    ]
    search_fields = [
        'first_name', 'middle_name', 'fathers_name', 'mothers_name',
        'id_number', 'contacts__email', 'contacts__phone'
    ]
    ordering_fields = ['first_name', 'fathers_name', 'created_at', 'birthday']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PersonListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PersonCreateUpdateSerializer
        return PersonDetailSerializer
    
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
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def create_profile(self, request, pk=None):
        """Crear perfil individual para la persona"""
        person = self.get_object()
        
        # Verificar si ya tiene perfil
        if hasattr(person, 'individualprofile'):
            return Response(
                {'detail': 'La persona ya tiene un perfil individual.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el perfil
        data = request.data.copy()
        data['person'] = person.id
        
        serializer = IndividualProfileCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                IndividualProfileSerializer(profile).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Obtener todos los contactos de la persona"""
        person = self.get_object()
        contacts = person.contacts.filter(is_active=True)
        serializer = ContactDetailSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Obtener todas las direcciones de la persona"""
        person = self.get_object()
        addresses = person.physicaladdress_set.filter(is_active=True)
        serializer = PhysicalAddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_semantic(self, request):
        """Búsqueda semántica avanzada de personas"""
        queryset = self.get_queryset()
        
        # Filtros semánticos del perfil individual
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
        
        # Aplicar filtros estándar
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContactDetailViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de detalles de contacto"""
    queryset = ContactDetail.objects.select_related('person').filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_primary', 'verified', 'person']
    search_fields = ['email', 'phone', 'person__first_name', 'person__fathers_name']
    ordering = ['-is_primary', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContactDetailListSerializer
        return ContactDetailSerializer


class IndividualProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de perfiles individuales"""
    queryset = IndividualProfile.objects.select_related(
        'person', 'academic_degree'
    ).prefetch_related(
        'industries', 'skills', 'functions'
    ).filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'academic_degree', 'preferred_contact_medium', 
        'accepts_privacy_policy', 'allows_marketing'
    ]
    search_fields = [
        'person__first_name', 'person__fathers_name',
        'industries__name', 'skills__name', 'functions__name'
    ]
    ordering = ['-created_at']
    
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
                'denies': queryset.filter(allows_marketing=False).count()
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
            )
        }
        
        return Response(analytics)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de organizaciones"""
    queryset = Organization.objects.select_related(
        'org_type', 'industry', 'country', 'id_type'
    ).filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['org_type', 'industry', 'country', 'id_type']
    search_fields = ['name', 'legal_name', 'id_number', 'main_address']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrganizationCreateUpdateSerializer
        return OrganizationDetailSerializer
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Obtener todas las direcciones de la organización"""
        organization = self.get_object()
        addresses = organization.physicaladdress_set.filter(is_active=True)
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
            )
        }
        
        return Response(analytics)


class PhysicalAddressViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de direcciones físicas"""
    queryset = PhysicalAddress.objects.select_related(
        'owner_person', 'owner_org', 'country'
    ).filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'owner_person', 'owner_org', 'country', 
        'is_primary', 'use_for_billing'
    ]
    search_fields = [
        'address', 'address_extra', 'city', 'region_or_state',
        'owner_person__first_name', 'owner_person__fathers_name',
        'owner_org__name'
    ]
    ordering = ['-is_primary', '-created_at']
    
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
