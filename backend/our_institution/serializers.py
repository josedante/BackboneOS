from rest_framework import serializers
from .models import OurOrganization, Division, Seat, Unit, Position, Team

class OurOrganizationSerializer(serializers.ModelSerializer):
    divisions_count = serializers.SerializerMethodField()
    seats_count = serializers.SerializerMethodField()
    units_count = serializers.SerializerMethodField()
    teams_count = serializers.SerializerMethodField()
    positions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = OurOrganization
        fields = ['id', 'name', 'legal_name', 'org_type', 'industry', 'tax_id', 
                 'country', 'website', 'logo', 'email', 'phone', 'address', 
                 'is_active', 'created_at', 'updated_at', 'divisions_count', 
                 'seats_count', 'units_count', 'teams_count', 'positions_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_divisions_count(self, obj):
        return obj.divisions.filter(is_active=True).count()
    
    def get_seats_count(self, obj):
        return obj.seats.filter(is_active=True).count()
        
    def get_units_count(self, obj):
        # Units están relacionados a través de divisions
        return sum(division.units.filter(is_active=True).count() 
                  for division in obj.divisions.filter(is_active=True))
        
    def get_teams_count(self, obj):
        # Teams están relacionados a través de divisions
        return sum(division.teams.filter(is_active=True).count() 
                  for division in obj.divisions.filter(is_active=True))
        
    def get_positions_count(self, obj):
        # Positions están relacionados a través de divisions->units
        return sum(unit.positions.filter(is_active=True).count() 
                  for division in obj.divisions.filter(is_active=True)
                  for unit in division.units.filter(is_active=True))

class DivisionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    units_count = serializers.ReadOnlyField()
    teams_count = serializers.ReadOnlyField()
    positions_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Division
        fields = ['id', 'name', 'code', 'description', 'organization', 
                 'organization_name', 'units_count', 'teams_count', 'positions_count',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SeatSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Seat
        fields = ['id', 'name', 'code', 'category', 'category_display', 'organization', 
                 'organization_name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UnitSerializer(serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.name', read_only=True)
    organization_name = serializers.CharField(source='division.organization.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    positions_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code', 'description', 'division', 'division_name',
                 'organization_name', 'parent', 'parent_name', 'children_count', 
                 'positions_count', 'full_path', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.filter(is_active=True).count()

class PositionSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_full_path = serializers.CharField(source='unit.full_path', read_only=True)
    division_name = serializers.CharField(source='unit.division.name', read_only=True)
    organization_name = serializers.CharField(source='unit.division.organization.name', read_only=True)
    
    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'description', 'unit', 'unit_name', 
                 'unit_full_path', 'division_name', 'organization_name',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TeamSerializer(serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.name', read_only=True)
    organization_name = serializers.CharField(source='division.organization.name', read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'code', 'description', 'division', 'division_name',
                 'organization_name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
