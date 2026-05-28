"""
HTML URLconf for products (mounted at /products/).

Uses ``products_html`` namespace to avoid clashing with DRF routes under /api/products/.
"""

from django.urls import path

from . import template_views

app_name = 'products_html'

urlpatterns = [
    path('', template_views.product_list, name='list'),
    path('new/', template_views.product_create, name='create'),
    path('<uuid:pk>/', template_views.product_detail, name='detail'),
    path('<uuid:pk>/delete/', template_views.product_delete, name='delete'),
]
