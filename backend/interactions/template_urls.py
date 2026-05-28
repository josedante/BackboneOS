"""
HTML URLconf for interactions (mounted at /interactions/).

Uses ``interactions_html`` namespace to avoid clashing with DRF routes under
/api/interactions/.
"""

from django.urls import path

from . import template_views

app_name = 'interactions_html'

urlpatterns = [
    path('', template_views.interactions_hub, name='list'),
    # Interactions are read-only here; capture happens in contextual apps via services.
    path('<uuid:pk>/', template_views.interaction_detail, name='interaction_detail'),
    path(
        'touchpoints/new/',
        template_views.touchpoint_create,
        name='touchpoint_create',
    ),
    path(
        'touchpoints/<uuid:pk>/',
        template_views.touchpoint_detail,
        name='touchpoint_detail',
    ),
    path(
        'touchpoints/<uuid:pk>/delete/',
        template_views.touchpoint_delete,
        name='touchpoint_delete',
    ),
]
