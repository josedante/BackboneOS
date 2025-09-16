from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('api/', include(router.urls)),
    path('login/', views.login, name='api_login'),
    path('jwt/login/', views.jwt_login, name='jwt_login'),
    path('jwt/logout/', views.jwt_logout, name='jwt_logout'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('user/', views.current_user, name='current_user'),
]