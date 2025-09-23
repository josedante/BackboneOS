"""
URL configuration for websites app.
"""

from django.urls import path
from . import views

app_name = 'websites'

urlpatterns = [
    path('events/page-view/', views.PageViewEventView.as_view(), name='page_view_event'),
]
