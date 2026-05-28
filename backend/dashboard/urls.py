from django.urls import path

from . import template_views

app_name = 'dashboard'

urlpatterns = [
    path('', template_views.home, name='home'),
]
