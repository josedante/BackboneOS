from django.shortcuts import render
from django.db.models import Q, Count, Avg, Sum, Min, Max, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ValidationError
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Campaign, CampaignTouchpoint
from .serializers import (
    CampaignListSerializer, CampaignDetailSerializer, CampaignCreateUpdateSerializer,
    CampaignChoiceSerializer, CampaignTouchpointListSerializer, CampaignTouchpointDetailSerializer,
    CampaignTouchpointCreateUpdateSerializer, CampaignAnalyticsSerializer, CampaignsChoicesSerializer
)


class CampaignFilter(django_filters.FilterSet):
    """Filtros personalizados para campañas"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtros de fecha
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Filtros de presupuesto
    budget_min = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    
    # Filtros por estado
    is_active_now = django_filters.BooleanFilter(method='filter_active_now')
    has_budget = django_filters.BooleanFilter(method='filter_has_budget')
    has_end_date = django_filters.BooleanFilter(method='filter_has_end_date')
    
    # Filtros por relaciones
    has_subcampaigns = django_filters.BooleanFilter(method='filter_has_subcampaigns')
    has_touchpoints = django_filters.BooleanFilter(method='filter_has_touchpoints')
    
    class Meta:
        model = Campaign
        fields = [
            'is_active', 'content_type', 'funnel_stage', 'division', 'team', 'parent',
            'channels', 'related_industries', 'related_functions', 'target_segments'
        ]
    
    def filter_active_now(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:
            return queryset.filter(
                is_active=True,
                start_date__lte=today
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
        else:
            return queryset.exclude(
                is_active=True,
                start_date__lte=today
            ).exclude(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
    
    def filter_has_budget(self, queryset, name, value):
        if value:
            return queryset.filter(budget__gt=0)
        else:
            return queryset.filter(Q(budget__isnull=True) | Q(budget=0))
    
    def filter_has_end_date(self, queryset, name, value):
        if value:
            return queryset.filter(end_date__isnull=False)
        else:
            return queryset.filter(end_date__isnull=True)
    
    def filter_has_subcampaigns(self, queryset, name, value):
        if value:
            return queryset.filter(subcampaigns__is_active=True).distinct()
        else:
            return queryset.filter(subcampaigns__isnull=True)
    
    def filter_has_touchpoints(self, queryset, name, value):
        if value:
            return queryset.filter(campaigntouchpoint__isnull=False).distinct()
        else:
            return queryset.filter(campaigntouchpoint__isnull=True)


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de campañas"""
    queryset = Campaign.objects.select_related(
        'division', 'team', 'parent'
    ).prefetch_related(
        'channels', 'related_industries', 'related_functions', 
        'target_segments', 'descriptors', 'tags', 'subcampaigns'
    ).filter(is_active=True)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CampaignFilter
    
    search_fields = [
        'name', 'code', 'description', 'division__name', 'team__name',
        'related_industries__name', 'target_segments__name'
    ]
    
    ordering_fields = [
        'name', 'code', 'start_date', 'end_date', 'budget',
        'created_at', 'updated_at'
    ]
    ordering = ['-start_date', 'name']
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Serializer contextual según acción"""
        if self.action == 'list':
            return CampaignListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CampaignCreateUpdateSerializer
        elif self.action == 'choices':
            return CampaignChoiceSerializer
        else:
            return CampaignDetailSerializer
    
    def get_queryset(self):
        """Queryset con optimizaciones según acción"""
        queryset = super().get_queryset()
        
        if self.action == 'list':
            return queryset.select_related(
                'division', 'team', 'parent'
            ).prefetch_related(
                'channels', 'target_segments', 'subcampaigns'
            )
        elif self.action == 'retrieve':
            return queryset.select_related(
                'division', 'team', 'parent'
            ).prefetch_related(
                'channels', 'related_industries', 'related_functions',
                'target_segments', 'descriptors', 'tags', 'subcampaigns',
                'campaigntouchpoint_set__touchpoint'
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Choices para formularios"""
        choices = CampaignsChoicesSerializer({}).data
        return Response(choices)
    
    @action(detail=False, methods=['get'])
    def active_now(self, request):
        """Campañas actualmente activas"""
        today = timezone.now().date()
        active_campaigns = self.get_queryset().filter(
            is_active=True,
            start_date__lte=today
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )
        
        serializer = CampaignListSerializer(active_campaigns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Campañas programadas (futuras)"""
        today = timezone.now().date()
        scheduled_campaigns = self.get_queryset().filter(
            is_active=True,
            start_date__gt=today
        )
        
        serializer = CampaignListSerializer(scheduled_campaigns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def finished(self, request):
        """Campañas finalizadas"""
        today = timezone.now().date()
        finished_campaigns = self.get_queryset().filter(
            end_date__lt=today
        )
        
        serializer = CampaignListSerializer(finished_campaigns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_division(self, request):
        """Campañas agrupadas por división"""
        division_id = request.query_params.get('division_id')
        if division_id:
            campaigns = self.get_queryset().filter(division_id=division_id)
        else:
            campaigns = self.get_queryset().select_related('division').exclude(division__isnull=True)
        
        # Agrupar por división
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for campaign in campaigns:
            division_name = campaign.division.name if campaign.division else 'Sin división'
            grouped[division_name].append(CampaignListSerializer(campaign).data)
        
        return Response(dict(grouped))
    
    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """Campañas agrupadas por equipo"""
        team_id = request.query_params.get('team_id')
        if team_id:
            campaigns = self.get_queryset().filter(team_id=team_id)
        else:
            campaigns = self.get_queryset().select_related('team').exclude(team__isnull=True)
        
        # Agrupar por equipo
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for campaign in campaigns:
            team_name = campaign.team.name if campaign.team else 'Sin equipo'
            grouped[team_name].append(CampaignListSerializer(campaign).data)
        
        return Response(dict(grouped))
    
    @action(detail=True, methods=['get'])
    def subcampaigns(self, request, pk=None):
        """Obtener subcampañas de una campaña"""
        campaign = self.get_object()
        subcampaigns = campaign.subcampaigns.filter(is_active=True)
        serializer = CampaignListSerializer(subcampaigns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def touchpoints(self, request, pk=None):
        """Obtener touchpoints de una campaña"""
        campaign = self.get_object()
        campaign_touchpoints = campaign.campaigntouchpoint_set.select_related('touchpoint')
        serializer = CampaignTouchpointListSerializer(campaign_touchpoints, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar una campaña"""
        original_campaign = self.get_object()
        
        # Crear nueva campaña
        new_campaign_data = {
            'name': f"{original_campaign.name} (Copia)",
            'code': f"{original_campaign.code}_copy_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            'description': original_campaign.description,
            'start_date': original_campaign.start_date,
            'end_date': original_campaign.end_date,
            'budget': original_campaign.budget,
            'division': original_campaign.division,
            'team': original_campaign.team,
            'metadata': original_campaign.metadata,
            'is_active': False  # Las copias inician inactivas
        }
        
        new_campaign = Campaign.objects.create(**new_campaign_data)
        
        # Copiar relaciones M2M
        new_campaign.channels.set(original_campaign.channels.all())
        new_campaign.related_industries.set(original_campaign.related_industries.all())
        new_campaign.related_functions.set(original_campaign.related_functions.all())
        new_campaign.target_segments.set(original_campaign.target_segments.all())
        new_campaign.descriptors.set(original_campaign.descriptors.all())
        new_campaign.tags.set(original_campaign.tags.all())
        
        # Copiar touchpoints
        for ct in original_campaign.campaigntouchpoint_set.all():
            CampaignTouchpoint.objects.create(
                campaign=new_campaign,
                touchpoint=ct.touchpoint,
                weight=ct.weight,
                priority=ct.priority,
                expected_conversions=ct.expected_conversions,
                budget_allocated=ct.budget_allocated,
                metadata=ct.metadata
            )
        
        serializer = CampaignDetailSerializer(new_campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def analytics(self, request):
        """Analytics completo de campañas"""
        queryset = Campaign.objects.all()  # Incluir inactivas para analytics
        today = timezone.now().date()
        
        # Métricas básicas
        total_campaigns = queryset.count()
        active_campaigns = queryset.filter(
            is_active=True,
            start_date__lte=today
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ).count()
        
        scheduled_campaigns = queryset.filter(
            is_active=True,
            start_date__gt=today
        ).count()
        
        finished_campaigns = queryset.filter(
            end_date__lt=today
        ).count()
        
        # Análisis por división
        by_division = queryset.values(
            'division__name'
        ).annotate(
            count=Count('id'),
            total_budget=Sum('budget'),
            avg_budget=Avg('budget')
        ).order_by('-count')
        
        # Análisis por equipo
        by_team = queryset.values(
            'team__name'
        ).annotate(
            count=Count('id'),
            total_budget=Sum('budget')
        ).order_by('-count')
        
        # Análisis por canal
        by_channel = queryset.values(
            'channels__name'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')
        
        # Análisis por industria
        by_industry = queryset.values(
            'related_industries__name'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')
        
        # Análisis por segmento
        by_segment = queryset.values(
            'target_segments__name'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')
        
        # Estadísticas de presupuesto
        budget_stats = queryset.filter(budget__gt=0).aggregate(
            total_budget=Sum('budget'),
            avg_budget=Avg('budget'),
            min_budget=Min('budget'),
            max_budget=Max('budget')
        )
        
        # Estadísticas de duración
        campaigns_with_dates = queryset.filter(
            start_date__isnull=False,
            end_date__isnull=False
        )
        
        duration_stats = {
            'total_campaigns_with_duration': campaigns_with_dates.count(),
            'avg_duration_days': 0,
            'min_duration_days': 0,
            'max_duration_days': 0
        }
        
        if campaigns_with_dates.exists():
            durations = [(c.end_date - c.start_date).days for c in campaigns_with_dates]
            duration_stats.update({
                'avg_duration_days': sum(durations) / len(durations),
                'min_duration_days': min(durations),
                'max_duration_days': max(durations)
            })
        
        # Top campañas por presupuesto
        top_campaigns = queryset.filter(
            budget__gt=0
        ).order_by('-budget')[:5].values(
            'id', 'name', 'code', 'budget', 'start_date', 'end_date'
        )
        
        # Campañas recientes
        recent_campaigns = queryset.filter(
            is_active=True
        ).order_by('-created_at')[:5].values(
            'id', 'name', 'code', 'start_date', 'created_at'
        )
        
        # Próximas campañas
        upcoming_campaigns = queryset.filter(
            is_active=True,
            start_date__gt=today
        ).order_by('start_date')[:5].values(
            'id', 'name', 'code', 'start_date'
        )
        
        analytics_data = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'scheduled_campaigns': scheduled_campaigns,
            'finished_campaigns': finished_campaigns,
            'by_division': list(by_division),
            'by_team': list(by_team),
            'by_channel': list(by_channel),
            'by_industry': list(by_industry),
            'by_segment': list(by_segment),
            'budget_statistics': budget_stats,
            'duration_statistics': duration_stats,
            'top_campaigns': list(top_campaigns),
            'recent_campaigns': list(recent_campaigns),
            'upcoming_campaigns': list(upcoming_campaigns)
        }
        
        serializer = CampaignAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class CampaignTouchpointFilter(django_filters.FilterSet):
    """Filtros para relaciones campaña-touchpoint"""
    campaign_name = django_filters.CharFilter(field_name='campaign__name', lookup_expr='icontains')
    touchpoint_name = django_filters.CharFilter(field_name='touchpoint__name', lookup_expr='icontains')
    
    # Filtros por peso y prioridad
    weight_min = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    weight_max = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    priority_min = django_filters.NumberFilter(field_name='priority', lookup_expr='gte')
    priority_max = django_filters.NumberFilter(field_name='priority', lookup_expr='lte')
    
    # Filtros por presupuesto
    budget_allocated_min = django_filters.NumberFilter(field_name='budget_allocated', lookup_expr='gte')
    budget_allocated_max = django_filters.NumberFilter(field_name='budget_allocated', lookup_expr='lte')
    has_budget_allocated = django_filters.BooleanFilter(method='filter_has_budget_allocated')
    
    class Meta:
        model = CampaignTouchpoint
        fields = ['campaign', 'touchpoint']
    
    def filter_has_budget_allocated(self, queryset, name, value):
        if value:
            return queryset.filter(budget_allocated__gt=0)
        else:
            return queryset.filter(Q(budget_allocated__isnull=True) | Q(budget_allocated=0))


class CampaignTouchpointViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de relaciones campaña-touchpoint"""
    queryset = CampaignTouchpoint.objects.select_related(
        'campaign', 'touchpoint'
    ).all()
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CampaignTouchpointFilter
    
    search_fields = [
        'campaign__name', 'campaign__code', 'touchpoint__name', 'touchpoint__code'
    ]
    
    ordering_fields = [
        'campaign__name', 'touchpoint__name', 'weight', 'priority',
        'expected_conversions', 'budget_allocated'
    ]
    ordering = ['campaign__name', 'priority', 'touchpoint__name']
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Serializer contextual según acción"""
        if self.action == 'list':
            return CampaignTouchpointListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CampaignTouchpointCreateUpdateSerializer
        else:
            return CampaignTouchpointDetailSerializer
    
    @action(detail=False, methods=['get'])
    def by_campaign(self, request):
        """Touchpoints agrupados por campaña"""
        campaign_id = request.query_params.get('campaign_id')
        if campaign_id:
            touchpoints = self.get_queryset().filter(campaign_id=campaign_id)
        else:
            touchpoints = self.get_queryset()
        
        # Agrupar por campaña
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for ct in touchpoints:
            campaign_name = ct.campaign.name
            grouped[campaign_name].append(CampaignTouchpointListSerializer(ct).data)
        
        return Response(dict(grouped))
    
    @action(detail=False, methods=['get'])
    def by_touchpoint(self, request):
        """Campañas agrupadas por touchpoint"""
        touchpoint_id = request.query_params.get('touchpoint_id')
        if touchpoint_id:
            campaign_touchpoints = self.get_queryset().filter(touchpoint_id=touchpoint_id)
        else:
            campaign_touchpoints = self.get_queryset()
        
        # Agrupar por touchpoint
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for ct in campaign_touchpoints:
            touchpoint_name = ct.touchpoint.name
            grouped[touchpoint_name].append(CampaignTouchpointListSerializer(ct).data)
        
        return Response(dict(grouped))
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analytics de relaciones campaña-touchpoint"""
        queryset = self.get_queryset()
        
        # Métricas básicas
        total_relations = queryset.count()
        avg_weight = queryset.aggregate(avg_weight=Avg('weight'))['avg_weight'] or 0
        total_expected_conversions = queryset.aggregate(
            total=Sum('expected_conversions')
        )['total'] or 0
        total_budget_allocated = queryset.aggregate(
            total=Sum('budget_allocated')
        )['total'] or 0
        
        # Top touchpoints por número de campañas
        top_touchpoints = queryset.values(
            'touchpoint__name'
        ).annotate(
            campaigns_count=Count('campaign', distinct=True),
            total_budget=Sum('budget_allocated'),
            avg_weight=Avg('weight')
        ).order_by('-campaigns_count')[:10]
        
        # Top campañas por número de touchpoints
        top_campaigns = queryset.values(
            'campaign__name'
        ).annotate(
            touchpoints_count=Count('touchpoint', distinct=True),
            total_budget_allocated=Sum('budget_allocated'),
            avg_weight=Avg('weight')
        ).order_by('-touchpoints_count')[:10]
        
        analytics_data = {
            'total_relations': total_relations,
            'avg_weight': round(avg_weight, 2),
            'total_expected_conversions': total_expected_conversions,
            'total_budget_allocated': float(total_budget_allocated) if total_budget_allocated else 0,
            'top_touchpoints': list(top_touchpoints),
            'top_campaigns': list(top_campaigns)
        }
        
        return Response(analytics_data)
