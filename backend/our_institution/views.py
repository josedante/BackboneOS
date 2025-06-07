from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import OurOrganization, Division, Seat, Unit, Position, Team
from .serializers import (
    OurOrganizationSerializer,
    DivisionSerializer,
    SeatSerializer,
    UnitSerializer,
    PositionSerializer,
    TeamSerializer,
)

class OurOrganizationViewSet(viewsets.ModelViewSet):
    queryset = OurOrganization.objects.all()
    serializer_class = OurOrganizationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'country', 'industry', 'org_type']
    search_fields = ['name', 'legal_name', 'tax_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.select_related('organization').all()
    serializer_class = DivisionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'organization']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.select_related('organization').all()
    serializer_class = SeatSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'category', 'organization']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('division', 'division__organization', 'parent').prefetch_related('children', 'positions').all()
    serializer_class = UnitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'division', 'parent', 'division__organization']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related('unit', 'unit__division', 'unit__division__organization').all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'unit', 'unit__division', 'unit__division__organization']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('division', 'division__organization').all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'division', 'division__organization']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
