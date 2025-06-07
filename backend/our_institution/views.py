from rest_framework import viewsets
from .models import OurOrganization, Seat, Unit, Position, Team
from .serializers import (
    OurOrganizationSerializer,
    SeatSerializer,
    UnitSerializer,
    PositionSerializer,
    TeamSerializer,
)

class OurOrganizationViewSet(viewsets.ModelViewSet):
    queryset = OurOrganization.objects.all()
    serializer_class = OurOrganizationSerializer

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
