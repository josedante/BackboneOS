from django.shortcuts import render
from django.db.models import Count, Q, Avg, Sum
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
    TouchpointClass, Touchpoint, Interaction
)
from .serializers import (
    MediumSerializer, MediumChoiceSerializer,
    ChannelSerializer, ChannelChoiceSerializer,
    ActionTypeSerializer, ActionTypeChoiceSerializer,
    ActionSerializer, ActionChoiceSerializer,
    AgentSerializer, AgentChoiceSerializer,
    TouchpointClassSerializer, TouchpointClassChoiceSerializer,
    TouchpointListSerializer, TouchpointDetailSerializer, TouchpointCreateUpdateSerializer, TouchpointChoiceSerializer,
    InteractionListSerializer, InteractionDetailSerializer, InteractionCreateUpdateSerializer
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
    queryset = Channel.objects.select_related('medium').all()
    serializer_class = ChannelSerializer
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'medium']
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
    
class TouchpointClassViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar touchpoint classes"""
    queryset = TouchpointClass.objects.all()
    serializer_class = TouchpointClassSerializer
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
        serializer = TouchpointClassChoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class TouchpointViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar touchpoints"""
    queryset = Touchpoint.objects.select_related(
        'touchpoint_class', 'assigned_staff', 'product', 'channel'
    ).prefetch_related(
        'related_industries', 'related_functions', 'related_skills', 'related_descriptors'
    ).all()
    permission_classes = get_permission_classes()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'is_active', 'content_type', 'touchpoint_class', 'assigned_staff',
        'related_industries', 'related_functions', 'channel'
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
        interactions = touchpoint.interaction_set.filter(is_active=True).order_by('-occurred_at')
        
        # Paginación manual simple
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_interactions = interactions[start:end]
        serializer = InteractionListSerializer(paginated_interactions, many=True)
        
        return Response({
            'count': interactions.count(),
            'results': serializer.data,
            'page': page,
            'page_size': page_size
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics de touchpoints"""
        # Estadísticas básicas
        total_touchpoints = self.get_queryset().filter(is_active=True).count()
        
        # Distribución por clase de touchpoint
        touchpoints_by_class = self.get_queryset().filter(is_active=True).select_related('touchpoint_class').values(
            'touchpoint_class__name'
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
                'touchpoint_class': touchpoint.touchpoint_class.name if touchpoint.touchpoint_class else None,
                'interactions_count': touchpoint.interactions_count
            })
        
        return Response({
            'total_touchpoints': total_touchpoints,
            'touchpoints_by_stage': list(touchpoints_by_stage),
            'touchpoints_by_class': list(touchpoints_by_class),
            'top_touchpoints': top_touchpoints_data,
            'summary': {
                'active_touchpoints': total_touchpoints,
                'total_interactions': sum(item['interactions_count'] for item in touchpoints_by_stage)
            }
        })


class InteractionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar interactions"""
    queryset = Interaction.objects.select_related(
        'person', 'organization', 'touchpoint', 'action',
        'agent', 'representative', 'product'
    ).select_related('touchpoint__channel').all()
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
        queryset = super().get_queryset()
        
        # Filtro por fecha
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(occurred_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(occurred_at__lte=end_date)
        
        # Filtro por geolocalización
        has_location = self.request.query_params.get('has_location')
        if has_location == 'true':
            queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False)
        elif has_location == 'false':
            queryset = queryset.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
        
        # Filtro por duración
        has_duration = self.request.query_params.get('has_duration')
        if has_duration == 'true':
            queryset = queryset.filter(duration_seconds__gt=0)
        elif has_duration == 'false':
            queryset = queryset.filter(Q(duration_seconds__isnull=True) | Q(duration_seconds=0))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Endpoint para analytics básicos de interacciones"""
        queryset = self.get_queryset().filter(is_active=True)
        
        # Métricas básicas
        total_interactions = queryset.count()
        unique_sessions = queryset.exclude(session_id='').values('session_id').distinct().count()
        
        # Interacciones por canal (through touchpoint)
        by_channel = queryset.filter(touchpoint__channel__isnull=False).values('touchpoint__channel__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Interacciones por acción
        by_action = queryset.values('action__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Duración promedio
        avg_duration = queryset.filter(duration_seconds__gt=0).aggregate(
            avg_duration=Avg('duration_seconds')
        )
        
        return Response({
            'total_interactions': total_interactions,
            'unique_sessions': unique_sessions,
            'avg_duration_seconds': avg_duration['avg_duration'],
            'by_channel': list(by_channel),
            'by_action': list(by_action),
        })
    
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
            interactions = serializer.save()
            return Response(
                {'created': len(interactions), 'message': 'Interacciones creadas exitosamente'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
