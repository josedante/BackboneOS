"""
HTML URLconf for campaigns (mounted at /campaigns/).

Uses ``campaigns_html`` namespace to avoid clashing with DRF routes under
/api/campaigns/.
"""

from django.urls import path

from . import template_views

app_name = 'campaigns_html'

urlpatterns = [
    path('', template_views.campaigns_hub, name='list'),
    path('new/', template_views.campaign_create, name='create'),
    path(
        'touchpoints/new/',
        template_views.campaign_touchpoint_create,
        name='touchpoint_create',
    ),
    path(
        'touchpoints/<int:pk>/',
        template_views.campaign_touchpoint_detail,
        name='touchpoint_detail',
    ),
    path(
        'touchpoints/<int:pk>/delete/',
        template_views.campaign_touchpoint_delete,
        name='touchpoint_delete',
    ),
    path('<uuid:pk>/', template_views.campaign_detail, name='detail'),
    path('<uuid:pk>/delete/', template_views.campaign_delete, name='delete'),
]
