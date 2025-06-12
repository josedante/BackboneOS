from rest_framework import serializers
from .models import Campaign, CampaignTouchpoint

# Importaciones de otras apps
from world.serializers import (
    IndustryChoiceSerializer, FunctionChoiceSerializer, 
    MarketSegmentSerializer, WorldDescriptorSerializer, TagSerializer
)
from interactions.serializers import ChannelChoiceSerializer, TouchpointChoiceSerializer
from our_institution.serializers import DivisionSerializer, TeamSerializer


class CampaignListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de campañas"""
    division_name = serializers.CharField(source='division.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    # Propiedades calculadas
    is_active_now = serializers.ReadOnlyField()
    budget_display = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    
    # Contadores
    channels_count = serializers.SerializerMethodField()
    touchpoints_count = serializers.SerializerMethodField()
    subcampaigns_count = serializers.SerializerMethodField()
    segments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'budget_display', 'duration_display', 'content_type',
            'division_name', 'team_name', 'parent_name', 'is_active', 'is_active_now',
            'channels_count', 'touchpoints_count', 'subcampaigns_count', 
            'segments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_budget_display(self, obj):
        """Formatear presupuesto para display"""
        if obj.budget:
            return f"${obj.budget:,.2f}"
        return "Sin presupuesto"
    
    def get_duration_display(self, obj):
        """Calcular duración de la campaña"""
        if obj.start_date and obj.end_date:
            duration = (obj.end_date - obj.start_date).days
            return f"{duration} días"
        elif obj.start_date:
            return "Sin fecha fin"
        return "Sin fechas"
    
    def get_channels_count(self, obj):
        return obj.channels.filter(is_active=True).count()
    
    def get_touchpoints_count(self, obj):
        return obj.campaigntouchpoint_set.count()
    
    def get_subcampaigns_count(self, obj):
        return obj.subcampaigns.filter(is_active=True).count()
    
    def get_segments_count(self, obj):
        return obj.target_segments.count()


class CampaignDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de campaña"""
    # Relaciones anidadas
    division = DivisionSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    parent = serializers.SerializerMethodField()
    
    # Relaciones semánticas
    channels = ChannelChoiceSerializer(many=True, read_only=True)
    related_industries = IndustryChoiceSerializer(many=True, read_only=True)
    related_functions = FunctionChoiceSerializer(many=True, read_only=True)
    target_segments = MarketSegmentSerializer(many=True, read_only=True)
    descriptors = WorldDescriptorSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    # Subcampañas y touchpoints
    subcampaigns = serializers.SerializerMethodField()
    touchpoints = serializers.SerializerMethodField()
    
    # Propiedades calculadas
    is_active_now = serializers.ReadOnlyField()
    budget_display = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    campaign_status = serializers.SerializerMethodField()
    
    # IDs para escritura
    division_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    team_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    parent_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    channels_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    related_industries_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    related_functions_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    target_segments_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    descriptors_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    tags_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'budget_display', 'duration_display', 'campaign_status', 'content_type',
            'division', 'division_id', 'team', 'team_id', 'parent', 'parent_id',
            'channels', 'channels_ids', 'related_industries', 'related_industries_ids',
            'related_functions', 'related_functions_ids', 'target_segments', 
            'target_segments_ids', 'descriptors', 'descriptors_ids', 'tags', 'tags_ids',
            'subcampaigns', 'touchpoints', 'metadata', 'is_active', 'is_active_now',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_parent(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'name': obj.parent.name,
                'code': obj.parent.code
            }
        return None
    
    def get_subcampaigns(self, obj):
        subcampaigns = obj.subcampaigns.filter(is_active=True)[:10]
        return [{
            'id': sub.id,
            'name': sub.name,
            'code': sub.code,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'is_active': sub.is_active,
            'is_active_now': sub.is_active_now
        } for sub in subcampaigns]
    
    def get_touchpoints(self, obj):
        campaign_touchpoints = obj.campaigntouchpoint_set.select_related('touchpoint')[:10]
        return [{
            'id': ct.touchpoint.id,
            'name': ct.touchpoint.name,
            'weight': ct.weight,
            'priority': ct.priority,
            'expected_conversions': ct.expected_conversions,
            'budget_allocated': ct.budget_allocated
        } for ct in campaign_touchpoints]
    
    def get_budget_display(self, obj):
        if obj.budget:
            return f"${obj.budget:,.2f}"
        return "Sin presupuesto"
    
    def get_duration_display(self, obj):
        if obj.start_date and obj.end_date:
            duration = (obj.end_date - obj.start_date).days
            return f"{duration} días"
        elif obj.start_date:
            return "Sin fecha fin"
        return "Sin fechas"
    
    def get_campaign_status(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        
        if not obj.is_active:
            return "inactiva"
        elif obj.start_date and obj.start_date > today:
            return "programada"
        elif obj.is_active_now:
            return "activa"
        else:
            return "finalizada"
    
    def create(self, validated_data):
        # Extraer IDs de relaciones M2M
        channels_ids = validated_data.pop('channels_ids', [])
        related_industries_ids = validated_data.pop('related_industries_ids', [])
        related_functions_ids = validated_data.pop('related_functions_ids', [])
        target_segments_ids = validated_data.pop('target_segments_ids', [])
        descriptors_ids = validated_data.pop('descriptors_ids', [])
        tags_ids = validated_data.pop('tags_ids', [])
        
        # Asignar IDs de FK
        if 'division_id' in validated_data:
            validated_data['division_id'] = validated_data.pop('division_id')
        if 'team_id' in validated_data:
            validated_data['team_id'] = validated_data.pop('team_id')
        if 'parent_id' in validated_data:
            validated_data['parent_id'] = validated_data.pop('parent_id')
        
        # Crear campaña
        campaign = Campaign.objects.create(**validated_data)
        
        # Asignar relaciones M2M
        if channels_ids:
            campaign.channels.set(channels_ids)
        if related_industries_ids:
            campaign.related_industries.set(related_industries_ids)
        if related_functions_ids:
            campaign.related_functions.set(related_functions_ids)
        if target_segments_ids:
            campaign.target_segments.set(target_segments_ids)
        if descriptors_ids:
            campaign.descriptors.set(descriptors_ids)
        if tags_ids:
            campaign.tags.set(tags_ids)
        
        return campaign
    
    def update(self, instance, validated_data):
        # Extraer IDs de relaciones M2M
        channels_ids = validated_data.pop('channels_ids', None)
        related_industries_ids = validated_data.pop('related_industries_ids', None)
        related_functions_ids = validated_data.pop('related_functions_ids', None)
        target_segments_ids = validated_data.pop('target_segments_ids', None)
        descriptors_ids = validated_data.pop('descriptors_ids', None)
        tags_ids = validated_data.pop('tags_ids', None)
        
        # Asignar IDs de FK
        if 'division_id' in validated_data:
            instance.division_id = validated_data.pop('division_id')
        if 'team_id' in validated_data:
            instance.team_id = validated_data.pop('team_id')
        if 'parent_id' in validated_data:
            instance.parent_id = validated_data.pop('parent_id')
        
        # Actualizar campos regulares
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar relaciones M2M
        if channels_ids is not None:
            instance.channels.set(channels_ids)
        if related_industries_ids is not None:
            instance.related_industries.set(related_industries_ids)
        if related_functions_ids is not None:
            instance.related_functions.set(related_functions_ids)
        if target_segments_ids is not None:
            instance.target_segments.set(target_segments_ids)
        if descriptors_ids is not None:
            instance.descriptors.set(descriptors_ids)
        if tags_ids is not None:
            instance.tags.set(tags_ids)
        
        return instance


class CampaignCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear/actualizar campañas"""
    
    class Meta:
        model = Campaign
        fields = [
            'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'content_type', 'division', 'team', 'parent', 'channels',
            'related_industries', 'related_functions', 'target_segments',
            'descriptors', 'tags', 'metadata', 'is_active'
        ]
    
    def validate_code(self, value):
        """Validar que el código sea único"""
        if self.instance:
            # En actualización, excluir la instancia actual
            if Campaign.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe una campaña con este código.")
        else:
            # En creación, verificar que no exista
            if Campaign.objects.filter(code=value).exists():
                raise serializers.ValidationError("Ya existe una campaña con este código.")
        return value
    
    def validate(self, data):
        """Validaciones de negocio"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        budget = data.get('budget')
        if budget and budget < 0:
            raise serializers.ValidationError("El presupuesto no puede ser negativo.")
        
        return data


class CampaignChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices en formularios"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'code', 'content_type', 'display_name', 'is_active', 'is_active_now']
    
    def get_display_name(self, obj):
        status = "🟢" if obj.is_active_now else "🔴"
        return f"{status} {obj.name} ({obj.code})"


class CampaignTouchpointListSerializer(serializers.ModelSerializer):
    """Serializer para listados de relaciones campaña-touchpoint"""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    touchpoint_name = serializers.CharField(source='touchpoint.name', read_only=True)
    touchpoint_funnel_stage = serializers.CharField(source='touchpoint.funnel_stage', read_only=True)
    
    # Propiedades calculadas
    is_product_targeted = serializers.ReadOnlyField()
    is_cross_product = serializers.ReadOnlyField()
    
    class Meta:
        model = CampaignTouchpoint
        fields = [
            'id', 'campaign', 'campaign_name', 'touchpoint', 'touchpoint_name',
            'touchpoint_funnel_stage', 'weight', 'priority', 'expected_conversions',
            'budget_allocated', 'is_product_targeted', 'is_cross_product', 'metadata'
        ]


class CampaignTouchpointDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de relación campaña-touchpoint"""
    campaign = CampaignChoiceSerializer(read_only=True)
    touchpoint = TouchpointChoiceSerializer(read_only=True)
    
    # Propiedades calculadas
    is_product_targeted = serializers.ReadOnlyField()
    is_cross_product = serializers.ReadOnlyField()
    budget_allocated_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CampaignTouchpoint
        fields = [
            'id', 'campaign', 'touchpoint', 'weight', 'priority', 
            'expected_conversions', 'budget_allocated', 'budget_allocated_display',
            'is_product_targeted', 'is_cross_product', 'metadata'
        ]
    
    def get_budget_allocated_display(self, obj):
        if obj.budget_allocated:
            return f"${obj.budget_allocated:,.2f}"
        return "Sin presupuesto asignado"


class CampaignTouchpointCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar relaciones campaña-touchpoint"""
    
    class Meta:
        model = CampaignTouchpoint
        fields = [
            'campaign', 'touchpoint', 'weight', 'priority',
            'expected_conversions', 'budget_allocated', 'metadata'
        ]
    
    def validate(self, data):
        """Validaciones de negocio"""
        weight = data.get('weight')
        if weight and weight < 0:
            raise serializers.ValidationError("El peso no puede ser negativo.")
        
        expected_conversions = data.get('expected_conversions')
        if expected_conversions and expected_conversions < 0:
            raise serializers.ValidationError("Las conversiones esperadas no pueden ser negativas.")
        
        budget_allocated = data.get('budget_allocated')
        if budget_allocated and budget_allocated < 0:
            raise serializers.ValidationError("El presupuesto asignado no puede ser negativo.")
        
        return data


class CampaignAnalyticsSerializer(serializers.Serializer):
    """Serializer para analytics de campañas"""
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    scheduled_campaigns = serializers.IntegerField()
    finished_campaigns = serializers.IntegerField()
    
    by_division = serializers.ListField()
    by_team = serializers.ListField()
    by_channel = serializers.ListField()
    by_industry = serializers.ListField()
    by_segment = serializers.ListField()
    
    budget_statistics = serializers.DictField()
    duration_statistics = serializers.DictField()
    
    top_campaigns = serializers.ListField()
    recent_campaigns = serializers.ListField()
    upcoming_campaigns = serializers.ListField()


# Serializers para choice fields (útiles para formularios)
class CampaignsChoicesSerializer(serializers.Serializer):
    """Serializer para obtener choices de campaigns"""
    campaigns = CampaignChoiceSerializer(many=True)
    
    def to_representation(self, instance):
        return {
            'campaigns': CampaignChoiceSerializer(
                Campaign.objects.filter(is_active=True).order_by('name'), 
                many=True
            ).data
        }
