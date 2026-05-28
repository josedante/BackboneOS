"""
HTML URLconf for offers (mounted at /offers/).

Uses ``offers_html`` namespace to avoid clashing with DRF routes under
/api/offers/.
"""

from django.urls import path

from . import template_views

app_name = 'offers_html'

urlpatterns = [
    path('', template_views.offering_list, name='list'),
    path('new/', template_views.offering_create, name='create'),
    path('<uuid:pk>/', template_views.offering_detail, name='detail'),
    path('<uuid:pk>/delete/', template_views.offering_delete, name='delete'),
]
