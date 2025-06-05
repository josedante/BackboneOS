from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch

from .models import (
    Country, Industry, FunctionOrResponsibility, Skill,
    PersonalIDType, OrganizationType, OrganizationalIDType,
    DescriptorFamily, WorldDescriptor, MarketSegment, Tag,
    AcademicDegree, Position
)
from .serializers import (
    CountrySerializer, CountryListSerializer, CountryChoiceSerializer,
    IndustrySerializer, IndustryTreeSerializer, IndustryChoiceSerializer,
    FunctionSerializer, FunctionChoiceSerializer,
    SkillSerializer, SkillChoiceSerializer,
    PersonalIDTypeSerializer, OrganizationTypeSerializer, OrganizationalIDTypeSerializer,
    DescriptorFamilySerializer, WorldDescriptorSerializer,
    MarketSegmentSerializer, MarketSegmentDetailSerializer,
    TagSerializer,
    AcademicDegreeSerializer, AcademicDegreeChoiceSerializer,
    PositionSerializer, PositionChoiceSerializer
)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para países"""
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    lookup_field = 'iso3_code'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'official_name', 'iso2_code', 'iso3_code']
    ordering_fields = ['name', 'iso3_code']
    ordering = ['name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CountryListSerializer
        elif self.action == 'choices':
            return CountryChoiceSerializer
        return CountrySerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint simplificado para selecciones en formularios"""
        countries = self.get_queryset()
        serializer = self.get_serializer(countries, many=True)
        return Response(serializer.data)


class IndustryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para industrias"""
    serializer_class = IndustrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'code', 'description', 'ciiu_code']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Industry.objects.filter(is_active=True).select_related('parent').prefetch_related('sub_industries')
    
    def get_serializer_class(self):
        if self.action == 'tree':
            return IndustryTreeSerializer
        elif self.action == 'choices':
            return IndustryChoiceSerializer
        return IndustrySerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Devuelve las industrias en estructura jerárquica"""
        root_industries = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_industries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint simplificado para selecciones"""
        industries = self.get_queryset()
        serializer = self.get_serializer(industries, many=True)
        return Response(serializer.data)


class WorldChoicesViewSet(viewsets.ViewSet):
    """ViewSet para obtener todas las opciones de world en una sola llamada"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Retorna todas las opciones básicas del mundo"""
        data = {
            'countries': CountryChoiceSerializer(
                Country.objects.filter(is_active=True), many=True
            ).data,
            'industries': IndustryChoiceSerializer(
                Industry.objects.filter(is_active=True), many=True
            ).data,
            'functions': FunctionChoiceSerializer(
                FunctionOrResponsibility.objects.filter(is_active=True), many=True
            ).data,
            'skills': SkillChoiceSerializer(
                Skill.objects.filter(is_active=True), many=True
            ).data,
            'academic_degrees': AcademicDegreeChoiceSerializer(
                AcademicDegree.objects.filter(is_active=True), many=True
            ).data,
            'positions': PositionChoiceSerializer(
                Position.objects.filter(is_active=True), many=True
            ).data,
        }
        return Response(data)


class FunctionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para funciones y responsabilidades"""
    serializer_class = FunctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active', 'typical_level']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return FunctionOrResponsibility.objects.filter(is_active=True).select_related('parent').prefetch_related('sub_functions')
    
    def get_serializer_class(self):
        if self.action == 'choices':
            return FunctionChoiceSerializer
        return FunctionSerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint simplificado para selecciones"""
        functions = self.get_queryset()
        serializer = self.get_serializer(functions, many=True)
        return Response(serializer.data)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para habilidades"""
    serializer_class = SkillSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['skill_type', 'typical_level_required', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['skill_type', 'display_order', 'name', 'created_at']
    ordering = ['skill_type', 'display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Skill.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'choices':
            return SkillChoiceSerializer
        return SkillSerializer
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint simplificado para selecciones"""
        skills = self.get_queryset()
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)


class PersonalIDTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de documentos personales"""
    serializer_class = PersonalIDTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['country__name', 'display_order', 'name']
    ordering = ['country__name', 'display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return PersonalIDType.objects.filter(is_active=True).select_related('country')


class OrganizationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de organizaciones"""
    serializer_class = OrganizationTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ownership_type', 'typical_size', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return OrganizationType.objects.filter(is_active=True)


class OrganizationalIDTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de documentos organizacionales"""
    serializer_class = OrganizationalIDTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['country__name', 'display_order', 'name']
    ordering = ['country__name', 'display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return OrganizationalIDType.objects.filter(is_active=True).select_related('country')


class DescriptorFamilyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para familias de descriptores"""
    serializer_class = DescriptorFamilySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return DescriptorFamily.objects.filter(is_active=True).prefetch_related('descriptors')


class WorldDescriptorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para descriptores del mundo"""
    serializer_class = WorldDescriptorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['family', 'parent', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['family__name', 'name', 'created_at']
    ordering = ['family__name', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return WorldDescriptor.objects.filter(is_active=True).select_related('family', 'parent').prefetch_related('children')


class MarketSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para segmentos de mercado"""
    serializer_class = MarketSegmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['segment_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return MarketSegment.objects.filter(is_active=True).prefetch_related(
            'industries', 'functions', 'skills', 'descriptors'
        )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MarketSegmentDetailSerializer
        return MarketSegmentSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para etiquetas"""
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AcademicDegreeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para grados académicos"""
    queryset = AcademicDegree.objects.filter(is_active=True)
    serializer_class = AcademicDegreeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']

    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples de grados académicos"""
        queryset = self.get_queryset()
        serializer = AcademicDegreeChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para posiciones/cargos"""
    queryset = Position.objects.filter(is_active=True)
    serializer_class = PositionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples de posiciones"""
        queryset = self.get_queryset()
        serializer = PositionChoiceSerializer(queryset, many=True)
        return Response(serializer.data)
