from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('api/', include(router.urls)),
    path('jwt/login/', views.jwt_login, name='jwt_login'),
    path('jwt/logout/', views.jwt_logout, name='jwt_logout'),
    path('jwt/refresh/', views.jwt_cookie_refresh, name='jwt_refresh'),
    path('user/', views.current_user, name='current_user'),
]