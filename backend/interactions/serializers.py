from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Agent, Medium, Channel, ActionType, Action,
    TouchpointClass, Touchpoint, Interaction
)


class UserChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices de usuarios"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class MediumSerializer(serializers.ModelSerializer):
    channels_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Medium
        fields = ['id', 'name', 'code', 'description', 'is_active', 'channels_count']
    
    def get_channels_count(self, obj):
        return obj.channels.filter(is_active=True).count()


class MediumChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = Medium
        fields = ['id', 'name', 'code']


class ChannelSerializer(serializers.ModelSerializer):
    medium = MediumChoiceSerializer(read_only=True)
    medium_id = serializers.PrimaryKeyRelatedField(
        queryset=Medium.objects.filter(is_active=True),
        source='medium', write_only=True, required=False
    )
    interactions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'code', 'description', 'medium', 'medium_id',
            'is_active', 'interactions_count'
        ]
    
    def get_interactions_count(self, obj):
        return obj.interaction_set.filter(is_active=True).count()


class ChannelChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = Channel
        fields = ['id', 'name', 'code']


class ActionTypeSerializer(serializers.ModelSerializer):
    actions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ActionType
        fields = ['id', 'name', 'code', 'description', 'is_active', 'actions_count']
    
    def get_actions_count(self, obj):
        return obj.actions.filter(is_active=True).count()


class ActionTypeChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = ActionType
        fields = ['id', 'name', 'code']


class ActionSerializer(serializers.ModelSerializer):
    action_type = ActionTypeChoiceSerializer(read_only=True)
    action_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ActionType.objects.filter(is_active=True),
        source='action_type', write_only=True, required=False
    )
    interactions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Action
        fields = [
            'id', 'name', 'code', 'description', 'action_type', 'action_type_id',
            'is_active', 'interactions_count'
        ]
    
    def get_interactions_count(self, obj):
        return obj.interaction_set.filter(is_active=True).count()


class ActionChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = Action
        fields = ['id', 'name', 'code']


class AgentSerializer(serializers.ModelSerializer):
    # Campos calculados
    represents_display = serializers.SerializerMethodField()
    interactions_count = serializers.SerializerMethodField()
    
    # Campos de relaciones para lectura
    operated_by_display = serializers.SerializerMethodField()
    represents_person_display = serializers.SerializerMethodField()
    represents_organization_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'agent_type', 'name', 'identifier', 'metadata',
            'operated_by', 'represents_person', 'represents_organization',
            'operated_by_display', 'represents_person_display', 'represents_organization_display',
            'represents_display', 'interactions_count', 'is_active'
        ]
    
    def get_represents_display(self, obj):
        if obj.represents_person:
            return f"👤 {obj.represents_person.full_name}"
        elif obj.represents_organization:
            return f"🏢 {obj.represents_organization.name}"
        return None
    
    def get_interactions_count(self, obj):
        return obj.interactions.filter(is_active=True).count()
    
    def get_operated_by_display(self, obj):
        return obj.operated_by.full_name if obj.operated_by else None
    
    def get_represents_person_display(self, obj):
        return obj.represents_person.full_name if obj.represents_person else None
    
    def get_represents_organization_display(self, obj):
        return obj.represents_organization.name if obj.represents_organization else None


class AgentChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = ['id', 'name', 'agent_type', 'display_name']
    
    def get_display_name(self, obj):
        agent_icons = {
            'browser': '🌐',
            'human': '👤', 
            'system': '💻',
            'device': '📱',
            'bot': '🤖',
            'ai': '🧠',
            'other': '❓'
        }
        icon = agent_icons.get(obj.agent_type, '❓')
        return f"{icon} {obj.name}"


class TouchpointClassSerializer(serializers.ModelSerializer):
    touchpoints_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TouchpointClass
        fields = ['id', 'name', 'code', 'description', 'is_active', 'touchpoints_count']
    
    def get_touchpoints_count(self, obj):
        return obj.touchpoints.filter(is_active=True).count()


class TouchpointClassChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = TouchpointClass
        fields = ['id', 'name', 'code']


class TouchpointListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados"""
    touchpoint_class = TouchpointClassChoiceSerializer(read_only=True)
    assigned_staff_display = serializers.SerializerMethodField()
    product_display = serializers.SerializerMethodField()
    interactions_count = serializers.SerializerMethodField()
    semantic_tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Touchpoint
        fields = [
            'id', 'name', 'code', 'touchpoint_class', 'funnel_stage', 'content_type',
            'assigned_staff_display', 'product_display', 'interactions_count',
            'semantic_tags', 'is_active'
        ]
    
    def get_assigned_staff_display(self, obj):
        if obj.assigned_staff:
            return f"{obj.assigned_staff.first_name} {obj.assigned_staff.last_name}".strip() or obj.assigned_staff.username
        return None
    
    def get_product_display(self, obj):
        return obj.product.name if obj.product else None
    
    def get_interactions_count(self, obj):
        return obj.interaction_set.filter(is_active=True).count()
    
    def get_semantic_tags(self, obj):
        tags = []
        if obj.related_industries.exists():
            tags.append(f"🏭 {obj.related_industries.count()} industrias")
        if obj.related_functions.exists():
            tags.append(f"⚙️ {obj.related_functions.count()} funciones")
        if obj.related_skills.exists():
            tags.append(f"🎯 {obj.related_skills.count()} skills")
        return tags


class TouchpointDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles"""
    touchpoint_class = TouchpointClassChoiceSerializer(read_only=True)
    assigned_staff = UserChoiceSerializer(read_only=True)
    
    # Relaciones semánticas
    related_industries = serializers.StringRelatedField(many=True, read_only=True)
    related_functions = serializers.StringRelatedField(many=True, read_only=True)
    related_skills = serializers.StringRelatedField(many=True, read_only=True)
    related_descriptors = serializers.StringRelatedField(many=True, read_only=True)
    
    # Estadísticas
    interactions_count = serializers.SerializerMethodField()
    recent_interactions = serializers.SerializerMethodField()
    
    class Meta:
        model = Touchpoint
        fields = [
            'id', 'name', 'code', 'description', 'url', 'external_id',
            'touchpoint_class', 'funnel_stage', 'content_type', 'product', 'assigned_staff',
            'related_industries', 'related_functions', 'related_skills', 'related_descriptors',
            'interactions_count', 'recent_interactions', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_interactions_count(self, obj):
        return obj.interaction_set.filter(is_active=True).count()
    
    def get_recent_interactions(self, obj):
        return obj.interaction_set.filter(is_active=True).order_by('-occurred_at')[:5].count()


class TouchpointCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar touchpoints"""
    class Meta:
        model = Touchpoint
        fields = [
            'id', 'name', 'code', 'description', 'url', 'external_id',
            'touchpoint_class', 'funnel_stage', 'content_type', 'product', 'assigned_staff',
            'related_industries', 'related_functions', 'related_skills', 'related_descriptors',
            'is_active'
        ]


class TouchpointChoiceSerializer(serializers.ModelSerializer):
    """Serializer simple para choices"""
    class Meta:
        model = Touchpoint
        fields = ['id', 'name', 'code', 'funnel_stage', 'content_type']


class InteractionListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de interacciones"""
    entity_display = serializers.SerializerMethodField()
    agent_display = serializers.SerializerMethodField()
    touchpoint_display = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    channel_display = serializers.SerializerMethodField()
    duration_display = serializers.ReadOnlyField()
    geographic_location = serializers.ReadOnlyField()
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'occurred_at', 'entity_display', 'agent_display',
            'touchpoint_display', 'action_display', 'channel_display',
            'jtbd_stage', 'duration_display', 'geographic_location',
            'source', 'is_active'
        ]
    
    def get_entity_display(self, obj):
        entity = obj.resolved_person or obj.resolved_organization
        if not entity:
            return "Anónimo"
        
        if obj.resolved_person:
            return f"👤 {entity.full_name}"
        else:
            return f"🏢 {entity.name}"
    
    def get_agent_display(self, obj):
        if not obj.agent:
            return None
        
        agent_icons = {
            'browser': '🌐',
            'human': '👤', 
            'system': '💻',
            'device': '📱',
            'bot': '🤖',
            'ai': '🧠',
            'other': '❓'
        }
        
        icon = agent_icons.get(obj.agent.agent_type, '❓')
        return f"{icon} {obj.agent.name[:20]}..."
    
    def get_touchpoint_display(self, obj):
        return obj.touchpoint.name if obj.touchpoint else None
    
    def get_action_display(self, obj):
        return obj.action.name if obj.action else None
    
    def get_channel_display(self, obj):
        return obj.channel.name if obj.channel else None


class InteractionDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de interacciones"""
    # Relaciones expandidas
    person = serializers.StringRelatedField(read_only=True)
    organization = serializers.StringRelatedField(read_only=True)
    touchpoint = TouchpointChoiceSerializer(read_only=True)
    action = ActionChoiceSerializer(read_only=True)
    channel = ChannelChoiceSerializer(read_only=True)
    agent = AgentChoiceSerializer(read_only=True)
    representative = UserChoiceSerializer(read_only=True)
    
    # Propiedades calculadas
    resolved_person_display = serializers.SerializerMethodField()
    resolved_organization_display = serializers.SerializerMethodField()
    duration_display = serializers.ReadOnlyField()
    geographic_location = serializers.ReadOnlyField()
    has_duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'person', 'organization', 'touchpoint', 'action', 'channel',
            'agent', 'representative', 'product',
            'occurred_at', 'duration_seconds', 'session_id',
            'latitude', 'longitude', 'referrer_url', 'user_agent', 'ip_address',
            'source', 'jtbd_stage', 'payload', 'metadata',
            'resolved_person_display', 'resolved_organization_display',
            'duration_display', 'geographic_location', 'has_duration',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_resolved_person_display(self, obj):
        person = obj.resolved_person
        return person.full_name if person else None
    
    def get_resolved_organization_display(self, obj):
        org = obj.resolved_organization
        return org.name if org else None


class InteractionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar interacciones"""
    class Meta:
        model = Interaction
        fields = [
            'id', 'person', 'organization', 'touchpoint', 'action', 'channel',
            'agent', 'representative', 'product',
            'occurred_at', 'duration_seconds', 'session_id',
            'latitude', 'longitude', 'referrer_url', 'user_agent', 'ip_address',
            'source', 'jtbd_stage', 'payload', 'metadata', 'is_active'
        ]
    
    def validate(self, data):
        """Validación personalizada"""
        # Validar que al menos una entidad esté presente
        if not data.get('person') and not data.get('organization') and not data.get('agent'):
            raise serializers.ValidationError(
                "Debe especificar al menos una persona, organización o agente."
            )
        
        return data
