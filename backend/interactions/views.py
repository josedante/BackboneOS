"""
DRF viewsets for the interactions app.

Interaction and Touchpoint mutations delegate to ``services.py``; lookup catalog
viewsets (Medium, Channel, Action, etc.) still use serializer.save() until Phase 2b.
"""

from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings

# Función para determinar permisos dinámicamente
def get_permission_classes():
    """Devuelve las clases de permisos apropiadas según el modo DEBUG"""
    if settings.DEBUG:
        return [AllowAny]
    return [IsAuthenticated]

from .models import (
    Agent, Medium, Channel, ActionType, Action,
    TouchpointType, Touchpoint, Interaction
)
from .serializers import (
    MediumSerializer, MediumChoiceSerializer,
    ChannelSerializer, ChannelChoiceSerializer,
    ActionTypeSerializer, ActionTypeChoiceSerializer,
    ActionSerializer, ActionChoiceSerializer,
    AgentSerializer, AgentChoiceSerializer,
    TouchpointTypeSerializer, TouchpointTypeChoiceSerializer,
    TouchpointListSerializer, TouchpointDetailSerializer, TouchpointCreateUpdateSerializer, TouchpointChoiceSerializer,
    InteractionListSerializer, InteractionDetailSerializer, InteractionCreateUpdateSerializer
)
from .selectors import (
    get_interaction_analytics_summary,
    interactions_base_queryset,
    interactions_list_filter,
    paginated_touchpoint_interactions,
    touchpoints_base_queryset,
)
from .services import (
    create_interaction,
    create_touchpoint,
    delete_interaction,
    delete_touchpoint,
    interaction_write_payload_from_request,
    update_interaction,
    update_touchpoint,
)


class MediumViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar mediums"""
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = MediumChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar channels"""
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'source_type']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ChannelChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class ActionTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar action types"""
    queryset = ActionType.objects.all()
    serializer_class = ActionTypeSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ActionTypeChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class ActionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar actions"""
    queryset = Action.objects.select_related('action_type').all()
    serializer_class = ActionSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'action_type']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ActionChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class AgentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar agents"""
    queryset = Agent.objects.select_related(
        'operated_by', 'represents_person', 'represents_organization'
    ).all()
    serializer_class = AgentSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'agent_type']
    search_fields = ['name', 'identifier']
    ordering_fields = ['name', 'agent_type', 'created_at']
    ordering = ['agent_type', 'name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = AgentChoiceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Endpoint para obtener agentes agrupados por tipo"""
        agent_type = request.query_params.get('type')
        if agent_type:
            queryset = self.get_queryset().filter(agent_type=agent_type, is_active=True)
        else:
            queryset = self.get_queryset().filter(is_active=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics de agentes"""
        # Estadísticas básicas
        total_agents = self.get_queryset().filter(is_active=True).count()
        
        # Distribución por tipo de agente
        agents_by_type = self.get_queryset().filter(is_active=True).values('agent_type').annotate(
            count=Count('id'),
            interactions_count=Count('interactions', filter=Q(interactions__is_active=True))
        ).order_by('-count')
        
        # Agentes más activos (con más interacciones)
        top_agents = self.get_queryset().filter(is_active=True).annotate(
            interactions_count=Count('interactions', filter=Q(interactions__is_active=True))
        ).filter(interactions_count__gt=0).order_by('-interactions_count')[:10]
        
        # Serializar top agents
        top_agents_data = []
        for agent in top_agents:
            top_agents_data.append({
                'id': str(agent.id),
                'name': agent.name,
                'agent_type': agent.agent_type,
                'interactions_count': agent.interactions_count
            })
        
        return Response({
            'total_agents': total_agents,
            'agents_by_type': list(agents_by_type),
            'top_agents': top_agents_data,
            'summary': {
                'active_agents': total_agents,
                'total_interactions': sum(item['interactions_count'] for item in agents_by_type)
            }
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics de agentes"""
        from django.db.models import Count, Q
        
        # Estadísticas básicas
        total_agents = self.get_queryset().filter(is_active=True).count()
        
        # Distribución por tipo de agente
        agents_by_type = self.get_queryset().filter(is_active=True).values('agent_type').annotate(
            count=Count('id'),
            interactions_count=Count('interactions', filter=Q(interactions__is_active=True))
        ).order_by('-count')
        
        # Agentes más activos (con más interacciones)
        top_agents = self.get_queryset().filter(is_active=True).annotate(
            interactions_count=Count('interactions', filter=Q(interactions__is_active=True))
        ).filter(interactions_count__gt=0).order_by('-interactions_count')[:10]
        
        # Serializar top agents
        top_agents_data = []
        for agent in top_agents:
            top_agents_data.append({
                'id': str(agent.id),
                'name': agent.name,
                'agent_type': agent.agent_type,
                'interactions_count': agent.interactions_count
            })
        
        return Response({
            'total_agents': total_agents,
            'agents_by_type': list(agents_by_type),
            'top_agents': top_agents_data,
            'summary': {
                'active_agents': total_agents,
                'total_interactions': sum(item['interactions_count'] for item in agents_by_type)
            }
        })
    
class TouchpointTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar touchpoint types"""
    queryset = TouchpointType.objects.all()
    serializer_class = TouchpointTypeSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = TouchpointTypeChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class TouchpointViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar touchpoints"""
    queryset = touchpoints_base_queryset()
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'is_active', 'content_type', 'touchpoint_type', 'assigned_staff',
        'related_industries', 'related_functions', 'channel', 'medium'
    ]
    search_fields = ['name', 'code', 'description', 'url']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TouchpointListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TouchpointCreateUpdateSerializer
        else:
            return TouchpointDetailSerializer

    def perform_create(self, serializer):
        touchpoint = create_touchpoint(data=dict(serializer.validated_data))
        serializer.instance = touchpoint

    def perform_update(self, serializer):
        partial = self.action == 'partial_update'
        touchpoint = update_touchpoint(
            serializer.instance,
            data=dict(serializer.validated_data),
            partial=partial,
        )
        serializer.instance = touchpoint

    def perform_destroy(self, instance):
        delete_touchpoint(instance)
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Endpoint para obtener choices simples"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = TouchpointChoiceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_content_type(self, request):
        """Endpoint para obtener touchpoints por tipo de contenido"""
        content_type = request.query_params.get('content_type')
        if content_type:
            queryset = self.get_queryset().filter(content_type=content_type, is_active=True)
        else:
            queryset = self.get_queryset().filter(is_active=True)
        
        serializer = TouchpointListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Obtener interacciones de un touchpoint específico"""
        touchpoint = self.get_object()
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        page_data = paginated_touchpoint_interactions(
            touchpoint, page=page, page_size=page_size
        )
        serializer = InteractionListSerializer(page_data['results'], many=True)
        return Response({
            'count': page_data['count'],
            'results': serializer.data,
            'page': page_data['page'],
            'page_size': page_data['page_size'],
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics de touchpoints"""
        # Estadísticas básicas
        total_touchpoints = self.get_queryset().filter(is_active=True).count()
        
        # Distribución por tipo de touchpoint
        touchpoints_by_type = self.get_queryset().filter(is_active=True).select_related('touchpoint_type').values(
            'touchpoint_type__name'
        ).annotate(
            count=Count('id'),
            interactions_count=Count('interaction', filter=Q(interaction__is_active=True))
        ).order_by('-count')
        
        # Touchpoints más activos (con más interacciones)
        top_touchpoints = self.get_queryset().filter(is_active=True).annotate(
            interactions_count=Count('interaction', filter=Q(interaction__is_active=True))
        ).filter(interactions_count__gt=0).order_by('-interactions_count')[:10]
        
        # Serializar top touchpoints
        top_touchpoints_data = []
        for touchpoint in top_touchpoints:
            top_touchpoints_data.append({
                'id': str(touchpoint.id),
                'name': touchpoint.name,
                'touchpoint_type': touchpoint.touchpoint_type.name if touchpoint.touchpoint_type else None,
                'interactions_count': touchpoint.interactions_count
            })
        
        return Response({
            'total_touchpoints': total_touchpoints,
            'touchpoints_by_type': list(touchpoints_by_type),
            'top_touchpoints': top_touchpoints_data,
            'summary': {
                'active_touchpoints': total_touchpoints,
                'total_interactions': sum(item['interactions_count'] for item in touchpoints_by_type)
            }
        })


class InteractionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar interactions"""
    queryset = interactions_base_queryset()
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'is_active', 'touchpoint__channel', 'action', 'touchpoint',
        'agent__agent_type', 'representative'
    ]
    search_fields = [
        'person__first_name', 'person__last_name', 'organization__name', 'source',
        'user_agent', 'ip_address', 'session_id'
    ]
    ordering_fields = ['occurred_at', 'duration_seconds', 'created_at']
    ordering = ['-occurred_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InteractionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InteractionCreateUpdateSerializer
        else:
            return InteractionDetailSerializer
    
    def get_queryset(self):
        params = self.request.query_params
        return interactions_list_filter(
            super().get_queryset(),
            start_date=params.get('start_date'),
            end_date=params.get('end_date'),
            has_location=params.get('has_location'),
            has_duration=params.get('has_duration'),
        )

    def perform_create(self, serializer):
        payload = interaction_write_payload_from_request(
            self.request.data, serializer.validated_data
        )
        interaction = create_interaction(data=payload)
        serializer.instance = interaction

    def perform_update(self, serializer):
        payload = interaction_write_payload_from_request(
            self.request.data, serializer.validated_data
        )
        partial = self.action == 'partial_update'
        interaction = update_interaction(
            serializer.instance, data=payload, partial=partial
        )
        serializer.instance = interaction

    def perform_destroy(self, instance):
        delete_interaction(instance)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics básicos de interacciones"""
        return Response(get_interaction_analytics_summary())
    
    @action(detail=False, methods=['get'])
    def geographic_distribution(self, request):
        """Distribución geográfica de interacciones"""
        queryset = self.get_queryset().filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        locations = queryset.values('latitude', 'longitude').annotate(
            count=Count('id')
        ).order_by('-count')[:100]  # Top 100 ubicaciones
        
        return Response({
            'total_with_location': queryset.count(),
            'locations': list(locations)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Crear múltiples interacciones en lote"""
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Se esperaba una lista de interacciones'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InteractionCreateUpdateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            created = []
            for item in serializer.validated_data:
                created.append(create_interaction(data=dict(item)))
            return Response(
                {'created': len(created), 'message': 'Interacciones creadas exitosamente'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
