"""
HTML URLconf for entities (mounted at /entities/).

Uses ``entities_html`` namespace to avoid clashing with DRF routes under /api/entities/.
"""

from django.urls import path

from . import template_views

app_name = 'entities_html'

urlpatterns = [
    path('', template_views.entities_list, name='list'),
    path('people/new/', template_views.person_create, name='person_create'),
    path('people/<uuid:pk>/', template_views.person_detail, name='person_detail'),
    path(
        'people/<uuid:pk>/create-profile/',
        template_views.person_create_profile,
        name='person_create_profile',
    ),
    path('people/<uuid:pk>/delete/', template_views.person_delete, name='person_delete'),
    path('organizations/new/', template_views.organization_create, name='org_create'),
    path(
        'organizations/<uuid:pk>/',
        template_views.organization_detail,
        name='org_detail',
    ),
    path(
        'organizations/<uuid:pk>/delete/',
        template_views.organization_delete,
        name='org_delete',
    ),
]
