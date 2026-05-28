from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Campaign, CampaignTouchpoint
from .services import (
    validate_campaign_code,
    validate_campaign_dates,
    validate_campaign_touchpoint_data,
)

# Importaciones de otras apps
from world.serializers import (
    IndustryChoiceSerializer, FunctionChoiceSerializer, 
    MarketSegmentSerializer, WorldDescriptorSerializer, TagSerializer
)
from interactions.serializers import ChannelChoiceSerializer, TouchpointChoiceSerializer
from our_institution.serializers import DivisionSerializer, TeamSerializer
from products.serializers import ProductListSerializer, ProductCategorySerializer
from offers.serializers import ProductOfferingChoiceSerializer


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
    
    # NEW: Product integration counters
    products_count = serializers.SerializerMethodField()
    categories_count = serializers.SerializerMethodField()
    offers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'budget_display', 'duration_display', 'content_type', 'funnel_stage',
            'division_name', 'team_name', 'parent_name', 'is_active', 'is_active_now',
            'channels_count', 'touchpoints_count', 'subcampaigns_count', 
            'segments_count', 'products_count', 'categories_count', 'offers_count',
            'created_at', 'updated_at'
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
    
    def get_products_count(self, obj):
        return obj.target_products.count()
    
    def get_categories_count(self, obj):
        return obj.target_categories.count()
    
    def get_offers_count(self, obj):
        return obj.target_offers.count()


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
    
    # NEW: Product integration
    target_products = ProductListSerializer(many=True, read_only=True)
    target_categories = ProductCategorySerializer(many=True, read_only=True)
    target_offers = ProductOfferingChoiceSerializer(many=True, read_only=True)
    
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
    
    # NEW: Product integration write-only fields
    target_products_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    target_categories_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    target_offers_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'budget_display', 'duration_display', 'campaign_status', 'content_type', 'funnel_stage',
            'division', 'division_id', 'team', 'team_id', 'parent', 'parent_id',
            'channels', 'channels_ids', 'related_industries', 'related_industries_ids',
            'related_functions', 'related_functions_ids', 'target_segments', 
            'target_segments_ids', 'descriptors', 'descriptors_ids', 'tags', 'tags_ids',
            'target_products', 'target_products_ids', 'target_categories', 'target_categories_ids',
            'target_offers', 'target_offers_ids', 'subcampaigns', 'touchpoints', 
            'metadata', 'is_active', 'is_active_now', 'created_at', 'updated_at'
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
    
class CampaignCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear/actualizar campañas"""
    
    class Meta:
        model = Campaign
        fields = [
            'name', 'code', 'description', 'start_date', 'end_date',
            'budget', 'content_type', 'funnel_stage', 'division', 'team', 'parent', 'channels',
            'related_industries', 'related_functions', 'target_segments',
            'descriptors', 'tags', 'target_products', 'target_categories', 'target_offers',
            'metadata', 'is_active'
        ]
    
    def validate_code(self, value):
        """Unique code — delegates to ``services.validate_campaign_code``."""
        exclude = self.instance.pk if self.instance else None
        try:
            validate_campaign_code(value, exclude_pk=exclude)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict.get('code', exc.messages))
        return value

    def validate(self, data):
        """Business rules — delegates to ``services.validate_campaign_dates``."""
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        budget = data.get('budget', getattr(self.instance, 'budget', None))
        try:
            validate_campaign_dates(start, end, budget=budget)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return data


class CampaignChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices en formularios"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'code', 'content_type', 'funnel_stage', 'display_name', 'is_active', 'is_active_now']
    
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
        """Delegates to ``services.validate_campaign_touchpoint_data``."""
        merged = {}
        if self.instance:
            merged = {
                'weight': self.instance.weight,
                'expected_conversions': self.instance.expected_conversions,
                'budget_allocated': self.instance.budget_allocated,
            }
        merged.update(data)
        try:
            validate_campaign_touchpoint_data(merged)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
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
